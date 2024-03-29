# TelegramStickerPackStats

A script to interact with the `Stickers` bot of Telegram to obtain usage statistics and save them. The goal would be to have this daily (at the end of the day) and aggregate the data in CSV to be able to easily generate graphs later on.

## Setup

1. Make sure you have [Python 3.5+](https://www.python.org/downloads/) installed. If you are using windows make sure to install [Git Bash](https://git-scm.com/downloads) so you can download the code and have a decent terminal to use.
2. In a terminal run `git clone https://github.com/PeterGimhself/TelegramStickerPackStats.git`
3. Run `pip install telethon` and `pip install emojis` to install dependencies. If you're on Linux/Mac then it is recommended to use `virtualenv` to install the required dependencies. See steps 1 and 2 
[here](https://github.com/PeterGhimself/BranchListUpdater#linux) for an example of 
using `virutalenv` with `requirements.txt`.
4. Before running the script you will need to [get your API id](https://core.telegram.org/api/obtaining_api_id) and then update the configuration file `telegramconfig.py` with your values. Make sure not to commit or publish your credentials. See step 4 regarding 
this.
5. **IMPORTANT**: From the root of the repository make sure to run `git update-index --skip-worktree telegramconfig.py` after cloning to ensure that the changes to the config file won't be tracked.
6. You may need to run `chmod +x sendmsg.py` to ensure it is executable.
7. You _will_ have to authenticate your account the first time you use the script. You will most likely be asked to input your phone number (formatting example: `+15145555555`) and then type in the code you receive by text message. After having done this once 
you won't be asked to authenticate like this again. Make sure not to delete the newly generated `.session` file.

## How to run

1. `sendmsg.py`
2. `getstats.py`

### Send a message to a contact

Send the default message to yourself:

- `./sendmsg.py`

To your contacts (they must have a public username):

- `./sendmsg.py JohnDoe`

Customize the message:

- `./sendmsg.py JohnDoe "This is my message to you, isn't it?"`

Send it to yourself instead:

- `./sendmsg.py me "This is a message to myself"`

### Get sticker stats

Sends the following queries to the Sticker bot:

- `/packstats` followed by `SpaceConcordia` as the parameter
- `/packtop 100`

Resulting in the following JSON files being created:

- `packstats.json`
- `packtop.json`

By running the script like so:

- `./getstats.py`
