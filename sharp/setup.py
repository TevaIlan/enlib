from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
	name="sharp",
	cmdclass = {"build_ext": build_ext},
	ext_modules = [
		Extension(
			name="sharp",
			sources=["sharp.pyx"],
			libraries=["sharp","c_utils","fftpack"],
			extra_link_args = ["-openmp"],
			)
		]
	)