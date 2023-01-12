## About the project
Game to make you type faster. By logging time at which each key is pressed, the game will propose words containing letters you're slow to typeand adapt the proposed words at which you're to make you progress based on your weakness.





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


