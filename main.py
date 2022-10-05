from turtle import pu
import numpy as np
import pygame
import sqlite3
import pandas as pd
import time
# from PyDictionary import PyDictionary
import os
from termcolor import colored

pygame.init()
con = sqlite3.connect("main_database.db")
current_dir = os.getcwd()


 






# Game settings
game_id = np.random.randint(10**10)
sentence_length = 25 #np.random.randint(25, 40)
max_word_length = None
min_word_length = None
capitalized_words_count = 0 # Set a float between 0 and 1 for the percentage of word that will be generated with a/multiple random case letter
capitalized_letters_count_perc = 0 # Set a float between 0 and 1 for the percentage of the letters of the word that will be capitalized. Set an integer for the nmumber or random case statement letters. 1 is all letters capitalized not 1 word. if 'first' then only first letter will be capitalized
punctuation_word_count_perc = 0 # Same as above but for punctuation around the word
force_shift = False # Force to type the right shift of the keyboard
hard_mode = False # For hard mode, less common and longer words like 'hydrocharitaceous' are proposed
train_letters = False
query_to_type = 'time_per_key_pressed'

player_name = ' hehjksdhfkjhsd'




def load_words() -> list:
    '''Opens one of two lists of words depending on the difficulty. 
    Common_words.txt contains 3000 common words where words.txt contains 
    about 450k words generally longer and harder to type compared to the 
    common word list.
    '''

    if hard_mode == True:
        file_path = f'{current_dir}/data/words.txt'
    else: 
        file_path = f'{current_dir}/data/common_words.txt'
        
    with open(file_path) as file: 
        all_words = file.read().split('\n')

    return all_words
       

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
        limit {n_past_games}
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
    key_score = dict(zip(df_keytime['following_key'], df_keytime['time_diff'].round(3)))
    print(key_score)

    # Get score for each word
    words = load_words()
    df_words = pd.DataFrame(words, columns=['word'])
    df_words['word_score'] = df_words['word'].apply(lambda word: sum([key_score[char] for char in word.lower().replace('-', '') if char in key_score.keys()]))
    df_words['avg_letter_score'] = df_words['word_score'] / df_words['word'].str.len()

    # Remove words done in the past four games
    done_words = query_n_past_games_words(8)
    # Remove punctuation
    done_words = [''.join([char for char in word if char.isalpha() or char == ' ']) for word in done_words]
    df_words = df_words[df_words['word'].isin(done_words) == False]

    # Sort dataframe and pick the top 25 words with at least four letters
    top_n = df_words.sort_values('avg_letter_score', ascending=False).query('word.str.len() > 4').iloc[:word_count, 0]
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
    print(punctuation_sentence_count)
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

    if train_letters != True:
        word_list = load_words()
        sentence = []
        while len(sentence) < sentence_length:
            picked_word = np.random.choice(word_list).lower()

            if max_word_length == None:
                sentence.append(picked_word)

            elif len(picked_word) <= max_word_length:
                sentence.append(picked_word)

    else:
        sentence = get_n_slowest_words(sentence_length)

    sentence = capitalize_random(sentence)
    sentence = add_punctuation(sentence)

    return ' '.join(sentence)





def log_key_pressed(key_pressed):
    column_names = ['key', 'correct_key', 'time', 'game_id']
    df_keys = pd.DataFrame(key_pressed, columns=column_names)
    df_keys.to_sql('keys_pressed', con, if_exists='append', index=False)

def log_game_settings():
    column_names = ['game_id', 'game_settings']
    game_settings = {'sentence': sentence, 
                     'sentence_length': sentence_length, 
                     'max_word_length': max_word_length, 
                     'capitalized_words_count': capitalized_words_count, 
                     'capitalized_letters_count_perc': capitalized_letters_count_perc, 
                     'punctuation_word_count_perc': punctuation_word_count_perc, 
                     'force_shift': force_shift,
                     'hard_mode': hard_mode,
                     'train_letters': train_letters,
                     'player_name': player_name}
    game_settings = [game_id, str(game_settings)]
    df_game_settings = pd.DataFrame([game_settings], columns=column_names)
    df_game_settings.to_sql('games_settings', con, if_exists='append', index=False)

def clean_games_settings():
    df = pd.read_sql_query('select * from games_settings', con)
    df['game_settings'] = df['game_settings'].apply(lambda x: eval(x))
    df_games_settings = pd.concat([df[['game_id']], df['game_settings'].apply(lambda x: pd.Series(x))], axis=1)
    df_games_settings.to_sql('clean_games_settings', con, if_exists='append', index=False)

def log_summary_per_game(): 
    query = f"""
        select
            kp.game_id
            , max(kp.time) - min(kp.time) game_duration
            , sum(case when kp.correct_key = 1 then 1 else 0 end) keys_to_press
            , count(*) keys_pressed
            , round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) accuracy
            , sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5 wpm
            , length(cgs.sentence) sentence_lentgh
            , cgs.sentence	
            , cgs.max_word_length	
            , cgs.capitalized_words_count	
            , cgs.capitalized_letters_count_perc	
            , cgs.punctuation_word_count_perc	
            , cgs.force_shift	
            , cgs.hard_mode	
            , cgs.train_letters	
            , cgs.comment	player_name

        from keys_pressed kp 
        left join clean_games_settings cgs using(game_id)
        where 1=1
            and cgs.game_id is not null
        group by 1
        """

        # query = 'select * from keys_pressed left join games_settings gs using(game_id)'

    df_high_score = pd.read_sql_query(query, con)
    df_high_score.to_sql('summary_per_game', con, if_exists='replace', index=False)


def push_to_gbq():
    df_keys_pressed = pd.read_sql_query('select * from keys_pressed', con)
    df_keys_pressed.to_gbq('pyfasttype.keys_pressed', if_exists='replace', progress_bar=None)
    df_clean_games_settings = pd.read_sql_query('select * from clean_games_settings', con)
    df_clean_games_settings['capitalized_letters_count_perc'] = df_clean_games_settings['capitalized_letters_count_perc'].astype(str)
    df_clean_games_settings.to_gbq('pyfasttype.clean_games_settings', if_exists='replace', progress_bar=None)
    df_summary_per_game = pd.read_sql_query('select * from summary_per_game', con)
    df_summary_per_game.to_gbq('pyfasttype.summary_per_game', if_exists='replace', progress_bar=None)
    print('Data pushed to GBQ')



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


def whats_bestscore (sort_by='score', condition=''):
    query = f"""
        with tbl1 as (
        select
            game_id
            , max(time) - min(time) game_duration
            , sum(case when correct_key = 1 then 1 else 0 end) keys_to_press
            , count(*) keys_pressed
            , round(CAST(sum(case when correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) accuracy
            , sum(case when correct_key = 1 then 1 else 0 end) / ((max(time) - min(time)) / 60) / 5 wpm
            , length(cgs.sentence) sentence_lentgh
            , cgs.*

        from keys_pressed
        left join clean_games_settings cgs using(game_id)
        where 1=1
            {condition}
            --and game_id = 3513153090
        group by 1
        )

        select 
            *
        
        from tbl1
        where 1=1
            and keys_pressed > 100
            --wpm = (select max(wpm) from tbl1)
        """

    # query = 'select * from keys_pressed left join games_settings gs using(game_id)'

    df_high_score = pd.read_sql_query(query, con)
    df_high_score['score'] = (df_high_score['accuracy'] * df_high_score['wpm'].round(1) * df_high_score['sentence_lentgh']).round(0)
    df_high_score = df_high_score.sort_values(sort_by, ascending=False).reset_index(drop=True)
    best_player_name = df_high_score.loc[0, 'player_name']
    best_hard_mode = df_high_score.loc[0, 'hard_mode']
    best_game_duration = df_high_score.loc[0, 'game_duration']
    best_keys_to_press = df_high_score.loc[0, 'keys_to_press']
    best_keys_pressed = df_high_score.loc[0, 'keys_pressed']
    best_accuracy = df_high_score.loc[0, 'accuracy']
    best_wpm = df_high_score.loc[0, 'wpm']
    best_score = df_high_score.round().loc[0, 'score']
    return best_game_duration, best_keys_to_press, best_keys_pressed, best_accuracy, best_wpm, best_score, best_player_name, best_hard_mode


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

def first_game():
    if pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name='keys_pressed';", con).shape[0] > 0:
        return False
    else:
        return True

def color_int(number: float, high_low_threshold = 0, prefix = '', suffix=''):
    if number < high_low_threshold:
        float_colored = colored(prefix + str(round(number, 1)) + suffix, 'red')
    else:
        float_colored = colored(prefix + '+' + str(round(number, 1)) + suffix, 'green')
    
    return float_colored

def score_game(key_pressed=None, game_id=None):
    if key_pressed == None:
        df = pd.read_sql_query(f'select * from keys_typed where game_id = {game_id}', con)
    else:
        column_names = ['key', 'correct_key', 'time', 'game_id']
        df = pd.DataFrame(key_pressed, columns=column_names)

    first_second, last_second = df.iloc[[0, -1], 2]
    game_duration = last_second - first_second
    keys_pressed = df.shape[0]
    keys_to_press = df.query('correct_key == 1').shape[0]
    accuracy = keys_to_press / keys_pressed
    wpm = round(keys_to_press / (game_duration / 60) / 5, 1)
    score = round(accuracy * wpm * len(sentence))

    if first_game() == False:
        best_game_duration, best_keys_to_press, best_keys_pressed, best_accuracy, best_wpm, best_score, best_player_name, best_hard_mode = whats_bestscore()
        avg_game_duration, avg_keys_to_press, avg_keys_pressed, avg_accuracy, avg_wpm, avg_score = whats_avgscore()

        if score >= best_score:
            for _ in range(10):
                print('RECORD\t'*10)
            print(score >= best_score, '\n')
            
        
        score_info_to_print =   f'Best hard mode:  {best_hard_mode}\n' +\
                                f'Char to type:    {keys_to_press}   | {color_int((keys_to_press - best_keys_to_press) / best_keys_to_press * 100, 0, "%")}\t {avg_keys_to_press}   | {color_int((keys_to_press - avg_keys_to_press) / avg_keys_to_press * 100, 0, "%")}\n' +\
                                f'Char typed:      {keys_pressed}   | {color_int((keys_pressed - best_keys_pressed) / best_keys_pressed * 100, 0, "%")}\t {avg_keys_pressed}   | {color_int((keys_pressed - avg_keys_pressed) / avg_keys_pressed * 100, 0, "%")}\n' +\
                                f'Game duration:   {int(game_duration)}    | {color_int((game_duration - best_game_duration) / best_game_duration * 100, 0, "%")}\t {int(avg_game_duration)}    | {color_int((game_duration - best_game_duration) / best_game_duration * 100, 0, "%")}\n' +\
                                f'Typing Accuracy: {accuracy:.1%} | {color_int((accuracy - best_accuracy) / best_accuracy * 100, 0, "%")}\t {avg_accuracy:.1%} | {color_int((accuracy - avg_accuracy) / avg_accuracy * 100, 0, "%")}\n' +\
                                f'WPM:             {round(wpm)}    | {color_int((wpm - best_wpm) / best_wpm * 100, 0, "%")}\t {round(avg_wpm)}    | {color_int((wpm - avg_wpm) / avg_wpm * 100, 0, "%")}\n' +\
                                f'Score:          {score}  | {color_int((score - best_score) / best_score * 100, 0, "%")}\t {avg_score}  | {color_int((score - avg_score) / avg_score * 100, 0, "%")}\n' +\
                                f'Best player:     {best_player_name}\n '

        print(score_info_to_print)

    else: 
        print('Play one more game to see highscore and stats')






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
    if first_game() == False:
        if len(key_pressed) > 1: 
            count_correct_keys = len(list(filter(lambda x: x[1] == True, key_pressed)))
            duration = key_pressed[-1][2] - key_pressed[0][2]
            wpm = count_correct_keys / duration * 60 / 5


            wpm_var_best = color_int((wpm - best_wpm) / best_wpm * 100, 0, "%")
            wpm_diff_best = color_int(wpm - best_wpm)
            wpm_var_avg = color_int((wpm - avg_wpm) / avg_wpm * 100, 0, "%")
            wpm_diff_avg = color_int(wpm - avg_wpm)
            wpm_colored = color_int(wpm, best_wpm)
            print('\n'*20)
            print(f'Next key to press: {char}\t\nWPM: {wpm_colored}|{wpm_var_best}|{wpm_diff_best}\t{wpm_var_avg}|{wpm_diff_avg}\n')

        else: 
            print('\n'*20)
            print(f'Next key to press: {char}\t\nWPM: {round(best_wpm)}|{avg_wpm}\n')
    

    words_to_display_count = 5
    words_to_display = ' '.join(sentence_to_display.split(' ')[:words_to_display_count])
    print(' ', words_to_display, '\t'*5, end='\r')
    return words_to_display


    
# sum(case when correct_key = 1 then 1 else 0 end) / ((max(time) - min(time)) / 60) / 5 wpm
def main(): 
    global sentence
    # Generating text to be typed
    sentence = pick_sentence()
    # if query_to_type != None: 
    #     sentence = load_query(query_to_type, text_only=True)
    #     print(sentence)
    # game_settings = [sentence, sentence_length, max_word_length, game_id, capitalized_words_count, capitalized_letters_count_perc, punctuation_word_count_perc, force_shift]
    sentence_length = len(sentence)

    best_wpm = whats_bestscore(sort_by='wpm')[4]
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





   



            # if index == sentence_length: # For last character of sentence only
            #     log_game = True
            #     guess = char
            #     break

            # print(guess, char, sentence[-1], index, sentence_length, guess == char, guess == 'return' and index == sentence_length)
            if guess == char: 
                correct_key = True
                key_pressed.append([str(guess), correct_key, time.time(), game_id]) 
                sentence_to_display = sentence_to_display[1:]
                break
            else:
                correct_key = False
                print(guess, words_to_display)
                key_pressed.append([str(guess), correct_key, time.time(), game_id]) 


    score_game(key_pressed)
    # if log_game == True:
    log_key_pressed(key_pressed=key_pressed)
    log_game_settings()
    clean_games_settings()
    push_to_gbq()





main()