import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Mines(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Mines extension loaded.')
    
    def cog_check(self,ctx):
        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
        if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
            return False
        return True

    @commands.command(aliases=['s'])
    @commands.cooldown(1,1,commands.BucketType.user)
    async def sell(self,ctx):
        bp = db.backpack
        mines = db.mines
        user = ctx.author
        
        gdata = db.game.find_one({"_id":user.id})
        
        if gdata["location"] != "mineshaft":
            return_msg = tools.travel(user,"mineshaft")

            if return_msg != 'walking':
                await ctx.send(return_msg)
            
            else:
                await tools.walkuser(ctx,user,"mineshaft")

        msg = ''

        m_info = mines.find_one({"_id":user.id})

        # all of the user's items' price added together
        items_total_price = 0

        # total number of items the user sold
        total_items = 0

        for item in m_info["wagon items"]:
            total = m_info["wagon items"][item]["total"]
            amount = m_info["wagon items"][item]["amount"]
            value = m_info["wagon items"][item]["value"]

            msg += f'{item.title()} x{amount} | **{total}**\n'

        if m_info["keep adding"] == False:
            mines.update_one({"_id":user.id},{"$set":{"keep adding":True}})
        
        items_total_price += amount*value
        total_items += 1
        
        m_info["wagon items"][item]["total"] = 0
        m_info["wagon items"][item]["amount"] = 0
        m_info["all items"] = 0
        
        bp.update_one({"_id":user.id},{"$inc":{"gold nuggets":items_total_price}})

        mines.update_one({"_id":user.id},{"$set":{"wagon items":m_info["wagon items"]}})

        mines.update_one({"_id":user.id},{"$set":{"all items":0}})

        msg += f'\nThis is your total {items_total_price}'

        em = discord.Embed(color=tools.lime,title="Test")

        em.add_field(name=f"Sold {total_items} items from your backpack.",value=msg)  

        bp_ = bp.find_one({"_id":user.id})

        em.add_field(name="\u200b",value=f"""
        **Total: {items_total_price}** 
        **You now have {bp_["gold nuggets"]} nuggets**
        """,inline=False)
        
        await ctx.send(embed=em)

        await tools.all_quest_and_chest_actions(ctx,"sell",user)
    
    @sell.error
    async def mining_error(self,ctx,error):
        if isinstance(error,commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention} mining takes a bit. Chill down and wait a few seconds.')
        
        else:
            raise error

        
    @commands.command()
    async def wagon(self,ctx):
        user = ctx.author
            
        mines = db.mines.find_one({"_id":user.id})

        em = discord.Embed(color=tools.lime)
        em.set_author(name=user,icon_url=user.avatar_url)

        # diving what the user has over what the limit is, multiply it by 10 to get the percentage, and call int on it to round down  
        percentage_full = int((mines["all items"]/mines["wagon size"]) * 100)

        em.add_field(name='Wagon',value=f"""
        **Level** `[{mines["wagon"]["level"]}]`
        {mines["all items"]}/{mines["wagon size"]} items
        **{percentage_full}**% full.
        """)

        em.add_field(name="\u200b",value="Upgrade your backpack with `.up wagon`",inline=False)

        em.set_footer(text=self.client.user,icon_url=self.client.user.avatar_url)
        
        await ctx.send(embed=em)

  
def setup(client):
    client.add_cog(Mines(client))