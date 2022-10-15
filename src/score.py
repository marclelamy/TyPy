import numpy as np
import pandas as pd
from termcolor import colored
import sqlite3
import os


# database_path = "data/main_database_real.db"
# try: 
#     os.remove(database_path)
# except Exception as e:
#     print(e)
# this_is_first_game = False if os.path.isfile(database_path) else True
# con = sqlite3.connect(database_path)



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



# Game settings
game_id = np.random.randint(10**10)
word_count = 25  #np.random.randint(25, 40)
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






class Score():
    def __init__(self, game_settings, con): 
        self.game_settings = game_settings
        self.con = con

        self.game_settings_query_condition = []
        for key, value in self.game_settings.items():
            if key not in ('word_count', 'min_word_length', 'max_word_length', 'capitalized_words_count', 'capitalized_letters_count_perc', 'punctuation_word_count_perc', 'force_shift', 'hard_mode', 'train_letters', 'train_letters_easy_mode'):
                continue
            if type(value) == str: 
                condition = f'{key} == "{value}"'
            else:
                condition = f'{key} == {value}'
                
            self.game_settings_query_condition.append(condition)

        
        
        self.this_is_first_game = self.this_is_first_game()
        
        
    def make_sure_all_tbl_exist(self):
        # '''Makes sure the database contains all tables 
        # for the code to run properly and doesn't have missing 
        # tables, like for the first game.'''

        # query = f"""
        #     select * from sqlite_master
        #     """
        # df_sqlite_master = pd.read_sql_query(query, con)
        # databse_existing_tables = df_sqlite_master['tbl_name'].to_list()

        # if 'keys_pressed' not in databse_existing_tables:
        #     df_keys_pressed = pd.DataFrame(columns=['key', 'correct_key', 'time', 'game_id', 'game_settings'])
        #     df_keys_pressed.to_sql('keys_pressed', con, index=False)

        # if 'games_settings' not in databse_existing_tables:
        #     df_games_settings = pd.DataFrame(columns=['game_id', 'game_settings'])
        #     df_games_settings.to_sql('games_settings', con, index=False)

        # if 'clean_games_settings' not in databse_existing_tables:
        #     df_clean_games_settings = pd.DataFrame(columns=['game_id', 'game_settings'])
        #     df_clean_games_settings.to_sql('clean_games_settings', con, index=False)

        ...


    def this_is_first_game(self):
        '''Check if there tables in the database. 
        Returns True if none, False otherwise'''

        query = f"""
            SELECT 
                *
            FROM sqlite_master
            """
        df_sqlite_master = pd.read_sql_query(query, self.con)
        
        if df_sqlite_master.shape[0] == 0:
            return True
        else:
            return False


    
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

        df_summary = pd.read_sql_query(query, self.con)   
        
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

        df_summary = pd.read_sql_query(query, self.con) 
        try:
            df_summary = df_summary.describe().loc[['max', 'mean'], :].T
        except KeyError:
            df_summary = {col: 0 for col in df_summary.columns}

        return df_summary


    def make_condition(self):
        '''Generate a string containing the current 
        games settings so that every oher query that 
        pulls games to compare high score, mean, etc
        compares the same games
        '''

        self.game_settings_query_condition = []
        for key, value in self.game_settings:
            if type(value) == str: 
                condition = f'{key} == "{value}"'
            else:
                condition = f'{key} == {value}'
                
            self.game_settings_query_condition.append(condition)


    def score_game(self, key_pressed=None):
        '''Takes the list of keyy pressed during the game and calculate 
        the different metrics like game duration, accuracy, wpm
        
        Parameter
        ---------
        keys_pressed: list of list containing the guess, corrct_key 1/0, epoch and game_id
        
        '''

        # Create a df to store and manipulate the data of the game
        column_names = ['key', 'correct_key', 'time', 'game_id']
        df = pd.DataFrame(key_pressed, columns=column_names)

        first_second, last_second = df.iloc[[0, -1], 2]
        game_duration = round(last_second - first_second) if last_second - first_second > 10 else round(last_second - first_second, 2) # Don't round the seconds unless games of less than 10 second (for development only unless you're putting some lame ass rules)
        keys_pressed = df.shape[0]
        keys_to_press = df.query('correct_key == 1').shape[0]
        accuracy = round(keys_to_press / keys_pressed, 2)
        wpm = round(keys_to_press / (game_duration / 60) / 5, 1)
        score = round(accuracy * wpm * len(self.sentence))



        if self.this_is_first_game == False:
            self.game_scores = game_duration, keys_to_press, accuracy, wpm, score

        else: 
            score_info_to_print =   f'Game duration:     {game_duration} seconds\n' +\
                                    f'Chars to type:     {keys_to_press}\n' +\
                                    f'Chars typed:       {keys_pressed}\n' +\
                                    f'Typing Accuracy:   {accuracy:.1%}\n' +\
                                    f'WPM:               {round(wpm)}\n' +\
                                    f'Score:             {score}\n'
            print(score_info_to_print)
            print('Play one more game to see highscores and stats comparison')


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
        # df_summary =.rename({'max': 'best', 'max_diff': 'best_diff'}, axis=1)
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



# score = Score(game_settings)
# best_wpm = score.best_game(sort_by='wpm desc')['wpm']





























