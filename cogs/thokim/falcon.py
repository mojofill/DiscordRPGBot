import discord,random
from discord.ext import commands, tasks
from dev.tools import tools
from dev.api import db

class Falcon(commands.Cog):
    def __init__(self,client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Falcon extension ready. ')

    @commands.command()
    async def feed(self,ctx:commands.Context,food:str):
        user = ctx.author
        
        if food.isdigit(): # this means the user has entered a number, meaning they want to feed his or her falcon a potion - number is the potion id
            potion_id = food # this makes it obvious what the bot is dealing with right now

            falcon_boosts = db.boosts.find_one({"_id":user.id},{"falcon":False})

            if potion_id not in falcon_boosts["local potions"]:
                await ctx.send(f'{user.mention} you do not have a potion with ID `{potion_id}` in your backpack - please enter `.potions` to see all available potions stored in your backpack.')
                return
            
            potion_type = falcon_boosts["local potions"][potion_id]["type"]

            unfeedable_potions = ['mining speed','wagon size','item price']

            if potion_type in unfeedable_potions:
                await ctx.send(f'{user.mention} You cannot feed {potion_type} to your falcon!')
                return
            
            falcon = db.falcon.find_one({"_id":user.id})

            if potion_type != 'luck':
                potion_value =falcon_boosts["local potions"][potion_id]["value"]
            
                if potion_type == 'damage increase':
                    for ability in falcon["abilities"]:
                        falcon["abilities"][ability]['damage'] *= (1 - potion_value)
                    
                    db.falcon.update_one({"_id":user.id},{"$set":{"abilities":falcon["abilities"]}})
                
                elif potion_type == 'protection': # while this seems counter-productive and harmful, protection potions reduce the INCOMING damage from outside sources
                    for armor_piece in falcon["armor"]:
                        falcon["armor"][armor_piece]["protection"] += potion_value # the protection is calcuated by the percentage taken away from the damage, not the final percentage of the damage that is coming

                    db.falcon.update_one({"_id":user.id},{"$set":{f"armor":falcon["armor"]}})

                    await ctx.send(f'{user.mention} upgraded {falcon["name"]}\'s armor - increased the damage reduction by {potion_value*10}%. ')
                
                elif potion_type == 'energy efficiency':
                    if falcon["energy is negatively affected"]:
                        # when falcon consumes a energy efficiency potion all harmful effects on the falcon's energy is canceled
                        falcon["energy gain time"] = falcon["base energy gain time"]

                        await ctx.send(f'{falcon["name"]}\'s energy is reverted back to normal from the potion, after being affected by an enemy falcon.')
            
                    falcon["energy gain time"] -= potion_value

                    potion_rarity = falcon_boosts["local potions"][potion_id]["rarity"] # finish this and the message below

                    await ctx.send(f'{falcon["name"]} has drank an Energy Efficiency potion (`rarity`=**{potion_rarity}**)')
            
            else: # this means that the potion type is luck
                """
                    If the potion type is luck, then that means the falcon has a better chance in hunting for pets and critical hits.

                    Important note - you cannot stack luck, unlike other potions. By "stacking", think like this. You take, say, a mining speed potion for 10 minutes, with mining speed x2. After 3 minutes, you take ANOTHER mining speed potion, this time speed x3, for 5 minutes. However, after the 5 minutes, your mining speed is reverted back to what is was before - mining speed x2. If you take mining speed x2 and x3, then you have, in total, speed x6. Pretty stacked IMO.
                """

                for ability in falcon["abilties"]:
                    try:
                        """Upgrade critical chances in ability"""
                        # the way we update this 

                        og_sample_size = falcon["abilities"][ability]["chance"]["sample size"]
                        og_hit = falcon["abilities"][ability]["critical"]["chance"]["hit range"]
                        
                        falcon["abilities"][ability]["critical"]["chance"]["sample size"] = 100

                        falcon_value = falcon_boosts["local potions"][potion_id]["falcon value"]

                        falcon["abilities"][ability]["critical"]["chance"]["hit range"] = [0,falcon_value*10]

                        # i need to have a revert nested dictionary because i need to be able to return to the previous stats before potion consumption
                        falcon["abilities"][ability]["revert"] = {
                            "sample size":og_sample_size,
                            "hit range":og_hit
                        }
                    
                    except KeyError:
                        """Ability has no critical chance attribute, so we don't need to do anything."""
                        pass
                    
                # set up the potion duration loop
                new_potion_id = tools.get_rand_id()

                loop: tasks.Loop = tools.get_potion_duration_subtract_loop(user,new_potion_id,falcon=True)

                loop.start()

        else:
            pass

def setup(client: commands.Bot):
    client.add_cog(Falcon(client))