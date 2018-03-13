#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
PyPiano!
This application makes you to be easy to read musical scores rapidly.
"""

__author__    = 'MIYAZAKI Masafumi (The Project Fukurous)'
__date__      = '2018/03/13'
__version__   = '0.1.1'

__copyright__ = "Copyright 2017-2018 MIYAZAKI Masafumi (The Project Fukurous)"
__license__   = 'The 2-Clause BSD License'


import org.fukurous.utils.filesystem
import pygame
from   pygame.locals import QUIT
import pygame.midi
import pygame.transform
import sys
import xml.etree.ElementTree

class PyPiano(object):

    FILE_FOR_PROPERTIES = "./xml/properties.xml"

    def __init__(self):
        self.props = Properties(PyPiano.FILE_FOR_PROPERTIES)
        self.WINDOW_TITLE = self.props.get("WindowTitle")
        self.SCREEN_SIZE = (int(self.props.get("WindowWidth")), int(self.props.get("WindowHeight")))
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_TRANSPARENCY = (255, 255, 255, 0)
        self.EXIT_SUCCESS = 0
        self.EXIT_FAILURE = 1
        self.midi_device = None
        self.canvas = None   # Surface for drawing
        self.screen = None   # Surface for displaying
        self.practice_cases = PracticeCases(self.props.get("DirectoryForCases"))
        self.previous_case = None
        self.current_case = None
        self.notes_image_height = 1500

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
        self.screen.fill(self.COLOR_WHITE)
        #image = pygame.image.load(IMAGE_FILE).convert()
        #screen.blit(image, (0, 0))
        pygame.display.update()

    def select_device(self):
        print("Count of MIDI devices: " + str(pygame.midi.get_count()))
        device_id = int(input("Choose device_id: "))
        print("MIDI Device: " + str(pygame.midi.get_device_info(device_id)))
        self.midi_device = pygame.midi.Input(device_id)
        input("Press any key to continue...")

    def select_suite(self):
        pass   ##### TODO #####

    def execute_suite(self):
        while True:
            self.select_case()
            self.display_case()
            self.wait_answer()
            self.display_answer()
            pygame.time.wait(self.props.get("IntervalTime"))

    def select_case(self):
        self.previous_case = self.current_case
        self.current_case = self.practice_cases.getById("Score_CM_C5")   ##### TODO ##### This is a sample!

    def display_case(self):
        self.screen.fill(self.COLOR_WHITE)
        if isinstance(self.current_case, PracticeCaseAsScore):
            self.draw_case_as_score()
        elif isinstance(self.current_case, PracticeCaseAsChord):
            self.draw_case_as_chord()
        elif isinstance(self.current_case, PracticeCaseAsSound):
            self.draw_case_as_sound()
        else:
            pass   # Unexpected case. Nothing to do....
        self.display_canvas_on_screen()
        pygame.display.update()

    def draw_case_as_score(self, is_as_answer = None):
        head_image  = self.get_head_image()
        key_image   = self.get_key_image()
        lines_image = self.get_lines_image()
        notes_image = self.get_notes_image(is_as_answer)
        whole_width  = head_image.get_width() + key_image.get_width() + lines_image.get_width()
        whole_height = max(head_image.get_height(), key_image.get_height(), lines_image.get_height())
        self.canvas = pygame.Surface((whole_width, whole_height))
        self.canvas.fill(self.COLOR_WHITE)
        head_position_x  = 0
        key_position_x   = head_position_x  + head_image.get_width()
        lines_position_x = key_position_x   + key_image.get_width()
        notes_position_x = lines_position_x + int(self.props.get("NoteOffsetX"))
        self.canvas.blit(head_image,  (head_position_x,  0))
        self.canvas.blit(key_image,   (key_position_x,   0))
        self.canvas.blit(lines_image, (lines_position_x, 0))
        self.canvas.blit(notes_image, (notes_position_x, 0))

    def get_head_image(self):
        return self.get_image(self.props.get("HeadImage"))

    def get_key_image(self):
        return self.get_image(self.props.get("KeyImage_" + self.current_case.getKey()))

    def get_lines_image(self):
        ##### TODO ##### This is a sample!
        base_image = self.get_image(self.props.get("LineImage_Base"))
        scaled_width = int(self.props.get("LineWidth"))
        scaled_height = base_image.get_height()
        return pygame.transform.scale(base_image, (scaled_width, scaled_height))

    def get_notes_image(self, is_as_answer = None):
        if is_as_answer:
            note_image = self.get_image(self.props.get("NoteImageAsAnswer"))
        else:
            note_image = self.get_image(self.props.get("NoteImage"))
        notes_image = pygame.Surface((note_image.get_width(), self.notes_image_height)).convert_alpha()
        notes_image.fill(self.COLOR_TRANSPARENCY)
        for note in self.current_case.getNotes():
            note_name = note.getName()
            note_y = int(self.props.get("NotePositionY_" + note_name))
            if (note_y + note_image.get_height()) > self.notes_image_height:
                self.notes_image_height = note_y + note_image.get_height()
                notes_image = pygame.Surface((note_image.get_width(), self.notes_image_height)).convert_alpha()
                notes_image.fill(self.COLOR_TRANSPARENCY)
            notes_image.blit(note_image, (0, note_y))
        return notes_image

    def get_image(self, filename):
        return pygame.image.load(filename).convert_alpha()

    def draw_case_as_chord(self):
        pass   ##### TODO #####

    def draw_case_as_sound(self):
        pass   ##### TODO #####

    def display_canvas_on_screen(self):
        scaled_width = int(self.canvas.get_width() * float(self.props.get("DisplayScale")))
        scaled_height = int(self.canvas.get_height() * float(self.props.get("DisplayScale")))
        scaled_canvas = pygame.transform.scale(self.canvas, (scaled_width, scaled_height))
        start_x = (self.screen.get_width() - scaled_canvas.get_width()) / 2
        start_y = (self.screen.get_height() - scaled_canvas.get_height()) / 2
        self.screen.blit(scaled_canvas, (start_x, start_y))

    def wait_answer(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:   # Exit on press Quit button.
                    return
                    #### TODO #####
            if self.midi_device.poll():
                for event in self.midi_device.read(10):
                    print("MIDI read: " + str(event))
                    #### TODO #####
            pygame.time.wait(20)

    def display_answer(self):
        self.screen.fill(self.COLOR_WHITE)
        if isinstance(self.current_case, PracticeCaseAsScore):
            self.draw_answer_as_score()
        elif isinstance(self.current_case, PracticeCaseAsChord):
            self.draw_answer_as_chord()
        elif isinstance(self.current_case, PracticeCaseAsSound):
            self.draw_answer_as_sound()
        else:
            pass   # Unexpected case. Nothing to do....
        self.display_canvas_on_screen()
        pygame.display.update()

    def draw_answer_as_score(self):
        is_as_answer = True
        self.draw_case_as_score(is_as_answer)

    def draw_answer_as_chord(self):
        pass   ##### TODO #####

    def draw_answer_as_sound(self):
        pass   ##### TODO #####

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

    def get(self, key):
        return self.getByKey(key)

    def set(self, key, value):
        self.setByKey(key, value)


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
            pass   ##### TODO #####


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
    #print(properties.get("KeyImage_CM"))

    #cases = PracticeCases(PyPiano.DIRECTORY_FOR_CASES)
    #print(cases.getById("Score_CM_C7").getNotes()[0].getName())

    return 0


def main():
    """ Main routine """
    instance = PyPiano()
    return_code = instance.perform()
    #return_code = readXmlForTest()
    return return_code


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)

