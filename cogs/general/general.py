import discord
import datetime
import asyncio
import sys
import os
from discord.ext import commands
from dev.db import Database
from dev.tools import tools
from dev.api import db
from threading import Thread

class General(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('General (about bot) extension ready. ')
    
    # making the help command phelp because i still want to the default help command, because it lists all the commands and when i want to test all the commands i can use the default help command
    @commands.command()
    async def phelp(self,ctx,aspect=None):
        # right here check if the aspect is part of the acceptable aspects
        user = ctx.author

        em = discord.Embed(title='',color=discord.Color.dark_green(),timestamp=datetime.datetime.utcnow())

        em.set_footer(text=f'Requested by {user}',icon_url=user.avatar_url)

        em.set_author(name=f'{self.client.user}',icon_url=self.client.user.avatar_url)

        if aspect == None:
            em.add_field(name='Commands',value="""
                For a list of all game commands, enter `.commands`. If you wish to have a deatiled look on one specific commands, enter `.help <command name>`

            """)

            em.add_field(name="Mechanics",value="""
                To see more about each command, enter `.botdev <command name>` to see how we made that command, statistics, probability and much, much more.

            """,inline=False)

            em.add_field(name="Trade Hub",value="""
                Join the club at Trade Hub (hey that rhymes) and chill with users across the world! Click on the link below.
                
                https://discord.gg/qJCZPw6NuH
                
                Have a nice time!
            
            """,inline=False)

            em.add_field(name="About the Developer",value="""
                This bot was designed by a programmer (duh). I am always learning new things and listening for new ideas. If you want to support "us" and join "our (tentative)" team (the team consists of one person - me <:pepelaugh:845728830785847303>), click on the link below:

                put a google form here and do stuff

                Answer a few questions and we'll be right with you!
            """)

            await ctx.send(embed=em)
        
    
    @commands.command()
    async def save(self, ctx: commands.Context):
        """Saves your current data in the database"""

        msg: discord.Message = await ctx.send('Updating your account...')
        
        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)
        
        def update_game_thread():
            user_data["game"]["status"] = 'stationary'
            
            db.game.replace_one({"_id":user.id}, user_data["game"])
        
        def update_backpack_thread():
            db.backpack.replace_one({"_id":user.id}, user_data["backpack"])
        
        def update_boosts_thread():
            db.boosts.replace_one({"_id":user.id}, user_data["boosts"])
        
        def update_chests_thread():
            db.chests.replace_one({"_id":user.id}, user_data["chests"])
        
        def update_coliseum_thread():
            db.coliseum.replace_one({"_id":user.id}, user_data["coliseum"])
        
        def update_duration_thread():
            db.duration.replace_one({"_id":user.id}, user_data["duration"])
        
        def update_duration_thread():
            db.falcon.replace_one({"_id":user.id}, user_data["falcon"])
        
        def update_falcon_duration_thread():
            db.falcon_duration.replace_one({"_id":user.id}, user_data["falcon duration"])
        
        def update_healthpoints_thread():
            db.healthpoints.replace_one({"_id":user.id}, user_data["healthpoints"])
        
        def update_pets_thread():
            db.pets.replace_one({"_id":user.id}, user_data["pets"])
        
        def update_special_commands_thread():
            db.special_commands.replace_one({"_id":user.id}, user_data["special commands"])
        
        def update_vault_thread():
            db.vault.replace_one({"_id":user.id}, user_data["vault"])
        
        thread1 = Thread(target=update_game_thread)
        thread2 = Thread(target=update_backpack_thread)
        thread3 = Thread(target=update_boosts_thread)
        thread4 = Thread(target=update_chests_thread)
        thread5 = Thread(target=update_coliseum_thread)
        thread6 = Thread(target=update_duration_thread)
        thread7 = Thread(target=update_duration_thread)
        thread8 = Thread(target=update_falcon_duration_thread)
        thread9 = Thread(target=update_healthpoints_thread)
        thread10 = Thread(target=update_pets_thread)
        thread11 = Thread(target=update_special_commands_thread)
        thread12 = Thread(target=update_vault_thread)

        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()
        thread5.start()
        thread6.start()
        thread7.start()
        thread8.start()
        thread9.start()
        thread10.start()
        thread11.start()
        thread12.start()

        await msg.edit(content=f'{user.mention} Successfully updated your profile!')

    @commands.command(name='commands')
    async def command(self,ctx):
        user = ctx.author
        em = discord.Embed(color=discord.Color.dark_green(),timestamp=datetime.datetime.utcnow(),title="Commands")
        
        em.set_author(name=self.client.user,icon_url=self.client.user.avatar_url)
        em.set_footer(text=f'Requested by {user}',icon_url=user.avatar_url)

        em.add_field(name="Mineshaft",value="""
        `sell`, `wagon`, `profile`
        """)

        em.add_field(name="Trading",value="""
        `forgegold`, `buy`
        remember that you have to go to trade hub for upgrades
        """,inline=False)

        em.add_field(name='Falcon',value="`hunt`, `feed`",inline=False)

        em.add_field(name='Desert',value="`engage`, `disengage`",inline=False)
        
        em.add_field(name="Grove",value="`enchant`, `disenchant`",inline=False)

        em.add_field(name="Finance",value="`deposit`, `withdraw`",inline=False)

        em.add_field(name='Shipments',value="`hourly`, `daily`, `weekly`",inline=False)

        em.add_field(name="Downtown",value="`coinflip` you gotta add more here",inline=False)

        em.add_field(name="Chests",value="`open`",inline=False)

        em.add_field(name="Blacksmith",value="`upgrade`",inline=False)

        # replace the knight with a better word 
        em.add_field(name="Knight",value="`knighthood`",inline=False)

        em.add_field(name="\u200b",value="`.help <command name>` for more information on the command, and `.botdev <command name>` for a detailed explanation and statistics on that command.",inline=False)

        await ctx.send(embed=em)

    @commands.command()
    async def profile(self, ctx: commands.Context, user:discord.User=None):
        if user == None:
            user = ctx.author

        user_data = Database.getStorageData(user)

        gdata = user_data["game"]
        bp = user_data["backpack"]
        coliseum = user_data["coliseum"]
        pets = user_data["pets"]
        boosts = user_data["boosts"]

        """
        Important bot aspects:
            Pets 
            Pet shards
            Barn
            Farm
            Healthpoints
            Potion boosts/multipliers (also from pets)
            Pickaxe/wagon
            Weapons
            Falcon
            Currency
            Coliseum victories
            Rank
            Badge/what kind of user you are (if you are patron you get special badge else you get something else that says you are ordinary player)

        """
        
        em = discord.Embed()

        em.set_thumbnail(url=user.avatar_url)

        em.set_author(name=user,icon_url=user.avatar_url)
        em.timestamp = datetime.datetime.utcnow()

        em.set_footer(text=self.client.user,icon_url=self.client.user.avatar_url)

        em.add_field(name="Game",value=f"""
        Level: **{gdata["level"]}**
        XP: **{gdata["experience"]}**
        Status: **{gdata["status"].title()}**
        Location: **{gdata["location"].title()}**
        """)

        em.add_field(name="Currency",value=f"""
        Gold bars: **{bp["gold bars"]}**
        """)

        total_pets = 0
        pets_copy = pets.copy()

        del pets_copy["_id"],pets_copy["shards"]

        for pet_type in pets_copy:
            total_pets += len(pets_copy[pet_type])

        em.add_field(name="Pets",value=f"""
        Information on {user.name}'s pets.
        Total pets: {total_pets}
        Pet shards: {pets["shards"]}
        """,inline=False)

        active_potion_boosts = ''
        
        for potion in boosts["all active potions"]:
            active_potion_boosts += f"""
            `[{potion}]`: {boosts["all active potions"][potion]["type"].title()}
            **Duration**: {boosts["all active potions"][potion]["duration"]}\n
            """
        
        if active_potion_boosts == '':
            active_potion_boosts = f'No active potions. Use `.consume` to use potion.'

        em.add_field(name="Coliseum",value=f"""
        Victories: **{coliseum["victories"]}**
        Entered championships: **{coliseum["entered championships"]}**
        Trophies: 
        **{coliseum["trophies"]["gold trophies"]}** gold trophies.
        **{coliseum["trophies"]["silver trophies"]}** silver trophies.
        **{coliseum["trophies"]["bronze trophies"]}** bronze trophies.
        """)

        em.add_field(name="\u200b",value="For more information, visit `.help` or `.commands`",inline=False)

        await ctx.send(embed=em)

    @commands.command(aliases=['bp'])
    async def backpack(self, ctx:commands.Context, user:discord.User = None):
        if user == None:
            user = ctx.author
        
        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        # remember the implement the method that rafael suggested, 
        em = discord.Embed(color=discord.Color.dark_green(),title="Backpack")
        em.set_author(name=user,icon_url=user.avatar_url)

        em.add_field(name="Currency",value=f"""
        Gold bars: {bp["gold bars"]} <:goldbar:847942259026558986>
        Gold nuggets: {bp["gold nuggets"]} <:nuggets:847953467053047838>
        """)
        
        em.add_field(name="Weapons",value="Information on all of your weapons.",inline=False)

        msg = ''

        for weapon in bp["weapons"]["weapons"]:
            msg += f"""
                **TYPE**: `{weapon.title()}`
                **DURABILITY**: `{bp["weapons"]["weapons"][weapon]["durability"]}`
            """
        
        if msg == '':
            msg = 'No weapons in `backpack`.'
        
        msg += f'\n**SELECTED WEAPON**: `{bp["weapons"]["equipped weapon"]}`'

        em.add_field(name='\u200b',value=msg)

        await ctx.send(embed=em)

    @commands.command(aliases=['g'])
    async def grab(self, ctx: commands.Context):
        """Grabs ALL items in the player's backpack."""

        user: discord.User = ctx.author

        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        if len(bp["grabbable items"]["weapons"]) + len(bp["grabbable items"]["loot"]) + len(bp["grabbable items"]["food"]) == 0:
            await ctx.reply('Nothing to grab.', mention_author=False)

            return
        
        await tools.addEquipments(ctx, bp["grabbable items"]["weapons"])
        await tools.addLoot(ctx, bp["grabbable items"]["loot"])
        await tools.addRawFood(ctx, bp["grabbable items"]["food"])
        await tools.addValuables(ctx, bp["grabbable items"]["valuables"])

        bp["grabbable items"] = {"weapons":{}, "loot":{}, "food":{}}
        
    @commands.command(aliases=['c'])
    async def cook(self, ctx: commands.Context):
        """Cooks food for the player"""
    
    @commands.command()
    async def add(self, ctx: commands.Context, *item):
        """Adds items to the cooking pot if the player is near a cooking pot."""

    @commands.command()
    async def eat(self, ctx: commands.Context, *items):
        pass

    @commands.command()
    async def eatmeal(self, ctx: commands.Context, meal):
        await ctx.send()
    
    @commands.command()
    async def weapons(self, ctx: commands.Context):
        """Sends a message on the player's current weapons"""

        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        weapons_str = [f'**{user}** Here are your weapons. Use `.equip <number>` to equip the given weapon at index `number`.\n']

        index = 1

        for wpn in bp["weapons"]["weapons"]:
            weapons_str.append(f'**{index}**: `{wpn}`. **DURABILITY**: {bp["weapons"]["weapons"][wpn]["durability"]}, **DAMAGE**: `{bp["weapons"]["weapons"][wpn]["damage"]}`')

            index += 1
        
        weapons_str = '\n'.join(weapons_str)

        # TODO maybe change to discord.Embed, not str

        await ctx.send(weapons_str)

    @commands.command(aliases=['bot'])
    async def about(self,ctx):
        em = discord.Embed(title='About DOLLARS',color=discord.Color.dark_green())
        em.set_author(name=self.client.user,icon_url = self.client.user.avatar_url)
        em.set_thumbnail(url=self.client.user.avatar_url)
        em.add_field(name='Version',value='1.0.0\n',inline=False)
        em.add_field(name='Date registered: ',value='1/24/2021')
        em.add_field(name='Date released: ',value='To Be Decided.')

        em.add_field(name='Developer',value='bazingun#4610',inline=False)
        em.add_field(name='Active users: 1',value='\u200b',inline=False)
        em.add_field(name='Gameplay',value='For more information on game play, do `.guide`.',inline = False)
        
        em.set_footer(text=f'Requested by {ctx.author}',icon_url=ctx.author.avatar_url)

        await ctx.send(embed=em)

    @commands.command(aliases=['quit'])
    async def stop(self, ctx: commands.Context):
        """TODO: DELETE THIS WHEN PUBLISHING THE BOT"""
        await ctx.reply('Stopping bot...')

        os.system('cls')
        sys.exit()

    @commands.command()
    async def travelby(self,ctx,mode):  
        user = ctx.author

        if mode not in ['walking','running','flying']:
            await ctx.send('Invalid mode, please choose between `walking`, `running`, or `flying`.')
            return

        db.game.update_one({"_id":user.id},{"$set":{"default transport":mode}})

        await ctx.send(f'{user.mention} Changed your default transport to {mode}.')
    
    @commands.command()
    async def walk(self,ctx,location):
        locations_to_realm = {
            "thokim":['mineshaft','home','jungle','mountain','']
        }

        realm = None

        for Realm in locations_to_realm:
            if location in locations_to_realm[Realm]:
                realm = Realm
                break
        
        if realm == None:
            await ctx.send('Invalid location argument. Check `.locations` to see all the locations in each realm.')
            return

        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
                
        if gdata["realm"] != realm:
            await ctx.send(f'You are not in {realm} yet, which is where {location} is. Check `.locations` to see all the locations in each realm.')
            return
        
        if gdata["location"] not in locations_to_realm[realm]:
            await ctx.send("{location} is not in {realm}. Check `.locations` to see all the locations in each realm.")
            return
        
        await ctx.send(f"Starting to walk to {location}..")
        
        await asyncio.sleep(gdata["walk time"])

        db.game.update_one({"_id":user.id},{"$set":{"location":location}})

        await ctx.send(f'{user.mention} you arrived at {location} by walking.')
  
def setup(client):
  client.add_cog(General(client))