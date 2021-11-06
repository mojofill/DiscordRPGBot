import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Quests(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Quests extension ready. ')

    @commands.command(name='quests',aliases=['quest,','qt'])
    async def _quests(self,ctx):
        user = ctx.author
        
        if not tools.user_at_required_location(user,"pub"):
            res = tools.travel(user,"pub")

            if res == "walking":
                await tools.walkuser(ctx,user,"pub")

            else:
                await ctx.send(res)
        
        quests = db.quests.find_one({"_id":user.id})
        msg = 'This is all your quests:\n'
        for quest_id in quests["quests"]:
            name = quests["quests"][quest_id]["name"]
            progress = quests["quests"][quest_id]["progress"]
            msg += f"{name} -> Progress: {progress}\n"

        await ctx.send(msg)

  
def setup(client):
    client.add_cog(Quests(client))