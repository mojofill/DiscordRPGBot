import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Falcon(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Falcon extension ready. ')
    
    def cog_check(self,ctx):
        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
        if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
            return False
        return True

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
                
                elif potion_type == 'damage reduce': # while this seems counter-productive and harmful, damage reduce potions reduce the INCOMING damage from outside sources
                    for armor_piece in falcon["armor"]:
                        falcon["armor"][armor_piece]["damage reduce"] += potion_value # the damage reduce is calcuated by the percentage taken away from the damage, not the final percentage of the damage that is coming

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

                loop = tools.get_potion_duration_subtract_loop(user,new_potion_id,falcon=True)

                loop.start()

        else:
            pass

# remember that users can hunt anytime, anywhere
async def hunt(ctx: commands.Context):
    # give legendaries (e.g. dragon eggs), mythicals (e.g. griffins and pegasuses), and normals (e.g. cattle lol) 

    # 1 - 45: normal
    # 46 - 49: mythical
    # 50: legendary
    # 56 - 100: no pets gained, just exp and hunger satiated

    user = ctx.author
    
    gdata = db.game.find_one({"_id":user.id})

    aichoice = random.randint(1,1000)

    random_pet = None # the pet that you get depending on the pet_type

    pet_type = None # which type of pet is it, normal, legendary and mythical

    if aichoice in range(205,1000):
        await ctx.send('Your falcon didnt get any pets but gained some exp and replenished amount hunger')
        return
        
    await ctx.send(aichoice)

    if aichoice in range(1,150):
        # normal
        await ctx.send('You got a normal')
        normal_pets = [
            'wolf', # decrease chance of getting robbed
            # add more to this
            'chicken', # mining speed
            'horse', # increase wagon size
            'snake', # mining speed
        ]

        pet_type = 'normal'

        random_pet = random.choice(normal_pets)

    elif aichoice in range(150,200):
        await ctx.send('You got a mythical')
        mythical_pets = [
            'griffin',
            'centaur',
            'sea serpent', 
            'sphinx', # critical hit chance higher
            'cerebus', # terrorize, silence and shock people for a duration
        ]

        pet_type = 'mythical'

        random_pet = random.choice(mythical_pets)

    elif aichoice in range(200,205):
        # legendary

        await ctx.send('You got a legendary.')

        legendary_pets = [
            'dragon', # hit multiplied by 2, more depending on upgraded dragons. Burns people also.
            'pegasus', # glory and higher dodge chance
            'phoenix', # THE BEST LEGENDARY!! has a 5 day cooldown, but allows you to escape any fight unscathed and rebound the attack, basically doing what the other guy did, but back at him. ALSO, it gives passive healing after 2 minutes of getting attacked and doing nothing. 
            'giant', # heightens mining speed, multiplying it by 4 for 5 minutes, and cooldown 6 hours
        ]

        pet_type = 'legendary'

        random_pet = random.choice(legendary_pets)

    # update these below later
    
    mining_speed_pets = {
        "wolf":0.1,
        "chicken":0.1,
        "goose":0.1,
        "horse":0.1,
        "snake":0.1
    }

    wagon_size_pets = {
        "elephant":0.1,
        "crocodile":0.1,
        "monkey":0.1,
        "horse":0.1
    }

    value_increase_pets = { 
        "lion":0.1,
        "tiger":0.1
    }

    already_updated = False

    await ctx.send(f'{user.mention} This is the pet you got {random_pet}. Processing pet benefits...')

    mines = db.mines.find_one({"_id":user.id})

    if random_pet in mining_speed_pets:
        value = mining_speed_pets[random_pet] # this is the percentage that we need for mining speed
        db.mines.update_one({"_id":user.id},{"$inc":{"multipliers.mining speed":value}}) # inside the multipliers dict are all the multipliers for all 3 aspects of mining - mining speed, wagon size and item value. Using the mining speed multipler may be confusing, so listen up.
        # The mining speed multiplier is used on the DROPS of a item. The drop of an item bascially means the number of items it drops per second. For example, an item that has a drop of 3 means it drops 3 items every second. Or, an item has a drop of 3.7. Do not panic, this does not mean suddenly the user has a decimal of item. This is not possible; bot will round the item down and calculate from there on. 
        # The reason why the COMPUTER will have a decimal of an item is because the user is still in the PROCESS of mining that item. Specifically, imagine this. After one second, you have mined 4 items, and you are in the process of mining another block. Say you are 50% of the way done, or 0.5 of the item. Obviously, in your wagon you still have 4 blocks, because you are still mining the fifth block. But if we note in our computer that the user has 4 blocks after 1 second, imagine another second has passed. If we calculate by 4 items/s, as noted in the computer, then at 2 seconds the user has 8 items. However, that's not true. After 1 second, the user has 4 blocks AND IS IN THE PROCESS OF MINING A 5TH ITEM. So after 2 seconds, the user should have 9 items. 
        
        # User's mining rate: 4.5 i/s
        
        # After 2 seconds:
        # Without decimals (rounded down) - 4 + 4 = 8   (INACCURATE)
        # With decimals - 4.5 + 4.5 = 9                 (ACCURATE)

        # this should clear up any confusion 
        # (if this looks weird to anyone im not explaining it to other people, im explaining it to myself when i come back later to review code)

        # multiply the drop key by the mining speed multiplier in every item in wagon items
        for item in mines["wagon items"]:
            mines["wagon items"][item]["drops"] *= mines["multipliers"]["mining speed"] # check comment above

        # finally update wagon items
        db.mines.update_one({"_id":user.id},{"$set":{"wagon items":mines["wagon items"]}})

        speed = mines["mining speed"]

        # set the mining speed as the original one times 1 + the percentage. Or rather, multiply the mining speed by 100 (plus the percenatge)
        db.mines.update_one({"_id":user.id},{"$set":{"mining speed":speed*(1+value)}}) 

    elif random_pet in wagon_size_pets:
        value = wagon_size_pets[random_pet]
        db.mines.update_one({"_id":user.id},{"$inc":{"multipliers.wagon size":value}})

        size = int(value * mines["wagon limit"])

        db.mines.update_one({"_id":user.id},{"$inc":{"wagon limt":size}})
        
    elif random_pet in value_increase_pets:
        value = value_increase_pets[random_pet]
        db.mines.update_one({"_id":user.id},{"$inc":{"multipliers.item value":value}})
    
# these are the pets that have special stuff - you need to do specific if statements for all of these

# all passives i have to right now, not at the bottom to massive update, because all passives are unique

    else:
        already_updated = True
        gcommands = db.special_commands.find_one({"_id":user.id})
        pets = db.pets.find_one({"_id":user.id})

        # legendary pets from here
        if random_pet == 'dragon':
            gcommands["available commands"]["dragon"] = True

            db.special_commands.update_one({"_id":user.id},{"$set":{"available commands":gcommands["available"]}})

            pets["legendary pets"]["dragon"] = {
            "commands":{
                "rage":{
                "duration":180,
                "cooldown":3600
                },
                "burn":{
                "duration":30,
                "cooldown":3600
                },
                "richboi":{
                "duration":300,
                "cooldown":1800
                }
            },
            "level":1
            }

            db.pets.update_one({"_id":user.id},{"$set":{"legendary pets":pets["legendary"]}})
    
        elif random_pet == 'pegasus':
            gcommands["available commands"]["pegasus"] = True

            pets["legendary pets"]["pegasus"] = {
            "commands":{
                "carry":{
                "duration":300,
                "cooldown":300
                },
                "exhilirate":{
                "duration":None,
                "cooldown":1800
                }
            },
            "level":1,
            "dodge":{
                "value":30
            }
            }

            gdata["unlocked dodge"] = True
            gdata["dodge"] = 30

            # pegasus allows you to dodge stuff

            db.game.update_one({"_id":user.id},{"$inc":{"rob":1}})
            db.game.update_one({"_id":user.id},{"$set":{"dodge":30}})
        
        elif random_pet == 'phoenix':
            gcommands["available commands"]["phoenix"][commands] = True

            pets["legendary pets"]["phoenix"] = {
            "commands":{
                "escape":{
                "duration":None,
                "cooldown":1440
                },
                "revive":{
                "duration":60,
                "cooldown":1209600 # 2 weeks
                }
            },
            "level":1,
            "heal":{
                "heal per second":15,
                "time wait":30 # 30 seconds
            }
            }
        
        elif random_pet == 'giant':
            gcommands["available commands"]["giant"] = True

            pets["legendary pets"]["giant"] = {
            "commands":{
                "stomp":{
                "duration":300,
                "cooldown":3600
                }
            },
            "level":1
            }
    
        # mythical pets from here
        elif random_pet == 'griffin':
            pets["mythical pets"]["griffin"] = {
            "guard":{
                "damage":100,
                "health":100
            },
            "level":1
            }
        
        # all upgrades are decreased by 0.0035, or 0.35 percent
        elif random_pet == 'centaur': # pickaxe upgrade
            pets["mythical pets"]["centaur"] = {
            "level":1
            }
        
        elif random_pet == 'sea serpent': # wagon upgrade
            pets["mythical pets"]["sea serpent"] = {
            "level":1
            }
        
        elif random_pet == 'nymph': # pet upgrade
            pets["mythical pets"]["nymph"] = {
            "level":1
            }
        
        elif random_pet == 'cerebus':
            gcommands["available commands"]["cerebus"] = True
    
            pets["mythical pets"]["cerebus"] = {
            "level":1,
            "commands":{
                "terrorize":{
                "cooldown":900
                }
            }
            }
    
    db.special_commands.update_one({"_id":user.id},{"$set":{"available commands":gcommands["available commands"]}})

    db.pets.update_one({"_id":user.id},{"$set":{f"{pet_type} pets":pets[f"{pet_type} pets"]}})

    if not already_updated:
        Pets = db.pets.find_one({"_id":user.id})
        Pets["normal pets"][random_pet] = {
            "level":1,
            "value":0.1
        }

    db.pets.update_one({"_id":user.id},{"$set":{f"{pet_type} pets":Pets[f"{pet_type} pets"]}})

    await ctx.send(f'You got a {random_pet}')

    await tools.all_quest_and_chest_actions(ctx,"hunt",user)

def setup(client):
    client.add_cog(Falcon(client))