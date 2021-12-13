import discord
from discord.ext import commands
from dev.tools import tools
from dev.items import ItemsTool
from dev.db import Database
from dev.chests import ChestsTool

class Town(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Town extension ready.')
    
    @commands.command()
    async def collect(self, ctx: commands.Context):
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)

        adventure_hub = user_data["adventure hub"]

        xp_gain = adventure_hub["xp gain"]

        if not xp_gain > 0:
            await ctx.send('Nothing to collect ❌')

            return

        gdata = user_data["game"]
        bp = user_data["backpack"]
        items = adventure_hub["items"]
        
        # items = {
        #     "weapons":{
        #         "mogo spear":2
        #     },
        #     "bows":{},
        #     "valuables":{},
        #     "enhancement crystals":int
        # }

        for item_type in items:
            if item_type == 'weapons' or item_type == 'bow':
                await tools.addEquipments(ctx, items[item_type])
            
            elif item_type == 'valuables':
                await tools.addValuables(ctx, items[item_type])
            
            elif item_type == 'enhancement crystals':
                amount = items[item_type]

                bp["enhancement crystals"] += amount

                await ctx.send(f"Added `{amount}` **enhancement ores**.")
    
        gdata["xp"] += xp_gain

        await ctx.send(
            f"""
            Collected `{xp_gain}` **XP**.
            """
        )

def setup(client: commands.Bot):
    client.add_cog(Town(client))