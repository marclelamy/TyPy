import pandas as pd
import numpy as np
import os
import nltk
import time 
from src.query import npast_games_words, character_ranking
from tabulate import tabulate
import re

class Sentence(): 
    def __init__(self, game_config, first_game, con): 
        self.cwd = os.getcwd()
        self.game_config = game_config
        self.first_game = first_game
        self.con = con

    def get_random_word(self):
        # Load a local dictionary file
        nltk.download('words')
        words = nltk.corpus.words.words()
        
        # Get a random word
        random_word = np.random.choice(words)
        return random_word

    def get_word_definitions(self, word):
        # Use nltk to look up word definitions
        definitions = nltk.corpus.wordnet.synsets(word)
        if definitions:
            # Retrieve the definitions if available
            definitions = [definition.definition() for definition in definitions]
            return '. '.join(definitions)
        else:
            return None

    def generate_sentence(self): 
        '''Creates a sentence based on the game_config
        '''
        if self.game_config['random_definition'] == True:
            while True: 
                word = self.get_random_word()
                definitions = self.get_word_definitions(word)
                if definitions:
                    sentence = word + ': ' + definitions + ' - ' + word
                    break
            self.sentence = '. '.join(map(lambda s: s.strip().capitalize(), sentence.split('.')))
            return self.sentence

        self.word_list = self.load_words(self.game_config['difficulty'])
        
        # Remove banned words
        ngames_past_words = npast_games_words(self.con, self.game_config['n_games_banned_words'])
        print(f'ngames_past_words: {ngames_past_words}')



        # Getting worst characters lower_case_letter
        

        # Remove words that are too long or too short or in the ngames_past_words
        self.word_list = [word for word in self.word_list if word not in ngames_past_words \
                                                            and len(word) <= self.game_config['word_length_max'] \
                                                            and len(word) >= self.game_config['word_length_min']]


        # Training mode
        if self.game_config['train'] == True: 
            df_character_ranking = character_ranking(self.con, 
                                                     max_key_count_to_use=self.game_config['max_key_count_to_use'],
                                                     min_key_count_to_use=self.game_config['min_key_count_to_use'])
            df_character_ranking = df_character_ranking.sort_values('avg_time_diff', ascending=self.game_config['train_easy'])
            df_character_ranking = df_character_ranking.query(f'type == "{self.game_config["train_letter_type"]}"')
            print(tabulate(df_character_ranking))
            
            # Set Character in focus 
            character_in_focus = df_character_ranking.query(f'type == "{self.game_config["train_letter_type"]}"').iloc[0:self.game_config['train_n_letters'], 0]
            character_in_focus = ''.join(character_in_focus)
            self.game_config['character_in_focus'] = character_in_focus

            # Calculate the weight of each char and the letter_count / letter_score
            time_per_char = {key: len(character_in_focus) - rank for rank, key in enumerate(character_in_focus)}
            print(time_per_char)
            character_in_focus_weights = {char: time_per_char[char] / sum(time_per_char.values()) for char in character_in_focus}
            print(character_in_focus_weights)
            df = pd.DataFrame(self.word_list, columns=['word'])
            df['letter_score'] = df['word'].apply(lambda word: sum([word.count(char) * character_in_focus_weights[char] for char in character_in_focus]))


            if self.game_config['train_rank_non_character_in_focus']: 
                df['total_potential_time'] = df['word'].apply(lambda x: sum([time_per_char[letter] for letter in list(x) if letter not in character_in_focus]))
                df['total_potential_time_per_letter'] = df['total_potential_time'] / df['word'].str.len()
                df = df.sort_values(by=['letter_score', 'total_potential_time_per_letter'], ascending=self.game_config['train_easy']).reset_index(drop=True)
            else:
                df = df.sort_values(by=['letter_score'], ascending=self.game_config['train_easy']).reset_index(drop=True)
            
            print(tabulate(df.head(50)))
            time.sleep(100)
            self.word_list = df['word'].tolist()

        elif self.game_config['mode'] == 'campaign': 
            letter = pd.read_sql_query('select * from campaing_letters where validated = False limit 1', self.con)['letter'].values[0]
            self.game_config['character_in_focus'] = letter

            # df_character_ranking = character_ranking(self.con,
            #                                             max_key_count_to_use=None,
            #                                             min_key_count_to_use=None,
            #                                             condition1='',
            #                                             condition2='',
            #                                             order='desc')
            # time_per_char = dict(df_character_ranking[['key', 'avg_time_diff']].values)
            # # Get the keys and probabilities as separate lists
            # total_value = sum(time_per_char.values())
            # probabilities = {key: value / total_value for key, value in time_per_char.items()}
            # #random pick and remove words
            # random_pick = np.random.choice(list(probabilities.keys()), p=list(probabilities.values()))        
            # print(self.word_list)
            self.word_list = [word for word in self.word_list if len(word) > 4 and letter in word]

        if 'character_in_focus' not in self.game_config.keys(): 
            self.game_config['character_in_focus'] = None
        # Capitalizing and adding punctuation
        # This comes at the end because it need the full list of words after filtering 
        self.word_list = self.word_list[:self.game_config['word_count']]
        print(f'word_list: {self.word_list}')

        self.word_list = self.capitalize_word_list(self.game_config['capitalized_words'], self.game_config['capitalized_letters'])
        print(f'word_list: {self.word_list}')

        self.word_list = self.add_punctuation(self.game_config['punctuation'], self.game_config['punctuation_char'])
        print(f'word_list: {self.word_list}')

        np.random.shuffle(self.word_list)
        self.sentence = ' '.join(self.word_list)
        # self.sentence = 'pizzazz zyzzyvas pizazzes razzmatazz zizzling benzalphenylhydrazone zyzzyva bezazzes hydroxyazobenzene bezazz benzeneazobenzene zizzled zizzles zizzle zigzagways buzzwords zigzaggedness benzdioxdiazine puzzleheadedness piezocrystallization pizazz zyzzogeton pizzazzes zigzaggedly zizz'
        print(f'sentence: {self.sentence}')
        # time.sleep(100)
        return self.sentence
        



    def load_words(self, difficulty) -> list:
        '''Opens one of three lists of words depending on the difficulty. 
        common_words.txt contains 3000 common word
        hard_words.txt contains 370k words words generally longer and harder 
        to type compared to the common word 
        google_most_used_words is the top 10k on Google
        '''
        file_paths = []
        if 'hard' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/hard_words.txt']
        if 'easy' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/common_words.txt']
        if 'medium' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/google_most_used_words.txt']
        if 'w1000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_1000.txt']
        if 'w2000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_2000.txt']
        if 'w5000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_5000.txt']
        if 'w10000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_10000.txt']
        if 'w20000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_20000.txt']
        if 'w50000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_50000.txt']
        if 'w100000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_100000.txt']
        if 'w200000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_200000.txt']
        if 'w500000' in difficulty.lower():
            file_paths += [f'{self.cwd}/data/text/wikipedia_500000.txt']
        if difficulty.lower() in 'nltk_corpus_words_250k': 
            file_paths += [f'{self.cwd}/data/text/nltk_corpus_words_250k.txt']
        
        word_list = []
        for file_path in file_paths:
            with open(file_path, 'r') as file: 
                word_list += file.read().split('\n')
        word_list = list(set(word_list))
        np.random.shuffle(word_list)
        return word_list




    def capitalize_word_list(self, capitalized_words, capitalized_letters): 
        words_to_cap = capitalized_words if capitalized_words > 1 else int(len(self.word_list) * capitalized_words)

        for index, word in enumerate(self.word_list[:words_to_cap]): 
            if capitalized_letters.lower() == "first":
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
        return self.word_list


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
        return self.word_list

    


