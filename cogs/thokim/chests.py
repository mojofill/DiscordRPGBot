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
        print('Chests extension ready. ')
    
    async def cog_command_error(self,ctx,error):
        if isinstance(error,commands.CheckFailure):
            pass
                
        else:
            raise error
    
    @commands.command()
    async def open(self, ctx: commands.Context, chest_type: str):
        user = ctx.author

        user_data = Database.getStorageData(user)

        chests = user_data["chests"]
        
        if chests["unclaimed chests"][chest_type] == 0:
          await ctx.send('You do not have that chest type!')
          return
        
        # types of chests - common, uncommon, epic, rare, mythical, and legendary

        chest_dict = {
            "common":{
                "shards":{
                    "chance":[1,25],
                    "amount":[3,20]
                },
                "experience":{
                    "chance":[26,50],
                    "amount":[10,30]
                }
            },
            "uncommon":{
                "shards":{
                    "chance":[1,25],
                    "amount":[10,25]
                },
                "experience":{
                    "chance":[25,50],
                    "amount":[15,40]
                }
            },
            "epic":{
                "shards":{
                    "chance":[1,25],
                    "amount":[20,50]
                },
                "experience":{
                    "chance":[25,50],
                    "amount":[30,60]
                }
            },
            "rare":{
                "shards":{
                    "chance":[1,25],
                    "amount":[15,30]
                },
                "experience":{
                    "chance":[25,50],
                    "amount":[20,45]
                },
            },
            "mythical":{
                "shards":{
                    "chance":[1,25],
                    "amount":[90,130]
                },
                "experience":{
                    "chance":[25,50],
                    "amount":[80,200]
                },
            },
            "legendary":{
                "pet eggs":['dragon','pegasus','phoenix','giant']
            }
        }

        if chest_type == 'legendary':
            try:
                farm = user_data["farm"]
            
            except KeyError:
                pass

            pet_choices = ['dragon','pegasus','phoenix','giant']
            egg = random.choice(pet_choices)

            hatch_time = {
                "dragon":86400,
                "pegasus":432000,
                "phoenix":604800,
            }

            farm["barn"][egg] = {
                "hatch time":hatch_time[egg],
            }
            
            await ctx.send(f'You got a {egg} egg {user.mention}!')
            return

        num = random.randint(1,100)

        reward = None

        for reward_ in chest_dict[chest_type]:
            chance = chest_dict[chest_type][reward_]["chance"]
            if num in range(chance[0],chance[1]):
                reward = reward_

        msg = None

        await ctx.send(f'This is your reward, {reward}')
        
        if reward == 'potion':
            potion_types = ['mining speed','item value','wagon size','damage increase','damage reduce','energy efficiency']
            
            potion_type = random.choice(potion_types)
            
            potion_stats = tools.get_potion_value_stats(potion_type,chests=True,potion_rarity=chest_type)

            boosts = user_data["boosts"]

            all_potion_ids = []

            for potion_id in boosts["local potions"]:
                all_potion_ids.append(potion_id)
            
            new_id = tools.get_rand_id(all_potion_ids)

            boosts["local potions"][new_id] = potion_stats
        
        elif reward == 'shards':
            value_list = chest_dict[chest_type]["shards"]["amount"]
            shards = random.randint(value_list[0],value_list[1])

            user_data["pets"]["shards"] += shards

            await ctx.send('you got shards')

            msg = f"{user.mention} you got {shards} shards."
        
        else:
            value_list = chest_dict[chest_type]["experience"]["amount"]
            xp = random.randint(value_list[0],value_list[1])

            user_data["game"]["experience"] += xp

            msg = f"{user.mention} you got {xp} experience."

        await ctx.send(msg)

        # return to this

def setup(client):
    client.add_cog(Chests(client))