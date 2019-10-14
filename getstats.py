#!/usr/bin/env python
from telethon import TelegramClient
from telethon import utils
import telegramconfig as cfg
import sys

client = TelegramClient(cfg.user['name'], cfg.user['api_id'], cfg.user['api_hash'])

async def main():
    # if no args passed, send message to myself
    recipient = 'me'
    msg = 'I just sent you this from a python script :)'
    default_msg = False

    if len(sys.argv) == 3:
        msg = sys.argv[2]
        recipient = sys.argv[1]
        default_msg = True
    elif len(sys.argv) == 2:
        recipient = sys.argv[1]

    result = await client.get_entity(recipient)
    display_name = utils.get_display_name(result)

    if len(display_name) > 0:
        print('found recipient: ' + recipient + ', display name: ' + display_name)
        first_name = display_name.split(' ')[0]

        if not default_msg:
            msg = 'Hey ' + first_name + '! ' + msg
    else:
        print('recipient: ' + recipient + ' not found')


    print('sending message: "' + msg + '"')

    # send message to recipient
    await client.send_message(recipient, msg)

with client:
    client.loop.run_until_complete(main())
