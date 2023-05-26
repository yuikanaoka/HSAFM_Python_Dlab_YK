from setuptools import setup
from setuptools.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [
    Extension(
        'dilationfunctionmodule',
        ['dilationfunc.pyx'],
        include_dirs=[np.get_include()]
    )
]

setup(
    name='DilationFunctionPackage',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
)
