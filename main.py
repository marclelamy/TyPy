import numpy as np
import pygame
import sqlite3
import pandas as pd
import time
# from PyDictionary import PyDictionary
import os

pygame.init()
con = sqlite3.connect("database.db")
current_dir = os.getcwd()


# Game settings
game_id = np.random.randint(10**10)
sentence_length = 40 #np.random.randint(25, 40)
max_word_length = None
me_playing = 1





def load_text (file_path=f'{current_dir}/data/common_words.txt') -> list:
    '''a '''
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




# dictionary=PyDictionary()
# def get_definition (word):
    # word_meaning = get_definition(word[0])
    # sentence = word + ' - ' + word_meaning[list(word_meaning.keys())[0]][0]
    # sentence = ''.join([char.lower() for char in sentence if char.isalpha() or char in (' ', '-')])
    # return dictionary.meaning(word)
    





def log_key_pressed(key_pressed):
    if me_playing == 1:
        column_names = ['key', 'correct_key', 'time', 'game_id']
        df_keys = pd.DataFrame(key_pressed, columns=column_names)
        df_keys.to_sql('keys_typed', con, if_exists='append', index=False)

def log_game_settings(game_settings):
    if me_playing == 1:
        column_names = ['sentence', 'sentence_length', 'max_word_length', 'game_id']
        df_game_settings = pd.DataFrame([game_settings], columns=column_names)
        df_game_settings.to_sql('games_settings', con, if_exists='append', index=False)




def score_game(key_pressed=None, game_id=None):
    if key_pressed == None:
        df = pd.read_sql_query(f'select * from keys_typed where game_id = {game_id}', con)
    else:
        column_names = ['key', 'correct_key', 'time', 'game_id']
        df = pd.DataFrame(key_pressed, columns=column_names)

    first_second, last_second = df.iloc[[0, -1], 2]
    game_duration = last_second - first_second
    char_typed = df.shape[0]
    char_to_type = df.query('correct_key == 1').shape[0]
    typing_accuracy = char_to_type / char_typed
    wpm = char_to_type / (game_duration / 60) / 4.7

    print(f'Char to type: {char_to_type} | Char typed: {char_typed} | Game duration: {int(game_duration)}s | Typing Accuracy: {typing_accuracy:.1%} | WPM: {round(wpm)}')




def main():
    # Generating text to be typed
    text = load_text()
    sentence = pick_words(text, max_word_length, sentence_length)

    game_settings = [sentence, sentence_length, max_word_length, game_id]
    print(game_settings)

    
    # Looping through each character to compare them to the last key pressed
    key_pressed = []
    sentence = sentence + ' ' # Adding one character at the end to validate the game (type enter)
    for index, char in enumerate(sentence):
        # Replacing space by spelled word space to match it to the key
        if char == ' ':
            char = 'space'
        
        # Printing au updated sentence
        print('\n'*20)
        words_to_display_count = 3
        words_to_display = ' '.join(sentence.split(' ')[:words_to_display_count])
        print(' ', words_to_display, '\t'*5, end='\r')

        # Looping through event key until the right key is pressed
        guess = '' 
        while guess != char:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    guess = pygame.key.name(event.key)
                    # print(guess, char, sentence[-1], index, len(game_settings[0]), guess == char, guess == 'return' and index == len(game_settings[0]))
                    
                    if index == len(game_settings[0]): # For last character of sentence only
                        if guess == 'return': # If last key pressed is enter, log the game otherwise not
                            log_game = True
                        else:
                            log_game = False
                        guess = char
                        break
                    
                    
                    else:
                        if guess == char: 
                            correct_key = True
                            sentence = sentence[1:]
                            break
                        else:
                            correct_key = False
                            print(guess, words_to_display)

                        key_pressed.append([str(guess), correct_key, time.time(), game_id]) 


    if log_game == True:
        log_key_pressed(key_pressed)
        log_game_settings(game_settings)

    score_game(key_pressed)

main()

