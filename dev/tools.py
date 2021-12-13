import random
import asyncio
from typing import Literal
import discord
import time
import gc
import threading
from discord.ext import commands
from discord.ext import tasks
from dev.api import db
from dev.db import Database
from dev.items import ItemsTool

"""There is something majorly wrong with the potion loops, with retrieving one of the past loops and restarting it. Fix this later."""

async def attack(ctx: commands.Context): # i completely forgot why i made this but it will come back because i DO remember thinking this is important i need to make this
    """Attacks player and does all necessary functions."""

class Tools:
    ITEM_DESPAWN_TIME = 300 # 300 seconds = 5 minutes - ALL items will despawn at most after 5 minutes. Some may despawn earlier

    class __GameException(Exception):
        pass
    
    class PlayerConfined(__GameException):
        pass

    class PlayerGameLocked(__GameException):
        pass

    def __init__(self):
        self.no_acc = 'You do not have an account. Make one with `.start`.'
        self.lime = discord.Color.from_rgb(144,238,144)
        self.safe_places = ['mineshaft','marketplace','grove','downtown','forge','vault','coliseum']


    def checkPLayerNotConfined(self, ctx: commands.Context):
        """Checks if player is contained in a certain place."""
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        gdata = user_data["game"]

        return gdata["confined"]

    def checkPlayerGameNotLocked(self, ctx: commands.Context):
        """Checks that the game is not locked for the `user`."""        
        user_data = Database.getStorageData(ctx.author)
        gdata = user_data.get('game')

        return gdata["game locked"]
    
    def get_frozen_em(self,user) -> discord.Embed:
        """This returns an object, instance of `discord.Embed`. Contains instructions for user that is frozen."""
        gdata = Database.getStorageData(user)["game"]
        
        remaining_time = int(gdata["time unfrozen"] - time.time())
        
        em = discord.Embed(title="Frozen",color=discord.Color.blue(),description=f"Frozen for {remaining_time}. buddy you\'re frozen. You can\'t do anything right now.")

        return em
    
    def user_at_required_location(self,user,location) -> bool:
        gdata = Database.getStorageData(user)["game"]
        if gdata["location"] != location:
            return False
        
        return True

    def user_at_required_realm(self,user,realm) -> bool:
        gdata = Database.getStorageData(user)["game"]

        if gdata["realm"] != realm:
            return False
        
        return

    def rob(self,user) -> bool or None:
        gdata = Database.getStorageData(user)["game"]

        if gdata["can be robbed"] == False:
            return False
    
        rob_ = random.randint(1,gdata["rob"])

        if rob_ == 1:
            user_database = Database.getStorageData(user)

            user_database["healthpoints"]["health"] -= 1

            bp = user_database["backpack"]

            if (bp["gold bars"] - gdata["rob steal"]) < 0:
                bp["gold bars"] = 0
            
            else:
                bp["gold bars"] -= gdata["rob steal"]
            
            return f'{user.mention} you have just been robbed'
        
        else:
            return False
        
    def wrong_location_msg(self,user,location,realm=None) -> str:
        """This returns a string that tells the user that he or she is in the wrong location (or realm). Should be an instance of `discord.Embed`, but for general purposes a string will suffice for now."""
        
        em = discord.Embed(color=self.lime,title='Not At Required Location')

        wrong_location_msg = f"{user.mention} are not at `{location}` yet."

        if realm != None:
            wrong_location_msg = f"{location} is in {realm}. You are not at {realm} yet!"
        
        return wrong_location_msg
        
    def dodge_attack(self,user) -> bool:
        """Returns `True` if RNG decides that this specific attack the user managed to dodge - `False` if not."""
        gdata = Database.getStorageData(user)["game"]

        x = random.randint(1,gdata["dodge"])

        if x == 1:
            return True
        
        return False
    
    def get_rand_id(self,all_potion_ids:list) -> str:
        """Returns a random ID - ID is not that large."""
        choice_range = 30

        count = 0
        
        while True:
            count += 1
            new_potion_id = random.randint(1,choice_range)

            if new_potion_id not in all_potion_ids:
                return str(new_potion_id)
            
            else:
                if count == choice_range:
                    choice_range += 10
    
    def deduct_xp(self, gdata: dict) -> None:
        """Method will dock 50 XP points from the user every time or she dies."""
        # just here because i dont want to have to write the entire thing out each time

        gdata["xp"] -= 50
    
    async def addXP(self, ctx: commands.Context, amount: int):
        """Adds `XP` to player current experience."""
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        gdata = user_data["game"]

        gdata["xp"] += amount

        await ctx.send(f'{user.mention} earned **{amount}** XP!')

    async def dialogue(self, character: str, client: commands.Bot, ctx: commands.Context, dialogue: dict):
        """
        Takes in `client: commands.Bot` because method needs to access `commands.Bot.wait_for`.
        Sends a message through `ctx`, and allows response from player.
        
        Example `dialogue` argument:
        ```
        {
            "sentence":"Yo what are you doing here",
            "responses":{
                1:"nothing particular",
                2:"peeing"
            },
            1:{
                "sentence":"no, i think youre up to no good",
                "responses":{
                    1:"no???"
                },
                1:{
                    "sentence":"Ah hah! I see your piss right there, you nasty ass."
                    # no responses, end dialogue
                }
            },
            2:{
                "sentence":"BOI GET YOUR NASTY ASS MF OUT OF MY HOUSE AND PISS SOMEWHERE ELSE",
                # no responses, end dialogue
            }
        }
        ```
        """
        user: discord.User = ctx.author

        class NoMoreResponses(Exception):
            pass

        user_data = Database.getStorageData(user)
        gdata = user_data["game"]
        gdata["game locked"] = True # lock game because player cannot do anything while inside a dialogue

        async def recursivelyFinishDialogue(data: dict):
            """Adds a single dialogue sequence, and once it is finished, tyr to move on. If unable to, then do not do recursion."""
            sentence: str = data["sentence"]

            try: 
                responses: dict = data["responses"]
            except: 
                await ctx.send(f'**{character}**: {sentence}')
                raise NoMoreResponses

            msg = sentence + '\n'

            numbered_reactions = {
                '1️⃣':1,
                '2️⃣':2,
                '3️⃣':3,
                '4️⃣':4,
                '5️⃣':5,
                '6️⃣':6,
                '7️⃣':7,
                '8️⃣':8,
                '9️⃣':9,
                '🔟':10
            }
            
            def emojiFromNumber(number: int) -> str:
                for reaction in numbered_reactions:
                    if numbered_reactions[reaction] == number:
                        return reaction

            def numberFromEmoji(emoji: str) -> int:
                return numbered_reactions[emoji]

            reactions_to_add = []

            for i in responses:
                i: int # the number id for response

                msg += f'\n{i}: {responses[i]}'

                number_reaction = emojiFromNumber(i)
                reactions_to_add.append(number_reaction)

            m: discord.Message = await ctx.send(f'**{character}**: {msg}')
            
            for i in reactions_to_add:
                await m.add_reaction(i)
            
            def check(reaction: discord.Reaction, _user: discord.User) -> bool:
                nonlocal user

                if reaction.emoji in reactions_to_add and _user.id == user.id:
                    return True
                else:
                    return False
            
            try:
                reaction, _user = await client.wait_for("reaction_add", check=check, timeout=30)
            
            except asyncio.TimeoutError: 
                await m.reply(f"{user.mention} timed out ❌")
                return

            reaction: discord.Reaction

            number = numberFromEmoji(reaction.emoji)

            response = data["responses"][number]

            await m.reply(content=f'**{user}** {response}', mention_author=False)

            try:
                await recursivelyFinishDialogue(data[number])
            except NoMoreResponses:
                gdata["game locked"] = False # unlock game because dialogue finished

                return
    
        await recursivelyFinishDialogue(dialogue)

    def get_probabilities(self,weapon: str) -> dict:
        percentages = {
            "stick":0.95
        }

        percentage = percentages[weapon]
        probabilities = {0:0}
        previous_total = 0

        piecewise = False
        piecewise_val = None
        piecewise_first_x = None
        
        for i in range(1,42):
            if piecewise: # if piecewise is True, then remaining damage powers will have the same probability
                probabilities[i] = piecewise_val
            
            else:
                previous_total += probabilities[i - 1]

                # if if statement below is true set piecewise to true
                if previous_total == 100: # cannot have this happen, because 100 - 100 is 0. the probability must be close to 0, not zero itself
                    # since most machines rounds the number 99.999999999 (and keeps going) to 100, lets just do that. Now, the system for getting new probabilities will be more of a piecewise function because all probabilities after this will stay the same

                    previous_probability = probabilities[i - 1]
                    final_probability = None

                    str_previous_probability = str(previous_probability)

                    index_of_e = str_previous_probability.index('e')
                    power_of_10 = int(str_previous_probability[(index_of_e + 1):])

                    # get a number less than the previous probability
                    
                    final_probability = previous_probability - 1 * 10 ** power_of_10

                    probabilities[i] = final_probability

                    piecewise = True
                    piecewise_val = final_probability

                    piecewise_first_x = i

                else:
                    probabilities[i] = percentage * (100 - previous_total)
            
        return probabilities, piecewise_first_x

    async def NoArgumentGiven(self, ctx: commands.Context, *missing_args):        
        msg = '`,'.join(missing_args)

        msg = msg[:-1]

        msg = '`' + msg + '`'
        
        await ctx.reply(f'❌ Missing arguments: {msg}. If you ever need help on how to use a command, use `.help <command name>`.')
    
    async def lockGame(self, user: discord.User, check, period: float = 0.5):
        """Locks the game AND code (inside method) for the user until check returns `True`. Check should be a function/method that returns `bool` - if `True` then unlock game. Method periodically checks if game can be unlocked, using `asyncio.sleep`."""

        user_data = Database.getStorageData(user)

        gdata = user_data.get('game')

        gdata["game locked"] = True

        while True:
            if check():
                gdata["game locked"] = False
                return
        
            await asyncio.sleep(period)
        
    async def wait(self, check, period: float = 0.5):
        """
        Waits for the `check` to return `True` - if not, do not continue code.
        """
        while True:
            if check():
                return True
            
            await asyncio.sleep(period)
        
    async def confinePlayer(self, user: discord.User, check):
        """Confines a player to a certain location until `check` (function or method) is met."""

        user_data = Database.getStorageData(user)
        gdata = user_data["game"]
        
        gdata["confined"] = True
        
        period = 0.5 # time sleep
        
        while True:
            if check():
                gdata["confined"] = False
                return
            
            await asyncio.sleep(period)

    def getAttackType(self, base_equipment_name: str) -> str:
        attack_types = {
            # MELEE
                "stick":"melee",
                "mogo club":"melee",
                "mogo club":"melee",
                "mogo spear":"melee",
                "mogo bat":"melee",
                "wooden bat":"melee",
                "wooden spiked bat":"melee",
                "wooden spear":"melee",
                "knight's broadsword":"melee",
                "knight's claymore":"melee",
                "steel spear":"melee",
                "steel sword":"melee",
                "steel mace":"melee",
                "stick":"melee",
            
            # RANGED
                "wooden bow":"ranged",
                "lightning staff":"ranged",
                "blaze staff":"ranged",
                "ice staff":"ranged",
                "flame sword":"ranged",
                "ice sword":"ranged",
            
            # BOW
            "mogo bow":"bow"
        }

        attack_type = attack_types[base_equipment_name]

        return attack_type
    
    async def addGrabbableItems(self, ctx: commands.Context, type: str, items: dict):
        """Adds an item to the player's grabbable items."""

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        for i in items:
            try: bp["grabbable items"][type][i] += items[i] # items[i] = amount of item to add
            except KeyError: bp["grabbable items"][type][i] = 1

        msg = ['`']

        for i in items:
            msg.append(f'{items[i]} {i}`, `')
        
        msg = ''.join(msg)

        msg = msg[:-1]

        await ctx.send(f'Added {msg} to your grabbable items - use `.grab` to grab these items.')

        def despawnItems():
            time.sleep(self.ITEM_DESPAWN_TIME)

            for i in items:
                if i in bp["grabbable items"][type]:
                    del bp["grabbable items"][type][i]

        threading.Thread(target=despawnItems).start()
    
    async def addItem(self, ctx: commands.Context, item: str, amount: int):
        """Adds a singular item to the player's backpack."""

        reward_type = ItemsTool.getRewardType(item)

        data_add = {item: amount}

        if reward_type == 'weapons' or reward_type == 'bows':
            await self.addEquipments(ctx, data_add)
        
        elif reward_type == 'valuables':
            await self.addValuables(ctx, data_add)
        
        elif reward_type == 'loot':
            await self.addLoot(ctx, data_add)
        
        elif reward_type == 'armor':
            await self.addArmors(ctx, data_add)
        
    async def addArmors(self, ctx: commands.Context, armors: dict):
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)

        # armors = {
        #     "leather helm":int,
        #     "leather chestpalte":int
        # }

        # do not need the amount of leather helm - you can only get one. instead, the data we need is the durability, the protection it gives, etc

        def getArmorPieceData(piece: str) -> dict:
            """
            Returns:
            ```
            {
                "durability":int,
                "protection":float,
                "type":Literal['helm', 'chestplate', 'greaves']
                "bonuses":None or str
            }
            ```
            """

            # TODO: finish this

            piece_data = {
                "leather cap":{
                    "type":"head",
                    "durability":30,
                    "protection":4
                },
                "leather shirt":{
                    "type":"chest",
                    "durability":40,
                    "protection":8
                },
                "leather pants":{
                    "type":"leg",
                    "durability":20,
                    "protection":3
                },

                # leather total: 0.12
            }

            return piece_data[piece]

        bp: dict = user_data["backpack"]

        msg = ''

        for armor in armors:
            bp["armor"]["base"][armor] = getArmorPieceData(armor)
    
    async def addValuables(self, ctx: commands.Context, items: dict):
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)

        bp: dict = user_data["backpack"]

        msg = ''
        
        for item in items:
            try: bp["grabbable items"]["valuables"][item] += items[item]
            except KeyError: bp["valuables"][item] = items[item]

            msg += f'\nAdded `{item}` to your valuables.'
        
        try:
            await ctx.send(msg)
        except discord.errors.HTTPException: # cannot send empty message
            pass

    async def addLoot(self, ctx: commands.Context, items: dict):
        """
            Adds loot to the player's loot. Loot consists of monster parts..
        """

    async def addRawFood(self, ctx: commands.Context, items: dict):
        """
            Adds food to the player's RAW food. If there's no more space for meals, then
        """

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        for i in items:
            try:
                bp["items"]["food"][i] += items[i]
            
            except KeyError: # this means that there isnt "i" type of food in the player's backpack yet, so add one
                bp["items"]["food"][i] = items[i] # first item that they had, so give a singular piece
    
    async def addMeal(self, ctx: commands.Context, meal_name: str, amount: int):
        """Adds a single meal to the player's backpack, because meals cannot stack on inventory"""

        # TODO finish this part of the code
    
    async def addEquipments(self, ctx: commands.Context, equipments: dict = {}, preset_equipments: list = [], grabbable: bool = False) -> dict:
        """
        NOTE: `equipments` POINTS towards `bp["grabbable items"]["weapons"]` - not an individual object

        NOTE: Method doesn't **actually** give the player equipment - it puts in the player's `grabbable items` `dict` in player' backpack.

        `shield_compatible` defaults `True`. Two handed weapons and all bows are not usable with shield.

        NOTE: bows take no energy when used. However, durability is still taken away.

        Adds a `dict` containing all the weapon information:
        ```
        "name":str
        "damage":int
        "durability":int
        "attack time":int
        "attack type":str
        "energy taken":int
        "shield compatible":bool
        ```

        NOTE - weapons are not finished. Finish adding weapons to `weapon_stats`
        """

        # TODO: add the rest of the weapons

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        for equipment in preset_equipments:
            equipment: dict

            attack_type: str = equipment["attack time"]
            name: str = equipment["name"]
            
            category = "weapons" if attack_type == "melee" else "bows"
            
            for category in ["weapons", "bows"]:
                equipment_amount = 1 # counting this new addition it's 1, not 0
                
                for equipment in bp[category][category]:
                    equipment: dict = bp[category][category][equipment]
                    
                    if equipment["name"] == name:
                        equipment_amount += 1

                if equipment_amount > 0:
                    new_name = name + "|" + str(equipment_amount)
                
                else:
                    new_name = name
                
            if grabbable:
                bp["grabbable items"][category][new_name] = equipment # value is SUPPOSED to be type (int), but set as type (dict)
                # easy "hacky" way to solve this problem is to build an exception where if the type is (dict) then it's preset data and simply do that

                await ctx.send(f'Added `{name}` to your grabbable items - use `.grab` to grab these items.')

            else:
                bp[category][category][new_name] = equipment
        
                await ctx.send(f"Added **{name}** to your backpack.")

        equipment_stats = {
            "stick":{
                "damage":[1, 2],
                "durability":[5, 10],
                "attack time":2,
                "attack type":"melee",
                "energy taken":1,
                "shield compatible":True
            },
            "mogo club":{
                "damage":[5, 10],
                "durability":[20, 30],
                "attack time":2.5,
                "attack type":"melee",
                "energy taken":2,
                "shield compatible":True
            }
        }

        # NOTE: the equipment name is the name of the BASE weapon name, such as sword. The "official" name of a weapon is the BASE weapon name and the number of the weapon name joined by '|'
            
        for equipment_name in equipments: # equipments = {"name": (int) amount}
            if type(equipments[equipment_name]) == dict:
                # preset data - simply set in backpack
                
                data = equipments[equipment_name]

                name = data["name"]
                attack_type = self.getAttackType(name)

                section = "weapons" if attack_type == "melee" else "bows"

                if len(bp[section][section]) == bp[section]["limit"]:
                    await ctx.send(f'At limit - cannot add `{name}` to `{section}`')
                
                else:
                    bp[section][section][equipment_name] = data
            
            else: # type(equipments[equipment_name]) == int => integer showing how many equipment to add
                stats = equipment_stats[equipment_name]

                stats["damage"] = random.randint(stats["damage"][0], stats["damage"][1])
                stats["durability"] = random.randint(stats["durability"][0], stats["durability"][1])

                attack_type = self.getAttackType(equipment_name)

                section = "weapons" if attack_type == 'melee' else "bows"

                if not len(bp[section][section]) == bp[section]["limit"]: # not at limit - if add more will pass limit
                    final_equipment_name = None

                    if not equipment_name in bp[section][section]: # weapon name not in the weapons - first type of weapon
                        stats["name"] = equipment_name
                        bp[section][section][f'{equipment_name}|1'] = stats

                        msg = f'{user.mention} Added **{equipment_name}** to your weapons.'

                        final_equipment_name = equipment_name + '|1'
                    
                    else:
                        # weapon name already in weapons
                        def get_default_equipment_name() -> str:
                            nonlocal equipment_name

                            default_equipment_name = equipment_name

                            found_copy_of_name = False

                            for equipment_name in bp[section][section]:
                                # checking the base name of weapons because default weapon name is set by finding all the same weapons and adding the amount plus one to it.
                                if bp[section][section][equipment_name]["name"] == equipment_name:
                                    found_copy_of_name = True

                                    # split the weapon kind by splitter "|". The second part of the list depicts which weapon number that is. First weapon number is 1 by default
                                    weapon_number = int(equipment_name.split('|')[1])
                                    new_weapon_number = weapon_number + 1

                                    # when replaced, the new weapon name will look like (example weapon as sword)
                                    # sword|3
                                    break
                            
                            # this is the first weapon of its kind in the user's backpack, so no copies were found
                            if found_copy_of_name == False:
                                # just slap a "1" on the end because its the first one
                                new_weapon_number = 1
                            
                            default_equipment_name += new_weapon_number
                            
                            return default_equipment_name
                        
                        default_equipment_name = get_default_equipment_name()
                    
                        weapon_info_split = default_equipment_name.split('|')

                        weapon_number = weapon_info_split[1]

                        msg = f"{user.mention} set your weapon to {weapon_info_split[0]}`{weapon_number}`.\nIf you wish to change your weapon name, use `.rename`"

                        final_equipment_name = default_equipment_name
                    
                    if attack_type == 'melee':
                        category = 'weapons'
                    
                    else:
                        category = 'bows'

                    def getEquipmentData() -> dict:
                        # TODO: finish all this
                        two_handed_weapon_attack_time = 1.5
                        spear_attack_time = 0.15
                        one_handed_weapon_attack_time = 0.25

                        two_handed_weapon_energy_taken = 25
                        one_handed_weapon_energy_taken = 10
                        spear_energy_taken = 15

                        equipment_datas = {
                            # MELEE
                                "mogo club":{
                                    "damage":[2, 5],
                                    "durability":[10, 20],
                                    "attack time":one_handed_weapon_attack_time,
                                    "energy taken":one_handed_weapon_energy_taken
                                },
                                "mogo spear":{
                                    "damage":[2, 5],
                                    "durability":[10, 20],
                                    "attack time":two_handed_weapon_attack_time,
                                    "energy taken":spear_energy_taken
                                },
                                "mogo bat":{
                                    "damage":[10, 20],
                                    "durability":[20, 30],
                                    "attack time":two_handed_weapon_attack_time,
                                    "energy taken":two_handed_weapon_energy_taken
                                },
                                "wooden bat":{
                                    "damage":[1, 5],
                                    "durability":[8, 16],
                                    "attack time":two_handed_weapon_attack_time,
                                    "energy taken":two_handed_weapon_energy_taken
                                },
                                "wooden spiked bat":{
                                    "damage":[10, 15],
                                    "durability":[10, 20],
                                    "attack time":two_handed_weapon_attack_time,
                                    "energy taken":two_handed_weapon_energy_taken
                                },
                                "wooden spear":{
                                    "damage":[1, 5],
                                    "durability":[5, 10],
                                    "attack time":spear_attack_time,
                                    "energy taken":spear_energy_taken
                                },
                                "knight's broadsword":{
                                    "damage":[20, 40],
                                    "durability":[30, 50],
                                    "attack time":one_handed_weapon_attack_time,
                                    "energy taken":one_handed_weapon_energy_taken
                                },
                                "knight's claymore":{
                                    "damage":[30, 60],
                                    "durability":[30, 50],
                                    "attack time":two_handed_weapon_attack_time,
                                    "energy taken":two_handed_weapon_energy_taken
                                },
                                "steel spear":{
                                    "damage":[25, 40],
                                    "durability":[25, 40],
                                    "attack time":spear_attack_time,
                                    "energy taken":spear_energy_taken
                                },
                                "steel sword":{
                                    "damage":[25, 40],
                                    "durability":[30, 45],
                                    "attack time":one_handed_weapon_attack_time,
                                    "energy taken":one_handed_weapon_energy_taken
                                },
                                "steel mace":{
                                    "damage":[40, 70],
                                    "durability":[45, 60],
                                    "attack time":two_handed_weapon_attack_time,
                                    "energy taken":two_handed_weapon_energy_taken
                                },
                                "stick":{
                                    "damage":[2, 3],
                                    "durability":[5, 8],
                                    "attack time":one_handed_weapon_attack_time,
                                    "energy taken":one_handed_weapon_energy_taken
                                },
                            
                            # RANGED

                        }

                        equipment_data = equipment_datas[equipment_name]

                        damage: int = random.randint(equipment_data["damage"][0], equipment_data["damage"][1])
                        durability: int = random.randint(equipment_data["durability"][0], equipment_data["durability"][1])

                        equipment_data["damage"] = damage
                        equipment_data["durability"] = durability

                        equipment_data["name"] = equipment_name
                        
                        return equipment_data
                    
                    bp[category][category][final_equipment_name] = getEquipmentData()
                    
                    await ctx.send(msg)
                
                else: # cannot add more weapon - will pass limit if so
                    await ctx.send(f'{user.mention} cannot add `{equipment_name}` to your backpack, not enough space.')

    def getDurabilityOfWeapon(self, *, wpn_str: str) -> int:
        """This method gets the durability of weapon given by the `wpn_str` parameter."""

        durability_ranges = {
            "stick":[10,20], # from 10 to 20 uses in the stick before it breaks
        }

        ranges = durability_ranges[wpn_str]

        return random.randint(ranges[0], ranges[1])
        
    def getIfWeaponIsRepairable(self, wpn_str: str) -> bool:
        """This method returns a `bool`, `True` if weapon can be repaired and `False` if not."""
    
    def getArmorDamageReductionRatio(self,data:dict) -> dict:
        """Method returns a `dict`, representing a ratio consisting of the damage reduction participation of every piece of armor in the data, compared to the `total_damage_reduce`."""
        total_damage_reduce = 0
        
        for armor in data["base"]:
            total_damage_reduce += data["base"][armor]["protection"]
        
        ratio = {}

        for armor in data["base"]:
            ratio[armor] =  data["base"][armor]["protection"] / total_damage_reduce # part over whole - simple fraction/ratio
        
        return ratio
    
    def death_message(self, user: discord.User, death_type: Literal["monster", "player", "weather"], monster_attack_type: Literal['melee', 'bow']= None, monster_type: str = None,weather_type: str = None) -> discord.Embed:
        """Returns a string that tells the user given that he or she has died, specifying which monster killed the user and how the user died."""
        monster_actions_past_tense = {
            "goblin":[
                'pummeled','punched','manslaughtered','crushed','demolished','smote','struck','crushed'
            ],
            "mogosok":[
                'beat','slaughtered','struck','pummeled','smote'
            ]
        }
        
        death_messages = {
            "monster":{
                "goblin":{
                    "melee":[
                        '__user__ got __verb__ while attacking __monster__.',
                        '__monster__ __verb__ __user__, crushing __user__\'s dreams of becoming the greatest.',
                        '__user__ played themself and got __verb__ by __monster__'
                    ],
                    "ranged":[
                        '__user__ got __verb__ whilst attacking __monster__'
                    ]
                },
                "mogosok":{
                    "melee":[
                        '__monster__ __verb__ __user__ and killed them.',
                        '__monster__ completely wrecked __user__, __verb__ them, dealing catastrophic damage.'
                    ],
                    "ranged":[
                        '__monster__ shot your fucking ass __user__'
                    ]
                }
            },
            "player":[
                # finish this thing
            ],
            "weather":{
                "thunderstorm":[
                    '__user__ got struck by lightning and died.',
                    'The thunderstorm got __user__, and struck them with divine lightning.',
                    'Lightning struck __user__ and killed them.'
                ],
                "tornado":[
                    '__user__ got knocked around too many times in the tornado and died.'
                ],
                "hurricane":[
                    '__user__ was washed away by the hurricane.',
                    'The hurricane washed away __user__, with no physical record of his or her will...',
                    'God has decided that __user__ will die today, and so the hurricane washed them away. Rest In Peace __user__...',
                    '__user__ decided tempt fate, and battled the strong currents of the hurricane. Alas, they have perished. Learn from their mistake, and don\'t ask God to kill you with a hurricane.'
                ],
                "flood":[
                    'The flood washed away __user__, leaving their families weeping for their loss.',
                    '__user__ was drowned in the flood. Learn from them, kids, and don\'t go out in a flood.',
                    '__user__ decided to tempt fate and venture outside during a flood. Sadly, they were washed away.'
                ]
            }
        }
        
        msg = None

        if death_type == 'monster':
            past_tense_verb = random.choice(monster_actions_past_tense[monster_type])

            msg: str = random.choice(death_messages["monster"][monster_type][monster_attack_type])

            msg = msg.replace('__user__',f'{user}').replace('__verb__',past_tense_verb).replace('__monster__', monster_type)
        
        elif death_type == 'weather':
            msg = random.choice(death_messages["weather"][weather_type]).replace('__user__',user)
        
        em = discord.Embed(
            title='Death',
            description=msg
        )

        em.set_author(name=user, icon_url=user.avatar_url)

        return em
    
    def get_potion_value_stats(self,potion_type:str,chests=False,**kwargs) -> tuple:
        """Method returns a dict containing the duration, value, falcon value and rarity of the potion."""

        if chests:
            potion_rarity = kwargs["chest_rarity"]

        def get_potion_rarity():
            potion_type_to_kind = {
                "mining speed":{
                    # write out the keys first
                    # types of chests - common, uncommon, rare, epic, mythical, and legendary
                    "common":[0,55],
                    "uncommon":[55,85],
                    "rare":[85,90],
                    "epic":[90,95],
                    "mythical":[95,99],
                    "legendary":[99,100]
                },
                "protection":{
                    "common":[0,45],
                    "uncommon":[45,70], # finish this, go down and add potion rarity in boosts.local potions, and finish code in falcon.py
                    "rare":[70,85],
                    "epic":[85,95],
                    "mythical":[95,98],
                    "legendary":[98,100]
                },
                "damage increase":{
                    "common":[0,50],
                    "uncommon":[50,70],
                    "rare":[70,85],
                    "epic":[85,94],
                    "mythical":[94,99],
                    "legendary":[99,100]
                },
                "energy efficiency":{
                    "common":[0,60],
                    "uncommon":[60,85],
                    "rare":[85,95],
                    "epic":[95,97],
                    "mythical":[97,99],
                    "legendary":[99,100]
                }
            }

            number = random.randint(0,99)
            potion_rarity = None

            for iterated_potion_rarity in potion_type_to_kind[potion_type]:
                num_range = potion_type_to_kind[potion_type][iterated_potion_rarity]
                
                if number in range(num_range[0],num_range[1]):
                    potion_rarity = iterated_potion_rarity
                    return potion_rarity
        
        def get_potion_duration(potion_rarity):
            duration_from_rarity = {
                "common":[30,50], # divide by 10 to get the time in minutes
                "uncommon":[40,60],
                "rare":[300,500],
                "epic":[600,1200],
                "mythical":[1800,2400],
                "legendary":[3600,4800]
            }

            num_range = duration_from_rarity[potion_rarity]

            number = random.randint(num_range[0],num_range[1])

            number /= 10 # precise float for number

            number *= 60 # get number in seconds

            return number

        def get_potion_value(potion_rarity,falcon:bool=False) -> tuple:
            value_from_type_and_rarity = {
                "mining speed":{
                    "common":[2,3],
                    "uncommon":[3,4],
                    "rare":[4,5],
                    "epic":[5,6],
                    "mythical":[6,7],
                    "legendary":[7,8]
                },
                "wagon size":{
                    "common":[2,3],
                    "uncommon":[3,4],
                    "rare":[4,5],
                    "epic":[5,6],
                    "mythical":[6,7],
                    "legendary":[7,8]
                },
                "item value":{
                    "common":[2,3],
                    "uncommon":[3,4],
                    "rare":[4,5],
                    "epic":[5,6],
                    "mythical":[6,7],
                    "legendary":[7,8]
                },
                "protection":{
                    "common":0.9, # this is the total reduction of the armor set.
                    "uncommon":0.9, # if i want this to be a real damage
                    "rare":0.85,
                    "epic":0.8,
                    "mythical":0.7,
                    "legendary":0.5
                },
                "damage increase":{
                    "common":[15,25], # divide number by 100 later on
                    "uncommon":[15,25],
                    "rare":[15,30],
                    "epic":[15,35],
                    "mythical":[20,35],
                    "legendary":[30,40]
                },
                "energy efficiency":{
                    "common":[1,2], # divide by 10 to get the time
                    "uncommon":[2,3], # tasks loop to update energy points. pass in the time in seconds (time will be a float)
                    "rare":[3,4],
                    "epic":[4,5], # subtract the float from 1 to get the final energy gain time
                    "mythical":[5,6], # this way we can add the value back after duration is finished
                    "legendary":[6,7] # anything bothering the falcon's energy gain per time will be canceled and returned the falcon's base energy gain time
                }
            }

            falcon_value_from_type_and_rarity = {
                "luck":{
                    "common":0.1,    # 10 out of 100 is headshot
                    "uncommon":0.15, # 15 out of 100
                    "rare":0.25,     # 25 out of 100
                    "epic":0.3,      # 30 out of 100
                    "mythical":0.35, # 35 out of 100
                    "legendary":0.45 # 45 out of 100
                },
                "damage increase":{
                    "common":[15,25], # divide number by 100 later on
                    "uncommon":[15,25],
                    "rare":[15,30],
                    "epic":[15,35],
                    "mythical":[20,35],
                    "legendary":[30,40]
                },
                "protection":{
                    "common":0.9, # this is the total reduction of the armor set.
                    "uncommon":0.9, # if i want this to be a real damage
                    "rare":0.85,
                    "epic":0.8,
                    "mythical":0.7,
                    "legendary":0.5
                },
                "energy efficiency":{
                    "common":[1,2],
                    "uncommon":[2,3],
                    "rare":[3,4],
                    "epic":[4,5],
                    "mythical":[5,6],
                    "legendary":[6,7]
                }
            }

            if falcon:
                try:
                    value_range = falcon_value_from_type_and_rarity[potion_type][potion_rarity]
                except KeyError:
                    return None # could not find a value for the given potion type, meaning the potion type cannot be fed to a falcon, so there is no way to assign a falcon value to the potion type

            else:
                value_range = value_from_type_and_rarity[potion_type][potion_rarity]

            if potion_type == "protection":
                value = value_range

            else:
                value = random.randint(value_range[0],value_range[1])
            
            if potion_type == 'damage incease':
                value /= 100

            return value

        potion_rarity = get_potion_rarity()

        potion_value = get_potion_value(potion_rarity)
        falcon_potion_value = get_potion_value(potion_rarity,falcon=True)
        
        potion_duration = get_potion_duration(potion_rarity)

        return {
            "value":potion_value,
            "falcon value":falcon_potion_value,
            "duration":potion_duration,
            "rarity":potion_rarity
        }

    def get_potion_duration_subtract_loop(self, user:discord.User, user_database: dict, potion_id:int, falcon:bool=False) -> tasks.Loop:
        """Methods starts a tasks loop where a specific potion's duration is subtracted per minute in a specific user's document. If `falcon` is `True`, then returned `tasks.Loop` will be different.
        
        If, on iteration, the duration of the potion id is equal to 0, that means the potion's time is up. We TAKE AWAY THE EFFECTS OF THE POTION OF THE GIVEN POTION ID, and then delete the key `potion_id` from user's doc in database, and also delete the key from active potions in the user's backpack.

        Check `./dev/tools.py` for more information"""

        # user database is the `user_data` grabbed from `Database`
        
        @tasks.loop(seconds=1)
        async def duration_subtract():
            duration_doc = user_database["duration"] # the duration nested dict in user storage - has the potion queue and potion duration information

            if duration_doc == None: # meaning the duration
                duration_subtract.cancel()
                return
            
            duration_doc["potion duration"][potion_id]["duration"] -= 1

            boosts = user_database["boosts"]

            potion_duration = duration_doc["potion duration"][potion_id]["duration"]
            potion_type = boosts["all active potions"][potion_id]["type"]

            if potion_duration == 0: # potion duration has met its end - time to revert everything back to what it was before the potion
                queue: list = duration_doc["queue"] # type = list. list of dicts
                
                if duration_doc["current potion loops"][id(duration_subtract)] == False: # this means that while the loop must still be on, when the loop is done do NOT change the stats
                    print(f'the potion loop that is dormant is supposed to be in queue is {potion_id}')
                    
                    current_loop_ID = id(duration_subtract)

                    def getDictOfLoopID(loop_id):
                        for _dict in queue:
                            if _dict["tasks loop id"] == loop_id:
                                print(_dict["potion id"])
                                return _dict
                    
                    data = getDictOfLoopID(current_loop_ID)

                    queue.remove(data) # removes the DICT containing the potion OBJECT (loop) id, not the POTION id, from the queue

                    duration_subtract.stop() # promptly stop the loop, do NOT revert back to what it was before
                    # all code below will be stopped because we called stop
                
                # if code below runs then that means the potion is NOT dormant
                try:
                    potion_value = duration_doc["potion duration"][potion_id]["value"]
                
                except KeyError: # if the potion does not have any value: luck potions
                    pass
                
                # revert value back to what it was BEFORE the potion - do not revert to the user's BASE stats, because OTHER potions may be in effect - in my game potions can stack on each other.
                # HOWEVER, some potions cannot be stacked, which is why we have dormant potions.

                if potion_type == 'mining speed':
                    mines = db.mines.find_one({"_id":user.id})
                    for item in mines["wagon items"]:
                        mines["wagon items"][item]["drops"] /= potion_value # reverts the drop value from every item in the wagon back to normal
                    
                    mines["mining speed"] /= potion_value # reverts the mining speed to what it was prior to changed from the potion

                    db.mines.update_one({"_id":user.id},{"$set":{"wagon items":mines["wagon items"]}})

                    db.mines.update_one({"_id":user.id},{"$set":{"mining speed":mines["mining speed"]}})
                
                elif potion_type == 'wagon size':
                    mines = db.mines.find_one({"_id":user.id})

                    mines["wagon size"] /= potion_value # returns wagon value to what it was prior to potion's effect
                    
                    db.mines.update_one({"_id":user.id},{"$set":{"wagon size":mines["wagon.original size"]}})
                
                elif potion_type == 'protection':
                    bp = db.backpack.find_one({"_id":user.id})

                    armor_ratio = bp["armor ratio"]

                    # all we want to do now is first, change everything back to what it was before the potion. Then, if there are potions queued up, apply those effects

                    base_total_damage_reduction = 0

                    for armor in bp["armor"]["base"]:
                        base_total_damage_reduction += bp["armor"]["base"][armor]["protection"]

                    for armor in bp["armor"]["final"]:
                        armor_damage_reduction_participation = armor_ratio[armor] # this is a float for the percentage of damage reduction the armor has compared to the total damage reduction

                        base_armor_damage_reduce_value = armor_damage_reduction_participation * base_total_damage_reduction

                        bp["armor"]["final"][armor]["protection"] = base_armor_damage_reduce_value
                    
                    db.backpack.update_one({"_id":user.id},{"$set":{"armor.final":bp["armor"]["final"]}})
                
                elif potion_type == 'damage increase':
                    bp = db.backpack.find_one({"_id":user.id})

                    for weapon in bp["weapons"]:
                        bp["weapons"][weapon]["damage"] /= (1 - potion_value) # revert everything back to what it was before
                        # potion value is how much we reduce it by - for example, 
                        # "reduce x by y percent". 
                        # y = 0.2
                        # new x = x * (1-y) to get the final result
                        # to get old x, we simply divide by (1-y) to go back to our old y

                    db.backpack.update_one({"_id":user.id},{"$set":{"weapons":bp["weapons"]}})
                
                elif potion_type == 'luck':
                    luck_type = user["potions duration"][potion_id]["luck type"]

                    if luck_type == 'rob':
                        db.game.update_one({"_id":user.id},{"$set":{"can be robbed":True}})
                    
                    elif luck_type == 'black market scam':
                        db.game.update_one({"_id":user.id},{"$set":{"can be scammed":True}})
                    
                    elif potion_type == 'value multiplier':
                        mines = db.mines.find_one({"_id":user.id})
                        for item in mines['wagon items']:
                            mines["wagon items"][item]["value"] /= (1+potion_value)
                        
                        # reverts everything back to what it was before the potions effect
                        db.mines.update_one({"_id":user.id},{"$set":{"wagon items":mines["wagon items"]}})

                del duration_doc["potion duration"][potion_id] # delete the potion from the potion duration

                del boosts["all active potions"][potion_id] # eletes the potion id from the active potions for the user
            
                db.duration.update_one({"_id":user.id},{"$set":{"potion duration":duration_doc["potion duration"]}})
                
                try:
                    next_loop_data = queue[0]

                    next_loop_ID = next_loop_data["tasks loop id"]

                    print(f'the potion loop that is dormant is supposed to be in queue is {next_loop_ID}. This is the next loop ID, for loop objects.')

                    def get_obj_from_id(_id):
                        all_objects = gc.get_objects()

                        for _obj in all_objects:
                            if id(_obj) == _id:
                                return _obj
                        
                        raise Exception(f"No object found with id {_id}")
                    
                    old_loop_obj = get_obj_from_id(next_loop_ID)

                    del old_loop_obj # deletes the loop object from the memory

                    print(queue)

                    queue.remove(next_loop_data) # removes the loop from the queue

                    db.duration.update_one({"_id":user.id},{"$set":{"queue":queue}})

                    next_potion_ID = next_loop_data["potion id"]

                    del queue[0] # removes the next loop from the queue as it is already activated

                    loop = self.get_potion_duration_subtract_loop(user=user,potion_id=next_potion_ID,falcon=falcon) # recursion to start new loop. dude. this starts an entirely new loop, completely unrelated with the old protection potion.

                    loop.start()
                
                except IndexError:
                    """There is no loop in queue, so there is nothing to do but stop current potion loop."""

                    duration_subtract.stop()
        
        if falcon: # this means this is a falcon potion duration subtract, not a potion for the user
            @tasks.loop(minutes=1)
            async def falcon_potion_duration_subtract():
                db.falcon_duration.update_one({"_id":user.id},{"$inc":{f"potion duration.{potion_id}.duration":-1}})

                duration_doc = db.falcon_duration.find_one({"_id":user.id})

                if duration_doc == None:
                    duration_subtract.cancel()

                data = db.duration.find_one({"_id":user.id},{"falcon":True})

                duration = data["potion duration"][potion_id]["duration"]

                if duration == 0: # this means the potion's time has finished up
                    if duration_subtract.dormant: # this means that while the loop must still be on, when the loop is done do NOT change the stats
                        duration_subtract.stop()

                    potion_type = duration_doc["potion duration"][potion_id]["type"]
                
                    try:
                        potion_value = duration_doc["potion duration"][potion_id]["value"]
                    
                    except KeyError: # if the potion does not have any value: luck potions
                        pass

                    falcon = db.falcon.find_one({"_id":user.id})
                
                    if potion_type == 'damage increase':
                        for ability in falcon["abilities"]:
                            falcon["abilities"][ability]["damage"] /= (1 - potion_value)
                        
                        db.falcon.update_one({"_id":user.id},{"$set":{f"abilities":falcon["abilities"]}})

                    elif potion_type == 'protection':
                        for armor_piece in falcon["armor"]:
                            falcon["armor"][armor_piece]["protection"]

                            """I need to set up some sort of plan for affecting stats and reverting to what it was before"""
            
            loop = falcon_potion_duration_subtract
        
        else:
            loop = duration_subtract

        return loop # tasks loop for updating the potion duration in the potion collection
    
    def getEquipmentAttackTime(self, equipment_type: str, wpn_name: str = None) -> tuple:
        """During each attack the player will need to pick the weapon back up. This is called attack time, and some weapons have it every 3 times it is swung, every time it is swung, or every 5 times. All bows have a attack time every time it is used.
        Returns a tuple with index 0 = attack time, index 1 = per amount of swings"""
        
        if equipment_type == 'bow':
            return 0.5 # all bows have 0.5 second attack time
        
        else:
            wpn_attack_times = {
                "mogo club":2.5, # we can change this later on
                "mogo spear":1.5,
                "mogo bow":1.5
            }

            return wpn_attack_times[wpn_name]
        
    def give_chest(self,user,quest_difficulty) -> str:
        """Method will return a string that tells the user what he or she has recieved a chest. Should be an instance of `discord.Embed`, but `str` will suffice for now."""
        quest_difficulty_dict = {
            "Easy":["common","uncommon"],
            "Medium":["epic","rare"],
            "Hard":["mythical"]
        }

        chest_type = random.choice(quest_difficulty_dict[quest_difficulty])

        db.chests.update_one({"_id":user.id},{"$inc":{f"chests.{chest_type}":1}})

        return f"{user.mention} gave you a {chest_type} chest!"

    def quests_with_commands_list(self,command_name,user) -> list:
        """returns a list of all the quest ids that needs you to use that command_name"""

        quests = db.quests.find_one({"_id":user.id})

        all_quest_ids = []

        for quest_id in quests["quests"]:
            if command_name in quests["quests"][quest_id]["commands with quest"]:
                all_quest_ids.append(quest_id)

        return all_quest_ids
    
    async def deal_weather_damage(self, user, ctx: commands.Context):
        """
        We will only deal with direct cause and chance, because there will already be a tasks loop dealing the recurring damage to the user, we do not have to call tools.deal_weather_damage all the time for the user when he or she goes out in the rain

        Direct cause:
            Weather that have direct cause as one of its risk types means that going out in this weather will, without exception, attempt to deal some kind of damage to ther user. Weather with direct cause as one of it's risk types include but does not limit to:
                1. Hurricane
                2. Tornado
                3. Flood
            
            Going out in this weather will always try cause some kind of damage to you, whether you like it or not. However, if you have special equipment, for example a boat for transportation in floods, or strong armor to reduce incoming damage (and if possible, a speed boosting potion to get to where you need faster.)

            1. Hurricane
                There is nothing special about a hurricane, except there is a possibility of losing your equipped weapon

        Chance:
            Weather that have chance as one of its risk types means that everytime a user goes out, there will be a chance the user will get some kind of damage. Not always, if the user is lucky.
            
            Of course, every weather is different. I have to send messages on what happened, which attack from the weather killed the user, what the after effects from the weather do, and much, much more. With each weather being unique, I have created a nested dictionary called "extras", which contain all that i need. All I have to do is access the dictionary.

            Now, time for the actual set up of the "extra" dictionary. As I said, each weather is different, so I will be walking you (and me, I'm trying to explain this to myself.)

            1. Thunderstorm
                Risk type(s):['chance']
                In thunderstorms, there is a chance of being struck by lightning. When getting struck by lightning, there is a small chance (1 in 20 strikes) of dropping your weapons and losing it in the wind, and you can never get your weapon back again. Which is why DO NOT GO OUTSIDE IN A THUNDERSTORM.

            (Unless you have protective equipment that shield you from electrical attacks, then you can go outside if you want.)

            (You can also unequip the weapon .unequip <weapon_name>)

            Depending on the strength of the thunderstorm, the chances of getting struck by lightning and losing your weapon are are higher with stronger thunderstorms, and lower with weaker thunderstorms. Regardless of what kind of weapon you have, it will be lost.
            
        Last but not least, we will talk about weather with temperature as risk type. We are not talking about how we are going to incorporate temperature and the recurring damage into tools.deal_weather_damage(), because there will be a tasks loop for that. Instead, we will be talking about how users can avoid weather damage, unique weather attributes that we can incorporate in the game, and so on.

        Weather with temperature risk type:
            1. Icestorm
                (Icestorm also has a chance risk type, but we will be focusing on the temperature)
                Ice storms simply make you slower with every recurring damage to you. Icestorms deal 20 HP to you, and all transportation time, excluding train rides, will be multiplied by 1.5, increasing transportation time by 50%. 
            
            2. Heat wave
                (Heat waves have the ability to change into a drought, see information below.)
                Just like icestorms, heat waves make you slower (you're tired in the heat) - however, there's a catch. If you have heat-resisting potion/equipment on, there will be no side effects in the heat wave. Absolutely zero - you can go out there for as long as you want, or as long as the potion effects last. 
                However, if you don't have those equipment, then you should not go outside. Heat waves will deal a recurring damage of 5 HP to you every 5 second, and after 2 real-time minutes, you will get a heat stroke, so eating all your food to resotre hp when going as fast as you can to where you need is not a good idea if you don't keep track of time and stay in the heat too long.
            
            3. Blizzard
                Not really anything unique about blizzard, except for one thing - there is a possibility of getting lost in the blizzard and ending up somewhere else. Harmless, and just kind of funny.
            
        Actually, on second thought, I don't know how to make the tasks loop for the weather stuff. I'm going to talk about it here, but I'm not going to put any code in tools.deal_weather_damage(), because it will be in the tasks loop.

        Before I do anything else I need to know when and where I am going to user self.deal_weather_damage()

        It's everytime the user goes outside, or uses the one of the travel methods that I will first check if the weather is dangerous, and then deal the weather damage

        Wait a fucking second if i just do the tasks loop in here, then that means I can use CTX instead of having to dm the user. Yes. This is what I will do.

        What I mean by that is, I will still make a TEMPORARY tasks loop inside this method. Basically, every time the user goes outside during weather with temperature with risk type temperautre, we will deal the recurring damage every ("wait" key's value in the risk dict) seconds. However, i am pretty sure that it is


        <talk about damage type>

        """

        # important note - chance means each time the user travels. For example, if lightning strike 1 out of 5 times, this means that every few seconds (depending on the information the dict gives us), lightning will strike, but only 1 out 5 times will it land on the user (only in the jungle)


        weather = db.climate.find_one({"_id":"weather"})
        
        final_embed = None

        for risk_type in weather["risks"]["risk type"]:
            if risk_type == 'direct cause':
                if weather["weather"] == 'hurricane': # this one is just the direct cause, not the chance one. Hurricane results in an instant death, UNLESS you have special equipment on
                    final_embed = self.death_message(user, "weather", weather_type="hurricane")
            
                elif weather["weather"] == 'tornado':
                    # choose random object that falls down on the user, dealing 50 HP every 5 seconds
                    # honestly now that i think about it tornado is really more of a recurring damage type of weather risk, but it's not temperature so i really cant just do "risk type":["temperature"]
                    wait = weather["risks"]["wait"]
                    @tasks.loop(seconds=wait)
                    async def tornado_loop():
                        tornado_em = discord.Embed(color=discord.Color.dark_green())

                        # deal the recurring damage to the user
                        nonlocal weather
                        
                        # this deals the actual damage
                        db.healthpoints.update_one({"_id":user.id},{"$inc":{"health":-1*weather["risks"]["extra"]["damage"]}})
                        
                        # this adds the attacking message value to the final embed
                        tornado_em.add_field(name="\u200b",value=self.weather_attack_message(user,"tornado"))
                        
                        if self.user_is_dead(user): # this retusn a True if the user has died, and False if not.
                            # add a value to the finl embed and break from loop
                            death_em = self.death_message(user, "weather", weather_type="tornado")

                            await ctx.send(embed=tornado_em) # send the embed right now because there is no extra things we need and we have to send it now, or else the user wont see

                            tornado_loop.stop()
                        
                        else:
                            gdata = db.game.find_one({"_id":user.id})

                            if gdata["location"] in self.safe_places: # this means that the user is now in safe place that will not recieve any torndao attacks, so we will stop the tornado damaging loop
                                tornado_loop.stop()
                            
                    # this deals the recurring damage to the user over time due to staying in the weather
                    tornado_loop.start()
            
                elif weather["weather"] == 'flood':
                    # isntant death, just like a hurricane, but there is no possibility of losing your equipped weapon.

                    final_embed = self.death_message(user, "weather", weather_type="flood")

                # and thats really about it for the direct cause weather risk type
                # i can always add more
        
            elif risk_type == 'chance':
                number = random.randint(1,weather["risks"]["sample size"])

                for number_range in weather["choices"]:
                    if number in range(number_range[0],number_range[1]):
                        result = weather["choice"][number_range]
                    
                    # if statement chains for all the weather types
                    if weather["weather"] == 'icestorm':
                        if result == 'complete freeze':
                            gdata = db.game.find_one({"_id":user.id})

                            # user cannot do anything for 7 seconds, before breaking melting. This means you cannot eat any food, run away, ANYTHING. All commands (besides) general commands like .help, .commands, will be unavailable to the user.
                            
                            # freeze the user
                            # remember that when the user is frozen, the all incoming damage is tripled
                            db.game.update_one({"_id":user.id},{"$set":{"status":"frozen"}})

                            # sets the time unfrozen, according to the current time
                            gdata["time unfrozen"] = time.time() + 7
                            
                            db.game.find_one_and_replace({"_id":user.id},gdata)

                            await asyncio.sleep(10)
                        
                            del gdata["time unfrozen"]

                            gdata["status"] = "stationary"

                            # finally reset staus as stationary and delete the time unfrozen thing
                            db.game.find_one_and_replace({"_id":user.id},gdata)
                
                    elif weather["weather"] == 'thunderstorm':
                        wait = weather["risks"]["wait"]
                        @tasks.loop(seconds=wait)
                        async def thunderstorm_loop():
                            em = discord.Embed(                        tornado_em = discord.Embed(color=discord.Color.dark_green())
)
                            gdata = db.game.find_one({"_id":user.id})
                            
                            # also do soemthing about other locations look to the left side of coding screen

                            # bool for if the user is in a place that attracts a lot of lightning.
                            user_area_attracts_more_lightning = False

                            for location in weather["risks"]["extra"]["lightning strike locations"]:
                                if gdata["location"] == location: # this means that bot has found user in place that attracts more lightning
                                    user_area_attracts_more_lightning = True
                                    number = random.randint(1,weather["risks"]["extra"][location]["sample size"])

                                    hit_range = weather["risks"]["extra"]["lightning strike locations"][location]["hit range"]

                                    if number in range(hit_range[0],hit_range[1]):
                                        # deal the lightning damage
                                        db.healhpoints.update_one({"_id":user.id},{"$inc":{"health":-1*weather["risks"]["damage"]}})
                                
                            if not user_area_attracts_more_lightning:
                                # this means the user is not in a place that attracts a lot of lightning, but still outside, so still calculate RNG
                                if number in range(weather["risks"]["extra"]["lightning strike locations"]["other"]["hit range"]):
                                    # deal the lightning strike here
                                    db.healhpoints.update_one({"_id":user.id},{"$inc":{"health":-1*weather["risks"]["damage"]}})

                                    # lightning attack message
                                    em.add_field(name="Lightning Strike",value=self.weather_attack_message(user,"thunderstorm"))

                            await ctx.send(embed=em)

                            gdata = db.game.find_one({"_id":user.id})

                            if gdata["location"] in self.safe_places:
                                # stop the thunderstorm chance damage loop because user has left the dangerous place. however it will wait for the current iteration to FINISH, so there is still a possibility of getting hit by lightning
                                thunderstorm_loop.stop()
                        
                        thunderstorm_loop.start()
                    
                    # i can add more to this
        
        await ctx.send(embed=final_embed)
    
    def weather_attack_message(self,user:discord.User,weather:str) -> str:
        """Returns a message (`str`), containing information - specifically a message about the attack the weather did to to the user."""
        weather_attack_messages = {
            "tornado":[
                '__article__ __object__ just fell on __user__.',
                '__user__ was hit by __article__ __object__',
                'The tornado just dropped __article__ __object__ on __user__.',
                '__article__ __object__ decided to land on __user__\'s head.'
            ]
        }

        if weather == 'tornado':
            article_is_the = ['moon','UFO']

            article_is_not_the = ['Mount Everest','Egypt','Jupiter','Mars','USA','Donald Duck','Tesla Model Y','Tesla Model X']

            all_objects = []

            for item in article_is_not_the:
                all_objects.append(item)
            
            for item in article_is_the:
                all_objects.append(item)
            
            __object__ = random.choice(all_objects)
            
            sentence = random.choice(weather_attack_messages["tornado"])

            article = None

            if __object__ in article_is_not_the:
                for i in ['a','e','i','o','u']:
                    if __object__.startswith(i):
                        article = 'an'
                
                if article == None:
                    article = 'a'
            
            else:
                article = 'the'
            
            sentence.replace('__user__',user).replace('__article__',article).replace('__object__',__object__)
    
    def is_weather_dangerous(self) -> bool:
        """Return the risk of going outside in the game's current weather. Specifically, if the weather is safe, then method returns `False`. If the weather is anything else than safe, then it is dangerous, so method will return `True`."""
        weather = db.climate.find_one({"_id":"weather"})

        if weather["risks"]["risk type"] == 'safe':
            return False
        
        else:
            return True
        
    async def user_is_dead(self,user) -> bool:
        """Returns `True` if the user's health is below 0, and `False` if not."""
        hp = db.healthpoints.find_one({"_id":user.id})

        if hp["health"] <= 0:
            return True
        
        else:
            return False
    
    async def teleport_to_realm(self,user:discord.User,realm:str):
        """Method needs to sleep so remember to use async"""
        db.game.update_one({"_id":user.id},{"$set":{"status":"teleporting"}})

        await asyncio.sleep(10)
        
        db.game.update_one({"_id":user.id},{"$set":{"realm":realm}})

        return f"{user.mention} teleported to {realm.title()}."

    async def travel(self, ctx: commands.Context, location_str: str):
        """
        Walk the player to a certain place.
        Check if the player has a quest here in this location.
        """
        
        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)
        gdata = user_data["game"]
        location = user_data["location"]

        if location["confined"]:
            raise self.PlayerConfined

        m: discord.Message = await ctx.send(f"{user.mention} Walking to {location_str}...")
        
        await asyncio.sleep(gdata["walk time"])

        await m.edit(f'{user.mention} You have arrived at {location_str}!')

        location["location"] = location_str

        quests = user_data["quests"]

        for quest_type in ["main", "side"]:
            for quest in quests[quest_type]:
                try:
                    quest_location = quests[quest_type][quest]["location"]
                    if location_str == quest_location and quests[quest_type][quest]["progress"] == 0 and gdata["xp level"] >= quests[quest_type][quest]["required xp level"]:
                        
                        # current location equal to quest location
                        # quest progress is 0
                        # xp level at or above required xp level for quest

                        await ctx.send(f"{quest_type.title()} quest unlocked! Check `.{quest_type}` for more information.")

                except KeyError:
                    pass

    def hasAcc(self,user:discord.User) -> bool:
        """Method returns `True` if the user has an account, and `False` if not."""
        
        try:
            Database.Storages[str(user.id)]
        
        except KeyError:
            return False
    
    def deal_falcon_armor_damage(user_id,data:dict,armor_piece:str) -> dict:
        """Method returns the given `data` argument, which is a dictionary queered from the MongoDB database, containing data for a specific user's falcon. Method will modify the value of the key, which is the given `armor_piece` argument in the `data` dictionary."""
        db.falcon.update_one({"_id":user_id},{"$inc":{f"armor.{armor_piece}":-1}})
    
    def get_falcon_attack_type(self,data:dict) -> str:
        """This returns the type of shot the falcon has just used - `headshot`, `body shot` and `poor shot`, and `helm`, `chestplate`, and `wing shield` protect the falcon from these shots respectively. Only the headshot has anything special - every headshot is a critical hit, no matter what."""
        randrange = data["randrange"]
        number = random.randint(1,randrange)

        shot = None

        for _shot in data["chance"]:
            shot_range = data["chance"][_shot]
            if number in range(shot_range[0],shot_range[1]):
                shot = _shot
        
        return shot
    
    def deal_falcon_damage_to_enemy(self,shot:str,ability:str,player_data:dict,enemy_id:int) -> None:
        """Method will deal the needed damage to enemy"""
        damage = 0
    
    def get_armor_from_shot_falcon(self,shot:str) -> str:
        """Returns `str` - which tells you which armor gets damaged depending on the shot given"""
        armor_from_shot = {
            "headshot":"helmet",
            "body shot":"chestplate",
            "poor shot":"wing shield"
        }

        return armor_from_shot[shot]

    def process_all_damage_reduce_falcon(self,user_id:int,incoming_damage:int) -> float:
        falcon = db.falcon.find_one({"_id":user_id})

        total_damage_reduce_percentage = 0
        
        for armor_piece in falcon["armor"]:
            total_damage_reduce_percentage += falcon["armor"][armor_piece]["protection"]
        
        final_damage = incoming_damage * (1-total_damage_reduce_percentage) # this is the equivalent of dmg = dmg * (100-x)%

        return final_damage
        
    def process_all_damage_reduce(self,user:discord.User,damage) -> float:
        """Returns the final damage of after processing the damage taken away from damage reduction (armor)"""
        user_data = Database.getStorageData(user)
        
        hp = user_data["healthpoints"]

        final_reduce = 0

        for armor in hp["equipped armor"]:
            # go through all the armor in the user's hp (what the user is wearing right now is always in the healthpoints collection) and calculate entire armor reduce

            final_reduce += hp["equipped armor"][armor]["protection"]

        # subtract reduce by one, because percentage and multiply that to the damage, which reduces it
        final_damage = (1-final_reduce) * damage

        return final_damage
    
    async def all_quest_and_chest_actions(self, ctx, command_name: str, user: discord.User) -> str:
        """This is a coroutine - use `await`. Method will finish all the quest actions, deleteing or giving chests. Returns a final message for bot to send."""
        command_quests = self.quests_with_commands_list(command_name,user)

        if len(command_quests) != 0: # this means that ARE quests that needed user to use the command.
            for quest_id in command_quests:
                db.quests.update_one({"_id":user.id},{"$inc":{f"quests.{quest_id}.progress":1}})

                if self.finished_quest(quest_id,user):
                    quests = db.quests.find_one({"_id":user.id})

                    msg = self.give_chest(user,quests["quests"][quest_id]["difficulty"])

                    self.del_quest(quest_id,user)

                    await ctx.send(msg)

tools = Tools()