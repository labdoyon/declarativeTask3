import subprocess
import os
import glob
import pickle
from declarativeTask3.config import rawFolder, soundsFolder, sounds, tempSounds

# Documentation: https://trac.ffmpeg.org/wiki/AudioVolume
# https://ffmpeg.org/ffmpeg.html#Main-options
# https://www.igorkromin.net/index.php/2016/12/23/prevent-errors-during-ffmpeg-execution-in-a-loop/

# How to install ffmpeg on Windows: https://www.wikihow.com/Install-FFmpeg-on-Windows


def play_sound(j):
    # f'"{}"' is in order to handle potential spaces in file names or paths
    command = 'ffplay -nodisp -loglevel quiet -autoexit ' + f'"{os.path.join(soundsFolder, tempSounds[j])}"'
    print(command)
    subprocess.call(command)


def change_volume(j, volume_adjustment_db=0):
    # f'"{}"' is in order to handle potential spaces in file names or paths
    input_sound = f'"{os.path.join(soundsFolder, sounds[j])}"'
    output_sound = f'"{os.path.join(soundsFolder, tempSounds[j])}"'
    command = 'ffmpeg -loglevel quiet -y -i ' + input_sound + \
              ' -filter:a "volume=' + str(volume_adjustment_db) + 'dB" ' + output_sound + ' -nostdin'
    print(command)
    subprocess.call(command)


def present_options(j):
    if j == 0:
        print("here is the 1st sound")
    elif j == 1:
        print("here is the 2nd sound")
    elif j == 2:
        print("here is the 3rd sound")
    elif j > 3:
        print("here is the " + str(j) + "th sound")

    print("left click to increase the volume, or right click to decrease")
    print("You may not increase the sound over 0dB")
    print("if the sound is not high enough, please ask the supervisor to increase system volume")
    print("press q to move onto the next sound")
    print("press w to hear the sound again")


def delete_temp_files():
    for j in range(len(sounds)):
        try:
            output_sound = os.path.join(soundsFolder, tempSounds[j])
            os.remove(output_sound)
        except:
            pass


# TODO rename create_temp_sound_files to get_temp_sound_files wherever appropriate


def create_temp_sound_files(subject_name, datafile_directory):
    subject_filename = 'soundsVolumeAdjustmentIndB_' + subject_name + '.pkl'
    candidate_files = []
    # Getting back the objects:
    subject_file_full_path = os.path.join(rawFolder, datafile_directory, subject_filename)
    all_files = glob.glob(os.path.join(rawFolder, 'sourcedata', 'sub-'+subject_name, 'ses-*', 'beh', subject_filename))
    if os.path.exists(subject_file_full_path):
        if os.path.getsize(subject_file_full_path) > 0:
            candidate_files.append(subject_file_full_path)
    for tmp_file in all_files:
        if os.path.getsize(tmp_file) > 0:
            candidate_files.append(tmp_file)
    if candidate_files:
        for tmp_file in candidate_files:
            with open(tmp_file, "rb") as f:
                sounds_volume_adjustment = pickle.load(f)
            for j in range(len(sounds)):
                change_volume(j, volume_adjustment_db=sounds_volume_adjustment[j])
            return sounds_volume_adjustment
    else:
        return [0]*len(sounds)  # importing sound volume settings failed. No valid file
