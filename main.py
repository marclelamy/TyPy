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
sentence_length = 10#np.random.randint(40, 60)
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
    





def log_key_pressed(key, correct):
    if me_playing == 1:
        pd.DataFrame({'key': [str(key)], 'correct': [correct], 'time': [time.time()], 'game_id': [game_id]}).to_sql('keys_typed', con, if_exists='append', index=False)

def log_game_settings(sentence):
    if me_playing == 1:
        pd.DataFrame({'sentence': [sentence], 'sentence_length': [sentence_length], 'max_word_length': [max_word_length], 'game_id': [game_id]}).to_sql('games_settings', con, if_exists='append', index=False)




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
    log_game_settings(sentence)

    # word_meaning = get_definition(word[0])
    # sentence = word + ' - ' + word_meaning[list(word_meaning.keys())[0]][0]
    # sentence = ''.join([char.lower() for char in sentence if char.isalpha() or char in (' ', '-')])
    
    # Looping through each character to compare them to the last key pressed
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
                        log_key_pressed(guess, True) 
                        sentence = sentence[1:]
                        break
                    
                    else:
                        log_key_pressed(guess, False) 
                        print(guess)


    score_game(game_id)

main()