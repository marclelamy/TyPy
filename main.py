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
sentence_length = np.random.randint(25, 40)
max_word_length = None
capitalized_words_count = 1 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
capitalized_letters_count = .1 # Set a float between 0 and 1 for the percentage of the letters of the word that will be capitalized. Set an integer for the nmumber or random case statement letters. 1 is all letters capitalized not 1 word. if 'first' then only first letter will be 
force_shift = True # Force to type the right shift of the keyboard
words_to_display_count = 10
me_playing = 1




def load_text (file_path=f'{current_dir}/data/common_words.txt') -> list:
    '''a '''
    with open(file_path) as file: 
        all_words = file.read().split('\n')

    return all_words



def capitalize_random(sentence):
    capitalized_words_count = 1 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
    capitalized_letters_perc = '0.8'
    capitalized_words_count = round(len(sentence) * capitalized_words_count)

    for index_word in range(capitalized_words_count):
        word = sentence[index_word]

        if type(capitalized_letters_perc) in [int, float]:
            if capitalized_letters_perc <= 1:
                capitalized_letters_count = round(len(word) * capitalized_letters_perc)

            rdm_list = list(range(len(word)))
            np.random.shuffle(rdm_list)
            rdm_list = rdm_list[:capitalized_letters_count]
            sentence[index_word] = ''.join([char.upper() if index_char in rdm_list else char for index_char, char in enumerate(word)])

        elif type(capitalized_letters_perc) == str:
            sentence[index_word] = word.title()

        

    np.random.shuffle(sentence)

    return sentence




def pick_words(word_list, max_word_length, sentence_length=10):
    '''returns a word based on criterias'''

    random_word = []
    while len(random_word) < sentence_length:
        picked_word = np.random.choice(word_list).lower()

        if max_word_length == None:
            random_word.append(picked_word)

        elif len(picked_word) <= max_word_length:
            random_word.append(picked_word)


    sentence = random_word
    # sentence = capitalize_random(sentence)

    return ' '.join(sentence)




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
        df_keys.to_sql('keys_pressed', con, if_exists='append', index=False)



def log_game_settings(game_settings):
    if me_playing == 1:
        column_names = ['sentence', 'sentence_length', 'max_word_length', 'game_id']
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
                
                if shift_pressed:
                    guess = key_map_shift[guess] if shift_pressed is True else guess
                    
                key=guess
                break

        count += 1

    return guess, 'right' if right_shift_pressed == True else ('left' if right_shift_pressed == True else None)



def whats_highscore ():
    query = """
    with tbl1 as (
    select
        game_id
        , max(time) - min(time) game_duration
        , sum(case when correct_key = 1 then 1 else 0 end) keys_to_press
        , count(*) keys_pressed
        , round(CAST(sum(case when correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) accuracy
        , round(sum(case when correct_key = 1 then 1 else 0 end) / ((max(time) - min(time)) / 60) / 4.7) wpm

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
    print(f'\nRECORD\nChar to type: {keys_to_press} | Char typed: {keys_pressed} | Game duration: {int(game_duration)}s | Typing Accuracy: {accuracy:.1%} | WPM: {round(wpm)}')



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
    whats_highscore ()



def rule_force_shift(key_pressed, shift_pressed):
    right = '`123456qwertgfdsazxcvb!~@#$%^QWERTASDFGZXCVB'
    left = "7890-=yuiop[]\hjkl;'bnm,./"

    if key_pressed not in eval(shift_pressed):
        print('WRONG SHIFT KEY')
        key_pressed = ' ' # 




def main():
    # Generating text to be typed
    text = load_text()
    sentence = pick_words(text, max_word_length, sentence_length)

    game_settings = [sentence, sentence_length, max_word_length, game_id]
    print(game_settings)

    
    # Looping through each character to compare them to the last key pressed
    key_pressed = []
    sentence = sentence + ' ' # Adding one character at the end to validate the game (type enter)
    print('\n'*5)
    for index, char in enumerate(sentence):
        # Replacing space by spelled word space to match it to the key
        if char == ' ':
            char = 'space'
        
        # Printing au updated sentence
        if index == len(game_settings[0]): 
            print('No more letters, press ENTER to save the game, any other to not.')
        else:     
            print('\n'*20)
            words_to_display = ' '.join(sentence.split(' ')[:words_to_display_count])
            print(' ', words_to_display, '\t'*5, end='\r')

        # Looping through event key until the right key is pressed
        guess = '' 
        while guess != char:
            guess, shift_pressed = next_key_pressed()

            # if force_shift == True:
            #     rule_force_shift(guess, shift_pressed)





   




    
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