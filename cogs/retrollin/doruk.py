import discord,time
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Doruk(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Retrollin - Doruk extension ready. ')

def setup(client):
    client.add_cog(Doruk(client))