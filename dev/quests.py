import discord
import asyncio
from discord.ext import commands
from typing import Literal

from dev.db import Database

class _Quests:
    def __init__(self) -> None:
        """
        Quests are an important part of the game. There are 2 types of quests. 
        """

    def getUserMainQuests(self, user: discord.User) -> list:
        """Returns a `list` containing all the quests (type `str`)."""

    async def __startFightQuest(self, user_data: dict, quest_name: str, command):
        pass

    async def __startLocationQuest(self, user_data: dict, quest_name: str, location: str,command):
        """Starts a location quest, where the player has to get to a specifc location for a quest."""

    async def __startUndefinedQuest(self, user_data: dict, quest_name: str, command, extra_args: dict = None):
        pass

    async def __FinishedFightQuest(self, ctx: commands.Context, quest_name: str):
        user: discord.User = ctx.author

        await ctx.send(f'{user.mention} You have finished quest {quest_name}!')

    async def startNewQuest(self, user: discord.User, quest_name: str, quest_category: Literal['main', 'side'], quest_type: Literal['fight', 'location', 'undefined'], command=None, location: str = None, monster_type: str = None, next_quest: str = None, **kwargs):
        """
        NOTE: QUEST TYPES SUBJECT TO CHANGE

        Takes in arguments: `type`, `quest_name`, `quest_category`, `quest_type`
        
        `type` is the type of quest being added: `main` or `side`, for main quests and side quests respectively
        
        `quest_name` is the name of the quest you wnat to add.

        `quest_category` is the category bot puts the quest in: `main` or `side`
        
        `quest_type` is the type of quest it is: `fight`, `location` or `undefined`.
        """
        
        user_data = Database.getStorageData(user)

        if quest_type == 'fight':
            await self.__startFightQuest(user_data, quest_name)

        elif quest_type == 'location':
            await self.__startLocationQuest(user_data, quest_name, command)
        
        else:
            await self.__startUndefinedQuest(user_data, quest_name, command, kwargs)

quests = _Quests()