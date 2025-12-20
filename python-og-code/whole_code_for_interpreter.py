l# Content from: src/query.py
import pandas as pd
import os
import time


cwd = os.getcwd()

def query_table(con, table_name, condition=''): 
    query = f'''
    select 
        * 
    from {table_name} 
    where 1 = 1 
        {condition}'''
    
    return pd.read_sql_query(query, con)


def npast_games_words(con, n_past_games, corpus_size):
    '''Returns a list of words from the last n games played
    '''

    query_npast_games_words = f'''
        select
            game_id
            , sentence
            , datetime(max(time), 'unixepoch', 'localtime') time

        from keys_pressed 
        left join clean_games_settings using(game_id)
        group by 1, 2
        order by 3 desc
        limit {n_past_games}
        '''

    df_query = pd.read_sql_query(query_npast_games_words, con)
    done_words = ' '.join(df_query['sentence'].unique()).split(' ')

    # if len(set(done_words)) < corpus_size:
        

    return done_words



def load_query(con, query_name: str, text_only: bool = False) -> list:
    '''Opens a given text file name and execute the 
    query to return a pd.DataFrame
    
    Parameter
    ---------
    query_name str: name of the file name to run
    '''

    # Open file and get the query 
    with open(f'{cwd}/data/queries/{query_name}.sql') as file: 
        query = file.read()

    if text_only == False:
        return pd.read_sql_query(query, con)
    elif text_only == True:
        return query



def letters_ranking(con, n_games: int = 10, n_letters: int = 10): 
    new_query = '''
    with tbl as (
    select 
        key
        , time
        , lead(time) over(partition by game_id order by time desc) lead_time
        , time - lead(time) over(partition by game_id order by time desc) time_diff
        --, lead(key) over(order by time desc) lead_key
        --, lead(time) over(order by time desc) lead_time
        , row_number() over(partition by key order by time desc) rank

    from keys_pressed
    left join clean_games_settings using(game_id)
    where 1=1 
        and word_count > 20
        and correct_key = 1

    order by time 
    )


    select 
        key
        , avg(time_diff) time_diff

    from tbl 
    where rank <= 200

    group by 1
    order by 2 desc

    '''

    df = pd.read_sql_query(new_query, con).sort_values('time_diff')
    print(tabulate(df))

# Content from: src/game.py
import src.detect_keys as dk
from src.query import query_table, letters_ranking
from src.sentence import Sentence
from src.score import Score
import time
import sqlite3
import toml
import os
import shutil
from tabulate import tabulate
import numpy as np
import pandas as pd
from termcolor import colored
import re
import sys

print('suuuuu')

cwd = os.getcwd()
# try: os.remove(f'{cwd}/data/main_database.db')
# except: pass


def update_terminal(): 
    os.system('cls' if os.name == 'nt' else 'clear')


class Game(): 
    def __init__(self): 
        self.game_id = np.random.randint(10**10)
        self.window_width, self.window_height = shutil.get_terminal_size()
        self.create_or_load_database()
        print('\n'*20)
        self.main_menu()



    def create_or_load_database(self): 
        '''Create the two tables of the database
        '''

        # if os.path.exists('data/main_database.db'):
        #     self.con = sqlite3.connect('data/main_database.db')
        #     if pd.read_sql_query('select * from keys_pressed', self.con).empty: 
        #         self.first_game = True
        #     else: 
        #         self.first_game = False
        # else:
        #     self.first_game = True
        self.con = sqlite3.connect(f'{cwd}/data/main_database.db')

        keys_pressed = '''
        CREATE TABLE IF NOT EXISTS keys_pressed (
        key TEXT,
        correct_key INTEGER,
        shift TEXT,
        time REAL,
        game_id INTEGER,
        game_settings TEXT
        )'''
        games_settings = '''
        CREATE TABLE IF NOT EXISTS games_settings (
        game_id INTEGER,
        game_settings TEXT
        )'''

        for query in [keys_pressed, games_settings]: 
            self.con.execute(query)

        if pd.read_sql_query('select * from keys_pressed', self.con).empty: 
            self.first_game = True
        else: 
            self.first_game = False


    
    def propose_menu(self, question: list, choices: dict, nwait_enter=False) -> int:
        '''Print a new menu with question/answers with key pressed
        
        parameters 
        ----------
        question str: question to ask to the player
        choices list: list of choices fo the user to answer 
        
        returns
        ----------
        Index of the list corresponding to the choice of the user
        '''
        # Show question with answers to user
        menu = '\n' + question
        for key, choice in choices.items(): 
            menu += f'\n\t{key} - {choice}'
        menu += '\n'
        print(menu)

        # Get user input and check 
        user_input = ''
        while user_input not in choices.keys(): 
            user_input = dk.next_key_pressed()[0].upper()
            print(f'Wrong letter, you pressed {user_input} but it\' not in {list(choices.keys())}. Press again.')
        return list(choices.keys()).index(user_input)


    def main_menu(self): 
        '''Menu players see when playing the game.
        '''
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nWelcome to TyPy!\n')
        print('Please dont use your mouse but only keyboard keys when prompt too to keep the window active or it wont detect your key presses afterwards.\nHave fun!\n\n')
        choice = self.propose_menu(question = 'Press the letter on the left to navigate through the menu:',
                                   choices = {'P': 'Play game', 
                                              'L': 'Leaderboard', 
                                              'S': 'Settings'})
        if choice == 0: 
            self.confirm_game_settings_before_game()
        elif choice == 1: 
            self.global_preference()
        elif choice == 2: 
            self.leaderboard()


    # @staticmethod
    def read_config(self, config='game_default') -> dict: 
        '''Given a config file name, reads it and return a dictionary
        with the game settings.'''
        with open(f'configs/{config}.toml', 'r') as f:
            game_config = toml.load(f)

        if config == 'game_default': 
            return game_config
        else:
            return self.clean_config(game_config)


    def clean_config(self, config):
        '''Clean the config to make sure that the game can be played
        '''
        with open(f'configs/game_default.toml', 'r') as f:
            default_config = toml.load(f)        
        for key, value in default_config.items(): 
            if key not in config.keys(): 
                config[key] = value 
        return config


    def confirm_game_settings_before_game(self): 
        '''Sets the config for the game before launching it.
        '''
        # Reads, sets and print default game config
        available_configs = [file.replace('.toml', '') for file in os.listdir('configs/')]
        if 'user_default' in available_configs:
            self.game_config = self.read_config('user_default')
        else:
            self.game_config = self.read_config('game_default')

        # print(self.game_config, self.game_preference)

        # Print current game config 
        print("\n\n\nCurrent game config: \n")
        for config_type, config in self.game_config.items():
            game_config_tabulate_basic = [[rule.capitalize().replace('_', ' '), value] for rule, value in config.items()]
            print(tabulate(game_config_tabulate_basic, headers=[config_type.capitalize(), 'Value'], showindex=True), '\n')

        # Propose current game config
        choice = self.propose_menu(question = 'Do you wanna change Any?',
                                   choices = {'Y': 'Yes', 
                                              'N': 'No, play the game', 
                                              'Q': f'Quick change'})

        if choice == 0: 
            self.change_game_config()
        elif choice == 1: 
            self.start_game()
        elif choice == 2: 
            self.quick_change_game_config()
        
        

    def quick_change_game_config(self): 
        '''Makes quick changes to rules using string pattern
        '''
        print('Change rules using the index of the table above and using this format:')
        print('Separate the rule index and value by a space and each new rule with a coma.')
        print('<rule_index> <rule_value>, <rule_index>... Press enter to validate and start the game.\n')

        # Capture full input of the user
        key = ''
        new_rules = '  '
        while key != 'return':
            new_rules += key 
            print(new_rules, end='\r')
            key = dk.next_key_pressed()[0].lower().replace('space', ' ')
            if key == 'back ': 
                new_rules == new_rules[:-1]
                key = ''
        

        # Set new rules
        for new_rule in new_rules.split(','): 
            new_rule, new_value = new_rule.strip().split(' ')
            rule = list(self.game_config.keys())[int(new_rule)]
            self.game_config[rule] = new_value


        self.start_game()


    def change_rule(self): 
        '''make tbl with all definitions, config (header, def, each config)'''
        print('Change rule')



    def change_game_config(self):
        '''
        '''
        print(self.available_configs)
        time.sleep(1)
        self.game_config = self.read_config('performance')['game_config']


        # if change config, set default first in case config doesnt have all the rules
        print('change game config')


        self.game_setup()



    def global_preference(self): 
        print('Play game function')



    def leaderboard(self):
        print('Leaderboard')


    def check_game_config(self): 
        print('check_game_config')


    def game_setup(self): 
        print('game_setup')
        


    @staticmethod
    def wpm(key_count, seconds): 
        return key_count / seconds * 60 / 5
    

    @staticmethod
    def print_multine_with_carriage(str): 
        lines_count = str.count('\n') + 1
        str = f"\x1B[{lines_count}A" + str.replace('\n', "\x1B[0K" + '\n')
        print(str, flush=True)


    def generate_chart(self, wpm_list):
        df = pd.DataFrame(wpm_list, columns=['wpm'])
        # Calculate the maximum value in the 'wpm' column
        max_wpm = df['wpm'].max()

        # Create a list of empty strings to represent each row in the chart
        rows = [' ' * len(df) for _ in range(20)]

        # Loop over the rows in the DataFrame and add an 'x' to the appropriate position in the chart
        for i, row in df.iterrows():
            # Calculate the y position for this data point
            y = int(row['wpm'] / max_wpm * 19)

            # Add the 'x' to the appropriate position in the chart
            rows[19 - y] = rows[19 - y][:i] + 'x' + rows[19 - y][i + 1:]

        # Add the y-axis to the chart
        for i in range(20):
            rows[i] = '| ' + rows[i]

        # Add the x-axis to the chart
        rows.append('+ ' + '-' * len(df) + '\n')

        # Convert the list of rows to a single string
        chart = '\n'.join(rows)

        print('\n' * 20)
        print(chart, end='\r')


    def generate_chart(self, data, height=20, width=80):
        # Determine the maximum value in the data
        max_val = max(data)

        # Determine the number of data points to plot
        num_points = min(len(data), width)

        # Determine the x-axis tick interval
        tick_interval = max(1, num_points // 10)

        # Determine the maximum value for the y-axis
        if len(data) >= height:
            max_y = max_val
        else:
            max_y = data[0]

        # Create a list of empty strings to represent each row in the chart
        rows = [' ' * num_points for _ in range(height)]

        # Loop over the data points and add an 'x' to the appropriate position in the chart
        for i in range(num_points):
            # Calculate the index of the data point to use for this position
            index = int(i / num_points * len(data))

            # Calculate the y position for this data point
            y = int(data[index] / max_y * (height - 1))

            # Add the 'x' to the appropriate position in the chart
            rows[height - 2 - y] = rows[height - 2 - y][:i] + 'x' + rows[height - 2 - y][i + 1:]

        # Add the y-axis ticks to the chart
        for i in range(height - 1):
            if i % (height // 10) == 0:
                rows[i] = '|' + rows[i][1:]
            else:
                rows[i] = '|' + rows[i][1:]

        # Add the x-axis ticks to the chart
        for i in range(0, num_points, tick_interval):
            rows[-1] = rows[-1][:i] + '-' + rows[-1][i + 1:]
            rows[-2] = rows[-2][:i] + str(i) + rows[-2][i + 1 + len(str(i)):]

        # Add the x-axis label to the chart
        rows[-1] = rows[-1][:-1] + '+'

        # Convert the list of rows to a single string
        chart = '\n'.join(rows)
        print(chart)
        # return chart

        
    def hud(self, sentence_to_display, correct_key_count, keys_pressed): 
        '''What to print during the game
        '''


        infos_to_print = ''
        # infos_to_print = '\n' * self.window_height
        if len(keys_pressed) > 1:
            # print(keys_pressed[-1][3],  keys_pressed[0][3])
            wpm = self.wpm(correct_key_count, keys_pressed[-1][3] - keys_pressed[0][3])
            self.wpm_list.append(wpm)
            wpm_formatted = self.color_formatting(round(wpm, 1), self.best_wpm)

            if self.game_config['display']['display_wpm'] == True:
                infos_to_print += f'WPM: {wpm_formatted}\n'

            # print('\n' * self.window_height)
            if self.game_config['display']['display_chart'] == True:
                self.generate_chart(self.wpm_list)
        else: 
            self.wpm_list = []

        if self.game_config['display']['display_words_left'] == True:
            words_left = sentence_to_display.count(' ')
            infos_to_print += f'{words_left + 1} words left to type\n'

        infos_to_print += ' ' + ' '.join(sentence_to_display.split(' '))[:self.window_width - 1]
        # infos_to_print += ' ' + ' '.join(sentence_to_display.split(' '))
        infos_to_print += ' ' * (self.window_width - len(infos_to_print)-10) 
        # print(infos_to_print, '\t'*5, end='\r')
        # print(repr(infos_to_print), '\n'*5)
        update_terminal()
        print(infos_to_print)
        # self.print_multine_with_carriage(infos_to_print) # This adds a new line at the end
        # sys.stdout.write(infos_to_print)
        


    def start_game(self): 
        print('Play game', '\n' * self.window_height)

        # Create sentence and score
        self.score = Score( 
            self.game_config['rules'],
            self.first_game,
            self.con)
        
        # Check if first game with those game particular settings
        try: 
            game_count = query_table(self.con, 'clean_games_settings', self.score.general_condition).shape[0]
            if game_count == 0: 
                self.first_game = True
        except pd.errors.DatabaseError: 
            self.first_game = True


        # Get best wpm
        try: 
            self.best_wpm = pd.read_sql_query(f'select * from games_summary where 1=1 {self.score.general_condition} order by wpm desc limit 1', self.con).loc[0, 'wpm']
            if self.best_wpm == None: 
                self.best_wpm == 0
                self.first_game == True 
        except: 
            self.best_wpm = 70

        
        # Generate sentence
        sentence = Sentence(
            self.game_config['rules'], 
            self.first_game,
            self.con,
            ).sentence


        #####################################
        #### Here really starts the game ####
        #####################################
        # self.best_score = Score().best_scores(self.config) # best game for each of the rules or only for one? i think the best score for each of the rules. This function in Score() could calculate for each of the rules the best, avg (describe() type) and would return what would be in the dictionary/parameters of the function
        keys_pressed = []
        correct_key_count, incorrect_key_count = 0, 0
        sentence_to_display = sentence
        for letter_to_type in sentence:
            # Refresh HUD
            self.hud(
                sentence_to_display,
                correct_key_count = correct_key_count,
                keys_pressed = keys_pressed,
            )

            # As long as the correct key is not typed
            while True: 
                guess, shift_pressed = dk.next_key_pressed()
                correct_key = guess == letter_to_type
                keys_pressed.append([str(guess), correct_key, shift_pressed, time.time(), self.game_id]) 

                # check opposite/right shift

                if correct_key: 
                    sentence_to_display = sentence_to_display[1:]
                    correct_key_count += 1
                    break # The while loop
                else:
                    incorrect_key_count += 1

        
        # End game
        self.end_game(
            sentence, 
            keys_pressed
        )




    def end_game(self, sentence, keys_pressed): 
        '''What happens after the game completed the full sentence. 
        the game data will always be saved then it's matter of user's
        ''' 
        print('\n'*20)
        # Log game
        game_data = {**self.game_config['rules'], **self.game_config['display']}
        game_data.update(
            {'sentence': sentence,
             'keys_pressed': keys_pressed,
             'game_id': self.game_id}
        )
        self.score.log_game(game_data)
         
        # Propose to save on gbg, back to main menu, leaderboard
        letters_ranking(self.con)

        self.score.summarize_games_scores(self.con)
        if self.first_game == False:
            self.compare_game()
        else:
            df_game_summary = self.score.load_game_stats(self.game_id)
            print('Game summary:')
            print(tabulate(df_game_summary.T))


        # What to do after the game    
        print('\n' * 1)
        choice = self.propose_menu(question = 'What do you want to do?',
                                   choices = {'P': 'Play again', 
                                              'M': 'Main menu', 
                                              'C': f'Change settings'})

        self.game_id = np.random.randint(10**10)
        self.first_game = False
        if choice == 0: 
            self.start_game()
        elif choice == 1: 
            self.main_menu()
        elif choice == 2: 
            self.confirm_game_settings_before_game()



    def color_formatting(self, val_to_print, val_to_compare, higher_better=True) -> str: 
        '''
        Format a value by adding color to it based on its comparison with another value.
        
        Parameters:
        val_to_print (int or float): The value to be formatted and printed.
        val_to_compare (int or float): The value to be compared with `val_to_print`.
        higher_better (bool, optional, default True): A flag indicating whether higher values are considered better (True) or lower values are considered better (False). Default is True.

        Returns:
            str: The formatted value with color added to it. The color depends on the comparison between `val_to_print` and `val_to_compare`:
                * Red if `val_to_print` is smaller than `val_to_compare` when `higher_better` is True, or 
                * Yellow if `val_to_print` is equal to `val_to_compare`, or 
                * Green if `val_to_print` is greater than `val_to_compare` when `higher_better` is False.
        '''
        sign = 1 if higher_better == True else -1
        # print(val_to_print, sign, val_to_compare)
        if sign * val_to_print < sign * val_to_compare: 
            return colored(val_to_print, 'red')
        elif sign * val_to_print == sign * val_to_compare: 
            return colored(val_to_print, 'yellow')
        else: 
            return colored(val_to_print, 'green')


    # def query(self, query): 
    #     return pd.read_sql_query(query', self.con)





    ################
    # rewrite compare_game() it's terrible
    ################
    def compare_game(self): 
        '''Compare stats of the game '''

        # # Current game stats
        # query = f'''
        # select 
        #     round(game_duration) as game_duration 
        #     , keys_to_press
        #     , keys_pressed
        #     , keys_pressed - keys_to_press as errors
        #     , round(accuracy * 100, 2) as accuracy
        #     , round(wpm, 2) as wpm
        #     --, round(cps, 4) as cps
        #     , word_count
        
        # from games_summary 
        # where 1=1
        #     and game_id = {self.game_id} 
        # '''
        # df_game_summary = pd.read_sql_query(query, self.con)
        # print(tabulate(df_game_summary.T, headers=['Metric', 'Score'], numalign="left"))
        # print('\n\n')

        metrics = ['wpm', 'accuracy', 'game_duration', 'keys_pressed', 'keys_to_press', 'errors']
        comparisons = ['current', 'max', 'mean', 'last']
        variation = True

        general_condition = self.score.general_condition
        df = pd.read_sql_query(f'select * from games_summary where 1=1 {general_condition}', self.con)
        total_games = len(df)

        df_described = df.describe(include='all')
        df_described = df_described.loc[[index for index in df_described.index if index in comparisons]]


        df_described.loc['current'] = df.sort_values('date_time', ascending=False).iloc[0]
        if self.first_game: 
            print(df_described)
            return
        if 'last' in comparisons: 
            df_described.loc['last'] = df.sort_values('date_time', ascending=False).iloc[1]


        df_described = df_described[metrics]

        # # df_described['max_diff'] = df_described['max_diff'].astype(int).astype(str).replace('0', 'New Record!')
        # # df_described = df_described.drop(['mean'], axis=1)[['current', 'max', 'max_diff', 'mean_diff', 'last', 'last_diff']].reset_index(names='')


        # tabulate_values = [[]]

        # # for column in df_described.columns: 
        # #     for row in df_described.index: 
        # #         value = df.loc[row, column]

        # #         if row == 'wpm': 

        # # df_described.loc['accuracy'] * 100 

        # formatting = {
        #     'wpm': {''}
        # }

        df_described['wpm'] = df_described['wpm'].round(1)
        df_described['accuracy'] = (df_described['accuracy'] * 100).round(2)
        df_described['game_duration'] = df_described['game_duration'].astype(int)
        df_described['keys_to_press'] = df_described['keys_to_press'].astype(int)
        df_described['keys_pressed'] = df_described['keys_pressed'].astype(int)
        df_described['errors'] = df_described['errors'].astype(int)


        # df_described = df_described.T




        # df_described = df_described.T#.astype(str).T[comparisons]



        # df_described['max_diff'] = (df_described['max'] - df_described['current']).astype(int)
        # # df_described['max_variation'] = df_described['current'] / df_described['max_diff'] * 100
        # df_described['mean_diff'] = (df_described['mean'] - df_described['current'])
        # # df_described['mean_variation'] = df_described['current'] / df_described['mean_diff'] * 100
        # df_described['last_diff'] = df_described['last'] - df_described['current']
        # # df_described['last_variation'] = df_described['current'] / df_described['last_diff'] * 100


        # df_described = df_described.reset_index(names=)

        higher_better_map = {
            'wpm': False,
            'accuracy': False,
            'game_duration': True, 
            'keys_pressed': False, 
            'keys_to_press': False, 
            'errors': True,
        }



        # tabular_data = []
        # for column in df_described.columns:
        #     if column in ['current']:
        #         continue
            
        #     current_value = df_described.loc[index, 'current']
        #     for index in df_described.index:
        #         other_value = df_described.loc[index, column]
        #         comparison = color_formatting(current_value, other_value, higher_better_map[column])
        #         tabular_data.append([index, comparison])

        tabular_data = []
        for metric in metrics: 
            row = [metric]
            for comparison in comparisons: 
                current_value = df_described.loc['current', metric]    
                if comparison == 'current': 
                    row.append(current_value)
                    continue 
            
                comparison_value = df_described.loc[comparison, metric]
                if metric in ('wpm', 'accuracy'):
                    value = self.color_formatting(comparison_value, current_value, higher_better_map[metric])
                else: 
                    value = comparison_value
                row.append(value )
            tabular_data.append(row)

        # tabular_data = list(map(list, zip(*tabular_data)))

        # display(df_described)
        print(tabulate(tabular_data, headers=[f'Total games: {total_games}'] + comparisons))
        # # tabular_data





# Content from: src/concat_all_db.py




import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from score import Score
import os 
from tabulate import tabulate

current_dir = os.getcwd()
con = sqlite3.connect("data/main_database.db")
# pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.max_columns', None)
connew = sqlite3.connect("data/main_database_new.db")

from tqdm import tqdm

import os

# Directory to start the search
directory = os.getcwd()

database_paths = []
# Loop through all the directories and files starting from the given directory
for root, dirs, files in os.walk(directory):
    # Loop through all the files in the current directory
    for filename in files:
        # Print the full path to the file
        file_path = os.path.join(root, filename)
        print(file_path)

        if file_path.endswith('.db'):
            database_paths.append(file_path)





def concat_sqlite_databases(databases, output_path):
    """
    Concatenate tables from SQLite databases with the same table and column names
    and write the result to a new SQLite database.

    Args:
        databases (list of str): Paths to the input SQLite databases.
        output_path (str): Path to the output SQLite database.

    Returns:
        None.
    """

    # Create a connection to the output database
    output_conn = sqlite3.connect(output_path)

    # Loop through each input database
    for db_path in tqdm(databases):
        try: 
            # Create a connection to the input database
            input_conn = sqlite3.connect(db_path)

            # Get a list of the table names in the input database
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", input_conn)['name'].tolist()

            # Loop through each table in the input database
            for table_name in tqdm(tables):
                # Read the current table from the input database into a DataFrame
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", input_conn)

                # Check if a table with the same name already exists in the output database
                table_exists = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'", output_conn)

                # If the table doesn't exist, write the DataFrame to a new table in the output database
                if table_exists.empty:
                    df.to_sql(table_name, output_conn)

                # If the table already exists, check if the column names are the same
                else:
                    existing_cols = pd.read_sql_query(f"PRAGMA table_info({table_name})", output_conn)['name']
                    new_cols = df.columns
                    # If the column names are the same, concatenate the new data with the existing data in the output database
                    existing_data = pd.read_sql_query(f"SELECT * FROM {table_name}", output_conn)
                    concatenated_data = pd.concat([existing_data, df], axis=0)
                    print(concatenated_data.shape, concatenated_data.drop_duplicates().shape)
                    concatenated_data.drop_duplicates().to_sql(table_name, output_conn, if_exists='replace', index=False)

            # Close the connection to the input database
            input_conn.close()

        except:
            print(f"Error: {db_path} is not a valid database")

    # Close the connection to the output database
    output_conn.close()




concat_sqlite_databases(database_paths, 'data/main_database.db')

# Content from: src/detect_keys.py
import pygame

# print('pre init')
pygame.init()

# print('post init')

# screen = pygame.display.set_mode((400, 300))



#########################
# REWRITE THIS FUNCTION #
# Add some inclusion and exclusion of character type, symbols and stuff
#########################
# def next_key_pressed(recursive=[]):
#     '''Detects whick key gets pressed and which shift if combination.
#     Example: a is typed a where A is typed shift + A. 
    
#     Returns
#     -------
#     guess str: which key has been pressed 
#     which_shift str: which shift key (right, left, None) has been pressed
#     '''

#     key_map_shift = {'`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', 'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T', 'y': 'Y', 'u': 'U', 'i': 'I', 'o': 'O', 'p': 'P', '[': '{', ']': '}', "''": '|', 'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'H', 'j': 'J', 'k': 'K', 'l': 'L', ';': ':', "'": '"', 'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B', 'n': 'N', 'm': 'M', ',': '<', '.': '>', '/': '?'}
#     key = None
#     count = 0
#     while key==None:
#         # Checking if any shift is pressed
#         mods = pygame.key.get_mods()
#         left_shift_pressed = True if mods and pygame.KMOD_LSHIFT else False
#         right_shift_pressed = True if mods and pygame.KMOD_RSHIFT else False
#         shift_pressed = True if True in (left_shift_pressed, right_shift_pressed) else False

#         for event in pygame.event.get():
#             if event.type == pygame.KEYDOWN:
#                 guess = pygame.key.name(event.key)
                
#                 if shift_pressed and guess != 'space':
#                     try: 
#                         guess = key_map_shift[guess] if shift_pressed is True else guess
#                     except KeyError: 
#                         continue
                    
#                 key=guess
#                 break
 
#         count += 1


#     if guess in recursive: 
#         guess, _ = next_key_pressed(recursive)



#     which_shift = 'right' if right_shift_pressed == True else ('left' if left_shift_pressed == True else None)
#     return guess, which_shift
import sys   
import termios
import tty
import os

def next_key_pressed():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if ch == '0': 
        raise KeyboardInterrupt
    # return ch.replace(' ', 'space'), None
    return ch, None
# while True: 
#     key, shift = next_key_pressed()
#     print(key, shift)

def rule_force_shift(key_pressed, shift_pressed):
    right = '&*()_+|}{POIUYHJKL:"?><MNB'
    left = '~!@#$%^QWERTGFDSAZXCVB'

    if key_pressed in eval(shift_pressed):
        print(key_pressed, shift_pressed)
        print('WRONG SHIFT KEY', '\n'*2)
        return ' '

    else:
        return key_pressed




# Content from: src/display.py
from termcolor import colored





def get_correct_size_string(string: str, spacing: int) -> int: 
    string = str(string)
    s = string + ' ' * (spacing - len(string))

    return s

def color_int(text_to_print, threshold=0, spacing=0, prefix='', suffix=''):
    if text_to_print < threshold:
        float_colored = colored(get_correct_size_string(prefix + str(text_to_print) + suffix, spacing), 'red')
    else:
        float_colored = colored(get_correct_size_string(prefix + str(text_to_print) + suffix, spacing), 'green')
    
    return float_colored


def info_to_print(display_infos, sentence_to_display, char, key_pressed, best_wpm, words_left_to_type):
    '''For every key pressed when playing the game, what is printed refreshed. 
    This function is made for what's get printed and in which case'''
    print('\n'*20)

    if len(key_pressed) > 1 and display_infos == True: 
        count_correct_keys = len(list(filter(lambda x: x[1] == True, key_pressed)))
        duration = key_pressed[-1][2] - key_pressed[0][2]
        wpm = count_correct_keys / duration * 60 / 5

        wpm_colored = color_int(round(wpm, 1), best_wpm)
        print('\n'*20)
        print(f'Words left to type: {words_left_to_type}\nWPM: {wpm_colored}\n')#|{wpm_var_best}|{wpm_diff_best}\t{wpm_var_avg}|{wpm_diff_avg}\n')

    else: 
        print(f'Words left to type: {words_left_to_type}\n')

    words_to_display_count = 5
    words_to_display = ' '.join(sentence_to_display.split(' ')[:words_to_display_count])
    print(' ', words_to_display, '\t'*5, end='\r')
    return words_to_display





# Content from: src/sentence.py
import pandas as pd
import numpy as np
import os


class Sentence(): 
    def __init__(self, game_config, first_game, con): 
        # self.game_config = game_config
        self.cwd = os.getcwd()
        self.game_config = game_config
        self.first_game = first_game
        self.con = con

        self.word_list = self.load_words(game_config['difficulty'])
        if self.game_config['train'] == False: 
            self.word_list = self.word_list[:self.game_config['word_count']]
        else: 
            # self.word_list = self.get_n_slowest_words(self.word_list)
            self.word_list = self.only_one_letter(self.word_list)


        # print(f'word_list: {self.word_list}')
        self.capitalize_word_list(game_config['capitalized_words'], game_config['capitalized_letters'])
        # print(f'cap: {self.word_list}')
        self.add_punctuation(game_config['punctuation'], game_config['punctuation_char'])
        # print(f'punc: {self.word_list}')
        self.sentence = ' '.join(self.word_list)
        # print(f'sentence: {self.sentence}')



    def load_words(self, difficulty) -> list:
        '''Opens one of three lists of words depending on the difficulty. 
        common_words.txt contains 3000 common word
        hard_words.txt contains 370k words words generally longer and harder 
        to type compared to the common word 
        google_most_used_words is the top 10k on Google
        '''

        if difficulty.lower() == 'hard':
            file_path = f'{self.cwd}/data/text/hard_words.txt'
        elif difficulty.lower() == 'easy':
            file_path = f'{self.cwd}/data/text/common_words.txt'
        elif difficulty.lower() == 'medium':
            file_path = f'{self.cwd}/data/text/google_most_used_words.txt'
            
        with open(file_path) as file: 
            all_words = file.read().split('\n')


        if self.first_game == False or self.game_config['train'] == False: 
            try: 
                banned_words = self.query.npast_games_words(self.game_config['n_games_banned_words'], len(all_words))
            except:
                banned_words = []
        else:
            banned_words = []


        # print(f'banned words {banned_words}')
        

        # Removing non letters characters and words g/l than max/min length
        word_list = self.filter_word_length(all_words, self.game_config['word_length_min'], self.game_config['word_length_max'])
        word_list = [''.join([char for char in word if char.isalpha()]).lower() for word in word_list if ''.join([char for char in word if char.isalpha()]).lower() not in banned_words]
        np.random.shuffle(word_list)
        return word_list


    def filter_word_length(self, all_words, word_length_min, word_length_max): 
        # print(word_length_min)
        return [word for word in all_words if word_length_min <= len(word) <= word_length_max]


    def capitalize_word_list(self, capitalized_words, capitalized_letters): 
        words_to_cap = capitalized_words if capitalized_words > 1 else int(len(self.word_list) * capitalized_words)

        for index, word in enumerate(self.word_list[:words_to_cap]): 
            if capitalized_letters == "First":
                self.word_list[index] = word.title()
            else:
                # Generate a list of n numbers, suffle it and keep the indexes >= to the number of letters to cap
                random_list = list(range(len(word)))
                np.random.shuffle(random_list)
                letters_to_cap = capitalized_letters if capitalized_letters > 1 else round(len(word) * capitalized_letters)
                # print(words_to_cap, letters_to_cap, len(word) * capitalized_letters)
                random_list = random_list[:letters_to_cap]
                self.word_list[index] = ''.join([char.upper() if index_char in random_list else char for index_char, char in enumerate(word)])
        
        np.random.shuffle(self.word_list)


    def add_punctuation(self, punctuation, punctuation_char):
        '''Given a list of word and punctuation_word_count_perc,
        randomly chooses a punctuation and adds it to the words
        
        parameter
        ---------
        sentence str: list of word
        '''
        punctuation_count = punctuation if punctuation > 1 else int(len(self.word_list) * punctuation)

        common_punctuations = ['()', '{}', '[]', '!', "''", '*', ',', '.', ';', ':', '-', '_', ]
        common_punctuations = ['()', '!', "''", '*', ',', '.', ';', ':', '-', '_', '<', '>', '/', '?', '=']
        common_punctuations = [',', '.', '-', '!', "''", '()']
        double_char = [punc for punc in common_punctuations if len(punc) > 1]
        

        # Limiting characters to use 
        np.random.shuffle(common_punctuations)
        common_punctuations = common_punctuations[:punctuation_char]

        for index in range(punctuation_count):
            word = self.word_list[index]
            rdm_punctuation = np.random.choice(common_punctuations)
            if len(rdm_punctuation) > 1: 
                word = rdm_punctuation[0] + word + rdm_punctuation[1]
            else: 
                word = rdm_punctuation + word + rdm_punctuation
            
            self.word_list[index] = word

        np.random.shuffle(self.word_list)


    def get_n_slowest_words(self, word_list):
        '''Among the list of word, find the words that would 
        potentially take the longest to type based on the 
        average duration it takes to the player to type all 
        each and individual letters of the words.

        parameters
        ----------
        word_count int: numbers of worst words to return
        '''

        # Load key score 
        df_keytime = self.query.load_query('time_per_key_pressed')
        key_score = dict(zip(df_keytime['following_key'], df_keytime['time_diff'].round(4)))

        # Get score for each word
        # print(f'{min([len(word) for word in word_list]) = } - {len(word_list) = }')
        df_words = pd.DataFrame(word_list, columns=['word'])

        # This is supposed to add a weight so that not only least frequent letters are proposed but it's not working
        # all_words_letters = ''.join(df_words['word'])
        # all_words_letters_count = {letter: all_words_letters.count(letter) for letter in set(all_words_letters)}
        # all_words_letters_count = {key: -(value - min(all_words_letters_count.values()))/(max(all_words_letters_count.values()) - min(all_words_letters_count.values())) for key, value in all_words_letters_count.items()}
        # key_score = {key: key_score[key] * all_words_letters_count[key] for key in all_words_letters_count.keys()}

        df_words['word_score'] = df_words['word'].apply(lambda word: sum([key_score[char] for char in word.lower().replace('-', '') if char in key_score.keys()]))
        df_words['avg_letter_score'] = df_words['word_score'] / df_words['word'].str.len()


        # Sort dataframe and pick the top 25 words with at least four letters
        df_words.sort_values('avg_letter_score', ascending=self.game_config['train_easy']).to_csv('word_score.csv', index=False)
        # print(df_words.head(100))
        top_n = df_words.sort_values('avg_letter_score', ascending=self.game_config['train_easy'])
        top_n = top_n.iloc[:self.game_config['word_count'], 0]
        return list(top_n)
    


    def only_one_letter(self, word_list): 
        query = '''
        with kp as (
        select 
            distinct
            key
            , time
            , correct_key
            , game_id
            , row_number() over(partition by key order by time desc) as key_index
            

        from keys_pressed 
        where 1=1
            and correct_key = 1
            and game_id > 100
            and time is not null
        order by time
        )

        , tbl1 as (
        select
            key
            , lead(key) over(partition by game_id order by game_id, time) following_key
            , time
            , lead(time) over(partition by game_id order by game_id, time) following_time
            , game_id

        from kp
        where 1=1
            and key_index <= 200
        )

        select 
            following_key
            , avg(following_time - time) as time_diff
            , count(*) count

        from tbl1
        where 1=1
            and following_key is not null
        group by 1
        having 1=1
            --and count < 200
        order by time_diff asc
        '''
        new_query = '''
        with tbl as (
        select 
            key
            , time
            , lead(time) over(partition by game_id order by time desc) lead_time
            , time - lead(time) over(partition by game_id order by time desc) time_diff
            --, lead(key) over(order by time desc) lead_key
            --, lead(time) over(order by time desc) lead_time
            , row_number() over(partition by key order by time desc) rank

        from keys_pressed
        left join clean_games_settings using(game_id)
        where 1=1 
            and word_count > 20
            and correct_key = 1

        order by time 
        )


        select 
            key
            , avg(time_diff) time_diff

        from tbl 
        where rank <= 200

        group by 1
        order by 2 desc

        '''

        df = pd.read_sql_query(new_query, self.con).sort_values('time_diff', ascending=True).query('key != " "')#.query('following_key.str.lower().str.isalpha() and following_key.str.lower() == following_key and following_key.str.len() == 1')
        print(df.head(50))
        letter = df.iloc[0, 0]
        # voyelle = df.query('following_key.str.contains("a|e|i|o|u|y")').iloc[0, 0]

        letter_count = {}
        for word in word_list:
            letter_count[word] = word.count(letter) #int(np.ceil(word.count(letter) + word.count(voyelle)/3)) #/3 is a weight so it does't count as much as a letter. In testing

        freq = dict(sorted(letter_count.items(), key=lambda item: item[1], reverse=True))
        freq = {k: v for k, v in freq.items() if v > 0}
        word_list = [word for word, count in freq.items() for x in range(count)]
        
        total_weights = sum(freq.values())
        probas = [weight/total_weights for weight in freq.values()]
        word_list = np.random.choice(list(freq.keys()), self.game_config['word_count'], False, probas)

        return list(word_list)

# Content from: src/score.py
import numpy as np
import pandas as pd
from src.query import query_table





class Score(): 
    def __init__(self, game_rules, first_game, con):
        self.game_rules = game_rules
        self.first_game = first_game
        self.con = con
        self.make_condition()


    def make_condition(self): 
        '''Makes a condition for all the WHERE statements that
        load data so that the compared games have the same rules.
        '''
        self.general_condition = ''
        rules = {'word_count': 'int', 
                 'word_length_max': 'int', 
                 'word_length_min': 'int', 
                 'capitalized_words': 'int', 
                 'capitalized_letters': 'int', 
                 'punctuation': 'int', 
                 'force_shift': 'bool', 
                 'difficulty': 'str', 
                 'train': 'int', 
                 'train_easy': 'int'}
        print(self.game_rules)
        for rule, type in rules.items(): 
            if isinstance(self.game_rules[rule], str): 
                self.general_condition += f' AND {rule} = "{self.game_rules[rule]}" '
            else: 
                self.general_condition += f' AND {rule} = {self.game_rules[rule]} '

        # print(self.general_condition)






    
    def log_game(self, game_data): 
        '''Save the data produced during the games
        '''
        # Saving keys strokes
        column_names = ['key', 'correct_key', 'shift', 'time', 'game_id']
        df_keys = pd.DataFrame(game_data['keys_pressed'], columns=column_names)
        df_keys.to_sql('keys_pressed', self.con, if_exists='append', index=False)

        # Saving game settings
        column_names = ['game_id', 'game_settings']
        game_id = game_data['game_id']
        del game_data['game_id']
        del game_data['keys_pressed']
        df_game_data = pd.DataFrame([[game_id, str(game_data)]], columns=column_names)
        df_game_data.to_sql('games_settings', self.con, if_exists='append', index=False)

        # Explode dictionary
        self.clean_game_settings(self.con, game_id)


    @staticmethod
    def clean_game_settings(con, game_id: int):
        '''Explodes the dictionary of the last game and append it into the 
        clean table
        '''

        df_current_game_settings = query_table(con, 'games_settings', f'and game_id = {game_id}')
        df_current_clean_games_settings = df_current_game_settings['game_settings'].apply(lambda x: pd.Series(eval(x)))
        df_current_clean_games_settings.insert(0, 'game_id', df_current_game_settings.loc[0, 'game_id'])
        df_current_clean_games_settings.to_sql('clean_games_settings', con, if_exists='append', index=False)
    
    @staticmethod
    def clean_all_games_settings(con):
        '''Explodes the dictionary of the last game and append it into the 
        clean table
        '''

        df_current_game_settings = query_table(con, 'games_settings')
        df_current_clean_games_settings = df_current_game_settings['game_settings'].apply(lambda x: pd.Series(eval(x)))
        df_current_clean_games_settings.insert(0, 'game_id', df_current_game_settings['game_id'])
        df_current_clean_games_settings.to_sql('clean_games_settings', con, if_exists='replace', index=False)
    


    @staticmethod
    def summarize_games_scores(con): 
        query = f"""
            select
                distinct
                kp.game_id
                , max(kp.time) maxdatetime_unix
                , min(kp.time) mindatetime_unix
                , datetime(max(kp.time), 'unixepoch', 'localtime') as date_time
                , max(kp.time) - min(kp.time) as game_duration
                , sum(kp.correct_key) as keys_to_press
                , count(*) as keys_pressed
                , count(*) - sum(kp.correct_key) as errors
                , round(CAST(sum(kp.correct_key) as REAL) / count(*), 3) as accuracy
                , sum(kp.correct_key) / ((max(kp.time) - min(kp.time)) / 60) / 5 as wpm
                , sum(kp.correct_key) / (max(kp.time) - min(kp.time)) as cps
                , length(cgs.sentence) as sentence_length
                , length(cgs.sentence) * (sum(kp.correct_key) / ((max(kp.time) - min(kp.time)) / 60) / 5) * round(CAST(sum(kp.correct_key) as REAL) / count(*), 3) as score
                , cgs.sentence
                , cgs.word_count
                , coalesce(cgs.word_length_max, 1000) as word_length_max
                , coalesce(cgs.word_length_min, 0) as word_length_min
                , coalesce(cgs.capitalized_words, 0) as capitalized_words
                , coalesce(cgs.capitalized_letters, 0) as capitalized_letters
                , coalesce(cgs.punctuation, 0) as punctuation
                , coalesce(cgs.force_shift, 0) as force_shift
                , coalesce(cgs.difficulty, 0) as difficulty
                , coalesce(cgs.train, 0) as train
                , case 
                    when cgs.train in (null, 0) then 0
                    else coalesce(cgs.train_easy, 0)
                    end as train_easy
                , LOWER(cgs.player_name) as player_name

            from keys_pressed kp 
            left join clean_games_settings cgs using(game_id)
            where 1=1

            group by 1
            order by maxdatetime_unix asc
            """

        df_high_score = pd.read_sql_query(query, con)
        df_high_score.to_sql('games_summary', con, if_exists='replace', index=False)


    

    def summaryze_rules(): 
        print('Summary rules')


    def load_game_stats(self, game_id): 
        query = f'''
        select 
            round(wpm, 2) as wpm
            , round(accuracy * 100, 2) as accuracy
            , round(game_duration) as game_duration 
            , keys_pressed
            , keys_to_press
            , keys_pressed - keys_to_press as errors
            --, round(cps, 4) as cps
        
        from games_summary 
        where 1=1
            and game_id = {game_id} 
        '''

        df_game_summary = pd.read_sql_query(query, self.con)
        return df_game_summary


    def load_best_stats(self): 
        query = f'''
        select 
            round(game_duration) as game_duration 
            , keys_to_press
            , keys_pressed
            , keys_pressed - keys_to_press as errors
            , round(accuracy * 100, 2) as accuracy
            , round(wpm, 2) as wpm
            --, round(cps, 4) as cps
            , word_count
        
        from games_summary 
        where 1=1
            and game_id = {self.game_id} 
            and word_count = {self.word_count}
        '''

        df_game_summary = pd.read_sql_query(query, self.con)




    # def make_conditions(self): 
    #     for key, value in self.conf




# class Score():
#     def __init__(self, game_settings, con): 
#         self.game_settings = game_settings
#         self.con = con

#         # Create main condition 
#         self.game_settings_query_condition = []
#         for key, value in self.game_settings.items():
#             if key not in ('word_count', 'min_word_length', 'max_word_length', 'capitalized_words_count', 'capitalized_letters_count_perc', 'punctuation_word_count_perc', 'force_shift', 'hard_mode', 'train_letters', 'train_letters_easy_mode'):
#                 continue
#             if type(value) == str: 
#                 condition = f'{key} == "{value}"'
#             else:
#                 condition = f'{key} == {value}'
                
#             self.game_settings_query_condition.append(condition)


        
#         # Check if a game has already been played by checking if there is any table in the master table
#         query_sqlite_master = f"""
#                 SELECT 
#                     *
#                 FROM sqlite_master
#                 """
#         df_sqlite_master = pd.read_sql_query(query_sqlite_master, self.con)
        
#         if df_sqlite_master.shape[0] == 0:
#             self.this_is_first_game = True
#             self.this_is_first_game_with_current_settings = True
#         else:
#             self.this_is_first_game = False

#         # Check if a game has already been played with similar game settings
#         if self.this_is_first_game == False:
#             condition = ''.join([' AND ' + condition for condition in self.game_settings_query_condition])
#             query_summary = f"""
#                 SELECT 
#                     game_duration
#                     , sentence_length
#                     , accuracy
#                     , wpm
#                     , score

#                 FROM games_summary
#                 WHERE 1=1
#                     {condition}
#                 """

#             df_summary = pd.read_sql_query(query_summary, self.con) 
            
#             if df_summary.shape[0] == 0:
#                 self.this_is_first_game_with_current_settings = True
#             else:
#                 self.this_is_first_game_with_current_settings = False


    
#     def best_game(self, sort_by='score', conditions=['1=1']):
#         '''Return the game settings of the best game based on the sorting'''

#         full_condition = ''.join([' AND ' + condition for condition in conditions + self.game_settings_query_condition])

#         query = f"""
#             SELECT 
#                 * 
#             FROM games_summary
#             WHERE 1=1
#                 {full_condition}
#             ORDER BY {sort_by}
#             """

#         df_summary = pd.read_sql_query(query, self.con)   
        
#         # If there hasn't been any game played with the settings, catch the keyerror 
#         try:
#             best_game = df_summary.loc[0, :].to_dict()
#         except KeyError: 
#             best_game = {col: 0 for col in df_summary.columns}

#         return best_game
    

#     def max_mean_score(self, conditions=['1=1']):
#         '''Return max and average metrics'''

#         full_condition = ''.join([' AND ' + condition for condition in conditions + self.game_settings_query_condition])

#         query = f"""
#             SELECT 
#                 game_duration
#                 , sentence_length
#                 , accuracy
#                 , wpm
#                 , score

#             FROM games_summary
#             WHERE 1=1
#                 {full_condition}
#             """

#         df_summary = pd.read_sql_query(query, self.con) 
#         try:
#             df_summary = df_summary.describe().loc[['max', 'mean'], :].T
#         except KeyError: # If first game with those game settings
#             df_summary = pd.DataFrame({'max': [0] * 5, 'mean': [0] * 5}, index=['game_duration', 'sentence_length', 'accuracy', 'wpm', 'score'])

#         return df_summary

    
#     def count_games(self, conditions=['1=1']):
#         '''Counts how many games have been played.
        
#         Parameter
#         ---------
#         conditions list: list of condition to be passed in the query'''

#         full_condition = ''.join([' AND ' + condition for condition in conditions + self.game_settings_query_condition])

#         query = f"""
#             SELECT 
#                 *

#             FROM games_summary
#             WHERE 1=1
#                 {full_condition}
#             """

#         game_count = pd.read_sql_query(query, self.con).shape[0]
#         return game_count


#     def make_condition(self):
#         '''Generate a string containing the current 
#         games settings so that every oher query that 
#         pulls games to compare high score, mean, etc
#         compares the same games
#         '''

#         self.game_settings_query_condition = []
#         for key, value in self.game_settings:
#             if type(value) == str: 
#                 condition = f'{key} == "{value}"'
#             else:
#                 condition = f'{key} == {value}'
                
#             self.game_settings_query_condition.append(condition)


#     def score_game(self, key_pressed=None):
#         '''Takes the list of keyy pressed during the game and calculate 
#         the different metrics like game duration, accuracy, wpm
        
#         Parameter
#         ---------
#         keys_pressed: list of list containing the guess, corrct_key 1/0, epoch and game_id
        
#         '''

#         # Create a df to store and manipulate the data of the game
#         column_names = ['key', 'correct_key', 'time', 'game_id']
#         df = pd.DataFrame(key_pressed, columns=column_names)

#         first_second, last_second = df.iloc[[0, -1], 2]
#         game_duration = round(last_second - first_second) if last_second - first_second > 10 else round(last_second - first_second, 2) # Don't round the seconds unless games of less than 10 second (for development only unless you're putting some lame ass rules)
#         keys_pressed = df.shape[0]
#         keys_to_press = df.query('correct_key == 1').shape[0]
#         accuracy = keys_to_press / keys_pressed
#         wpm = keys_to_press / (game_duration / 60) / 5
#         score = accuracy * wpm * len(self.sentence)



#         if self.this_is_first_game == False:
#             self.game_scores = game_duration, keys_to_press, accuracy, wpm, score

#         else: 
#             score_info_to_print =   f'Game duration:     {game_duration} seconds\n' +\
#                                     f'Chars to type:     {keys_to_press}\n' +\
#                                     f'Chars typed:       {keys_pressed}\n' +\
#                                     f'Typing Accuracy:   {accuracy:.1%}\n' +\
#                                     f'WPM:               {round(wpm)}\n' +\
#                                     f'Score:             {round(score)}\n'
#             print(score_info_to_print)
#             print('Play one more game to see highscores and stats comparison')


#     def compare_game(self):
#         df_summary = self.max_mean_score()

#         if type(df_summary) == dict: 
#             print('Play another game to see the stats')
#             return 

#         df_summary.insert(0, 'game', self.game_scores)
#         max_diff = ((df_summary['game'] - df_summary['max']) / df_summary['max'] * 100)
#         df_summary.insert(2, 'max_diff', max_diff)
#         mean_diff = ((df_summary['game'] - df_summary['mean']) / df_summary['mean'] * 100)
#         df_summary.insert(4, 'mean_diff', mean_diff)
#         df_summary = df_summary.reset_index().T.reset_index().T.replace('index', '')
#         # df_summary =.rename({'max': 'best', 'max_diff': 'best_diff'}, axis=1)
#         # data_col_index = [[''] + list(df_summary.columns)] + [[df_summary.index[index]] + [value for value in row] for index, row in enumerate(data)]

#         print(f'Games count: {self.count_games()}')
#         text_to_print = ''
#         for y, row in enumerate(df_summary.to_numpy().tolist()):
#             for x, value in enumerate(row):
#                 if x == 0 or y == 0: # Columns and rows names
#                     value = value
#                     current_string = get_correct_size_string(value, 20)
                
#                 elif (y != 0 and x in (3, 5)): # _diff cols (variation %)
#                     value = round(value, 2)
#                     current_string = color_int(value, spacing=20, suffix=' %')
                
#                 elif y in (1, 2): # game duration and sentene length
#                     value = int(value)
#                     current_string = get_correct_size_string(int(value), 20)

#                 elif y in (3,4): # Accuracy and wpm
#                     value = round(value, 2)
#                     current_string = get_correct_size_string(round(value, 2), 20)

#                 text_to_print += current_string + '\t'

#             text_to_print += '\n'

#         print(text_to_print)



# # score = Score(game_settings)
# # best_wpm = score.best_game(sort_by='wpm desc')['wpm']































# Content from: src/log_data.py
# import sqlite3
# import pandas as pd

# con = sqlite3.connect("data/main_database.db")

  





# def log_key_pressed(key_pressed):
#     column_names = ['key', 'correct_key', 'time', 'game_id']
#     df_keys = pd.DataFrame(key_pressed, columns=column_names)
#     df_keys.to_sql('keys_pressed', con, if_exists='append', index=False)


# def log_game_settings(game_settings):
#     game_id = game_settings['game_id']
#     del game_settings['game_id']
#     df_game_settings = pd.DataFrame(
#         data=[[game_id, str(game_settings)]], 
#         columns=['game_id', 'game_settings']
#     )
#     df_game_settings.to_sql('games_settings', con, if_exists='append', index=False)





# def clean_games_settings(self, game_id):
#     df = pd.read_sql_query('select distinct * from games_settings', con)
#     df['game_settings'] = df['game_settings'].apply(lambda x: eval(x))
#     df_games_settings = pd.concat(
#         [df[['game_id']], df['game_settings'].apply(lambda x: pd.Series(x))], 
#         axis=1
#     )
#     df_games_settings.drop_duplicates().to_sql('clean_games_settings', con, if_exists='replace', index=False)


# def log_summary_per_game(): 
#     query = f"""
#         select
#             distinct
#             kp.game_id
#             , max(kp.time) maxdatetime_unix
#             , min(kp.time) mindatetime_unix
#             , datetime(max(kp.time), 'unixepoch', 'localtime') as date_time
#             , max(kp.time) - min(kp.time) as game_duration
#             , sum(case when kp.correct_key = 1 then 1 else 0 end) as keys_to_press
#             , count(*) as keys_pressed
#             , round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) as accuracy
#             , sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5 as wpm
#             , length(cgs.sentence) as sentence_length
#             , length(cgs.sentence) * (sum(case when kp.correct_key = 1 then 1 else 0 end) / ((max(kp.time) - min(kp.time)) / 60) / 5) * round(CAST(sum(case when kp.correct_key = 1 then 1 else 0 end) as REAL) / count(*), 3) as score
#             , cgs.sentence
#             , cgs.word_count
#             , coalesce(cgs.max_word_length, 1000) as max_word_length
#             , coalesce(cgs.min_word_length, 0) as min_word_length
#             , coalesce(cgs.capitalized_words_count, 0) as capitalized_words_count
#             , coalesce(cgs.capitalized_letters_count_perc, 0) as capitalized_letters_count_perc
#             , coalesce(cgs.punctuation_word_count_perc, 0) as punctuation_word_count_perc
#             , coalesce(cgs.force_shift, 0) as force_shift
#             , coalesce(cgs.hard_mode, 0) as hard_mode
#             , coalesce(cgs.train_letters, 0) as train_letters
#             , case 
#                 when cgs.train_letters in (null, 0) then 0
#                 else coalesce(cgs.train_letters_easy_mode, 0)
#                 end as train_letters_easy_mode
#             , LOWER(cgs.player_name) as player_name

#         from keys_pressed kp 
#         left join clean_games_settings cgs using(game_id)
#         where 1=1
#         group by 1
#         order by maxdatetime_unix asc
#         """

#     df_high_score = pd.read_sql_query(query, con)
#     df_high_score.to_sql('summary_per_game', con, if_exists='replace', index=False)



# def push_to_gbq(game_id):
#     '''Pushes the data about a specific game to BigQuery. 
#     For how to authenticate, see the Google Cloud doc https://cloud.google.com/bigquery/docs/authentication/
#     '''

#     # df_keys_pressed = pd.read_sql_query(f'select distinct * from keys_pressed', con)
#     # df_clean_games_settings = pd.read_sql_query(f'select distinct * from clean_games_settings', con)
#     df_summary_per_game = pd.read_sql_query(f'select distinct * from summary_per_game where game_id = {game_id}', con)
#     # df_clean_games_settings['capitalized_letters_count_perc'] = df_clean_games_settings['capitalized_letters_count_perc'].astype(str)
#     # print(df_clean_games_settings)
#     # print(pd.read_gbq('select * from pyfasttype.clean_games_settings'))
#     # df_clean_games_settings.to_gbq('pyfasttype.clean_games_settings', if_exists='replace', progress_bar=None)
#     # print('clean_games_settings done')
#     # df_keys_pressed.to_gbq('pyfasttype.keys_pressed', if_exists='replace', progress_bar=None)
#     # print('keys_pressed done')
#     df_summary_per_game.to_gbq('pyfasttype.summary_per_game', if_exists='append', progress_bar=None)
#     print('Data pushed to GBQ')




# # clean_games_settings()
# # log_summary_per_game()


# # # print(pd.read_sql_query('select * from summary_per_game', con).columns)




# # push_to_gbq()

