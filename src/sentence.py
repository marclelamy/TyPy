import numpy as np




class Sentence(): 
    def __init__(self, game_config, cwd): 
        self.game_config = game_config
        self.cwd = cwd

        for rule, value in self.game_config.items(): 
            setattr(self, rule, value)

        self.load_words()
        self.filter_word_length()
        self.sentence = ' '.join(self.word_list)



    def load_words(self) -> list:
        '''Opens one of three lists of words depending on the difficulty. 
        common_words.txt contains 3000 common word
        hard_words.txt contains 370k words words generally longer and harder 
        to type compared to the common word 
        google_most_used_words is the top 10k on Google
        '''

        if self.difficulty.lower() == 'hard':
            file_path = f'{self.cwd}/data/text/hard_words.txt'
        elif self.difficulty.lower() == 'easy':
            file_path = f'{self.cwd}/data/text/google_most_used_words.txt'
        elif self.difficulty.lower() == 'medium':
            file_path = f'{self.cwd}/data/text/common_words.txt'
            
        with open(file_path) as file: 
            all_words = file.read().split('\n')

        # Removing non letters characters and words g/l than max/min length
        lowered_words = [''.join([char for char in word if char.isalpha()]).lower() for word in all_words]
        np.random.shuffle(lowered_words)
        self.word_list = lowered_words[:self.word_count]
        # print(time.time() - a)


    def filter_word_length(self): 
        self.word_list = [word for word in self.word_list if self.word_length_max == None or self.word_length_min <= len(word) <= self.word_length_max]




