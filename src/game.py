import detect_keys as dk
import time
import sqlite3
import toml
import os
from tabulate import tabulate
import numpy as np
from sentence import Sentence
from termcolor import colored
import re


class Game(): 
    def __init__(self): 

        print('\n'*20)
        # self.game_settings = self.set_game_settings(config, kwargs)
        self.con = sqlite3.connect("data/main_database.db")
        self.available_config = [file.replace('.toml', '') for file in os.listdir('configs/')]
        self.game_id = np.random.randint(10**10)
        self.cwd = os.getcwd()
        self.main_menu()



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
        if 'user_default' in self.available_config:
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
        
        
# I both need to propose a quick option with the index and new value and a menu with full table, range and everything
    def quick_change_game_config(self): 
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


    def check_input_format(input_str):
        pattern = "^q (\w+) (\w+),(\w+) (\w+)"
        print(input_str)
        match = re.match(pattern, input_str)
        print('input check', input_str, match)


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

        sentence = Sentence(self.game_config,
                            self.cwd)


        print(sentence.sentence)





    def propose_menu(self, question: list, choices: list, wait_enter=False) -> int:
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