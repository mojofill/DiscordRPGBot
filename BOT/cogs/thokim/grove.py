import discord
from discord.ext import commands
from dev.tools import tools
from dev.api import db

class Grove(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Grove extension ready. ')
    
    def cog_check(self,ctx):
        user = ctx.author
        gdata = db.game.find_one({"_id":user.id})
        if gdata["status"] == 'frozen' or gdata["status"] == 'stunned' or gdata["status"] != 'stationary':
            return False
        return True

    @commands.command()
    async def enchant(self,ctx,scroll_id,item):
        user = ctx.author
        bp = db.backpack.find_one({"_id":user.id})

        if not item.isdigit():
            await ctx.send('Invalid scroll id argument - please pass in an integer. ')
            return
        
        if scroll_id not in bp["scrolls"].keys():
            await ctx.send('Scroll id not found.')
            return

        scroll_to_item = {
        "efficiency":["pickaxe"],
        "durability":["chestplate","sword","club"]
        }

        scroll_type = bp["scrolls"][scroll_id]["type"]

        if item not in scroll_to_item[scroll_type]:
            await ctx.send(f'Cannot enchant {scroll_type} with {item}')

        scroll_type = bp["scrolls"][scroll_id]["type"]
        value = bp["scrolls"][scroll_id]["value"]
        
        if scroll_type == 'efficiency':
            mines = db.backpack.find_one({"_id":user.id})

            mines["mining speed"] *= 1 + bp["scrolls"][scroll_id]["value"]

            for item in mines["wagon items"]:
                mines["wagon items"][item]["drops"] *= 1 + value
            
            db.mines.replace_one({"_id":user.id},mines)
        
        elif scroll_type == 'durability':
            weapons = [
                'sword',
                'spear',
                'crossbow',
                'ax',
                'axe',
                'club'
            ]

            armor = [
                'chestplate',
                'helmet',
                'boots',
                'leggings'
            ]

            if item in weapons:
                try:
                    health = bp["weapons"][item]["health"]
                except KeyError:
                    await ctx.send(f'You do not have {item}.')
                return
                
                if item == 'axe':
                    item = 'ax'

                db.backpack.update_one({"_id":user},{"$inc":{f"weapons.{item}.health":value * health}})

            elif item in armor:
                try:
                    health = bp["armor"][item]
                except KeyError:
                    await ctx.send(f'You do not have {item}.')
                    return
                
                health = bp["armor"][item]["health"]

                db.backpack.update_one({"_id":user.id},{"$inc":{f"armor.{item}.health":value * health}})
            
            else:
                await ctx.send(f'{item} cannot be enchanted with durability.')
                return

        elif scroll_type == 'sharpness':
            try:
                damage = bp["weapons"][item]["damage"]
            except KeyError:
                await ctx.send(f'You do not have {item} as a weapon.')
                return

        db.backpack.update_one({"_id":user.id},{"$inc":{f"weapons.{item}.damage":damage*value}})

        await ctx.send(f'Successfully enchanted {item} with {bp["scrolls"][scroll_id]["name"]}')
  
def setup(client):
  client.add_cog(Grove(client))