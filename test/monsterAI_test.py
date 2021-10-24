import random
import time
import json
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
    "health":13,
    "attack type":"melee",
    "weapon":{
        "name":"mogo club",
        "durability":20,
        "damage":7,
        "attack time":0.5
    },
    "shield":shield_data,
    "equipment type":"weapon"
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

user_data = {"healthpoints":{"health":100,"energy":100000}}

hp = user_data["healthpoints"]
bp = {
    "weapons": { # umbrella dict containing all weapon data
        "weapons":{
            "mogo club":{
                "damage":12,
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
    
    def incrementHealth(self, amount: int):
        """Increments the given amount `amount: int` to monster's heath (`self.health`)"""

        self.health += amount # if to take away health amount should be negative
    
    def throwWeapon(self) -> bool:
        """Throws the monster's weapon at the player - deals 3x damage but weapon instantly breaks"""

        self.enemyPlayerObject.deduceHealth(3 * self.damage)

        if self.enemyPlayerObject.health <= 0:
            return True
        
        else:
            self.equipment_broke = True
            return False
    
    def startAttackLoop(self):
        """Asyncronous method will starting asyncio loop that will get the monster to start attacking the user."""

        open_attack_chance = False # if this is set True then that means the AI thinks that this is a good time to fight the player, because his armor either broke or he is knocked down
        
        fightBool = True # if this becomes false then we stop the loop

        def getVerbOfWeaponName(weapon_name: str):
            """Returns the past tense verb that goes with the weapon name"""
            base_weapon_name = weapon_name.split(' ')[1]

            verb_from_weapon = {
                "club":"struck",
                "spear":"stabbed"
            }

            return verb_from_weapon[base_weapon_name]

        while fightBool and self.health > 0:
            if open_attack_chance: # this means the monster has decided to attack the user
                """Code here will deal the actual damage to the user"""

                time.sleep(self.attack_wait)

                try:
                    weapon_name: str = self.wpn["name"]
                    weapon_damage: int = self.wpn["damage"]

                    self.enemyPlayerObject.deduceHealth(weapon_damage)

                    verb = getVerbOfWeaponName(weapon_name)

                    msg = f'A {self.name} used its {weapon_name} and {verb} you, dealing {weapon_damage}.'

                    dmg = weapon_damage

                    hp["health"] -= weapon_damage

                except TypeError: # meaning wpn was None (meaning the equipment the monster has is a bow) and is not "subscriptable" - cannot access keys of wpn because its not a dict
                    base_bow_damage = self.bow["damage"]
                    
                    msg = f'A {self.name} shot its {self.bow["name"]} at you, dealing {base_bow_damage}'
                    
                    dmg = base_bow_damage

                self.enemyPlayerObject.deduceHealth(dmg)
                
                writeToFile(msg)

                open_attack_chance = False
            
            else:
                """Code here will decide whether to wait for an opening, randomly (read = stupidly) try to attack or run away (this is only if the user has not attacked and only retreated for a duration of time."""
                
                # how i think it should work:
                # the monster usually waits for 3 seconds and if the user has not done anything it will attack
                # other times it will be stupid and charge the player
                # sometimes it will charge attack, but depending on the monster type the chances of charge attack will vary

                # decide whether to wait or be stupid
                number = random.randint(1, 50)

                if number == 1: # just start attacking the user without waiting
                    open_attack_chance = True
                    
                    time.sleep(1) # at least sleep 1 second to give the user time to think and prepare

                    writeToFile("monster decided to suddenly attack the player")
                
                else: # do NOT be stupid - try to do something smart
                    """Take in data from player and decide what the next step should be"""

                    if not self.equipment_durability <= 4: # this means that the monster's weapon is not about to break
                        if self.enemyPlayerObject.health <= 2 * self.damage: # this means that the player is only 2 hits away from death
                            # higher chance of monster hitting the player

                            chance = random.randint(1, 3)

                            if chance in range(1, 3): # 1 or 2 - does not include 3
                                # hit the player
                                open_attack_chance = True

                                msg = f'A {self.name} used it\'s weapon on you, dealing {self.damage}'

                                writeToFile(msg)
                                
                        else: # user is not about to die
                            # now, based on the monster's intelligence, it can notice if the user is currently in attack and attack in the perfect time
                            if self.enemyPlayerObject.in_attack: # code below will run if the enemy player is currently in attack - else just passes
                                if not self.intelligence <= 2: # if the monster is less than 2 then just forget about it - too dumb
                                    if self.intelligence == 3:
                                        number = random.randint(1, 4)

                                    else:
                                        number = random.randint(1, 3)

                                    if number == 1: # if number is 1 then that means the monster has enough intelligence to spot when the player is in the middle of an attack and strike back
                                        writeToFile("monster sees that you are currently in attack AND is smart enough to attack back.")
                                        open_attack_chance = True
                            
                            else: # this means that the user is not currently in the middle of attacking - the monster can choose to attack or wait.
                                number = random.randint(1, 50)

                                if number in range(1, 6):
                                    writeToFile(f"number = {number} - monster has decided to fight you - you are not in the middle of an attack")
                                    open_attack_chance = True
                                    
                                time.sleep(0.8) # just so that the timing can be better
                    
                    else: # monster weapon about to break - throw weapon at player to gain 3x attack damage - however weapon instant break, resorts to punching if NOT player already dead
                        player_dead = self.throwWeapon()

                        if player_dead:
                            msg = 'you died :('
                            
                            writeToFile(msg)

                            fightBool = False
            
            if self.enemyPlayerObject.health <= 0:
                fightBool = False

                msg = 'you died :('

                writeToFile(msg)

class Player:
    def __init__(self):
        self.health = hp["health"] # current health the user has left
        self.energy = hp["energy"] # current energy the user has left

        self.in_attack = False

    def deduceHealth(self, base_damage: int) -> None:
        """Takes IN the user's armor reduction, and takes away the final damage reduce."""

        hp["health"] -= base_damage

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
    monster.startAttackLoop()

def getPlayerInput():
    while True:
        time.sleep(3)

        with open('./test/fight.json','r') as f:
            data = json.load(f)
        
        fight = data["fight"]

        if fight != 'a':
            player.attack('melee', monster)

            data["fight"] = 'a'
        
            with open('./test/fight.json','w') as f:
                json.dump(data, f, indent=4)

MonsterLoopThread = threading.Thread(target=monsterLoopThread)
PlayerInputThread = threading.Thread(target=getPlayerInput)

MonsterLoopThread.start()
PlayerInputThread.start()