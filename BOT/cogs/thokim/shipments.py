import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Shipments(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Shipments extension ready. ')
    
    def cog_check(self,ctx):
        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
        if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
            return False
        return True
    
    @commands.command()
    async def hourly(self,ctx):
        user = ctx.author
            
        chests = db.chests.find_one({"_id":user.id})

        if not chests["unclaimed shipments"]["hourly"]:
            await ctx.send(f'{user.mention} Your hourly shipment has not arrived yet!')
            return

        num = random.randint(1,100)
        chest_type = None

        if num in range(0,48):
            chest_type = 'uncommon'

        elif num in range(48,100):
            chest_type = 'common'

        db.chests.update_one({"_id":user.id},{"$inc":{f"chests.{chest_type}":1}})

        db.chests.update_one({"_id":user.id},{"$set":{"unclaimed shipments.hourly":False}})
    
    @commands.command()
    async def daily(self,ctx):
        user = ctx.author
        
        chests = db.chests.find_one({"_id":user.id})

        if not chests["unclaimed shipments"]["daily"]:
            await ctx.send(f'{user.mention} Your hourly shipment has not arrived yet!')
            return

        chest_type = None

        num = random.randint(1,100)

        if num in range(0,40):
            chest_type = 'rare'
        
        elif num in range(40,100):
            chest_type = 'epic'

        db.chests.update_one({"_id":user.id},{"$inc":{f"chests.{chest_type}":1}})

        db.chests.update_one({"_id":user.id},{"$set":{"unclaimed shipments.daily":False}})

        await ctx.send(f'You recieved a {chest_type} chest. ')
    
    @commands.command()
    async def weekly(self,ctx):
        user = ctx.author
        
        chests = db.chests.find_one({"_id":user.id})

        if not chests["unclaimed shipments"]["weekly"]:
            await ctx.send(f'{user.mention} Your hourly shipment has not arrived yet!')
            return

        chest_type = None
        num = random.randint(1,12)

        if num == 1:
            chest_type = 'legendary'
        else:
            chest_type = 'mythical'

        db.chests.update_one({"_id":user.id},{"$inc":{f"chests.{chest_type}":1}})

        db.chests.update_one({"_id":user.id},{"$set":{"unclaimed shipments.weekly":False}})

        await ctx.send('You got a mythical chest.') 
    
def setup(client):
    client.add_cog(Shipments(client))