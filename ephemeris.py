"""Helper functions for pyephem."""
import numpy as np, ephem
from enlib import utils

def mjd2djd(mjd): return np.asarray(mjd) + 2400000.5 - 2415020
def define_subsamples(t, dt=10):
	t = np.asarray(t)
	if t.ndim == 0: return np.array([t]), np.array([0])
	if dt == 0: return t, np.arange(len(t))
	box       = utils.widen_box([np.min(t),np.max(t)], 1e-2)
	sub_nsamp = max(3,int((box[1]-box[0])/dt))
	if sub_nsamp > len(t): return t, np.arange(len(t))
	sub_t     = np.linspace(box[0], box[1], sub_nsamp, endpoint=True)
	return sub_t, (t-box[0])*(sub_nsamp-1)/(box[1]-box[0])

def ephem_raw(objname, mjd):
	"""Simple wrapper around pyephem. Returns astrometric ra, dec, rad (AU)
	for each specified modified julian date for the given object name
	(case sensitive)."""
	mjd = np.asarray(mjd)
	with utils.flatview(mjd, mode="r"):
		djd = mjd2djd(mjd)
		obj = getattr(ephem, objname)()
		res = np.zeros([3,len(djd)])
		for i, t in enumerate(djd):
			obj.compute(t)
			res[0,i] = obj.a_ra
			res[1,i] = obj.a_dec
			res[2,i] = obj.earth_distance
	res.reshape((3,)+mjd.shape)
	return res

def ephem_vec(objname, mjd, dt=10):
	"""Computes the earth-relative position vector[{x,y,z},ntime] for the
	given object. Uses interpolation in steps dt (seconds) to speed things up.
	Set dt to 0 to disable this. The resulting vector has units of AU."""
	# Get low-res [ra,dec,r]
	sub_time, inds = define_subsamples(mjd, dt=dt/(24.*3600))
	sub_pos  = ephem_raw(objname, sub_time)
	# Convert to low-res [x,y,z]
	sub_vec  = utils.ang2rect(sub_pos[:2],zenith=False)*sub_pos[2]
	# Interpolate to target resolution
	full_vec = utils.interpol(sub_vec, inds[None])
	return full_vec

def ephem_pos(objname, mjd, dt=10):
	"""Computes the earth-relative angular position and radius [{ra,dec,r},ntime]
	for the given object. Uses interpolation in steps dt (seconds) to sepeed
	things up. Set dt to 0 to disable this. r has units of AU."""
	# Get low-res [ra,dec,r]
	sub_time, inds = define_subsamples(mjd, dt=dt/(24.*3600))
	sub_pos = ephem_raw(objname, sub_time)
	# Avoid angle wraps, as they will mess up the interpolation
	sub_pos[0] = utils.unwind(sub_pos[0])
	# Interpolate to target resolution
	full_pos = utils.interpol(sub_pos, inds[None])
	return full_pos
