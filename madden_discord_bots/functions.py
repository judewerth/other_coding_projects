# This file is meant to store functions that are used in multiple places.

# Import Librariess
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from variables import *
import numpy as np

async def create_private_channel(member, channel_name, category_name=None):
    """
    Create a private channel for a new member in the specified guild and category.
    The member can variable can also be a role or any object that has a guild attribute.
    """
    guild = member.guild

    # Create or get the category for the private channels
    category = discord.utils.get(guild.categories, name=category_name)
    if category is None:
        # If the category does not exist, create it
        print(f"No category named '{category_name}' found. Creating a new category.")
        category = await guild.create_category(name=category_name)

    # Set up private channel permissions
    # Find 'commissioner' role (case-insensitive)
    commissioner_role = discord.utils.find(
        lambda r: r.name.lower() == "commissioner", guild.roles
    )
    # Get server owner as fallback
    server_owner = guild.owner

    # Set up permission overwrites
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False), # everyone else
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True), # The new member
        guild.me: discord.PermissionOverwrite(view_channel=True),  # The bot itself
    }

    # If the commissioner role exists, give it view permissions; otherwise, give the server owner view permissions
    if commissioner_role:
        overwrites[commissioner_role] = discord.PermissionOverwrite(view_channel=True)
    else:
        overwrites[server_owner] = discord.PermissionOverwrite(view_channel=True)

    # Create the private channel for the member
    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,  # Specify the parent category here
        overwrites=overwrites  # Apply the permission overwrites (make private)
        )
    print(f"Private channel '{channel_name}' created in category '{category_name}'.")
    
    return channel

async def create_public_channel(guild, channel_name, category_name=None, create_if_not_exists=False):
    """
    Create a public channel in the specified guild and category.
    """
    # Get the category if it exists, otherwise create it
    if category_name:
        category = discord.utils.get(guild.categories, name=category_name)

        if category is None:
            if create_if_not_exists:
                print(f"No category named '{category_name}' found. Creating a new category.")
                category = await guild.create_category(name=category_name)
            else:
                print(f"Error creating public channel {channel_name}. Category '{category_name}' does not exist and 'create_if_not_exists' is False.")
                return None
    else:
        category = None

    # Create the public channel with no permission overwrites
    channel = await guild.create_text_channel(
        name=channel_name,
        category=category  # Specify the parent category here
    )
    
    # Log the creation of the public channel
    if category_name is None:
        category_name = "None"
    print(f"Public channel '{channel_name}' created in category '{category_name}'.")
    
    return channel

async def get_channel(guild, channel_name, create_if_not_exists=False):
    """
    Get a channel object by name in the specified guild.
    """
    # Find the channel by name
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    
    if channel is None:
        if create_if_not_exists:
            print(f"Creating channel '{channel_name}' as it does not exist.")
            channel = await create_public_channel(guild, channel_name)
        else:
            print(f"Channel '{channel_name}' does not exist and 'create_if_not_exists' is False.")
    
    return channel

async def handle_member_join(member):
    """
    Handle the member join event by creating a private channel and sending welcome messages.
    """

    # Define parameteers for the welcome channel
    channel_name = f'{member.name} private channel'
    category_name = "Private Channels"
    
    # Log the member join event
    print(f'{member.name} has joined the server.')
    guild = member.guild

    # Call the function to create a private channel for the new member
    channel = await create_private_channel(member, channel_name, category_name)

    # Send a welcome message in the newly created channel
    bot_information_channel = await get_channel(guild, 'bot-information', create_if_not_exists=True)

    welcome_message = f"\
    Welcome {member.mention}! This is your private channel.\n\
    This channel is for you to to use the bot privately, check out {bot_information_channel.mention} for more info!"
    await channel.send(welcome_message)

    # Send instructions message in the private channel
    rules_channel = await get_channel(guild, 'rules', create_if_not_exists=True)
    draft_time_channel = await get_channel(guild, 'draft-time', create_if_not_exists=True)

    # Define your source strings without spaces
    rules_strings = [
        "Here are some instructions to get you started:",
        f"1. Read the {rules_channel.mention} channel.",
        f"""2. Choose your team:
    - To choose your team, use the command '/choose_team'. 
    - You will be prompted with buttons for the available teams. 
    - Select your team by clicking the button.""",
        f"""3. Navigate to the {draft_time_channel.mention} channel. 
    - There you will be able to vote on a draft time. 
    - The draft won't start until all 32 teams have agreed on a time.
    - If you join during the season, unfortunately you will need to wait till next season to play. 
    - However, feel free to hang out and participate in the community.
    - Coins you earn will carry over to the next season!"""
    ]

    # Function to apply indent rules
    def format_instructions(instructions):
        result = []
        for line in instructions:
            formatted_lines = []
            for subline in line.split("\n"):
                if subline.strip().startswith("-"):
                    formatted_lines.append("        " + subline.strip())  # 8 spaces
                elif subline.strip()[0].isdigit():
                    formatted_lines.append("    " + subline.strip())      # 4 spaces
                else:
                    formatted_lines.append(subline.strip())
            result.append("\n".join(formatted_lines))
        return result

    # Format and assemble message
    rule_strings= format_instructions(rules_strings)
    instructions_message = "\n".join(rule_strings)

    await channel.send(instructions_message)

async def handle_leave(member):
    """
    Remove team role and alert wait list of an opening
    """

    guild = member.guild

    # remove team role
    # find team role user was on
    user_roles = np.array([role.name for role in member.roles])

    # Check if the user already has a team role
    user_team_bool = np.isin(np.array(NFL_TEAMS), user_roles)
    if np.any(user_team_bool):
        user_team = np.array(NFL_TEAMS)[user_team_bool][0]

        # send message to people with "Wait List" role
        channel = await get_channel(guild, channel_name="wait-list", create_if_not_exists=True)
        wait_list_role = discord.utils.get(guild.roles, name="Wait List")    

        await channel.send(f"{wait_list_role.mention}: The {user_team} is now avaiable! Use /choose_team to reserve the team.")


async def handle_member_leave(member):

    """
    Handle the member leave event by deleting the private channel, and using handle_leave
    """
    
    guild = member.guild
    channel_name = f'{member.name}-private-channel'
    category_name = "Private Channels"

    # Log the member leave event
    print(f'{member.name} has left the server.')

    # delete private channel
    cattegory = discord.utils.get(guild.categories, name=category_name)
    channel = discord.utils.get(guild.text_channels, name=channel_name, category=cattegory)
    if channel:
        await channel.delete()
        print(f"Private channel '{channel_name}' deleted.")
    
    # handle team leaving
    await handle_leave(member)


async def create_custom_emoji(guild, emoji_name, image_path):
    """
    Create a custom emoji in the specified guild.
    """

    existing = discord.utils.get(guild.emojis, name=emoji_name)

    if existing:
        print(f"An emoji named '{emoji_name}' already exists. Skipping upload.")
        return f"Already exists: {emoji_name} ({existing})"
    
    try:
        # Open the image file as bytes
        with open(image_path, "rb") as image:
            image_bytes = image.read()

        # Create the custom emoji
        emoji = await guild.create_custom_emoji(name=emoji_name, image=image_bytes)
        print(f"Emoji {emoji} added successfully.")
        return f"Added: {emoji_name} ({emoji})"
    
    except Exception as e:
        print(f"Failed to add emoji: {e}")
        return f"Failed to add: {emoji_name}"

async def create_role(guild: discord.Guild, role_name: str):
    # Find role by name (case-insensitive)
    existing_role = discord.utils.get(guild.roles, name=role_name)
    if existing_role:
        # Role already exists
        return_str = f"Role already exists: {role_name}"
        print(return_str)
        
        return existing_role, return_str  # or return f"Role '{role_name}' already exists."
    
    # Create the role
    try:
        role = await guild.create_role(name=role_name)
        return_str = f"Added Role: '{role_name}' successfully."
        print(return_str)
 
        return role, return_str  # or return f"Role '{role_name}' created successfully."
    except Exception as e:
        # Handle errors (e.g., missing permissions)
        return_str = f"Failed to create role: {role_name}.\n{str(e)}"
        print(return_str)

        return None, return_str  # or return f"Failed to create role '{role_name}': {str(e)}"
    
async def handle_no_available_teams(interaction: discord.Interaction):
    """
    Handle the case when there are no available teams to choose from.
    """
    # Check if the user is already on the wait list
    role_name = "Wait List"

    wait_list_role = discord.utils.get(interaction.guild.roles, name=role_name)
    if wait_list_role is None:
        # Create the wait list role if it doesn't exist
        wait_list_role, _ = await create_role(interaction.guild, role_name)
    
    # Check if the user already has the wait list role
    if wait_list_role in interaction.user.roles:
        await interaction.response.send_message(
            f"You are already on the wait list. Please wait for a team to become available.",
            ephemeral=True
        )
        return

    # Create a message to inform the user
    message = "There are no available teams at the moment. Would you like to join the wait list and be notified when a team becomes available?"

    view = discord.ui.View(timeout=None)  # Create a view to hold the buttons
    # Create a Yes and No button
    yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
    no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)
    async def yes_callback(interaction: discord.Interaction):

        # Handle the Yes button click
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        await interaction.user.add_roles(role)

        await interaction.response.edit_message(content="You have been added to the wait list!", view=None)
        view.stop()

    async def no_callback(interaction: discord.Interaction):
        # Handle the No button click
        await interaction.response.edit_message(content="You chose not to join the wait list.", view=None)
        view.stop()
    
    # Assign the callbacks to the buttons
    yes_button.callback = yes_callback
    no_button.callback = no_callback

    # Add the buttons to the view
    view.add_item(yes_button)
    view.add_item(no_button)

    # Send the message with the buttons
    await interaction.response.send_message(message, view=view, ephemeral=True)

        
async def count_available_teams(guild):
    count = 0
    for _, division_teams in NFL_DIVISIONS.items():
        for team in division_teams:
            role = discord.utils.get(guild.roles, name=team)
            if role is None or len(role.members) == 0:
                count += 1
    return count