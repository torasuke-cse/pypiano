# -*- coding:utf-8 -*-
import pygame
import pygame.midi
from pygame.locals import *
import sys

SCREEN_SIZE = (600, 400)
IMAGE_FILE = "./resources/731A9867.JPG"
WINDOW_TITLE = "PyPiano"

def main():
    pygame.init()                                     # Pygameの初期化
    pygame.midi.init()                                # Pygame.midiの初期化
    pygame.fastevent.init()                           # Pygame.fasteventの初期化

    print("Count of MIDI devices: " + str(pygame.midi.get_count()))
    device_id = int(input("Choose device_id: "))
    print(pygame.midi.get_device_info(device_id))
    midi_device = pygame.midi.Input(device_id)
    print("MIDI Device: " + str(midi_device))
    input("Press any key to continue...")

    screen = pygame.display.set_mode(SCREEN_SIZE)     # 画面生成
    image = pygame.image.load(IMAGE_FILE).convert()   # 画像読み込み
    pygame.display.set_caption(WINDOW_TITLE)          # タイトルバーに表示する文字

    screen.fill((0,0,0))         # 画面を黒色(#000000)に塗りつぶし
    screen.blit(image, (0, 0))   # 画像表示
    pygame.display.update()      # 画面を更新
    pygame.time.delay(500)

    while True:

        #if pygame.event.poll() != pygame.NOEVENT:
        for event in pygame.event.get():
            if event.type == QUIT:   # 閉じるボタンが押されたら終了
                pygame.quit()        # Pygameの終了(画面閉じられる)
                sys.exit()
        if midi_device.poll():
            print("MIDI poll")
            for event in midi_device.read(1):
                print("MIDI read: " + str(event))
        pygame.time.wait(20)


if __name__ == "__main__":
    main()


