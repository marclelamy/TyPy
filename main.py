# https://datastudio.google.com/u/0/reporting/191d67ab-f6e7-43c6-bd99-37b3e4091ead/page/YJH4C/edit
import numpy as np
import pygame
import sqlite3
import pandas as pd
import shutil
import time
# from PyDictionary import PyDictionary
import os
from termcolor import colored

from src.score import Score
from src.log_data import *




pd.set_option('display.float_format', lambda x: '%.2f' % x)
pygame.init()
database_path = "data/main_database.db"
this_is_first_game = False if os.path.isfile(database_path) else True
con = sqlite3.connect("data/main_database.db")
current_dir = os.getcwd()


clean_games_settings()
log_summary_per_game()

 


# Game settings
game_id = np.random.randint(10**10)
word_count = 13  #np.random.randint(25, 40)
min_word_length = 0 # min length of a word
max_word_length = 1000 # max length of a word
capitalized_words_count = 0 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
capitalized_letters_count_perc = 0 # Set a float between 0 and 1 for the percentage of the letters of the word that will be capitalized. Set an integer for the nmumber or random case statement letters. 1 is all letters capitalized not 1 word. if 'first' then only first letter will be capitalized
punctuation_word_count_perc = 0 # Same as above but for punctuation around the word
force_shift = False # Force to type the right shift of the keyboard
hard_mode = False # For hard mode, less common and longer words like 'hydrocharitaceous' are proposed
train_letters = False 
train_letters_easy_mode = False # true for this will proposed most optimal words to type fast and beat records
player_name = 'marc'

game_settings = {'game_id': game_id,
                'word_count': word_count, 
                'min_word_length': min_word_length, 
                'max_word_length': max_word_length, 
                'capitalized_words_count': capitalized_words_count, 
                'capitalized_letters_count_perc': capitalized_letters_count_perc, 
                'punctuation_word_count_perc': punctuation_word_count_perc, 
                'force_shift': force_shift,
                'hard_mode': hard_mode,
                'train_letters': train_letters,
                'train_letters_easy_mode': train_letters_easy_mode,
                'player_name': player_name}







def load_words() -> list:
    '''Opens one of two lists of words depending on the difficulty. 
    Common_words.txt contains 3000 common words where words.txt contains 
    about 450k words generally longer and harder to type compared to the 
    common word list.
    '''

    if hard_mode == True:
        file_path = f'{current_dir}/data/text/words.txt'
    else: 
        file_path = f'{current_dir}/data/text/common_words.txt'
        
    with open(file_path) as file: 
        all_words = file.read().split('\n')

    lowered_words = [''.join([char for char in word if char.isalpha()]).lower() for word in all_words if max_word_length == None or min_word_length <= len(word) <= max_word_length]
    return lowered_words
       

def load_query (query_name: str, text_only: bool = False) -> list:
    '''Opens a given text file name and execute the 
    query to return a pd.DataFrame
    
    Parameter
    ---------
    query_name str: name of the file name to run
    '''

    # Open file and get the query 
    with open(f'{current_dir}/data/queries/{query_name}.sql') as file: 
        query = file.read()

    # Query database
    df = pd.read_sql_query(query, con)

    if text_only == False:
        return df
    elif text_only == True:
        return query


def query_n_past_games_words(n_past_games: int) -> str:
    '''Query the past n games and returns all 
    words in used in them.
    
    parameter
    ---------
    n_past_games int: number of games to query
    '''
    if n_past_games == -1: 
        limit_rows = ''
    else:
        limit_rows = f'limit {n_past_games}'

    query_npast_games_words = f'''
        select
            trim(sentence) sentence
            , max(time)

        from keys_pressed kp
        left join clean_games_settings gs using(game_id)
        where 1=1
            and game_id > 100
            and sentence not null
        group by 1
        order by 2 desc
        {limit_rows}
        '''

    df_query = pd.read_sql_query(query_npast_games_words, con)
    done_words = ' '.join(df_query['sentence']).split(' ')
    return done_words


def get_n_slowest_words(word_count: list) -> list:
    '''Among the list of word, find the words that would 
    potentially take the longest to type based on the 
    average duration it takes to the player to type all 
    each and individual letters of the words.

    parameters
    ----------
    word_count int: numbers of worst words to return
    
    '''
    # Load key score 
    df_keytime = load_query('time_per_key_pressed')
    key_score = dict(zip(df_keytime['following_key'], df_keytime['time_diff']))

    # Get score for each word
    words = load_words()
    df_words = pd.DataFrame(words, columns=['word'])
    df_words['word_score'] = df_words['word'].apply(lambda word: sum([key_score[char] for char in word.lower().replace('-', '') if char in key_score.keys()]))
    df_words['avg_letter_score'] = df_words['word_score'] / df_words['word'].str.len()

    # Remove words done in the past 8 games
    done_words = query_n_past_games_words(8)
    # Remove punctuation
    done_words = [''.join([char for char in word if char.isalpha() or char == ' ']) for word in done_words]
    df_words = df_words[df_words['word'].isin(done_words) == False]

    # Sort dataframe and pick the top 25 words with at least four letters
    top_n = df_words.sort_values('avg_letter_score', ascending=train_letters_easy_mode).query('word.str.len() > 4').iloc[:word_count, 0]
    return list(top_n)



def capitalize_random(sentence: list) -> list:
    '''Given a list of words, capitalized_words_count and 
    capitalized_letters_count_perc (terrible naming I know), 
    capitalizes some letters.
    
    parameters
    ----------
    sentence list: list of words
    '''
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
    '''Given a list of word and punctuation_word_count_perc,
    randomly chooses a punctuation and adds it to the words
    
    parameter
    ---------
    sentence str: list of word
    '''
    punctuation_sentence_count = round(len(sentence) * punctuation_word_count_perc)
    common_punctuations = ['()', '{}', '[]', '!', "''", '*', ',', '.', ';', ':', '-', '_', ]
    common_punctuations = ['()', '!', "''", '*', ',', '.', ';', ':', '-', '_', '<', '>', '/', '?', '=']
    # common_punctuations = ['{}']
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


def pick_sentence():
    '''Based on the game settings, generates a list of words'''

    if train_letters == False:
        done_words = query_n_past_games_words(-1)
        word_list = load_words()
        pickable_words = set(word_list).difference(set(done_words))
        pickable_words = [word for word in list(pickable_words)]
        np.random.shuffle(pickable_words)
        sentence = pickable_words[:word_count]
        print(sentence)




        # sentence = []
        # while len(sentence) < word_count:
        #     picked_word = np.random.choice(pickable_words).lower()

        #     if max_word_length == None or min_word_length <= len(picked_word) <= max_word_length:
        #         sentence.append(picked_word)

    else:
        sentence = get_n_slowest_words(word_count)

    sentence = capitalize_random(sentence)
    sentence = add_punctuation(sentence)

    return ' '.join(sentence)





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



def whats_avgscore():
    query = """
    with tbl1 as (
    select
        game_id
        , max(time) - min(time) game_duration
        , sum(case when correct_key = 1 then 1 else 0 end) keys_to_press
        , count(*) keys_pressed
        , round(CAST(sum(case when correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) accuracy
        , sum(case when correct_key = 1 then 1 else 0 end) / ((max(time) - min(time)) / 60) / 5 wpm
        , max(time) time
        , length(cgs.sentence) sentence_lentgh
        , cgs.*

    from keys_pressed
    left join clean_games_settings cgs using(game_id)
    where 1=1
        --and game_id = 3513153090
    group by 1
    )

    select 
        *
    
    from tbl1
    where 1=1
        --wpm = (select max(wpm) from tbl1)
    """

    df_high_score = pd.read_sql_query(query, con)
    df_high_score['score'] = (df_high_score['accuracy'] * df_high_score['wpm'].round(1) * df_high_score['sentence_lentgh']).round(0)
    df_high_score.sort_values('time', ascending=False).iloc[:100]
    df_high_score = df_high_score.sort_values('score', ascending=False).reset_index(drop=True)
    avg_game_duration = round(df_high_score['game_duration'].mean())
    avg_keys_to_press = round(df_high_score['keys_to_press'].mean())
    avg_keys_pressed = round(df_high_score['keys_pressed'].mean())
    avg_accuracy = round(df_high_score['accuracy'].mean(),3)
    avg_wpm = round(df_high_score['wpm'].mean())
    avg_score = round(df_high_score['score'].mean())

    return avg_game_duration, avg_keys_to_press, avg_keys_pressed, avg_accuracy, avg_wpm, avg_score






def rule_force_shift(key_pressed, shift_pressed):
    right = '&*()_+|}{POIUYHJKL:"?><MNB'
    left = '~!@#$%^QWERTGFDSAZXCVB'

    if key_pressed in eval(shift_pressed):
        print(key_pressed, shift_pressed)
        print('WRONG SHIFT KEY', '\n'*2)
        return ' '

    else:
        return key_pressed








def info_to_print(sentence_to_display, char, key_pressed, best_wpm, avg_wpm):
    best_accuracy = score.best_game('accuracy')['accuracy']
    if this_is_first_game == False:
        if len(key_pressed) > 1 and best_wpm > 0: 
            count_correct_keys = len(list(filter(lambda x: x[1] == True, key_pressed)))
            duration = key_pressed[-1][2] - key_pressed[0][2]
            wpm = count_correct_keys / duration * 60 / 5


            # wpm_var_best = color_int((wpm - best_wpm) / best_wpm * 100, 0, suffix="%")
            # wpm_diff_best = color_int(wpm - best_wpm)
            # wpm_var_avg = color_int((wpm - avg_wpm) / avg_wpm * 100, 0, suffix="%")
            # wpm_diff_avg = color_int(wpm - avg_wpm)
            wpm_colored = color_int(wpm, best_wpm)
            acc_colored = color_int(count_correct_keys / len(key_pressed)*100, best_accuracy)
            print('\n'*20)
            print(f'Next key to press: {char}\t\nAccuracy: {acc_colored}\nWPM: {wpm_colored}\n')#|{wpm_var_best}|{wpm_diff_best}\t{wpm_var_avg}|{wpm_diff_avg}\n')

        else: 
            print('\n'*20)
            print(f'Next key to press: {char}\t\nWPM: {round(best_wpm)}|{avg_wpm}\n')
    

    words_to_display_count = 5
    words_to_display = ' '.join(sentence_to_display.split(' ')[:words_to_display_count])
    print(' ', words_to_display, '\t'*5, end='\r')
    return words_to_display


def get_correct_size_string(string: str, lentgh: int) -> int: 
    # print('get correct', string, type(string), lentgh, type(lentgh))
    return string + ' ' * (lentgh - len(string))

def color_int(text, high_low_threshold = 0, spacing=0, prefix = '', suffix=''):
    # print('color_inta', text, type(text))
    if text < high_low_threshold:
        float_colored = colored(get_correct_size_string(prefix + str(round(text, 1)) + suffix, spacing), 'red')
    else:
        float_colored = colored(get_correct_size_string(prefix + str(round(text, 1)) + suffix, spacing), 'green')
    
    return float_colored



def main(): 
    global sentence
    global score

    # Generating text, sentence or list of word to be typed
    sentence = pick_sentence()
    game_settings['sentence'] = sentence
    # if query_to_type != None: 
    #     sentence = load_query(query_to_type, text_only=True)
    print(f'{sentence}')

    score = Score(game_settings)
    score.game_settings = game_settings
    score.sentence = sentence
    # for value in dir(score):
    #     try: print(f'score.{value}', eval(f'score.{value}'))
    #     except: ...

    # best_score_condition = [f'train_letters == {train_letters}', f'hard_mode == {hard_mode}', f'word_count == {word_count}']
    # best_score_condition = ''
    best_wpm = score.best_game(sort_by='wpm desc')['wpm']
    avg_wpm = whats_avgscore()[4]

    
    # Looping through each character to compare them to the last key pressed
    key_pressed = []
    sentence_to_display = sentence + '' # Adding one character at the end to validate the game (type enter)
    print('\n'*5)
    for index, char in enumerate(sentence_to_display):
        # Replacing space by spelled word space to match it to the key
        if char == ' ':
            char = 'space'
        elif char == '\n':
            char = 'return'
        elif char == '\t':
            char = 'tab'

        
        # Printing updated sentence
        # if index == sentence_length: 
        #     print('No more letters, press ENTER to save the game, any other to not.')
        # else:     
        words_to_display = info_to_print(sentence_to_display, char, key_pressed, best_wpm, avg_wpm)

        # Looping through event key until the right key is pressed
        guess = '' 
        while guess != char:
            guess, shift_pressed = next_key_pressed()
            # print(guess, shift_pressed)

            if force_shift == True and shift_pressed != None:
                guess = rule_force_shift(guess, shift_pressed)


            if guess == char: 
                correct_key = True
                key_pressed.append([str(guess), correct_key, time.time(), game_id]) 
                sentence_to_display = sentence_to_display[1:]
                break
            else:
                correct_key = False
                print(guess, words_to_display)
                key_pressed.append([str(guess), correct_key, time.time(), game_id]) 


    # print('\n'*10, this_is_first_game)
    score.score_game(key_pressed)
    score.compare_game()
    log_key_pressed(key_pressed=key_pressed)
    log_game_settings(game_settings)
    
    if game_id % 7 == 0: 
        push_to_gbq()

    shutil.copyfile('data/main_database.db', 'data/example_database.db')


if __name__ == '__main__':
    main()