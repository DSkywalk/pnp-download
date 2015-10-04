import sys
from distutils.core import setup
from cx_Freeze import setup, Executable

import requests

build_exe_options = { 
    "packages" : [
    'requests',
    'urllib3'
]}

base = None

if sys.platform == "win32":
    base = "Win32GUI"


setup(  name = "ps-downloader",
        version = "0.1",
        description = "PS Downloader!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("ps-downloader.py", base=base)])
