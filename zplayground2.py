# for random functions
from random import random
import numpy as np
import pygame
import sqlite3
import pandas as pd
import time
from PyDictionary import PyDictionary
pygame.init()


def key_pressed():
    key_map_shift = {'`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', 'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T', 'y': 'Y', 'u': 'U', 'i': 'I', 'o': 'O', 'p': 'P', '[': '{', ']': '}', "''": '|', 'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L', ';': ':', "'": '"', 'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B', 'n': 'N', 'm': 'M', ',': '<', '.': '>', '/': '?'}
    key = None
    while key==None:
        # Checking if any shift is pressed
        mods = pygame.key.get_mods()
        left_shift_held = True if mods and pygame.KMOD_LSHIFT else False
        right_shift_held = True if mods and pygame.KMOD_RSHIFT else False
        shift_held = True if True in (left_shift_held, right_shift_held) else False

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                guess = pygame.key.name(event.key)
                
                if shift_held:
                    guess = key_map_shift[guess] if shift_held is True else guess
                    
                key=guess
                break

    return guess


for _ in range(100):
    print(key_pressed())