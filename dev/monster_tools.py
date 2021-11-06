from typing import Literal
import discord
import datetime
import asyncio
import random
import time
from dev.tools import tools
from dev.db import Database
from discord.ext import commands

class _monster_tools():
    class MonsterSpawnFailed(Exception):
        pass

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
    
    async def startMonsterAttackLoop(self, ctx: commands.Context, user: discord.User, monster_rank: int, monster_data: dict, client: commands.Bot):
        """`monster_data` should be the return value of `spawnMonster`."""

        process_all_damage_reduce_func = self.process_all_damage_reduce
        death_message = self.death_message

        user_data = Database.getStorageData(user)

        hp = user_data["healthpoints"]
        bp = user_data["backpack"]
        monsters = user_data["monsters"]

        monsters["hunt loop"] = True

        def getMonsterIntelligence(monster_name: str, monster_rank: int):
            """Monster intelligence is split in these 5 ranges
                1, 20: pretty dumb
                20, 40: very slow reaction time/doesnt know what to do half the time
                40, 60: knows what to do but slow at performing it
                60, 80: generally knows what to do and is good at performing it
                80, 100: experienced monster who knows exactly wtf its supposed to do and kills less experienced monster and is usually at the top of a monster camp hierarchy, regardless of size.
            """
            
            monster_intelligences = {                
                "mogosok":{
                    1:[1, 20],
                    2:[20, 50],
                    3:[50, 80],
                    4:[80, 100]
                }
            }

            rand_range = monster_intelligences[monster_name][monster_rank]

            return random.randint(rand_range[0], rand_range[1])
        
        lime = self.lime

        class Monster:
            def __init__(self, enemyPlayerObject, name: str, rank: int, attack_wait: int, wpn: dict = None, bow: str = None, shield: dict = None):
                self.name = name
                self.wpn = wpn
                self.bow = bow
                self.shield = shield
                self.attack_wait = attack_wait

                self.enemyPlayerObject: Player = enemyPlayerObject

                self.health: int = monster_data["health"]
                self.attack_type: str = monster_data["attack type"]

                equipment_type: str = monster_data["equipment type"]
                
                self.equipment_name: str = monster_data[equipment_type]["name"]
                self.equipment_durability: int = monster_data[equipment_type]["durability"] # decided to NOT deduct durability when monster uses weapon
                self.damage: int = monster_data[equipment_type]["damage"]
                self.fightback_countdown: int = monster_data["fight back countdown"]

                self.equipment_broke = False

                intelligence = getMonsterIntelligence(name, rank) # number that shows how smart the monster is - 1 = stupid, 4 = oh my god this is the smartest monster that is a tactician, stalker, everything

                if intelligence in range(1, 21):
                    self.intelligence = 1
                
                elif intelligence in range(21, 51):
                    self.intelligence = 2
                
                elif intelligence in range(51, 81):
                    self.intelligence = 3
                
                else:
                    self.intelligence = 4

                self.last_attack: float = time.time()
                self.attack_because_player_wouldnt_move: float = time.time()
                self.shot_probababilty: int = monster_data["shot probability"]

                base_patience = random.randint(30, 40)

                self.base_patience = base_patience
                self.patience: int =  base_patience # if after a number between 30 and 40 seconds the user has not made any move, just say the monster got uninterested in the user and left.
                # if the user leaves a game, no matter what game, they lose 3 XP.
                # its a lot of XP in the beginning stages of the game, but later on it doesn't really matter much, as a way to engage the user in the game more.
            
            def incrementHealth(self, amount: int):
                """Increments the given amount `amount: int` to monster's heath (`self.health`)"""

                self.health += amount # if to take away health amount should be negative
            
            def throwWeapon(self) -> bool:
                """Throws the monster's weapon at the player - deals 3x damage but weapon instantly breaks. Returns `True` if the user is killed by this blow, `False` if not"""

                self.enemyPlayerObject.deductHealth(3 * self.damage)

                if self.enemyPlayerObject.health <= 0:
                    return True
                
                else:
                    self.equipment_broke = True
                    return False
                
            async def check_if_user_is_engaged_in_battle(self):
                if self.patience == 0:
                    await ctx.send(f'{user.mention} the monster grew bored of you because you did nothing back and left you. You have lost 3 XP because you dont want to fucking leave battles.')
                    
                    monsters["hunt loop"] = False

                    gdata = user_data["game"]

                    if not gdata["experience"] < 3:
                        gdata["experience"] -= 3

                else:
                    if time.time() - self.enemyPlayerObject.time_of_previous_move >= 5:
                        self.patience -= 1
                    
                    else:
                        self.patience = self.base_patience # reset patience

                    await asyncio.sleep(1)
                    
                    await self.check_if_user_is_engaged_in_battle() # recusion - i dont know why i chose recursion but i did, its simple
            
            async def startAttackLoop(self):
                """Asyncronous method will starting asyncio loop that will get the monster to start attacking the user."""

                start_time: float = time.time()

                open_attack_chance = False # if this is set True then that means the AI thinks that this is a good time to fight the player, because his armor either broke or he is knocked down

                def getVerbOfWeaponName(weapon_name: str):
                    """Returns the past tense verb that goes with the weapon name"""
                    base_weapon_name = weapon_name.split(' ')[1]

                    verb_from_weapon = {
                        "club":"struck",
                        "spear":"stabbed"
                    }

                    return verb_from_weapon[base_weapon_name]

                while self.enemyPlayerObject.health > 0 and self.health > 0 and monsters["hunt loop"]:
                    if time.time() - self.last_attack >= 6:
                        # its been more than 6 seconds since monster has last attacked - needs to attack back
                        if random.randint(1, 10) in range(1, 8):
                            open_attack_chance = True

                    if open_attack_chance: # this means the monster has decided to attack the user
                        """Code here will deal the actual damage to the user"""

                        await asyncio.sleep(self.attack_wait)

                        try:
                            weapon_name: str = self.wpn["name"]
                            weapon_damage: int = self.wpn["damage"]

                            verb = getVerbOfWeaponName(weapon_name)

                            msg = f'A {self.name} used its **{weapon_name.title()}** and {verb} you, dealing {weapon_damage} **HP**.'

                            dmg = weapon_damage

                        except TypeError: # meaning wpn was None (meaning the equipment the monster has is a bow) and is not "subscriptable" - cannot access keys of wpn because its not a dict
                            base_bow_damage = self.bow["damage"]
                            
                            msg = f'A {self.name} shot its **{self.bow["name"].title()}** at you, dealing {base_bow_damage} **HP**.'
                            
                            dmg = base_bow_damage

                        self.enemyPlayerObject.deductHealth(dmg)
                        
                        em = discord.Embed(
                            color=lime,
                            description=msg
                        )

                        em.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)

                        em.add_field(name='Monster Data', value=f'''
                            Name: {self.name}
                            Health: {self.health}
                        ''',inline=False)

                        em.add_field(name='Player Data', value=f'''
                            Name: {user}
                            Health: {self.enemyPlayerObject.health}
                            Energy: {self.enemyPlayerObject.energy}
                            Attack Type: {self.enemyPlayerObject.PlayerType}
                            Equipment Name: {self.enemyPlayerObject.equipment_name}
                            Equipment Durability: {self.enemyPlayerObject.equipment_durability}
                            Attack time: {self.enemyPlayerObject.attack_time}
                        ''',inline=False)

                        open_attack_chance = False

                        self.last_attack = time.time()

                        await ctx.send(embed=em)
                    
                    else:
                        """Code here will decide whether to wait for an opening or randomly (read = stupidly) try to attack."""
                        
                        number = random.randint(1, 50)

                        if number == 1:
                            open_attack_chance = True
                            await asyncio.sleep(1) # might delete
                        
                        else: # do NOT be stupid - try to do something smart
                            """Take in data from player and decide what the next step should be"""

                            # based on the monster's intelligence it can notice if the user is currently in attack and attack in the perfect time
                            
                            if self.enemyPlayerObject.in_attack and self.intelligence > 2:
                                await ctx.send('monster has seen that you are in the middle of an attack')
                                if self.intelligence == 3:
                                    number = random.randint(1, 4)

                                else:
                                    number = random.randint(1, 3)

                                if number == 1: # if number is 1 then that means the monster has enough intelligence to spot when the player is in the middle of an attack and strike back
                                    open_attack_chance = True
                            
                            else: # player is not in the middle of attacking - the monster can choose to attack or wait.
                                
                                # NOTE - this code is UNREACHABLE because monster needs to fight every 6 seconds
                                if time.time() - self.fightback_countdown >= self.enemyPlayerObject.time_of_previous_move and time.time() - self.fightback_countdown > self.attack_because_player_wouldnt_move: # more than 10 seconds have passed from the player's previous move AND since the last time the monster has had to fight the player because he or she refused to attack back
                                    
                                    open_attack_chance = True

                                    self.attack_because_player_wouldnt_move = time.time() # save the time

                                else:
                                    await asyncio.sleep(2) # it takes the monster 2 seconds to decide to attack or not

                                    number = random.randint(1, self.shot_probababilty) # 1 out of 5 chance monster will attack you. should probably make this customizable

                                    if number == 1: # RNG says that it wants monster to attack the user
                                        open_attack_chance = True
                                    
                                    # else:
                                    #     await ctx.send(f'number = {number} the monster has decided to not fight you')
                                
                            index = -1
                            
                            if len(self.enemyPlayerObject.previous_moves) >= 3:
                                time_between_last_3_moves: float = self.enemyPlayerObject.previous_moves[index] - self.enemyPlayerObject.previous_moves[index - 2]

                                if time_between_last_3_moves >= 5: # this means that the user has not done anything for the past 5 seconds
                                    if random.randint(1, 3) == 1: # one out of 3 chance monster will fight back
                                        await asyncio.sleep(2)

                                        open_attack_chance = True
                            
                            if self.enemyPlayerObject.energy <= 3 * self.enemyPlayerObject.energy_taken and self.intelligence >= 3: # this means that the user cannot use more than 3 more shots before dying from low energy and the monster is smart enough to see it.
                                # monster should wait a bit before going onto the final kill to give player time to recover - ONLY a bit AND if the monster is feeling nice = RNG

                                if random.randint(1, 10) == 1:
                                    await asyncio.sleep(2)

                                    await ctx.send('monster sees that your energy level is rather low and can only afford 3 more attacks before dying from lack of energy, sleeping for 2 seconds before attacking.')
                                    
                                    open_attack_chance = True
                    
                    if self.enemyPlayerObject.health <= 0:
                        msg = 'you died :('

                        await ctx.send(msg)
                    
                if self.health <= 0:
                    await ctx.send('you have killed the monster!')
                
                elif self.enemyPlayerObject.health <= 0:
                    em = death_message(user, 'monster', self.attack_type, monster_type='mogosok')
                    
                    await ctx.send(embed=em)
                
                # else: user left the game
                #     pass
                
                end_time = time.time()

                await ctx.send(f'battle time: {end_time - start_time}')

                monsters["hunt loop"] = False
            
        class Player:
            def __init__(self):
                """First thing you do is set the player type"""
                self.in_attack = False
                self.time_of_previous_move: float = time.time()

                self.PlayerType: str = None
                self.attack_time: int = None

                self.previous_moves = [self.time_of_previous_move]

                # to be built in self.setPlayerData:
                # self.damage: int
                # self.attack_time: int
                # self.equipment_durability: int
                # self.energy_taken: int
                # self.equipment_name: str
            
            async def setPlayerData(self) -> bool or str:
                async def getPlayerType() -> bool or str:
                    """Returns `True` if the user didn't reply back with anything - in that case stop the program. If not, then returns a string representing the equipment type player is using"""
                    if bp["weapons"]["equipped weapon"] != None:
                        return "melee"
                    
                    elif bp["bows"]["equipped bow"] != None:
                        return "bow"
                    
                    else:
                        def check(m: discord.Message):
                            return m.author.id == user.id and m.channel.id == ctx.channel.id
                        
                        await ctx.send('Please tell me if you are going to be `melee` (enter melee or m) or `bow` (enter bow or b). Time out in 30 seconds.')

                        try:
                            m: discord.Message = await client.wait_for("message", check=check, timeout=30)
                        
                        except asyncio.TimeoutError:
                            await ctx.send('you have timed out.')
                        
                            return True
                        
                        else:
                            if m.content == 'melee' or 'm':
                                return "melee"
                            
                            elif m.content == 'bow' or 'b':
                                return "bow"
                            
                            else:
                                await ctx.send('Answers needs to be one of four - `bow`, `b`, `melee`, or `m`.')
                            
                                res = await getPlayerType() # recursion

                                return res
                    
                self.PlayerType = await getPlayerType()

                if self.PlayerType == 'melee':
                    equipped_weapon = bp["weapons"]["equipped weapon"]

                    durability = bp["weapons"]["weapons"][equipped_weapon]["durability"]

                    attack_time = bp["weapons"]["weapons"][equipped_weapon]["attack time"]
                    energy_taken = bp["weapons"]["weapons"][equipped_weapon]["energy taken"]

                    name: str = bp["weapons"]["weapons"][equipped_weapon]["name"]

                    damage: int = bp["weapons"]["weapons"][equipped_weapon]["damage"]

                else:
                    equipped_bow = bp["bows"]["equipped bow"]

                    durability = bp["bows"]["bows"][equipped_bow]["durability"]
                    
                    attack_time = 0.5
                    energy_taken = 0

                    name: str = bp["bows"]["bows"][equipped_bow]["name"]

                    damage: int = bp["bows"]["bows"][equipped_bow]["damage"]
                
                self.attack_time: float or int = attack_time
                self.energy_taken: int = energy_taken
                self.equipment_durability: int = durability
                self.equipment_name: str = name # name of the equipment the player is using
                self.damage: int = damage
            
            def updatePlayerData(self, PlayerType: Literal['melee', 'bow']):
                """When the user wants to change their selected weapon - data is changed here"""

                self.PlayerType = PlayerType
                
                if PlayerType == 'melee':
                    equipped_weapon: str = bp["weapons"]["equipped weapon"]

                    durability: int = bp["weapons"]["weapons"][equipped_weapon]["durability"]

                    attack_time: int or float = bp["weapons"]["weapons"][equipped_weapon]["attack time"]
                    energy_taken: int = bp["weapons"]["weapons"][equipped_weapon]["energy taken"]

                    damage = bp["weapons"]["weapons"][equipped_weapon]["damage"]
                
                else:
                    equipped_bow: str = bp["bows"]["equipped bow"]

                    durability: int = bp["bows"]["bows"][equipped_bow]["durability"]

                    attack_time = 0.5
                    energy_taken = 0

                    damage = bp["bows"]["bows"][equipped_bow]["damage"]
                
                self.equipment_durability = durability
                self.attack_time = attack_time
                self.energy_taken = energy_taken
                self.damage: int = damage

            def deductHealth(self, base_damage: int) -> None:
                """Takes IN the user's armor reduction, and takes away the final damage reduce."""

                final_damage = process_all_damage_reduce_func(user, base_damage)

                hp["health"] -= final_damage # in dict deduct health
            
            def deductDurability(self) -> bool:
                """Subtracts `1` to the equipment the player has. Returns `True` if equipment has broken, `False` if not."""

                if self.PlayerType == 'melee':
                    bp["weapons"]["weapons"][self.equipment_name]["durability"] -= 1

                    if bp["weapons"]["weapons"][self.equipment_name]["durability"] <= 0:
                        return True
                
                else:
                    bp["bows"]["bows"][self.equipment_name]["durability"] -= 1

                    if bp["bows"]["bows"][self.equipment_name]["durability"] >= 0:
                        return True

            @property
            def health(self):
                """Player health user has left"""
                return hp["health"]
            
            @property
            def energy(self):
                """Player energy user has left"""
                return hp["energy"]

            async def attack(self, monster: Monster) -> None:
                """Attacks the monster."""
                
                self.in_attack = True
                
                await asyncio.sleep(self.attack_time)

                self.in_attack = False

                monster.incrementHealth(-self.damage)

                # if on challenge mode, every few seconds monster wll regain health

                await ctx.send(f'you have attacked the monster, dealing {self.damage}. Monster remaining health: {monster.health}')

                curr_time = time.time()

                self.time_of_previous_move = curr_time # set time in here for monster to decide whether or not to attack
                self.previous_moves.append(curr_time)

                res = self.deductDurability() # deduct durability on the player's weapon

                if res:
                    await ctx.send(f'{user.mention} your `{self.equipment_name}`` has broken! Dealing 3x **critical hit**!')

                    monster.incrementHealth(-2 * self.damage) # only 2x damage because already dealt 1x damage above

                    if self.PlayerType == 'melee':
                        del bp["weapons"]["weapons"][self.equipment_name]
                        bp["weapons"]["equipped weapon"] = None
                    
                    else:
                        del bp["bows"]["bows"][self.equipment_name]
                        bp["bows"]["equipped bow"] = None

                # if not res: pass
            
        player = Player()
        await player.setPlayerData()

        # now data is all set - game is ready to go

        name = monster_data["name"]
        attack_type = monster_data["attack type"]
        equipment_type = monster_data["equipment type"]
        shield = monster_data["shield"]
        attack_wait = monster_data[equipment_type]["attack time"] # the time it takes for a single attack

        if attack_type == 'melee':
            monster_wpn = monster_data["weapon"]
            monster = Monster(player, name=name, rank=1, wpn=monster_wpn, shield=shield, attack_wait=attack_wait)

        else:
            monster_bow = monster_data["bow"]
            monster = Monster(player, name=name, rank=1, bow=monster_bow, shield=shield, attack_wait=attack_wait)

        async def startUserInputLoop():
            # start loop for taking in user data
            def check(m: discord.Message):
                return m.author.id == user.id and m.channel.id == ctx.channel.id

            while monsters["hunt loop"]:
                # TODO figure out a fix to replace for wait for because if my bot goes big, it cannot use wait_for anymore because verified bots have no more access to user message content
                
                m: discord.Message = await client.wait_for('message', check=check) # this keeps getting user input as form text

                game_commands = {
                    'attack':'attack',
                    'a':'attack'
                }

                # check if user has changed anything since last time
                if bp["weapons"]["equipped weapon"] != player.equipment_name:
                    player.updatePlayerData() # update data in object

                try:
                    command = game_commands[m.content]

                    if command == 'attack':
                        # attack the monster

                        await player.attack(monster)
                    
                except KeyError: # user input not valid command
                    pass

        await asyncio.gather(monster.startAttackLoop(), startUserInputLoop(), monster.check_if_user_is_engaged_in_battle())
        await ctx.send('will code work here?')

    async def spawnMonster(self, ctx: commands.Context, client: commands.Bot, user: discord.User, monster_type: str, monster_rank: int, block: bool = False) -> dict:
        """Method spawns a monster. User can either choose to engage the monster, or on rare occasions the monster will come towards to user. Returns `dict` if the monster spawn worked. Raises `MonsterSpawnFailed` if user declines if `block` is `False` (it's `False` by default) - immediately returns `dict` if `block` is `True`"""
        
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

                return monster_health_dict[monster_type][monster_rank]
            
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
            
            def getFightBackCountdown(base_monster: str) -> int:
                monster_fightback_countdowns = {
                    "mogosok":15
                }

                return monster_fightback_countdowns[base_monster]
            
            def getShotProbability(base_monster: str) -> int:
                """Returns the probability (chance) that the monster decides to attack back, not wait. Returns `int` because it represents the probability 1 out of [return value]"""

                shot_probabilities = {
                    "mogosok":5
                }

                return shot_probabilities[base_monster]

            # code below gets the monster data
            monster_health = getMonsterHealth()
            
            durability, damage, base_equipment_name, name, monster_attack_type = getMonsterEquipmentData() # monster attack type is the type of equipment the monster is using - weapon or bow
            shield_durability, shield_knockback, shield_name = getShieldData()

            if monster_attack_type == 'bow':
                attack_time = self.getEquipmentAttackTime(base_equipment_name, name)
            
            else:
                attack_time = self.getEquipmentAttackTime(base_equipment_name, name)
            
            fightback_countdown = getFightBackCountdown(monster_type)
            shot_probability = getShotProbability(monster_type)

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
                "equipment type":equipment_type,
                "fight back countdown":fightback_countdown,
                "shot probability":shot_probability
            }
            
            return new_monster_data # returns the entire data for the monster
        
        monster_data = getMonster()

        base_monster: str = monster_data["name"]
        attack_type = monster_data["attack type"] # this is either `bow` or `melee`
        equipment_type = monster_data["equipment type"] # this is either `bow` or `weapon`

        equipment_data = monster_data[equipment_type] # contains: name, durability, damage, and attack time of the equipment the monster is using.

        shield_name = monster_data["shield"] if monster_data["shield"] != None else None

        await ctx.send(f"{user.mention} you have found a **{base_monster}**! Enter `.more` to find out more about this monster. React with 🇾 to engage with the {base_monster}, 🇳 to pass. Message will timeout in 60 seconds.")

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
        em.add_field(name="\u200b",value='You can use the Thokim Epitome gifted by the Mages to find out more about a monster by `.more <object name>`. For example, `.more mogosok`.')
        
        m: discord.Message = await ctx.send(embed=em)
        
        if not block:
            await m.add_reaction('🇾')
            await m.add_reaction('🇳')

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
                    return monster_data
            
                else: # user has passed
                    raise self.MonsterSpawnFailed
                
        else:
            return monster_data # do not ask if user wants to fight monster or not if block is True
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
                    "gorsok":[998, 1000]
                },
                (10, 20):{
                    "mogosok":[0, 850],
                    "jawsok":[850, 950],
                    "drasok":[950, 990],
                    "baursok":[990, 997],
                    "bugosok":[997, 998],
                    "gorsok":[998, 1000]
                },
                (20, 30):{
                    "mogosok":[0, 800],
                    "jawsok":[800, 900],
                    "drasok":[900, 985],
                    "baursok":[985, 995],
                    "bugosok":[995, 998],
                    "gorsok":[998, 1000]
                },
                (30, 40):{
                    "mogosok":[0, 750],
                    "jawsok":[750, 900],
                    "drasok":[900, 985],
                    "baursok":[985, 995],
                    "bugosok":[995, 998],
                    "gorsok":[998, 1000]
                },
                (40, 50):{
                    "mogosok":[0, 700],
                    "jawsok":[700, 800],
                    "drasok":[800, 900],
                    "baursok":[900, 950],
                    "bugosok":[950, 990],
                    "gorsok":[990, 1000]
                },
                (50, 60):{
                    "mogosok":[0, 650],
                    "jawsok":[650, 800],
                    "drasok":[800, 900],
                    "baursok":[900, 950],
                    "bugosok":[950, 990],
                    "gorsok":[990, 1000] 
                }
            }

            number = random.randint(1, 999)
            for lvl_range in list(monsters.keys()):
                if level in range(lvl_range[0], lvl_range[1]): # this should print out each key in monsters right?????????
                    for monster in list(monsters[lvl_range].keys()):
                        monster_probability = monsters[lvl_range][monster]

                        if number in range(monster_probability[0], monster_probability[1]):
                            return monster # returns the base monster from above
            
            raise # raise if for some reason it doesnt return above
        
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
    
    async def startMonsterAttackLoop(self, ctx: commands.Context, user: discord.User, monster_rank: int, monster_data: dict, client: commands.Bot):
        """`monster_data` should be the return value of `spawnMonster`."""

        death_message = tools.death_message

        user_data = Database.getStorageData(user)

        hp = user_data["healthpoints"]
        bp = user_data["backpack"]
        monsters = user_data["monsters"]

        monsters["hunt loop"] = True

        def getMonsterIntelligence(monster_name: str, monster_rank: int):
            """Monster intelligence is split in these 5 ranges
                1, 20: pretty dumb
                20, 40: very slow reaction time/doesnt know what to do half the time
                40, 60: knows what to do but slow at performing it
                60, 80: generally knows what to do and is good at performing it
                80, 100: experienced monster who knows exactly wtf its supposed to do and kills less experienced monster and is usually at the top of a monster camp hierarchy, regardless of size.
            """
            
            monster_intelligences = {                
                "mogosok":{
                    1:[1, 20],
                    2:[20, 50],
                    3:[50, 80],
                    4:[80, 100]
                }
            }

            rand_range = monster_intelligences[monster_name][monster_rank]

            return random.randint(rand_range[0], rand_range[1])
        
        class Monster:
            def __init__(self, enemyPlayerObject, name: str, rank: int, attack_wait: int, wpn: dict = None, bow: str = None, shield: dict = None):
                self.name = name
                self.wpn = wpn
                self.bow = bow
                self.shield = shield
                self.attack_wait = attack_wait

                self.enemyPlayerObject: Player = enemyPlayerObject

                self.health: int = monster_data["health"]
                self.attack_type: str = monster_data["attack type"]

                equipment_type: str = monster_data["equipment type"]
                
                self.equipment_name: str = monster_data[equipment_type]["name"]
                self.equipment_durability: int = monster_data[equipment_type]["durability"] # decided to NOT deduct durability when monster uses weapon
                self.damage: int = monster_data[equipment_type]["damage"]
                self.fightback_countdown: int = monster_data["fight back countdown"]

                self.equipment_broke = False

                intelligence = getMonsterIntelligence(name, rank) # number that shows how smart the monster is - 1 = stupid, 4 = oh my god this is the smartest monster that is a tactician, stalker, everything

                if intelligence in range(1, 21):
                    self.intelligence = 1
                
                elif intelligence in range(21, 51):
                    self.intelligence = 2
                
                elif intelligence in range(51, 81):
                    self.intelligence = 3
                
                else:
                    self.intelligence = 4

                self.last_attack: float = time.time()
                self.attack_because_player_wouldnt_move: float = time.time()
                self.shot_probababilty: int = monster_data["shot probability"]

                base_patience = random.randint(30, 40)

                self.base_patience = base_patience
                self.patience: int =  base_patience # if after a number between 30 and 40 seconds the user has not made any move, just say the monster got uninterested in the user and left.
                # if the user leaves a game, no matter what game, they lose 3 XP.
                # its a lot of XP in the beginning stages of the game, but later on it doesn't really matter much, as a way to engage the user in the game more.
            
            def incrementHealth(self, amount: int):
                """Increments the given amount `amount: int` to monster's heath (`self.health`)"""

                self.health += amount # if to take away health amount should be negative
            
            def throwWeapon(self) -> bool:
                """Throws the monster's weapon at the player - deals 3x damage but weapon instantly breaks. Returns `True` if the user is killed by this blow, `False` if not"""

                self.enemyPlayerObject.deductHealth(3 * self.damage)

                if self.enemyPlayerObject.health <= 0:
                    return True
                
                else:
                    self.equipment_broke = True
                    return False
                
            async def check_if_user_is_engaged_in_battle(self):
                if self.patience == 0:
                    await ctx.send(f'{user.mention} the monster grew bored of you because you did nothing back and left you. You have lost 3 XP because you dont want to fucking leave battles.')
                    
                    monsters["hunt loop"] = False

                    gdata = user_data["game"]

                    if not gdata["experience"] < 3:
                        gdata["experience"] -= 3

                else:
                    if time.time() - self.enemyPlayerObject.time_of_previous_move >= 5:
                        self.patience -= 1
                    
                    else:
                        self.patience = self.base_patience # reset patience

                    await asyncio.sleep(1)
                    
                    await self.check_if_user_is_engaged_in_battle() # recusion - i dont know why i chose recursion but i did, its simple
            
            async def startAttackLoop(self):
                """Asyncronous method will starting asyncio loop that will get the monster to start attacking the user."""

                start_time: float = time.time()

                open_attack_chance = False # if this is set True then that means the AI thinks that this is a good time to fight the player, because his armor either broke or he is knocked down

                def getVerbOfWeaponName(weapon_name: str):
                    """Returns the past tense verb that goes with the weapon name"""
                    base_weapon_name = weapon_name.split(' ')[1]

                    verb_from_weapon = {
                        "club":"struck",
                        "spear":"stabbed"
                    }

                    return verb_from_weapon[base_weapon_name]

                while self.enemyPlayerObject.health > 0 and self.health > 0 and monsters["hunt loop"]:
                    if time.time() - self.last_attack >= 6:
                        # its been more than 6 seconds since monster has last attacked - needs to attack back
                        if random.randint(1, 10) in range(1, 8):
                            open_attack_chance = True

                    if open_attack_chance: # this means the monster has decided to attack the user
                        """Code here will deal the actual damage to the user"""

                        await asyncio.sleep(self.attack_wait)

                        try:
                            weapon_name: str = self.wpn["name"]
                            weapon_damage: int = self.wpn["damage"]

                            verb = getVerbOfWeaponName(weapon_name)

                            msg = f'A {self.name} used its **{weapon_name.title()}** and {verb} you, dealing {weapon_damage} **HP**.'

                            dmg = weapon_damage

                        except TypeError: # meaning wpn was None (meaning the equipment the monster has is a bow) and is not "subscriptable" - cannot access keys of wpn because its not a dict
                            base_bow_damage = self.bow["damage"]
                            
                            msg = f'A {self.name} shot its **{self.bow["name"].title()}** at you, dealing {base_bow_damage} **HP**.'
                            
                            dmg = base_bow_damage

                        self.enemyPlayerObject.deductHealth(dmg)
                        
                        em = discord.Embed(
                            color=tools.lime,
                            description=msg
                        )

                        em.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)

                        em.add_field(name='Monster Data', value=f'''
                            Name: {self.name}
                            Health: {self.health}
                        ''',inline=False)

                        em.add_field(name='Player Data', value=f'''
                            Name: {user}
                            Health: {self.enemyPlayerObject.health}
                            Energy: {self.enemyPlayerObject.energy}
                            Attack Type: {self.enemyPlayerObject.PlayerType}
                            Equipment Name: {self.enemyPlayerObject.equipment_name}
                            Equipment Durability: {self.enemyPlayerObject.equipment_durability}
                            Attack time: {self.enemyPlayerObject.attack_time}
                        ''',inline=False)

                        open_attack_chance = False

                        self.last_attack = time.time()

                        await ctx.send(embed=em)
                    
                    else:
                        """Code here will decide whether to wait for an opening or randomly (read = stupidly) try to attack."""
                        
                        number = random.randint(1, 50)

                        if number == 1:
                            open_attack_chance = True
                            await asyncio.sleep(1) # might delete
                        
                        else: # do NOT be stupid - try to do something smart
                            """Take in data from player and decide what the next step should be"""

                            # based on the monster's intelligence it can notice if the user is currently in attack and attack in the perfect time
                            
                            if self.enemyPlayerObject.in_attack and self.intelligence > 2:
                                await ctx.send('monster has seen that you are in the middle of an attack')
                                if self.intelligence == 3:
                                    number = random.randint(1, 4)

                                else:
                                    number = random.randint(1, 3)

                                if number == 1: # if number is 1 then that means the monster has enough intelligence to spot when the player is in the middle of an attack and strike back
                                    open_attack_chance = True
                            
                            else: # player is not in the middle of attacking - the monster can choose to attack or wait.
                                
                                # NOTE - this code is UNREACHABLE because monster needs to fight every 6 seconds
                                if time.time() - self.fightback_countdown >= self.enemyPlayerObject.time_of_previous_move and time.time() - self.fightback_countdown > self.attack_because_player_wouldnt_move: # more than 10 seconds have passed from the player's previous move AND since the last time the monster has had to fight the player because he or she refused to attack back
                                    
                                    open_attack_chance = True

                                    self.attack_because_player_wouldnt_move = time.time() # save the time

                                else:
                                    await asyncio.sleep(2) # it takes the monster 2 seconds to decide to attack or not

                                    number = random.randint(1, self.shot_probababilty) # 1 out of 5 chance monster will attack you. should probably make this customizable

                                    if number == 1: # RNG says that it wants monster to attack the user
                                        open_attack_chance = True
                                    
                                    # else:
                                    #     await ctx.send(f'number = {number} the monster has decided to not fight you')
                                
                            index = -1
                            
                            if len(self.enemyPlayerObject.previous_moves) >= 3:
                                time_between_last_3_moves: float = self.enemyPlayerObject.previous_moves[index] - self.enemyPlayerObject.previous_moves[index - 2]

                                if time_between_last_3_moves >= 5: # this means that the user has not done anything for the past 5 seconds
                                    if random.randint(1, 3) == 1: # one out of 3 chance monster will fight back
                                        await asyncio.sleep(2)

                                        open_attack_chance = True
                            
                            if self.enemyPlayerObject.energy <= 3 * self.enemyPlayerObject.energy_taken and self.intelligence >= 3: # this means that the user cannot use more than 3 more shots before dying from low energy and the monster is smart enough to see it.
                                # monster should wait a bit before going onto the final kill to give player time to recover - ONLY a bit AND if the monster is feeling nice = RNG

                                if random.randint(1, 10) == 1:
                                    await asyncio.sleep(2)

                                    await ctx.send('monster sees that your energy level is rather low and can only afford 3 more attacks before dying from lack of energy, sleeping for 2 seconds before attacking.')
                                    
                                    open_attack_chance = True
                    
                    if self.enemyPlayerObject.health <= 0:
                        msg = 'you died :('

                        await ctx.send(msg)
                    
                if self.health <= 0:
                    await ctx.send('you have killed the monster!')
                
                elif self.enemyPlayerObject.health <= 0:
                    em = death_message(user, 'monster', self.attack_type, monster_type='mogosok')
                    
                    await ctx.send(embed=em)
                
                # else: user left the game
                #     pass
                
                end_time = time.time()

                await ctx.send(f'battle time: {end_time - start_time}')

                monsters["hunt loop"] = False
            
        class Player:
            def __init__(self):
                """First thing you do is set the player type"""
                self.in_attack = False
                self.time_of_previous_move: float = time.time()

                self.PlayerType: str = None
                self.attack_time: int = None

                self.previous_moves = [self.time_of_previous_move]

                # to be built in self.setPlayerData:
                # self.damage: int
                # self.attack_time: int
                # self.equipment_durability: int
                # self.energy_taken: int
                # self.equipment_name: str
            
            async def setPlayerData(self) -> bool or str:
                async def getPlayerType() -> bool or str:
                    """Returns `True` if the user didn't reply back with anything - in that case stop the program. If not, then returns a string representing the equipment type player is using"""
                    if bp["weapons"]["equipped weapon"] != None:
                        return "melee"
                    
                    elif bp["bows"]["equipped bow"] != None:
                        return "bow"
                    
                    else:
                        def check(m: discord.Message):
                            return m.author.id == user.id and m.channel.id == ctx.channel.id
                        
                        await ctx.send('Please tell me if you are going to be `melee` (enter melee or m) or `bow` (enter bow or b). Time out in 30 seconds.')

                        try:
                            m: discord.Message = await client.wait_for("message", check=check, timeout=30)
                        
                        except asyncio.TimeoutError:
                            await ctx.send('you have timed out.')
                        
                            return True
                        
                        else:
                            if m.content == 'melee' or 'm':
                                return "melee"
                            
                            elif m.content == 'bow' or 'b':
                                return "bow"
                            
                            else:
                                await ctx.send('Answers needs to be one of four - `bow`, `b`, `melee`, or `m`.')
                            
                                res = await getPlayerType() # recursion

                                return res
                    
                self.PlayerType = await getPlayerType()

                if self.PlayerType == 'melee':
                    equipped_weapon = bp["weapons"]["equipped weapon"]

                    durability = bp["weapons"]["weapons"][equipped_weapon]["durability"]

                    attack_time = bp["weapons"]["weapons"][equipped_weapon]["attack time"]
                    energy_taken = bp["weapons"]["weapons"][equipped_weapon]["energy taken"]

                    name: str = bp["weapons"]["weapons"][equipped_weapon]["name"]

                    damage: int = bp["weapons"]["weapons"][equipped_weapon]["damage"]

                else:
                    equipped_bow = bp["bows"]["equipped bow"]

                    durability = bp["bows"]["bows"][equipped_bow]["durability"]
                    
                    attack_time = 0.5
                    energy_taken = 0

                    name: str = bp["bows"]["bows"][equipped_bow]["name"]

                    damage: int = bp["bows"]["bows"][equipped_bow]["damage"]
                
                self.attack_time: float or int = attack_time
                self.energy_taken: int = energy_taken
                self.equipment_durability: int = durability
                self.equipment_name: str = name # name of the equipment the player is using
                self.damage: int = damage
            
            def updatePlayerData(self, PlayerType: Literal['melee', 'bow']):
                """When the user wants to change their selected weapon - data is changed here"""

                self.PlayerType = PlayerType
                
                if PlayerType == 'melee':
                    equipped_weapon: str = bp["weapons"]["equipped weapon"]

                    durability: int = bp["weapons"]["weapons"][equipped_weapon]["durability"]

                    attack_time: int or float = bp["weapons"]["weapons"][equipped_weapon]["attack time"]
                    energy_taken: int = bp["weapons"]["weapons"][equipped_weapon]["energy taken"]

                    damage = bp["weapons"]["weapons"][equipped_weapon]["damage"]
                
                else:
                    equipped_bow: str = bp["bows"]["equipped bow"]

                    durability: int = bp["bows"]["bows"][equipped_bow]["durability"]

                    attack_time = 0.5
                    energy_taken = 0

                    damage = bp["bows"]["bows"][equipped_bow]["damage"]
                
                self.equipment_durability = durability
                self.attack_time = attack_time
                self.energy_taken = energy_taken
                self.damage: int = damage

            def deductHealth(self, base_damage: int) -> None:
                """Takes IN the user's armor reduction, and takes away the final damage reduce."""

                final_damage = tools.process_all_damage_reduce(user, base_damage)

                hp["health"] -= final_damage # in dict deduct health
            
            def deductDurability(self) -> bool:
                """Subtracts `1` to the equipment the player has. Returns `True` if equipment has broken, `False` if not."""

                if self.PlayerType == 'melee':
                    bp["weapons"]["weapons"][self.equipment_name]["durability"] -= 1

                    if bp["weapons"]["weapons"][self.equipment_name]["durability"] <= 0:
                        return True
                
                else:
                    bp["bows"]["bows"][self.equipment_name]["durability"] -= 1

                    if bp["bows"]["bows"][self.equipment_name]["durability"] >= 0:
                        return True

            @property
            def health(self):
                """Player health user has left"""
                return hp["health"]
            
            @property
            def energy(self):
                """Player energy user has left"""
                return hp["energy"]

            async def attack(self, monster: Monster) -> None:
                """Attacks the monster."""
                
                self.in_attack = True
                
                await asyncio.sleep(self.attack_time)

                self.in_attack = False

                monster.incrementHealth(-self.damage)

                # if on challenge mode, every few seconds monster wll regain health

                await ctx.send(f'you have attacked the monster, dealing {self.damage}. Monster remaining health: {monster.health}')

                curr_time = time.time()

                self.time_of_previous_move = curr_time # set time in here for monster to decide whether or not to attack
                self.previous_moves.append(curr_time)

                res = self.deductDurability() # deduct durability on the player's weapon

                if res:
                    await ctx.send(f'{user.mention} your `{self.equipment_name}`` has broken! Dealing 3x **critical hit**!')

                    monster.incrementHealth(-2 * self.damage) # only 2x damage because already dealt 1x damage above

                    if self.PlayerType == 'melee':
                        del bp["weapons"]["weapons"][self.equipment_name]
                        bp["weapons"]["equipped weapon"] = None
                    
                    else:
                        del bp["bows"]["bows"][self.equipment_name]
                        bp["bows"]["equipped bow"] = None

                # if not res: pass
            
        player = Player()
        await player.setPlayerData()

        # now data is all set - game is ready to go

        name = monster_data["name"]
        attack_type = monster_data["attack type"]
        equipment_type = monster_data["equipment type"]
        shield = monster_data["shield"]
        attack_wait = monster_data[equipment_type]["attack time"] # the time it takes for a single attack

        if attack_type == 'melee':
            monster_wpn = monster_data["weapon"]
            monster = Monster(player, name=name, rank=1, wpn=monster_wpn, shield=shield, attack_wait=attack_wait)

        else:
            monster_bow = monster_data["bow"]
            monster = Monster(player, name=name, rank=1, bow=monster_bow, shield=shield, attack_wait=attack_wait)

        async def startUserInputLoop():
            # start loop for taking in user data
            def check(m: discord.Message):
                return m.author.id == user.id and m.channel.id == ctx.channel.id

            while monsters["hunt loop"]:
                # TODO figure out a fix to replace for wait for because if my bot goes big, it cannot use wait_for anymore because verified bots have no more access to user message content
                
                m: discord.Message = await client.wait_for('message', check=check) # this keeps getting user input as form text

                game_commands = {
                    'attack':'attack',
                    'a':'attack'
                }

                # check if user has changed anything since last time
                if bp["weapons"]["equipped weapon"] != player.equipment_name:
                    player.updatePlayerData() # update data in object

                try:
                    command = game_commands[m.content]

                    if command == 'attack':
                        # attack the monster

                        await player.attack(monster)
                    
                except KeyError: # user input not valid command
                    pass

        await asyncio.gather(monster.startAttackLoop(), startUserInputLoop(), monster.check_if_user_is_engaged_in_battle())
        await ctx.send('will code work here?')

    async def spawnMonster(self, ctx: commands.Context, client: commands.Bot, user: discord.User, monster_type: str, monster_rank: int, block: bool = False) -> dict:
        """Method spawns a monster. User can either choose to engage the monster, or on rare occasions the monster will come towards to user. Returns `dict` if the monster spawn worked. Raises `MonsterSpawnFailed` if user declines if `block` is `False` (it's `False` by default) - immediately returns `dict` if `block` is `True`"""
        
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

                return monster_health_dict[monster_type][monster_rank]
            
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
            
            def getFightBackCountdown(base_monster: str) -> int:
                monster_fightback_countdowns = {
                    "mogosok":15
                }

                return monster_fightback_countdowns[base_monster]
            
            def getShotProbability(base_monster: str) -> int:
                """Returns the probability (chance) that the monster decides to attack back, not wait. Returns `int` because it represents the probability 1 out of [return value]"""

                shot_probabilities = {
                    "mogosok":5
                }

                return shot_probabilities[base_monster]

            # code below gets the monster data
            monster_health = getMonsterHealth()
            
            durability, damage, base_equipment_name, name, monster_attack_type = getMonsterEquipmentData() # monster attack type is the type of equipment the monster is using - weapon or bow
            shield_durability, shield_knockback, shield_name = getShieldData()

            if monster_attack_type == 'bow':
                attack_time = tools.getEquipmentAttackTime(base_equipment_name, name)
            
            else:
                attack_time = tools.getEquipmentAttackTime(base_equipment_name, name)
            
            fightback_countdown = getFightBackCountdown(monster_type)
            shot_probability = getShotProbability(monster_type)

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
                "equipment type":equipment_type,
                "fight back countdown":fightback_countdown,
                "shot probability":shot_probability
            }
            
            return new_monster_data # returns the entire data for the monster
        
        monster_data = getMonster()

        base_monster: str = monster_data["name"]
        attack_type = monster_data["attack type"] # this is either `bow` or `melee`
        equipment_type = monster_data["equipment type"] # this is either `bow` or `weapon`

        equipment_data = monster_data[equipment_type] # contains: name, durability, damage, and attack time of the equipment the monster is using.

        shield_name = monster_data["shield"] if monster_data["shield"] != None else None

        await ctx.send(f"{user.mention} you have found a **{base_monster}**! Enter `.more` to find out more about this monster. React with 🇾 to engage with the {base_monster}, 🇳 to pass. Message will timeout in 60 seconds.")

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
        em.add_field(name="\u200b",value='You can use the Thokim Epitome gifted by the Mages to find out more about a monster by `.more <object name>`. For example, `.more mogosok`.')
        
        m: discord.Message = await ctx.send(embed=em)
        
        if not block:
            await m.add_reaction('🇾')
            await m.add_reaction('🇳')

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
                    return monster_data
            
                else: # user has passed
                    
                    class MonsterSpawnFailed:
                        pass
                
                    raise MonsterSpawnFailed
                
        else:
            return monster_data # do not ask if user wants to fight monster or not if block is True
        
monster_tools = _monster_tools()