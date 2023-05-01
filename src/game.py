import src.detect_keys as dk
from src.query import query_table
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
try: os.remove(f'{cwd}/data/main_database.db')
except: pass



def update_terminal(): 
    os.system('cls' if os.name == 'nt' else 'clear')


class Game(): 
    def __init__(self): 
        self.game_id = np.random.randint(10**10)
        self.window_width, self.window_height = shutil.get_terminal_size()
        self.create_or_load_database()
        self.available_configs = [file.replace('.toml', '') for file in os.listdir('configs/')]
        print('\n'*20)
        self.main_menu()



    # @staticmethod
    def read_config(self, config='game_default') -> dict: 
        '''Given a config file name, reads it and return a dictionary
        with the game settings.'''
        with open(f'configs/{config}.toml', 'r') as f:
            config = toml.load(f)

        return self.clean_config(config)


    def clean_config(self, config):
        '''Clean the config to make sure that the game can be played
        '''
        # Adding rules if not in the config file
        with open(f'configs/game_default.toml', 'r') as f:
            default_config = toml.load(f)        
        for key, value in default_config.items(): 
            if key not in config.keys(): 
                config[key] = value 

        return config


    def conf(self, config): 
        game_config = config['game_config']
        if game_config['train'] == True: 
            if game_config['word_length_min'] < 5: 
                game_config['word_length_min'] = 5

        config['game_config'] = game_config
        return config


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



    def confirm_game_settings_before_game(self): 
        '''Sets the config for the game before launching it.
        '''

        # Reads, sets and print default game confi
        if 'user_default' in self.available_configs:
            config = self.read_config('user_default')
        else:
            config = self.read_config('game_default')
        self.game_config = config['game_config']
        self.game_preference = config['game_preference']

        print(self.game_config, self.game_preference)

        self.print_game_config()

        # Choose action
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


    def print_game_config(self, extensive=False): 
        print("\n\n\nCurrent game settings: \n\n")
        game_config_tabulate_basic = [[rule.capitalize().replace('_', ' '), value] for rule, value in self.game_config.items()]
        print(tabulate(game_config_tabulate_basic, headers=['Rule', 'Value'], showindex=True))


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

            if self.game_preference['display_wpm'] == True:
                infos_to_print += f'WPM: {wpm_formatted}\n'

            # print('\n' * self.window_height)
            if self.game_preference['display_chart'] == True:
                self.generate_chart(self.wpm_list)
        else: 
            self.wpm_list = []

        if self.game_preference['display_words_left'] == True:
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
        self.print_game_config()
        print('Play game', '\n' * self.window_height)

        # Create sentence and score
        self.score = Score( 
            self.game_config,
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
            self.game_config, 
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
        game_data = self.game_config
        game_data.update(
            {'sentence': sentence,
             'keys_pressed': keys_pressed,
             'game_id': self.game_id}
        )
        self.score.log_game(game_data)

        self.score.summarize_games_scores(self.con)
        if self.first_game == False:
            self.compare_game()
        else:
            df_game_summary = self.score.load_game_stats(self.game_id)
            print('Game summary:')
            print(tabulate(df_game_summary.T))
         
        # Propose to save on gbg, back to main menu, leaderboard
        

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



