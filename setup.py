from cx_Freeze import setup, Executable
import sys
import matplotlib

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["matplotlib.backends.backend_qt4agg"],
					excludes = ["tkinter",
								"scipy",
								"PyQt4",
								#"numpy.linalg"
								],
					include_files = [
									#(matplotlib.get_data_path(),"mpl-data"),
									("images","images")],
					optimize = 2,
					compressed = True
					)


base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('OsmoData.pyw', base=base)
]

setup(name='OsmoData',
      version = '0.5',
      description = 'OsmoData is a program to convert datafiles from the OsmoInspector to a simple csv file with average permeances',
      options = dict(build_exe = buildOptions),
      executables = executables)
