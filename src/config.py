import glob
import os
# from math import ceil
from expyriment.misc import constants

rawFolder = os.getcwd() + os.path.sep

picturesFolder = rawFolder + 'stimulis' + os.path.sep
picturesExamplesFolder = rawFolder + 'stimulisExample' + os.path.sep
picturesXFolder = picturesFolder + 'association_test_X' + os.path.sep
dataFolder = rawFolder + 'data' + os.path.sep
soundsFolder = rawFolder + 'stimulis' + os.path.sep + 'sounds' + os.path.sep

mouseButton = 1

windowMode = False  # if False use FullScreen
windowSize = (1024, 768)  # if windowMode is True then use windowSize

picturesExamples = ['triangle.png', 'square.png', 'circle.png']
sounds = ['shortest-1-100ms.wav', 'shortest-2-100ms.wav', 'shortest-3-100ms.wav']
tempSounds = ['sound' + str(i) + '.wav' for i in range(len(sounds))]

templatePicture = picturesFolder + 'class_a' + os.path.sep + 'a001.png'

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
matrixSize = (5, 4)
cardSize = (90, 90)

''' Circles '''

startSpace = cardSize[1] + 20

nbBlocksMax = 10

presentationCard = 2000

responseTime = 5000
AssociationResponseTime = 10000
SoundBeforeImageTime = 200
shortRest = 2500
thankYouRest = 5000
restPeriod = 15000
clicPeriod = 200

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
elif matrixSize == (5, 4):
    matrixTemplate = [0] * 20
    removeCards = []

# correctAnswersMax = int(ceil((matrixSize[0]*matrixSize[0] - len(removeCards))*7./10))
correctAnswersMax = 13
numberBlocksLearning = 10
numberBlocksSubUnit = 2
numberLearningSubUnits = 5
if numberBlocksSubUnit * numberLearningSubUnits != numberBlocksLearning:
    raise ValueError("""the number of blocks of learning is not equal to
    its number of subUnits * the number of blocks during a subUnit""")

classPictures = ['a', 'b', 'c']
picturesFolderClass = {category: picturesFolder+'class_'+category+os.path.sep for category in classPictures}
# one category (as we'll later rename (refactor) classes) should always be a single lowercase letter
numberClasses = len(classPictures)
# The setting below allows the experimenter to prevent a learned matrix (currentCorrectAnswers > correctAnswersMax)
# from appearing again during the Encoding Phase. In other words, as soon as this matrix is learned, during the encoding
# phase, it won't appear again, during the encoding phase, again. The Encoding phase will continue, using only unlearned
# matrices during the Encoding phase
ignore_learned_matrices = False

listPictures = {}
for classPicture in classPictures:
    listPictures[classPicture] = glob.glob(picturesFolderClass[classPicture] + classPicture + '*[0-9][0-9][0-9].png')

for category in classPictures:
    listPictures[category] = [p.replace(picturesFolderClass[category], '') for p in listPictures[category]]

feedback_frame_correct_color = constants.C_GREEN
feedback_frame_wrong_color = constants.C_RED
feedback_time = 1000
inter_feedback_delay_time = 1000
choose_location_minimum_response_time = 5000

debug = False
