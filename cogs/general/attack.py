import asyncio
import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.db  import Database
from cogs.thokim.falcon import hunt
from dev.map import Map
from dev.monster_tools import monster_tools

class Attack(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Attack extension loaded. ')
  
    @commands.command()
    async def punch(self,ctx:commands.Context,enemy):
        user = ctx.author

        user_data = Database.getStorageData(user)
        
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
        
        enemy_data = Database.getStorageData(enemy)

        enemy_data["backpack"] -= stolen_money

        await ctx.send(f'Punched {enemy.mention}, dealing {fist_damage} and stealing {stolen_money}.')

        # refence dev.tools for more information on the code below

        msg = tools.all_quest_and_chest_actions(ctx, 'coinflip', user)

        await ctx.send(msg)


    @commands.command(aliases=['select'])
    async def equip(self, ctx:commands.Context, wpn_id: int = None):
        if wpn_id == None:
            await tools.NoArgumentGiven(ctx, ['wpn_id'])
            return
        
        user: discord.User = ctx.author
        
        user_data = Database.Storages[user.id]

        bp = user_data["backpack"]

        i = 1

        wpn_id = int(wpn_id)

        for wpn in bp["weapons"]["weapons"]:
            if i == wpn_id:
                bp["weapons"]["equipped weapon"] = wpn

                await ctx.send(f'You have equipped **{bp["weapons"]["weapons"][wpn]["name"]}**')

                return
        
        # if code reaches here then the bot has not found a weapon with the given name
        await ctx.send(embed=discord.Embed(
            description=f'You do not have a weapon with id `{wpn_id}` - please check your weapons with `.weapons`.'
        ))
    
    @commands.command(aliases=['nwpn'])
    async def rename(self, ctx: commands.Context, prev_wpn_name: str, wpn_name: str):
        """Finds the weapon with name `prev_wpn_name` and sets it's name as `wpn_name`, so long there is not already a weapon with name `wpn_name`."""

        user = ctx.author

        user_data = Database.getStorageData(user)

        bp = user_data["backpack"]

        for wpn_key in bp["weapons"]:
            if bp["weapons"][wpn_key]["name"] == wpn_name:
                await ctx.send(embed=discord.Embed(
                    title='Same Weapon Name Found',
                    description=f'Argument for `<wpn_name>` "{wpn_name}" was found in your backpack - please select another name.'
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

        user_data = Database.getStorageData(ctx.author)
        
        bp = user_data["backpack"]
        
        if wpn_name != bp["selected weapon"]:
            await ctx.send(f'You do not have {wpn_name} equipped right now - the weapon that you have equipped is {bp["selected weapon"]}')
            return
        
        bp["equipped weapon"] = wpn_name

        em = discord.Embed(
            description=f'Unequipped `weapon-type: {bp["weapons"][wpn_name]["type"]}`, `name: {wpn_name}`'
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
                Monsters: 👊
                Falcon: 🐦
                Prey: 🍖
            """)

            em.set_footer(text='This message will time out in 60 seconds.')

            m: discord.Message = await ctx.send(embed=em)

            await m.add_reaction('👊')
            await m.add_reaction('🐦')
            await m.add_reaction('🍖')
            
            emoji = None
                
            def check(reaction: discord.Reaction, _user: discord.User):
                nonlocal emoji
                
                if _user.id == user.id :
                    for emoji_ in ['👊','🐦','🍖']:
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
            
            if emoji == '👊':
                target = 'monster'
            
            elif emoji == '🐦':
                target = 'falcon'
            
            else:
                target = 'prey'
            
            await m.remove_reaction(emoji, user)
        
            await ctx.send(f'{user.mention} You have selected {target}')

        user_data = Database.getStorageData(user)
        monsters = user_data["monsters"]
        
        if target == 'monster':
            """Start monster loop"""

            await ctx.send(f"{user.mention} entering hunting loop...")

            await asyncio.sleep(1)

            x = random.randint(-500, 500) # spawning point of user - x
            y = random.randint(-250, 250) # spawning point of user - y

            spawnCoordX = x
            spawnCoordY = y

            iter_x_add = 1
            iter_y_add = 1
            iter_x_subtract = 1
            iter_y_subtract = 1

            foundUp = False
            foundDown = False
            foundRight = False
            foundLeft = False

            borders_found = 0

            borders = []

            while True: # there can only be 4 borders
                coords = [] # contains COORDINATES
                
                if not foundUp:
                    up = (x, y + iter_y_add)
                    iter_y_add += 1
                    coords.append(up)

                if not foundDown:
                    down = (x, y - iter_y_add)
                    iter_y_subtract += 1
                    coords.append(down)

                if not foundRight:
                    right = (x + iter_x_add, y)
                    iter_x_add += 1
                    coords.append(right)

                if not foundLeft:
                    left = (x - iter_x_add, y)
                    iter_x_subtract += 1
                    coords.append(left)

                bool_to_coord_direction = {
                    up:foundUp,
                    down:foundDown,
                    left:foundLeft,
                    right:foundRight
                }

                def check(m: discord.Message):
                    return m.author.id == user.id

                for coord in coords: # go through each coord and check if one is a border
                    try:
                        block = Map.Thokim[coord]

                        if block[0] == 'b': # each block begins with a b or m, signifying border or monster respectively
                            borders.append(block[2:])

                            # await self.client.wait_for("message",check=check)

                            borders_found += 1

                            bool_to_coord_direction[coord] = True # set the bool for the given coord as True as to not try and find more
                    
                    except KeyError:
                        pass # meaning the coordinate is not in the Thokim Map
                
                if borders_found == 4:
                    break

            environment = None # environment the user spawns in - currently None
            first_border = borders[0] # first border COORDINATE in the coords
            
            for border in borders[1:]: # get the rest of the borders besides to first one to save time
                if border == 'map-border' or border != first_border: # if any of the borders do not match the previous one then that means the user spawned in open space
                    environment = 'open space' # set environment to open space
                    break
            
            if environment == None: # this means that all 4 borders were the same AND no border was a map border
                environment = first_border # set environment to first border because all the borders are the same prev border is just the last one we iterated on and its saved
            
            if environment == 'open space': # grasslands
                await ctx.send(f"{user.mention} Entered hunting loop! You have spawned in the grasslands.")
            
            else:
                await ctx.send(f"{user.mention} Entered hunting loop! You have spawned in the {environment[2:]}")

            # you can either find an alone monster, or a monster camp which basically works like a dungeon

            spawnCoordX = random.randint(-500, 500)
            spawnCoordY = random.randint(-250, 250)

            spawnCoord = (spawnCoordX, spawnCoordY)

            radius = 30

            current_cord = spawnCoord
            
            loop = True

            while loop: # this is for the monster loop
                aloneOrMonsterCamp = random.randint(1, 50)

                if aloneOrMonsterCamp == 50: # RNG decides that the user can fight a whole monster camp!
                    pass
            
                else: # RNG says that the user can only fight a singular monster
                    gdata = user_data["game"]

                    base_monster, monster_rank = monster_tools.getMonsterFromPlayerLevel(gdata["level"])

                    monster_data = await monster_tools.spawnMonster(ctx, user, base_monster, monster_rank)

                    # now we can start accepting user commands

                    monsters["preview monster"] = monster_data

                    loop = False # delete this later
                
            else: # user did not find a monster. i can choose to put something here if i want
                pass
        
            while True: # while loop for ONE of the next coords
                x = random.randint(current_cord[0] - radius, current_cord[0] + radius)
                y = random.randint(current_cord[1] - radius, current_cord[1] + radius)

                a = abs(x - current_cord[0]) + abs(y - current_cord[1])
                b = abs(x - current_cord[0])
                c = abs(y - current_cord[1])

                if abs(x - current_cord[0]) + abs(y - current_cord[1]) <= radius:
                    current_cord = (x, y)
                    loop = False
                    break
        
        elif target == 'prey':
            """Start prey loop"""
    
        else: # hunt with falcon
            await hunt(ctx)

def setup(client: commands.Bot):
    client.add_cog(Attack(client))