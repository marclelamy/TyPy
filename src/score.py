import pandas as pd
import sqlite3 

con = sqlite3.connect('main_database.db ')


class Score():
    def __init__(self, game_settings): 
        self.game = self.best_game()
        self.game_settings = game_settings
        
        for key, value in game_settings.items():
            exec(f'self.{key} = {value}')
    
    
    def best_game(self, sort_by='score', conditions=['1=1']):
        '''Return the game settings of the best game based on the '''
        full_condition = ''.join([' AND ' + condition for condition in conditions])

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



    # def set_game_settings(self, game_settings):
        # for key, value in game_settings.items():
        #     exec(f'self.{key} = {value}')


