import sys

import glob
from os.path import normpath, join, dirname, basename
# from math import ceil
from expyriment.misc import constants

python_interpreter = '"'+sys.executable+'"'  # the '"' are there in case of spaces in the fullpath to the python_interpreter interpreter

rawFolder = normpath(join(dirname(__file__), '..', '..'))

picturesFolder = normpath(join(rawFolder, 'stimulis'))
picturesExamplesFolder = normpath(join(rawFolder, 'stimulisExample'))
picturesXFolder = normpath(join(picturesFolder, 'association_test_X'))
soundsFolder = normpath(join(rawFolder, 'stimulis',  'sounds'))

mouseButton = 1

windowMode = False  # if False use FullScreen
windowSize = (1024, 768)  # if windowMode is True then use windowSize

picturesExamples = ['triangle.png', 'square.png', 'circle.png']
sounds = ['shortest-1-100ms.wav', 'shortest-3-100ms.wav']
tempSounds = ['sound' + str(i) + '.wav' for i in range(len(sounds))]
soundNames = {
    None: {0: 'S1', 1: 'S3'},
    'english': {0: 'standard', 1: 'A'},
    'french': {0: 'standard', 1: 'A'}}
# starting volume value for the sounds to be adjusted based on the system:
starting_sound_volume = -40  # dB

templatePicture = normpath(join(picturesFolder, 'class_a', 'a001.png'))

linesThickness = 0
colorLine = (0, 0, 0)  # expyriment.misc.constants.C_BLACK

cueCardColor = (255, 255, 255)   # expyriment.misc.constants.C_WHITE
cardColor = (255, 255, 255)  # expyriment.misc.constants.C_WHITE

clickColor = (200, 200, 200)
restBGColor = (0, 0, 0)  # expyriment.misc.constants.C_BLACK
restCrossColor = (255, 255, 255)  # expyriment.misc.constants.C_WHITE
restCrossSize = (100, 100)
restCrossThickness = 20
dotColor = (0, 0, 0)  # expyriment.misc.constants.C_BLACK
bgColor = (150, 150, 150)
textColor = (0, 0, 0)  # expyriment.misc.constants.C_BLACK


textSize = 50
matrixSize = (6, 4)
cardSize = (90, 90)

''' Circles '''

startSpace = cardSize[1] + 20

nbBlocksMax = 3

presentationCard = 2000

responseTime = 5000
AssociationResponseTime = 10000
SoundBeforeImageTime = 200
shortRest = 2500
thankYouRest = 5000
restPeriod = 15000
pleaseGetReadyPeriod = 2000
clicPeriod = 300

min_max_ISI = [500, 1500]  # [min, max] inter_stimulus interval

##

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


arrow = ("xX                      ",
         "X.X                     ",
         "X..X                    ",
         "X...X                   ",
         "X....X                  ",
         "X.....X                 ",
         "X......X                ",
         "X.......X               ",
         "X........X              ",
         "X.........X             ",
         "X......XXXXX            ",
         "X...X..X                ",
         "X..XX..X                ",
         "X.X XX..X               ",
         "XX   X..X               ",
         "X     X..X              ",
         "      X..X              ",
         "       X..X             ",
         "       X..X             ",
         "        XX              ",
         "                        ",
         "                        ",
         "                        ",
         "                        ")

arrow1 = (' XX                                                                             ',
          ' XXXX                                                                           ',
          ' XX.XXX                                                                         ',
          ' XX...XXX                                                                       ',
          ' XX.....XXX                                                                     ',
          ' XX.......XXX                                                                   ',
          ' XX.........XXX                                                                 ',
          ' XX...........XXX                                                               ',
          ' XX.............XXX                                                             ',
          ' XX...............XXX                                                           ',
          ' XX.................XXX                                                         ',
          ' XX...............XXXX                                                          ',
          ' XX..............XX                                                             ',
          ' XX....  ......XX                                                               ',
          ' XX..XX......XX                                                                 ',
          ' XXX   XX......XX                                                               ',
          '        XX......XX                                                              ',
          '         XX......XX                                                             ',
          '          XX......XX                                                            ',
          '           XX......XX                                                           ',
          '            XX......XX                                                          ',
          '             XX......XX                                                         ',
          '              XX......XX                                                        ',
          '               XX......XX                                                       ',
          '                XX......XX                                                      ',
          '                 XXXXXXXXXX                                                     ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ',
          '                                                                                ')

if matrixSize == (4, 4):
    matrixTemplate = [0]*16
    removeCards = []
elif matrixSize == (5, 5):
    matrixTemplate = [2,0,2,1,1,1,1,0,2,0,2,2,0,1,2,1,2,2,0,0,0,1,0,1]
    removeCards = [12]
elif matrixSize == (6, 6):
    removeCards = []
    matrixTemplate = [0, 1, 1, 2, 0, 2,
                      2, 0, 0, 2, 1, 1,
                      1, 0, 2, 1, 2, 0,
                      0, 2, 1, 0, 1, 2,
                      1, 2, 1, 2, 0, 1,
                      0, 1, 0, 2, 2, 0]
elif matrixSize == (7, 7):
    removeCards = [24]
    matrixTemplate = [0, 1, 1, 0, 2, 0, 2,
                      2, 0, 0, 1, 2, 1, 1,
                      1, 0, 2, 2, 1, 2, 0,
                      2, 1, 0,    2, 0, 1,
                      0, 2, 1, 2, 0, 1, 2,
                      1, 2, 1, 0, 2, 0, 1,
                      0, 1, 0, 1, 2, 2, 0]
elif matrixSize == (6, 4):
    matrixTemplate = [0] * 24
    removeCards = []

# correctAnswersMax = int(ceil((matrixSize[0]*matrixSize[0] - len(removeCards))*7./10))
correctAnswersMax = 15  # 65%

classPictures = ['a', 'c']
classNames = {'english': {'a': 'animals', 'b': 'household', 'c': 'clothes'},
              'french': {'a': 'animaux', 'b': 'maison', 'c': 'vêtements'},
              None: {'a': 'a', 'c': 'c'}}

picturesFolderClass = {category: join(picturesFolder, 'class_'+category) for category in classPictures}
# one category (as we'll later rename (refactor) classes) should always be a single lowercase letter
numberClasses = len(classPictures)
# The setting below allows the experimenter to prevent a learned matrix (currentCorrectAnswers > correctAnswersMax)
# from appearing again during the Encoding Phase. In other words, as soon as this matrix is learned, during the encoding
# phase, it won't appear again, during the encoding phase, again. The Encoding phase will continue, using only unlearned
# matrices during the Encoding phase
# Overridden for Vaishali task: we don't stop until both matrices are learned
ignore_one_learned_matrices = True
min_number_learned_matrices = len(classPictures)

listPictures = {}
for classPicture in classPictures:
    listPictures[classPicture] = glob.glob(
        join(picturesFolderClass[classPicture], classPicture + '*[0-9][0-9][0-9].png'))

for category in classPictures:
    listPictures[category] = [basename(p) for p in listPictures[category]]

feedback_frame_correct_color = constants.C_GREEN
feedback_frame_wrong_color = constants.C_RED
feedback_time = 1000
inter_feedback_delay_time = 1000
choose_location_minimum_response_time = 5000

debug = False

sessions = ['expePreNap', 'expePostNap']
experiment_session = {
    'generate-matrix':          'expePreNap',
    'choose-sound-association': 'expePreNap',
    'choose-language':          'expePreNap',
    'soundVolumeAdjustment':    'expePreNap',
    'stimuli-presentation':     'expePreNap',
    'Example':                  'expePreNap',
    'Encoding':                 'expePreNap',
    'Test-Encoding':            'expePreNap',
    'ReTest-Encoding':          'expePostNap',
    'DayOne-Recognition':       'expePostNap'}

tasks_to_generate = ['Encoding' + str(trf_j) for trf_j in range(nbBlocksMax)] + ['Test-Encoding'] + ['ReTest-Encoding']
