import discord
import datetime
from discord.ext import commands
from dev.db import Database
from dev.monster_tools import monster_tools
from dev.tools import tools

class Monsters(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.command()
    async def monster(self, ctx: commands.Context):
        """Tells the user about the specific monster they asked for."""

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        monsters = user_data["monsters"]

        if monsters["preview monster"] == None:
            await ctx.send(f'{user.mention} no monster in sight ❌')
            return
        
        monster_data = monsters["preview monster"]

        # TODO: decide to keep or not keep monster health in the preview - if taken out it would make the game harder
        name: str = monster_data["name"]
        health: int = monster_data["health"]
        equipment_data: dict = monster_data["equipment"]

        # "equipment":{
        #     "name":str,
        #     "durability":int,
        #     "damage":int,
        #     "attack time":int,
        #     "elemental":bool,,
        #     [OPTIONAL] "elemental type":str
        # }
        
        em = discord.Embed(
            title=name.title(),
            description='A short description on the monster you are currently facing.'
        )

        msg = f"""
            TODO: finish this

            **TYPE**: `{name.title()}`
            **HEALTH** ❤️: `{health}`
            **EQUIPMENT** ⚔️🏹: `{equipment_data["name"]}`
        """

        if equipment_data["elemental"]:
            msg += f'\n**ELEMENTAL TYPE**: {equipment_data["elemental type"]}'

        em.add_field(name='\u200b', value=msg)

        await ctx.send(embed=em)
    
    @commands.command()
    async def engage(self, ctx: commands.Context):
        """Starts fight between user and monster."""

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        monsters = user_data["monsters"]

        monsters["engaged monster"] = monsters["preview monster"]
        monsters["preview monster"] = None

        await monster_tools.startMonsterAttackLoop(ctx, user)

    @commands.command(aliases=['att','a','atk'])
    async def attack(self, ctx: commands.Context):
        "Uses whatever weapon player is using and fights the current monster with it"

        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        monsters = user_data["monsters"]

        try:
            bp: dict = user_data["backpack"]

            equiped_weapon: str = bp["weapons"]["equipped weapon"]

            if equiped_weapon == None: # no weapon equipped
                await ctx.reply('No weapon equipped. Use `.equiped <weapon_name>` to equip a wepaon. Use `.weapons` to look at your weapons.')

                return

            monster_data: dict = monsters["engaged monster"]

            monster_data["health"] -= bp["weapons"]["weapons"][equiped_weapon]["damage"]

            bp["weapons"]["weapons"][equiped_weapon]["durability"] -= 1

            em = discord.Embed(
                description=f'Used `{bp["weapons"]["weapons"][equiped_weapon]["name"]}` and dealt **{bp["weapons"]["weapons"][equiped_weapon]["damage"]} DAMAGE** to **{monster_data["name"]}**.',
                color=discord.Color.dark_green(),
                timestamp=datetime.datetime.utcnow()
            )

            if bp["weapons"]["weapons"][equiped_weapon]["durability"] == 0:
                await ctx.send(f'{user.mention} your `{bp["weapons"]["weapons"][equiped_weapon]["name"]}` broke!')
        
        except KeyError: # no engaged monster
            return

        except:
            raise
    
    @commands.command(aliases=['s'])
    async def shoot(self, ctx: commands.Context):
        "Uses whatever bow player is using and fights the current monster with it"

        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        monsters = user_data["monsters"]

        if monsters["engaged monster"] == None: # user currently not fighting a monster, just return
            return

        monster_data: dict = monsters["engaged monster"]
        bp: dict - user_data["backpack"]

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skips the current fight player is challenged to - player did NOT use `.engage` yet, so everything is fine."""

        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)
        monsters: dict = user_data["monsters"]

        if monsters["engaged monster"] != None:
            await ctx.send(f'❌ Already in battle with **{monsters["engaged monster"]["name"].title()}**')

def setup(client: commands.Bot):
    client.add_cog(Monsters(client))