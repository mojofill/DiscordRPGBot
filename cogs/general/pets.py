import discord
import random
from discord.ext import commands
from dev.tools import tools
from dev.db import Database
from discord.ext.commands import Context

class Pets(commands.Cog):
    def __init__(self,client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Hunt extension ready. ')
    
    @commands.command()
    async def pets(self, ctx: commands.Context):
        user: discord.User = ctx.author
        user_data = Database.getStorageData(user)

        pets = user_data["pets"]

    @commands.command(aliases=['htp'])
    async def huntp(self, ctx: commands.Context):
        # random between 1 and 1,000,000
        pets = {
            (1, 100)
        }
        
        number = random.randint(1, 1000000)
        pet = None

        for _range in pets:
            if number in range(_range[0], _range[1]):
                pet = pets[_range]
                break
        
        pet: str

        # base stats for all pets - player can upgrade pets
        # TODO: write out full documentation for pets
        
        # NOTE: attack name is past tense version. The way you use it f'{attack_name} {user.name}'

        # NOTE: when a player Monsterizes a pet, the ALL pet stats are increased by 1.5 EXCEPT for attack time
        
        pet_stats = {
            "wolf":{
                "health":100,
                "damage":5,
                "attack name":"bit",
                "attack time":0.5
            },
            "falcon":{
                "health":100,
                "damage":5,
                "attack name":"flew at",
                "attack time":0.3
            }
        }

def setup(client: commands.Bot):
    client.add_cog(Pets(client))