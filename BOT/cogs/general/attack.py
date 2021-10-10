import asyncio
import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.api import db
from dev.db  import Database
from cogs.thokim.falcon import hunt
from dev.map import Map

class Attack(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Attack extension loaded. ')
  
    @commands.command()
    async def punch(self,ctx:commands.Context,enemy):
        user = ctx.author

        user_data = tools.getStorageData(user)
        
        user_hp = user_data["health"]

        # punch someone and steal their money

        fist_damage = user_hp["fist damage"]
        fist_steal_range = user_hp["fist steal range"]

        one = fist_steal_range[0]
        two = fist_steal_range[1]

        stolen_money = random.randint(one,two)

        await ctx.send(f"This is what your fist damage is, {fist_damage}")

        await ctx.send(f"This is what your stolen_money is, {stolen_money}")

        # take health from target

        user_data["healthpoints"]["health"] -= fist_damage

        user_data["backpack"]["emeralds"] += stolen_money
        
        enemy_data = tools.getStorageData(enemy)

        enemy_data["backpack"] -= stolen_money

        await ctx.send(f'Punched {enemy.mention}, dealing {fist_damage} and stealing {stolen_money}.')

        # refence dev.tools for more information on the code below

        msg = tools.all_quest_and_chest_actions(ctx,'coinflip',user)

        await ctx.send(msg)


    @commands.command(aliases=['select'])
    async def equip(self,ctx:commands.Context,wpn_name=None):
        if wpn_name == None:
            await ctx.send('No argument for `weapon` - check your backpack with `.bp` to see all your weapons.')
            return

        user = ctx.author
        
        user_data = Database.Storages[user.id]

        bp = user_data["backpack"]

        if bp["equipped weapon"] == wpn_name:
            ctx.message.add_reaction('<:x:883531508198035456>')
            return

        for wpn in bp["weapons"]:
            if bp["weapons"][wpn]["name"] == wpn_name:
                # update in the user's document in backpack collection with equiped weapon as the weapon argument

                user_data["backpack"]["equiped weapon"] = wpn_name
        
                em = discord.Embed(
                    description=f'You have equiped `{wpn_name}`'
                )

                await ctx.send(embed=em)

                return
        
        await ctx.send(embed=discord.Embed(
            description=f'You do not have weapon of name `{wpn_name}`'
        ))
    
    @commands.command(aliases=['nwpn'])
    async def nameweapon(self, ctx: commands.Context, prev_wpn_name: str, wpn_name: str):
        """Finds the weapon with name `prev_wpn_name` and sets it's name as `wpn_name`, so long there is not already a weapon with name `wpn_name`."""

        user = ctx.author

        user_data = tools.getStorageData(user)

        bp = user_data["backpack"]

        for wpn_key in bp["weapons"]:
            if bp["weapons"][wpn_key]["name"] == wpn_name:
                await ctx.send(embed=discord.Embed(
                    title='Same Weapon Name Found',
                    description='Argument for `<wpn_name>` "{wpn_name}" was found in your backpack - please select another name.'
                ))

                return
            
            if bp["weapons"][wpn_key]["name"] == prev_wpn_name:
                bp["weapons"][wpn_key]["name"] = wpn_name

                await ctx.send(embed=discord.Embed(
                    description=f'{user.mention} set the weapon which previously had the name of `{prev_wpn_name}` to `{wpn_name}`'
                ))

                return

        # if code reaches here that means no weapon name with prev_wpn_name was found
        await ctx.send(f'No weapon with name `{prev_wpn_name}` was found - please check your backpack with `.bp` to find your weapon name.')
    
    @commands.command(aliases=['deselect'])
    async def unequip(self, ctx:commands.Context, wpn_name: str = None):
        if wpn_name == None:
            await ctx.send('Invalid unequip command, check your backpack with `.bp` for your weapons.')
            return

        user_data = tools.getStorageData(ctx.author)
        
        bp = user_data["backpack"]
        
        if wpn_name != bp["selected weapon"]:
            await ctx.send(f'You do not have {wpn_name} equiped right now - the weapon that you have equiped is {bp["selected weapon"]}')
            return
        
        bp["equipped weapon"] = wpn_name

        em = discord.Embed(
            description=f'Unequiped `weapon-type: {bp["weapons"][wpn_name]["type"]}`, `name: {wpn_name}`'
        )

        await ctx.send(embed=em)
    
    @commands.command()
    async def hunt(self, ctx: commands.Context, target: str = None) -> None:
        user: discord.User = ctx.author
        
        if target == None:
            em = discord.Embed(
                title='Select Target',
                description='''
                    Tip: If you do not wish to see this message everytime you want to hunt, enter one of the following to hunt for a specific type -\n  
                    `monster`, `m`: (Hunt for monsters)
                    `falcon`, `falc`, `flc`, `f`: (Hunt for prey **with** Falcon)
                    `prey`, `p`: (Hunt for prey)
                '''
            )

            em.add_field(name='React with one of the following to hunt', value="""
                Monsters: ✊
                Falcon: 🐦
                Prey: 🍖
            """)

            em.set_footer(text='This message will time out in 60 seconds.')

            m: discord.Message = await ctx.send(embed=em)

            await m.add_reaction('✊')
            await m.add_reaction('🐦')
            await m.add_reaction('🍖')
            
            emoji = None
                
            def check(reaction: discord.Reaction, _user: discord.User):
                nonlocal emoji
                
                if _user.id == user.id :
                    for emoji_ in ['✊','🐦','🍖']:
                        if reaction.emoji == emoji_:
                            emoji = emoji_

                            return True
                
                return False
            
            try:
                await self.client.wait_for('reaction_add', check=check, timeout=60)
            
            except asyncio.TimeoutError:
                await ctx.send(f'{user.mention} you have timed out.')
                return
            
            target = None
            
            if emoji == '✊':
                target = 'monster'
            
            elif emoji == '🐦':
                target = 'falcon'
            
            else:
                target = 'prey'
            
            await m.remove_reaction(emoji, user)
        
            await ctx.send(f'{user.mention} You have selected {target}')
        
        if target == 'monster':
            """Start monster loop"""

            await ctx.send(f"{user.mention} entering hunting loop...")

            await asyncio.sleep(1)

            x = random.randint(-500, 500) # spawning point of user - x
            y = random.randint(-250, 250) # spawning point of user - y

            iter_x_add = 1
            iter_y_add = 1

            while True:
                coords = []
                
                up = (x, y + iter_y_add)
                down = (x, y - iter_y_add)
                right = (x + iter_x_add, y)
                left = (x - iter_x_add, y)

                coords.extend([up, down, right, left])
                
                borders = []

                number_of_borders = 0

                for coord in coords: # go through each coord and check if one is a border
                    try:
                        block = Map.Thokim[coord]

                        if block[0] == 'b':
                            borders.append(block[2:])

                        number_of_borders += 1
                    
                    except KeyError:
                        pass
                
                if number_of_borders == 4:
                    break

            environment = None # environment the user spawns in - currently None
            prev_border = coords[0] # first border in the coords
            
            for border in borders[1::]: # get the rest of the borders besides to first one to save time
                if border == 'map-border' or border != prev_border: # if any of the borders do not match the previous one then that means the user spawned in open space
                    environment = 'open space' # set environment to open space
                    break
            
            if environment == None: # this means that all 4 borders were the same AND no border was a map border
                environment = prev_border # set environment to prev_border because all the borders are the same prev border is just the last one we iterated on and its saved
            
            if environment == 'open space': # grasslands
                await ctx.send(f"{user.mention} Entered hunting loop! You have spawned in the grasslands.")
            
            else:
                await ctx.send(f"{user.mention} Entered hunting loop! You have spawned in the {environment[2:]}")

            # you can either find an alone monster, or a monster camp which basically works like a dungeon
            async def engageMonster(monster_type: str):
                pass

            spawnCoordX = random.randint(-500, 500)
            spawnCoordY = random.randint(-250, 250)

            spawnCoord = (spawnCoordX, spawnCoordY)

            radius = 30

            current_cord = spawnCoord
            
            while True: # this is for the monster loop
                foundMonster = random.randint(1, 10)

                if foundMonster == 1:
                    aloneOrMonsterCamp = random.randint(1, 50)

                    if aloneOrMonsterCamp == 50: # RNG decides that the user can fight a whole monster camp!
                        pass
                
                    else: # RNG says that the user can only fight a singular monster
                        await tools.spawnMonster(ctx, user)

                    while True: # while loop for ONE of the next coords
                        x = random.randint(current_cord[0] - radius, current_cord[0] + radius)
                        y = random.randint(current_cord[1] - radius, current_cord[1] + radius)
                    
                        if abs(x - current_cord[0]) + abs(y - current_cord[1]) <= radius:
                            current_cord = (x, y)
                            break
                    
                else: # user did not find a monster. i can choose to put something here if i want
                    pass
        
        elif target == 'prey':
            """Start prey loop"""
    
        else: # hunt with falcon
            await hunt(ctx)

def setup(client: commands.Bot):
    client.add_cog(Attack(client))