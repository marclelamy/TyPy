import pandas as pd
import numpy as np
import os
import time 
from src.query import npast_games_words, character_ranking


class Sentence(): 
    def __init__(self, game_config, first_game, con): 
        # self.game_config = game_config
        self.cwd = os.getcwd()
        self.game_config = game_config
        self.first_game = first_game
        self.con = con
        # self.word_list = self.load_words(self.game_config['difficulty'])
        # if self.game_config['train'] == False: 
        #     self.word_list = self.word_list[:self.game_config['word_count']]
        # else: 
        #     # self.word_list = self.get_n_slowest_words(self.word_list)
        #     self.word_list = self.only_one_letter(self.word_list)


        # # print(f'word_list: {self.word_list}')
        # self.capitalize_word_list(self.game_config['capitalized_words'], self.game_config['capitalized_letters'])
        # # print(f'cap: {self.word_list}')
        # self.add_punctuation(self.game_config['punctuation'], self.game_config['punctuation_char'])
        # # print(f'punc: {self.word_list}')
        # self.sentence = ' '.join(self.word_list)
        # # self.sentence = '''--=qwertyuiop[]asdfghjkl;'zxcvbnm,./"'''
        # # print(f'sentence: {self.sentence}')



    def generate_sentence(self): 
        '''Creates a sentence based on the game_config
        '''

        self.word_list = self.load_words(self.game_config['difficulty'])
        
        # Remove banned words
        ngames_past_words = npast_games_words(self.con, self.game_config['n_games_banned_words'])


        # Getting worst characters 
        
        
        
        # Remove words that are too long or too short or in the ngames_past_words
        for word in self.word_list: 
            if word in ngames_past_words or len(word) > self.game_config['word_length_max'] or len(word) < self.game_config['word_length_min']:
                self.word_list.remove(word)


        # Training mode
        if self.game_config['train'] == True: 
            df_character_ranking = character_ranking(self.con)
            if self.game_config['train_letter_type'] == 'lower_case_letters':
                df = pd.DataFrame(self.word_list, columns=['word'])
                letter_in_focus = df_character_ranking.query(f'type == "{self.game_config["train_letter_type"]}"').iloc[0, 0]
                self.game_config['character_in_focus'] = letter_in_focus

                df_character_ranking = character_ranking(self.con)
                time_per_char = dict(df_character_ranking[['key', 'avg_time_diff']].values)
                df['letter_count'] = df['word'].str.count(letter_in_focus)
                df['total_potential_time'] = df['word'].apply(lambda x: sum([time_per_char[letter] for letter in list(x) if letter != letter_in_focus]))
                df['total_potential_time_per_letter'] = df['total_potential_time'] / df['word'].str.len()
                df = df.sort_values(by=['letter_count', 'total_potential_time_per_letter'], ascending=False).reset_index(drop=True)
                self.word_list = df['word'].tolist()

            print(df_character_ranking.query(f'type == "{self.game_config["train_letter_type"]}"').head(5))
            time.sleep(20)

        # Capitalizing and adding punctuation
        # This comes at the end because it need the full list of words after filtering 
        np.random.shuffle(self.word_list)
        self.sentence = ' '.join(self.word_list[:self.game_config['word_count']])
        return self.sentence
        




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
        
        return all_words




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
        print(f'punctuation: {punctuation_char}')
        punctuation_count = punctuation if punctuation > 1 else int(len(self.word_list) * punctuation)

        common_punctuations = list('''12345678900--=qwertyuiop[]\asdfghjkl;'zxcvbnm,./!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?"''')
        # common_punctuations = ['()', '{}', '[]', '!', "''", '*', ',', '.', ';', ':', '-', '_', ]
        # common_punctuations = ['()', '!', "''", '*', ',', '.', ';', ':', '-', '_', '<', '>', '/', '?', '=']
        # common_punctuations = [',', '.', '-', '!', "''", '()']
        double_char = [punc for punc in common_punctuations if len(punc) > 1]

        # Limiting characters to use 
        if isinstance(punctuation_char, int) or isinstance(punctuation_char, float):
            np.random.shuffle(common_punctuations)
            common_punctuations = common_punctuations[:punctuation_char]
        elif isinstance(punctuation_char, str):
            common_punctuations = [punctuation_char]

        for index in range(punctuation_count):
            word = self.word_list[index]
            rdm_punctuation = np.random.choice(common_punctuations)
            if len(rdm_punctuation) > 1: 
                word = rdm_punctuation[0] + word + rdm_punctuation[1]
            else: 
                word = rdm_punctuation + word + rdm_punctuation
            
            self.word_list[index] = word

        np.random.shuffle(self.word_list)


    


    def only_one_letter(self, word_list): 
        max_key_count_to_use = 200
        min_key_count_to_use = 1


        query = f''' 
        with time_per_key as (
        select 
            key
            , time
            , lead(time) over(partition by game_id order by time desc) lead_time
            , time - lead(time) over(partition by game_id order by time desc) time_diff
            --, lead(key) over(order by time desc) lead_key
            --, lead(time) over(order by time desc) lead_time
            , row_number() over(partition by key order by time desc) letter_descending_rank 

        from keys_pressed
        left join clean_games_settings using(game_id)
        where 1=1 
            --and word_count > 20
            and correct_key = 1

        order by time 
        )


        select 
            key 
            , avg(time_diff) avg_time_diff
            , count(*) count
            , max(letter_descending_rank) 

        from time_per_key
        where 1=1
            and letter_descending_rank <= {max_key_count_to_use}
            and letter_descending_rank >= {min_key_count_to_use}

        group by key 
        order by avg_time_diff desc
        '''

        letters = list('qwertyuiopasdfghjklzxcvbnm')
        allowed_characters = list('''qwertyuiop[]asdfghjkl;'zxcvbnm,./-=''')
        df = pd.read_sql_query(query, self.con).sort_values ('time_diff', ascending=self.game_config['train_easy']).query('key in @allowed_characters')

        # If training and punctuation are set, keep only punctuation else keep only letters
        print(df.head(50))
        # import time
        # time.sleep(10)
        if self.game_config['punctuation'] > 0: 
            df = df.query('key not in @letters')
        else:
            df = df.query('key in @letters')
        letter = df.iloc[0, 0]
        self.game_config['character_in_focus'] = letter
        if letter.isalpha() == False: 
            self.game_config['punctuation_char'] = letter
            word_list = word_list[:self.game_config['word_count']]

        else: 
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