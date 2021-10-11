import asyncio
import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db
from dev.db import Database
from string import ascii_lowercase
import random

class Coliseum(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Coliseum extension ready. ')
    
    @commands.command(aliases=['teamjoin'])
    async def tjoin(self, ctx: commands.Context, game_id=None, hidename=False):
        pass

    @commands.command(aliases=['solojoin'])
    async def sjoin(self, ctx: commands.Context, game_id=None, hidename=False):
        user = ctx.author

        user_data = Database.getStorageData(user)

        gdata = user_data["game"]

        if hidename != False:
            name = "UNKNOWN_USERNAME" + f"|{user.id}" + f"|{gdata['username']}"
        
        else:
            name = gdata["username"] + f"|{user.id}"
        
        if game_id != None:
            try:
                game_data = Database.Coliseum[game_id]

                def check(m: discord.Message):
                    return m.author.id == ctx.author.id
                
                try:
                    msg = await self.client.wait_for('message', check=check, timeout=60)
                
                except asyncio.TimeoutError:
                    await ctx.send()

                game_data["players"][user.id] = name

                return # do not proceed because code will make host a game with the user as host, but if the user wants to join a game, then add the user to the game
            
            except KeyError:
                await ctx.send(f'No game with game id of `{game_id}` was found - if you want to join the game your friend is in, simply enter `.join <@your friend\'s name>.')

                return

        numbers = [str(i) for i in range(0,10)]
        
        game_id = ''

        letters_and_numbers = list(ascii_lowercase).extend(numbers)

        for _ in range(6):
            game_id += random.choice(letters_and_numbers)

        while True:
            if game_id in list(Database.Coliseum.MatchmakingServer):
                game_id += random.choice(letters_and_numbers)
            
            else:
                break
        
        col = Database.Coliseum

        col.MatchmakingServer[game_id] = {
            "team fight":False,
            "players":{
                user.id:name
            }
        }
  
def setup(client: commands.Bot):
    client.add_cog(Coliseum(client))