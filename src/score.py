import numpy as np
import pandas as pd
from termcolor import colored
import sqlite3
import os


database_path = "data/main_database.db"
this_is_first_game = False if os.path.isfile(database_path) else True
con = sqlite3.connect("data/main_database.db")



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










class Score():
    def __init__(self, game_settings): 
        self.game_settings = game_settings

        self.game_settings_query_condition = []
        for key, value in self.game_settings.items():
            if key not in ('word_count', 'min_word_length', 'max_word_length', 'capitalized_words_count', 'capitalized_letters_count_perc', 'punctuation_word_count_perc', 'force_shift', 'hard_mode', 'train_letters', 'train_letters_easy_mode'):
                continue
            if type(value) == str: 
                condition = f'{key} == "{value}"'
            else:
                condition = f'{key} == {value}'
                
            self.game_settings_query_condition.append(condition)

    
    
    def best_game(self, sort_by='score', conditions=['1=1']):
        '''Return the game settings of the best game based on the sorting'''

        full_condition = ''.join([' AND ' + condition for condition in conditions + self.game_settings_query_condition])

        query = f"""
            SELECT 
                * 
            FROM summary_per_game
            WHERE 1=1
                {full_condition}
            ORDER BY {sort_by}
            """
        print(query)
        df_summary = pd.read_sql_query(query, con)   
        
        # If there hasn't been any game played with the settings, catch the keyerror 
        try:
            best_game = df_summary.loc[0, :].to_dict()
        except KeyError: 
            best_game = {col: 0 for col in df_summary.columns}

        return best_game
    

    def max_mean_score(self, conditions=['1=1']):
        '''Return max and average metrics'''

        full_condition = ''.join([' AND ' + condition for condition in conditions + self.game_settings_query_condition])

        query = f"""
            SELECT 
                game_duration
                , sentence_length
                , accuracy
                , wpm
                , score

            FROM summary_per_game
            WHERE 1=1
                {full_condition}
            """

        df_summary = pd.read_sql_query(query, con) 
        try:
            df_summary = df_summary.describe().loc[['max', 'mean'], :].T
        except KeyError: 
            df_summary = {col: 0 for col in df_summary.columns}

        return df_summary



    def make_condition(self):
        '''Generate a string containing games settings that will act 
        as condition for the mutliple queries'''

        self.game_settings_query_condition = []
        for key, value in self.game_settings:
            if type(value) == str: 
                condition = f'{key} == "{value}"'
            else:
                condition = f'{key} == {value}'
                
            self.game_settings_query_condition.append(condition)

    def score_game(self, key_pressed=None, game_id=None):
        if game_id != None:
            df = pd.read_sql_query(f'select * from keys_typed where game_id = {game_id}', con)
        else:
            column_names = ['key', 'correct_key', 'time', 'game_id']
            df = pd.DataFrame(key_pressed, columns=column_names)

        first_second, last_second = df.iloc[[0, -1], 2]
        game_duration = round(last_second - first_second) if round(last_second - first_second) > 0 else last_second - first_second
        keys_pressed = df.shape[0]
        keys_to_press = df.query('correct_key == 1').shape[0]
        accuracy = round(keys_to_press / keys_pressed, 2)
        wpm = round(keys_to_press / (game_duration / 60) / 5, 1)
        score = round(accuracy * wpm * len(self.sentence))



        query = '''select distinct * from summary_per_game where keys_to_press > 100'''

        df = pd.read_sql_query(query, con).describe().round()
        df = df.loc[['mean', 'max'], :]

        df = df.T

        # df.insert(1, '')
        df.loc['game_id', 'current_game'] = game_id
        df.loc['maxdatetime_unix', 'current_game'] = first_second
        df.loc['last_second', 'current_game'] = last_second
        df.loc['keys_to_press', 'current_game'] = keys_to_press
        df.loc['keys_pressed', 'current_game'] = keys_pressed
        df.loc['accuracy', 'current_game'] = accuracy
        df.loc['wpm', 'current_game'] = wpm
        df.loc['score', 'current_game'] = score

        if this_is_first_game == False:
            self.game_scores = game_duration, keys_to_press, accuracy, wpm, score
        #     best_game_duration, best_keys_to_press, best_keys_pressed, best_accuracy, best_wpm, best_score, best_player_name, best_hard_mode = whats_bestscore()
        #     avg_game_duration, avg_keys_to_press, avg_keys_pressed, avg_accuracy, avg_wpm, avg_score = whats_avgscore()

        #     if score >= best_score:
        #         for _ in range(10):
        #             print('RECORD\t'*10)
        #         print(score >= best_score, '\n')
                
            
        #     score_info_to_print =   f'Best hard mode:  {best_hard_mode}\n' +\
        #                             f'Char to type:    {keys_to_press}   | {color_int((keys_to_press - best_keys_to_press) / best_keys_to_press * 100, 0, "%")}\t {avg_keys_to_press}   | {color_int((keys_to_press - avg_keys_to_press) / avg_keys_to_press * 100, 0, "%")}\n' +\
        #                             f'Char typed:      {keys_pressed}   | {color_int((keys_pressed - best_keys_pressed) / best_keys_pressed * 100, 0, "%")}\t {avg_keys_pressed}   | {color_int((keys_pressed - avg_keys_pressed) / avg_keys_pressed * 100, 0, "%")}\n' +\
        #                             f'Game duration:   {int(game_duration)}    | {color_int((game_duration - best_game_duration) / best_game_duration * 100, 0, "%")}\t {int(avg_game_duration)}    | {color_int((game_duration - avg_game_duration) / avg_game_duration * 100, 0, "%")}\n' +\
        #                             f'Typing Accuracy: {accuracy:.1%} | {color_int((accuracy - best_accuracy) / best_accuracy * 100, 0, "%")}\t {avg_accuracy:.1%} | {color_int((accuracy - avg_accuracy) / avg_accuracy * 100, 0, "%")}\n' +\
        #                             f'WPM:             {round(wpm)}    | {color_int((wpm - best_wpm) / best_wpm * 100, 0, "%")}\t {round(avg_wpm)}    | {color_int((wpm - avg_wpm) / avg_wpm * 100, 0, "%")}\n' +\
        #                             f'Score:           {score}  | {color_int((score - best_score) / best_score * 100, 0, "%")}\t {avg_score}  | {color_int((score - avg_score) / avg_score * 100, 0, "%")}\n' +\
        #                             f'Best player:     {best_player_name}\n '
        # print(tabulate(df))

        else: 
            print('Play one more game to see highscore and stats')


    def compare_game(self):
        df_summary = self.max_mean_score()
        
        if type(df_summary) == dict: 
            print('Play another game to see the stats')
            return 

        df_summary.insert(0, 'game', self.game_scores)
        max_diff = ((df_summary['game'] - df_summary['max']) / df_summary['max'] * 100).round()
        df_summary.insert(2, 'max_diff', max_diff)
        mean_diff = ((df_summary['game'] - df_summary['mean']) / df_summary['mean'] * 100).round()
        df_summary.insert(4, 'mean_diff', mean_diff)
        df_summary = df_summary.reset_index().T.reset_index().T.replace('index', '')

        # data_col_index = [[''] + list(df_summary.columns)] + [[df_summary.index[index]] + [value for value in row] for index, row in enumerate(data)]

        text_to_print = ''
        for index1, row in enumerate(df_summary.to_numpy().tolist()):
            for index2, value in enumerate(row):
                # if index2 in (2, 4):
                #     spacing = 9
                # else: 
                #     spacing = 15

                # if type(value) in [int, float] or index2 not in (1, 3, 5):
                #     value = round(value, 3)
                #     text_to_print += color_int(value, 10) + '\t'
                # else:
                #     text_to_print += get_correct_size_string(value, 10) + '\t'
                if index2 == 0:
                    text_to_print += get_correct_size_string(str(value), 20) + '\t'

                elif index1 == 0 and index2 in (4, 5):
                    text_to_print += get_correct_size_string(str(value), 10) + '\t'

                elif (index1 == 0 and index2 not in (4,6)) or index2 in (0, 1, 2, 4):
                    if type(value) in [int, float]:
                        value = round(value)
                    text_to_print += get_correct_size_string(str(value), 10) + '\t'
                else:
                    # value = round(value, 3)
                    text_to_print += color_int(value, spacing=10, suffix='%') + '\t'
                # if index1 == 0 and index2 in (0, 1, 2, 5) or index2 == 0:
                #     text_to_print += get_correct_size_string(str(value), 10) + '\t'
                
                # elif index1 == 0 and index2 in (3, 4, 5):
                #     text_to_print += get_correct_size_string(str(value), 10) + '\t'

                # elif index1 == 3 and index2 == 1:
                #     text_to_print += get_correct_size_string(value*100, spacing=10) + '\t'

                # elif index1 == 3 and index2 in (1, 2, 4):
                #     text_to_print += color_int(value*100, spacing=10) + '\t'
                
                # elif index1 == 3 and index2 in (3, 4, 5):
                #     text_to_print += color_int(value, spacing=10) + '\t'
                



            text_to_print += '\n'

        print(text_to_print)
