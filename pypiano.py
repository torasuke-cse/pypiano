#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
PyPiano!
This application makes you to be easy to read musical scores rapidly.
"""

__author__    = 'MIYAZAKI Masafumi (The Project Fukurous)'
__date__      = '2018/03/18'
__version__   = '0.2.0'

__copyright__ = "Copyright 2017-2018 MIYAZAKI Masafumi (The Project Fukurous)"
__license__   = 'The 2-Clause BSD License'


import datetime
import org.fukurous.utils.filesystem
import pygame
from   pygame.locals import QUIT
import pygame.midi
import pygame.transform
import random
import re
import sys
import xml.etree.ElementTree

import time

class PyPiano(object):

    FILE_FOR_PROPERTIES = "./xml/properties.xml"
    FILE_FOR_LOGGER = "./logs/log.txt"

    def __init__(self):
        self.props = Properties(PyPiano.FILE_FOR_PROPERTIES)
        self.WINDOW_TITLE = self.props.get("WindowTitle")
        self.SCREEN_SIZE = (int(self.props.get("WindowWidth")), int(self.props.get("WindowHeight")))
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_TRANSPARENCY = (255, 255, 255, 0)
        self.EXIT_SUCCESS = 0
        self.EXIT_FAILURE = 1
        self.midi_device = None
        self.midi_output_device = None
        self.canvas = None   # Surface for drawing
        self.screen = None   # Surface for displaying
        self.practice_cases = PracticeCases(self.props.get("DirectoryForCases"))
        self.practice_suites = PracticeSuites(self.props.get("DirectoryForSuites"))
        self.previous_case = None
        self.current_case = None
        self.notes_image_height = 1500
        self.pressing_keys = list()
        self.log_file = None

    def perform(self):
        try:
            self.initialize()
            self.write_info_log("PyPiano started.")
            self.select_device()
            self.select_suite()
            self.execute_suite()
        except NotFoundMidiDeviceException as exception:
            self.write_error_log("Not found MIDI devices")
        except NotFoundMidiInputDeviceException as exception:
            self.write_error_log("Not found MIDI input devices")
        except SystemContinuationException as exception:
            self.write_info_log("Receive a request to exit application")
        finally:
            self.write_info_log("PyPiano stopped.")
            self.finalize()
        return self.EXIT_SUCCESS

    def initialize(self):
        self.log_file = open(PyPiano.FILE_FOR_LOGGER, "a")
        pygame.init()
        pygame.midi.init()
        pygame.fastevent.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        pygame.display.set_caption(self.WINDOW_TITLE)
        self.screen.fill(self.COLOR_WHITE)
        pygame.display.update()

    def select_device(self):
        input_devices = self.get_midi_input_devices()
        self.print_device_list(input_devices)
        device_id = int(input("Choose device_id: "))
        self.midi_device = pygame.midi.Input(device_id)
        self.midi_output_device = pygame.midi.Output(3)
        self.write_info_log("MIDI device connected")

    def get_midi_input_devices(self):
        number_of_midi_devices = pygame.midi.get_count()
        if number_of_midi_devices <= 0:
            raise NotFoundMidiDeviceException
        is_closed_input_device = lambda device: (device[2] == 1 and device[4] == 0)
        input_devices = list()
        for device_id in range(number_of_midi_devices):
            device_info = pygame.midi.get_device_info(device_id)
            if is_closed_input_device(device_info):
                input_devices.append((device_id, device_info))
        if len(input_devices) <= 0:
            raise NotFoundMidiInputDeviceException
        return input_devices

    def print_device_list(self, input_devices):
        print("======= MIDI Devices =======")
        for device in input_devices:
            device_id = device[0]
            device_name = device[1][1].decode()
            print(" " + str(device_id) + " : " + device_name)
        print("============================")

    def select_suite(self):
        suite_list = self.practice_suites.get_list()
        self.print_suite_list(suite_list)
        suite_index = int(input("Choose suite_id: "))
        suite_id = suite_list[suite_index]
        self.current_suite = self.practice_suites.get_by_id(suite_id)

    def print_suite_list(self, suite_list):
        print("========== Suites ==========")
        for (key, value) in enumerate(suite_list):
            suite_index = key
            suite_id = value
            print(" " + str(suite_index) + " : " + suite_id)
        print("============================")

    def execute_suite(self):
        while True:
            self.select_case()
            self.display_case()
            self.write_pre_answer_log()
            self.wait_answer()
            self.write_post_answer_log()
            self.display_answer()
            self.wait_interval()

    def select_case(self):
        self.previous_case = self.current_case
        current_case_id = self.current_suite.choose_one_id()
        self.current_case = self.practice_cases.get_by_id(current_case_id)

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
        return self.get_image(self.props.get("KeyImage_" + self.current_case.get_key()))

    def get_lines_image(self):
        base_image = self.get_image(self.props.get("LineImage_Base"))
        scaled_width = int(self.props.get("LineWidth"))
        scaled_height = base_image.get_height()
        scaled_image = pygame.transform.scale(base_image, (scaled_width, scaled_height))
        additional_lines_image = self.get_additional_lines_image()
        if additional_lines_image is not None:
            additional_lines_offset_x = int(self.props.get("AdditionalLinesOffsetX"))
            scaled_image.blit(additional_lines_image, (additional_lines_offset_x, 0))
        return scaled_image

    def get_additional_lines_image(self):
        additional_line_images = self.get_additional_line_images()
        if len(additional_line_images) == 0:
            return None
        base_image = additional_line_images.pop()
        for additional_line_image in additional_line_images:
            base_image.blit(additional_line_image, (0, 0))
        scaled_width = int(self.props.get("AdditionalLinesWidth"))
        scaled_height = base_image.get_height()
        scaled_image = pygame.transform.scale(base_image, (scaled_width, scaled_height))
        return scaled_image

    def get_additional_line_images(self):
        dictionary = dict()
        for note in self.current_case.get_notes():
            note_name = note.get_position_name()
            note_step = note.get_step()
            if note_step:
                note_y = int(self.props.get("NotePositionY_" + note_name + "_" + note_step))
            else:
                note_y = int(self.props.get("NotePositionY_" + note_name))
            if note_y <= int(self.props.get("NotePositionY_B6")):
                self.add_line_image_into_dictionary("LineImage_Upper_Top5th", dictionary)
            if note_y <= int(self.props.get("NotePositionY_G6")):
                self.add_line_image_into_dictionary("LineImage_Upper_Top4th", dictionary)
            if note_y <= int(self.props.get("NotePositionY_E6")):
                self.add_line_image_into_dictionary("LineImage_Upper_Top3rd", dictionary)
            if note_y <= int(self.props.get("NotePositionY_C6")):
                self.add_line_image_into_dictionary("LineImage_Upper_Top2nd", dictionary)
            if note_y <= int(self.props.get("NotePositionY_A5")):
                self.add_line_image_into_dictionary("LineImage_Upper_Top1st", dictionary)
            if (note.step is None and
                note_y >= int(self.props.get("NotePositionY_C4_Upper")) and
                note_y <= int(self.props.get("NotePositionY_G3_Upper"))):
                self.add_line_image_into_dictionary("LineImage_Upper_Bottom1st", dictionary)
            if (note.step is None and
                note_y >= int(self.props.get("NotePositionY_A3_Upper")) and
                note_y <= int(self.props.get("NotePositionY_G3_Upper"))):
                self.add_line_image_into_dictionary("LineImage_Upper_Bottom2nd", dictionary)
            if (note.step == "Upper" and
                note_y >= int(self.props.get("NotePositionY_C4_Upper")) and
                note_y <= int(self.props.get("NotePositionY_G3_Upper"))):
                self.add_line_image_into_dictionary("LineImage_Upper_Bottom1st", dictionary)
            if (note.step == "Upper" and
                note_y >= int(self.props.get("NotePositionY_A3_Upper")) and
                note_y <= int(self.props.get("NotePositionY_G3_Upper"))):
                self.add_line_image_into_dictionary("LineImage_Upper_Bottom2nd", dictionary)
            if (note.step == "Lower" and
                note_y >= int(self.props.get("NotePositionY_F4_Lower")) and
                note_y <= int(self.props.get("NotePositionY_E4_Lower"))):
                self.add_line_image_into_dictionary("LineImage_Lower_Top2nd", dictionary)
            if (note.step == "Lower" and
                note_y >= int(self.props.get("NotePositionY_F4_Lower")) and
                note_y <= int(self.props.get("NotePositionY_C4_Lower"))):
                self.add_line_image_into_dictionary("LineImage_Lower_Top1st", dictionary)
            if note_y >= int(self.props.get("NotePositionY_E2")):
                self.add_line_image_into_dictionary("LineImage_Lower_Bottom1st", dictionary)
            if note_y >= int(self.props.get("NotePositionY_C2")):
                self.add_line_image_into_dictionary("LineImage_Lower_Bottom2nd", dictionary)
            if note_y >= int(self.props.get("NotePositionY_A1")):
                self.add_line_image_into_dictionary("LineImage_Lower_Bottom3rd", dictionary)
            if note_y >= int(self.props.get("NotePositionY_F1")):
                self.add_line_image_into_dictionary("LineImage_Lower_Bottom4th", dictionary)
            if note_y >= int(self.props.get("NotePositionY_D1")):
                self.add_line_image_into_dictionary("LineImage_Lower_Bottom5th", dictionary)
        return list(dictionary.values())

    def add_line_image_into_dictionary(self, key, dictionary):
        if key not in dictionary.keys():
            dictionary[key] = self.get_image(self.props.get(key))

    def get_notes_image(self, is_as_answer = None):
        if is_as_answer:
            note_image = self.get_image(self.props.get("NoteImageAsAnswer"))
        else:
            note_image = self.get_image(self.props.get("NoteImage"))
        notes_image = pygame.Surface((note_image.get_width(), self.notes_image_height)).convert_alpha()
        notes_image.fill(self.COLOR_TRANSPARENCY)
        for note in self.current_case.get_notes():
            note_name = note.get_position_name()
            note_step = note.get_step()
            if note_step:
                note_y = int(self.props.get("NotePositionY_" + note_name + "_" + note_step))
            else:
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
        ### 1. Display a speaker image.
        whole_width = int(self.props.get("WindowWidth"))
        whole_height = int(self.props.get("WindowHeight"))
        self.canvas = pygame.Surface((whole_width, whole_height))
        self.canvas.fill(self.COLOR_WHITE)
        ### 2. Play the sound according to selected case.

        print("Note on!")
        self.midi_output_device.note_on(64, 127)

        time.sleep(1)

        print("Note off!")
        self.midi_output_device.note_off(64, 127)
        pass

    def display_canvas_on_screen(self):
        scaled_width = int(self.canvas.get_width() * float(self.props.get("DisplayScale")))
        scaled_height = int(self.canvas.get_height() * float(self.props.get("DisplayScale")))
        scaled_canvas = pygame.transform.scale(self.canvas, (scaled_width, scaled_height))
        start_x = (self.screen.get_width() - scaled_canvas.get_width()) / 2
        start_y = (self.screen.get_height() - scaled_canvas.get_height()) / 2
        self.screen.blit(scaled_canvas, (start_x, start_y))

    def wait_answer(self):
        answer_dictionary = self.create_answer_dictionary()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:   # Exit on press Quit button.
                    raise SystemContinuationException
            if self.midi_device.poll():
                for event in self.midi_device.read(10):
                    self.write_info_log("MIDI event got : " + str(event))
                    midi_event = MidiEvent(event)
                    note_number_string = str(midi_event.get_data1())
                    if note_number_string in answer_dictionary:
                        if midi_event.is_note_on():
                            answer_dictionary[note_number_string] = True
                        elif midi_event.is_note_off():
                            answer_dictionary[note_number_string] = False
                if list(answer_dictionary.values()).count(True) == len(answer_dictionary):
                    return
            pygame.time.wait(20)

    def create_answer_dictionary(self):
        dictionary = dict()
        for note in self.current_case.get_notes():
            note_number_string = self.props.get("NoteNumber_" + note.get_name())
            dictionary[note_number_string] = False
        return dictionary

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

    def wait_interval(self):
        pygame.event.pump()
        pygame.time.wait(int(self.props.get("IntervalTime")))

    def write_pre_answer_log(self):
        self.write_info_log_with_action("displayed")

    def write_post_answer_log(self):
        self.write_info_log_with_action("answered")

    def write_info_log_with_action(self, action):
        self.write_info_log("Case(" + self.current_case.get_id() + ") in Suite(" + self.current_suite.get_id() + ") is " + action + ".")

    def write_info_log(self, message):
        self.write_log_with_tag("[Info]", message)

    def write_error_log(self, message):
        self.write_log_with_tag("[Error]", message)

    def write_log_with_tag(self, tag, message):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        self.write_log("[" + timestamp + "]" + tag + " " + message)

    def write_log(self, message):
        print(message)
        self.log_file.write(message + "\n")

    def finalize(self):
        if self.midi_device is not None:
            self.midi_device.close()
        pygame.midi.quit()
        pygame.quit()
        if (self.log_file is not None) and (self.log_file.closed is False):
            self.log_file.close()


class Properties(object):

    def __init__(self, xml_filename):
        self.tree = xml.etree.ElementTree.parse(xml_filename)
        self.dictionary = dict()
        for element in self.tree.findall(".//property"):
            self.dictionary[element.get("key")] = element.get("value")

    def get_by_key(self, key):
        return self.dictionary[key]

    def set_by_key(self, key, value):
        self.dictionary[key] = value

    def get(self, key):
        return self.get_by_key(key)

    def set(self, key, value):
        self.set_by_key(key, value)


class PracticeSuites(object):

    def __init__(self, directory):
        self.suites = dict()
        for xml_file in org.fukurous.utils.filesystem.filelist_recursive(directory):
            xml_filename = str(xml_file)
            self.tree = xml.etree.ElementTree.parse(xml_filename)
            for suite_node in self.tree.findall(".//suite"):
                self.suites[suite_node.get("id")] = PracticeSuite(suite_node)

    def get_by_id(self, id_name):
        return self.suites[id_name]

    def get_list(self):
        return sorted(list(self.suites.keys()))


class PracticeSuite(object):

    def __init__(self, suite_node, randomly = True):
        self.dictionary = dict()
        self.total_rate = 0
        self.id = suite_node.get("id")
        for element in suite_node.findall(".//case"):
            rate = int(element.get("rate"))
            self.dictionary[element.get("id")] = rate
        for key in self.dictionary.keys():
            self.total_rate = self.total_rate + self.dictionary[key]
        self.current_index = -1
        self.randomly = randomly

    def get_id(self):
        return self.id

    def choose_one_id(self):
        if self.randomly:
            return self.choose_one_id_randomly()
        else:
            return self.choose_one_id_sequentially()

    def choose_one_id_randomly(self):
        random_number = random.randint(1, self.total_rate)
        threshold = 0
        for key in self.dictionary.keys():
            threshold = threshold + self.dictionary[key]
            if threshold >= random_number:
                break
        chosen_id = key
        return chosen_id

    def choose_one_id_sequentially(self):
        self.current_index = self.current_index + 1
        if self.current_index >= len(self.dictionary):
            self.current_index = 0
        return list(self.dictionary.keys())[self.current_index]


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
                    for note_node in case.findall("./notes/note"):
                        note_name = note_node.get("name")
                        note_step = note_node.get("step")
                        if note_step:
                            note = Note(note_name, note_step)
                        else:
                            note = Note(note_name)
                        notes.append(note)
                    self.cases[id_name] = PracticeCaseAsScore(id_name, key, notes)
                elif type_name == "chord":
                    pass   ##### TODO #####
                elif type_name == "sound":
                    pass   ##### TODO #####
                else:
                    pass   # Unexpected case. Nothing to do....

    def get_by_id(self, id_name):
        return self.cases[id_name]


class PracticeCase(object):

    def __init__(self, id_name, notes):
        self.id = id_name
        self.notes = notes

    def get_id(self):
        return self.id

    def get_notes(self):
        return self.notes


class PracticeCaseAsScore(PracticeCase):

    def __init__(self, id_name, key, notes):
        super().__init__(id_name, notes)
        self.key = key

    def get_key(self):
        return self.key


class PracticeCaseAsChord(PracticeCase):

    def __init__(self, id_name, chord, notes):
        super.__init__(id_name, notes)
        self.chord = chord

    def get_chord(self):
        return self.chord


class PracticeCaseAsSound(PracticeCase):

    def __init__(self, id_name, notes):
        super.__init__(id_name, notes)


class Note(object):

    def __init__(self, name, step = None):
        self.name = name
        self.step = step

    def get_name(self):
        return self.name

    def get_position_name(self):
        return re.sub("^(.).?(.)$", r"\1\2", self.name)

    def get_step(self):
        return self.step


class MidiEvent(object):

    def __init__(self, event):
        self.raw_event = event

    def get_status(self):
        return self.raw_event[0][0]

    def get_data1(self):
        return self.raw_event[0][1]

    def get_data2(self):
        return self.raw_event[0][2]

    def get_data3(self):
        return self.raw_event[0][3]

    def get_timestamp(self):
        return self.raw_event[1]

    def is_note_on(self):
        return (self.raw_event != None) and (self.get_status() == 0x90)

    def is_note_off(self):
        return (self.raw_event != None) and (self.get_status() == 0x80)


class SystemContinuationException(Exception):
    
    pass


class NotFoundMidiDeviceException(Exception):

    pass


class NotFoundMidiInputDeviceException(Exception):

    pass


def main():
    """ Main routine """
    instance = PyPiano()
    return_code = instance.perform()
    return return_code


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)

