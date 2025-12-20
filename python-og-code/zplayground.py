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
import time


# os.remove('data/text/wiki/wikipedia2.sqlite')
con = sqlite3.connect('data/text/wiki/wikipedia2.sqlite')

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
    except Exception as e:
        print(e)
        time.s

def multi_threaded_doit(page_urls):
    with ThreadPoolExecutor(max_workers=1) as executor:
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




if __name__ == '__main__':
    # for x in range(100):
    for x in range(100):
        # df = pd.read_sql_query('select distinct * from links where url not in (select url from pages)', con)
        # print(f'len(df): {len(df)}', pd.read_sql_query('select * from pages', con).shape)
        # links = df['url'].to_list()
        # np.random.shuffle(links)
        # # links = pd.read_csv('data/text/liiiinks.csv')['url'].to_list()
        # # links = ['https://en.wikipedia.org/wiki/Wikipedia']
        # np.random.shuffle(links)
        # links = links[:10000]
        # chunksize = len(links) // (8 * 4)

        # # process_map(doit, links, max_workers=8)#, chunksize=chunksize
        # cpu_count = 4
        # process_map(multi_threaded_doit, np.array_split(links, cpu_count), max_workers=cpu_count)



        # # con = sqlite3.connect('data/text/wiki/wikipedia2.sqlite')

        directory = 'data/text/wiki/csv/'
        for file in tqdm(os.listdir(directory)): 
            file = os.path.join(directory, file)
            if 'link' in file: 
                try: 
                    df = pd.read_csv(file, header=None).drop_duplicates()
                    df.columns = ['url']
                    df.to_sql('links', con, if_exists='append', index=False)
                    shutil.move(file, file.replace('csv/', 'imported_csv/'))
                except pd.errors.EmptyDataError:
                    pass  
                # shutil.move(file, file.replace('csv/', 'imported_csv/'))
            elif 'page' in file: 
                try: 
                    df = pd.read_csv(file, header=None).drop_duplicates()
                    df.columns = ['text', 'url']
                    df.to_sql('pages', con, if_exists='append', index=False)
                    shutil.move(file, file.replace('csv/', 'imported_csv/'))
                except pd.errors.EmptyDataError:
                    pass        


        remove_duplicates_from_tables('data/text/wiki/wikipedia2.sqlite') 