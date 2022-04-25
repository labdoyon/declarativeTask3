import os
import subprocess
from xpd_to_tsv_config import data_path

from declarativeTask3.config import python_interpreter

# activate_python_env_prefix = \
#     r"""C:\Users\Dreamy\Documents\GitHub\declarativeTask3_2021-04-07\venv\Scripts\activate.bat""" + ' & '
activate_python_env_prefix = ''
sep = os.path.sep
folders_and_files = os.listdir(data_path)

folders = []
for folder in folders_and_files:
    if os.path.isdir(data_path + sep + folder):
        folders.append(folder)

for folder in folders:
    if folder != 'HBHLDec_Y011' and folder != 'HBHLDec_Y015_001' and folder != 'HBHLDec_Y010_001' and \
            'EXCLUDED' not in folder:
        command = activate_python_env_prefix + python_interpreter + ' ld_analysis.py ' + data_path + sep + folder
        print('\n'*2 + '='*30)
        print(folder)
        print(command)
        print('='*30)
        subprocess.call(command)
