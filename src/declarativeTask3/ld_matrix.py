import random
import numpy as np
import subprocess
from expyriment.stimuli import Circle, Rectangle, Shape
from expyriment.misc import constants, geometry
from playsound import playsound
from os.path import join

from declarativeTask3.ld_card import LdCard
from declarativeTask3.config import cardSize, linesThickness, cueCardColor, matrixTemplate, listPictures, removeCards, dotColor, bgColor
from declarativeTask3.config import numberClasses, classPictures, picturesFolderClass, picturesFolder
from declarativeTask3.config import sounds, soundsFolder, tempSounds
from declarativeTask3.config import feedback_frame_correct_color, feedback_frame_wrong_color

class LdMatrix(object):
    def __init__(self, size, windowSize):
        self._windowSize = windowSize
        self._size = size
        self._threshold = 0
        self._isFill = False
        self._isValid = False
        self._gap = None
        self._cueCard = []
        self._matrix = np.ndarray(shape=self._size, dtype=object)
        self._listPictures = []
        self._rowGap = 0
        self._columnGap = 0
        self._category = None

        self.populate()  # Populate with cards
        self.isValidMatrix()  # Check Matrix validity
        self.setPositions()  # Set cards positions

    def populate(self):

        for nCard in range(self._matrix.size):
                self._matrix.itemset(nCard, LdCard(cardSize))

        for i in range(len(classPictures)):
            self._cueCard.append(LdCard(cardSize, cueCardColor))

    def isValidMatrix(self):
        spaceRowLeft = self.windowSize[0] - (self.size[0] * self._matrix.item(0).size[0])
        spaceColumnLeft = self.windowSize[1] - ((self.size[1] + 2) * self._matrix.item(0).size[1]) - 2 * linesThickness

        spaceRowLeftPerGap = spaceRowLeft/(self.size[0] + 1)
        spaceColumnLeftPerGap = spaceColumnLeft/(self.size[1] + 1 + 4)  # 4: gaps top and bottom

        self._gap = min(spaceColumnLeftPerGap, spaceRowLeftPerGap)

        if self._gap > self._threshold:
            self._isValid = True
            return self._isValid
        else:
            print('This matrix is not Valid')
            import sys
            sys.exit()


    def scale(self):
        for nCard in range(self._matrix.size):
            self._matrix.item(nCard).stimuli[0].scale(self._matrix.item(nCard).size[0]/float(300))

    def setPositions(self):

        if self._isValid:
            sizeRows = self._matrix.item(0).size[0]  # Size of a card
            sizeColumns = self._matrix.item(0).size[1]  # Size of a card

            rowGap = (self.windowSize[0] - (self.size[0] * sizeRows + (self.size[0] - 1) * self.gap))/2
            columnGap = (self.windowSize[1] - (self.size[1] * sizeColumns + (self.size[1] - 1) * self.gap))/2  # Validated

            self._rowGap = rowGap  # Save Row Gap
            self._columnGap = columnGap  # Save Column Gap

            iCard = 0  # Loop over cards

            for iRow in range(self._size[0]):
                for iColumn in range(self._size[1]):
                    rowPosition = -self._windowSize[0]/2 + rowGap + self.gap * iRow + iRow * sizeRows + sizeRows/2
                    columnPosition = self._windowSize[1]/2 - (columnGap + self.gap * iColumn + iColumn*sizeColumns + sizeColumns/2)
                    self._matrix.item(iCard).position = (rowPosition, columnPosition)
                    self._matrix.item(iCard).stimuli[0].reposition(self._matrix.item(iCard).position)
                    self._matrix.item(iCard).stimuli[1].reposition(self._matrix.item(iCard).position)
                    iCard += 1

            for i in range(len(classPictures)):
                rowPosition = 0 + (self.gap + sizeRows) * (i-1)
                (self._cueCard[i]).position = (rowPosition, self._windowSize[1]/float(2) - self.gap - sizeRows/float(2.0))
                (self._cueCard[i]).stimuli[0].reposition(self._cueCard[i].position)
                (self._cueCard[i]).stimuli[1].reposition(self._cueCard[i].position)
        else:
            print('Matrix is not valid')

    def associateCategory(self, category):
        self._category = category

    def changeCueCardPosition(self, position, cue_index):
        sizeRows = self._matrix.item(0).size[0]  # Size of a card
        self._cueCard[cue_index].position = position

    def plotCueCard(self, cue_index, showPicture, bs, draw=False):  # Plot cue Card
        if showPicture is True:
            self._cueCard[cue_index].stimuli[0].plot(bs)
        else:
            self._cueCard[cue_index].stimuli[1].plot(bs)
        if draw:
            bs.present(False, True)
        else:
            return bs

    def plotCard(self, nCard, showPicture, bs, draw=False):  # Plot specific card
        if showPicture is True:
            self._matrix.item(nCard).stimuli[0].plot(bs)
        else:
            self._matrix.item(nCard).stimuli[1].plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def returnPicture(self, nCard):
        return self._matrix.item(nCard).picture

    def playSound(self, soundsAllocation_index, volumeAdjusted=False):
        if volumeAdjusted:
            sound = tempSounds[soundsAllocation_index[self._category]]
        else:
            sound = sounds[soundsAllocation_index[self._category]]
        # f'"{}"' is in order to handle potential spaces in file names or paths
        command = 'ffplay -nodisp -loglevel quiet -autoexit ' + f'"{join(soundsFolder, sound)}"'
        subprocess.call(command)
        return command, sound

    def playCueSound(self, volumeAdjusted = False):
        if volumeAdjusted:
            sound = tempSounds[self._cueCard.sound]
        else:
            sound = sounds[self._cueCard.sound]
        # f'"{}"' is in order to handle potential spaces in file names or paths
        command = 'ffplay -nodisp -loglevel quiet -autoexit ' +\
                  f'"{join(soundsFolder, sound)}"'
        subprocess.call(command)

    def plotDefault(self, bs, draw=False, show_matrix=True):
        for nCard in range(self._matrix.size):
            if nCard in removeCards or not show_matrix:
                 self._matrix.item(nCard).color = bgColor

            bs = self.plotCard(nCard, False, bs)

        for i in range(len(classPictures)):
            if not show_matrix:
                self._cueCard[i].color = bgColor
            bs = self.plotCueCard(i, False, bs)

        if (self.size[0] % 2 == 0) and (self.size[1] % 2 == 0):
            if show_matrix:
                local_color = dotColor
            else:
                local_color = bgColor
            centerDot = Circle(self.gap/2, colour=local_color, position=(0, 0))
            centerDot.plot(bs)
        elif (self.size[0] % 2 == 1) and (self.size[1] % 2 == 1):
            if show_matrix:
                local_color = constants.C_WHITE
            else:
                local_color = bgColor
            centerSquare = Rectangle(cardSize, colour=local_color, position=(0, 0))
            centerSquare.plot(bs)

        if draw:
            bs.present(False, True)
        else:
            return bs

    def findMatrix(self, category, previousMatrix=None, keep=False):

        newMatrix = []

        if previousMatrix is None:   # New Matrix
            pictures = list(listPictures[category])
            for itemMatrix in range(self._size[0]*self._size[1]):
                randomIndex = np.random.randint(0, len(pictures))
                newMatrix.append(pictures[randomIndex])
                pictures.remove(pictures[randomIndex])
        elif keep:  # Keep previous Matrix
            previousMatrix = np.asarray(previousMatrix)
            newMatrix = previousMatrix
        else:    # New Matrix different from previous matrix
            newMatrix = previousMatrix
            while np.any(newMatrix == previousMatrix):
                newMatrix = []
                perm = np.random.permutation(numberClasses)
                newClassesPictures = np.asarray(listPictures)[perm]
                newClassesPictures = np.ndarray.tolist(newClassesPictures)
                for itemMatrix in matrixTemplate:
                    currentClass = newClassesPictures[itemMatrix]
                    randomIndex = np.random.randint(0, len(currentClass))
                    newMatrix.append(currentClass[randomIndex])
                    newClassesPictures[itemMatrix].remove(currentClass[randomIndex])

        return newMatrix

    def associatePictures(self, newMatrix, pictureFolder=picturesFolder):
        nPict = 0
        for nCard in range(self._matrix.size):
            if nCard not in removeCards:
                if newMatrix[nPict][0] in classPictures:
                    self._matrix.item(nCard).setPicture(
                        join(picturesFolderClass[newMatrix[nPict][0]], newMatrix[nPict]), False, picture=newMatrix[nPict])
                else:
                    self._matrix.item(nCard).setPicture(
                        join(pictureFolder, newMatrix[nPict]), False, picture=newMatrix[nPict])
                self._matrix.item(nCard).stimuli[0].scale(self._matrix.item(nCard).size[0]/float(300))
                self._listPictures.append(newMatrix[nPict])
                nPict += 1

    def newRecognitionMatrix(self, previousMatrix, category):
        tempListPictures = list(listPictures[category])

        # Filling matrix with images
        newMatrix = tempListPictures
        random.shuffle(newMatrix)
        while np.any(np.array(newMatrix) == np.array(previousMatrix)):
            random.shuffle(newMatrix)

        return newMatrix

    def associateSounds(self, newMatrix, soundsAllocation):
        nPict = 0
        for nCard in range(self._matrix.size):
            if nCard not in removeCards:
                picture = newMatrix[nPict].rstrip('.png')
                for i in range(numberClasses):
                    if classPictures[i] in picture:  # if card belongs to the the i-th class of pictures
                        # associate this class' sound to the card
                        self._matrix.item(nCard).setSound(soundsAllocation[i])
                nPict += 1

    def checkPosition(self, position, cue_card=False):
        if not cue_card:
            for nCard in range(self._matrix.size):
                if nCard not in removeCards:
                    if self._matrix.item(nCard).stimuli[1].overlapping_with_position(position):
                        return nCard
            return None
        else:
            for cuecard_index in range(len(classPictures)):
                if (self._cueCard[cuecard_index]).stimuli[1].overlapping_with_position(position):
                    return cuecard_index
            return None

    def response_feedback_stimuli_frame(self, bs, position, subject_correct, show_or_hide=True, draw=False,
                                        no_feedback=False):
        if show_or_hide:
            if not no_feedback:
                if subject_correct:
                    color = feedback_frame_correct_color
                else:
                    color = feedback_frame_wrong_color
            else:
                color = constants.C_BLACK
        else:
            color = bgColor

        geometry.vertices_frame(size=(110, 110), frame_thickness=10)
        response_stimuli = Shape(position=position,
                                 vertex_list=geometry.vertices_frame(size=(110, 110), frame_thickness=10),
                                 colour=color)

        response_stimuli.plot(bs)
        if draw:
            bs.present(False, True)
        else:
            return bs

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._matrix = np.ndarray(shape=value, dtype=np.object)
        self._size = value

    @property
    def gap(self):
        return self._gap

    @property
    def windowSize(self):
        return self._windowSize

    @property
    def listPictures(self):
        return self._listPictures