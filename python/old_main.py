# https://datastudio.google.com/u/0/reporting/191d67ab-f6e7-43c6-bd99-37b3e4091ead/page/YJH4C/edit
from turtle import left
import numpy as np
import sqlite3
import pandas as pd
import shutil
import time
import os

from src.score import Score
from src.log_data import *
from src.detect_keys import *
from src.display import *




con = sqlite3.connect("data/main_database.db")
current_dir = os.getcwd()



       

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
    key_score = dict(zip(df_keytime['following_key'], df_keytime['time_diff'].round(4)))
    # print(key_score)

    # Get score for each word
    words = load_words()
    df_words = pd.DataFrame(words, columns=['word'])

    # This is supposed to add a weight so that not only least frequent letters are proposed but it's not woroking great
    # all_words_letters = ''.join(df_words['word'])
    # all_words_letters_count = {letter: all_words_letters.count(letter) for letter in set(all_words_letters)}
    # all_words_letters_count = {key: -(value - min(all_words_letters_count.values()))/(max(all_words_letters_count.values()) - min(all_words_letters_count.values())) for key, value in all_words_letters_count.items()}
    # key_score = {key: key_score[key] * all_words_letters_count[key] for key in all_words_letters_count.keys()}

    df_words['word_score'] = df_words['word'].apply(lambda word: sum([key_score[char] for char in word.lower().replace('-', '') if char in key_score.keys()]))
    df_words['avg_letter_score'] = df_words['word_score'] / df_words['word'].str.len()


    # Remove words done in the past 8 games
    done_words = query_n_past_games_words(8)
    # Remove non letter and space characters
    done_words = [''.join([char for char in word if char.isalpha() or char == ' ']) for word in done_words]
    df_words = df_words[df_words['word'].isin(done_words) == False]


    # Sort dataframe and pick the top 25 words with at least four letters
    top_n = df_words.sort_values('avg_letter_score', ascending=train_letters_easy_mode).query('word.str.len() > 4').iloc[:word_count, 0]
    return list(top_n)


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








def main(): 
    # global sentence
    global score

    # Initialize the class with game settings
    score = Score(game_settings, con)

    # Generating text, sentence or list of word to be typed
    sentence = pick_sentence()
    game_settings['sentence'] = sentence
    score.sentence = sentence

    print(f'{sentence}')

    if score.this_is_first_game or score.this_is_first_game_with_current_settings:
        best_wpm = 0
    else:
        best_wpm = score.max_mean_score().loc['wpm', 'max']


    
    # Looping through each character to compare them to the key pressed
    key_pressed = []
    sentence_to_display = sentence 
    words_left_to_type = sentence.count(' ') + 1
    print('\n'*5)
    for index, char in enumerate(sentence_to_display):
        # Replacing space by spelled word space to match it to the key
        if char == ' ':
            char = 'space'
            words_left_to_type -= 1
        elif char == '\n':
            char = 'return'
        elif char == '\t':
            char = 'tab'

        
        # Printing updated sentence
        # if index == sentence_length: 
        #     print('No more letters, press ENTER to save the game, any other to not.')
        # else:      

        words_to_display = info_to_print(display_infos, sentence_to_display, char, key_pressed, best_wpm, words_left_to_type)


        # Looping through event key until the right key is pressed
        guess = '' 
        while guess != char:
            guess, shift_pressed = next_key_pressed()
            # print('\n'*10, guess, shift_pressed, '\n'*10)
            # print(guess, shift_pressed)

            if force_shift == True and shift_pressed != None:
                guess = rule_force_shift(guess, shift_pressed)


            if guess == char:  
                correct_key = True
                key_pressed.append([str(guess), correct_key, time.time(), game_id]) 
                sentence_to_display = sentence_to_display[1:]
                break
            elif 'shift' not in guess: # That's because when you type shift a for A it logs shift and then shift + a
                correct_key = False
                print(guess, words_to_display)
                key_pressed.append([str(guess), correct_key, time.time(), game_id]) 



    score.score_game(key_pressed)

    if score.this_is_first_game_with_current_settings == False:
        score.compare_game()
    log_key_pressed(key_pressed)
    log_game_settings(game_settings)
    clean_games_settings()
    log_summary_per_game()

    # print('Starting Push')
    if game_id % 7777777777 == 0: # Pushing data takes time so I do it every 7 games
        try:
            push_to_gbq(game_id)
        except Exception as error: 
            print("Error trying to push the data to GBQ. See errror below.")
            print(error)


    # print(f'Total distinct words typed: {len(query_n_past_games_words(-1))} | {len(query_n_past_games_words(-1))/len(load_words()):.1%}')

    shutil.copyfile('data/main_database.db', 'data/example_database.db')


if __name__ == '__main__':
    # for _ in range(10000):
        # print(len('81.96 %            '))
    main()  


# a = '0                      '
# b = '5.33 %              '

# print(len(a), len(b))
