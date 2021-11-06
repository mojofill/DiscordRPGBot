import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Vault(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Vault extension loaded.')
    
    @commands.command()
    async def deposit(self,ctx,amount=None):
        user = ctx.author

        if amount == None:
            await ctx.send('Amount argument missing, please try again. ')
            return
        
        try:
            amount = int(amount)
        except:
            await ctx.send('Invalid amount argument, please pass in an integer. ')
            return
        
        bp = db.backpack
        econ = db.economy

        
        try:
            amount = int(amount)
        except:
            await ctx.send('Invalid amount argument, please try again. ')
            return

        bp_user = bp.find_one({"_id":user.id})

        if amount > bp_user["gold bars"]:
            await ctx.send(f'{user.mention} your backpack does not contain {amount} gold <:emerald:827000475768324126>. ')
            return

        bp.update_one({"_id":user.id},{"$inc":{"gold bars":-1*amount}})

        econ.update_one({"_id":user.id},{"$inc":{"vault":amount}})

        await ctx.send(f'Taken {amount} from your backpack and added {amount} to your vault')

    @commands.command()
    async def withdraw(self,ctx,amount=None):
        if amount == None:
            await ctx.send('Amount argument missing, please try again. ')
            return
        
        try:
            amount = int(amount)
        except:
            await ctx.send('Invalid amount argument, please pass in an integer. ')
            return
        
        bp = db.backpack
        econ = db.economy

        user = ctx.author
            
        try:
            amount = int(amount)
        except:
            await ctx.send('Invalid amount argument, please try again. ')
            return

        user = ctx.author

        bp_user = bp.find_one({"_id":user.id})

        if amount > bp_user["gold bars"]:
            await ctx.send(f'{user.mention} your backpack does not contain {amount} gold <:emerald:827000475768324126>. ')
            return

        bp.update_one({"_id":user.id},{"$inc":{"gold bars":-1*amount}})

        econ.update_one({"_id":user.id},{"$inc":{"vault":amount}})

        await ctx.send(f'Taken {amount} from your backpack and added {amount} to your vault')

def setup(client):
  client.add_cog(Vault(client))