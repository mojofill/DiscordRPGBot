"""I'm deciding whether this file is worth keeping or not"""

from dev.db import Database
import discord,random,asyncio
from discord.ext import commands,tasks
from dev.tools import tools
from dev.api import db

class Monsters(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.command()
    async def monster(self, ctx: commands.Context):
        """Tells the user about the specific monster they asked for."""

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        monsters = user_data["monsters"]

        if monsters["prevoew monster"] == None:
            await ctx.send(f'{user.mention} no monster in sight ❌')
            return
        
        monster_data = monsters["preview monster"]

        # TODO: decide to keep or not keep monster health in the preview - if taken out it would make the game harder
        name: str = monster_data["name"]
        health: int = monster_data["health"]
        equipment_data: dict = monster_data["equipment"]
        
    
    @commands.command()
    async def engage(self, ctx: commands.Context):
        """Starts fight between user and monster."""

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        monsters = user_data["monsters"]

        monsters["engaged monster"] = monsters["preview monster"]

    @commands.command()
    async def skip(self, ctx: commands.Context):
        pass

def setup(client: commands.Bot):
    client.add_cog(Monsters(client))