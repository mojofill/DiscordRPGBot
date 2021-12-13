import asyncio
import discord
from discord.ext import commands
from dev.tools import tools
from dev.MonsterTools import MonsterTools
from dev.db import Database

class _Challenges:
    def __init__(self) -> None:
        pass

    async def startConfinedFightChallenge(self, challenge_name: str, ctx: commands.Context, monsters: list):
        """
        Example `monsters` value
        ```
        [{"mogosok":1}, {"baursok":2}]
        ```
        A list of dicts, with each dict being {(`str`) monster_name: (`int`) monster rank}
        """

        user_data = Database.getStorageData(ctx.author)
        location = user_data["location"]

        location["confined"] = True # confine player
        
        player_monster_data = user_data["monsters"]

        await ctx.send(f"Starting challenge: {challenge_name.title()}")

        period = 0.5

        for monster_data in monsters:
            monster_data: dict

            monster_type: str = list(monster_data.keys())[0]
            monster_rank: int = monster_data[monster_type]
            
            await MonsterTools.spawnMonster(ctx, monster_type, monster_rank)

            # do not send "Challenge complete" until everything has been done
            while True:
                if player_monster_data["preview monster"] == None: # if preview monster is None, that means the player has stopped fighting monsters
                    await ctx.send('Challenge complete!')
                    
                    location["confined"] = False

                    break

                await asyncio.sleep(period)
    
ChallengesTool = _Challenges()