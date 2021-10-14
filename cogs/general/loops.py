import discord,random,json,threading,time
from discord.ext import commands,tasks
from dev.tools import tools
from dev.api import db

class Loops(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.add_items.start()
        self.add_mining_speed.start()
        self.change_daily_quests.start()
        self.hourly_shipments.start()
        self.daily_shipments.start()
        self.weekly_shipments.start()
        self.give_credits.start()
        print('Loops extension ready. ')

        self.items = {
            "miner":{
                "stone":[1,30],
                "dirt":[30,55],
                "coal":[55,75],
                "marble":[75,90],
                "clay":[90,100]
            },
            "supplier":{ # finish this later
                "":[]
            },
            "distributor":{
                "":[]
            },
            "trader":{
                "":[]
            },
            "merchant":{
                "":[]
            },
            "entrepeneur":{
                "":[]
            }
        }

        self.quest_choices = {
            'flip a coin __value__ times':{
                "limit":20,
                "commands with quest":[
                    'coinflip'
                ]
            }, 
            'hunt __value__ times':{
                "limit":20,
                "commands with quest":[
                    'hunt'
                ]
            },
            'defeat __value__ monsters':{
                "limit":20,
                "commands with quest":[
                    'attack'
                ]
            },
            'fight __value__ monsters':{
                "limit":20,
                "commands with quest":[
                    'attack'
                ]
            },
            'sell __value__ items':{
                "limit":20,
                "commands with quest":[
                    'sell'
                ]
            },
            'climb up the Temple of Power __value__ times':{
                "limit":20,
                "commands with quest":[
                    'meditate'
                ]
            },
            'upgrade pickaxe __value__ times':{
                "limit":10,
                "commands with quest":[
                    'upgrade'
                ]
            },
            'upgrade wagon __value__ times':{
                "limit":10,
                "commands with quest":[
                    'upgrade'
                ]
            },
            "consume __value__ potions":{
                "limit":10,
                "commands with quest":[
                    'consume'
                ]
            }
        }

    @tasks.loop(seconds=1)
    async def add_items(self):
        mines = db.mines
        users = mines.find({"keep adding":True})
        
        for user in users:
            def run():
                _id = user["_id"]
                number = random.randint(1,100)

                for itype in self.items[user["mineshaft level"]]:
                    level = user["mineshaft level"]
                    if number in range(self.items[level][itype][0],self.items[level][itype][1]):
                        # "amount" key is for the actual AMOUNT of that item you have. For example, every second a type of item drops 5 times. Your mineshaft has been running for 6 seconds. This means you have 30 amount of that item.
                        user["wagon items"][itype]["amount"] += user["wagon items"][itype]["drops"]

                        # "total" may seem similar to "amount", but total means the total VALUE. That is, the total GOLD NUGGETS you collected, depending on the total amount of items you had and 
                        user["wagon items"][itype]["total"] += user["wagon items"][itype]["drops"] * user["wagon items"][itype]["value"]

                        mines.update_one({"_id":_id},{"$set":{"wagon items":user["wagon items"]}})
                
            threading.Thread(target=run).start()

    @tasks.loop(seconds=1)
    async def add_mining_speed(self):
        mines = db.mines
        users = mines.find({})

        for user in users:
            def run():
                _id = user["_id"]
                if user["keep adding"] == True:
                    if user["all items"] >= user["wagon size"]:
                        limit = user["wagon size"]
                        mines.update_one({"_id":_id},{"$set":{"all items":limit}})
                        mines.update_one({"_id":_id},{"$set":{"keep adding":False}})
                
                else:
                    mines.update_one({"_id":_id},{"$inc":{"all items":user["mining speed"]}})
            
            threading.Thread(target=run).start()


    @tasks.loop(seconds=86400) # 86400 seconds in a day
    async def daily_shipments(self):
        allusers = db.chests.find({})
        for user in allusers:
            def run():
                _id = user["_id"]
                db.chests.update_one({"_id":_id},{"$set":{"unclaimed shipments.daily":True}})
            
            threading.Thread(target=run).start()
        

    @tasks.loop(seconds=604800) # 604800 seconds in a week
    async def weekly_shipments(self):
        allusers = db.chests.find({})
        for user in allusers:
            def run():
                _id = user["_id"]
                db.chests.update_one({"_id":_id},{"$set":{"unclaimed shipments.weekly":True}})
            
            threading.Thread(target=run).start()


    @tasks.loop(hours=1)
    async def hourly_shipments(self): # one hour in a day. duh lmao
        allusers = db.chests.find({})
        for user in allusers:
            def run():
                _id = user["_id"]
                db.chests.update_one({"_id":_id},{"$set":{"unclaimed shipments.hourly":True}})
            
            threading.Thread(target=run).start()

    @tasks.loop(seconds=86400)
    async def give_credits(self):
        pass

    @tasks.loop(seconds=86400) # 86400 seconds in a day
    async def change_daily_quests(self):
        quests_ = db.quests

        player_quests = quests_.find({})

        for player in player_quests:
            def run():
                user_id = player["_id"]

                all_quest_ids = list(player["quests"].keys())

                for quest_id in all_quest_ids:
                    del player["quests"][quest_id]
                
                quests_.update_one({"_id":user_id},{"$set":{"quests":player["quests"]}})

                quests_to_give = random.randint(3,5)

                quests = quests_.find_one({"_id":user_id})

                quest_choices_name = list(self.quest_choices.keys())

                quest_choices_values = list(self.quest_choices.values())

                for i in range(quests_to_give):
                    quest_name = random.choice(quest_choices_name)

                    equipped_quest_index = quest_choices_name.index(quest_name)

                    quest = quest_choices_values[equipped_quest_index]

                    limit = quest["limit"]

                    __value__ = random.randint(1,limit)

                    quest_name = quest_name.replace('__value__',str(__value__))

                    if __value__ < 0.5 * limit:
                        difficulty = 'Easy'
                    
                    elif __value__ >= 0.5 * limit and __value__ < 0.75 * limit:
                        difficulty = 'Medium'

                    else:
                        difficulty = 'Hard'

                    all_quest_ids = list(quests["quests"].keys())
                    
                    choice_range = 30

                    # count = 0
                    
                    while True:
                    # count += 1
                        new_quest_id = random.randint(1,choice_range)

                        if new_quest_id not in all_quest_ids:
                            break
                    
                    # else:
                    #   if count == choice_range:
                    #     choice_range += 10

                    quests["quests"][str(new_quest_id)] = {
                        "name":quest_name,
                        "difficulty":difficulty,
                        "amount required":__value__,
                        "commands with quest":quest["commands with quest"],
                        "progress":0
                    }

                quests_.update_one({"_id":user_id},{"$set":{"quests":quests["quests"]}})

            threading.Thread(target=run).start()

def setup(client):
    client.add_cog(Loops(client))