"""This module defines shortcuts for generating WCS instances and working
with them."""
import numpy as np
from astropy.wcs import WCS
from enlib import slice

deg2rad = np.pi/180
rad2deg = 1/deg2rad

def car(shape, box):
	"""Set up a plate carree system with bounds
	box=[[ra0,dec0],[ra1,dec1]] and pixels in each
	direciton given by shape=[nra,ndec]. Box indicates
	the edge of pixels, not centers, so all pixels will
	be wholly inside the box."""
	box = np.asfarray(box)*rad2deg
	w = WCS(naxis=2)
	# Reference point must be on equator to
	# get an unrotated plate carree.
	w.wcs.cdelt = (box[1]-box[0])/shape[-2:]
	w.wcs.crval = np.array([0.,0.])
	# The 0.5 handles the pixel center vs. edge issue
	w.wcs.crpix = (w.wcs.crval-box[0])/w.wcs.cdelt+0.5
	w.wcs.ctype = ["RA---CAR", "DEC--CAR"]
	return w

# cea has
# ra  = x
# dec = asin(lambda*y)
# with lambda specified by PV2_1.
# The projection will be conformal at theta_c,
# lambda = cos(theta_c)**2.
# Must find bounds in y
# y = sin(dec)/lambda
def cea(shape, box):
	"""Set up a cylindrical equal area system with bounds
	box=[[ra0,dec0],[ra1,dec1]] and pixels in each
	direciton given by shape=[nra,ndec]. Box indicates
	the edge of pixels, not centers, so all pixels will
	be wholly inside the box. The center of the box will be
	conformal."""
	box = np.asfarray(box)
	lam = np.cos(np.mean(box[:,1]))**2
	xybox = np.array([box[:,0],np.sin(box[:,1])/lam]).T*rad2deg
	w = WCS(naxis=2)
	w.wcs.cdelt = (xybox[1]-xybox[0])/shape[-2:]
	w.wcs.crval = np.array([0.,0.])
	# The 0.5 handles the pixel center vs. edge issue
	w.wcs.crpix = (w.wcs.crval-xybox[0])/w.wcs.cdelt+0.5
	w.wcs.set_pv([(2,1,lam)])
	w.wcs.ctype = ["RA---CEA", "DEC--CEA"]
	return w

def zea(shape, box):
	"""Setups up an oblate Lambert's azimuthal equal area
	system with bounds box=[[ra0,dec0],[ra1,dec1]] and pixels
	in each direciton given by shape=[nra,ndec]. Box indicates
	the edge of pixels, not centers, so all pixels will be
	wholly inside the box."""
	return autobox(shape, box, "ZEA")

def air(shape, box):
	"""Setups up an Airy system with bounds
	box=[[ra0,dec0],[ra1,dec1]] and pixels in each direciton
	given by shape=[nra,ndec]. Box indicates the edge of pixels,
	not centers, so all pixels will be wholly inside the box."""
	return autobox(shape, box, "AIR")

def autobox(shape, box, name):
	"""Sets up a wcs with the given bounding box
	for an image of the given shape for the named
	coordinate system, provided no fancy options are
	needed. crval will be in the center of the box,
	so this function produces oblique projections."""
	box = np.asfarray(box)
	w = WCS(naxis=2)
	w.wcs.ctype = ["RA---"+name, "DEC--"+name]
	# Set up temporary pixel coordinates.
	w.wcs.cdelt = np.array([1.,1.])
	w.wcs.crval = np.mean(box,0)[::-1]*rad2deg
	w.wcs.crpix = np.array([0.,0.])
	corners = w.wcs_world2pix(box[:,::-1]*rad2deg,0)+0.5
	# Shift crpix to make the corner the pixel origin
	w.wcs.crpix -= corners[0]
	# Scale cdelt so that the number of pixels inside
	# is correct
	w.wcs.crpix -= 0.5
	scale = shape[::-1][:2]/(corners[1]-corners[0])
	w.wcs.cdelt /= scale
	w.wcs.crpix *= scale
	w.wcs.crpix += 0.5
	return w

systems = {"car": car, "cea": cea, "air": airy, "zea": zea }

def from_bounds(shape, box, system="cea"):
	"""Construct a WCS object based with bounds
	box=[[ra0,dec0],[ra1,dec1]] and pixels in each
	direciton given by shape=[nra,ndec]. Box indicates
	the edge of pixels, not centers, so all pixels will
	be wholly inside the box. The optional system
	argument determines which WCS to use. The default
	is "cea": cylindrical equal area"."""
	return systems[system.lower()](shape, box)

def describe(wcs):
	"""Since astropy.wcs.WCS objects to not have a useful
	str implementation, this function provides a relpacement."""
	sys  = wcs.wcs.ctype[0][-3:].lower()
	n    = wcs.naxis
	return ("%s:{cdelt:["+",".join(["%.3g"]*n)+"],crval:["+",".join(["%.3g"]*n)+"],crpix:["+",".join(["%.3g"]*n)+"]}") % ((sys,) + tuple(wcs.wcs.cdelt) + tuple(wcs.wcs.crval) + tuple(wcs.wcs.crpix))
