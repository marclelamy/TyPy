# import sqlite3
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.io as pio
# from src.score import Score
# import os 
# import toml
# from tabulate import tabulate
# from tqdm import tqdm
# import re 
# from tqdm.contrib.concurrent import process_map
# # Import
# from pandarallel import pandarallel

# # Initialization
# pandarallel.initialize(progress_bar=True, nb_workers=8)

# current_dir = os.getcwd()
# con = sqlite3.connect("data/main_database.db")
# # pd.set_option('display.float_format', lambda x: '%.3f' % x)
# pd.set_option('display.max_columns', None)
# connew = sqlite3.connect("data/text/wiki/wikipedia2.sqlite")


# df = pd.read_sql_query('select * from clean_article', connew)
# print(df.shape)






# # df.groupby(args).apply(func)
# # for i in tqdm(range(406, 1000)):
# def doit(df):
#     valcount = df.str.split(' ').explode().value_counts().to_frame().reset_index()
#     valcount.to_sql('valcount', connew, if_exists='append', index=False)
# # print(dsahofhsad)


# # if __name__ == '__main__':

#     # lst = df.loc[:len(df) // 1, 'clean_article'].to_list()
#     # lst = ' '.join(lst).split(' ')
#     # print(len(lst))
# data = [df.loc[len(df) // 1000 * i:len(df) // 1000 * (i+1), 'clean_article'] for i in range(1000)]
# print(f'len(data): {len(data)}')
# # process_map(doit, data, max_workers=2)
# for df in tqdm(data):
#     doit(df)
# print('process_map done')
# df = pd.read_sql_query('select * from valcount', connew)
# print(df.shape)
# df = df.groupby('index').sum().sort_values('clean_article', ascending=False)
# print(df.shape)
# df.to_sql('valcount', connew, if_exists='replace', index=True)

# print('done')
# print(askldjf)

from tqdm.contrib.concurrent import process_map
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import numpy as np
import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import os
import shutil
import random
import nltk
import time
import math
from collections import Counter
from tabulate import tabulate
import re


# os.remove('data/text/wiki/wikipedia2.sqlite')
# con = sqlite3.connect('data/text/wiki/wikipedia2.sqlite')
con = sqlite3.connect("data/main_database.sqlite")

def get_wikipedia_page_content(url):
    # Send a GET request to the Wikipedia page
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful

    # Create a BeautifulSoup object with the page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main content area of the Wikipedia page
    content_div = soup.find(id='mw-content-text')

    # Extract all the text within the main content area
    text = content_div.get_text().strip()

    # Find all the links within the main content area
    links = [a['href'] for a in content_div.find_all('a', href=True)]
    links = ['https://en.wikipedia.org' + link for link in links if link.startswith('/wiki/') and link.count('/') == 2 and '.' not in link and ':' not in link]

    return text, links




def doit(page_url):
    try: 
        page_text, page_links = get_wikipedia_page_content(page_url)
        # page_text = page_text.replace("\n", " ").split(" ")
        # page_text = ' '.join([word.lower() for word in page_text if all([letter.isalpha() for letter in word])])

        # pd.DataFrame(page_links, columns=['url']).to_sql('links', con, if_exists='append', index=False)
        # pd.DataFrame([[page_text, page_url]], columns=['text', 'url']).to_sql('pages', con, if_exists='append', index=False)

        randomm = np.random.randint(0, 10**10)
        pd.DataFrame(page_links, columns=['url']).to_csv(f'data/text/wiki/csv/links{randomm}.csv', header=False, index=False)
        pd.DataFrame([[page_text, page_url]], columns=['text', 'url']).to_csv(f'data/text/wiki/csv/pages{randomm}.csv', header=False, index=False)
        # pd.DataFrame(page_links, columns=['url']).to_csv(f'/Volumes/Marc - ByteG/code_io_test/links{randomm}.csv', header=False, index=False)
        # pd.DataFrame([[page_text, page_url]], columns=['text', 'url']).to_csv(f'/Volumes/Marc - ByteG/code_io_test/pages{randomm}.csv', header=False, index=False)
    except Exception as e:
        print(e)
        pass
 
def multi_threaded_doit(page_urls):
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(doit, page_urls)



def remove_duplicates_from_tables(database_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)

    # Get the list of table names
    table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name']

    # Iterate over each table
    for table_name in tqdm(table_names):
        # Read the table into a DataFrame
        df = pd.read_sql_query(f'select * from {table_name}', conn)

        # Remove duplicates
        df.drop_duplicates(inplace=True)

        # Replace the original table with the deduplicated DataFrame
        df.to_sql(table_name, conn, if_exists='replace', index=False)

    # Close the database connection
    conn.close()


def process_csv(file): 
    file = file[0]
    if 'link' in file: 
        try: 
            df = pd.read_csv(file, header=None).drop_duplicates()
            df.columns = ['url']
            df.to_sql('links', con, if_exists='append', index=False)
            shutil.move(file, file.replace('csv/', 'imported_csv/'))
            # print('moved link')
            # time.sleep(1)
        except pd.errors.EmptyDataError:
            pass  
        # shutil.move(file, file.replace('csv/', 'imported_csv/'))
    elif 'page' in file: 
        # print('page in file')
        try:  
            df = pd.read_csv(file, header=None).drop_duplicates()
            # print(f'df.shape: {df.shape}')
            # time.sleep(1)
            df.columns = ['text', 'url']
            # print(df)
            # time.sleep(19)
            df.to_sql('pages', con, if_exists='append', index=False)
            shutil.move(file, file.replace('csv/', 'imported_csv/'))
            # print('moved page')
            # time.sleep(1)
        except pd.errors.EmptyDataError: 
            pass     
        # print('doneeeeee')   
        # time.sleep(5)

def multi_threaded_process_csv(page_urls):
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_csv, page_urls)






def get_random_word():
    # Load a local dictionary file
    words = nltk.corpus.words.words()
    
    # Get a random word
    random_word = random.choice(words)
    return random_word

def get_word_definitions(word):
    # Use nltk to look up word definitions
    definitions = nltk.corpus.wordnet.synsets(word)
    if definitions:
        # Retrieve the definitions if available
        definitions = [definition.definition() for definition in definitions]
        return definitions
    else:
        return None
    


def calculate_entropy(sentence):
    try: 
        # convert the sentence to lower case and remove all non alphabetic characters
        sentence = ''.join(c for c in sentence.lower() if c.isalpha())
        
        # count the frequency of each letter
        freqs = Counter(sentence)
        
        # calculate the total number of letters
        total_chars = sum(freqs.values())
        
        # calculate the probability for each letter and then the entropy
        entropy = -sum(count/total_chars * math.log2(count/total_chars) for count in freqs.values())
        
        # normalize the entropy
        entropy /= math.log2(min(total_chars, 26))
        
        return entropy
    except: 
        print(f'sentence', sentence)
        print(dasf)

def clean(sentence): 
    try: 
        return str(re.sub(r'[^a-zA-Z,.\s:]', '', x))
    except:
        print(f'sentence: {sentence}')

def generate_definitions(d=None):
    # while True:
    # Get a random word
    # Get a random word
    random_word = get_random_word()
    # print(f'random_word: {random_word}')

    # Get definitions of the random word
    definitions = get_word_definitions(random_word)
    # print("Random Word:", random_word)
    # print("Definitions:", definitions)
    # print(f'definitions: {definitions} | {definitions is not None}')
    if definitions is not None:
        definitions = '. '.join(definitions)
        # print('in the if')
        df = pd.DataFrame({
            'word': [random_word],
            'definition': [definitions]
        })
        # print(f'df.shape: {df.shape}')
        # print(tabulate(df, headers='keys'))
        # df['entropy'] = (df['word'] + df['definition']).apply(clean)
        df['entropy'] = df['word'] + df['definition']
        entropycolumn = df['entropy'].tolist()
        # print(f'df endtroypy: {entropycolumn}')
        df['entropy'] = df['entropy'].apply(calculate_entropy)
        # print(f'MY DFSSSSS', df, df, df, df, df)
        df.to_sql('words', con, if_exists='append', index=False)
        # print(f'df.shape: {df.shape}')
        # print(df)

        # time.sleep(3)
        # c += 1
    # print(c, end='\r')

    # print(pd.read_sql_query('select * from words', con).shape)
    
def multi_threaded_generate_definitions(page_urls):
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(generate_definitions, page_urls)




    
if __name__ == '__main__':
    # df = pd.read_sql_query('select distinct l.* from links l left join pages p using(url) where p.url is null', con)
    # df = pd.read_csv('data/text/wiki/onemillionlinks.csv', header=1)
    # df.columns = ['url']
    # print(df)
    # print(f'len(df): {len(df)}')#, pd.read_sql_query('select * from pages', con).shape)
    # links = df['url'].to_list()
    # np.random.shuffle(links)
    # # links = links[:10000]
    
    # chunksize = len(links) // (8 * 4)
    # cpu_count = 8
    # links = np.array_split(links, len(links))
    # process_map(multi_threaded_doit, links, max_workers=cpu_count)



    # # Move files around
    # ####################################
    # directory = 'data/text/wiki/csv/'
    # all_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]
    # all_files = np.array_split(all_files, len(all_files))
    # cpu_count = 8
    # # for file in all_files: 
    # #     process_csv(file)
    # process_map(process_csv, all_files, max_workers=cpu_count)


    # # Remove duplicates
    # ####################################
    # remove_duplicates_from_tables('data/text/wiki/wikipedia2.sqlite') 






    ## Generate definitions DONT FORGET TO CREATE A TEXT FILE BASED ON ALL NLTK WORDS
    ####################################
    # for x in range(1000):
    #     generate_definitions()
    process_map(generate_definitions, list('a'*100000), max_workers=8)



