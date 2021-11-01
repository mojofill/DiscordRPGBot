import discord
from discord.ext import commands
from dev.tools import tools
from dev.db import Database

class Test(commands.Cog):
    def __init__(self,client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Test extension ready. ')
    
    @commands.command()
    async def test(self, ctx: commands.Context):
        m: discord.Message = await ctx.send('Starting Message Listening Loop...')

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
        
        await m.edit('Loop Started.')

        while True:
            m: discord.Message = await self.client.wait_for('message', check=check)

    @commands.command(aliases=['print'])
    async def _print(self, ctx: commands.Context):
        await ctx.send('**TEST MESSAGE**')

def setup(client: commands.Bot):
    client.add_cog(Test(client))