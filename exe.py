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
        script='sistema.py',
        targetName='sistema.exe',
        base="Win32GUI",
        copyDependentFiles=True
    )
]

setup(
    name="sistema",
    version="1.0",
    description="Sistema de ventas",
    author="Carlos Serrada",
    options=dict(build_exe=buildOptions),
    executables=executables
)
