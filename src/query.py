import pandas as pd
import os



class Query(): 
    def __init__(self, con) -> None:
        self.con = con
        self.cwd = os.getcwd()


    def npast_games_words(self, n_past_games):
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

        df_query = pd.read_sql_query(query_npast_games_words, self.con)
        done_words = ' '.join(df_query['sentence'].unique()).split(' ')
        return done_words



    def load_query (self, query_name: str, text_only: bool = False) -> list:
        '''Opens a given text file name and execute the 
        query to return a pd.DataFrame
        
        Parameter
        ---------
        query_name str: name of the file name to run
        '''

        # Open file and get the query 
        with open(f'{self.cwd}/data/queries/{query_name}.sql') as file: 
            query = file.read()

        if text_only == False:
            return pd.read_sql_query(query, self.con)
        elif text_only == True:
            return query



