"""
On line 126 of cogs.thokim.boosts, we set a key,value pair with ID as a pair, and that id is an integer, which is not BSONSerializable. Change later if need be.

As a reminder, before you publish this bot go to global search and search TODO to find all the things still need to be done
"""

import discord
import datetime
import os
import json
import asyncio
import random
from discord import Message
from dotenv import load_dotenv
from copy import deepcopy
from dev.tools import tools
from dev.api import db
from discord.ext import commands, tasks
from discord import Embed
from discord_slash import SlashCommand, SlashContext, ButtonStyle
from dev.db import Database
from discord_slash.utils.manage_components import create_button, create_actionrow

load_dotenv()

client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    print('Project is ready.')

# in case of any crashes, make the crash.json "crasehd" key as value of true
@client.check
def in_case_of_crash(ctx:commands.Context):
    with open('./crashed.json','r') as f:
        data = json.load(f)

    if data["crashed"] == True:
        if ctx.author.id == 680546360717606941:
            # only i can use the bot when its crashed
            return True
    
        else:
            # no one else can use the bot
            return False
    
    else: # this just means its all good, nothing crashed
        return True
    

@client.check # add check name attr - inheritance new class etc
async def hasAcc(ctx:commands.Context):
    name = ctx.command.name
    if name == 'start':
        return True
    
    elif name == 'clear':
        return True
    
    elif name == 'help':
        return True

    res = Database.Storages.get(ctx.author.id)

    if res == None:
        await ctx.send('user does not have an account')
        
        return False
    else:
        return True

@client.check
async def user_not_frozen(ctx:commands.Context):
    user: discord.User = ctx.author
    gdata = db.game.find_one({"_id":user.id})

    if gdata == None: # this means that the user does not have an account yet, so we can ignore the user
        return True

    if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
        return False # if code gets here that means that user's command was not found in general commands, so return False because you cant use any game-specific commands when you are frozen
    
    else: # person is not frozen so he or she can use any command they want
        return True

@client.event
async def on_command_error(ctx:commands.Context,error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Error occured - check terminal.')
        
        user: discord.User = ctx.author

        user_data = Database.Storages.get(user.id)

        if user_data == None:
            await ctx.send('test')
            await ctx.send(tools.no_acc)
            return
        
        general_commands = {
            'reload':reload,
            'clear':clear,
            'clear1':clear1,
            'start':start
        }
        cog,command,args,name = ctx.cog,ctx.command,ctx.args,ctx.command.name

        if cog == None: # this means that these commands are here in the setup file, for DEVS
            command_game_specific = True

            no_args = ['reload','clear','clear1','start']

            for command_name in general_commands:
                if ctx.command.name == command_name:
                    command_game_specific = False
                    command_run = general_commands[command_name]
                    if ctx.command.name in no_args:
                        await command_run(ctx)
                    
                    else:
                        if ctx.command.name == 'phelp':
                            if len(ctx.command.args) == 0: # this means that there were no arguments passed in
                                await command_run(ctx)
                            
                            else:
                                await command_run(ctx,ctx.command.args[0])
            
            if command_game_specific:
                gdata = db.game.find_one({"_id":user.id})
                await ctx.send(f'{user.mention} you are still {gdata["status"]}!')
            
        else:    
            cogs_game_specific_commands = {
                "Attack":['punch','equip','unequip','attack','raid'],
                "Boosts":['consume'],
                "Chests":['open'],
                "Coliseum":[],
                "Donate":["knight"],
                "Downtown":['coinflip'],
                "Falcon":['hunt','charge'],
                "Forge":['upgrade'],
                "General":['travelby'],
                "Grove":['enchant'],
                "Example":[],
                "Loops":[],
                "Marketplace":['shop','trade'],
                "Mines":['sell','wagon'],
                "Monsters":['engage','strike'],
                "Quests":['quests'],
                "Search":['search'],
                "Shipments":['hourly','daily','weekly'],
                "Shop":['purchase','pub','buy'],
                "Vault":['deposit','withdraw']
            }
            
            game_specific_commands = cogs_game_specific_commands[cog.qualified_name]

            if name in game_specific_commands:
                gdata = db.game.find_one({"_id":user.id})
                await ctx.send(f'{user.mention} You are still {gdata["status"]}!')

            else:
                if cog.qualified_name == 'General':
                    if name == 'phelp':
                        if args[0] == None: # this means that it was the argument for command_name is None, which is the default and we dont need to do anything if thats the case
                            await command()
                        else:
                            await command(args[0])
                
                elif cog.qualified_name == 'Doruk':
                    at_location = tools.user_at_required_location(ctx.author,"fortress of vorbul")
                    at_realm = tools.user_at_required_realm(ctx.author,"retrollin")

                    if not at_location:
                        if not at_realm:
                            await ctx.send(tools.wrong_location_msg(user=ctx.author,location="Fortress of Vorbul",realm="Retrollin"))
                        else:
                            await ctx.send(tools.wrong_location_msg(user=ctx.author,location="Fortress of Vorbul"))
                    
                    else:
                        pass
                
                # finish the if statement chain
        
    else: # error is not an discord command error - system error or something more important
        raise error

@client.command()
async def reload(ctx):
    for folder in os.listdir('./cogs'):
        if not folder == '__pycache__':
            for file in os.listdir(f'/cogs/{folder}'):
                if file.endswith('.py'):
                    try:
                        client.unload_extension(f'cogs.{file[:-3]}')
                        client.load_extension(f'cogs.{file[:-3]}')
                    except:
                        client.load_extension(f'cogs{file[:-3]}')
    await ctx.send('All file reloaded. ')

@client.command()
async def emoji(ctx,emoji):
    await ctx.send(f'```{emoji}```')

@client.command()
async def testemoji(ctx):
    await ctx.send('<:goldbar:847940504889065482>')

@client.command()
async def start(ctx:commands.Context):    
    user: discord.User = ctx.author
    users = db.game.find({})

    for player in users:
        if user.id == player["_id"]:
            await ctx.send('You already have an account. ')
            return

    today_ = datetime.date.today()

    today = today_.strftime("%m/%d/20%y")
    
    gdata = {
        "_id":user.id,
        "realm":"thokim",
        "location":"home",
        "status":"stationary",
        "default transport":"walking",
        "level":1,
        "running energy taken":30,
        "flying energy taken":30,
        "walk time":5,
        "experience":0,
        "can be scammed":True,
        "black market scams":20, # one of every 20 commands, you get scammed
        "unlocked dodge":False,
        "dodge":None,
        "can be robbed":True,
        "rob":30, # in of 30 travels
        "rob damage":100,
        "rob steal":10, # gold
        "date registered":today
    }

    hp = {
        "_id":user.id,
        "health":100, # base health the user has
        "energy":1000, # base energy the user has
        "equipped armor":{}, # holds the armor the user is currently wearing  - other armor is stored in the backpack
        "fist damage":20, # TODO decide whether to keep this
        "fist steal range":[1000,2000], #??? should i keep?
        "wet":False, # this means if the user is currently in the rain or not
        "energy gain time":1 # every second the user gains a portion of energy back - MIGHT BE TOO MUCH FOR THE BOT. will probably just set a larger energy, and remind the user to replenish his or her energy every once in a while
    }

    coliseum = {
        "_id":user.id,
        "victories":0,
        "losses":0,
        "entered championships":0,
        "rank":0,
        "trophies":{
        "gold trophies":0,
        "silver trophies":0,
        "bronze trophies":0
        }
    }

    armor = {
        "base":{ # this is the weapon's BASE armor stats
            "helmet":{ # key as name of the weapon, type as the type of weapon it is
                "type":"helmet",
                "health":1000,
                "bonuses":None,
                "damage reduce":0.2
            },
            "chestplate":{
                "type":"chestplate",
                "health":1000,
                "bonuses":None,
                "damage reduce":0.5
            },
            "greaves":{
                "type":"greaves",
                "health":1000,
                "bonuses":None,
                "damage reduce":0.3
            }
        },
        "final":{ # takes in all potion effects too
            "helmet":{
                "type":"helmet",
                "health":1000,
                "bonuses":None,
                "damage reduce":0.2
            },
            "chestplate":{
                "type":"chestplate",
                "health":1000,
                "bonuses":None,
                "damage reduce":0.5
            },
            "greaves":{
                "type":"greaves",
                "health":1000,
                "bonuses":None,
                "damage reduce":0.3
            }
        }
    }

    bp = {
        "_id":user.id,
        "gold nuggets":0,
        "gold bars":0,
        "shields":{
            "mogo shield":{
                "health":100,
                "knockback":5
            }
        },
        "weapons": { # umbrella dict containing all weapon data
            "weapons":{
                "mogo club|1":{
                    "name":"mogo club",
                    "damage":2,
                    "durability":30,
                    "attack time":2,
                    "energy taken":10 # player has 1000 energy
                }
            }, # contains all the weapons the user has
            "equipped weapon":None,
            "limit":7,
            "damage increase multiply":1
        },
        "bows":{
            "bows":{},
            "equipped bow":None,
            "limit":7,
            "damage increase multiply":1,
        },
        "armor":armor,
        "armor ratio":tools.getArmorDamageReductionRatio(armor), # type dict, armor damage reduction participation compared to total damage reduce
        "meals":{}, # these are for COOKED meals, not food that can be eaten raw
        "items":{}, # items in here range from monster parts to apples
        "unfinished potions":{},
        "scrolls":{}
    }

    vault = {
        "_id":user.id,
        "vault":0
    }

    falc = {
        "_id":user.id,
        "name":"Falcon",
        "health":100,
        "energy":100 ,
        "armor":{
            "helmet":{
                "name":"helmet",
                "damage reduce":0.03,
                "health":50
            },
            "chestplate":{
                "name":"chestplate",
                "damage reduce":0.07,
                "health":65
            },
            "wing shield":{
                "name":"wing shield",
                "damage reduce":0.05,
                "health":50
            }
        },
        "chance":{
            "randrange":1000,
            "headshot":[0,49],
            "body shot":[50,899],
            "poor shot":[900,999]
        },
        "steal range":[10000,50000],
        "knockout":600,
        "level":1,
        "abilities":{
            "claw":{
                "damage":10,
                "energy taken":15,
                "recovery time":1,
                "critical":{
                    "critical hit":2, # multiply BASE damage by 2 - any additional stuff will be included after the multiplication
                    "chance":{
                        "sample size":10,
                        "hit range":[0,1]
                    }
                }
            },
            "drop":{
                "damage":10,
                "energy taken":13,
                "recovery time":6
            },
            "tackle":{
                "damage":25,
                "energy taken":30,
                "recovery time":3,
                "stun time":3
            },
            "lunge":{
                "damage":20,
                "energy taken":30,
                "recovery time":1.9,
                "critical":{
                    "critical hit":2,
                    "chance":{
                        "sample size":20,
                        "hit range":[0,1]
                    }
                }
            }
        },
        "trophies":0,
        "recovered":True,
        "stunned":False,
        "time of previous attack":None, # timedelta instance
        "time of stun":None, # timedelta instances
        "energy gain time":1,
        "base energy gain time":1,
        "energy is negatively affected":False
    }

    monsters = {
        "_id":user.id,
        "preview monster":{},
        "engaged monster":None,
        # "engaged monster":{}, # this is for the engaged monsters that are targetting and attacking the user
        "hunt loop":False, # if this is False then hunting loop is stopped - else hunting loop should be continued
        "total monsters defeated":0,
        "trophies":0,
        "previous moves":[], # clear this after every monster fight
        "in attack":False
    }

    mines = { # currently users are default given a mineshaft - later on you have to buy the mineshaft, and you have to be a certain level on xp
        "_id":user.id,
        "keep adding": True,
        "all items":0,
        "mineshaft level":"miner",
        "wagon size":250,
        "mining speed":1,
        "pickaxe":{
            "type":"normal",
            "level":1,
            "original mining speed":1
        },
        "wagon":{
            "type":"normal",
            "level":1,
            "original limit":250
        },
        "upgrade pickaxe":{
            "price":1050,
            "add to":53,
            "final multiply":1
        },
        "upgrade wagon": {
            "price":1050,
            "add to":53,
            "final multiply":1
        },
        "wagon items": {
            "stone":{
                "drops":1,
                "value":5,
                "amount":0,
                "total":0
            },
            "dirt":{
                "drops":1,
                "value":3,
                "amount":0,
                "total":0
            },
            "coal":{
                "drops":1,
                "value":10,
                "amount":0,
                "total":0
                },
            "marble":{
                "drops":1,
                "value":30,
                "amount":0,
                "total":0
            },
            "clay":{
                "drops":1,
                "value":15,
                "amount":0,
                "total":0
            }
        },
        "multipliers":{
            "wagon size":1,
            "mining speed":1,
            "item value":1
        }
    }

    pet = {
        "_id":user.id,
        "shards":0,
        "normal pets":{},
        "mythical pets":{},
        "legendary pets":{},
    }

    # important note, lcuk arrays here will just be for fractions. For example [1,4] would be 1 out of 4 chance of something happening.

    # REMEMBER TO MAKE SOMETHING THAT STOPS BOOSTS

    # also remember that item multiplies just doubles the AMOUNT of items you mine per second. when enabling it, just DOUBLE the DROPS key and the MINING SPEED key.

    # what these boosts should be like is it has a dictionary of all boosts available, like key as boost id and value as a list, index 0 as duration and index 1 as the value. for example, 
        # potion --> id = 2
        
        # {
        #   "mining speed":{
        #     "2":[120,0.5] # adds 50 percent more items per second, and 120 as 2 minutes duration
        #   }
        # } 

    boosts = {
        "_id":user.id,
        "pet boosts":{
            "activate":{
                "mining speed":{},
                "value multipliers":{},
                "wagon size":{},
                "scam luck":0,
                "damage reduce":{},
                "damage increase":{}
            },
            "passive":{
                "mining speed":{},
                "value multipliers":{},
                "wagon size":{},
                "healing":1,
                "scam luck":0,
                "damage reduce":{},
                "damage increase":{}
            }
            },
            "local potions":{
            "luck":{},
            "damage reduce":{},
            "damage increase":{},
            "value multipliers":{},
            "mining speed":{},
            "wagon size":{}
            },
            "total potions":0,
            "all active potions":{},
            "all unused potions":{}
    }

    chests = {
        "_id":user.id,
        "chests":{
            "legendary":0,
            "rare":0,
            "epic":0,
            "uncommon":0,
            "common":0
        },
        "unclaimed shipments":{
            "hourly":False,
            "daily":False,
            "weekly":False
        }
    }

    farm = {
        "_id":user.id,
        "crops":{},
        "barn":{}
    }

    special_commands = {
        "_id":user.id,
        "available commands":{}
    }

    duration = {
        "_id":user.id,
        "potion duration":{},
        "queue":{},
        "current potion loops":{}
    }

    falcon_duration = {
        "_id":user.id,
        "falcon":True,
        "potion duration":{},
        "queue":{}
    }

    quests = {
        "_id":user.id,
        "quests":{
            '1':{
                "name":'flip a coin 3 times',
                "limit":20,
                "commands with quest":[
                'coinflip'
                ],
                "amount required":3,
                "progress":0
                }
            }
        }

    async def tutorial():
        """This tutorial should first, give the user a weapon and tell user about the game."""

        async def give_background():
            """The player is playing in the role of (insert player's name), and it is said that the player was chosen to become the hero of Thokim. The name of this player is Arrow. There is great evil that rules the Realms, and it is up to (player name) of Thokim to purge the Realms of this great evil. 
            
            But the Realms are not revealed to the player yet, and it is said that the Elders chose you because of you proved your talent in the Trial of Valor, slaying every monster you see. 
            
            However, from your last clash with the evil Neorjh, you were broken, soul scattered throughout the lands. you did not die because of an accident and miscalculation on Neorjh's part, but your soul simply broke apart. It took a brave group of young heroes to awaken you, collecting shards of your soul. 
            
            When they started collected your shards, 10 years have passed since the Great War, and the monsters native to the Realms all grew stronger because most of the Royal Force were severely beaten and forced underground, as the remaining soldiers were no match against the numerous monsters still roaming the land.
            
            This group of 5 (we will call them the 5 Mages) battled monsters across the land, and for the first time in 10 years, the sheer amount of monsters faded away a bit thanks to the Mages' work, allowing the people of Thokim to finally leave their underground bunkers, freely breathing the fresh Thokim air after a decade of hiding, only going outside to search for food, and only in the morning.

            The Mages were appointed in the underground bunker for the Royal Force, and set off on one of the greatest quests of the Blood Age, second only to the quest to purge Neorjh. This quest to to resurrect the hero.

            Getting the shards themselves was a major accomplishment, a feat worthy of praise and admiration. And yet, the resurrection itself was an even bigger problem. One of the Mages went to far, and burned himself up during the process. This Mage's name was Orion, and was Arrow's closest friend. They battled together for years, and were with each other on the quest to kill Neorjh. Without 5 people in total, there wasn't enough power to fully resurrect Arrow, and what came out was a partial form of Arrow, lacking certain abilities and most importantly, his memory. Arrow will never learn who he was before, and can only imagine his past through the words of others. The Mages thought that a broken Arrow had no use to them, as he would only fall down and accomplish nothing, and might even die and this time, forever.

            Instead, the Mages worked up a spell and sent Arrow into a deep slumber, letting his own magical body do the healing process. They set in the Temple of Power. Now, the Mages can finally rest, and wait for the Arrow to wake up again, into a new world, completely different from the world in whiche grew up in - and yet he will have no memories of the past, and think that this wasteland of monsters he sees is the true world.

            However, after many years, the land healed itself, and wildlife and humanity flourished once again, living not in harmony, but in avoidance and therefore a shallow peace with monsters.

            As Arrow wakes up, he finds that he has trouble thinking about who he is, how he got to this sanctum. He only remembers 3 names: Arrow, Orion and Neorjh. As he opens the door, he sees he's in a temple, worshipping the Goddess Thokia. There is a sudden voice in the room, and Thokia tells him - 

                "It is not often I meddle with mortal affairs, but Neorjh threatens to rise once again, sensing the awakening of you, my chosen hero. It might seem like the Royal Force, the king, or even the princess chose you, but it was I that saw the talent, the courage and grit you had. My hero, it is time again. Embark on your quest to purge the Realms from Neorjh again, and this time it will be a solo quest. I'm afraid it has been very, very long since you have set foot on the world, and much has changed. Go, and see for yourself."
            
            The user will be transported out of the temple, and sees Thokim in its beauty again. When you get out, you find a stick on the ground, and it is encouraged that the user picks it up for fighting later on.

            After user picks up the stick, the user meet a mogosok that sees Arrow and immediately attacks. The monster attacks FIRST, something like a sneak strike, and the user is caught offguard. The message says "A Mogosok just attacked you! Use `.punch <target>` to fight off the Mogosok, or `.equip <weapon_name>` to equip a weapon in your backpack and `.attack 1` (because monsters are given ids, and the first monster targeting you has id of 1, 2nd has id of 2 and so forth) to smack the Mogosok. Tip* (this will be a footer) use `.target <monster id>` to use attack without needing the monster id when using `.attack`.".

            An important tip is you can equip your shield to block off attacks. However, each time a monster hits your sheild, depending on your shields power, if an opponent hits your shield a certain amount of times, it gets knocked out of your hand and you have to pick it up AND equip it again.

            Another thing is if you get 6 consecutive punches on your target, you get rewarded with a chance to Burst Attack on your target, rapidly releasing 7 attacks with your equipped weapon if it's a one-handed weapon, and 5 attacks if it's a two-handed weapon. Within this short window the user (if the target is a user) cannot attack back. Just the `.attack` will not work, but anything else works fine. However, you have to get 3 consecutive punches without taking damage or 

            Finally, one more combat tip - the 

            """
    
        async def getPlayerUsername():
            """Get the username the user wants."""
            em = Embed(
                description=f'Before we make your account, we need to know the name the Hero of Thokim. Please type your name in **{ctx.channel.name}** within the next `60` seconds.'
            )
            
            await ctx.send(embed=em)

            def check(message:discord.Message):
                return message.author.id == user.id and message.channel.id == ctx.channel.id
            
            username = None

            try:
                username = client.wait_for("message",check=check,timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(f'{user.mention} you have timed out, if you want to make an account again use `.start`.')
            
            gdata["username"] = username

            em = Embed(
                description=f"Set your username to {username}"
            )
            
            await ctx.send(embed=em)
        
        def insertUserAccountInMongoDB():
            db.game.insert_one(gdata)
            db.healthpoints.insert_one(hp)
            db.mines.insert_one(mines)
            db.falcon.insert_one(falc)
            db.pets.insert_one(pet)
            db.backpack.insert_one(bp)
            db.vault.insert_one(vault)
            db.monsters.insert_one(monsters)
            db.boosts.insert_one(boosts)
            db.chests.insert_one(chests)
            db.farm.insert_one(farm)
            db.special_commands.insert_one(special_commands)
            db.duration.insert_one(duration)
            db.falcon_duration.insert_one(falcon_duration)
            db.quests.insert_one(quests)
            db.coliseum.insert_one(coliseum)
        
        def setUserAccountInDatabase():
            """This sets the user's account in the dictionary that contains all the game information"""
            
            data = {}
    
            immediate_game_data = deepcopy(gdata)
            immediate_hp_data = deepcopy(hp)
            immediate_coliseum_data = deepcopy(coliseum)
            immediate_armor_data = deepcopy(armor)
            immediate_backpack_data = deepcopy(bp)
            immediate_vault_data = deepcopy(vault)
            immediate_falcon_data = deepcopy(falc)
            immediate_monsters_data = deepcopy(monsters)
            immediate_pet_data = deepcopy(pet)
            immediate_boosts_data = deepcopy(boosts)
            immediate_chests_data = deepcopy(chests)
            # immediate_farm_data = deepcopy(farm)
            immediate_special_commands_data = deepcopy(special_commands)
            immediate_duration_data = deepcopy(duration)
            immediate_falcon_duration_data = deepcopy(falcon_duration)
            immediate_quests_data = deepcopy(quests)

            del immediate_game_data["date registered"]

            # set up all the important details in the GAME - just the game part, like fighting monsters and such. Important parts of the game that needs to be immediately accessible and fast to get
            data = {
                "game":immediate_game_data,
                "monsters":immediate_monsters_data,
                "healthpoints":immediate_hp_data,
                "backpack":immediate_backpack_data,
                "armor":immediate_armor_data,
                "pets":immediate_pet_data,
                "boosts":immediate_boosts_data,
                "vault":immediate_vault_data,
                "falcon":immediate_falcon_data,
                "chests":immediate_chests_data,
                "coliseum":immediate_coliseum_data,
                "special commands":immediate_special_commands_data,
                "duration":immediate_duration_data,
                "falcon duration":immediate_falcon_duration_data,
                "quests":immediate_quests_data
            }

            Database.addUser(user, data) # sets the user's information in the database
        
        insertUserAccountInMongoDB()
        setUserAccountInDatabase()

        user_data = Database.getStorageData(user)

        async def giveStick():
            """Give the player a stick."""

            walk_to_outside_em = Embed(
                description="Arrow walkeS outside of the temple, getting fresh air after a decade of sleeping in the Temple of Power..."
            )

            await ctx.send(embed=walk_to_outside_em)

            await asyncio.sleep(3)

            give_stick_em = Embed(
                description="Arrow found a stick!"
            )

            give_stick_em.set_image(url='https://static.wikia.nocookie.net/zelda_gamepedia_en/images/4/4f/BotW_Tree_Branch_Model.png/revision/latest?cb=20201117203720')

            take_stick_em = Embed(
                description='Do you want to take the stick? React with <:regional_indicator_y:878106223839420436> or <:regional_indicator_n:878106367926349824>'
            )
            
            await ctx.send(embed=give_stick_em)
            stick_msg: Message = await ctx.send(embed=take_stick_em)

            await stick_msg.add_reaction('🇾')
            await stick_msg.add_reaction('🇳')
            
            reaction = None

            try:
                def check(reaction:discord.Reaction, _user:discord.User):
                    return _user.id == user.id and str(reaction.emoji) in ['🇾','🇳'] and reaction.message.id == stick_msg.id
            
                reaction: discord.Reaction = await client.wait_for('reaction_add',check=check,timeout=30.0) # this specific wait for returns (reaction, user), but we only need the reaction object so we take the first element of the tuple, which is the reaction

                reaction = reaction[0]
            
            except asyncio.TimeoutError:
                await ctx.send('You have timed out, you are not taking the stick.')
                return

            # code here runs if the user has decided to take the stick, indicating that by reacting with y
            if str(reaction.emoji) == '🇾': # this means the user wants to take the stick
                await tools.addEquipment(ctx, user, "stick", "melee")

                # damage = stick_stats["damage"]
                # durability = stick_stats["durability"]
                # attack_time = stick_stats["attack time"]
                # energy_taken = stick_stats["energy taken"]

                # bp["weapons"]["weapons"]["stick"] = {
                #     "name":"stick",
                #     "damage":stick_damage,
                #     "durability":stick_durability,
                #     "attack time":3,
                #     "energy taken":5
                # }
                
                # _em = discord.Embed(description='Arrow picked the stick up')

                # _em.add_field(
                #     name="Stick Attributes",
                #     value=f"""
                #         `Attack Power`: `{stick_damage}`
                #         `Durability`: `{stick_durability}`
                #         `Attack time`: `3 seconds`
                #     """
                # )

                # _em.add_field(name='\u200b',value='Optional: set the name of your weapon with `.rename <weapon_name> <new_weapon_name>`')

                # await ctx.send(embed=_em)

                bp["weapons"]["equipped weapon"] = "stick"

                # send a monster to attack user
            
            else: # user decided to not take the stick
                em = discord.Embed(
                    description='You have decided to not take the stick.',
                    color=tools.lime
                )

            em = Embed(
                description="Arrow was ambushed by a monster! A Mogosok just appeared in front of Arrow! Fight back!"
            )

            em.set_footer(text='')
            
            await ctx.send(embed=em)

            # start the attack on the user
            monster_data = await tools.spawnMonster(ctx, client, user, "mogosok", 1, block=True)

            await tools.startMonsterAttackLoop(ctx, user, 1, monster_data, client)
        
        # await giveStick()
    
    await tutorial()

    await ctx.send(f'{user.mention} made your account. ')

@client.command()
async def clear(ctx: commands.Context):
    names = db.list_collection_names()
    for collection in names:
        if not collection == 'climate':
            var = db[collection]
            var.delete_many({})
        
    Database.Storages = {}
    
    await ctx.send('All user accounts deleted.')

@client.command()
async def clear1(ctx):
    names = db.list_collection_names()
    user: discord.User = ctx.author
    for collection in names:
        col = db[collection]
        col.delete_one({"_id":user.id})
    
    await ctx.send(f'Deleted {user.mention}\'s account. ')

for folder in os.listdir('./cogs'):
    if folder == '__pychache__':
        pass
    else:
        for file in os.listdir(f'./cogs/{folder}'):
            if file.endswith('.py'):
                client.load_extension(f'cogs.{folder}.{file[:-3]}')

def run():
    client.run(os.getenv('TOKEN'))

def main():
    # try:
        run()
    # except:
        print('Bot has crashed, retrying...')
        # recursion
        main()

        # now we gotta go and check if anhy user was in a fight, championship or anything extremely important

        all_gdata = db.game.find({})

        # this prevents any non developers from using my bot while fixing any error that came up

        for gdata in all_gdata:
        # we have to check through all the important things
        # important things that if the bot doesnt go back to would make everything the user did bullsh*t

            """
                1. Coliseum championships ({location:"coliseum arena"})
                2. Fighting a monster ({"status":"fighting"}) (then also check if there are monsters in the monsters dictionary in the monster dict from db.monster.find_one({"_id":user.id}))
                
                If length of keys is equal to 0 then they user is currently not engaged with any monster.
                
                I can add more here
            """
            
            if gdata["location"] == 'coliseum arena' and gdata["status"] == 'fighting arena bot':
                pass