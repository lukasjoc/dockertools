#!/usr/bin/env python3

import distutils.core
import Cython.Build

distutils.core.setup(
    name="cooldocker",
    version="0.1",
    description="list docker entities with color and count",
    author='lukasjoc',
    url="https://github.com/lukasjoc/cooldocker",
    ext_modules = Cython.Build.cythonize("cython_cooldocker.pyx", language_level=3),
)
