from pymongo.errors import DuplicateKeyError
from datetime import timedelta, datetime
import discord, asyncio, threading, random
from discord.ext.commands import Context
from string import ascii_letters
from discord.ext import commands, tasks
from dev.tools import tools
from dev.api import db

# important to remember that falcons have names that we will write in the games - "<enemy_falcon_name> ran past <falcon_name>", "<enemy_falcon_name> lunged at <falcon_name>", instead of <user.mention> ran past <enemy.mention>, as sometimes these enemies are bots, and have no discord user


class Falcon_games(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.connecting_users()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ventus - Falcon games ready.')
    
    @commands.command()
    async def register(self,ctx:Context,mode:str,invisible=None):
        mode,invisible = mode.lower(),invisible.lower()
        if mode not in ['arena','race']:
            await ctx.send('Invalid `mode` argument - please select between **arena** and **race**. No other arguments accepted.')
            return
        
        if invisible != None and invisible not in ['invis','invisible']:
            await ctx.send(f'Invalid argument - `{invisible}``. Please enter `invis` or `invisible` if you wish to be invisible.')
            return
        
        user = ctx.author

        if mode == 'arena':
            data = db.falcon_arena.find_one({"_id":user.id})

            if data == None:
                db.falcon_arena.insert_one(
                    {
                        "_id":user.id,
                        "in match":False,
                        "match ID":None,
                        "finding match":False, # should be discord.User instance
                        "win":0,
                        "loss":0,
                        "coins earned":0
                    }
                )

            else:
                await ctx.send(f'{user.mention} You are already registered in the arena!')
                return

            await ctx.send(f'{user.mention} Registed you in the fighting arena.')

        elif mode == 'race':
            data = db.falcon_race.find_one({"_id":user.id})
            
            if data == None:
                db.falcon_race.insert_one(
                    {
                        "_id":user.id,
                        "match ID":None, # the ID of the game that the user is playing in. The ID will be the "_id" key of the game document in whichever arena the user is in
                        "finding match":False, # list of all the users inside the game
                        "commmands available":False,
                        "coins earned":0
                    }
                )
            else:
                await ctx.send(f'{user.mention} You are already registed in the racing competitions! ')
                return

    @commands.command()
    async def readyup(self,ctx:Context,game_type):
        if game_type not in ['arena','race']:
            await ctx.send('Invalid `.readyup` command argument - game is not in `arena` or `race`. PLease try again, and if you do not understand what `.readyup` does, please check out `.help readyup`.')
            return

        user = ctx.author
        
        arena,race = db.falcon_arena.find_one({"_id":user.id}),db.falcon_race.find_one({"_id":user.id})

        if arena == None or race == None:
            await ctx.send('You are not registered to play in the arena or race yet. Enter `.register` if you want to play.')
            return

        await ctx.send('Almost done with the readyup. Please select a channel to bind all messages from other player\'s attacks. Go to that channel, (and can be the one you just used `.readyup`), and enter `.bind`. Timeout - 30 seconds.')

        def check(m:discord.Message):
            return m.author.id == user.id and m.content == '.bind'
        
        channel = None

        try:
            channel = await self.client.wait_for("message",check=check,timeout=30).channel
        except asyncio.TimeoutError:
            await ctx.send(f'{user.mention} you have timed out.')
            return

        if game_type == "arena":
            db.arena.update_one({"_id":user.id},{"$set":{"finding match":True}})
        else:
            db.race.update_one({"_id":user.id},{"$set":{"finding match":True}})
        
        # now we are going to finally make the game document in the falcon games
        
        # set the player_limit
        if game_type == 'arena':
            player_limit = 2
        else:
            player_limit = 8

        games = db.falcon_games.find({"game type":game_type},{"filled":False})

        # this meability no games are being hosted for that game_type
        if not bool(list(games)): # games collection's MongoDB Cursor object is empty
            # since there are no current games hosted, we make one
            falcon = db.falcon.find_one({"_id":user.id})
            trophies = falcon["trophies"]

            trophy_ranges = {
                (0,20):"Bronze",
                (20,50):"Silver",
                (50,100):"Gold",
                (100,200):"Platinum",
                (200,400):"Prodigy",
                # above 500 is champion
            }

            trophy_range_name = None
            
            for trophy_range in trophy_ranges:
                if trophies in range(trophy_range[0],trophy_range[1]):
                    trophy_range_name = trophy_ranges[trophy_range]
                    break
            
            if trophy_range_name == None: # this meability that the trophy range is 400+, which meability the user is a champion
                trophy_range_name = "Champion"

            game = {
                "game type":game_type,
                "match started":False, # "match started" is here to tell check if the user is trying to use commands specific to the game, but if it hasnt started yet bot will tell the user game has not started and you cant use that command yet.
                "players":[user.id],
                "player limit":player_limit,
                "player channels":{
                    user.id:channel
                },
                "falcon names from ID":{
                    user.id:falcon["name"]
                },
                "commands available":False,
                "filled":False,
                "trophy range":trophy_range_name
            }
            
            db.falcon_games.insert_one(game) # this puts in the falcon games collection a game that users can join. in other words makes a game
        
        else: # there are already games hosted for that type of game
            game = list(games)[0]
            
            game["players"].append(user.id)

            game["player channels"][user.id] = channel

            db.falcon_games.update_one({"_id":game["_id"]},{"$set":{"players":game["players"]}})
            db.falcon_games.update_one({"_id":game["_id"]},{"$set":{"player channels":game["player channels"]}})

            self.start_falcon_game(mode=game_type,match_id=game["_id"])
        
        # now all that's left is to wait for the game to filled up. When it's filled up, we will finally start asking for commands from the player.
    
    def all_bot_moves(self,game_doc:dict,bot_id:str) -> None:
        """This method will do all bot actions in a certain game, described by the game_doc which has a certain `_id` key."""
        bot = game_doc["bots"][bot_id]

        # before i head on, i need to get all the possible actions a falcon can perform in an arena
    
    
    def start_falcon_game(self,mode:str,match_id:str) -> None:
        """
            Each user will have their own async function that will deal a certain damage to an enemy. Since it is an async function, code will break off when waiting for user to reply with a command. 
        """

        data = db.falcon_games.find_one({"_id":match_id})

        # this means that during the split second which the execution of self.start_falcon_game, another has popped up into the game. While this is a highly unlikely possibility, it is still a possibility so i must write some code to get rid of this bug. First, i will check if there are bots in the game that I can remove from the game to have room for additional human players
        if len(data["players"]) > data["player limit"]:
            index,final_player_list = 0,[]
            
            limit = data["player limit"]
            count = 0
            
            # add 1 to the count when we iterate onto a discord user, and if the iterated user
            
            while True:
                if '-' in data["players"][index]:
                    # this meability that this is a bot
                    bot_id = data["players"][index]

                    data["players"].remove(bot_id) # this removes the bot_id from the list

                    data["players"].append(bot_id) # this adds the bot_id back into the list, EXCEPT this time it is at the very back

                else:
                    final_player_list.append(data["players"][index]) # this gets the current player the index is on in the players list
                    data["players"].remove(data["players"][index]) # this removes the current player bot iterated onto so we can go through all the players LEFT in the list later on

                index += 1
                count += 1

                if count == limit:
                    break
            
            # the only players left in the original "players" list in the data dict are those that were kicked because there were too many people, and they are added to new games.

            db.falcon_games.update_one({"_id":match_id},{"$set":{"players":data["players"]}})
            
            remaining_players = data["players"]
            for player_id in remaining_players:
                if '-' in player_id:
                    # this meability that this a bot
                    pass
                else:
                    async def get_ability():
                        channel,user = None

                        def check(m:discord.Message):
                            nonlocal channel,user

                            channel = m.channel
                            user = m.author

                            return m.author.id == player_id and m.content.startswith('.') # this is the command prefix

                        # normally, we would have a command like async def attack(self,ability,target:discord.User), but since this is a 1 on 1 matchup (in the arena), there will be no need to reference a user to target, and more importantly there will be no discord.User instance to pass in, as there is no need to because in 1v1 arenas, there is only one other player you are directing your attack at

                        ability = await self.client.wait_for("message",check=check).content # no timeout
                        falcon = db.falcon.find_one({"_id":player_id})

                        if ability not in falcon["abilities"]:
                            ability = await get_ability() # recursion
                        
                        energy = falcon["abilities"][ability]["energy taken"]

                        if falcon["stunned"]:
                            time_of_stun = falcon["time of stun"]

                            now = datetime.now()

                            now_in_timedelta = timedelta(minutes=now.minute,seconds=now.second)

                            time_remaining = now_in_timedelta - time_of_stun
                            
                            await channel.send(f'{user.mention} your falcon is still stunned - {time_remaining} seconds left. ')

                        if not falcon["recovered"]: # this means that the falcon has not yet recovered from a previous attack
                            time_of_previous_attack = falcon["time of previous attack"] # this is an instace of timedelta

                            now = datetime.now()

                            now_in_timedelta = timedelta(minutes=now.minute,seconds=now.second)

                            time_remaining = now_in_timedelta - time_of_previous_attack
                            
                            await channel.send(f'{user.mention} you\'re falcon has not recovered from the previous attack, please wait {time_remaining} seconds.')
                        
                        if falcon["energy"] - energy < 0:
                            await channel.send(f'{user.mention} your falcon does not have enough energy to perform {ability}.')
                            
                        enemy_id = data["players"].remove(player_id)[0] # this removes the player id from the list of players, and the only player left is the enemy.

                        # enact the given ability from the user

                        damage = falcon["abilities"][ability]["damage"]

                        if ability == 'drop': # this one here is a special command. check the google doc for more information
                            # this is rather confusing - im going to write out EXACTLY what i want.
                            # user CANNOT use any other attacks while grabbing the enemy up in the air, but the enemy falcon can. However, all attacks are decreased by 0.3, as the enemy falcon is in a poor position. With every passing 3 seconds, the enemy falcon is lifted up 10 feet. Upgrade drop in order to upgrade the base damage every 10 feet.
                            
                            enemy_falcon_name = data["falcon names from ID"][enemy_id]
                            falcon_name = data["falcon names from ID"][user.id]

                            # remember that <channel> is the channel of the current user that is attacking, and <enemy_channel> is the opponent the attack is directed at

                            enemy_channel = data["player channels"][enemy_id]

                            await channel.send(f'{user.mention} your falcon is starting to rise {enemy_falcon_name}, preparing to drop it down.')

                            await enemy_channel.send(f'{falcon_name} picked {enemy_falcon_name} up and raised it up into the air, preparing to drop it down! ')
                            
                            async def sleep():
                                await asyncio.sleep(3)

                            asyncio.run(sleep()) # sleep for 3 seconds before adding loop because loop will immediately run first, THEN wait for the given amount of time

                            drop_height = 0

                            @tasks.loop(seconds=3)
                            async def drop_increment():
                                """Loop will continuously add 10 to the drop height"""
                                nonlocal drop_height
                                drop_height += 10

                                await enemy_channel.send(f'{falcon_name} has raised your falcon {enemy_falcon_name} up 10 ft in the air, at the height of {drop_height}, preparing to drop your falcon down!')

                                await channel.send(f'{falcon_name} has flown 10 ft. up and carried {enemy_falcon_name} with it at the height of {drop_height}, preparing to drop it down.')

                                # also calculate energy deductions

                                

                            # async function to get user commdn .stop, right after async function stop loop, as loop will not be stopped after user writes .stop and also write some checks to cancel the flying upwards if user runs out of energy
                        
                            drop_increment.start() # Loop will continuously add 10 to the drop height

                            def check(m:discord.Message):
                                return m.content == '.stop'
                            
                            await self.client.wait_for('message',check=check)

                            drop_increment.stop() # stop the loop right after the async function has finished

                        damage = tools.process_all_damage_reduce_falcon(user_id=enemy_id) # this is the final damage that i have after processing the enemy falcon's armor

                        # now i have to deal damage to the enemy falcon's armor. I have to decide how to do this

                        # every ability (attacks) you use has three attribute - critical hit (headshot), body hit and poor hit.

                        # this is chosen through RNG.

                        shot = tools.get_falcon_attack_type(falcon)
                        
                        # increment the negative of the damage variable that user falcon dealt to enemy falcon
                        db.falcon.update_one({"_id":enemy_id},{"$inc":{"health":-1*damage}})

                        db.falcon.update_one({"_id":enemy_id},{"$inc":{f"armor.{shot}.health":-1}})

                        # now we have to inform the enemy user wtf just happened to them, or he or she will never know
                        
                        # this is the final recursion i must put for a loop
                        await get_ability()

                    asyncio.run(get_ability()) # main game/getting commands loop
                    # check if command will kill opponent if kills then give trophy and end game and everything else

    
    def connecting_users(self):
        """Connects ever user that is trying to get in a match."""
        loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)

        @tasks.loop(seconds=1)
        async def connecting_user_to_arena():
            users = db.falcon_arena.find({"finding match":True}) # this gets every user trying to join a game
            for arena_doc in users:
                user_id = arena_doc["_id"]
                def main():
                    game_doc = None # game_doc is a the first document that the bot finds unfilled queered from the database
                    trophy_ranges = {
                        (0,20):"Bronze",
                        (20,50):"silver",
                        (50,100):"gold",
                        (100,200):"diamond",
                        (200,400):"platinum",
                        (400,1000):"prodigy",
                        # above 500 is champion
                    }

                    falcon = db.falcon.find_one({"_id":arena_doc["_id"]})
                    trophies = falcon["trophies"]

                    trophy_range_name = None
                    
                    for trophy_range in trophy_ranges:
                        if trophies in range(trophy_range[0],trophy_range[1]):
                            trophy_range_name = trophy_ranges[trophy_range]
                            break
                    
                    if trophy_range_name == None: # this meability that the trophy range is 400+, which meability the user is a champion
                        trophy_range_name = "champion"

                    for i in range(10): # i will only try to connect the user 10 times. If after 10 times there have been no users that joined game, we will supply bots in.
                        game_doc = db.falcon_game.find_one({"game type":"arena"},{"filled":False},{"trophy range":trophy_range_name},{"trophy range":trophy_range_name})

                        # add bot and users specifically to trophy range

                        if bool(list(game_doc)): # this meability that there is currently a game in the falcon_games that is hosting a fighitng arena
                            db.falcon_arena.update_one({"_id":arena_doc["_id"]},{"$set":{"in match":True}})
                            db.falcon_arena.update_one({"_id":arena_doc["_id"]},{"$set":{"match ID":game_doc["_id"]}})
                            
                            game_doc["players"].append(arena_doc["_id"]) # this appends the user's ID to the players list in the game doc

                            db.falcon_game.update_one({"_id":game_doc["_id"]},{"$set":{"players":game_doc["players"]}})

                            if len(game_doc["players"]) >= game_doc["player limit"]:
                                db.falcon_game.update_one({"_id":game_doc["_id"]},{"$set":{"filled":True}})
                            
                            break
                        else:
                            async def sleep():
                                await asyncio.sleep(1)
                            
                            asyncio.run(sleep()) # i have to do asyncio.run because i cannot run asyncio.sleep inside the main synchronous function that i will turn into a thread.
                    
                    if game_doc == None: # this meability that there were no games that were found that have the game type of arena, so we will make one for the user. if game_doc is not equal to none, then we will add the user to the game document
                        game = {
                            "game type":"arena",
                            "host":user_id,
                            "players":[user_id], # should be empty list, but the user trying to find a match so add the user in the game as he or she is already in it, waiting for other people to join
                            "amount of players":1 # one because the user is in there already
                        }

                        # this inserts another game in the falcon arena for other people to connect to
                        db.falcon_games.insert_one(game)

                        def main_thread(): # main thread is here for checking if people join the game. If no one joins the game, then add bots
                            game_started = False
                            for i in range(20):
                                data = db.falcon_games.find_one({"host":user_id}) # get the game that was just made by the user
                                
                                if len(data["players"]) >= data["player limit"]: # this meability that there are enough or more than enough players ready for the game to be started
                                    game_started = True
                                    self.start_falcon_game(mode="arena",match_id=data["_id"])
                                    break
                                
                                async def sleep():
                                    await asyncio.sleep(1)
                                
                                asyncio.run(sleep())
                            
                            if not game_started: # this meability that after 20 seconds, the game has not started. In this case, we add bots into the game only if it's a race. add bots according to the user's level.
                                def get_bots(amount:int) -> list:
                                    """This function will generate `amount` number of bots (falcon bots). More specifically, returns a `list` containing all the bots generated. List will contain dictionaries that represents a falcon bot."""
                                    falcon_stats = {
                                        "bronze":{
                                            "fighting":{
                                                "claw":{
                                                    "damage":[10,15], # choose a random integer between these. the integer will decide the attack daamge of claw
                                                    "energy taken":[10,15],
                                                    "recovery time":1
                                                },
                                                "drop":{ # drop attacks are special, check the google doc and click on FALCON on the outline for more details about the drop attack with falcons
                                                # link - https://docs.google.com/document/d/1uJFf25Bv-5N3XGNbCqCgG1X9U3VkVfIlnYFkkPr8KUc/edit#
                                                    "damage":[10,13],
                                                    "energy taken":[10,13],
                                                    "recovery time":6
                                                },
                                                "tackle":{
                                                    "damage":[25,30],
                                                    "energy taken":[30,30],
                                                    "recovery time":3,
                                                    "stun time":3 # check the link of the google doc above for more information on stun time. as it sounds, tackle stuns the user for a certain amount time
                                                },
                                                "lunge":{
                                                    "damage":[20,25],
                                                    "energy taken":[25,30],
                                                    "recovery time":[15,19] # divide the random integer by 10 to get the wait time in seconds
                                                }
                                            },
                                            "non-fighting":{
                                                "health":{
                                                    "health":[100,120],
                                                    "energy":[100,120],
                                                    "regen":[14,16],
                                                    "seconds":5
                                                },
                                                "armor":{
                                                    "helm":{
                                                        "protection":3, # divide the random integer by 100, since we cannot generate a random float
                                                        "health":100
                                                    },
                                                    "chestplate":{
                                                        "protection":7,
                                                        "health":100
                                                    },
                                                    "greaves":{
                                                        "protection":5,
                                                        "health":100
                                                    }
                                                }
                                            }
                                        },
                                        "silver":{
                                            "fighting":{
                                                "claw":{
                                                    "damage":[15,20],
                                                    "energy taken":[10,15],
                                                    "recovery time":1
                                                },
                                                "drop":{
                                                    "damage":[11,14],
                                                    "energy taken":[10,13],
                                                    "recovery time":6
                                                },
                                                "tackle":{
                                                    "damage":[27,32],
                                                    "energy taken":[27,30],
                                                    "recovery time":3,
                                                    "stun time":3
                                                },
                                                "lunge":{
                                                    "damage":[22,26],
                                                    "energy taken":[30,30],
                                                    "recovery time":[15,19] # divide by 10
                                                }
                                            },
                                            "non-fighting":{
                                                "health":{
                                                    "health":[105,125],
                                                    "energy":[105,125],
                                                    "regen":[14,16],
                                                    "seconds":5
                                                },
                                                "armor":{
                                                    "helm":{
                                                        "protection":5,
                                                        "health":100
                                                    },
                                                    "chestplate":{
                                                        "protection":15,
                                                        "health":100
                                                    },
                                                    "greaves":{
                                                        "protection":1,
                                                        "health":100
                                                    }
                                                }
                                            }
                                        },
                                        "gold":{
                                            "fighting":{
                                                "claw":{
                                                    "damage":[17,25],
                                                    "energy taken":[9,15],
                                                    "recovery time":1
                                                },
                                                "drop":{
                                                    "damage":[15,20],
                                                    "energy taken":[9,11],
                                                    "recovery time":6
                                                },
                                                "tackle":{
                                                    "damage":[29,36],
                                                    "energy taken":[24,27],
                                                    "recovery time":3,
                                                    "stun time":4
                                                },
                                                "lunge":{
                                                    "damage":[24,28],
                                                    "energy taken":[25,28],
                                                    "recovery time":[12,16]
                                                }
                                            },
                                            "non-fighting":{
                                                "health":{
                                                    "health":[110,130],
                                                    "energy":[110,130],
                                                    "regen":[16,19],
                                                    "seconds":5
                                                },
                                                "armor":{
                                                    "helm":{
                                                        "protection":10,
                                                        "health":105
                                                    },
                                                    "chestplate":{
                                                        "protection":15,
                                                        "health":105
                                                    },
                                                    "greaves":{
                                                        "protection":15,
                                                        "health":105
                                                    }
                                                }
                                            }
                                        },
                                        "diamond":{
                                            "fighting":{
                                                "claw":{
                                                    "damage":[19,30],
                                                    "energy taken":[8,12],
                                                    "recovery time":1
                                                },
                                                "drop":{
                                                    "damage":[17,24],
                                                    "energy taken":[7,10],
                                                    "recovery time":6
                                                },
                                                "tackle":{
                                                    "damage":[]
                                                }
                                            },
                                            "non-fighting":{}
                                        }
                                    }
                                    
                                    def get_singular_bot():
                                        """This function returns a singular bot, which details are special according to the trophy range."""

                                        # this gets the information of the specific trophy range
                                        stats = falcon_stats[trophy_range_name]

                                        bot = {
                                            "abilities":{},
                                            "non-fighting":{}
                                        }

                                        def gen_fight_abilities(bot):
                                            """Adds the fighting abilities the bot has in store."""

                                            for ability in stats["fighting"]:
                                                dmg_list = stats["fighting"][ability]["damage"]
                                                damage = random.randint(dmg_list[0],dmg_list[1])

                                                energy_taken_list = stats["fighting"][ability]["energy taken"]
                                                energy_taken = random.randint(energy_taken_list[0],energy_taken_list[1])

                                                recovery_time_list = stats["fighting"][ability]["recovery time"]
                                                recovery_time = random.randint(recovery_time_list[0],recovery_time_list[1])

                                                bot["abilities"][ability] = {
                                                    "damage":damage,
                                                    "energy taken":energy_taken,
                                                    "recovery time":recovery_time
                                                }
                                        
                                        def gen_nonfighting_attributes(bot):
                                            """Adds the non-fighting aspects of a falcon, such as the health and energy."""

                                            health_list = stats["non-fighting"]["health"]
                                            health = random.randint(health_list[0],health_list[1])

                                            energy_list = stats["non-fighting"]["energy"]
                                            energy = random.randint(energy_list[0],energy_list[1])

                                            regen_list = stats["non-fighting"]["regen"]
                                            regen = random.randint(regen_list[0],regen_list[1])

                                            seconds = stats["non-fighting"]["seconds"]

                                            if type(seconds) == list:
                                                seconds = random.randint(seconds[0],seconds[1])

                                            bot["non-fighting"] = {
                                                "health":health,
                                                "energy":energy,
                                                "regen":regen,
                                                "seconds":seconds
                                            }
                                        
                                        # edit and add the certain parts of the falcon bot
                                        bot = gen_fight_abilities(bot)
                                        bot = gen_nonfighting_attributes(bot)

                                        # this returns the SINGLE bot that was generated
                                        return bot

                                    # list of all the bots
                                    bots = []

                                    for i in range(amount):
                                        bot = get_singular_bot()
                                        bots.append(bot)

                                    # returns the LIST of all the bots generated. list of dictionaries that represents a falcon bot
                                    return bots
                                
                                amount = game["player limit"] - len(game["players"])
                                
                                bots = get_bots(amount) # contains a list of dictionaries that represent a falcon bot

                                bot_ids = []
                                
                                for i in bots:
                                    bot_id_str = []
                                    while True:
                                        for i in range(10):
                                            bot_id_str.append(random.choice(ascii_letters))
                                        
                                        bot_id = ''.join(bot_id_str)

                                        if bot_id in bot_ids:
                                            pass
                                        
                                        else:
                                            break
                                
                                # important thing to remember is, when bots are always on "invisible" - you cannot spectate or look at their falcon profile
                                # these are only the bots that are not asked for - if the player specifically asked for a bot falcon to train with, then the string will be bot-VISIBLE
                                
                                game["bots"] = {} # make a dictionary that will store all the bots in the game

                                for bot_id in bot_ids:
                                    game["players"].append(f'bot-INVISIBLE-{bot_id}')

                                    # we need to get the falcon name

                                    names = [
                                        'America',
                                        'Bro',
                                        'Fungus',
                                        'Champ',
                                        'PogChamp'
                                    ]

                                    name = random.choice(names)

                                    data["bots"]["falcon"] = bots[bot_id]

                                    data["bots"]["falcon"]["name"] = name
                                
                                db.falcon_games.delete_one({"_id":data["_id"]})
                                had_to_change_id = False
                                
                                try:
                                    db.falcon_games.insert_one(data)
                                except DuplicateKeyError:
                                    del data["_id"] # delete the old _id, and when doc is inserted into a collection without an _id key already supplied, random id will be generated for the user
                                    
                                    db.falcon_games.insert_one(data)

                                    had_to_change_id = True
                            
                                if had_to_change_id:
                                    data = db.falcon_games.find_one({"host":user_id}) # we cannot do "_id":something, since we do not know the _id of the game document. instead, since a user can only host one game, use filter above instead.
                                    # queer data from database again since original _id has changed.
                                
                                # now that we have added enough bots into the game, we can finally start the user's new game
                                self.start_falcon_game(mode="arena",match_id=data["_id"]) # data document is the user's new game
                            
                            else: # this meability that a sufficient amount of people have joined the user's server, so we can start the game
                                self.start_falcon_game(mode="arena",match_id=game["_id"]) # game_doc is the first game found that is not hosted by the user
                    
                        thread = threading.Thread(target=main_thread,name=f"Waiting for people to join thread - for user {user_id}")
                        thread.start()
                    
                    else:
                        # append user's id to the list of player_id that are playing in the game
                        game_doc["players"].append(user_id)
                        
                        # this updates the player list in the game
                        db.falcon_games.update_one({"_id":game_doc["_id"]},{"$set":{"players":game_doc["players"]}})
                    
                # this is the thread that will go connect to database and connect the user to a game. Not a process but a thread because only top-level functions can be turned into processes - methods in an object cannot be turned into a process
                thread = threading.Thread(target=main,name=f"Connecting user with user id {user_id} to falcon arena.")
                thread.start()

        @tasks.loop(seconds=1)
        async def connecting_user_to_race():
            users = db.falcon_race.find({"finding match":True})
            for race_data in users:
                user_id = race_data["_id"]
                def main():
                    race_games = db.falcon_arena.find_one({"game type":"race"})
                    race = list(race_games)[0] # this gets the first game in the race games.

                thread = threading.Thread(target=main,name=f"Connecting user with user id {user_id} to falcon race.")
                thread.start()
            
        # this starts the async tasks loop
        connecting_user_to_arena.start()
        connecting_user_to_race.start()
    
    @commands.command()
    async def spectate(self,ctx:Context,player:discord.User,mode:str):
        falcon = db.falcon.find_one({"_id":player.id})

        if falcon == None:
            await ctx.send(f'{player} does not have a falcon.')
            return

        mode = mode.lower()

        if mode == 'arena':
            data = db.falcon_arena.find_one({"_id":player})
            article = 'an'
        else:
            data = db.falcon_race.find_one({"_id":player})
            article = 'a'
        
        if data == None:
            await ctx.send(f'{player} is not in {article} {mode}.')
            return
        
        # we can go back to this later

def setup(client):
    client.add_cog(Falcon_games(client))