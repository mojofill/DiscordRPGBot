from copy import deepcopy
import discord
import random
import threading
import asyncio
import gc
from discord.ext import commands, tasks
from dev.tools import tools
from dev.api import db
from dev.db import Database
import time

class Boosts(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Potions extension ready. ')

    async def cog_command_error(self,ctx,error):
        if isinstance(error,commands.CheckFailure):
            pass
            
        else:
            raise error
    
    @commands.command()
    async def consume(self,ctx:commands.Context,potion_id:str) -> None:
        """Method (command) here APPLIES the potion effects on the user - code here deals with USING THE STORED VALUES in the backpack, coming from command `buy`, which stores the potion values in user's backpack. To look at getting the stats, go to `shop.py`. If you want to look at code TAKING AWAY THE EFFECT ON STATS, go to `tools.py`, where there will be a loop that subtracts the duration of the potion. When the potion duration is equal to zero, we TAKE AWAY THE POTION EFFECTS ON THE USER.

        3 main things with potions:
            1. getting stats (storing values in user's backpack)\n
            2. appling stats (user drinks potion, apply the effects on user)\n
            3. taking away stats/effects (potion's duration is finished, take away the effects on the user's stats.)\n
        
        We are dealing with the SECOND one right now, using the stored values from the database.
        """
        user = ctx.author
        
        user_data = Database.getStorageData(user)

        boosts = user_data["boosts"]
        duration_doc = user_data["duration"]
 
        # potion_type_ is the kind of potion it is, the group in which it belongs to. there are 5 kinds: luck, damage, value multipliers, mining speed, and wagon size

        # potion_type is the type of potion it is, whether it's common, legendary, mythical, etc.
        
        def get_potion_data() -> tuple:
            """Func returns a tuple containg the `potion_type` and `duration` of the potion."""
            potion_type = None
            duration = None

            for potion_type_ in boosts["local potions"]:
                for ID in boosts["local potions"][potion_type_]:
                    if ID == potion_id:
                        duration = boosts["local potions"][potion_type_][ID]["duration"]

                        potion_type = potion_type_
                        
                        return potion_type, duration
                    
            return None, None # if code reaches here then there is nothing to return besides None
        
        potion_type, duration = get_potion_data() # hover over func to see details
        
        if potion_type == None: # this means that the user tried to use a potion id that was not binded to a potion the user bought
            await ctx.send(f'You do not have potion with id `{potion_id}`')
            return

        potion_value = boosts["local potions"][potion_type][potion_id]["value"]
        potion_falcon_value = boosts["local potions"][potion_type][potion_id]["falcon value"]

        def applyPotionEffects(potion_value:int) -> None:
            """Function applies the potion's effects on the user's document in the database. Does not set the duration and everything else - func defined after this func does. """
            if potion_type == 'luck': # luck is for black market and gambling scams
                luck_type = boosts["local potions"]["luck"][potion_type][potion_type][potion_id]["type"]
                
                if luck_type == 'black market scams':
                    user_data["game"]["black market scams"] = False
                
                elif luck_type == 'rob':
                    # 1 out of 30 times you travel, you get robbed and 20% of your money gets taken
                    user_data["game"]["can be robbed":False]

            elif potion_type == 'damage increase':
                bp = user_data["backpack"]

                for weapon in bp["weapons"]:
                    potion_value += 1
                    bp["weapons"][weapon]["damage"] *= potion_value # this updates the base damage of every weapon in the user's backpack
                    
                user_data["backpack"]["weapons"] = bp["weapons"]

            elif potion_type == 'damage reduce':
                hp = user_data["healthpoints"]
                bp = user_data["backpack"]
                
                ratio = bp["armor ratio"]
                rounded_armor_values_of_new_damage_reduce = {}
                
                def storeRoundedData() -> None:
                    """Stores in the rounded_data dict all the values for  every piece of armor, accordingly to the ratio of iterated piece of armor damage reduction participation and total damage reduction"""
                    for armor in ratio: # for loop is for adding the rounded value of the percentage
                        percentage = ratio[armor]
                        
                        final_armor_value_float = percentage * potion_value

                        rounded_armor_values_of_new_damage_reduce[armor] = percentage * potion_value # get an amount that is equivalent in ratio when we compare < the old armor's damage reduction and total reduction > with < the new value we just calculated and the new total reduction >.

                        # we need to get a float with only 2 decimal points, no more.

                        bp["armor"]["final"][armor]["damage reduce"] = final_armor_value_float
                
                storeRoundedData() # hover over function to see details
                
                # as of right now, we have three important values: rounded armor percentage, accurate armor percentage (ratio) of the old total damage reduce, and the final armor set in the database. we need to store the accurate data in the duration

                # dont need to update anything because the dictionaries i use are pointers, not a seperate dict

                # now, all thats left to do is the turn the current active damage reduce potion (if there is one) off.
                
                for _potion_id in boosts["all active potions"]: # only damage reduce potions need this
                    if boosts["all active potions"][_potion_id]["type"] == 'damage reduce': # find all potions with damage reduce
                        loop_obj_id = duration_doc["potion duration"][_potion_id]["loop ID"]

                        duration_doc["current potion loops"][loop_obj_id] = False

                        queue: list = duration_doc["queue"]
                        queue.append(loop_obj_id) # queue is not sorted, but that doesnt matter because code later on will sort the queue
            
            elif potion_type == 'value multiplier':
                mines = user_data["mines"]

                for item in mines["wagon items"]:
                    mines["wagon items"][item]["value"] *= potion_value

            elif potion_type == 'mining speed':
                mines = user_data["mines"]

                for item in mines["wagon items"]:
                    mines["wagon items"][item]["drops"] *= potion_value
                
            elif potion_type == 'wagon size':
                mines = user_data["mines"]

                mines["wagon limit"] *= potion_value
            
            elif potion_type == 'energy efficiency':
                hp = user_data["healthpoints"]
                hp["energy gain time"] = potion_value
        
        applyPotionEffects(potion_value) # hover over func for details
        
        user_database = Database.getStorageData(user)
        
        duration_subtract = tools.get_potion_duration_subtract_loop(user, user_database, potion_id)

        duration_doc["potion duration"][potion_id] = {
            "loop ID":id(duration_subtract) # this sets in the database the specific id for the loop object for the specific potion id, for the specific user
        }

        await ctx.send(f'this is the loop id for potion id of {potion_id} - {duration_doc["potion duration"][potion_id]["loop ID"]}')

        all_potion_ids = list(boosts["all active potions"].keys())

        all_potion_ids.extend(list(boosts["local potions"]))
        
        def addPotionToActivePotions(potion_id:str) -> dict:
            """Modifies and returns the boosts (specifically the "all active potions" part of the boosts data) data for the user with given potion id."""

            boosts["all active potions"][potion_id] = {
                "duration":duration,
                "type":potion_type,
                "value":potion_value,
                "falcon value":potion_falcon_value,
                "time drank":time.time()
            }

            if potion_type == 'luck':
                luck_type = boosts["local potions"]["luck"][potion_type][potion_type][potion_id]["type"]

                boosts["all active potions"][potion_id]["luck type"] = luck_type
            
            return boosts
        
        def addPotionToDuration(potion_id:str) -> dict:
            """Modifies and returns the duration (specifically the "potion duration" part of the duration data) data for the user with given potion id."""

            duration_doc["potion duration"][potion_id] = {
                "duration":duration,
                "loop ID":id(duration_subtract)
            }

            return duration_doc

        def updateQueue() -> None:
            """Updates the queue part of the duration doc."""

            new_queue = {} # new queue to be updated onto the database

            save_data = {} # save data is here to reference to during update

            time_drank_to_potionID = {} # inverted queue is the same thing, except the keys are the start time and value is the potion id. This works because the start times are always unique

            sorted_potion_drink_times = []

            def setUnsortedQueue() -> None:
                """Sets up the queues, or lists of potion times."""

                for _potion_id in boosts["all active potions"]:
                    time_drank = boosts["all active potions"][_potion_id]["time drank"]

                    finish_time = time_drank + duration
                    
                    data = {
                        "time drank":time_drank,
                        "finish time":finish_time
                    }

                    save_data[potion_id] = data
                    time_drank_to_potionID[time_drank] = _potion_id
            
            def sortQueues() -> None:
                """Sort the queues into the ascending order, and also creates a list containing all the potion ids, and every element in the list has a corresponding time drank element in a different list."""

                nonlocal sorted_potion_drink_times

                unsorted_potion_drink_times = [save_data[_potion_id]["time drank"] for _potion_id in save_data] # this isnt sorted yet

                unsorted_potion_drink_times.sort() # this puts the list in ascending order

                sorted_potion_drink_times = unsorted_potion_drink_times # now the variable name will not be confused. This is a reference to the "unsorted" list, but the value (list) is now sorted
                
                # now we have a list containing the potion time dranks, and every time drank has a corresponding potion_id value
            
            def updateQueueDict() -> None:
                # now i need to make a queue consisting of the the ID for the potion tasks LOOP for each specific potion ID

                queue = []
                
                for time_drank in sorted_potion_drink_times:
                    potion_id_from_time_drank = time_drank_to_potionID[time_drank]

                    potion_loop_id = duration_doc["potion duration"][potion_id]["loop ID"]

                    data = {
                        "potion id":potion_id_from_time_drank,
                        "tasks loop id":potion_loop_id
                    }
                    
                    queue.append(data)
            
                # now we have a list of potion ids that corresponds the the potions sorted by time drank

            setUnsortedQueue()
            sortQueues()
            updateQueueDict()

            duration_doc["queue"] = new_queue # after all the functions were the queue is updated
        
        boosts = addPotionToActivePotions(potion_id) # hover over func to see details

        duration_doc = addPotionToDuration(potion_id) # hover over func to see details

        del boosts["local potions"][potion_type][potion_id] # deletes the potion data from the local potions, as data is being transfered over to a different document

        await ctx.send(f'{user.mention} used {potion_type} - {potion_type} ({potion_id}), duration {duration}.')
    
        await tools.all_quest_and_chest_actions(ctx,'consume',user)
        
        duration_subtract.start()

        await ctx.send('just did `duration_subtract.start()`, loop should be starting NOW.')

        updateQueue()

def setup(client: commands.Bot):
    client.add_cog(Boosts(client))