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


import pygame
from   pygame.locals import QUIT
import pygame.midi
import sys
import xml.etree.ElementTree

class PyPiano(object):

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


def readXmlForTest():
    tree = xml.etree.ElementTree.parse("./xml/properties.xml")
    print(str(tree))
    print("-----")
    for element in tree.findall(".//property"):
        print(str(element.get("name") + " -> " + element.get("value")))
    print("-----")
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

