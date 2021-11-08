import discord
import random
import asyncio
import copy
from discord.ext import commands
from dev.tools import tools
from dev.api import db
from dev.db import Database

class Marketplace(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Market place extension ready. ')
    
    @commands.command(aliases=['market'])
    async def shop(self,ctx):
        em = discord.Embed(title='Trade Center',description='Trade gold bars for game items here!',color=tools.lime)
        em.add_field(name='Scrolls',value="Different kinds of scrolls you can use to enchant your weapons and armor.",inline=False)
    
        em.add_field(name="Haste",value="""
        `[1]` Haste **1**: 100 <:goldbar:847942259026558986>
        `[2]` Haste **2**: 200 <:goldbar:847942259026558986>
        `[3]` Haste **3**: 300 <:goldbar:847942259026558986>
        """)

        em.add_field(name="Protection",value="""
        `[4]` Protection **1**: 100 <:goldbar:847942259026558986>
        `[5]` Protection **2**: 200 <:goldbar:847942259026558986>
        `[6]` Protection **3**: 300 <:goldbar:847942259026558986>
        """)

        em.add_field(name="Sharpness",value="""
        `[7]` Sharpness **1**: 100 <:goldbar:847942259026558986>
        `[8]` Sharpness **2**: 200 <:goldbar:847942259026558986>
        `[9]` Sharpness **3**: 300 <:goldbar:847942259026558986>
        """,inline=False)

        em.add_field(name="Speed",value="""
        `[10]` Speed **1**: 100 <:goldbar:847942259026558986>
        `[11]` Speed **2**: 200 <:goldbar:847942259026558986>
        `[12]` Speed **3**: 300 <:goldbar:847942259026558986>
        """)

        """
        Different type of enchantments:
            Make your armor reduce more damage.
            Reduce damage directed at you (enchant with armor).
            Sharpness - Increase damage from you (enchant with weapons)
            Increase mining speed
            More storage (enchant with wagon)
            Faster walking 
            Knockout (make someone pass out and cant use any commands)
            Everlasting (increase durability on weapons and armor)
        """

        # make a table for the translation, converting all numbers to supscripted version
        SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

        # converts 1 to supscripted version
        supscript1 = '1'.translate(SUP)


        em.add_field(name='Food',value=f"""
        `[13]` **Apple**: Restores 20 HP
        `[14]` **Aquashrooms**: Restores 40 HP. When cooked restores more HP.**{supscript1}**
        `[15]` **Zoomshrooms**: Restores 20 HP. When cooked grants you faster movement.**{supscript1}**
        `[16]` **Strongshrooms**: Restores 25 HP. When cooked makes you stronger, dealing more damage from all sources.**{supscript1}**
        `[17]` **Toughshrooms**: Restores: 25 HP. When cooked makes you tougher, reducing incoming damage from all sources.**{supscript1}**
        
        """,inline=False)
        
        # convert 2 to supscripted version
        supscript2 = '2'.translate(SUP)

        em.add_field(name="Weapons",value=f"""
        `[18]` **Sword**: Deals 75 HP{supscript2}
        `[19]` **Spear**: Deals 100 HP{supscript2}
        `[20]` **Ax**: Deals 90 HP{supscript2}
        `[21]` **Club** Deals 90 HP{supscript2}
        """)

        em.add_field(name='\u200b',value=f"""
        {supscript1}: enter `.cook <food name> information` (or `.cook <food name> info`) for more information on that food when cooked.
        {supscript2}: enter `.weapons `<weapon name>` for more information on your weapon.
        """,inline=False)

        await ctx.send(embed=em)
    
    @commands.command()
    async def give(self, ctx: commands.Context):
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        bp: dict = user_data["backpack"]

        bp["gold bars"] += 100000000

        await ctx.send('ok')
    
    @commands.command()
    async def trade(self, ctx: commands.Context, item_id: int, amount=1):
        user = ctx.author
        
        try: # check if item_id is in fact an integer
            item_id = int(item_id)
        except:
            await ctx.send('Invalid item id argument, please enter an integer.')
            return
        
        try: # amount argument also needs to be an integer - can't have "poop" amount of swords
            amount = int(amount)
        except:
            await ctx.send('Invalid amount argument, please enter an integer.')
            return

        if item_id not in range(1,21): # change the number to total of items you are able to buy
            await ctx.send('Item id not found, please check the shop and try again.')
            return

        user_data = Database.getStorageData(user)
        
        gdata = user_data["game"]

        if gdata["location"] != "marketplace":
            if gdata["default transport"] == 'walking':
                await tools.walkuser(ctx, user, "marketplace")
            
            else:
                tools.travel(user,"marketplace")
        
        # TODO finish all the ranges of id in this
        # i should also reformat the code so different sections of the shop is given to the player
        item_type_dict = {
            (0,1):"gold bars",
            (1,12):"scrolls",
            (12,17):"food",
            (17,21):"weapons"
        }

        item_type = None

        # go through the dict's keys, which are all the item_id ranges for all items you are able to buy in the shop
        for item_range in item_type_dict:
            # check if the item id is in the range of iter variable
            if item_id in range(item_range[0],item_range[1]):
                # set the item_type as the the value of the key item_range in item_type_dict, as it is from a list of the item_type_dict keys
                item_type = item_type_dict[item_range]
        
        if item_type == None:
            await ctx.send(f'Invalid item id: `{item_id}` not found. Check `.shop` for more information on item ids and shop items.')
            return

        def too_expensive(total):
            if total > bp["gold bars"]:
                return True
        
            return False

        bp = user_data["backpack"]
        msg = None
        price = None

        # make if statements for which kind of item the user wants to buy and do stuff accordingly to the item

        if item_type == "gold bars":
            if amount > bp["gold nuggets"]:
                await ctx.send('That number exceeds your current balance of gold nuggets.')
                return
            
            gold_bars = amount//4

            # add to the user's gold bars
            bp["gold bars"] = gold_bars
            
            # subtract from the user's gold nuggets
            bp["gold nuggets"] -= 4 * gold_bars

            await ctx.send(f"Sucessfully forged **{gold_bars}** gold bars from **{4*gold_bars}**")

        elif item_type == "scroll":
            scroll_type = None # 3 different scroll types: efficiency, durability and speed

            if item_id in range(1,4):
                scroll_type = 'efficiency'

            elif item_id in range(4,7):
                scroll_type = 'durability'

            elif item_id in range(7,10):
                scroll_type = 'speed'

            upgrade_scrolls = {
                1:{
                    "name":"Mining I",
                    "price":1000000,
                    "value":0.3
                },
                2:{
                    "name":"Mining II",
                    "price":2000000,
                    "value":0.5
                },
                3:{
                    "name":"Mining III",
                    "price":3000000,
                    "value":0.5
                },
                4:{
                    "name":"Durability I",
                    "price":1000000,
                    "value":0.3
                },
                5:{
                    "name":"Durability II",
                    "price":2000000,
                    "value":0.5
                },
                6:{
                    "name":"Durability III",
                    "price":3000000,
                    "value":0.5
                },
                7:{
                    "name":"Efficiency I",
                    "price":1000000,
                    "value":0.1
                },
                8:{
                    "name":"Efficiency II",
                    "price":2000000,
                    "value":0.3
                },
                9:{
                    "name":"Efficiency III",
                    "price":3000000,
                    "value":0.5
                },
                10:{
                    "name":"Speed I",
                    "price":100000000,
                    "value":1
                },
                11:
                {
                    "name":"Speed II",
                    "price":200000000,
                    "value":2
                },
                12:{
                    "name":"Speed III",
                    "price":1000000000,
                    "value":3
                }
            }

            price = upgrade_scrolls[item_id]["price"]

            if too_expensive(price*amount): # as the name sounds, returns True if the user does not have enough money to buy the amount of items
                await ctx.send(f'You do not have enough money to buy {amount} of {upgrade_scrolls[item_id]["name"]} scrolls.')
                return

            for _ in range(amount):
                # get all the scroll ids from the user's scroll
                all_scroll_ids = list(bp["scrolls"].keys())
                choice_range = 30
                count = 0
            
                while True:
                    count += 1
                    next_scroll_id = random.randint(1,choice_range)

                    if next_scroll_id not in all_scroll_ids:
                        break
                    
                    else:
                        if count == choice_range: # this means the user has more than 30 scrolls, so we add 10 more to the random range, and RNG will soooner or later land on a number above 30, and give the user that scroll ID
                            choice_range += 10

                    await ctx.send(f'This is your next_scroll_id {next_scroll_id}')
                    
                    bp["scrolls"][next_scroll_id] = {
                        "type":scroll_type,
                        "name":upgrade_scrolls[item_id]["name"],
                        "value":upgrade_scrolls[item_id]["value"]
                    }

                    bp["gold bars"] -= amount * price

            msg = f'Successfully bought {upgrade_scrolls[item_id]["name"]} for {price * amount}'

        elif item_type == 'food':
            food_type = None
            # python only counts the number in the range if the number is equal to the first number, or within all the numbers to the second number. python does not count the second number, so if the item id is equal to 14, then the number is not in range.
            if item_id in range(13,14):
                food_type = 'other'

            elif item_id in range(14,18):
                food_type = 'mushrooms'
            
            # bro add more to the food
            
            if food_type == 'mushrooms':
                id_to_shroom = {
                    14:"aquashroom",
                    15:"zoomshroom",
                    16:"strongshroom",
                    17:"toughshroom"
                }

                shroom_price = {
                    "aquashroom":500000,
                    "zoomshroom":800000,
                    "strongshroom":800000,
                    "toughtshroom":800000
                }

                shroom = id_to_shroom[item_id]
                
                # set price of shroom
                price = shroom_price[shroom]

                res = too_expensive(price*amount)

                if res:
                    await ctx.send(f'You do not have enough gold bars to buy {amount} of {shroom}s.')
                    return

                while True:
                    try:
                        # find mushroom type and add the amount of mushrooms you bought to it
                        bp["food"]["mushrooms"][shroom] += amount
                        break
                    except:
                        bp["food"]["mushrooms"][shroom] = 0

            elif food_type == 'other':
                id_to_food = {
                13:"apple"
                }

                food_price = {
                "apple":5
                }

                food = id_to_food[item_id]
                
                # set price for food
                price = food_price[food]

                res = too_expensive(price*amount)

                if res:
                    await ctx.send(f'You do not have enough gold bars to buy {amount} of {food}s.')
                    return
                
                # loop to simply make the food category if it was not found
                while True:
                    try:
                        bp["food"]["other"][food] += amount
                        break
                    
                    except ValueError:
                        bp["food"]["other"][food] = 0
        
            msg = f'Bought amount of {food} for {price*amount} gold bars.'

        elif item_type == 'weapons':
            id_to_weapon = {
                18:"sword",
                19:"spear",
                20:"ax",
                21:"club"
            }

            weapon = id_to_weapon[item_id]

            weapon_price = {
                "sword":100,
                "spear":1000000,
                "ax":10000000,
                "club":1000000
            }

            price = weapon_price[weapon]

            if too_expensive(price*amount):
                await ctx.send(f'You do not have enough gold bars to buy {amount} of {weapon}.')
                return

            # add limit to how many weapons user's backpack can store

            # check if all the weapons PLUS the one they're about to buy is above the limit amount of weapons the user's backpack can hold
            if len(bp["weapons"]["weapons"]) + 1 > bp["weapons"]["limit"]:
                await ctx.send(f'You do not have enough space in your backpack to store {weapon}. Use `.store <item>` to store your weapon in your vault.\n Your weapons are {list(bp["weapons"]["weapons"].keys())}. Space limit is {bp["weapons"]["limit"]}.\n{bp["weapons"]["weapons"]}')
                return
            
            # function for getting the name of the weapon, whether default or the user wants to name it
            # making a function because recursion if the user makes a mistake. easier to make and use than a while loop, dont judge me

            class CustomError(Exception):
                pass
            
            async def get_name():
                name = None

                nonlocal weapon
            
                m: discord.Message = await ctx.send('Do you want to name your weapon? (Y/N)')

                await m.add_reaction('🇾')
                await m.add_reaction('🇳')

                def check(reaction: discord.Reaction, _user: discord.User): # check for client.wait_for()
                    return _user.id == user.id and reaction.message.id == m.id and reaction.emoji in ['🇾','🇳']

                # boolean to know if the user has beaten the clock and sent the message before the timeout error from asyncio
                user_has_replied = False

                try:
                    # get reaction from the user
                    reaction, _user = await self.client.wait_for('reaction_add',check=check,timeout=20)

                    reaction: discord.Reaction

                    # if code gets here that means user has sent a message
                    user_has_replied = True
                
                # if code reaches here that means the user has timed out
                except asyncio.TimeoutError:
                    await ctx.send(f'You have timed out, please try again with `.buy <{item_id}>`')
                    raise CustomError

                # user has beaten the clock and sent the message before asyncio timeout error

                if user_has_replied:
                    def give_default_weapon_name():
                        # the "dedault" weapon name does NOT yet have a "|" to show which weapon number it is. the name might be misleading
                        default_weapon_name = weapon

                        # bool to tell if the for loop has seen a weapon whose name is equal to the weapon name
                        found_copy_of_name = False

                        # go through all the weapons in bp_copy because bp_copy does not have keys that are not weapons
                        for weapon_name in bp["weapons"]["weapons"]:
                            # compare the actual name of the weapon, instead of the reference that the computer has to reference to
                            if bp["weapons"]["weapons"][weapon_name]["name"] == weapon:
                                # set this as true to tell later on we've already update and set a default weapon name
                                found_copy_of_name = True

                                # split the weapon kind by splitter "|". The second part of the list depicts which weapon number that is. First weapon number is 1 by default
                                weapon_number = int(weapon_name.split('|')[1])
                            
                                # set the new number for the weapon
                                new_weapon_number = weapon_number + 1

                                # new weapon name returned will be the weapon_name, which is what kind of weapon it is, sword, club etc.
                                # when replaced, the new weapon name will look like (example weapon as sword)
                                # sword|3
                                default_weapon_name = weapon_name.replace(str(weapon_number),str(new_weapon_number))

                                # we've found the weapon name, so we can break to reduce time
                                break
                        
                        # this is the first weapon of its kind in the user's backpack, so no copies were found
                        if found_copy_of_name == False:
                            # just slap a "1" on the end because its the first one
                            default_weapon_name += "|1"
                        
                        return default_weapon_name

                    # user replies YES
                    if reaction.emoji == '🇾':
                        await ctx.send('What do you want to name your weapon? (Characters limit = 15).')
                        
                        # another boolean to check if user has beaten the second clock, asking what the user wants the weapon name to be
                        user_has_replied_what_weapon_name_is = False

                        try:
                            name: discord.Message = await self.client.wait_for('message',check=check)
                            # user has said what they want the weapon name to be, so the bool to true
                            user_has_replied_what_weapon_name_is = True

                            # discord.py has the message class string as a whole bunch of nonsense, only name.content has the actual content of the message.
                            name = name.content

                        except asyncio.TimeoutError:
                            await ctx.send('You have timed out. moving on to the next step...')
                            return
                        
                        if user_has_replied_what_weapon_name_is:
                            # code below to check if the user has tried to name the weapon that another weapon's name is
                            all_weapon_names = []

                            for weapon in bp["weapons"]["weapons"]:
                                await ctx.send(weapon)
                                all_weapon_names.append(bp["weapons"]["weapons"][weapon]["name"])

                            if name in all_weapon_names:
                                # user cannot use this name because another weapon is called that already

                                await ctx.send(f'There is already a weapon called {name}. If you would like us to give your weapon a default name, enter `n`. If you would like to try again, enter `y`. Check `.bp` and `.vault` for all of your weapon names.')

                                # recursion, with wait_for() and everything else
                                await get_name()
                    
                    # user replies NO
                    elif reaction.emoji == '🇳':
                        default_weapon_name = give_default_weapon_name()

                        name = default_weapon_name

                        await ctx.send(f'Your weapon\'s name will be {default_weapon_name} by default.')
                    
                    # user replies with something that isnt acceptable
                    else:
                        await ctx.send('❌ Invalid answer. Acceptable answer as as follows: Y/N.')
                        # recursive loop - the user has made a mistake the return the user back to the beginning of the function

                        await get_name()
                    
                    # returns the name of the weapon
                    return name

            try:
                name = await get_name()
            except CustomError: # raises error when user times out
                await ctx.send('timed out so function return')
                return # return so no more code is ran - user will have to use command again

            await ctx.send(f'This is your name {name}.')
            
            weapons = {
                "spear": {
                    "name":"spear",
                    "durability": 30,
                    "steal range": [
                        100000,
                        500000
                    ],
                    "damage":60,
                    "cooldown":600,
                    "energy taken":10,
                    "upgrade price":500, # XP. 1 hit from this gives you a random number between [10,20], and if you kill something with this weapon, you get 50 XP
                    "xp gain":{
                        "on hit xp":[10,20],
                        "final kill xp":50
                    },
                    "enchantments":{}
                },
                "crossbow":{
                    "name":"crossbow",
                    "durability":30,
                    "steal range": [
                        30000,
                        70000
                    ],
                    "damage":50,
                    "cooldown":600,
                    "energy taken":10,
                    "upgrade price":500, # XP. 1 hit from this gives you a random number between [10,20], and if you kill something with this weapon, you get 50 XP
                    "xp gain":{
                        "on hit xp":[10,20],
                        "final kill xp":50
                    },
                    "enchantments":{}
                },
                "sword": {
                    "name":"sword",
                    "durability":30,
                    "steal range": [
                        40000,
                        80000
                    ],
                    "damage":75,
                    "cooldown":600,
                    "energy taken":10,
                    "upgrade price":500, # XP. 1 hit from this gives you a random number between [10,20], and if you kill something with this weapon, you get 50 XP
                    "xp gain":{
                        "on hit xp":[10,20],
                        "final kill xp":50
                    },
                    "enchantments":{}
                },
                "ax": {
                    "name":"ax",
                    "durability":30,
                    "steal range": [
                        200000,
                        600000
                    ],
                    "knockout":300,
                    "damage":90,
                    "cooldown":900,
                    "energy taken":15,
                    "upgrade price":500, # XP. 1 hit from this gives you a random number between [10,20], and if you kill something with this weapon, you get 50 XP
                    "xp gain":{
                        "on hit xp":[10,20],
                        "final kill xp":50
                    },
                    "enchantments":{}
                },
                "club": {
                    "name":"club",
                    "durability":30,
                    "steal range": [
                        100000,
                        300000
                    ],
                    "knockout":600,
                    "damage":90,
                    "cooldown":900,
                    "energy taken":15,
                    "upgrade price":500, # XP. 1 hit from this gives you a random number between [10,20], and if you kill something with this weapon, you get 50 XP
                    "xp gain":{
                        "on hit xp":[10,20],
                        "final kill xp":50
                    },
                    "enchantments":{}
                }
            }

            # get specific weapon's data (dict)
            weapon_info = weapons[weapon]

            # set the weapon in the backpack as dict above
            bp["weapons"]["weapons"][name] = weapon_info

            # dock money from user's balance
            bp["gold bars"] -= price * amount

            msg = f'Bought {weapon} fpr {price*amount} gold bars.'
        
        # messsage is preset, depending on what the user bought.
        await ctx.send(msg)
        
    @commands.command(name='return')
    async def _return(self, ctx: commands.Context, item_id: int):
        """Returns an item back to the shop, recieving 90% the value back. Item is identified by the item id given (`.return <item_id>`)"""
  
def setup(client):
    client.add_cog(Marketplace(client))