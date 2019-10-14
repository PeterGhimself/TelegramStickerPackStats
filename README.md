# TelegramStickerPackStats

A script to interact with the `Stickers` bot of Telegram to obtain usage statistics and save them. The goal would be to have this daily (at the end of the day) and aggregate the data in CSV to be able to easily generate graphs later on.

## Setup

1. Make sure you have [Python 3.5+](https://www.python.org/downloads/) installed. If you are using windows make sure to install [Git Bash](https://git-scm.com/downloads) so you can download the code and have a decent terminal to use.
2. In a terminal run `git clone https://github.com/PeterGimhself/TelegramStickerPackStats.git`
2. Run `pip install telethon` to install dependencies. If you're on Linux/Mac then it is recommended to use `virtualenv` to install the required dependencies. See steps 1 and 2 [here](https://github.com/PeterGhimself/BranchListUpdater#linux) for an example of 
using `virutalenv` with `requirements.txt`.
3. Before running the script you will need to [get your API id](https://core.telegram.org/api/obtaining_api_id) and then update the configuration file `telegramconfig.py` with your values. Make sure not to commit or publish your credentials. See step 4 regarding 
this.
4. **IMPORTANT**: Make sure to run `git update-index --skip-worktree telegramconfig.py` after cloning to ensure that the changes to the config file won't be tracked.
5. You may need to run `chmod +x getstats.py` to ensure it is executable.

## How to run

### Send message

Send message to yourself:

- `./getstats.py`

Or to others in your contacts (they must have a public username):

- `./getstats.py JohnDoe`
