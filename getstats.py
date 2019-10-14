#!/usr/bin/env python
from telethon import TelegramClient
from telethon import utils
import telegramconfig as cfg
import sys

client = TelegramClient(cfg.user['name'], cfg.user['api_id'], cfg.user['api_hash'])

async def main():
    # if no args passed, send message to myself
    recipient = 'me'

    if len(sys.argv) >= 2:
        recipient = sys.argv[1]
        print('recipient:', recipient)
        result = await client.get_entity(recipient)
        display_name = utils.get_display_name(result)
        if len(display_name) > 0:
            print("found recipient: " + recipient)
            print("display name: " + display_name)

    # Now you can use all client methods listed below, like for example...
    await client.send_message(recipient, 'I just sent you this message from my python script :)')

with client:
    client.loop.run_until_complete(main())
