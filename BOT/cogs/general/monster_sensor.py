import discord
from discord.ext import commands, tasks
from dev.tools import tools
from dev.db import Database

class Example(commands.Cog):
    def __init__(self,client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Example extension ready. ')
    
    @commands.command(aliases=['ms','msensor'])
    async def monstersensor(self, ctx: commands.Context):
        user = ctx.author
        
        user_data = Database.getStorageData(user)

        monster_data = user_data["monsters"]
    
    @commands.command()
    async def _(self, ctx: commands.Context):
        @tasks.loop(seconds=0.5)
        async def loop():
            pass

        loop.start()

        await ctx.send('code works')

def setup(client: commands.Bot):
    client.add_cog(Example(client))