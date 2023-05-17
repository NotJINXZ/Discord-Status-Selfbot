import discord
from discord.ext import commands
import itertools
import json
from colorama import init, Fore, Style
import logging
import ctypes

# Initialize colorama
init()

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Load or create config
try:
    with open('config.json') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        'time_interval': 30,  # Time interval between cycling (in seconds)
        'statuses': {
            'Made by jinxz!': {
                'type': 'streaming'
            }
        },  # Dictionary of status_name: status_info pairs
        'streaming_url': 'https://twitch.tv/its_jinxz',
        'tokens': ['YOUR_TOKEN']  # List of bot tokens
    }
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print(f"[{Fore.RED}-{Style.RESET_ALL}] Please fill out the 'config.json' file with your bot tokens, streaming URL, and customize other settings.")
    exit()

# Function to validate statuses
def validate_statuses(statuses):
    if not isinstance(statuses, dict) or len(statuses) == 0:
        raise ValueError("Invalid statuses. Please provide a dictionary of status_name: status_info pairs.")
    return statuses

# Function to validate bot tokens
def validate_tokens(tokens):
    if not isinstance(tokens, list) or len(tokens) == 0:
        raise ValueError("Invalid bot tokens. Please provide a list of bot tokens.")
    return tokens

# Check config validity
try:
    config['time_interval'] = int(config['time_interval'])
    config['statuses'] = validate_statuses(config['statuses'])
    config['tokens'] = validate_tokens(config['tokens'])
except (ValueError, KeyError) as e:
    print(f"[{Fore.RED}-{Style.RESET_ALL}] Invalid config format. Please check the 'config.json' file and ensure all fields are correctly filled.")
    exit()

status_cycle = itertools.cycle(config['statuses'].items())

# Variable to store the count of online clients
online_count = 0

bots = []
for token in config['tokens']:
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), self_bot=True)
    bots.append(bot)

    @bot.event
    async def on_ready():
        global online_count
        online_count += 1
        logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        set_console_title(online_count)
        await cycle_status()

    @bot.event
    async def on_disconnect():
        global online_count
        online_count -= 1
        set_console_title(online_count)

    async def cycle_status():
        status_name, status_info = next(status_cycle)
        status_type = status_info.get('type')

        activity_type = getattr(discord.ActivityType, status_type, None)
        if activity_type is None:
            logging.error(f"Invalid status type '{status_type}' for status name '{status_name}'. Skipping...")
            await bot.change_presence(activity=None)
        else:
            streaming_url = config.get('streaming_url')
            await bot.change_presence(activity=discord.Streaming(name=status_name, url=streaming_url))

        bot.loop.call_later(config['time_interval'], bot.loop.create_task, cycle_status())

# Function to set console title with the count of online clients
def set_console_title(online_count):
    title = f"JINXZ Discord Status (Clients Online: {online_count})"
    ctypes.windll.kernel32.SetConsoleTitleW(title)



# Run all bots with respective tokens
try:
    for bot, token in zip(bots, config['tokens']):
        logging.info(f"Logging in with token: {token[:10]}...")
        bot.run(token)
except discord.errors.LoginFailure:
    print(f"[{Fore.RED}-{Style.RESET_ALL}] Improper token has been passed : {token}")