#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from cx_Freeze import setup, Executable

includes = ["atexit"]

buildOptions = dict(
    create_shared_zip=False,
    append_script_to_exe=True,
    includes=includes
)

executables = [
    Executable(
        script='ceicsv.py',
        targetName='CEIC-Suite.exe',
        base="Win32GUI",
        copyDependentFiles=True
    )
]

setup(
    name="CEIC Suite",
    version="1.0",
    description="Sistema multipropósito del CEIC",
    author="Carlos Serrada",
    options=dict(build_exe=buildOptions),
    executables=executables
)
