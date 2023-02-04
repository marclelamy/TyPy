import numpy as np




class Sentence(): 
    def __init__(self, game_config, cwd): 
        # self.game_config = game_config
        self.cwd = cwd
        print(game_config)
        # for rule, value in self.game_config.items(): 
        #     setattr(self, rule, value)

        self.load_words(game_config['difficulty'], game_config['word_count'])
        self.filter_word_length(game_config['word_length_min'], game_config['word_length_max'])
        self.capitalize_word_list(game_config['capitalized_words'], game_config['capitalized_letters'])
        self.add_punctuation(game_config['punctuation'], game_config['punctuation_char'])
        self.sentence = ' '.join(self.word_list)



    def load_words(self, difficulty, word_count) -> list:
        '''Opens one of three lists of words depending on the difficulty. 
        common_words.txt contains 3000 common word
        hard_words.txt contains 370k words words generally longer and harder 
        to type compared to the common word 
        google_most_used_words is the top 10k on Google
        '''

        if difficulty.lower() == 'hard':
            file_path = f'{self.cwd}/data/text/hard_words.txt'
        elif difficulty.lower() == 'easy':
            file_path = f'{self.cwd}/data/text/google_most_used_words.txt'
        elif difficulty.lower() == 'medium':
            file_path = f'{self.cwd}/data/text/common_words.txt'
            
        with open(file_path) as file: 
            all_words = file.read().split('\n')

        # Removing non letters characters and words g/l than max/min length
        lowered_words = [''.join([char for char in word if char.isalpha()]).lower() for word in all_words]
        np.random.shuffle(lowered_words)
        self.word_list = lowered_words[:word_count]
        # print(time.time() - a)


    def filter_word_length(self, word_length_min, word_length_max): 
        self.word_list = [word for word in self.word_list if word_length_min <= len(word) <= word_length_max]



    def capitalize_word_list(self, capitalized_words, capitalized_letters): 
        words_to_cap = capitalized_words if capitalized_words > 1 else int(len(self.word_list) * capitalized_words)

        for index, word in enumerate(self.word_list[:words_to_cap]): 
            # Generate a list of n numbers, suffle it and keep the indexes >= to the number of letters to cap
            random_list = list(range(len(word)))
            np.random.shuffle(random_list)
            letters_to_cap = capitalized_letters if capitalized_letters > 1 else round(len(word) * capitalized_letters)
            print(words_to_cap, letters_to_cap, len(word) * capitalized_letters)
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