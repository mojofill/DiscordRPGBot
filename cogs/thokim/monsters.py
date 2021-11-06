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

        em = discord.Embed()
    
    @commands.command()
    async def engage(self, ctx: commands.Context):
        pass

    @commands.command()
    async def skip(self, ctx: commands.Context):
        pass

def setup(client: commands.Bot):
    client.add_cog(Monsters(client))