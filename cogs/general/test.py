import discord
from discord.ext import commands
from dev.tools import tools
from dev.db import Database

class Test(commands.Cog):
    def __init__(self,client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Test extension ready. ')
    
    @commands.command()
    async def test(self, ctx: commands.Context):
        dialogue_data = {
            "sentence":"Yo what are you doing here",
            "responses":{
                1:"nothing particular",
                2:"peeing"
            },
            1:{
                "sentence":"no, i think youre up to no good",
                "responses":{
                    1:"no???"
                },
                1:{
                    "sentence":"Ah hah! I see your piss right there, you nasty ass."
                    # no responses, end dialogue
                }
            },
            2:{
                "sentence":"BOI GET YOUR NASTY ASS MF OUT OF MY HOUSE AND PISS SOMEWHERE ELSE",
                # no responses, end dialogue
            }
        }
        
        await tools.dialogue("Your Mom", self.client, ctx, dialogue_data)

def setup(client: commands.Bot):
    client.add_cog(Test(client))