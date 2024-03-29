#!/usr/bin/env python
from telethon import TelegramClient
from telethon import utils, events
from telethon.tl.functions.messages import GetAllStickersRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
import telegramconfig as cfg
import sys
import time
import json
import re
import pickle
import os.path
import codecs
import emojis

client = TelegramClient(cfg.user['name'], cfg.user['api_id'], cfg.user['api_hash'])
replies = []
rest = []

def get_char(s):
    return codecs.decode(s, 'unicode_escape')

def get_emoji_name(c):
    try:
        print(c)
    except Exception as e:
        print('caught exception:')
        print(str(e))

    emoji_name = 'NOT SUPPORTED BY EMOJIS MODULE'
    try:
        emoji_name = emojis.db.get_emoji_by_code(c)[0][0]
    except Exception as e:
        print('caught exception:')
        print(str(e))

    return emoji_name

def is_unicode(s):
    s = str(s)
    return re.search('\\\\(u|U)\d+\w*\d*', s)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

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

    # skip stats
    if 'Today' in stats[0]:
        pass
    # skip packtop 100
    elif re.search('#\d+ \w+', stats[0]):
        pass
    # otherwise for top 20 and packstats pop the tail
    elif len(stats) > 3:
        stats = stats[:-1]

    for s in stats:
        data = s.split(':')
        for d in data:
            raw_vals.append(d.strip())

    return raw_vals

# these functions parse bot responses messages
# and clean them so that they can be eventually made into json objects
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

def get_arr_stats(msg):
    msg = str(msg)
    msgs = msg.split('\n\n')
    msgs = str(msgs).split('\\n')
    # acceptance criteria: must be tuple
    pattern = re.compile('(\w+: \d+)|(\w+:\d+)')

    for m in msgs:
        if not pattern.match(m):
            msgs.remove(m)

    # get rid of random '\\'s
    msgs = list(filter(('\\').__ne__, msgs))

    # remove '\\'s within good strings
    msgs = [item.replace('\\', '') for item in msgs]

    return break_down(msgs)

# replace get_json() call on top20_arr with this
def get_top20_data(arr, token='#'):
    data = {}
    ranks = []

    # separate data into lists
    for i in arr:
        if '#' in i:
            ranks.append(i)

    stats = [[] for i in range(len(ranks))]

    pairs = {}
    skip = False
    j = -1
    arr_len = len(arr)
    for i in range(arr_len):
        if skip:
            skip = False
            continue

        if '#' in arr[i]:
            # reset temp obj
            if j >= 0:
                stats[j].append(pairs)
            pairs = {}
            j += 1
        elif is_unicode(arr[i]):
            pairs['unicode'] = arr[i]
            pairs['emoji'] = get_emoji_name(get_char(arr[i][1:-1]))
        else:
            if i >= arr_len - 1:
                break
            pairs[arr[i]] = arr[i+1]
            skip = True

    # once we're done just need to add the data to the last obj
    stats[j].append(pairs)

    for i in range(len(ranks)):
        data[ranks[i]] = stats[i]

    json_data = json.dumps(data, indent = 4, sort_keys=True)
    return json_data

def get_nested_data(arr, token='#'):
    data = {}
    packs = []
    is_valid = False

    if token != '#':
        # check to see if token is a valid regex
        try:
            re.compile(token)
            is_valid = True
        except re.error:
            is_valid = False

    if not is_valid:
        # get all packs first
        for l in arr:
            if token in l:
                packs.append(l)

        pack_stats = [[] for i in range(len(packs))]

        # construct nested arrays
        i = -1
        for l in arr:
            if token in l:
                i += 1
            else:
                pack_stats[i].append(l)

        i = 0
        for p in packs:
            data[p] = pack_stats[i]
            i += 1

    else:
        token = re.compile(token)
        for l in arr:
            if token.search(l):
                packs.append(l)

        stats = [[] for i in range(len(packs))]

        # construct nested arrays
        i = -1
        arr_len = len(arr)
        skip = False
        pair = {}
        for j in range(arr_len):
            if skip:
                skip = False
                continue

            if token.search(arr[j]):
                # reset temp obj
                if i >= 0:
                    stats[i].append(pair)
                pair = {}
                i += 1
            else:
                if j >= arr_len:
                    break
                pair[arr[j]] = arr[j+1]
                skip = True

        # once we're done just need to add the data to the last obj
        stats[i].append(pair)

        i = 0
        for p in packs:
            data[p] = stats[i]
            i += 1

    return data

# json-ify the data already in array form
def get_json(arr, token='#'):
    data = {}

    if token == False:
        # bypass
        json_data = json.dumps(arr, indent = 4)
        return json_data

    # case of packtop and top20, stats
    if token in arr[0]:
        data = get_nested_data(arr, token)
    # case of packstats
    else:
        for i in range(0, (len(arr) - 1)):
            # to ensure key/value pairs get added correctly
            if i % 2 == 0:
                data[arr[i]] = arr[i + 1]

    json_data = json.dumps(data, indent = 4)

    return json_data

# helper function to insert array elements into another array
# default offset set to 1 --> new elements inserted after token
# set to 0 to insert before token
def merge(arr, new_arr, token, offset = 1):
    indices = []
    ctr = 0
    for i in range(0, len(arr) - 1):
        if token in arr[i]:
            indices.append(i + offset + ctr) # insert after token
            ctr += 1 # need to shift next index by amount inserted before it

    i = 0
    for u in new_arr:
        arr.insert(indices[i], u)
        i += 1

    return arr

@client.on(events.NewMessage())
async def get_stats(event):
    msg = event.message.message
    # packstats
    if 'Stats for the sticker pack' in msg:
        replies.append(msg)
    elif 'packtop' in msg:
        replies.append(msg)
    elif '#' in msg:
        replies.append(msg)
    elif 'Stats for this sticker' in msg:
        replies.append(msg)
    else:
        rest.append(msg)
        path = await message.download_media()

async def main():
    global replies
    global rest
    recipient = 'Stickers'
    queries = ['/packstats', '/packtop 100', '/top 20', '/stats']
    jsons = ['packstats.json', 'packtop.json', 'top20.json', 'stats.json']
    # this is the short_name (not title) attribute of a sticker set object
    sticker_set_name = 'SpaceConcordia' #@TODO: pass this as arg to script
    client_obj_file = './client_obj.dictionary'
    client_obj = None

    # if exists then read client obj from file
    if os.path.exists(client_obj_file):
        print('loading existing client obj\n')
        with open(client_obj_file, 'rb') as obj_dictionary_file:
            client_obj = pickle.load(obj_dictionary_file)
    else: # or request one if we need to
        print('requesting new client obj\n')
        client_obj = await client.get_entity(recipient)

    print('client_obj', client_obj, '\n')

    # persist object to file for later reuse
    if not os.path.exists(client_obj_file):
        print('saving new client obj for later use\n')
        with open(client_obj_file, 'wb') as obj_dictionary_file:
            pickle.dump(client_obj, obj_dictionary_file)

    display_name = utils.get_display_name(client_obj)

    if len(recipient) > 0:
        print('found recipient: ' + recipient + ', display name: ' + display_name + '\n')
    else:
        print('found recipient: ' + recipient + ', display name not found\n')

    print('sending message: "' + queries[0] + '"')

    # send /packstats query
    await client.send_message(recipient, queries[0])
    time.sleep(0.3)
    await client.send_message(recipient, sticker_set_name)
    time.sleep(0.3)

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
    time.sleep(0.3)

    # synch up again
    await client.catch_up()

    pack_top = get_arr_packtop(replies[-1])
    json_data = get_json(pack_top)

    print(jsons[1] + ':', json_data)
    print(json_data, file=open(jsons[1], 'w'))
    print()

    # send /top 20
    print('sending message: "' + queries[2] + '"')
    await client.send_message(recipient, queries[2])
    time.sleep(0.3)

    # synch up again
    await client.catch_up()

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
    print('getting unicodes for stickers...\n')
    async for msg in msgs:
        if i >= total:
            break
        try:
            # skip first message (last one received from bot)
            if i > 0:
                # the following print statement (msg)
                # intentionally raises UnicodeEncodeError
                # which in turn gives us the emoji unicode for a sticker
                print(msg)
                m = get_arr_top20(msg.message)
                top20_stats.append(m)
        except Exception as e:
            err = '"' + str(e) + '"'
            u_code = err.partition('encode character')[2]
            u_code = u_code.partition('in position')[0].strip()
            u_codes.append(u_code)
        i += 1
    print('done\n')
    print('unicodes found:', u_codes)

    top20_stats = merge(flatten(top20_stats), u_codes, '#')
    json_data = get_top20_data(top20_stats)

    print(jsons[2] + ':', json_data)
    print(json_data, file=open(jsons[2], 'w'))
    print()

    # /stats (per sticker)

    # Get all the sticker sets this user has
    sticker_sets = await client(GetAllStickersRequest(0))

    # select the chosen one
    sticker_set = None
    for s in sticker_sets.sets:
        if s.short_name == 'SpaceConcordia':
            sticker_set = s

    # Get the stickers for this sticker set
    stickers = await client(GetStickerSetRequest(
        stickerset=InputStickerSetID(
            id=sticker_set.id, access_hash=sticker_set.access_hash
        )
    ))


    u_codes = []
    # Stickers are nothing more than files, so send that
    for sticker in stickers.documents:
        try: # need to throw exception to get unicode
            print(sticker)
        except Exception as e:
            err = str(e)
            u_code = err.partition('encode character')[2]
            u_code = u_code.partition('in position')[0].strip()
            u_codes.append(u_code) # remove surround single quotes

        await client.send_message(recipient, queries[3])
        time.sleep(0.3)
        await client.send_message(recipient, sticker_set_name)
        time.sleep(0.3)

        await client.send_file(recipient, sticker)

    print('u_codes', u_codes)

    time.sleep(0.3)
    # synch up
    await client.catch_up()

    total_stickers = len(stickers.documents)
    # get rid of duplicate last response (idk why it's here)
    replies = replies[:-1]
    start_index = len(replies) - total_stickers
    responses = replies[start_index:]
    stats = get_arr_stats(replies[start_index:])

    stats = merge(stats, u_codes, 'Today', 0)
    json_data = get_json(get_nested_data(stats, '\\\\(u|U)\d+\w*\d*'), False)

    print(jsons[3] + ':', json_data)
    print(json_data, file=open(jsons[3], 'w'))
    print()

with client:
    client.loop.run_until_complete(main())
