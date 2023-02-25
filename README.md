![](https://github.com/marclelamy/pyTypeFast/blob/main/game_demo.gif)



## About the project
Game in the terminal to make you type faster. By logging time at which each key is pressed, the game will propose words containing letters you're slow to type and adapt the proposed words at which you're to make you progress based on your weakness.





## Installation

1. Open your terminal and go to the directory (folder) you want to store the project
   ```sh
   cd your/favorite/directory/to/clone/cool/github/projects
   ```
2. Clone the repo
   ```sh
   git clone https://github.com/marclelamy/pyTypeFast.git
   ```
3. Open directory and install `requirements.txt`
   ```sh
   cd pyTypeFast
   pip install -r requirements.txt
   ```
4. Play the game
   ```sh
   python3 main.py
   ```



## Features 
You can navigate through the game 



## Rules 
The game is supposed to be highly customizable. You can change some variables in the configs files to modify the proposed text of the presentation of the game. 

Game Config: 
| Rule | Rule Description | Value type | Default |
|:----|:----------------|:----------|:-------:|
| word_count | How many words to be proposed in the game | 1 to n | 25 |
| word_length_min | Minimum length of words | 1 to n | 4 |
| word_length_max | Maximum length of words | 1 to n | 1000 |
| capitalized_words | If int, count of words of word_count to have capitalized letter in it. If float, percentage of words of word_count to have capitalized letter in it | "- 0 to 1: percentage of word to cap - 1 to n: number" | 0 |
| capitalized_letters | If int, numbers of letters in each word to be capitalized. If float, percentage of letters in each word to be capitalized. if 'first', capitalizes only the first letter of the words to be capitalized. | "- 0 to 1: percentage of letters to cap - 1 to n: number - First: first letter cap only" | 0 |
| punctuation | If int, count of words of word_count to have punctualtion around it. If float, percentage of words of word_count to have punctuation around it. | 0 to 100 or 0 to word_count | 0 |
| punctuation_char | Number of different punctuations used | 0 to n | 0 |
| force_shift | Force to type the right shift of the keyboard. When having capitalization or punctuation on, you will be force to type use the shift key (right/left) with the letter not typing on the key. | true/false | FALSE |
| difficulty | For hard mode, less common and longer words like 'hydrocharitaceous' are proposed. Medium is google top 10000 words. Easy is common 3000 words. | Easy, Medium, Hard | Medium |
| n_games_banned_words | Wont propose words that have been used if not all have been used. If all have been, will remove the half of the corpus from the last games. | -1 or greater than 0 | 0 |
| train | Analyse the past games to propose potential slow words to type to force weakness learning. | true/false | FALSE |
| train_easy | For the training, instead of proposing the potential slow words, it'll propose the potential fast words | true/false can't be true without previous true too | FALSE |

Game preferences: 
| Rule | Rule Description | Value type | Default |
|:----|:----------------|:----------|:-------:|
| player_name | The name of the player | n/a | 'NPC' |
| display_chart | Boolean for if a live chart should be displayed (beta) | true/false | FALSE |
| display_wpm | Boolean for if the words per minute should be displayed | true/false | TRUE |
| display_words_left | Boolean for if the words left to type should be displayed | true/false | TRUE |
| display_word_count | -1 for auto, it's find the width of window and scale accordingly. | -1 or greater than 0 | -1 |




## Usage
Once you start the game, if you click on anything else or change app focus, the key detection won't detect anything else anymore. If it happens, restart the game.


## Folder Structure
<details>
<summary></summary>

.
├── data                
│   ├── queries             # Queries to pull and analyze data from the database
│   └── text                # Text files used to propose words during the games

├── src                     # Source files
│   ├── detect_keys.py              
│   ├── display.py              
│   ├── log_data.py             
│   ├── score.py            # 

</details> 


