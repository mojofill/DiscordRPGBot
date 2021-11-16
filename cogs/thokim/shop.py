import discord,random
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Shop(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Shops extension ready. ')

    # remember all commands here should have a default 5% chance of having a scam, with someone taking all their money and they earn nothing back. (5% means 1 out of 20)
    
    # this is the black market
    @commands.command()
    async def purchase(self,ctx,item_id):
        user = ctx.author

        if not item_id.isdigit():
            await ctx.send('Not a valid item id, argument given is not a number.')
            return
        
        # you get unfinished potions. need to find ingredients and finally, brew them at the town hall, depending on the random num, you can get a very bad potion or very good one

        shop = {
            "1":{},
            "2":{},
            "3":{},
            "4":{},
            "5":{},
            "6":{},
        }

        if item_id not in list(shop.keys()):
            await ctx.send(f'Invalid item id - `{item_id}` not found.')
            return
    
    # this is the pub
    @commands.command()
    async def pub(self,ctx):
        if not tools.user_at_required_location(ctx.author,"pub"):
            res = tools.travel(ctx.author,"pub")

            if res == "walking":
                await tools.walkuser(ctx,ctx.author,"pub")

            else:
                await ctx.send(res)

        em = discord.Embed(
            title='Black Market',
            description='Where the bullshit happen...',
            color=discord.Color.dark_green()
            )

        em.add_field(
        name='Half-Brewed Potions',
        value="""
            `[1]` Mining speed: 100
            `[2]` Wagon size: 100
            `[3]` item value: 100
            `[4]` Damage increase: 200
            `[5]` (Incoming) damage reduce: 200
            `[6]` Luck: 80
        """
        )

        await ctx.send(embed=em)
    
    # buy for pub
    @commands.command()
    async def buy(self,ctx:commands.Context,potion_id:str,amount:str="1"):
        """Method (command) here GIVES the user a potion - code deals with GETTING the stats. The stats are not applied yet - to look at applied stats, go to `boosts.py`, where there will be a `consume` command, drinking the potion and getting the effects. If you want to look at code TAKING AWAY THE EFFECT ON STATS, go to `tools.py`, where there will be a loop that subtracts the duration of the potion. When the potion duration is equal to zero, we TAKE AWAY THE POTION EFFECTS ON THE USER.
        
        3 main things with potions:
            1. getting stats (storing values in user's backpack)\n
            2. appling stats (user drinks potion, apply the effects on user)\n
            3. taking away stats/effects (potion's duration is finished, take away the effects on the user's stats.)\n
        
        We are dealing with the first one right now, getting and storing the stats.
        """
        user = ctx.author

        try:
            potion_id = int(potion_id)
        except:
            await ctx.send('Invalid item id argument, please enter an integer.')
            return
        try:
            amount = int(amount)
        except:
            await ctx.send('Invalid amount argument: please pass in an integer.')
            return
        if potion_id not in range(1,21):
            await ctx.send('Item id not found, check `.pub` for more information.')
            return
        
        potion_type_dict = {
            1:"mining speed",
            2:"wagon size",
            3:"item value",
            4:"damage increase",
            5:"damage reduce",
            6:"luck",
            7:"energy efficiency",
            8:"heat resist",
            9:"cold resist"
        }

        potion_type = potion_type_dict[potion_id]

        # plan
        # dict for all the recipes in a potion

        recipes = {
            "mining speed":{
                "goblin horns":15,
                "mogosok fang":20,
                "drasok fang":5,
                "jawsok bone":3
            },
            "wagon size":{
                "baursok tail":20,
                "mogosok fang":20,
                "drasok guts":5,
                "jawsok bone":3
            },
            "item value":{
                "drasok wings":20,
                "basilisk fang":15,
                "jawsok bone":15,
                "chimera lion mane":13,
                "minotaur horn":5,
                "bugosok bone":15
            },
            "damage increase":{
                "drasok wings":10,
                "basilisk fang":10,
                "chimera serpent tail":2,
                "bugosok bone":10,
                "minotaur horn":8
            },
            "damage reduce":{
                "tough ogre skin":20,
                "cyclops eye":15,
                "baursok tail":10
            },
            "energy efficiency":{
                "mogosok fang":10,
                "minotaur horn":5,
                "chimera serpent tail":4,
                "chimera lion mane":5,
                "bugosok bone":7,
                "jawsok horn":6,
                "jawsok fang":8
            }
        }

        # start with a random number between 1 and 100
        # if number above 50 (not equal to 50), then add 1 percent to the total completion of the final potion

        def get_potion_completion():
            final_completion_percent = 50 # has base percentage as 50

            base = 50

            while True:
                number = random.randint(base,100)
                # number is above first number, so add 1 percent to the user's potion_completion
                if number > final_completion_percent:
                    final_completion_percent += 1
                    # 90 is the maximun you can get, so we break
                    if final_completion_percent == 90:
                        break
                    # if code reaches here, then we can add 1 to base
                    base += 1
                else:
                    # this means the user got bad luck, and random number was below the first number. so user's final percentage is given back
                    break
                
            return final_completion_percent
            
        # get the completion of the potion, in percentage (decimals)
        potion_completion = get_potion_completion()/100

        potion_recipe = recipes[potion_type]

        # get all the items in the potion_recipe, add it to the backpack unfinished potions part of the backpack, and update it.
        # make a a `.finish <potion_id>` for the user to finish the potion
        # do all standard checks, check if user's backpack has that potion id. if not, tell that to the user and return
        # if the user does not meet the required amount of one an item, tell the user everything that he or she is missing, and return

        # figure out which item to give the user
        # get the total amount of items you need for the potion_completion
        # divide percent by 100 and multiply by amount
        # then choose random thing and add that to the completion

        total = 0

        for item in potion_recipe:
            total += potion_recipe[item]
        
        items_given,counter = int(potion_completion * total),0

        # when we change (what is possibly a float, potion_completion * total) into an integer, it chops off the end decimals, so number is techinically rounded down

        list_of_items = list(potion_recipe.keys())

        final_contents = {}
        
        while counter <= items_given:
            item = random.choice(list_of_items)
            try:
                if final_contents[item] + 1 > potion_recipe[item]:
                    # this means adding one to the item would result in going above what is needed in the recipe
                    pass

                else:
                    final_contents[item] += 1
                    # this is just to count times we have added an item to the potion recipe
                    counter += 1
            
            # first time user got that item
            except: 
                final_contents[item] = 1
                counter += 1

        potion_stats = tools.get_potion_value_stats(potion_type=potion_type)

        duration = potion_stats["duration"]
        value = potion_stats["value"]
        falcon_value = potion_stats["falcon value"]
        potion_rarity = potion_stats["rarity"]

        em = discord.Embed(
            color=discord.Color.dark_green(),
            title=f"{user}'s Half-Brewed Potion",
            description="Thank you for buying from Thokim Pub! We're sorry we couldn't finish the potion you bought, but if you manage to find the rest of the ingredients needed, bring it back here and use `.finish <potion id>`."
        )

        em.set_footer(text="If you do not enjoy your potion, return it with `.return <potion id>` - but this only works within the first 30 seconds from buying the potion. After 30 seconds the bartender will refuse to accept the return!")

        em.add_field(
            name=f"{potion_type.title()} potion for {user}",
            value="\u200b"
        )

        content_msg = ''

        for item in final_contents:
            content_msg += f"""
                **{item}**: `{final_contents[item]}`
            """

            # this adds in the final value for the embed "Contents" every6 item from the GIVEN potion recipe (not what is needed)
        
        em.add_field(
            name='Potion Information',
            value=
                f"""
                    Value = {value}
                    Rarity = {potion_rarity}
                    Duration = {duration}
                    Type = {potion_type}
                """,
            inline=False
        )

        em.add_field(
            name="Potion Contents",
            value=content_msg,
            inline=False
        )
        
        recipe_msg = ''

        for item in recipes[potion_type]:
            recipe_msg += f"""
                {item}: `{recipes[potion_type][item]}`
            """

            # this adds in the final value for the embed "Potion Recipe" every item from the actual recipe for the potion, not the given, half finished one

        em.add_field(
            name="Potion Recipe",
            value=recipe_msg,
            inline=False
        )

        await ctx.send(embed=em)

        # add potion to unused potion in database
        boosts = db.boosts.find_one({"_id":user.id})

        # get a random number for the potion id
        all_potion_ids = list(boosts["all active potions"].keys())
        new_potion_id = tools.get_rand_id(all_potion_ids)

        boosts["local potions"][potion_type][new_potion_id] = {
            "duration":duration,
            "type":potion_type,
            "value":value,
            "rarity":potion_rarity
        }

        await ctx.send(new_potion_id)

        if falcon_value != None: # potion is feedable to a falcon, so add falcon value to potion
            boosts["local potions"][potion_type][new_potion_id]["falcon value"] = falcon_value

        db.boosts.update_one({"_id":user.id},{"$set":{"local potions":boosts["local potions"]}}) # this adds another potion in the boosts collection's user's document
        db.boosts.update_one({"_id":user.id},{"$inc":{"total potions":1}})
    
    @commands.command(aliases=['bm'])
    async def blackmarket(self,ctx:commands.Context):
        pass
    
    @commands.command(aliases=['exch'])
    async def exchange(self,ctx:commands.Context,item_id:int):
        pass

  
def setup(client):
    client.add_cog(Shop(client))