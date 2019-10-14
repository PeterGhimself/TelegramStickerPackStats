#!/usr/bin/env python
from telethon import TelegramClient
from telethon import utils, events
import telegramconfig as cfg
import sys
import time
import json

client = TelegramClient(cfg.user['name'], cfg.user['api_id'], cfg.user['api_hash'])
replies = []

def get_arr_packstats(msg):
    msgs = msg.split('\n\n')
    # remove first and last
    msgs = msgs[1:-1]

    #print('MSGS:', msgs)
    #print()

    stats = []
    for m in msgs:
        lines = m.split('\n')
        for l in lines:
            stats.append(l)

    stats = stats[:-1]
    raw_vals = []

    for s in stats:
        data = s.split(':')
        for d in data:
            raw_vals.append(d.strip())

    return raw_vals

def get_json(arr):
    data = {}

    for i in range(0, (len(arr) - 1)):
        # to ensure key/value pairs get added correctly
        if i % 2 == 0:
            data[arr[i]] = arr[i + 1]

    json_data = json.dumps(data)

    return json_data

@client.on(events.NewMessage(pattern='Stats for the sticker pack'))
async def get_packstats(event):
    #print("new message received")
    #print(event.message.message)
    replies.append(event.message.message)

async def main():
    global replies
    # if no args passed, send message to myself
    recipient = 'Stickers'
    queries = ['/packstats']
    sticker_set = 'SpaceConcordia'

    result = await client.get_entity(recipient)
    display_name = utils.get_display_name(result)

    if len(display_name) > 0:
        print('found recipient: ' + recipient + ', display name: ' + display_name)

    else:
        print('recipient: ' + recipient + ' not found')

    print('sending message: "' + queries[0] + '"')

    # send /packstats query
    await client.send_message(recipient, queries[0])
    time.sleep(0.5)
    await client.send_message(recipient, sticker_set)
    time.sleep(0.5)

    # get responses
    await client.catch_up()

    # remove duplicates
    # idk why but either I get duplicates or nothing at all
    replies = list(set(replies))
    pack_stats = get_arr_packstats(replies[-1])

    json_data = get_json(pack_stats)

    print('json_data', json_data)
    print(json_data, file=open('packstats.json', 'w'))

with client:
    client.loop.run_until_complete(main())
