import discord
from discord.ext import commands
from dev.tools import tools
from dev.db import Database
from discord.ext.commands import Context

class Example(commands.Cog):
    def __init__(self,client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Example extension ready. ')

def setup(client: commands.Bot):
    client.add_cog(Example(client))