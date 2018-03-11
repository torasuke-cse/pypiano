#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
PyPiano!
This application makes you to be easy to read musical scores rapidly.
"""

__author__    = 'MIYAZAKI Masafumi (The Project Fukurous)'
__date__      = '2018/03/07'
__version__   = '0.1.0'

__copyright__ = "Copyright 2017-2018 MIYAZAKI Masafumi (The Project Fukurous)"
__license__   = 'The 2-Clause BSD License'


import org.fukurous.utils.filesystem
import pygame
from   pygame.locals import QUIT
import pygame.midi
import sys
import xml.etree.ElementTree

class PyPiano(object):

    FILE_FOR_PROPERTIES = "./xml/properties.xml"
    DIRECTORY_FOR_CASES = "./cases"
    DIRECTORY_FOR_SUITES = "./suites"

    def __init__(self):
        self.WINDOW_TITLE = "PyPiano"
        self.SCREEN_SIZE = (600, 400)
        self.COLOR_BLACK = (0, 0, 0)
        self.EXIT_SUCCESS = 0
        self.device_id = None
        self.midi_device = None
        self.screen = None

    def perform(self):
        self.initialize()
        self.select_device()
        self.select_suite()
        self.execute_suite()
        self.finalize()
        return self.EXIT_SUCCESS

    def initialize(self):
        pygame.init()
        pygame.midi.init()
        pygame.fastevent.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.display.set_caption(self.WINDOW_TITLE)
        self.screen.fill(self.COLOR_BLACK)
        #image = pygame.image.load(IMAGE_FILE).convert()
        #screen.blit(image, (0, 0))
        pygame.display.update()

    def select_device(self):
        print("Count of MIDI devices: " + str(pygame.midi.get_count()))
        self.device_id = int(input("Choose device_id: "))
        print("MIDI Device: " + str(pygame.midi.get_device_info(self.device_id)))
        self.midi_device = pygame.midi.Input(self.device_id)
        input("Press any key to continue...")

    def select_suite(self):
        pass

    def execute_suite(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:   # Exit on press Quit button.
                    return
            if self.midi_device.poll():
                for event in self.midi_device.read(1):
                    print("MIDI read: " + str(event))
            pygame.time.wait(20)

    def finalize(self):
        self.midi_device.close()
        pygame.midi.quit()
        pygame.quit()


class Properties(object):

    def __init__(self, xml_filename):
        self.tree = xml.etree.ElementTree.parse(xml_filename)
        self.dictionary = dict()
        for element in self.tree.findall(".//property"):
            self.dictionary[element.get("key")] = element.get("value")

    def getByKey(self, key):
        return self.dictionary[key]

    def setByKey(self, key, value):
        self.dictionary[key] = value


class PracticeSuites(object):

    def __init__(self, directory):
        self.suites = dict()

    def getById(self, id_name):
        return self.suites[id_name]


class PracticeSuite(object):

    def __init__(self, xml_filename):
        self.dictionary = dict()
        self.tree = xml.etree.ElementTree.parse(xml_filename)
        self.id = self.tree.getroot().get("id")
        for element in self.tree.findall(".//case"):
            pass   ################ not yet


class PracticeCases(object):

    def __init__(self, directory):
        self.cases = dict()
        for xml_file in org.fukurous.utils.filesystem.filelist_recursive(directory):
            xml_filename = str(xml_file)
            self.tree = xml.etree.ElementTree.parse(xml_filename)
            for case in self.tree.findall(".//case"):
                type_name = case.get("type")
                if type_name == "score":
                    id_name = case.get("id")
                    key = case.find("./score").get("key")
                    notes = list()
                    for note in case.findall("./notes/note"):
                        notes.append(Note(note.get("name")))
                    self.cases[id_name] = PracticeCaseAsScore(id_name, key, notes)
                elif type_name == "chord":
                    pass   ##### TODO #####
                elif type_name == "sound":
                    pass   ##### TODO #####
                else:
                    pass   # Unexpected case. Nothing to do....

    def getById(self, id_name):
        return self.cases[id_name]


class PracticeCase(object):

    def __init__(self, id_name, notes):
        self.id = id_name
        self.notes = notes

    def getId(self):
        return self.id

    def getNotes(self):
        return self.notes


class PracticeCaseAsScore(PracticeCase):

    def __init__(self, id_name, key, notes):
        super().__init__(id_name, notes)
        self.key = key

    def getKey(self):
        return self.key


class PracticeCaseAsChord(PracticeCase):

    def __init__(self, id_name, chord, notes):
        super.__init__(id_name, notes)
        self.chord = chord

    def getChord(self):
        return self.chord


class PracticeCaseAsSound(PracticeCase):

    def __init__(self, id_name, notes):
        super.__init__(id_name, notes)


class Note(object):

    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name


def readXmlForTest():
    #properties = Properties(PyPiano.FILE_FOR_PROPERTIES)
    #print(properties.getByKey("KeyImage_CM"))

    #cases = PracticeCases(PyPiano.DIRECTORY_FOR_CASES)
    #print(cases.getById("Score_CM_C7").getNotes()[0].getName())

    return 0


def main():
    """ Main routine """
    #instance = PyPiano()
    #return_code = instance.perform()
    return_code = readXmlForTest()
    return return_code


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)

