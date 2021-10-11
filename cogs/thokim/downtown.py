import discord,random,asyncio
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Downtown(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Downtown extension ready. ')
    
    def cog_check(self,ctx):
        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
        if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
            return False
        return True
    
    async def cog_command_error(self,ctx,error):
        if isinstance(error,commands.CheckFailure):
            pass
                
        else:
            raise error

    @commands.command(aliases=['cf'])
    async def coinflip(self,ctx,bet=None,amount=None):
        user = ctx.author
        
        gdata = db.game.find_one({"_id":user.id})

        if gdata["location"] != "downtown":
            msg = tools.travel(user,"downtown")

            if msg == 'walking':
                db.game.update_one({"_id":user.id},{"$set":{"status":"walking"}})
                await tools.walkuser(ctx,user,"downtown")
                db.game.update_one({"_id":user.id},{"$set":{"location":"downtown"}})
                db.game.update_one({"_id":user.id},{"$set":{"status":"stationary"}})

        backpack = db.backpack
        choices = ['heads','tails','h','t']

        if bet == None:
            await ctx.send('Please put in a argument for bet. For example `.coinflip heads 1`.')
            return
            
        if amount == None:
            await ctx.send('Please put in a argument for amount. For example `.coinflip heads 1`.')
        
        try:
            amount = int(amount)
        except:
            await ctx.send('Invalid argument for amount. Please put in an integer.')
            return
        
        if bet not in choices:
            await ctx.send('Invalid argument for bet. Please put in a valid argument, `heads` or `tails`.')
            return

        ai_choice = random.choice(choices)

        bet_dict = {
            "h":"heads",
            "heads":"heads",
            "t":"tails",
            "tails":"tails"
        }

        bet = bet_dict[bet]

        if ai_choice == bet:
            await ctx.send(f'You have won, earning {amount} plus an extra {amount}.')
            backpack.update_one({"_id":user.id},{"$inc":{"gold bars":2*amount}})
            
        else:
            await ctx.send(f'You have lost, losing {amount}.')
            backpack.update_one({"_id":user.id},{"$inc":{"gold bars":-1*amount}})
            
            command_quests = tools.quests_with_commands_list('coinflip',user)

        await tools.all_quest_and_chest_actions(ctx,"coinflip",user)

  
def setup(client):
  client.add_cog(Downtown(client))