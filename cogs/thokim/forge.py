import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Forge(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Forge extension ready. ')

    # do the make better weapons here
    # also better tools

    @commands.command(aliases=['up'])
    async def upgrade(self,ctx,aspect=None,amount=1):
        mines = db.mines
        bp = db.backpack

        user = ctx.author
        
        gdata = db.game.find_one({"_id":user.id})

        wrong_location = False
        wrong_realm_and_location = False

        if gdata["location"] != 'midtown':
            wrong_location = True
            if gdata["realm"] != "thokim":
                wrong_realm_and_location = True
        
        if wrong_location:
            await ctx.send(tools.wrong_location_msg("Midtown"))
            return
        if wrong_realm_and_location:
            await ctx.send(tools.wrong_location_msg("Midtown","Thokim"))
            return
        
        m_info = mines.find_one({"_id":user.id})
        bp_info = bp.find_one({"_id":user.id})

        valid_upgrade_args = ["pickaxe","p","wagon","w"]

        if aspect == None:
            await ctx.send('Here are some commands you can use with `.upgrade`.\n`.upgrade mining` - upgrade how many items you mine per second. `upgrade wagon` - ')
            return
        
        aspect = aspect.lower()

        if aspect not in valid_upgrade_args:
            await ctx.send(f'{user.mention} you can only upgrade pickaxe or wagon, not {aspect}. If you wished to reforge your item with another item, do `.reforge <item> with <item2>. `')
            return

        if aspect == 'pickaxe' or aspect == 'p':
            aspect = 'pickaxe'
        
        else:
            aspect = 'wagon'
        
        final_amount = 0

        for i in range(amount):
            upgrade_price = m_info[f"upgrade {aspect}"]["price"]
            final_amount += upgrade_price

        add_to = m_info[f"upgrade {aspect}"]["add to"]

        new_upgrade_price = upgrade_price + add_to

        m_info[f"upgrade {aspect}"]["price"] = new_upgrade_price
        m_info[f"upgrade {aspect}"]["add to"] += 2

        if final_amount > bp_info["gold bars"]:
            await ctx.send('You do not have enough gold to upgrade that much.')
            return

        mines.update_one({"_id":user.id},{"$set":{f"upgrade {aspect}":m_info[f"upgrade {aspect}"]}})

        mines.update_one({"_id":user.id},{"$set":{"add to":m_info[f"upgrade {aspect}"]["add to"]}})

        bp.update_one({"_id":user.id},{"$inc":{"gold bars":-1*final_amount}})
        
        check_m_info = mines.find_one({"_id":user.id})

        upgrade_price = check_m_info[f"upgrade {aspect}"]["price"]

        await ctx.send(f'This is your new upgrade price, {upgrade_price}')

        # consult dev.tools
        tools.all_quest_and_chest_actions(ctx,"upgrade",user)

    @commands.command()
    async def forge(self,ctx,tool,scroll_id):
        user = ctx.author

        # gotta finish this, make a "recipe" for weapons, what metal you need, and other stuff to make good weapons

def setup(client):
    client.add_cog(Forge(client))