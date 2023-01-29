import detect_keys as dk
import time
import sqlite3





class Game(): 
    def __init__(self, 
                 config='default',
                 **kwargs): 

        print('\n'*20)
        # self.game_settings = self.set_game_settings(config, kwargs)
        self.con = sqlite3.connect("data/main_database.db")
        self.main_menu()



    def main_menu(self): 
        '''Menu the player sees when playing the game'''
        print('Welcome to pyFastType!\n')
        print('Please dont use your mouse but only keyboard keys when prompt too to keep the window active or it wont detect your key presses afterwards.\nHave fun!\n\n')
        choice = self.propose_menu(question = 'Press the letter on the left to navigate through the menu:',
                                   choices = ['Play game', 'Leaderboard', 'Settings'])


        {0: self.confirm_game_settings_before_game(),
         1: self.settings(),
         2: self.leaderboard()}[choice]





    def confirm_game_settings_before_game(self): 
        # Call game settings and print 
        print('\n'*20)
        print("Here's the game settings: \n\nDo you wanna change the settings?\n\tY - Yes pls daddy\n\tN - No\n")
        key = dk.next_key_pressed()[0].lower()

        if key == 'y': 
            self.set_settings()
        elif key == 'n':
            self.play_game()






    def settings(self): 
        print('Play game function')





    def leaderboard(self):
        print('Leaderboard')





    def play_game(self): 
        print('Play game')





    def propose_menu(self, question: list, choices: list) -> int:
        '''Print a new menu with question/answers with key pressed
        
        parameters 
        ----------
        question str: question to ask to the player
        choices list: list of choices fo the user to answer 
        
        returns
        ----------
        Index of the list corresponding to the choice of the user
        '''

        print(question.capitalize())
        choices_first_letter = []
        for choice in choices: 
            print(f'\t{choice[0].upper()} - {choice}')
            choices_first_letter.append(choice[0].lower())

        key = dk.next_key_pressed()[0].lower()
        return choices_first_letter.index(key)


Game()




# def main():
#     print('Welcome to the game, choose a menu (type the letter on the left):\n\tP - Play game\n\tS - Settings\n')    
#     key = dk.next_key_pressed()[0]


#     if key == 'p': 
#         play_game()
#     elif key == 'S':
#         settings()
    
















# main()