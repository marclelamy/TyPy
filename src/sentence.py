




class Sentence(): 
    def __init__(self, game_config, cwd): 
        self.game_config = game_config
        self.cwd = cwd

        for rule, value in self.game_config.items(): 
            print(f'|{rule}| - |{value}|')
            setattr(self, rule, value)

        print(self.game_config)
        print(self.hard_mode)

        self.load_words()
        self.filter_word_length()
        self.sentence = ' '.join(self.word_list)



    def load_words(self) -> list:
        '''Opens one of three lists of words depending on the difficulty. 
        common_words.txt contains 3000 common word
        hard_words.txt contains 370k words words generally longer and harder 
        to type compared to the common word 
        google_most_used_words is the top 10k on Googe
        '''

        if self.hard_mode.lower() == 'hard':
            file_path = f'{self.cwd}/data/text/hard_words.txt'
        elif self.hard_mode.lower() == 'easy':
            file_path = f'{self.cwd}/data/text/google_most_used_words.txt'
        elif self.hard_mode.lower() == 'medium':
            file_path = f'{self.cwd}/data/text/common_words.txt'
            
        with open(file_path) as file: 
            all_words = file.read().split('\n')

        # Removing non letters characters and words g/l than max/min length
        # a = time.time()
        lowered_words = [''.join([char for char in word if char.isalpha()]).lower() for word in all_words]
        self.word_list = lowered_words
        # print(time.time() - a)


    def filter_word_length(self): 
        self.word_list = [word for word in self.word_list if self.word_length_max == None or self.word_length_min <= len(word) <= self.word_length_max]




    def capitalize_random(sentence: list) -> list:
        '''Given a list of words, capitalized_words_count and 
        capitalized_letters_count_perc (terrible naming I know), 
        capitalizes some letters.
        
        parameters
        ----------
        sentence list: list of words
        '''
        sentence_length = len(sentence)

        # print(capitalized_words_count)
        # capitalized_words_count = capitalized_words_count if capitalized_words_count <= sentence_length else sentence_length

        # setting the numbers of words to capitalize depending on int/float capitalized_words_count
        if  0 < capitalized_words_count <= 1:
            print(capitalized_words_count = 200)
            capitalized_words_sentence_count = round(len(sentence) * capitalized_words_count)
        elif type(capitalized_words_count) == int: 
            capitalized_words_sentence_count = capitalized_words_count

        # Looping through count of words to capitalize
        for index in range(capitalized_words_sentence_count):
            current_word = sentence[index]

            if type(capitalized_letters_count_perc) in [int, float]:
                if 0 < capitalized_letters_count_perc <= 1: 
                    capitalized_letters_sentence_count_perc = round(len(current_word) * capitalized_letters_count_perc)

                # Generate a list of n numbers, suffle it and keep the indexes >= to the number of letters to cap
                random_list = list(range(len(current_word)))
                np.random.shuffle(random_list)
                random_list = random_list[:capitalized_letters_sentence_count_perc]
                sentence[index] = ''.join([char.upper() if index_char in random_list else char for index_char, char in enumerate(current_word)])

            elif capitalized_letters_count_perc == 'first':
                sentence[index] = current_word.title()

        np.random.shuffle(sentence)


        return sentence
