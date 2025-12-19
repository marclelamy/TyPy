![](https://github.com/marclelamy/pyTypeFast/blob/main/game_demo.gif)



## About the project
Type Faster is a game designed to help you type faster and more accurately by proposing words containing the letters you're slow to type. The game records the time at which each key is pressed, and uses this data to adapt the proposed words to your skill level.





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
| difficulty | Difficulty of the corpus used to pick words. `Easy` is a `3.000` common words (avg/max length: `6.41`/`16`), `Medium` is google's top `10.000` words (`6.59`/`18`) and `Hard` contains `370.106` words (`9.44`/`31`)| Easy, Medium, Hard | Medium |
| word_count | How many words to be proposed in the game | `1` to `your_desire` | `25` |
| word_length_min | Minimum length of words | `1` to `max_length` | `4` |
| word_length_max | Maximum length of words | `1` to `max_length` | `1000` |
| capitalized_words | If int, count of words of word_count to have capitalized letter in it. If float, percentage of words of word_count to have capitalized letter in it | - `0` to `1`: percentage of word to cap </br> - `1` to n: number | `0` |
| capitalized_letters | If int, numbers of letters in each word to be capitalized. If float, percentage of letters in each word to be capitalized. if 'first', capitalizes only the first letter of the words to be capitalized. | - `0` to `1`: percentage of letters to cap </br>- 1 to `n`: number</br>- First: first letter cap only" | `0` |
| punctuation | If int, count of words of word_count to have punctualtion around it. If float, percentage of words of word_count to have punctuation around it. | `0` to `100` or `0` to word_count | `0` |
| punctuation_char | Number of different punctuations used | `0` to `n` | `0` |
| force_shift | Force to type the right shift of the keyboard. When having capitalization or punctuation on, you will be force to type use the shift key (right/left) with the letter not typing on the key. | `True`/`False` | `False` |
| n_games_banned_words | Wont propose words that have been used if not all have been used. If all have been, will remove the half of the corpus from the last games. | -1 or greater than `0` | `0` |
| train | Analyse the past games to propose potential slow words to type to force weakness learning. | `True`/`False` | `False` |
| train_easy | For the training, instead of proposing the potential slow words, it'll propose the potential fast words | `True`/`False` can't be `True` without `train` being `True` too | `False` |

Game preferences: 
| Rule | Rule Description | Value type | Default |
|:----|:----------------|:----------|:-------:|
| player_name | The name of the player | string | 'NPC' |
| display_chart | Boolean for if a live chart should be displayed (beta) | `True`/`False` | `False` |
| display_wpm | Boolean for if the words per minute should be displayed | `True`/`False` | `True` |
| display_words_left | Boolean for if the words left to type should be displayed | `True`/`False` | `True` |
| display_word_count | -1 for auto, it's find the width of window and scale accordingly. | -1 or greater than 0 | -1 |







## Feedback
If you have any feedback or suggestions for improving the game, please feel free to create an issue or Pull Request.