import discord
import re
import random

from dotenv import load_dotenv
load_dotenv()

import os

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('+roll '):
        await roll(message)


async def roll(message):

    content = message.content

    roll = content.lstrip('+roll ')

    match = re.match(r'(\d*)d(\d+)([e!])?(k[hl]\d*)?([+-]\d+)?', roll)

    if not match:
        print(f'No match found on input "{roll}".')
        return

    rolls = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    explosion = True if (match.group(3) and sides >= 2) else False

    keep = match.group(4) if match.group(4) else False

    if keep:
        keep = keep + '1' if len(keep) == 2 else keep
        keep_multiplier = 1 if keep[:2] == 'kh' else -1 if keep[:2] == 'kl' else ''
        keep_amount = int(keep[2])*keep_multiplier

    modifier = int(match.group(5)) if match.group(5) else 0



    if not 1 <= rolls <= 100:
        print(f'The amount of rolls must be between 1 and 100. Got {rolls}.')
        return
    
    if not 1 <= sides <= 1_000_000:
        print(f'The amount of sides must be between 1 and 1_000_000. Got {sides}.')
        return

    print(f'{rolls} roll(s). {sides} side(s).')

    total_roll_list = []

    if rolls == 1:
        roll = random.randint(1, sides)
        roll_list = [roll]

        await message.channel.send(f'**Roll:** {roll}')

    else:
        roll_list = [random.randint(1, sides) for _ in range(rolls)]
        
        await message.channel.send(f'**Rolls:** {roll_list}')

    total_roll_list = roll_list


    while explosion and sides in roll_list:
        explosion_amount = len([n for n in roll_list if n == sides])
        roll_list = [random.randint(1, sides) for _ in range(explosion_amount)]

        await message.channel.send(f'-----------------------\n:boom: EXPLOSION :boom:\n**Explosion Rolls:** {roll_list}\n')
        total_roll_list.extend(roll_list)


    all_rolls_text = f'-----------------------\n**All Rolls:** {total_roll_list}\n' if roll_list != total_roll_list else ''


    if keep:
        total_roll_list = n_max_min_numbers(total_roll_list, keep_amount)
        keep_rolls_text = f'-----------------------\n**Kept Rolls:** {total_roll_list}\n'
    else:
        keep_rolls_text = ''


    if 1 <= abs(modifier) <= 1_000_000:
        operator = '+' if modifier > 0 else '-'
        sum_roll_text = f'**Total:** {sum(total_roll_list)} {operator} {abs(modifier)} = {sum(total_roll_list) + modifier}'
    else:
        sum_roll_text = f'**Total:** {sum(total_roll_list)}'


    await message.channel.send(f'{all_rolls_text}{keep_rolls_text}{sum_roll_text}')



def n_max_min_numbers(nums, n):

    found_nums = []

    for _ in range(abs(n)):
        found_num = max(nums) if n > 0 else min(nums)
        nums.remove(found_num)
        found_nums.append(found_num)

    return found_nums

    

client.run(os.getenv("TOKEN"))
