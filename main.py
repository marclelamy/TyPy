from turtle import pu
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
sentence_length = 25#np.random.randint(25, 40)
max_word_length = None
capitalized_words_count = 0 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
capitalized_letters_count_perc = 0 # Set a float between 0 and 1 for the percentage of the letters of the word that will be capitalized. Set an integer for the nmumber or random case statement letters. 1 is all letters capitalized not 1 word. if 'first' then only first letter will be capitalized
punctuation_word_count_perc = .3 # Same as above but for punctuation around the word
force_shift = True # Force to type the right shift of the keyboard




def load_text (file_path=f'{current_dir}/data/common_words.txt') -> list:
    '''a '''
    with open(file_path) as file: 
        all_words = file.read().split('\n')

    return all_words



def capitalize_random(sentence):
    capitalized_words_sentence_count = round(len(sentence) * capitalized_words_count)

    for index in range(capitalized_words_sentence_count):
        word = sentence[index]

        if type(capitalized_letters_count_perc) in [int, float]:
            if capitalized_letters_count_perc <= 1:
                capitalized_letters_sentence_count_perc = round(len(word) * capitalized_letters_count_perc)

            rdm_list = list(range(len(word)))
            np.random.shuffle(rdm_list)
            rdm_list = rdm_list[:capitalized_letters_sentence_count_perc]
            sentence[index] = ''.join([char.upper() if index_char in rdm_list else char for index_char, char in enumerate(word)])

        elif capitalized_letters_count_perc == 'first':
            sentence[index] = word.title()

    np.random.shuffle(sentence)

    return sentence



def add_punctuation (sentence: list):
    punctuation_sentence_count = round(len(sentence) * punctuation_word_count_perc)
    print(punctuation_sentence_count)
    common_punctuations = ['()', '{}', '[]', '!', "''", '*', ',', '.', ';', ':', '-', '_', ]
    common_punctuations = [':']
    rdm_punctuation = np.random.choice(common_punctuations)

    for index in range(punctuation_sentence_count):
        word = sentence[index]
        
        if len(rdm_punctuation) == 2:
            word = rdm_punctuation[0] + word + rdm_punctuation[1]
        else:
            word += rdm_punctuation

        sentence[index] = word

    np.random.shuffle(sentence)

    return sentence



def pick_words(word_list, capitalize=False, punctuation=False):
    '''returns a word based on criterias'''

    sentence = []
    while len(sentence) < sentence_length:
        picked_word = np.random.choice(word_list).lower()

        if max_word_length == None:
            sentence.append(picked_word)

        elif len(picked_word) <= max_word_length:
            sentence.append(picked_word)


    sentence = capitalize_random(sentence)
    sentence = add_punctuation(sentence)

    return ' '.join(sentence)





def log_key_pressed(key_pressed):
    column_names = ['key', 'correct_key', 'time', 'game_id']
    df_keys = pd.DataFrame(key_pressed, columns=column_names)
    df_keys.to_sql('keys_pressed', con, if_exists='append', index=False)

def log_game_settings(game_settings):
    column_names = ['sentence', 'sentence_length', 'max_word_length', 'game_id', 'capitalized_words_count', 'capitalized_letters_count_perc', 'punctuation_word_count_perc', 'force_shift']
    df_game_settings = pd.DataFrame([game_settings], columns=column_names)
    df_game_settings.to_sql('games_settings', con, if_exists='append', index=False)



def next_key_pressed():
    key_map_shift = {'`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', 'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T', 'y': 'Y', 'u': 'U', 'i': 'I', 'o': 'O', 'p': 'P', '[': '{', ']': '}', "''": '|', 'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L', ';': ':', "'": '"', 'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B', 'n': 'N', 'm': 'M', ',': '<', '.': '>', '/': '?'}
    key = None
    count = 0
    while key==None:
        # Checking if any shift is pressed
        mods = pygame.key.get_mods()
        left_shift_pressed = True if mods and pygame.KMOD_LSHIFT else False
        right_shift_pressed = True if mods and pygame.KMOD_RSHIFT else False
        shift_pressed = True if True in (left_shift_pressed, right_shift_pressed) else False

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                guess = pygame.key.name(event.key)
                
                if shift_pressed and guess != 'space':
                    guess = key_map_shift[guess] if shift_pressed is True else guess
                    
                key=guess
                break

        count += 1

    return guess, 'right' if right_shift_pressed == True else ('left' if left_shift_pressed == True else None)


def whats_highscore ():
    query = """
    with tbl1 as (
    select
        game_id
        , max(time) - min(time) game_duration
        , sum(case when correct_key = 1 then 1 else 0 end) keys_to_press
        , count(*) keys_pressed
        , round(CAST(sum(case when correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) accuracy
        , round(sum(case when correct_key = 1 then 1 else 0 end) / ((max(time) - min(time)) / 60) / 5) wpm

    from keys_pressed
    where 1=1
        --and game_id = 3513153090
    group by 1
    having
        count(*) >= 20
    )

    select * from tbl1
    where wpm = (select max(wpm) from tbl1)
    """

    df_high_score = pd.read_sql_query(query, con)
    game_duration = df_high_score.loc[0, 'game_duration']
    keys_to_press = df_high_score.loc[0, 'keys_to_press']
    keys_pressed = df_high_score.loc[0, 'keys_pressed']
    accuracy = df_high_score.loc[0, 'accuracy']
    wpm = df_high_score.loc[0, 'wpm']
    return f'Char to type: {keys_to_press} | Char typed: {keys_pressed} | Game duration: {int(game_duration)}s | Typing Accuracy: {accuracy:.1%} | WPM: {round(wpm)} | Score: {round(accuracy * wpm * 100)}' 



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
    accuracy = char_to_type / char_typed
    wpm = char_to_type / (game_duration / 60) / 5

    score = f'Char to type: {char_to_type} | Char typed: {char_typed} | Game duration: {int(game_duration)}s | Typing Accuracy: {accuracy:.1%} | WPM: {round(wpm)} | Score: {round(accuracy * wpm * 100)}'
    best_score = whats_highscore ()
    if score == best_score:
        for _ in range(10):
            print('RECORD\t'*10)
        print(score)
    else:
        print(score)
        print('\nRECORD\n', best_score)


def rule_force_shift(key_pressed, shift_pressed):
    right = '&*()_+|}{POIUYHJKL:"?><MNB'
    left = '~!@#$%^QWERTGFDSAZXCVB'

    if key_pressed not in eval(shift_pressed):
        print(key_pressed, shift_pressed)
        print(key_pressed, shift_pressed, eval(shift_pressed))
        print('WRONG SHIFT KEY', '\n'*2)
        return ' '

    else:
        return key_pressed



def main():
    # Generating text to be typed
    text = load_text()
    sentence = pick_words(text, punctuation=False)

    game_settings = [sentence, sentence_length, max_word_length, game_id, capitalized_words_count, capitalized_letters_count_perc, punctuation_word_count_perc, force_shift]
    print(game_settings)

    
    # Looping through each character to compare them to the last key pressed
    key_pressed = []
    sentence = sentence + '⏎' # Adding one character at the end to validate the game (type enter)
    print('\n'*5)
    for index, char in enumerate(sentence):
        # Replacing space by spelled word space to match it to the key
        if char == ' ':
            char = 'space'
        
        # Printing updated sentence
        if index == len(game_settings[0]): 
            print('No more letters, press ENTER to save the game, any other to not.')
        else:     
            print('\n'*20)
            words_to_display_count = 5
            words_to_display = ' '.join(sentence.split(' ')[:words_to_display_count])
            print(' ', words_to_display, '\t'*5, end='\r')

        # Looping through event key until the right key is pressed
        guess = '' 
        while guess != char:
            guess, shift_pressed = next_key_pressed()
            print(guess, shift_pressed)

            if force_shift == True and shift_pressed != None:
                guess = rule_force_shift(guess, shift_pressed)





   




    
            # print(guess, char, sentence[-1], index, len(game_settings[0]), guess == char, guess == 'return' and index == len(game_settings[0]))
            
            if index == len(game_settings[0]): # For last character of sentence only
                if guess == 'return': # If last key pressed is enter, log the game otherwise not
                    log_game = True
                else:
                    if guess != 'return':
                        double_check = input('Are you sure? Press ENTER to save the game')
                        if double_check == '':
                            log_game = True
                    else:        
                        log_game = False
                guess = char
                break
            
            
            else:
                if guess == char: 
                    correct_key = True
                    key_pressed.append([str(guess), correct_key, time.time(), game_id]) 
                    sentence = sentence[1:]
                    break
                else:
                    
                    correct_key = False
                    print(guess, words_to_display)
                    key_pressed.append([str(guess), correct_key, time.time(), game_id]) 


    if log_game == True:
        log_key_pressed(key_pressed=key_pressed)
        log_game_settings(game_settings)

    score_game(key_pressed)










main()