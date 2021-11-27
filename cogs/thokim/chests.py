from dev.db import Database
import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.api import db

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
        # all_rewards = 
        # {
        #     category:{
        #         reward:int
        #     }
        # }

        def getRewardType(reward_name: str) -> str:
            """Takes in `reward_name` and returns a string representing the type of reward it is - `sword` would return `weapon`"""

            # TODO: finish this

            items = {
                # weapons
                    # basic weapons
                    "mogo club":"weapons",
                    "mogo spear":"weapons",
                    "mogo bat":"weapons",
                    "wooden bat":"weapons",
                    "wooden spiked bat":"weapons",
                    "wooden spear":"weapons",
                    "knight's broadsword":"weapons",
                    "knight's claymore":"weapons",
                    "steel spear":"weapons",
                    "steel sword":"weapons",
                    "steel mace":"weapons",
                    "stick":"weapons",

                    # elemental weapons
                        # ranged - staffs
                        "lightning staff":"weapons",
                        "blaze staff":"weapons",
                        "ice staff":"weapons",

                    "flame sword":"weapons",
                    "ice sword":"weapons",

                    # ranged weapons

                # bows
                    "mogo bow":"bow",
                
                # valuables
                    "emeralds":"valuables",
                    "ruby":"valuables",
                    "sapphire":"valuables",
                    "topaz":"valuables",
                    "opal":"valuables",
                    "diamond":"valuables",
                
                # armor

            }

            return items[reward_name]

        await ctx.send(chests)

        for chest_type in chests["chests"]:
            for chest_data in chests["chests"][chest_type]:
                # chest_data = all rewards in each chest

                for reward in chest_data:
                    reward_type = getRewardType(reward_name=reward)

                    if reward_type not in all_rewards:
                        all_rewards[reward_type] = {reward:1}
                    
                    else:
                        all_rewards[reward_type][reward] += 1
                    
        for reward_type in all_rewards:
            await tools.addItems(ctx, reward_type, all_rewards[reward_type]) # dumps all rewards into player backpack and send a message on it

def setup(client: commands.Bot):
    client.add_cog(Chests(client))