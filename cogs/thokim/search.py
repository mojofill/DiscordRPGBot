import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Searching(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Searching extension ready. ')
    
    def cog_check(self,ctx):
        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
        if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
            return False
        return True
    
    @commands.command()
    async def search(self,ctx):
        user = ctx.author
        
        # choose something between 1 and 10,000

        searchable_locations = ['jungle','mountian','ocean','grasslands']

        gdata = db.game.find_one({"_id":user.id})

        if gdata["location"] not in searchable_locations:
            await ctx.send('Location not in searchable locations, redirecting you to default place to search jungle...')

        if gdata["default transport"] == 'walking':
            await tools.walkuser(ctx,user,'jungle')
        
        else:
            db.game.update_one({"_id":user.id},{"$set":{"location":"jungle"}})

            msg = tools.travel(user,"jungle")

            await ctx.send(msg)

            return

        items_to_place = {
            "jungle":{
                "aquarooms":[]
            }
        }
    
  
def setup(client):
    client.add_cog(Searching(client))