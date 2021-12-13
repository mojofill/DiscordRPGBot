import discord
from discord.ext import commands
from dev.db import Database
from dev.tools import tools
from dev.api import db

class Quests(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Quests extension ready. ')

    @commands.command(name='quests',aliases=['quest,','qt'])
    async def _quests(self,ctx):
        user = ctx.author
        
        if not tools.user_at_required_location(user,"pub"):
            res = tools.travel(user,"pub")

            if res == "walking":
                await tools.walkuser(ctx,user,"pub")

            else:
                await ctx.send(res)
        
        quests = db.quests.find_one({"_id":user.id})
        msg = 'This is all your quests:\n'
        for quest_id in quests["quests"]:
            name = quests["quests"][quest_id]["name"]
            progress = quests["quests"][quest_id]["progress"]
            msg += f"{name} -> Progress: {progress}\n"

        await ctx.send(msg)
    
    @commands.command()
    async def questlocation(self, ctx: commands.Context):
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)

        quests = user_data["quests"]

        focused_quest: str = quests["focused quest"]

        if focused_quest == None:
            await ctx.send('❌ Focused quest is `None`. Use `.focus <quest id>` to focus on any quest.')
            return
        
        try:
            location = quests["location"]
        except:
            await ctx.send(f"❌ Quest has no `location` attribute: {focused_quest} can be completed anywhere..")

            return

        await tools.travel(ctx, location)
    
    @commands.command()
    async def main(self, ctx: commands.Context):
        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)
        quests = user_data["quests"]
        gdata = user_data["game"]

        player_xp_level: int = gdata["xp level"]

        # player did not finish these quests - ongoing quests that are incomplete
        fight_in_progress_msg = "**Quests that player has not finished yet**"
        item_in_progress_msg = "**Quests that player has not finished yet**"

        # player completed these quests - probably dont need to show these actually
        # fight_completed_msg = ""
        # item_completed_msg = ""

        # player did not start these quests even though they are unlocked and ready
        fight_not_started_msg = "**Quests available but player did not start**"
        item_not_started_msg = "**Quests available but player did not start**"
        
        # player cannot start these quests because xp level not high enough
        fight_locked_msg = "**Quests unavailable because player level not high enough**"
        item_locked_msg = "**Quests unavailable because player level not high enough**"

        for monster_type in quests["main"]["fight"]: # player has to fight a certain amount of a specific monsters
            quests_for_monster_type: list = quests["main"]["fight"][monster_type]

            for quest in quests_for_monster_type:
                quest: dict # quest data
                progress: int = quest["progress"]
                amount: int = quest["amount"]
                required_xp_level: int = quest["required xp level"]
                quest_name: str = quest["name"]
                required_location = quest["required location"]

                if player_xp_level >= required_xp_level:
                    if progress == 0: # user has not started fighting yet
                        fight_not_started_msg += f"\n`{quest_name}`\nGoal: `{amount}`\nProgress: `{progress}`\nRequired Location to Recieve Reward: `{required_location.title()}`"
                    
                    else:
                        fight_in_progress_msg += f"\n`{quest_name}`\nGoal: `{amount}`\nProgress: `{progress}`\nRequired Location to Recieve Reward: `{required_location.title()}`"
                
                else:
                    fight_locked_msg += f"\n`{quest_name}`\nGoal: `{amount}`\nProgress: `{progress}`\nRequired Location to Recieve Reward: `{required_location.title()}`"
        
        for quest in quests["main"]["item"]: # player has to get a certain amount of a specific items
            quest_name: str = quest["quest name"]
            item_name: str = quest["item"]
            amount: int = quest["amount"]
            progress: int = quest["progress"]
            required_xp_level: int = quest["required xp level"]
            required_location: str = quest["required location"]

            if player_xp_level >= required_xp_level:
                if progress == 0:
                    # player xp high enough but did not start the quest yet
                    item_not_started_msg += f"\n`{quest_name.title()}`: Item: `{item_name}`\n Goal: `{amount}`\nProgress: `{progress}`Required Location to Recieve Reward: `{required_location.title()}`"
                
                else:
                    item_in_progress_msg += f"\n`{quest_name.title()}`: Item: `{item_name}`\n Goal: `{amount}`\nProgress: `{progress}`Required Location to Recieve Reward: `{required_location.title()}`"
            
            else:
                item_locked_msg += f"\n`{quest_name.title()}`: Item: `{item_name}`\n Goal: `{amount}`\nProgress: `{progress}`Required Location to Recieve Reward: `{required_location.title()}`"

        em = discord.Embed(
            title="Main Quests",
            description="Contains all the main quests you have, and those that you have yet to unlock.",
            color=discord.Color.gold()
        )

        em.add_field(
            name="Fight Quests",
            value=fight_in_progress_msg + "\n" + fight_not_started_msg + "\n" + fight_locked_msg
        )

        em.add_field(
            name="Item Quests",
            value=item_in_progress_msg + '\n' + item_not_started_msg + '\n' + item_locked_msg,
            inline=False
        )

        await ctx.send(embed=em)
  
def setup(client):
    client.add_cog(Quests(client))