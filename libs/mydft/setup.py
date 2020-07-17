from distutils.core import setup, Extension, DEBUG

sfc_module = Extension('mydft', sources = ['mydft.cpp'])

setup(name = 'mydft', version = '1.0',
    description = 'Python Package with DFT128',
    ext_modules = [sfc_module]
    )