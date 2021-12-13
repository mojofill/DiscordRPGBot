from typing import Literal
from dev.db import Database
import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.items import ItemsTool

class Chests(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Chests extension ready.')
    
    @commands.command()
    async def open(self, ctx: commands.Context):
        user = ctx.author

        user_data = Database.getStorageData(user)

        chests = user_data["chests"]
        
        # chests = {
        #     list of dicts - dicts contain chests data - when player uses .open, all chests in each category are opened
        # 
        #     "monster camp chests":list,
        #     "temple chests":list,
        #     "treasure chests":list,
        #     "wooden chests":list
        #
        # }
        
        all_rewards = {}
        # all_rewards = {
        #     (str) reward type:{
        #         (str) reward:int
        #     }
        #
        # E.G.
        #     "valuables":{
        #         "opal":5
        #     }            
        # }

        for chest_data in chests["chests"]:
            
            # chest_data = {
            #     "type":str,
            #     "items":dict
            # }

            for reward in chest_data["items"]:
                reward_type = ItemsTool.getRewardType(reward_name=reward)

                if reward_type not in all_rewards:
                    all_rewards[reward_type] = {reward:1}
                
                else:
                    all_rewards[reward_type][reward] += 1
        
        chests["chests"] = [] # clear data

        import json

        await ctx.send(json.dumps(all_rewards, indent=4))

        for reward_type in all_rewards:
            rewards: dict = all_rewards[reward_type]

            await tools.addGrabbableItems(ctx, reward_type, rewards) # dumps all rewards into player backpack and send a message on it

def setup(client: commands.Bot):
    client.add_cog(Chests(client))