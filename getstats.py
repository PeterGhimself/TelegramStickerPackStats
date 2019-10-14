#!/usr/bin/env python
from telethon import TelegramClient
from telethon import utils, events
import telegramconfig as cfg
import sys
import time
import json

client = TelegramClient(cfg.user['name'], cfg.user['api_id'], cfg.user['api_hash'])
replies = []

def break_down(msgs):
    stats = []
    raw_vals = []

    for m in msgs:
        lines = m.split('\n')
        for l in lines:
            stats.append(l)

    stats = stats[:-1]

    for s in stats:
        data = s.split(':')
        for d in data:
            raw_vals.append(d.strip())

    return raw_vals

def get_arr_packstats(msg):
    msgs = msg.split('\n\n')
    # remove first and last
    msgs = msgs[1:-1]

    return break_down(msgs)

def get_arr_packtop(msg):
    msgs = msg.split('\n\n')
    msgs = msgs[:-1]

    return break_down(msgs)

def get_json(arr):
    data = {}

    # edge case of packtop
    if '#' in arr[0]:
        packs = []

        for l in arr:
            if '#' in l:
                packs.append(l)

        pack_stats = [[]] * len(packs)
        # construct nested arrays
        i = -1
        for l in arr:
            if '#' in l:
                i += 1
            else:
                pack_stats[i].append(l)

        i = 0
        for p in packs:
            data[p] = pack_stats[i]
            i += 1
    else:
        for i in range(0, (len(arr) - 1)):
            # to ensure key/value pairs get added correctly
            if i % 2 == 0:
                data[arr[i]] = arr[i + 1]

    json_data = json.dumps(data)

    return json_data

@client.on(events.NewMessage())
async def get_stats(event):
    msg = event.message.message
    # packstats
    if 'Stats for the sticker pack' in msg:
        replies.append(msg)
    elif 'packtop' in msg:
        replies.append(msg)

async def main():
    global replies
    recipient = 'Stickers'
    queries = ['/packstats', '/packtop 100']
    jsons = ['packstats.json', 'packtop.json']
    sticker_set = 'SpaceConcordia' #@TODO: pass this as arg to script

    result = await client.get_entity(recipient)
    display_name = utils.get_display_name(result)

    if len(display_name) > 0:
        print('found recipient: ' + recipient + ', display name: ' + display_name + '\n')

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

    print(jsons[0] + ':', json_data)
    print(json_data, file=open(jsons[0], 'w'))
    print()

    # send /packtop 100
    print('sending message: "' + queries[1] + '"')

    await client.send_message(recipient, queries[1])
    time.sleep(0.5)

    # get responses
    await client.catch_up()

    pack_top = get_arr_packtop(replies[-1])
    json_data = get_json(pack_top)

    print(jsons[1] + ':', json_data)
    print(json_data, file=open(jsons[1], 'w'))
    #print()

with client:
    client.loop.run_until_complete(main())
