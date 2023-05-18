import pandas as pd
import numpy as np
import os
from src.query import npast_games_words


class Sentence(): 
    def __init__(self, game_config, first_game, con): 
        # self.game_config = game_config
        self.cwd = os.getcwd()
        self.game_config = game_config
        self.first_game = first_game
        self.con = con
        self.word_list = self.load_words(self.game_config['difficulty'])
        if self.game_config['train'] == False: 
            self.word_list = self.word_list[:self.game_config['word_count']]
        else: 
            # self.word_list = self.get_n_slowest_words(self.word_list)
            self.word_list = self.only_one_letter(self.word_list)


        # print(f'word_list: {self.word_list}')
        self.capitalize_word_list(self.game_config['capitalized_words'], self.game_config['capitalized_letters'])
        # print(f'cap: {self.word_list}')
        self.add_punctuation(self.game_config['punctuation'], self.game_config['punctuation_char'])
        # print(f'punc: {self.word_list}')
        self.sentence = ' '.join(self.word_list)
        # self.sentence = '''--=qwertyuiop[]asdfghjkl;'zxcvbnm,./"'''
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
                banned_words = npast_games_words(self.con, self.game_config['n_games_banned_words'], len(all_words))
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
            --and word_count > 20
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
        letters = list('qwertyuiopasdfghjklzxcvbnm')
        allowed_characters = list('''qwertyuiop[]asdfghjkl;'zxcvbnm,./-=''')
        df = pd.read_sql_query(new_query, self.con).sort_values('time_diff', ascending=self.game_config['train_easy']).query('key in @allowed_characters')

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