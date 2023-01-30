import detect_keys as dk
import time
import sqlite3
import toml
import os
from tabulate import tabulate
import numpy as np
from sentence import Sentence
from score import Score
from termcolor import colored
import re


class Game(): 
    def __init__(self): 
        self.game_id = np.random.randint(10**10)
        self.create_db_if_doesnt_exists()
        self.available_configs = [file.replace('.toml', '') for file in os.listdir('configs/')]
        self.cwd = os.getcwd()
        self.main_menu()


    # def check_if_first_game(self): 
    #     '''Check if a 
    #     '''

    #     if os.path.exists('data/main_database.db'): 
    #         self.con = sqlite3.connect('data/main_database.db')
    #     else: 
    #         self.create_db()

    def create_db_if_doesnt_exists(self): 
        '''Create the two tables of the database
        '''
        self.con = sqlite3.connect('data/main_database.db')

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
        


    def main_menu(self): 
        '''Menu players see when playing the game.
        '''
        print('Welcome to pyFastType!\n')
        print('Please dont use your mouse but only keyboard keys when prompt too to keep the window active or it wont detect your key presses afterwards.\nHave fun!\n\n')
        choice = self.propose_menu(question = 'Press the letter on the left to navigate through the menu:',
                                   choices = ['Play game', 'Leaderboard', 'Settings'])

        {
            0: self.confirm_game_settings_before_game,
            1: self.global_preference,
            2: self.leaderboard
        }[choice]()

# from teh tabular, choose the row index to directly modify the rules



    def confirm_game_settings_before_game(self): 
        '''Sets the config for the game before launching it.
        '''
        print('\n'*20)

        # Reads, sets and print default game confi
        if 'user_default' in self.available_configs:
            self.game_config = self.read_config('user_default')['game_config']
        else:
            self.game_config = self.read_config('game_default')['game_config']
        self.print_game_config()

        # Choose action
        choice = self.propose_menu(question = 'Do you wanna change Any?',
                                   choices = ['yes', 'no, play the game', f'Quick change'])

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
        print('Change rule')


    def print_game_config(self, extensive=False): 
        print("\n\n\nCurrent game settings: \n\n")
        game_config_tabulate_basic = [[rule.capitalize().replace('_', ' '), value] for rule, value in self.game_config.items()]
        print(tabulate(game_config_tabulate_basic, headers=['Rule', 'Value'], showindex=True))

        



    def change_game_config(self):
        print('change game config')


    def global_preference(self): 
        print('Play game function')





    def leaderboard(self):
        print('Leaderboard')





    def start_game(self): 
        self.print_game_config()
        print('Play game')

        # Create sentence
        sentence = Sentence(self.game_config, self.cwd).sentence

        score = Score(self.con)
        # self.best_score = Score().best_scores(self.config) # best game for each of the rules or only for one? i think the best score for each of the rules. This function in Score() could calculate for each of the rules the best, avg (describe() type) and would return what would be in the dictionary/parameters of the function
        keys_pressed = []
        sentence_to_display = sentence
        for index, letter_to_type in enumerate(sentence):
            if letter_to_type == ' ': 
                letter_to_type = 'space'

            
            # Show infos 
            # Find how to call the ui video games 
            self.show_infos(
                sentence_to_display,

            )


            # Check guess 
            while True: 
                guess, shift_pressed = dk.next_key_pressed()
                correct_key = guess == letter_to_type


                # check fo shift 
                # if self.force_shift == True and 


                if correct_key: 
                    keys_pressed.append([str(guess), correct_key, shift_pressed, time.time(), self.game_id]) 
                    sentence_to_display = sentence_to_display[1:]
                    break
                else:
                    keys_pressed.append([str(guess), correct_key, shift_pressed, time.time(), self.game_id]) 

        

        # Log game
        game_data = self.game_config
        game_data.update(
            {'sentence': sentence,
             'keys_pressed': keys_pressed,
             'game_id': self.game_id}
        )
        score.log_game(game_data)









    def show_infos(self, display_sentence): 
        '''What to print during the game
        '''
        infos_to_print = ''

        print(' '.join(display_sentence.split(' ')[:5]), end='\r')






    def propose_menu(self, question: list, choices: list, nwait_enter=False) -> int:
        '''Print a new menu with question/answers with key pressed
        
        parameters 
        ----------
        question str: question to ask to the player
        choices list: list of choices fo the user to answer 
        
        returns
        ----------
        Index of the list corresponding to the choice of the user
        '''

        print('\n')
        print(question.capitalize())
        choices_first_letter = []
        for choice in choices: 
            print(f'\t{choice[0].upper()} - {choice.capitalize()}')
            choices_first_letter.append(choice[0].lower())
        print('\n')

        key = dk.next_key_pressed()[0].lower()

        if key not in choices_first_letter: 
            print('Wrong letter, press again.')
            self.propose_menu(question, choices)
        else:
            return choices_first_letter.index(key)






    @staticmethod
    def read_config(config='game_config') -> dict: 
        '''Given a config file name, reads it and return a dictionary
        with the game settings.'''
        with open(f'configs/{config}.toml', 'r') as f:
            config = toml.load(f)
        return config
        


    # def global_game



Game()




# def main():
#     print('Welcome to the game, choose a menu (type the letter on the left):\n\tP - Play game\n\tS - Settings\n')    
#     key = dk.next_key_pressed()[0]


#     if key == 'p': 
#         start_game()
#     elif key == 'S':
#         settings()
    
















# main()