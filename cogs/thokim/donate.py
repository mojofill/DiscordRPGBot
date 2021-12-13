import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db


class Donate(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Donatation extension ready. ')

    # remember that you can get one time recievement of credits from paying through paypal. gotta make it unfair so people choose patron

    # something like 1 dollar for 1 credit

    @commands.command()
    async def knight(self,ctx):
        user = ctx.author

        em = discord.Embed(color=discord.Color.dark_green())

        # do stuff here

        donor_info = {
        "_id":user.id,
        "level":""
        }
        
        db.patreon.insert_one(donor_info)
        db.credits.insert_one({"_id":user.id,"credits":0})


    @commands.command()
    async def credits(self,ctx):
        pass
  
    # remember there are monthly credits and you can get one-time recieved credits by donating through paypal

  
def setup(client):
    client.add_cog(Donate(client))