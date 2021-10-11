from discord import User
from dev.api import db
from threading import Thread

storage_capacity_limit = 100 # only 200 data sets are allowed in each storage. This can be changed

amount_of_storages = 0

gdata = db.game.find({})

storages = {}

for user_data in gdata:
    user_id = user_data["_id"]

    user_stored_data = {
        "game":user_data
    }

    def set_dict():
        def get_hp():
            user_stored_data["healthpoints"] = db.healthpoints.find_one({"_id":user_id})

        def get_falcon():
            user_stored_data["falcon"] = db.falcon.find_one({"_id":user_id})
        
        def get_backpack():
            user_stored_data["backpack"] = db.backpack.find_one({"_id":user_id})

        def get_monsters():
            monsters_dict = db.monsters.find_one({"_id":user_id})

            monsters_dict["engaged monsters"] = {} # set the active monsters to none

            user_stored_data["monsters"] = monsters_dict
        
        def get_pets():
            user_stored_data["pets"] = db.pets.find_one({"_id":user_id})
        
        def get_boosts():
            user_stored_data["boosts"] = db.boosts.find_one({"_id":user_id})

        def get_chests():
            user_stored_data["chests"] = db.chests.find_one({"_id":user_id})
        
        def get_quests():
            user_stored_data["quests"] = db.quests.find_one({"_id":user_id})
        
        def get_duration():
            user_stored_data["duration"] = db.duration.find_one({"_id":user_id})
        
        def get_falcon_duration():
            user_stored_data["falcon duration"] = db.falcon_duration.find_one({"_id":user_id})
        
        def get_coliseum():
            user_stored_data["coliseum"] = db.coliseum.find_one({"_id":user_id})
        
        def get_vault():
            user_stored_data["vault"] = db.vault.find_one({"_id":user_id})
        
        def get_special_commands():
            user_stored_data["special commands"] = db.special_commands.find_one({"_id":user_id})
        
        hp_thread = Thread(target=get_hp)
        falcon_thread = Thread(target=get_falcon)
        backpack_thread = Thread(target=get_backpack)
        monsters_thread = Thread(target=get_monsters)
        pets_thread = Thread(target=get_pets)
        boosts_thread = Thread(target=get_boosts)
        chests_thread = Thread(target=get_chests)
        quests_thread = Thread(target=get_quests)
        duration_thread = Thread(target=get_duration)
        falcon_duration_thread = Thread(target=get_falcon_duration)
        coliseum_thread = Thread(target=get_coliseum)
        vault_thread = Thread(target=get_vault)
        special_commands_thread = Thread(target=get_special_commands)

        hp_thread.start()
        falcon_thread.start()
        backpack_thread.start()
        monsters_thread.start()
        pets_thread.start()
        boosts_thread.start()
        chests_thread.start()
        quests_thread.start()
        duration_thread.start()
        falcon_duration_thread.start()
        coliseum_thread.start()
        vault_thread.start()
        special_commands_thread.start()

    set_dict()

    storages[user_id] = user_stored_data

class ArenaObject:
    def __init__(self):
        self.MatchmakingServer = {
            # this will have nested dictionaries. The keys will the be the game id (str), and the value of the game id will be a dict, which will have all the neccessary data to make a basic game. Specific games will need specific data, but this will set the bare minimum.

            # example:

            # "1xewq207hy":{
            #     "players":{
            #         680546360717606941:"henryzhang"
            #     }
            #     "start time":None, # in seconds
            #     "stop time":None, # in seconds. these two keys are here to find the time elapsed
            # }
        }

        self.InGameServer = {}
    
    def startGame(self, game_id: str): # FINISH THIS
        """Starts the game with id of `game_id`"""
        
        game_data = self.MatchmakingServer[game_id]
        
        del self.MatchmakingServer[game_id]

        self.InGameServer[game_id] = {}

class _Coliseum(ArenaObject):
    def __init__(self):
        ArenaObject.__init__(self)

class _FalconArena(ArenaObject):
    def __init__(self):
        ArenaObject.__init__(self)

class _FalconRace(ArenaObject):
    def __init__(self):
        ArenaObject.__init__(self)

class _Database:
    def __init__(self):
        self.Storages = storages
        self.Weather: dict = db.climate.find_one({"_id":"weather"})

        self.DesertWeather = {
            "temperature":90
        }

        self.UpperMountainWeather = {
            "temperature":15
        }

        self.Coliseum = _Coliseum()
        self.FalconArena = _FalconArena()
        self.FalconRace = _FalconRace()
    
    def getStorageData(self, user) -> dict:
        """Returns the pointer to the value in the dict `Database.Storages` with key `user.id`"""
        user_storage = Database.Storages[user.id]

        return user_storage

    def addUser(self, user: User, data: dict):
        """Adds a user to the database"""
        self.Storages[user.id] = data
    
Database = _Database()