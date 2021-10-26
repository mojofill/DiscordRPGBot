import random
import time
from datetime import datetime, timedelta
import threading
from typing import Literal

def writeToFile(msg: str):
    with open('./test/output.txt','a') as f:
        f.write(f'{msg}\n')

shield_data = {
    "name":"mogo shield",
    "durability":12,
    "knockback":4
}

monster_data = {
    "name":"mogosok",
    "health":30,
    "attack type":"melee",
    "weapon":{
        "name":"mogo club",
        "durability":20,
        "damage":2,
        "attack time":0.5
    },
    "shield":shield_data,
    "equipment type":"weapon",
    "fight back countdown":15,
    "shot probability":5 # this means one out of five times the monster decides to attack, not wait
}

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

user_data = {"healthpoints":{"health":30,"energy":100000}}

hp = user_data["healthpoints"]
bp = {
    "weapons": { # umbrella dict containing all weapon data
        "weapons":{
            "mogo club":{
                "damage":2,
                "attack time":0.5
            }
        }, # contains all the weapons the user has
        "equipped weapon":"mogo club",
        "limit":7,
        "damage increase multiply":1
    },
    "bows": { # umbrella dict containing all weapon data
        "bows":{
            "mogo bow":{
                "damage":8,
                "durability":20,
                "attack time":0.5
            }
        }, # contains all the weapons the user has
        "equipped bow":"mogo bow",
        "limit":7,
        "damage increase multiply":1
    }
}

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
        self.equipment_durability: int = monster_data[equipment_type]["durability"]
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

        self.times_of_attack = []

        self.attack_because_player_wouldnt_move: float = time.time()
        self.shot_probababilty: int = monster_data["shot probability"]
    
    def incrementHealth(self, amount: int):
        """Increments the given amount `amount: int` to monster's heath (`self.health`)"""

        self.health += amount # if to take away health amount should be negative
    
    def throwWeapon(self) -> bool:
        """Throws the monster's weapon at the player - deals 3x damage but weapon instantly breaks. Returns `True` if the user is killed by this blow, `False` if not"""

        self.enemyPlayerObject.deduceHealth(3 * self.damage)

        if self.enemyPlayerObject.health <= 0:
            return True
        
        else:
            self.equipment_broke = True
            return False
    
    def startAttackLoop(self):
        """Asyncronous method will starting asyncio loop that will get the monster to start attacking the user."""

        open_attack_chance = False # if this is set True then that means the AI thinks that this is a good time to fight the player, because his armor either broke or he is knocked down

        def getVerbOfWeaponName(weapon_name: str):
            """Returns the past tense verb that goes with the weapon name"""
            base_weapon_name = weapon_name.split(' ')[1]

            verb_from_weapon = {
                "club":"struck",
                "spear":"stabbed"
            }

            return verb_from_weapon[base_weapon_name]

        while self.enemyPlayerObject.health > 0 and self.health > 0:
            if open_attack_chance: # this means the monster has decided to attack the user
                """Code here will deal the actual damage to the user"""

                time.sleep(self.attack_wait)

                try:
                    weapon_name: str = self.wpn["name"]
                    weapon_damage: int = self.wpn["damage"]

                    verb = getVerbOfWeaponName(weapon_name)

                    msg = f'A {self.name} used its {weapon_name} and {verb} you, dealing {weapon_damage}.'

                    dmg = weapon_damage

                except TypeError: # meaning wpn was None (meaning the equipment the monster has is a bow) and is not "subscriptable" - cannot access keys of wpn because its not a dict
                    base_bow_damage = self.bow["damage"]
                    
                    msg = f'A {self.name} shot its {self.bow["name"]} at you, dealing {base_bow_damage}'
                    
                    dmg = base_bow_damage

                self.enemyPlayerObject.deduceHealth(dmg)
                self.equipment_durability -= 1

                now = datetime.now()

                hour = now.hour
                minute = now.minute
                second = now.second
                
                writeToFile(msg + f' -- {hour}:{minute}:{second} -- ' + f'monster health is {self.health}. your health is {self.enemyPlayerObject.health}')

                open_attack_chance = False

                self.times_of_attack.append(f'{hour}:{minute}:{second}')
            
            else:
                """Code here will decide whether to wait for an opening or randomly (read = stupidly) try to attack."""
                
                number = random.randint(1, 50)

                if number == 1:
                    open_attack_chance = True
                    
                    writeToFile('about to "suddenly" attack the player - sleeping for one second to give user time to prepare?? might delete this sleep.')
                    time.sleep(1) # might delete

                    writeToFile(f"{self.name} decided to suddenly attack the player")
                
                else: # do NOT be stupid - try to do something smart
                    """Take in data from player and decide what the next step should be"""

                    if not self.equipment_durability <= 4: # this means that the monster's weapon is not about to break
                        if self.enemyPlayerObject.health <= 2 * self.damage: # this means that the player is only 2 hits away from death
                            # higher chance of monster hitting the player

                            chance = random.randint(1, 3)

                            if chance in range(1, 3): # excludes 3
                                open_attack_chance = True

                                msg = f'monster sees you are 2 or 1 shots away from death, decided to just speed things up.'

                                writeToFile(msg)
                                
                        else: # user is not about to die
                            # based on the monster's intelligence it can notice if the user is currently in attack and attack in the perfect time
                            
                            if self.enemyPlayerObject.in_attack and self.intelligence > 2:
                                writeToFile('monster has seen that you are in the middle of an attack')
                                if self.intelligence == 3:
                                    number = random.randint(1, 4)

                                else:
                                    number = random.randint(1, 3)

                                if number == 1: # if number is 1 then that means the monster has enough intelligence to spot when the player is in the middle of an attack and strike back
                                    writeToFile(f"{self.name} sees that you are currently in attack AND is smart enough to attack back.")
                                    open_attack_chance = True
                            
                            else: # player is not in the middle of attacking - the monster can choose to attack or wait.
                                
                                if time.time() - self.fightback_countdown >= self.enemyPlayerObject.time_of_previous_move and time.time() - self.attack_because_player_wouldnt_move > self.attack_because_player_wouldnt_move: # more than 10 seconds have passed from the player's previous move AND since the last time the monster has had to fight the player because he or she refused to attack back
                                    
                                    open_attack_chance = True

                                    writeToFile(f'{self.name} sees that you have not done anything for 10 seconds, and will attack you.')

                                    self.attack_because_player_wouldnt_move = time.time() # save the time

                                else:
                                    time.sleep(2) # it takes the monster 2 seconds to decide to attack or not

                                    number = random.randint(1, self.shot_probababilty) # 1 out of 5 chance monster will attack you. should probably make this customizable

                                    if number == 1:
                                        writeToFile(f"{self.name} has decided to fight you")
                                        open_attack_chance = True
                                    
                                    else:
                                        writeToFile(f'number = {number} the monster has decided to not fight you')
                    
                    else: # monster weapon about to break - throw weapon at player to gain 3x attack damage - however weapon instant break, resorts to punching if NOT player already dead
                        player_dead = self.throwWeapon()

                        if player_dead:
                            msg = 'you died :('
                            
                            writeToFile(msg)
            
            if self.enemyPlayerObject.health <= 0:
                msg = 'you died :('

                writeToFile(msg)
            
        if self.health <= 0:
            writeToFile('you have killed the monster!')
        
        else:
            writeToFile(f'{self.name} has killed you...')

        writeToFile('\n')

        for i in self.times_of_attack:
            writeToFile(i)

class Player:
    def __init__(self):
        self.health = hp["health"] # current health the user has left
        self.energy = hp["energy"] # current energy the user has left

        self.in_attack = False
        self.time_of_previous_move: float = time.time()

    def deduceHealth(self, base_damage: int) -> None:
        """Takes IN the user's armor reduction, and takes away the final damage reduce."""

        hp["health"] -= base_damage

        self.health -= base_damage

    def attack(self, form: Literal["melee", "bow"], monster: Monster) -> None:
        """Takes in the form, which can only be `melee` or `bow`, and attacks the monster."""

        if form == 'melee':
            """Attack monster with weapon"""

            equipped_wpn: str = bp["weapons"]["equipped weapon"]
            
            damage: int = bp["weapons"]["weapons"][equipped_wpn]["damage"]

            attack_wait = bp["weapons"]["weapons"][equipped_wpn]["attack time"]
    
        else:
            """Attack monster with bow"""

            equipped_bow: int = bp["bows"]["equipped bow"]

            damage: int = bp["bows"][equipped_bow]

            attack_wait = bp["bows"]["bows"][equipped_bow]["attack time"]
        
        self.in_attack = True
        
        time.sleep(attack_wait)

        self.in_attack = False
            
        monster.incrementHealth(-damage)

        # if on challenge mode, every few seconds monster wll regain health

        writeToFile(f'you have attacked the monster, dealing {damage}. Monster remaining health: {monster.health}')

        self.time_of_previous_move = time.time()
    
player = Player()

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

def monsterLoopThread():
    start = time.time()
    writeToFile('time of attack start - ' + datetime.now().strftime('%H:%M:%S'))
    
    writeToFile(f'your current health: {player.health}. monster current health: {monster.health}\n')

    monster.startAttackLoop()

    end = time.time()
    writeToFile('\ntime ended = ' + datetime.now().strftime('%H:%M:%S'))
    writeToFile('\nbattle time = ' + str(end - start))

def getPlayerInput():
    while True:
        input('Enter to attack: ')

        player.attack('melee', monster)

MonsterLoopThread = threading.Thread(target=monsterLoopThread)
PlayerInputThread = threading.Thread(target=getPlayerInput)

MonsterLoopThread.start()
PlayerInputThread.start()