import os
from distutils.sysconfig import get_python_lib
import platform

datas = [('./data', 'data'), ('./lib/d3', 'lib/d3')]

a = Analysis(['./main.py'],
        pathex=['./'],
        binaries=None,
        datas=datas,
        hiddenimports=[],
        hookspath=['./hooks',],
        runtime_hooks=None,
        excludes=None,
        win_no_prefer_redirects=None,
        win_private_assemblies=None,
        cipher=None)

# Additional DLLs
tmp = []
arch = platform.architecture()[0]
if arch=='32bit':
    dll_path = os.path.join('dll', 'x86')
else:
    dll_path = os.path.join('dll', 'x64')

for dir_path, dir_names, file_names in os.walk(dll_path):
    for file_name in file_names:
        tmp.append(
                (
                    file_name,
                    os.path.join(os.getcwd(), dir_path, file_name),
                    'BINARY'
                    )
                )

# For Numpy MKL
blacklist = ['mkl_rt.dll', 'tbb.dll', 'libmmd.dll', 'libifcoremd.dll']
a.binaries = list(filter(lambda t:t[0] not in blacklist, a.binaries))
numpy_dll_path = os.path.join(get_python_lib(), 'numpy', 'core')
for dir_path, dir_names, file_names in os.walk(numpy_dll_path):
    for file_name in file_names:
        if os.path.splitext(file_name)[1]=='.dll':
            tmp.append(
                    (
                        file_name,
                        os.path.join(dir_path, file_name),
                        'BINARY'
                        )
                    )

a.binaries += tmp

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
        a.scripts,
        name='UMATracker-Area51',
        debug=False,
        strip=None,
        upx=True,
        exclude_binaries=True,
        console=False, icon='./icon/icon.ico')

coll = COLLECT(exe,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name='UMATracker-Area51',
        debug=False,
        strip=None,
        upx=True,
        console=False, icon='./icon/icon.ico')
