# Import Librariess
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio

# Import custom functions and variables
from functions import *  
from variables import * 
from slash_commands import *

# Load environment variables
load_dotenv()

# Get the Discord token from environment variables
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("No DISCORD_TOKEN found in environment variables.")

# Set up logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up Class
class Client(commands.Bot):

    # Log when the bot is ready
    async def on_ready(self):
        # logging.basicConfig(level=logging.INFO, handlers=[handler])
        # logging.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')

        # Sync commandds to discord
        try:
            guild = discord.Object(id=1304262812377419927)  
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to {guild.id}')
        except Exception as e:
            print(f'Failed to sync commands: {e}')
        print('------')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable members intent

# Create bot instance
bot = Client(command_prefix='!', intents=intents)

# Create functionality for member join event
@bot.event
async def on_member_join(member):   
    await handle_member_join(member)

@bot.event
async def on_member_remove(member):
    await handle_member_leave(member)

# Slash Comands
GUILD_ID = discord.Object(id=1304262812377419927)  

# Command to add team emojis to the serveer
@bot.tree.command(name='create_team_emojis', description='Add team emojis to the server.', guild=GUILD_ID)
async def create_team_emojis(interaction: discord.Interaction):
    await handle_create_team_emojis(interaction)

# Command to create team roles to the server
@bot.tree.command(name='create_team_roles', description='Create team roles for each NFL team.', guild=GUILD_ID)
async def create_team_roles(interaction: discord.Interaction):
    await handle_create_team_roles(interaction)

# Command to choose a team by pressing a button
@bot.tree.command(name='choose_team', description='Choose your team by pressing a button.', guild=GUILD_ID)
async def choose_team(interaction: discord.Interaction):
    await handle_choose_team(interaction, bot)

# Command to remove a team role from a user
@bot.tree.command(name='remove_team_role', description='Remove a team role from a given user (comissioner only).', guild=GUILD_ID)
async def remove_team_role(interaction: discord.Interaction, user: discord.Member):
    await handle_remove_team_role(interaction, user)



# Run the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)


