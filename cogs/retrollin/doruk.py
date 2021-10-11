import discord,time
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Doruk(commands.Cog):
    def __init__(self,client):
        self.client = client

    async def cog_check(self,ctx):
        user = ctx.author

        at_location = tools.user_at_required_location(user,"fortress of doruk")
        at_realm = tools.user_at_required_realm(user,"retrollin")

        if at_location and at_realm:
            return True
        
        return False
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Retrollin - Doruk extension ready. ')

def setup(client):
    client.add_cog(Doruk(client))