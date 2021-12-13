
"""
Add subquests in the quests.
"""

import discord
import asyncio
import random
from discord.ext import commands
from typing import Literal

from dev.db import Database
from dev.MonsterTools import MonsterTools
from dev.tools import tools

class _Quests:
    def __init__(self) -> None:
        """
        Quests are an important part of the game. There are 2 types of quests. 
        """

    def __getRandomQuestId(self, quests_data: dict, quest_category: Literal['main', 'side'], quest_type: Literal['item', 'fight', 'location']):
        randomId = None

        base_quest_limit = len(quests_data[quest_category][quest_type]) + 30

        while True:
            randomId = random.randint(0, base_quest_limit)

            if randomId not in quests_data[quest_category][quest_type]:
                return randomId

    def getUserMainQuests(self, user: discord.User) -> list:
        """Returns a `list` containing all the quests (type `str`)."""
    
    async def __InformFightQuest(self, ctx: commands.Context, target: str, amount: int, location: str = None):
        msg = f"""
            {ctx.author.mention} Quest added! Defeat a `{target}` **{amount}** times to earn some rewards!
            """

        if location != None:
            msg += f"\nReport back to `{location}` to gain your reward when you are done."

        msg += '\nGood luck!'

        await ctx.send(msg)
    
    async def __InformItemQuest(self, ctx: commands.Context, item: str, amount: int, location: str = None):
        msg = f"""
        {ctx.author.mention} Quest added! Find and get **{amount}** `{item}`.
        """

        if location != None:
            msg += f"Report back to `{location}` to recieve your reward!"

        await ctx.send(msg)
    
    async def __InformLocationQuest(self, ctx: commands.Context, item: str, amount: int, location: str = None):
        msg = f"""

        """

    async def setFightQuestSingularTarget(self, ctx: commands.Context, quest_name: str, quest_category: Literal['main', 'side'], target: str, amount: int, location: str = None, session: bool = False):
        """
        Starts a fight quest, where the player has to fight a certain monster. 
        
        NOTE: QUEST TYPES SUBJECT TO CHANGE

        Takes in arguments: `ctx`, `quest_name`, `quest_category`, `target`, `amount`, `command = None`
        
        `type` is the type of quest being added: `main` or `side`, for main quests and side quests respectively
        
        `quest_name` is the name of the quest to add.

        If `session` == `True`, then create an ingame session, where the player is contained in a place and has to finish fighting bosses.
        """

        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        quests = user_data["quests"]

        quests[quest_category]["fight"] = {
            "name":quest_name,
            "target":target, # the thing that the player is supposed to fight, from monster to another player
            "amount":amount
        }

        await self.__InformFightQuest(ctx, target, amount, location)
    
    async def setFightQuestMonsterCamp(self, ctx: commands.Context, quest_name: str, quest_category: str, monsters: list, preset_chest: dict = None, session: bool = False):
        """
        `monsters`: `dict`
        Create monsters as a list of dictionaries, with first index being first monster player faces in the monster camp.
        Set `preset_chest` to a dictionary if the monster camp is built with a chest that is already determined, such as a monster camp for a quest.
        `session` tells if the player cannot do anything else until the monster camp is cleared.
        ```
        monsters = {
            [
                {
                    "name":"mogosok",
                    "rank":int
                },
                {
                    "name":"jaursok",
                    "rank":int
                }
            ]
        }
        ```
        """

        user_data = Database.getStorageData(ctx.author)

        for monster in monsters:
            monster: dict

            # monster = {
            #     "name":monster_type,
            #     "rank":monster_rank,
            # }

            monster_type: str = monster["name"]
            monster_rank: int = monster["rank"]

            await MonsterTools.spawnMonster(ctx, monster_type, monster_rank)

            def check():
                monster_data = user_data["monsters"]
                return monster_data["preview monster"] == None # only set to None when player is finished fighting

            if session:
                await tools.confinePlayer(ctx.author, check)
            
            else:
                await tools.wait(check)
        
        await ctx.send('you have finished monster camp')
    
    async def setItemQuest(self, ctx: commands.Context, user_data: dict, quest_name: str, quest_category: Literal['main', 'side'], item_name: str, amount: int, reward: dict, location: str = None, subItemQuests: list = None):
        """
        Sets an item quest, where the player has to find a specific amount of items.
        `subItemQuests` is argument that is `type list` and essentially tells me what items the player needs to get right after the quest.
        """

        quests = user_data["quests"]

        randomQuestId = self.__getRandomQuestId(quests, quest_category, 'item')
        
        quests[quest_category]["item"][randomQuestId] = {
            "show":True,
            "item":item_name,
            "amount":amount,
            "reward":reward
        }

        linkedQuests = [randomQuestId]

        index = 0
        
        if subItemQuests != None:
            for item_data in subItemQuests:
                randomId = self.__getRandomQuestId(quests, quest_category, "item")
                
                item_data["show"] = False # do not show this yet
                
                quests[quest_category]["item"][randomId] = item_data

                prev_quest_id = linkedQuests[index]
                
                quests[quest_category]["item"][prev_quest_id]["next"] = randomId

                index += 1

        await self.__InformItemQuest(ctx, item_name, amount, location)

    async def setLocationQuest(self, user_data: dict, quest_name: str, quest_category: Literal['main', 'side'], location: str):
        """Starts a location quest, where the player has to get to a specifc location for a quest."""

        quests = user_data["quests"]

        quests[quest_name] = {
            "type":"location",
            "category":quest_category,
            "location":location
        }

    async def FinishedFightQuest(self, ctx: commands.Context, quest_name: str):
        user: discord.User = ctx.author

        await ctx.send(f'{user.mention} You have finished quest {quest_name}!')

QuestsTool = _Quests()