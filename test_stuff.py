from pickle import FALSE
import pygame
import pygame.locals
import joblib 
import json
import numpy as np
pygame.init()



capitalized_words_count = 1 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
capitalized_letters_count = .1 # Set a float between 0 and 1 for the percentage of the letters of the word that will be capitalized. Set an integer for the nmumber or random case statement letters. 1 is all letters capitalized not 1 word
force_shift = True # Force to type the right shift of the keyboard
me_playing = 1



def capitalize_random(sentence):
    capitalized_words_count = 1 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
    capitalized_letters_perc = 0.1
    capitalized_words_count = round(len(sentence) * capitalized_words_count)

    for index_word in range(capitalized_words_count):
        word = sentence[index_word]

        if capitalized_letters_perc <= 1:
            capitalized_letters_count = round(len(word) * capitalized_letters_perc)

        rdm_list = list(range(len(word)))
        np.random.shuffle(rdm_list)
        rdm_list = rdm_list[:capitalized_letters_count]
        sentence[index_word] = ''.join([char.upper() if index_char in rdm_list else char for index_char, char in enumerate(word)])

    np.random.shuffle(sentence)

    return sentence




print(capitalize_random(['jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj', 'dddddddddddddddddddddddddddddddd', 'wwwwwwwwwwwwwwwwwwwwwww', 'ccccccccccc', 'llllllllllllllllllllllllllllllllllllllllllllllllllllllllllll']))