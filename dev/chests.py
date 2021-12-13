import discord
import random
from discord.ext import commands
from typing import Literal
from dev.db import Database

class _Chests:
    def __init__(self) -> None:
        pass

    async def spawnChest(self, ctx: commands.Context, type: Literal['monster camp', 'temple', 'treasure', 'wooden'], preset_chest_data: dict = None):
        """Appends to `"chests"` list in chests dict of user_data"""
        user: discord.user = ctx.author
        user_data = Database.getStorageData(user)

        chests: dict = user_data["chests"]

        # chests["chests"] = []

        if preset_chest_data != None:
            chests["chests"].append(preset_chest_data)
            await ctx.send(f'A `{type}` chest has appeared! Use `.open` to open the chest.')

            return

        def getChestData():
            # range: 100
            # NOTE: subject to change
            
            number = random.randint(0, 999)

            chestFromTypeDict = {
                "monster camp":{
                    (0, 400):"equipment",
                    (400, 700):"pet shards",
                    (700, 900):"valuables",
                    (900, 960):"potions",
                    (960, 1000):"armor"
                },
                "temple":{
                    (0, 500):"equipment",
                    (500, 800):"pet shards",
                    (800, 950):"valuables",
                    (950, 970):"potions",
                    (970, 1000):"armor"
                },
                "treasure":{
                    (0, 300):"equipment",
                    (300, 400):"pet shards",
                    (400, 950):"valuables",
                    (950, 990):"potions",
                    (990, 1000):"armor"
                },
                "wooden":{
                    (0, 10):"equipment",
                    (10, 30):"pet shards",
                    (30, 35):"potions",
                    (35, 36):"armor",
                    (36, 1000):"valuables"
                }
            }

            def getAmountOfRewardFromChestType(reward_type: str) -> int:
                """Returns an amount that represents the amount of stuff player recieves from a certain chest."""
                reward_amounts = {
                    "wooden":{
                        "equipment":[0,1],
                        "pet shards":[5,50],
                        "valuables":[5,20]
                    },
                    "temple":{
                        "equipment":[0,30],
                        "pet shards":[20,50],
                        "valuables":[20,30],
                        "potions":[45,50],
                        "armor":[1, 1]
                    },
                    "treasure":{
                        "equipment":[0,20],
                        "pet shards":[0,50],
                        "valuables":[30,45],
                        "potions":[5, 10]
                    },
                    "monster camp":{
                        "equipment":[0,30],
                        "pet shards":[0,10],
                        "valuables":[25,50],
                        "potions":[10, 15],
                        "armor":[1,1]
                    }
                }

                amount: int = random.randint(reward_amounts[type][reward_type][0], reward_amounts[type][reward_type][1])

                return amount
            
            def getSpecificArmorPieceFromSet(armor_set_name: str):
                armor_pieces_data = {
                    "leather set":{
                        "monster camp":{
                            (0, 30):"leather helm",
                            (30, 66):"leather chestplate",
                            (66, 100):"leather boots"
                        },
                        "temple":{
                            (0, 30):"leather helm",
                            (30, 66):"leather chestplate",
                            (66, 100):"leather boots"
                        },
                        "treasure":{
                            (0, 30):"leather helm",
                            (30, 66):"leather chestplate",
                            (66, 100):"leather boots"
                        },
                        "wooden":{
                            (0, 30):"leather helm",
                            (30, 56):"leather chestplate",
                            (56, 100):"leather boots"
                        }
                    },
                    "steel set":{
                        "monster camp":{
                            (0, 33):"steel helm",
                            (33, 66):"steel chestplate",
                            (66, 100):"steel greaves"
                        },
                        "temple":{
                            (0, 30):"steel helm",
                            (30, 66):"steel chestplate",
                            (66, 100):"steel greaves"
                        },
                        "treasure":{
                            (0, 30):"steel helm",
                            (30, 66):"steel chestplate",
                            (66, 100):"steel greaves"
                        },
                        "wooden":{
                            (0, 30):"steel helm",
                            (30, 56):"steel chestplate",
                            (56, 100):"steel greaves"
                        }
                    },
                    "soldier set":{
                        "monster camp":{
                            (0, 30):"soldier's helm",
                            (30, 76):"soldier's chestplate",
                            (76, 100):"soldier's greaves"
                        },
                        "temple":{
                            (0, 30):"soldier's helm",
                            (30, 66):"soldier's chestplate",
                            (66, 100):"soldier's greaves"
                        },
                        "treasure":{
                            (0, 35):"soldier's helm",
                            (35, 66):"soldier's chestplate",
                            (66, 100):"soldier's greaves"
                        },
                        "wooden":{
                            (0, 30):"soldier's helm",
                            (30, 66):"soldier's chestplate",
                            (66, 100):"soldier's greaves"
                        }
                    },
                    "diamond set":{
                        "monster camp":{
                            (0, 30):"diamond helm",
                            (30, 66):"diamond chestplate",
                            (66, 100):"diamond greaves"
                        },
                        "temple":{
                            (0, 33):"diamond helm",
                            (33, 66):"diamond chestplate",
                            (66, 100):"diamond greaves"
                        },
                        "treasure":{
                            (0, 30):"diamond helm",
                            (30, 60):"diamond chestplate",
                            (60, 100):"diamond greaves"
                        },
                        "wooden":{
                            (0, 40):"diamond helm",
                            (40, 56):"diamond chestplate",
                            (56, 100):"diamond greaves"
                        }
                    },
                    "radiant set":{ # set bonus: cold resistance
                        "monster camp":{
                            (0, 30):"radiant helm",
                            (30, 66):"radiant chestplate",
                            (66, 100):"radiant greaves"
                        },
                        "temple":{
                            (0, 30):"radiant helm",
                            (30, 66):"radiant chestplate",
                            (66, 100):"radiant greaves"
                        },
                        "treasure":{
                            (0, 30):"radiant helm",
                            (30, 66):"radiant chestplate",
                            (66, 100):"radiant greaves"
                        },
                        "wooden":{
                            (0, 30):"radiant helm",
                            (30, 66):"radiant chestplate",
                            (66, 100):"radiant greaves"
                        }
                    },
                    "glaitol set":{
                        "monster camp":{
                            (0, 30):"glaitol helm",
                            (30, 66):"glaitol chestplate",
                            (66, 100):"glaitol greaves"
                        },
                        "temple":{
                            (0, 30):"glaitol helm",
                            (30, 66):"glaitol chestplate",
                            (66, 100):"glaitol greaves"
                        },
                        "treasure":{
                            (0, 30):"glaitol helm",
                            (30, 66):"glaitol chestplate",
                            (66, 100):"glaitol greaves"
                        },
                        "wooden":{
                            (0, 30):"glaitol helm",
                            (30, 66):"glaitol chestplate",
                            (66, 100):"glaitol greaves"
                        }
                    },
                    "platinum set":{
                        "monster camp":{
                            (0, 30):"platinum helm",
                            (30, 66):"platinum chestplate",
                            (66, 100):"platinum greaves"
                        },
                        "temple":{
                            (0, 30):"platinum helm",
                            (30, 66):"platinum chestplate",
                            (66, 100):"platinum greaves"
                        },
                        "treasure":{
                            (0, 30):"platinum helm",
                            (30, 66):"platinum chestplate",
                            (66, 100):"platinum greaves"
                        },
                        "wooden":{
                            (0, 30):"platinum helm",
                            (30, 66):"platinum chestplate",
                            (66, 100):"platinum greaves"
                        }
                    },
                    "champion set":{
                        "monster camp":{
                            (0, 30):"champion's helm",
                            (30, 66):"champion's chestplate",
                            (66, 100):"champion's greaves"
                        },
                        "temple":{
                            (0, 30):"champion's helm",
                            (30, 66):"champion's chestplate",
                            (66, 100):"champion's greaves"
                        },
                        "treasure":{
                            (0, 30):"champion's helm",
                            (30, 66):"champion's chestplate",
                            (66, 100):"champion's greaves"
                        },
                        "wooden":{
                            (0, 30):"champion's helm",
                            (30, 66):"champion's chestplate",
                            (66, 100):"champion's greaves"
                        }
                    }
                }

                number = random.randint(0, 100)

                for _range in armor_pieces_data[armor_set_name][type]:
                    if number in range(_range[0], _range[1]):
                        armor_piece = armor_pieces_data[type][_range]

                        return armor_piece
                    
                class DidNotCreateArmorPiece(Exception):
                    pass

                raise DidNotCreateArmorPiece("Function did not return an armor piece, check code.")
            
            def getSpecificRewardFromType(reward_type: str) -> str:
                """Returns a `string` which represents the reward the player recieves"""

                rewards = {
                    "armor":{
                        "monster camp":{
                            (0, 50):"leather set",
                            (50, 99):"steel set",
                            (99, 100):"soldier set"
                        },
                        "temple":{
                            (0, 60):"leather set",
                            (60, 99):"steel set",
                            (99, 100):"soldier set"
                        },
                        "treasure":{
                            (0, 99):"leather set",
                            (99, 100):"steel set"
                        },
                        # impossible to get armor from wooden chest
                        # "wooden":{
                        #     (0, 100):"leather set"
                        # }
                    },
                    # theres not really "types" of pet shards - pet shards are just pet shards
                    # "pet shards":{}
                    "valuables":{
                        "monster camp":{
                            (0, 50):"topaz", # 50%
                            (50, 90):"opal", # 40%
                            (90, 100):"diamond" # 10%
                        },
                        "temple":{
                            (0, 5):"emerald", # 5%
                            (5, 30):"opal", # 25%
                            (30, 70):"sapphire", # 40%
                            (70, 99):"ruby", # 29%
                            (99, 100):"diamond" # 1%
                        },
                        "treasure":{
                            (0, 400):"emerald", # 40%
                            (400, 700):"ruby", # 30%
                            (700, 900):"sapphire", # 20%
                            (900, 970):"topaz", # 7%
                            (970, 999):"opal", # 2.9%
                            (999, 1000):"diamond" # 0.1%
                        },
                        "wooden":{
                            # divide by 10000
                            (0, 9000):"emerald", # 90%
                            (9000, 9900):"ruby", # 9%
                            (9900, 9990):"sapphire", # 0.9%
                            (9990, 9995):"topaz", # 0.05%
                            (9995, 9999):"opal", # 0.04%
                            (9999, 10000):"diamond" # 0.01%
                        }
                    },
                    "potions":{
                        "monster camp":{
                            (0, )
                        }
                    }
                }

                data = rewards[reward_type]

                data_keys = list(data.keys())

                last_number = data_keys[-1][1]

                number = random.randint(0, last_number)

                for _range in data_keys:
                    if number in range(_range[0], _range[1]):
                        reward: str = data[_range]
                        return reward

            chest_data_probability = chestFromTypeDict[type]

            chest_data = {"type":type, "items":[]}

            # get all the stuff that the player got from the chest
            for _range in chest_data_probability:
                if number in range(_range[0], _range[1]):
                    reward_type: str = chest_data_probability[_range] # euquipment, pet shards, valuables, potions, or armor
                    
                    specific_reward = getSpecificRewardFromType(reward_type) # e.g. heat resistance potion
                    
                    if reward_type == 'armor':
                        specific_reward = getSpecificArmorPieceFromSet(specific_reward)

                    reward_amount = getAmountOfRewardFromChestType(reward_type)

                    chest_data["items"][reward_type] = {specific_reward:reward_amount}

                    # example chest_data:
                    # {
                    #     "valuables":{
                    #         "opal":10,
                    #         "emeralds":20
                    #     },
                    #     "armor":{
                    #         "leather set":1
                    #     }
                    # }

            return chest_data
        
        chest_data = getChestData()

        chests["chests"].append(chest_data)

        await ctx.send(f'A `{type}` chest has appeared! Use `.open` to open the chest.')

ChestsTool = _Chests()