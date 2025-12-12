# Import necessary libraries
import discord
from discord import app_commands
from discord.ext import commands
from functions import *
from variables import * 
import numpy as np
import asyncio

# Create a command to add team emojis
async def handle_create_team_emojis(interaction: discord.Interaction):

    """
    Adds custom emojis for each NFL team to the server.
    This command needs custom images in the correct directory.
    The images should be named in the format 'team_name.webp' where team_name is the name of the team in lowercase with spaces replaced by underscores.
    """ 

    # Defer immediately so Discord knows you're working (it'll raise an error if you don't)
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    success_count = 0
    failure_count = 0
    already_exists = 0

    for nfl_team in NFL_TEAMS:

        # Generate emoji name and image path
        emoji_name = nfl_team.lower().replace(" ", "_")
        image_path = os.path.join("images", "nfl_logos", emoji_name + ".webp")

        # Use a helper that returns a status string, NOT call.response.send_message
        result = await create_custom_emoji(guild, emoji_name, image_path)
        
        if result.startswith("Added:"):
            success_count += 1
        elif result.startswith("Failed to add emoji:"):
            failure_count += 1
        elif result.startswith("Already exists:"):
            already_exists += 1

    # Reply ONCE with a summary
    summary = f"Successfully added {success_count} emojis\nFailed to add {failure_count}\nSkipped {already_exists} that already existed."
    await interaction.followup.send(summary, ephemeral=True)

async def handle_create_team_roles(interaction: discord.Interaction):
    """
    Creates roles for each NFL team in the server.
    This command creates roles with the same names as the teams.
    """

    # Defer immediately so Discord knows you're working (it'll raise an error if you don't)
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    success_count = 0
    failure_count = 0
    already_exists = 0

    for nfl_team in NFL_TEAMS:
        role_name = nfl_team

        # Use a helper that returns a status string, NOT call.response.send_message
        _, result = await create_role(guild, role_name)
        
        if result.startswith("Added Role:"):
            success_count += 1
        elif result.startswith("Role already exists:"):
            already_exists += 1
        elif result.startswith("Failed to create role:"):
            failure_count += 1
        else:
            raise ValueError(f"Unexpected result: {result}")

    # Reply ONCE with a summary
    summary = f"Successfully created {success_count} roles\nFailed to create {failure_count}\nSkipped {already_exists} that already existed."
    await interaction.followup.send(summary, ephemeral=True)

async def handle_choose_team(interaction: discord.Interaction, bot):

    guild = interaction.guild
    timeout = 180  # 3 minutes

    class NFLTeamView(discord.ui.View):

        def __init__(self, conference, timeout=timeout):
            super().__init__(timeout=timeout)

            if conference not in ["AFC", "NFC"]:
                raise ValueError("Conference must be either 'AFC' or 'NFC'")
            
            # initialize interact confeerene with None
            self.chosen = False

            row_index = 0  # Start at the first row
            for division_name, division_teams in NFL_DIVISIONS.items():

                # Filter teams based on the conference
                if not division_name.startswith(conference):
                    continue

                for team in division_teams:
                    
                    # Skip if there is already a user with that team role
                    existing_role = discord.utils.get(guild.roles, name=team)
                    if existing_role is None:
                        _, role = create_role(guild, team)
                        existing_role = role
                    if len(existing_role.members) > 0:
                        continue

                    # Get emoji based on the team name
                    emoji = discord.utils.get(guild.emojis, name=team.lower().replace(" ", "_"))
                    if not emoji:
                        print(f"Emoji for {team} not found, skipping.")
                        continue

                    # Create a button 
                    button = discord.ui.Button(
                        label="",
                        style=discord.ButtonStyle.secondary,
                        emoji= f"<:{emoji.name}:{emoji.id}>",
                        row=row_index,
                        # custom_id=f"choose_{team.lower().replace(' ', '_')}"
                    )

                    # Assign a callback unique for each button
                    button.callback = self.make_callback(team)
                    self.add_item(button)

                # Increment row index
                row_index += 1

        # Helper method to generate callbacks per team
        def make_callback(self, team_name):
            async def callback(interaction: discord.Interaction):
                
                role_name = team_name
                role = discord.utils.get(guild.roles, name=role_name)

                # Add the role to the user
                await interaction.user.add_roles(role)

                # Remove wait list role
                wait_list_role = discord.utils.get(guild.roles, name="Wait List")
                if wait_list_role in interaction.user.roles:
                    await interaction.user.remove_roles(wait_list_role)
                    print(f"{interaction.user.name} has removed the wait list role")

                # Set the user's nickname
                try:
                    await interaction.user.edit(nick=team_name)
                    print(f"User {interaction.user.name} has chosen the {team_name} and their nickname has been set.")
                except discord.Forbidden:
                    print(f"User {interaction.user.name} has chosen the {team_name}, but I don't have permission to change their nickname. Please change it manually.")

                self.chosen = True  # Update the conference in the view
                self.team_name = team_name  # Store the team name in the view
                self.stop()
                
            return callback
    
    # Check if the user already has a team role
    # Get the users roles
    user_roles = np.array([role.name for role in interaction.user.roles])

    # Check if the user already has a team role
    user_team_bool = np.isin(np.array(NFL_TEAMS), user_roles)
    if np.any(user_team_bool):
        user_team = np.array(NFL_TEAMS)[user_team_bool][0]
        await interaction.response.send_message(f"You are already the {user_team}. To switch teams reach out for commissioner aproval")
        
    else:
        
        # Count available teams
        num_avaiable_teams = await count_available_teams(guild)
        if num_avaiable_teams == 0:
            await handle_no_available_teams(interaction)
        else:
            
            # Create the view with buttons for each team
            bot.afc_view = NFLTeamView(conference="AFC")
            bot.nfc_view = NFLTeamView(conference="NFC")

            choose_team_string = "Please select from the available teams below:"
            await interaction.response.send_message(choose_team_string, ephemeral=True)
            afc_msg = await interaction.followup.send("AFC Teams:", view=bot.afc_view, ephemeral=True)
            nfc_msg = await interaction.followup.send("NFC Teams:", view=bot.nfc_view, ephemeral=True)

            # wait until after callback interation is complete
            await asyncio.wait(
                [bot.afc_view.wait(), bot.nfc_view.wait()],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            main_msg = await interaction.original_response()
            # After the user has chosen a team, delete the conference views and edit the main message
            if bot.afc_view.chosen:
                team_name = bot.afc_view.team_name
                await afc_msg.delete()
                await nfc_msg.delete()
                await main_msg.edit(content=f"You have chosen the {team_name}!", view=None)
                
            elif bot.nfc_view.chosen:
                team_name = bot.nfc_view.team_name
                await afc_msg.delete()
                await nfc_msg.delete()
                await main_msg.edit(content=f"You have chosen the {team_name}!", view=None)

            else:
                await afc_msg.delete()
                await nfc_msg.delete()
                await main_msg.edit(content="You did not choose a team in time. Please try again later.", view=None)




            




async def handle_remove_team_role(interaction: discord.Interaction, user: discord.Member):
    """
    Remove a team role from a user.
    This command is intended for commissioners only.
    """

    # Check if the user has the commissioner role
    if not any(role.name == "Commissioner" for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Get the user's roles
    user_roles = np.array([role.name for role in user.roles])

    # Check if the user has any team roles
    team_roles = np.array(NFL_TEAMS)
    user_team_roles = np.isin(team_roles, user_roles)

    if not np.any(user_team_roles):
        await interaction.response.send_message(f"{user.name} does not have any team roles.", ephemeral=True)
        return

    # Remove all team roles from the user
    roles_to_remove = team_roles[user_team_roles]
    
    for role_name in roles_to_remove:
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await user.remove_roles(role)

    # Remove the user's nickname
    try:
        await user.edit(nick=None)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to change the user's nickname. Please change it manually.", ephemeral=True)
        return

    await interaction.response.send_message(f"Removed team roles {', '.join(roles_to_remove)} from {user.name}.", ephemeral=True)
