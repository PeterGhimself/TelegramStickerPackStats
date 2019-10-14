#!/usr/bin/env python
from telethon import TelegramClient
from telethon import utils, events
from telethon.tl.types import InputMessagesFilterPhotos
import telegramconfig as cfg
import sys
import time
import json
import re

client = TelegramClient(cfg.user['name'], cfg.user['api_id'], cfg.user['api_hash'])
replies = []
rest = []

def flatten(l):
    flat_list = [item for sublist in l for item in sublist]
    return flat_list

def break_down(msgs):
    stats = []
    raw_vals = []

    for m in msgs:
        lines = m.split('\n')
        for l in lines:
            stats.append(l)

    # handle edge case: top 20 should not be affected by this
    if len(stats) > 3:
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

def get_arr_top20(msg):
    msg = str(msg)
    msgs = msg.split('\n')
    return break_down(msgs)

def get_json(arr):
    data = {}

    # case of packtop
    if '#' in arr[0]:
        packs = []

        # get all packs first
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
    # case of top20
    elif len(arr[0][0]) > 0 and '#' in arr[0][0]:
        # get stickers
        stickers = []
        flat = flatten(arr)
        for s in flat:
            if '#' in s:
                stickers.append(s)

        data = stickers
    # case of packstats
    else:
        for i in range(0, (len(arr) - 1)):
            # to ensure key/value pairs get added correctly
            if i % 2 == 0:
                data[arr[i]] = arr[i + 1]

    json_data = json.dumps(data)

    return json_data

@client.on(events.NewMessage())
async def get_stats(event):
    #print('got stats:', event)
    msg = event.message.message
    # packstats
    if 'Stats for the sticker pack' in msg:
        replies.append(msg)
    elif 'packtop' in msg:
        replies.append(msg)
    elif '#' in msg:
        replies.append(msg)
    else:
        rest.append(msg)
        path = await message.download_media()
        print('path', path)

async def main():
    global replies
    global rest
    recipient = 'Stickers'
    queries = ['/packstats', '/packtop 100', '/top 20']
    jsons = ['packstats.json', 'packtop.json', 'top20.json']
    sticker_set = 'SpaceConcordia' #@TODO: pass this as arg to script

    result = await client.get_entity(recipient)
    #@TODO: log 'result' to file? try to read from file first before calling get_entity
    # because of potential of raising FloodWaitError
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

    # synch up
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

    # synch up again
    await client.catch_up()

    pack_top = get_arr_packtop(replies[-1])
    json_data = get_json(pack_top)

    print(jsons[1] + ':', json_data)
    print(json_data, file=open(jsons[1], 'w'))

    # send /top 20
    print('sending message: "' + queries[2] + '"')
    await client.send_message(recipient, queries[2])
    time.sleep(0.5)

    # synch up again
    await client.catch_up()

    print('replies', replies)
    print('rest', rest)

    # get all messages with the bot
    chat = await client.get_input_entity('Stickers')
    msgs = client.iter_messages('Stickers')

    # does not support indexing so we get first elem the nasty way
    i = 0
    first = None
    async for msg in msgs:
        first = msg
        i += 1
        if i >= 1:
            break

    first = first.to_dict()
    total_stickers = first['entities'][0]
    total_stickers = total_stickers['length']

    u_codes = []
    top20_stats = []
    i = 0
    # multiply by 2 because every sticker has a corresponding text, and the final message included
    # +1 because the text for the image follows the image itself
    total = (total_stickers * 2) + 1
    async for msg in msgs:
        print(i)
        if i >= total:
            break
        try:
            # skip first message (last one received from bot)
            if i > 0:
                print(msg)
                print('extract', msg.message)
                m = get_arr_top20(msg.message)
                top20_stats.append(m)
                print('m', m)
        except Exception as e:
            print(e)
            err = '"' + str(e) + '"'
            print('err', err)
            u_code = err.partition('encode character')[2]
            u_code = u_code.partition('in position')[0].strip()
            print('u_code:', u_code)
            u_codes.append(u_code)
            #print(str(msg).encode(sys.stdout.encoding, errors='replace'))
        i += 1

    print('u_codes', u_codes)
    print('top20_stats', top20_stats)

    #top20_stats = flatten(top20_stats)
    #print('top20_stats_flat', top20_stats)
    json_data = get_json(top20_stats)

    print(jsons[2] + ':', json_data)
    print(json_data, file=open(jsons[2], 'w'))
    print()

with client:
    client.loop.run_until_complete(main())
