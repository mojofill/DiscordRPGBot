import random
import datetime
import asyncio
import discord
import time
import gc
from discord.ext import commands
from discord.ext import tasks
from dev.api import db
from dev.db import Database

"""There is something majorly wrong with the potion loops, with retrieving one of the past loops and restarting it."""

class Tools:
    def __init__(self):
        self.no_acc = 'You do not have an account. Make one with `.start`.'
        self.lime = discord.Color.from_rgb(144,238,144)
        self.safe_places = ['mineshaft','marketplace','grove','downtown','forge','vault','coliseum']
    
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

        gdata -= 50
    
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

    def getDurabilityOfWeapon(self, *, wpn_str: str) -> int:
        """This method gets the durability of weapon given by the `wpn_str` parameter."""

        durability_ranges = {
            "stick":[10,20], # from 10 to 20 uses in the stick before it breaks
        }

        ranges = durability_ranges[wpn_str]

        return random.randint(ranges[0], ranges[1])
        
    def getIfWeaponIsRepairable(self, wpn_str: str) -> bool:
        """This method returns a `bool`, `True` if weapon can be repaired and `False1 if not."""
    
    def getArmorDamageReductionRatio(self,data:dict) -> dict:
        """Method returns a `dict`, representing a ratio consisting of the damage reduction participation of every piece of armor in the data, compared to the `total_damage_reduce`."""
        total_damage_reduce = 0
        
        for armor in data["base"]:
            total_damage_reduce += data["base"][armor]["damage reduce"]
        
        ratio = {}

        for armor in data["base"]:
            ratio[armor] =  data["base"][armor]["damage reduce"] / total_damage_reduce # part over whole - simple fraction/ratio
        
        return ratio
    
    def death_message(self,user,death_type,monster_type=None,weather_type=None) -> str:
        """Returns a string that tells the user given that he or she has died, specifying which monster killed the user and how the user died."""
        monster_actions_past_tense = {
            "goblin":[
                'pummeled','punched','manslaughtered','crushed','demolished','smote','struck','crushed'
            ]
        }
        
        death_messages = {
            "monster":{
                "goblin":[
                '__user__ got __verb__ while attacking __monster__.',
                '__monster__ __verb__ __user__, crushing __user__\'s dreams of becoming the greatest.',
                '__user__ played themself and got __verb__ by __monster__'
                ]
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

            msg = random.choice(death_messages["monster"][monster_type])

            msg = msg.replace('__user__',user).replace('__verb__',past_tense_verb)
        
        elif death_type == 'weather':
            msg = random.choice(death_messages["weather"][weather_type]).replace('__user__',user)
        
        return msg
    
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
                "damage reduce":{
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
                "damage reduce":{
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
                "damage reduce":{
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

            if potion_type == "damage reduce":
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
                
                elif potion_type == 'damage reduce':
                    bp = db.backpack.find_one({"_id":user.id})

                    armor_ratio = bp["armor ratio"]

                    # all we want to do now is first, change everything back to what it was before the potion. Then, if there are potions queued up, apply those effects

                    base_total_damage_reduction = 0

                    for armor in bp["armor"]["base"]:
                        base_total_damage_reduction += bp["armor"]["base"][armor]["damage reduce"]

                    for armor in bp["armor"]["final"]:
                        armor_damage_reduction_participation = armor_ratio[armor] # this is a float for the percentage of damage reduction the armor has compared to the total damage reduction

                        base_armor_damage_reduce_value = armor_damage_reduction_participation * base_total_damage_reduction

                        bp["armor"]["final"][armor]["damage reduce"] = base_armor_damage_reduce_value
                    
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

                    loop = self.get_potion_duration_subtract_loop(user=user,potion_id=next_potion_ID,falcon=falcon) # recursion to start new loop. dude. this starts an entirely new loop, completely unrelated with the old damage reduce potion.

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

                    elif potion_type == 'damage reduce':
                        for armor_piece in falcon["armor"]:
                            falcon["armor"][armor_piece]["damage reduce"]

                            """I need to set up some sort of plan for affecting stats and reverting to what it was before"""
            
            loop = falcon_potion_duration_subtract
        
        else:
            loop = duration_subtract

        return loop # tasks loop for updating the potion duration in the potion collection
    
    def getEquipmentAttackTime(self, equipment_type: str, wpn_name: str = None) -> tuple:
        """During each attack the player will need to pick the weapon back up. This is called attack time, and some weapons have it every 3 times it is swung, every time it is swung, or every 5 times. All bows have a attack time every time it is used.
        Returns a tuple with index 0 = attack time, index 1 = per amount of swings"""
        
        if equipment_type == 'bow':
            return 0.5
        
        else:
            wpn_attack_times = {
                "mogo club":0.5, # we can change this later on
                "mogo spear":0.3,
                "mogo bow":1.5
            }

            return wpn_attack_times[wpn_name]
        
    def getMonsterFromPlayerLevel(self, level: int) -> str:
        """Takes in the player level `level` and returns a random monster (`str` format) based on the user's level. Returns a tuple containing `base_monster` and `monster_rank`"""
        
        def getBaseMonsterType():
            # computer pick random number from 1 to 1000
            monsters = {
                (1, 10):{ # players with levels 1 through 10 have these probability
                    "mogosok":[0, 900],
                    "jawsok":[900, 950],
                    "drasok":[950, 990],
                    "baursok":[990, 997],
                    "bugosok":[997, 998],
                    "gorsok":[998, 999]
                },
                (10, 20):{
                    "mogosok":[0, 850],
                    "jawsok":[850, 950],
                    "drasok":[950, 990],
                    "baursok":[990, 997],
                    "bugosok":[997, 998],
                    "gorsok":[998, 999]
                },
                (20, 30):{
                    "mogosok":[0, 800],
                    "jawsok":[800, 900],
                    "drasok":[900, 985],
                    "baursok":[985, 995],
                    "bugosok":[995, 998],
                    "gorsok":[998, 999]
                },
                (30, 40):{
                    "mogosok":[0, 750],
                    "jawsok":[750, 900],
                    "drasok":[900, 985],
                    "baursok":[985, 995],
                    "bugosok":[995, 998],
                    "gorsok":[998, 999]
                },
                (40, 50):{
                    "mogosok":[0, 700],
                    "jawsok":[700, 800],
                    "drasok":[800, 900],
                    "baursok":[900, 950],
                    "bugosok":[950, 990],
                    "gorsok":[990, 999]
                },
                (50, 60):{
                    "mogosok":[0, 650],
                    "jawsok":[650, 800],
                    "drasok":[800, 900],
                    "baursok":[900, 950],
                    "bugosok":[950, 990],
                    "gorsok":[990, 999]
                    
                }
            }

            number = random.randint(0, 999)
            
            for lvl_range in monsters:
                if level in range(lvl_range[0], lvl_range[1]):
                    for monster in monsters[lvl_range]:
                        monster_probability = monsters[lvl_range][monster]

                        if number in range(monster_probability[0], monster_probability[1]):
                            return monster # returns the base monster from above
        
        base_monster = getBaseMonsterType()

        def getMonsterRankFromBaseMonsterAndLevel():
            """Returns the monster rank based on the user's level and the base monster type"""
            specific_monster_from_base_monster = { # this is still based on the user level
                (1, 20):{
                    "mogosok":{ # for users level 1 through 20 the mogosoks are either rank 1 or 2
                        1:[1, 990],
                        2:[990, 999]
                    },
                    "jawsok":{
                        1:[1, 990],
                        2:[990, 999]
                    },
                    "drasok":{
                        1:[1, 990],
                        2:[990, 999]
                    },
                    "baursok":{
                        1:[1, 990],
                        2:[990, 999]
                    },
                    "bugosok":{
                        1:[1, 990],
                        2:[990, 999]
                    },
                    "gorsok":{
                        1:[1, 990],
                        2:[990, 999]
                    }
                },
                (20, 50):{
                    # finish this shit
                }
            }

            x = random.randint(0, 999)

            for level_range in specific_monster_from_base_monster:
                if level in range(level_range[0], level_range[1]):
                    monster_ranks_from_base_monster: dict = specific_monster_from_base_monster[level_range][base_monster] # this contains the monster ranks from base_monster

                    for monster_rank in monster_ranks_from_base_monster:
                        if x in range(monster_ranks_from_base_monster[monster_rank][0], monster_ranks_from_base_monster[monster_rank][1]):
                            return monster_rank
        
        monster_rank = getMonsterRankFromBaseMonsterAndLevel()

        return base_monster, monster_rank
    
    async def startMonsterAttackLoop(self, ctx: commands.Context, user: discord.User, monster_data: dict):
        """`monster_data` should be the return value of `spawnMonster`."""

        class Monster:
            def __init__(self, enemy: discord.User, *, name: str, wpn: dict = None, bow: str = None, shield: dict = None, attack_wait: int):
                self.name = name
                self.wpn = wpn
                self.bow = bow
                self.shield = shield
                self.enemy = enemy
            
            async def startAttackLoop(self):
                """Asyncronous method will starting asyncio loop that will get the monster to start attacking the user."""
                user = self.enemy
                
                user_data = Database.getStorageData(user)
                
                hp = user_data["healthpoints"]

                open_attack_chance = False # if this is set True then that means the AI thinks that this is a good time to fight the player, because his armor either broke or he is knocked down
                
                fightBool = False # if this becomes false then we stop the loop

                def getVerbOfWeaponName(weapon_name: str):
                    """Returns the past tense verb that goes with the weapon name"""
                    base_weapon_name = weapon_name.split(' ')[1]

                    verb_from_weapon = {
                        "club":"struck"
                    }

                    return verb_from_weapon[base_weapon_name]

                while fightBool:
                    if open_attack_chance: # this means the monster has decided to attack the user
                        """Code here will deal the actual damage to the user"""
                        try:
                            weapon_name: str = self.wpn["name"]
                            weapon_damage: int = self.wpn["damage"]

                            weapon_damage = tools.process_all_damage_reduce(user, weapon_damage)

                            hp["health"] -= weapon_damage

                            verb = getVerbOfWeaponName(weapon_name)

                            em = discord.Embed(
                                description=f'A {self.name} used its {weapon_name} and {verb} {user.mention}, dealing **{weapon_damage}**.'
                            )

                            em.add_field(name='\u200b', value=f"""
                                Remaining health: {hp["health"]}
                            """)
                            
                            await ctx.send(embed=em)

                        except TypeError: # meaning wpn was None (meaning the equipment the monster has is a bow) and is not "subscriptable" - cannot access keys of wpn because its not a dict
                            hp["health"] -= self.bow["damage"]
                    
                    else:
                        """Code here will decide whether to wait for an opening, randomly (read = stupidly) try to attack or run away (this is only if the user has not attacked and only retreated for a duration of time."""
                        
                        # how i think it should work:
                        # the monster usually waits for 3 seconds and if the user has not done anything it will attack
                        # other times it will be stupid and charge the player
                        # sometimes it will charge attack, but depending on the monster type the chances of charge attack will vary

                        # decide whether to wait or be stupid
                        number = random.randint(1, 9)

                        if number == 1: # just start attacking the user without waiting
                            open_attack_chance = True
                            
                            await asyncio.sleep(1) # at least sleep 1 second to give the user time to think and prepare
        
        name = monster_data["name"]
        attack_type = monster_data["attack type"]
        equipment_type = monster_data["equipment type"]
        shield = monster_data["shield"]
        attack_wait = monster_data[equipment_type]["attack time"] # the time it takes for a single attack

        if attack_type == 'melee':
            await ctx.send('code has reached here')
            monster_wpn = monster_data["weapon"]
            monster = Monster(user, name=name, wpn=monster_wpn, shield=shield, attack_wait=attack_wait)
        
        else:
            monster_bow = monster_data["bow"]
            monster = Monster(user, name=name, bow=monster_bow, shield=shield, attack_wait=attack_wait)

        # starts the actual monster attack loop
        await monster.startAttackLoop()

    async def spawnMonster(self, ctx: commands.Context, client: commands.Bot, user: discord.User, monster_type: str, monster_rank: int) -> bool or dict:
        """Method spawns a monster. User can either choose to engage the monster, or on rare occasions the monster will come towards to user. Returns `True` if the monster spawn worked, `False` if not (the user might have declined)"""
        
        """
            monster_type = name of monster
            monster_rank = the ranking of the monster in the monster hierarchy
        """

        def getMonster():
            def getWpnData(base_wpn_name: str) -> tuple:
                """Takes in the base weapon name, uses the monster rank to decide on a final weapon which is has that weapon as a base but modifications designed for a monster that specific rank."""

                wpn_data_dict = {
                    "mogo club":{
                        "durability":{
                            1:[15,25],
                            2:[25,35],
                            3:[35,45],
                            4:[40,50],
                        },
                        "damage":{
                            1:[5,10],
                            2:[13,20],
                            3:[23,30],
                            4:[32,38]
                        }
                    },
                    "mogo spear":{
                        "durability":{
                            1:[10,20],
                            2:[20,30],
                            3:[30,45],
                            4:[45,55] 
                        },
                        "damage":{
                            1:[3,9],
                            2:[12,19],
                            3:[21,29],
                            4:[32,38]
                        }
                    }
                }

                new_wpn_name_dict = {
                    "mogo club":{
                        1:"mogo club",
                        2:"spiked mogo club",
                        3:"spiked mogo club",
                        4:"spiked mogo club"
                    },
                    "mogo spear":{
                        1:"mogo spear",
                        2:"sharpened mogo spear",
                        3:"steel mogo spear",
                        4:"sharpened steel mogo spear"
                    }
                }

                wpn_durability_range = wpn_data_dict[base_wpn_name]["durability"][monster_rank]

                wpn_damage_range = wpn_data_dict[base_wpn_name]["damage"][monster_rank]

                wpn_durability = random.randint(wpn_durability_range[0], wpn_durability_range[1])

                wpn_damage = random.randint(wpn_damage_range[0], wpn_damage_range[1])

                new_wpn_name = new_wpn_name_dict[base_wpn_name][monster_rank]

                return wpn_durability, wpn_damage, new_wpn_name
            
            def getBowData(base_bow_name) -> tuple:
                """Read the `__doc__` of `getWpnData`, but replace weapon with bow and you get the gist."""
                bow_data_dict = {
                    "mogo bow":{
                        "durability":{
                            1:[15,25],
                            2:[25,35],
                            3:[35,45],
                            4:[40,50],
                        },
                        "damage":{
                            1:[8,13],
                            2:[15,23],
                            3:[25,30],
                            4:[32,41]
                        }
                    }
                }

                new_bow_name_dict = {
                    "mogo bow":{
                        1:"mogo bow",
                        2:"reinforced mogo bow",
                        3:"reinforced mogo bow",
                        4:"reinforced mogo bow"
                    }
                }

                bow_durability_range = bow_data_dict[base_bow_name]["durability"][monster_rank]
                bow_durability = random.randint(bow_durability_range[0], bow_durability_range[1])

                bow_damage_range = bow_data_dict[base_bow_name]["damage"][monster_rank]
                bow_damage = random.randint(bow_damage_range[0], bow_damage_range[1])

                new_bow_name = new_bow_name_dict[base_bow_name][monster_rank]

                return bow_durability, bow_damage, new_bow_name
            
            def getShieldData():
                monster_shields = {
                    "mogosok":{
                        1:{
                            "range":1,
                            "choices":{
                                "mogo shield":[0,1]
                            }
                        }
                    }
                }

                number = random.randint(0, monster_shields[monster_type][monster_rank]["range"] - 1)

                shield_name = None

                for shield_ in monster_shields[monster_type][monster_rank]["choices"]:
                    sheild_probability = monster_shields[monster_type][monster_rank]["choices"][shield_]

                    if number in range(sheild_probability[0], sheild_probability[1]):
                        shield_name = shield_
                        break
                
                shield_dict = {
                    "mogo shield":{
                        "durability":[10,15],
                        "knockback":[3,6] # this dictates the number of time a shield can take a hit in a row before the user gets knocked on their feet.
                    }
                }

                durability_range = shield_dict[shield_name]["durability"]
                knockback_range = shield_dict[shield_name]["knockback"]

                durability = random.randint(durability_range[0], durability_range[1])
                knockback = random.randint(knockback_range[0], knockback_range[1])

                new_shield_name_dict = {
                    "mogo shield":{
                        1:"mogo shield",
                        2:"reinforced shield",
                        3:"steel shield",
                        4:"steel alpha shield"
                    }
                }

                new_shield_name = new_shield_name_dict[shield_name][monster_rank]

                return durability, knockback, new_shield_name
            
            def getMonsterHealth():
                monster_health_dict = {
                    "mogosok":{
                        1:13,
                        2:40,
                        3:100,
                        4:400
                    },
                    "drasok":{
                        1:13,
                        2:40,
                        3:80,
                        4:300
                    },
                    "baursok":{
                        1:45,
                        2:75,
                        3:130,
                        4:500
                    },
                    "bugosok":{
                        1:30,
                        2:70,
                        3:130,
                        4:450
                    },
                    "gorsok":{
                        1:300,
                        2:600,
                        3:800,
                        4:950
                    }
                }

                return monster_health_dict[monster_type]
            
            def getMonsterEquipmentData():
                monster_attack_type_probabilities = {
                    "mogosok":{
                        "range":10,
                        "choices":{
                            "melee":[1,7],
                            "bow":[7,10]
                        }
                    }
                }

                nonlocal monster_type

                monster_attack_type_data = monster_attack_type_probabilities[monster_type]

                number = random.randint(1, monster_attack_type_data["range"] - 1)

                monster_attack_type = None

                for monster_attack_type_ in monster_attack_type_data["choices"]:
                    if number in range(monster_attack_type_data["choices"][monster_attack_type_][0], monster_attack_type_data["choices"][monster_attack_type_][1]):
                        monster_attack_type = monster_attack_type_
                        break
            
                if monster_attack_type == None:
                    print('monster attack type is None')
                
                base_equipment_name_dict = {
                    "melee":{
                        "mogosok":{
                            "range":8,
                            "choices":{
                                "mogo club":[0,5],
                                "mogo spear":[5,8]
                            }
                        }
                    },
                    "bow":{
                        "mogosok":{
                            "range":1,
                            "choices":{
                                "mogo bow":[0,2]
                            }
                        }
                    }
                }

                monster_base_equipment_data = base_equipment_name_dict[monster_attack_type][monster_type]

                equipment_name = None

                number = random.randint(0, monster_base_equipment_data["range"] - 1)

                for equipment_name_ in monster_base_equipment_data["choices"]:
                    if number in range(monster_base_equipment_data["choices"][equipment_name_][0], monster_base_equipment_data["choices"][equipment_name_][1]):                        
                        equipment_name = equipment_name_
                        break
            
                if monster_attack_type == 'melee':
                    equipment_durability, equipment_damage, new_equipment_name = getWpnData(equipment_name)
                
                else:
                    equipment_durability, equipment_damage, new_equipment_name = getBowData(equipment_name)
                
                return equipment_durability, equipment_damage, equipment_name, new_equipment_name, monster_attack_type

            # code below gets the monster data
            monster_health = getMonsterHealth()
            
            durability, damage, base_equipment_name, name, monster_attack_type = getMonsterEquipmentData() # monster attack type is the type of equipment the monster is using - weapon or bow
            shield_durability, shield_knockback, shield_name = getShieldData()

            if monster_attack_type == 'bow':
                attack_time = self.getEquipmentAttackTime(base_equipment_name, name)
            
            else:
                attack_time = self.getEquipmentAttackTime(base_equipment_name, name)

            if shield_durability == None:
                shield_data = None
            
            else:
                shield_data = {
                    "name":shield_name,
                    "durability":shield_durability,
                    "knockback":shield_knockback
                }

            if monster_attack_type == 'melee':
                equipment_type = 'weapon'
            
            else:
                equipment_type = 'bow'

            new_monster_data = {
                "name":monster_type,
                "health":monster_health,
                "attack type":monster_attack_type,
                equipment_type:{
                    "name":name,
                    "durability":durability,
                    "damage":damage,
                    "attack time":attack_time
                },
                "shield":shield_data,
                "equipment type":equipment_type
            }
            
            return new_monster_data # returns the entire data for the monster
        
        monster_data = getMonster()

        base_monster = monster_data["name"]
        health = monster_data["health"]
        attack_type = monster_data["attack type"] # this is either `bow` or `melee`
        equipment_type = monster_data["equipment type"] # this is either `bow` or `weapon`

        equipment_data = monster_data[equipment_type] # contains: name, durability, damage, and attack time of the equipment the monster is using.

        shield_name = monster_data["shield"] if monster_data["shield"] != None else None

        m: discord.Message = await ctx.send(f"{user.mention} you have found a **{base_monster}**! Enter `.more` to find out more about this monster. React with 🇾 to engage with the {base_monster}, 🇳 to pass. Message will timeout in 60 seconds.")

        await m.add_reaction('🇾')
        await m.add_reaction('🇳')

        em = discord.Embed(
            title='Monster Found!',
            description='Stay alert...',
            timestamp=datetime.datetime.utcnow()
        )

        em.add_field(name="Monster Data", value=f"""
            Monster Type: {base_monster}
            Attack Type: {attack_type}
            Equipment: {equipment_type}
            Equipment name: {equipment_data["name"]}
            Shield: {shield_name}
        """)

        em.set_author(name=user, icon_url=user.avatar_url)
        em.set_footer(text='You can use the Thokim Epitome gifted by the Mages to find out more about a monster by `.more <object name>`. For example, `.more mogosok`.')
        
        await ctx.send(embed=em)

        if random.randint(1, 100) == 1: # monster has chosen to attack the user
            await ctx.send(f'{user.mention} Watch out! A {base_monster} has decided to attack you!')
        
        else:
            ans = None # either yes or no
            
            def check(reaction: discord.Reaction, user_: discord.User):
                nonlocal ans

                if reaction.emoji in ['🇾','🇳'] and user_.id == user.id and reaction.message.id == m.id:
                    ans = reaction.emoji # save the reaction emoji
                
                    return True
                
                return False
            
            try:
                await client.wait_for("reaction_add", check=check, timeout=60.0)
            
            except asyncio.TimeoutError:
                await ctx.send(f'{user.mention} you have timed out ❌')
            
            if ans == '🇾':
                await ctx.send('please let this work')

                return monster_data
        
            else: # user has passed
                return False

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
    
    async def deal_weather_damage(self,user,ctx):
        """
        We will only deal with direct cause and chance, because there will already be a tasks loop dealing the recurring damage to the user, we do not have to call tools.deal_weather_damage all the time for the user when he or she goes out in the rain

        Direct cause:
            Weather that have direct cause as one of its risk types means that going out in this weather will, without exception, attempt to deal some kind of damage to ther user. Weather with direct cause as one of it's risk types include but does not limit to:
                1. Hurricane
                2. Tornado
                3. Flood
            
            Going out in this weather will always try cause some kind of damage to you, whether you like it or not. However, if you have special equipment, for example a boat for transportation in floods, or strong armor to reduce incoming damage (and if possible, a speed boosting potion to get to where you need faster.)

            1. Hurricane
                There is nothing special about a hurricane, except there is a possibility of losing your equiped weapon

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
        
        final_embed = discord.Embed(color=self.lime,title=weather["weather"])

        for risk_type in weather["risks"]["risk type"]:
            if risk_type == 'direct cause':
                if weather["weather"] == 'hurricane': # this one is just the direct cause, not the chance one. Hurricane results in an instant death, UNLESS you have special equipment on
                    final_embed.add_field(name="Death",value=self.death_message(user,"weather",weather_type="hurricane"))
            
                elif weather["weather"] == 'tornado':
                    # choose random object that falls down on the user, dealing 50 HP every 5 seconds
                    # honestly now that i think about it tornado is really more of a recurring damage type of weather risk, but it's not temperature so i really cant just do "risk type":["temperature"]
                    wait = weather["risks"]["wait"]
                    @tasks.loop(seconds=wait)
                    async def tornado_loop():
                        tornado_em = discord.Embed(color=self.lime)

                        # deal the recurring damage to the user
                        nonlocal weather
                        
                        # this deals the actual damage
                        db.healthpoints.update_one({"_id":user.id},{"$inc":{"health":-1*weather["risks"]["extra"]["damage"]}})
                        
                        # this adds the attacking message value to the final embed
                        tornado_em.add_field(name="\u200b",value=self.weather_attack_message(user,"tornado"))
                        
                        if self.user_is_dead(user): # this retusn a True if the user has died, and False if not.
                            # add a value to the finl embed and break from loop
                            tornado_em.add_field(name="Death",value=self.death_message(user,"weather",weather_type="tornado"))

                            await ctx.send(embed=tornado_em) # send the embed right now because there is no extra things we need and we have to send it now, or else the user wont see

                            tornado_loop.stop()
                        
                        else:
                            gdata = db.game.find_one({"_id":user.id})

                            if gdata["location"] in self.safe_places: # this means that the user is now in safe place that will not recieve any torndao attacks, so we will stop the tornado damaging loop
                                tornado_loop.stop()
                            
                    # this deals the recurring damage to the user over time due to staying in the weather
                    tornado_loop.start()
            
                elif weather["weather"] == 'flood':
                    # isntant death, just like a hurricane, but there is no possibility of losing your equiped weapon.
                    final_embed.add_field(name='Death',value=self.death_message(user,death_type="weather",weather_type="flood"))

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
                            em = discord.Embed(color=tools.lime)
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

    def travel(self,user:discord.User,location:str) -> str:
        "Method will return the string `walking` if the user is walking. If not, then method will run some code, and return a message that says the user ran or flew somewhere."
        gdata = db.game.find_one({"_id":user.id})
        
        transport_method = gdata["default transport"]

        energytaken = None

        weather = db.climate.find_one({"_id":"weather"})

        print(weather)

        if weather["risk type"] != "safe":
            self.deal_weather_damage()

        if transport_method == 'running':
            energytaken = gdata["running energy taken"]
            db.healthpoints.update_one({"_id":user.id},{"$inc":{"energy":-1*energytaken}})
        
        elif transport_method == 'flying':
            energytaken = gdata["flying energy taken"]
            db.falcon.update_one({"_id":user.id},{"$inc":{"energy":energytaken}})

        else:
            return "walking"
        
        travel_verb_dict = {
            "walking":"walked",
            "running":"ran",
            "flying":"flew"
        }

        travel_verb = travel_verb_dict[transport_method]

        db.game.update_one({"_id":user.id},{"$set":{"location":location}})

        msg = f'{user.mention} has {travel_verb} to {location} and spent {energytaken}.'

        return msg


    async def walkuser(self,ctx,user:discord.User,location:str) -> None:
        """NOTE - ASYNC FUNCTION. USE AWAIT. Methods runs code to sleep for however long the user's walking time is, and then saves the user's location as the location given."""
        gdata = db.game.find_one({"_id":user.id})

        await ctx.send(f'{user.mention} You are walking to {location}...')

        await asyncio.sleep(gdata["walk time"])

        await ctx.send(f'{user.mention} You have arrived at {location}.')

        db.game.update_one({"_id":user.id},{"$set":{"location":location}})

    def finished_quest(self,quest_id:int,user:discord.User) -> bool:
        """Method returns `True` if the user has finished the quest of the given `quest_id`, and `False` if not."""
        quests = db.quests
        # GET REQUIRED AMOUNT OF QUEST_ID, COMPARE PROGRESS, TELL IF USER HAS FINISHED QUEST YET. GO TO attack.py AND FINISH CODE THERE

        quest = quests.find_one({"_id":user.id})

        if quest["quests"][quest_id]["progress"] == quest["quests"][quest_id]["amount required"]:
            return True
        
        return False


    def del_quest(self,quest_id:int,user:discord.User) -> None:
        """Method deletes the dict value of the key `quest_id`."""
        quests_ = db.quests
        quests = quests_.find_one({"_id":user.id})

        del quests["quests"][quest_id]

        quests_.update_one({"_id":user.id},{"$set":{"quests":quests["quests"]}})
        

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
            total_damage_reduce_percentage += falcon["armor"][armor_piece]["damage reduce"]
        
        final_damage = incoming_damage * (1-total_damage_reduce_percentage) # this is the equivalent of dmg = dmg * (100-x)%

        return final_damage
        
    def process_all_damage_reduce(self,user:discord.User,damage) -> float:
        """Returns the final damage of after processing the damage taken away from damage reduction (armor)"""
        hp = db.healthpoints.find_one({"_id":user.id})

        final_reduce = 0

        for armor in hp["armor"]:
            # go through all the armor in the user's hp (what the user is wearing right now is always in the healthpoints collection) and calculate entire armor reduce

            final_reduce += hp["equiped armor"][armor]["damage reduce"]

        # subtract reduce by one, because percentage and multiply that to the damage, which reduces it
        final_damage = (1-final_reduce) * damage

        return final_damage
    
    async def all_quest_and_chest_actions(self,ctx,command_name:str,user:discord.User) -> str:
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
            
    def drop(self,monster_type:str,item_type:str="parts") -> list:
        """Returns a list of all the drops the given monster has dropped for the user. Code currently doesn't adjust to user's use of luck potions, but should be taken in account. If looking for dropped weapons, then pass in `item_type="weapons"`. `item_type` defaults to `"parts"`. Finish code later."""

        if item_type == 'parts':
            monster_drops = {
                "goblin":{
                    "sample size":1,
                    "choices":{
                        "goblin horn":[0,1]
                    }
                },
                "minotaur":{
                    "sample size":3,
                    "choices":{
                        "minotaur horn":[0,3]
                    },
                },
                "cyclops":{
                    "sample size":1,
                    "choices":{
                        "cyclops eye":[0,1]
                    }
                },
                "ogre":{
                    "sample size":3,
                    "choices":{
                        "tough ogre skin":[0,3]
                    }
                },
                "chimera":{
                    "sample size":3,
                    "choice":{
                        "chimera serpent tail":[0,1],
                        "chimera lion mane":[1,2]
                    }
                },
                "basilisk":{
                    "sample size":1,
                    "choices":{
                        "basilisks fang":[0,1]      
                    }
                },
                "mogosok":{
                    "sample size":2,
                    "choices":{
                        "mogosok fang":[0,1]
                    }
                },
                "drasok":{
                    "sample size":6,
                    "choices":{
                        "drasok guts":[0,4],
                        "drasok wings":[4,5]
                    }
                },
                "bugosok":{
                    "sample size":5,
                    "choices":{
                        "bugosok bone":[0,2],
                        "bugosok claw":[0,4]
                    }
                },
                "jawsok":{
                    "sample size":5,
                    "choices":{
                        "jawsok fang":[0,3],
                        "jawsok horn":[2,4]
                    }
                },
                "stormsok":{
                    "sample size":5,
                    "choices":{
                        "galestaff":[0,1],
                        "stormsok ballon":[0,5]
                    }
                }
            }

            items_dropped = []

            num = random.randint(1,monster_drops[monster_type])
            
            for item in monster_drops[monster_type]["choices"]:
                drop_range = monster_drops[monster_type][item]

                if num in range(drop_range[0]) or num == drop_range[0]:
                    items_dropped.append(item)
                
            return items_dropped

tools = Tools()