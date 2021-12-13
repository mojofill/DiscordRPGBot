from typing import Literal


class _Items:
    def __init__(self):
        pass
    
    def getRewardType(self, reward_name: str) -> Literal['xp', 'weapons', 'bow', 'valuables', 'armor', 'loot', 'armor']:
        """Takes in `reward_name` and returns a string representing the type of reward it is - `sword` would return `weapon`"""

        # TODO: finish this

        items = {
            # MISCELLANEOUS
                "xp":"xp",

            # weapons
                # basic weapons
                "mogo club":"weapons",
                "mogo spear":"weapons",
                "mogo bat":"weapons",
                "wooden bat":"weapons",
                "wooden spiked bat":"weapons",
                "wooden spear":"weapons",
                "knight's broadsword":"weapons",
                "knight's claymore":"weapons",
                "steel spear":"weapons",
                "steel sword":"weapons",
                "steel mace":"weapons",
                "stick":"weapons",

                # elemental weapons
                    # ranged - staffs
                    "lightning staff":"weapons",
                    "blaze staff":"weapons",
                    "ice staff":"weapons",

                "flame sword":"weapons",
                "ice sword":"weapons",

                # ranged weapons

            # bows
                "mogo bow":"bow",
            
            # valuables
                "emeralds":"valuables",
                "ruby":"valuables",
                "sapphire":"valuables",
                "topaz":"valuables",
                "opal":"valuables",
                "diamond":"valuables",
            
            # ARMOR

            # LOOT
                "mogo fang":"loot",
                "mogo guts":"loot",
                "mogo horn":"loot"
        }

        return items[reward_name]
    
    def getArmorData(self, armor_name: str):
        pass

ItemsTool = _Items()