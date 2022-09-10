# for random functions
from random import random
import numpy as np
import pygame
import sqlite3
import pandas as pd
import time
from PyDictionary import PyDictionary

pygame.init()
con = sqlite3.connect("database.db")

game_id = np.random.randint(10**10)
sentence_length = 3#np.random.randint(40, 60)
max_word_length = None
me_playing = 1





def load_text (file_path='/Users/marclamy/Desktop/code/typing/data/common_words.txt') -> list:
    with open(file_path) as file: 
        all_words = file.read().split('\n')

    return all_words


def pick_words(word_list, max_word_length, sentence_length=10):
    '''returns a word based on criterias'''

    random_word = []
    while len(random_word) < sentence_length:
        picked_word = np.random.choice(word_list).lower()

        if max_word_length == None:
            random_word.append(picked_word)

        elif len(picked_word) <= max_word_length:
            random_word.append(picked_word)


    return ' '.join(random_word)




dictionary=PyDictionary()
def get_definition (word):
    return dictionary.meaning(word)
    





def log_key_pressed(key_pressed):
    if me_playing == 1:
        column_names = ['key', 'correct', 'time', 'game_id']
        pd.DataFrame(key_pressed, columns=column_names).to_sql('keys_typed', con, if_exists='append', index=False)

def log_game_settings(game_settings):
    if me_playing == 1:
        column_names = ['sentence', 'sentence_length', 'max_word_length', 'game_id']
        pd.DataFrame([game_settings], columns=column_names).to_sql('games_settings', con, if_exists='append', index=False)




def score_game(game_id):
    df = pd.read_sql_query('select * from keys_typed', con)

    first_second, last_second = df.query('game_id == @game_id').iloc[[0, -1], 2]
    game_duration = last_second - first_second
    char_typed = df.query('game_id == @game_id').shape[0]
    char_to_type = df.query('game_id == @game_id and correct == 1').shape[0]
    typing_accuracy = char_to_type / char_typed
    wpm = char_to_type / (game_duration / 60) / 4.7

    print(f'Char to type: {char_to_type} | Char typed: {char_typed} | Game duration: {int(game_duration)} | Typing Accuracy: {typing_accuracy:.1%} | WPM: {round(wpm)}')




def main():
    # Generating text to be typed
    text = load_text()
    sentence = pick_words(text, max_word_length, sentence_length)

    game_settings = []


    # word_meaning = get_definition(word[0])
    # sentence = word + ' - ' + word_meaning[list(word_meaning.keys())[0]][0]
    # sentence = ''.join([char.lower() for char in sentence if char.isalpha() or char in (' ', '-')])
    
    # Looping through each character to compare them to the last key pressed
    key_pressed = []
    for char in sentence:
        if char == ' ':
            char = 'space'

        print('\n'*20)
        first_two_words = ' '.join(sentence.split(' ')[:3])
        print(' ', first_two_words, '\t'*10, end='\r')

        guess = '' 
        while guess != char:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    guess = pygame.key.name(event.key)

                    if guess == char:
                        key_pressed.append([str(guess), True, time.time(), game_id])
                        sentence = sentence[1:]
                        break
                    
                    else:
                        key_pressed.append([str(guess), False, time.time(), game_id])
                        print(guess)


    game_settings = [sentence, sentence_length, max_word_length, game_id]
    log_key_pressed(key_pressed)
    log_game_settings(game_settings)

    score_game(game_id)

main()