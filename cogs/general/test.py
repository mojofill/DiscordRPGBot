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
        user = ctx.author

        save = None

        def check(reaction: discord.Reaction, _user: discord.User):
            nonlocal save

            save = reaction.emoji

            return True

        m: discord.Message = await ctx.send('React to this message with 👍.')

        await m.add_reaction('👍')
        
        await self.client.wait_for("reaction_add", check=check)

        await ctx.send(save)

    @commands.command(aliases=['print'])
    async def _print(self, ctx: commands.Context):
        await ctx.send('**TEST MESSAGE**')

def setup(client: commands.Bot):
    client.add_cog(Test(client))