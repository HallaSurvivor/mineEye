"""
A set up file for telling cx_Freeze how to compile the game properly.
"""
import sys
import cx_Freeze

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [cx_Freeze.Executable(script="run.py", base=base)]

packages = []

include_files = ['Fonts/', 'Music/', 'Sprites/', 'dependencies/', 'replays/', 'room_options.txt']

excludes = []

cx_Freeze.setup(
    name="mineEye",
    options={"build_exe": {"packages":packages, "include_files":include_files, "excludes": excludes}},
    executables=executables
)