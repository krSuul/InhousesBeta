
# bot.py

import os
import urllib
from datetime import date, datetime
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

import utils.utilities as util
import utils.rankUtil as rws
import utils.jsonUtil as jsu

os.chdir('C:/Users/Lucas/Documents/Inhouses/bot')

commandPrefix = '!'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix=commandPrefix)

@bot.event
async def on_ready():

    print(f'{bot.user.name} has connected to discord')


@bot.command("setup")
async def set_rank(ctx, *args):

    if util.check(ctx.author, ctx):

        ign = ' '.join(args)

        rank = rws.get_Rank(ign)

        if(rank == ""):
            await ctx.send("There is no ign with a rank, either you didn't input an ign, or check your spelling")
            return

        emojis = ['✅', '❌']

        message = await ctx.send("Your Rank is **" + rank + "**\nIs this correct?")

        for emoji in emojis:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.message.author and reaction.message == message
        
        reaction = await bot.wait_for("reaction_add", check=check)  # Wait for a reaction

        if str(reaction[0]) == '✅':
            
            jsu.setup(userid=str(ctx.author.id),ign=ign,rank=rank)

            await ctx.send("Added player **" + ign + "** with rank **" + rank + "**")

        if str(reaction[0]) == '❌':

            await ctx.send("Please restart with the proper ign\nOr make sure to update your u.gg found at https://u.gg/lol/profile/na1/" + urllib.parse.quote(ign) + "/overview")

# 5 v 5 lobby, automatically balanced based on rank, then decide winners and losers, winners increment wins, losers increment loss, win/win+loss for winrate
@bot.command("lobby")
async def createLobby(ctx):

    datestr = date.today().strftime("%m/%d/%Y")
    timestr = datetime.now().strftime("%H:%M")
    description = "5v5 Lobby created at " + timestr + " on " +  datestr + "\n\n**For Players**\nTo join, react with ✅\nTo leave, react with ❌\n\n**For Lobby Leader**\nTo close the lobby, react with 😭\n To begin match, react with 💢\n"
    
    embed=discord.Embed(title="League 5v5" , url="https://github.com/Tentacultist/Inhouses", description=description, color=0x006cfa)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://pentagram-production.imgix.net/cc7fa9e7-bf44-4438-a132-6df2b9664660/EMO_LOL_02.jpg?rect=0%2C0%2C1440%2C1512&w=640&crop=1&fm=jpg&q=70&auto=format&fit=crop&h=672")
    
    playerlist = [ctx.author.display_name,"---------","---------","---------","---------","---------","---------","---------","---------","---------"]
    playeridlist = [ctx.author.id, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    embed.add_field(name="Queued Players", value="{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(*playerlist), inline=True)

    msg = await ctx.send(embed=embed)

    #after embed created, need loop to add players and id to the list, up to 10 players
    emojis = ['✅', '❌', '😭', '💢']

    for emoji in emojis:
        await msg.add_reaction(emoji)

    def checkReaction(reaction, user):
        return reaction.message == msg and user != msg.author

 
    while(True):

        reaction = await bot.wait_for("reaction_add", check=checkReaction)

        # closes lobby
        if str(reaction[0]) == '😭':
            
            descriptionClosed = "Restart lobby with `!lobby`\nOr you guys can touch grass\n"
            embedClosed = discord.Embed(title="Lobby Closed", description=descriptionClosed)
            await msg.edit(embed=embedClosed)

            for emoji in emojis:
                await msg.clear_reaction(emoji)

            return
        
        if str(reaction[0]) == '✅':
            
            userid = reaction[1].id
            user = await bot.fetch_user(userid)
            usernick = user.display_name

            # user is already in lobby
            if userid in playeridlist:
                
                await ctx.send("You are already queued up")
                await msg.remove_reaction(reaction[0], user)
                continue
            
            # lobby has 10 players
            if playeridlist[9] != 0:

                await ctx.send("Lobby is Full")
                await msg.remove_reaction(reaction[0], user)
                continue
            
            firstOpen = 0

            for playerid in playeridlist:
                if playerid == 0:
                    break
                else:
                    firstOpen += 1

            playerlist[firstOpen] = usernick
            playeridlist[firstOpen] = userid

            

            # embed stuff
            embedAdd=discord.Embed(title="League 5v5" , url="https://github.com/Tentacultist/Inhouses", description=description, color=0x006cfa)
            embedAdd.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embedAdd.set_thumbnail(url="https://pentagram-production.imgix.net/cc7fa9e7-bf44-4438-a132-6df2b9664660/EMO_LOL_02.jpg?rect=0%2C0%2C1440%2C1512&w=640&crop=1&fm=jpg&q=70&auto=format&fit=crop&h=672")
            embedAdd.add_field(name="Queued Players", value="{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(*playerlist), inline=True)
            
            await msg.edit(embed=embedAdd)

            await msg.remove_reaction(reaction[0], user)
        
        if str(reaction[0]) == '❌':
            print("remove dn")

        # splits list of players into 2 and then displays
        if str(reaction[0]) == '💢':
            await ctx.send(":^)")

    # at any number of people, will split the players in half based on rank lp, need to make module to determine rank/number associated, use algo to return


# leaderboard 

# past lobbies :^)

bot.run(TOKEN)