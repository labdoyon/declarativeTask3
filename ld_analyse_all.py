import os
import subprocess
from xpd_to_tsv_config import data_path

from declarativeTask3.config import rawFolder, python_interpreter
sourcedata_folder = os.path.join(rawFolder, 'sourcedata')
rawdata_folder = os.path.join(rawFolder, 'rawdata')
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

all_subjects_output = open(os.path.join(rawdata_folder, "all_subjects.csv"), "w", newline='')

subjectCode = folders[0]
with open(os.path.join(rawdata_folder, subjectCode.replace('sub-', '') + '_preprocessed_data.csv'), 'r') as subject_file:
    for line in subject_file:
        all_subjects_output.write(line)
# now the rest:
for subjectCode in folders[1:]:
    try:
        with open(os.path.join(rawdata_folder, subjectCode.replace('sub-', '') + '_preprocessed_data.csv'), 'r') as f:
            index = 0
            for line in f:
                if not index:
                    index = 1
                else:
                    all_subjects_output.write(line)
    except FileNotFoundError:
        pass

all_subjects_output.close()
