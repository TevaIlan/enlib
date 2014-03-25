"""This module is intended to make it easier to implement slicing."""
import numpy as np
from enlib.utils import cumsplit, listsplit

def expand_slice(sel, n):
	"""Expands defaults and negatives in a slice to their implied values.
	After this, all entries of the slice are guaranteed to be present in their final form.
	Note, doing this twice may result in odd results, so don't send the result of this
	into functions that expect an unexpanded slice."""
	step = sel.step or 1
	def cycle(i,n): return min(i,n) if i >= 0 else n+i
	if step == 0: raise ValueError("slice step cannot be zero")
	if step > 0: return slice(cycle(sel.start or 0,n),cycle(sel.stop or n,n),step)
	else: return slice(cycle(sel.start or n-1, n), cycle(sel.stop,n) if sel.stop else -1, step)

def split_slice(sel, ndims):
	"""Splits a numpy-compatible slice "sel" into sub-slices sub[:], such that
	a[sel] = s[sub[0]][:,sub[1]][:,:,sub[2]][...], This is useful when
	implementing arrays with heterogeneous indices. Ndims indicates the number of
	indices to allocate to each split, starting from the left. Also expands all
	ellipsis."""
	if not isinstance(sel,tuple): sel = (sel,)
	# We know the total number of dimensions involved, so we can expand ellipis
	# What the heck? "in" operator is apparently broken for lists that
	# contain numpy arrays.
	parts = listsplit(sel, Ellipsis)
	if len(parts) > 1:
		# Only the rightmost ellipsis has any effect
		left, right = sum(parts[:-1],()), parts[-1]
		nfree = sum(ndims) - sum([i is not None for i in (left+right)])
		sel = left + tuple([slice(None) for i in range(nfree)]) + right
	return split_slice_simple(sel, ndims)

def split_slice_simple(sel, ndims):
	"""Helper function for split_slice. Splits a slice
	in the absence of ellipsis."""
	res = [[] for n in ndims]
	notNone = [v != None for v in sel]
	subs = np.concatenate([[0],cumsplit(notNone, ndims)])
	for i, r in enumerate(res):
		r += sel[subs[i]:subs[i+1]]
	return [tuple(v) for v in res]

def parse_slice(desc):
	class Foo:
		def __getitem__(self, p): return p
	foo = Foo()
	return eval("foo"+desc)