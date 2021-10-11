from dev.db import Database
import discord,datetime,random,threading
from discord.ext import commands,tasks
from dev.tools import tools
from dev.api import db

class Weather(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Weather extension ready. ')
        self.change_season.start()
        self.check_weather_duration.start()
    
    @tasks.loop(minutes=5)
    async def check_weather_duration(self):
        weather = Database.Weather

        if weather["duration"] == 0:
            self.change_weather()
        
        else:
            weather["duration"] -= 5
    
    def change_weather(self):
        """This method is an umbrella command which deals with all the information being changed when anything related with the weather is trying to be changed"""
        weather = Database.Weather

        # this will change the weather and temperature outside every hour

        """
        All types of weathers:
            1. Heat wave
            2. Hail
            3. Snowy
            4. Sunny
            5. Cold
            6. Hot
            7. Chilly
            8. Stormy (thunderstorms, icestorms, wind storms, hurricanes and tornadoes)
            9. Cloudy
            10. Windy
        """

        # i just need the base weather down here, then i can choose the extremes or normal after random number decides on the base weather

        """
        Base weathers:
        1. Sunny
        2. Cloudy
        3. Windy
        4. Rainy
        5. Stormy
        """

        def get_seasonal_base_weather(season):
            """Gets the `base_weather` of the given season by parameter `seasons`"""
            seasonal_base_weathers = {
                "spring":{
                    (0,35):"cloudy",
                    (35,50):"windy",
                    (50,65):"sunny",
                    (65,85):"rainy",
                    (85,100):"stormy"
                },
                "summer":{
                    (0,50):"sunny",
                    (50,80):"stormy",
                    (80,90):"rainy",
                    (90,95):"cloudy",
                    (95,100):"windy"
                },
                "autumn":{
                    (0,35):"windy",
                    (35,55):"cloudy",
                    (55,75):"sunny",
                    (75,90):"rainy",
                    (90,100):"stormy"
                },
                "winter":{
                    (0,45):"snowy",
                    (45,65):"cloudy",
                    (65,75):"rainy",
                    (75,90):"windy",
                    (90,100):"stormy"
                }
            }

            # random number for which base weather to get, based on which weather it it
            base_weather_number = random.randint(1,100)

            base_weather = None

            for base_weather_range in seasonal_base_weathers[season]:
                if base_weather_number in range(base_weather_range[0],base_weather_range[1]):
                    base_weather = seasonal_base_weathers[season][base_weather_range]
                    break
                
            return base_weather

        # calculated in fahrenheit
        # all temperatures given down below is based on my experience in philly
        def get_seasonal_temperature_from_weather(season, base_weather) -> int:
            """Returns an integer representing the temperature in the game - shown in Fahrenheit"""
            seasonal_temperature_to_weather = {
                "spring":{ # below is all spring
                    "sunny":{
                        # on sunny days its 30% warm, 60% chilly, 10% cold (below 32 degrees fahrenheit)
                        # at least how "warm" and "chilly" feels in philly
                        # i think warm would be
                        (0,30):[55,69],
                        (30,90):[40,54],
                        (90,100):[18,39]
                    },
                    "cloudy":{
                        # on cloudy days during the spring, it would be 15% pretty warm, 65% chilly, 20% very cold
                        (0,15):[55,63],
                        (15,80):[40,54],
                        (80,100):[18,39]
                    },
                    "rainy":{
                        # on rainy days it cant be below 32 fahrenheit, because thats when 
                        # it would be 10% warm, 90% chilly
                        (0,10):[55,63],
                        (10,100):[40,54]
                    },
                    "windy":{
                        # on windy days it would be 60% chilly, 25% warm and 15% cold
                        (0,60):[40.54],
                        (60,85):[55,63],
                        (85,100):[19,39]
                    },
                    "stormy":{
                        # on stormy days (thunderstorms), it will be 100% chilly
                        (0,100):[37,55]
                    }
                },
                "summer":{
                    "sunny":{
                        # during sunny days in the summer, it would be 
                        (0,85):[80,90], # normal hot temperature in the summer
                        (85,95):[91,100], # this is really hot, do not go out in this weather
                        (95,99):[71,79], # this lucky, everyone got a cool temperature
                        (99,100):[105,134]
                    },
                    "cloudy":{
                        (0,75):[70,85], # pretty hot
                        (75,100):[65,69]
                    },
                    "rainy":{
                        (1,70):[65,76],
                        (70,100):[77,87]
                    },
                    "windy":{
                        (1,70):[80,90],
                        (70,100):[71,79]
                    },
                    "stormy":{
                        (1,90):[71,85],
                        (90,100):[86,90]
                    }
                },
                "autumn":{
                    "sunny":{
                        (1,80):[55,69],
                        (80,100):[70,77]
                    },
                    "cloudy":{
                        (1,90):[55,69],
                        (90,100):[70,77]
                    },
                    "rainy":{
                        (1,90):[52,67],
                        (90,100):[68,70]
                    },
                    "windy":{
                        (1,95):[54,69],
                        (95,100):[70,73]
                    },
                    "stormy":{
                        (1,100):[51,62]
                    }
                },
                "winter":{
                    "sunny":{
                        (1,90):[40,46],
                        (90,100):[34,39]
                    },
                    "cloudy":{
                        (1,95):[31,40],
                        (95,100):[41,46]
                    },
                    "rainy":{
                        (1,90):[29,39],
                        (90,100):[40,46]
                    },
                    "windy":{
                        (1,90):[30,39],
                        (90,100):[40,46]
                    },
                    "stormy":{
                        (1,90):[28,37],
                        (90,100):[38,46]
                    }
                }
            }

            temp_ranges = seasonal_temperature_to_weather[season][base_weather]
            number = random.randint(1,99)

            temperature = None
            
            for temp_range in temp_ranges:
                if number in range(temp_range[0], temp_range[1]):
                    temperature = random.randint(temp_ranges[temp_range][0], temp_ranges[temp_range][1])
                    return temperature

        def get_base_weather_duration(base_weather,season) -> int:
            """Get the duration from the base weather - returns an integer representing the duration."""
            # calculated in minutes, later on divide by 5 because every 5 minutes script will subtract 1 from the duration and weather will then chance

            # the duration will not be realistic because gotta keep the game SCPIY AND FUN AND DIFFERENT. cant have it raining for 12 hours
            from_season_base_weather_duration = {
                "spring":{
                    "sunny":[30,60],
                    "rainy":[30,50],
                    "cloudy":[30,60],
                    "windy":{20,50},
                    "stormy":[30,70] # gotta make it extra painful for my users lmao
                },
                "summer":{
                    "sunny":[60,120],
                    "rainy":[90,180],
                    "cloudy":[30,90],
                    "windy":[40,90],
                    "stormy":[100,200]
                },
                "autumn":{
                    "sunny":[60,100],
                    "rainy":[60,100],
                    "cloudy":[90,180],
                    "windy":[90,125],
                    "stormy":[40,70]
                },
                "winter":{
                    "sunny":[30,60],
                    "rainy":[30,80],
                    "cloudy":[80,200],
                    "windy":[100,200],
                    "stormy":[100,200]
                }
            }

            duration_range = from_season_base_weather_duration[season][base_weather]
            
            duration = random.randint(duration_range[0],duration_range[1])

            return duration

            # now get the specific type of weather from base weather
            # the temperature (can) change 

        def get_specific_weather_from_base_weather(base_weather,season) -> str:
            """Returns a string representing the new weather gotten from the base weather"""
            """Returns a"""
            specific_weather_from_base_weather = {
                "sunny":{
                    "spring":{
                        (1,100):"sunny" # may seem redundant, but sunny just means a normal sunny weather
                    },
                    "summer":{
                        (1,90):"sunny",
                        (90,100):"heat wave" # heat waves can cause droughts, which make cooling off harder
                    },
                    "autumn":{
                        (1,100):"sunny"
                    },
                    "winter":{
                        (1,100):"sunny"
                    }
                },
                "cloudy":{ # i can change this later on if i want to 
                    "spring":{
                        (1,50):"slightly cloudy",
                        (50,70):"very cloudy",
                        (70,100):"normal"
                    },
                    "summer":{
                        (1,60):"normal",
                        (60,95):"slightly cloudy",
                        (95,100):"very cloudy"
                    },
                    "autumn":{
                        (1,55):"very cloudy",
                        (55,85):"normal",
                        (85,100):"slightly cloudy"
                    },
                    "winter":{
                        (1,70):"very cloudy",
                        (70,95):"normal",
                        (95,100):"very cloudy"
                    }
                },
                "rainy":{
                    "spring":{
                        (1,50):"light rain", # also called a slight drizzle
                        (50,80):"moderate rain",
                        (80,95):" heavy rain",
                        (95,100):"violent rain" # really dangerous, somethings might drop from the sky like trees, flooding will occur, watch out in this kind of weather
                    },
                    "summer":{
                        (1,30):"light rain",
                        (30,70):"moderate rain",
                        (70,85):"heavy rain",
                        (85,100):"violent rain"
                    },
                    "autumn":{
                        (1,65):"light rain",
                        (65,85):"moderate rain",
                        (85,95):"heavy rain",
                        (95,100):"violent rain"
                    },
                    "winter":{
                        (1,25):"light rain",
                        (25,55):"moderate rain",
                        (55,85):"heavy rain",
                        (85,100):"violent rain"
                    }
                },
                "windy":{
                    "spring":{
                        (1,85):"mild wind",
                        (85,100):"moderate wind"
                    },
                    "summer":{
                        (1,80):"mild wind",
                        (80,95):"moderate wind",
                        (95,100):"heavy wind"
                    },
                    "autumn":{
                        (1,70):"mild wind",
                        (70,90):"moderate wind",
                        (90,100):"heavy wind"
                    },
                    "winter":{
                        (1,65):"mild wind",
                        (65,85):"moderate wind",
                        (80,95):"heavy wind",
                        (95,100):"violent wind"
                    }
                },
                "stormy":{
                    "spring":{
                        (1,60):"moderate thunderstorm",
                        (60,85):"heavy thunderstorm",
                        (85,95):"violent thunderstorm",
                        (95,100):"tornado"
                    },
                    "summer":{
                        (1,58):"moderate thunderstorm",
                        (58,83):"heavy thunderstorm",
                        (83,93):"violent thunderstorm",
                        (93,98):"tornado",
                        (98,100):"hurricane"
                    },
                    "autumn":{
                        (1,60):"moderate thunderstorm",
                        (60,85):"heavy thunderstorm",
                        (85,95):"violent thunderstorm",
                        (95,100):"hurricane"
                    },
                    "winter":{ # check below if the temperature is below 32. if it is then the storms will be automatically changed into something new
                        (1,35):"moderate thunderstorm",
                        (35,70):"heavy thunderstorm",
                        (70,100):"violent thunderstorm"
                    }
                }
            }

            weather_ranges = list(specific_weather_from_base_weather[base_weather][season].keys())

            number = random.randint(1,100)

            specific_weather = None
            
            for weather_range in weather_ranges:
                if number in range(weather_range[0],weather_range[1]):
                    specific_weather = specific_weather_from_base_weather[base_weather][season][weather_range]
                    break
                
            return specific_weather

        # then i figure out the actual weather, according to the temperature i got and the specific weather. for Weather, if i got a cold temperature (below 32 degrees fahrenheit), then i have ice rain

        # i only need to change the water related weather tpyes because the temperature that day might affect the weather
        season = db.climate.find_one({"_id":"season"})["season"]

        base_weather = get_seasonal_base_weather(season)
        specific_weather = get_specific_weather_from_base_weather(base_weather, season)
        temperature = get_seasonal_temperature_from_weather(season, base_weather)
        base_weather_duration = get_base_weather_duration(base_weather, season)

        # i need to find these few things about the weather
        """
            1. Base weather
            2. Specific weather
            3. Duration
            4. Risks
            5. Temperature
        """
        
        # base weathers are 
        
        #  1. Sunny
        #  2. Cloudy
        #  3. Windy
        #  4. Rainy
        #  5. Stormy
        
        # now we feed the base weather to the specifc_weather_from_base_weather to get that specific weather, including but not all

        # this gets the seasons currently in the bot game

        # now its time to see if the specific weather will have to be changed because of the temperature

        # this means its raining, but its also below the freezing point of water, so it cant be raining. we can choose freezing rain or snow 
        def subzero_change_weather(base_weather):
            # below is a dictionary for changing normal weather to something else due to subzero weather
            # key = the specific weather getting changed
            # value = what it will be changed into
            subzero = {
                "rainy":{
                    "light rain":"freezing rain",
                    "moderate rain":"sleet",
                    "heavy rain":"small hail",
                    "violent rain":"hail"
                },
                "stormy":{
                    # im not going to add a "light thunderstorm" key in here because winter has 0 chance of getting those
                    "moderate thunderstorm":"snowstorm", # add function below to change to blizzard if luck is good
                    "heavy thunderstorm":"hailstorm",
                    "violent thunderstorm":"icestorm"
                }
            }

            nonlocal specific_weather

            specific_weather = subzero[base_weather][specific_weather]
            
            # the specific weather is only changed when its subzero

        # the name might be misleading, the snowstorm only changes 1 out of 6 times into a blizzard
        def change_snowstorm():
            nonlocal specific_weather
            if specific_weather == 'snowstorm':
                number = random.randint(1,5)

                if number == 1:
                    specific_weather = "blizzard"
            
        if specific_weather == 'snowstorm':
            specific_weather = change_snowstorm()
        
        # this changes the *specific weather* (if needed), because freezing temperatures (abviously) freeze the water, therefore changing the weather entirely
        if temperature <= 32:
            subzero_change_weather(base_weather)

            # now that we have the specific weather, we update the weather and temperature
            # you need really warm clothes to go outside
            # gotta use temperature to some use, like BOTW

            db.climate.update_one({"_id":"weather"},{"$set":{"weather":specific_weather}})

            db.climate.update_one({"_id":"temperature"},{"$set":{"temperature":temperature}})

            # when he user gets hit by a passive damage, only when the user's health passes a milestone will it be notified

        # yes, i have to make temperature check and the level of danger outside, and if i should advise the user to stay inside if you do not have efficient armor to block any damage coming your way
        def give_caution_if_needed(specific_weather):
            # on the recurring damage wetaher types, you can change those around
            dangerous_weather = {
                # heat waves are dangerous, too hot to move a lot outside
                "heat wave":{ # it makes you move slower
                    "can transform":True,
                    "transformation":{
                        (0,1):"drought", # 1 out of 6 heat waves cause a drought
                    },
                    "sample size":6,
                    "risk type":["temperature"], # this means what is causing the danger levels to go high
                    "damage tpye":"recurring damage",
                    "recurring damage":5, # this is what is damaging the user
                    "wait":5 # every 5 seconds, 
                },
                "drought":{
                    "can transform":False,
                    "risk type":["temperature"],
                    "damage type":"recurring damage",
                    "recurring damage":15, # deals 5 HP to the user every 5 seconds
                    "wait":5
                },
                "blizzard":{
                    "can transform":False,
                    "risk type":["temperature"],
                    "damage":3,
                    "wait":5
                },
                "thunderstorm":{
                    "can transform":True,
                    "transformation":{
                        (0,1):"flood" # 1 out of 50 thunderstorms cause a complete flood for 10 minutes, making the user unable to travel anywhere on foot, can only rely on falcon for flying and the train. if the user tries to go anywhere during a flood, game will warn user to not outisde ONCE, and if the user keeps trying to then INSTANT DEATH. Just like a hurricane, except there will be no possibility of losing your equiped weapon
                    },
                    "risk type":["chance"],
                    # thunderstorms should be more likely to hit a person in the jungle and desert
                    "chance":{
                        (1,100):"lightning strike"
                    }, # there are no choices in here, check the extra nested dictionary
                    "sample size":100,
                    "damage":10000, # a lightning strike should strike a person dead - damage is 100 times the default total hp user has
                    "extra":{
                        "lightning strike locations":{
                            # depending on user's location lightning striking the user chance will differ
                            "jungle":{
                                "hit range":[0,1],
                                "sample size":15
                            },
                            "desert":{
                                "hit range":[0,1],
                                "sample size":20
                            },
                            "other":{
                                "hit range":[0,1],
                                "sample size":60
                            }
                        }
                    }
                },
                "icestorm":{
                    "can transform":False,
                    "risk type":["chance","temperature"],
                    "recurring damage":20,
                    "chance":{
                        (0,1):"complete freeze" # 1 out of 20 freeze attacks causes user to be completely frozen, killing the user because he or she will never be able to move again. ominous...
                    },
                    "sample size":20,
                    "wait":5
                },
                "tornado":{
                    "can transform":False,
                    "risk type":["direct cause"], # this means it is a direct cause of being in the middle of a tornado
                    "extra":{
                        "recurring damage":50, # important note tornadoes will drop things on you. make it funny, make a big list that contains dumb things to drop on a persons head, like a UFO or the moon
                        "wait":3,
                        "damage type":"recurring damage"
                    }
                },
                "heavy rain":{
                    "can transform":True,
                    "risk type":["safe"],
                    "transformation":{
                        (0,10):"flood", # check thunderstorm flood comment above
                    },
                    "sample size":75 # 1 in 75 HEAVY rains becomes a flood
                },
                "violent rain":{ # i just copy and pasted ebcaue its easier than doing a if statement and making changed down below
                    "can transform":True,
                    "risk type":["safe"],
                    "transformation":{
                        (0,1):"flood", # check thunderstorm flood comment above
                    }, # violent rains do not deal any damage to the user
                    "sample size":30 # 1 in 30 VIOLENT rains becomes a flood
                },
                "hurricane":{
                    "can transform":False,
                    "risk type":["direct cause"],
                    # as soon as you fall into the hurricane youre dead, drowned
                    "extra":{
                        "lose weapon range":[0,1],
                        "number range":[1,10] # 1 out of 10 people that are washed away will also lose their equiped weapon when they respawn
                    }
                },
                "flood":{
                    "can transform":False,
                    "risk type":['direct cause'],
                    "damage type":"instant death"
                }
            }
            try:
                weather_danger_info = dangerous_weather[specific_weather]
            except KeyError: # this means that since it couldnt find the weather in the dictionary, that weather is not dangerous, so we can return
                return

            if weather_danger_info["can transform"]:
                number = random.randint(1,weather_danger_info["sample size"])

                for number_range in weather_danger_info["transformation"]:
                    if number in range(number_range[0],number_range[1]):
                        result = weather_danger_info["transformation"][number_range]
                        # recursion because the result is still in the function
                        give_caution_if_needed(result)
            
            # if code reaches here that means recursion has not happened, meaning the weather has not changed

            # now we give all the SIMPLE (defualt, not UNIQUE) information in the weather dict

            for risk_type in weather_danger_info["risk type"]:
                if risk_type == 'chance':
                    weather["risks"] = {
                        "sample size":weather_danger_info["sample size"],
                        "choices":weather["chance"], # inside chance dictionary theres all the possible outcomes, with key as tuple for number range, and value as string for representation of weather attack. I will only go this far in the choices, carrying out the attacks and deciding how to do it from the string representation will be done in tools.deal_weather_damage()
                    }
                
                elif risk_type == 'direct cause': # direct cause is just a better sounding name for "there is not one risk type group for this weather, figure this out yourself in tools.deal_weather_damage()". just put the "extra" nested dict in the database and call it a day
                    weather["risks"] = {
                        "extra":weather_danger_info["extra"]
                    }
                
                elif risk_type == 'temperature':
                    weather["risks"] = {
                        "damage":weather_danger_info["damage"],
                        "wait":weather_danger_info["wait"]
                    }

            try: # if there are more that i should put in the dict, there will be a nested dictionary called "extra"
                weather["risks"]["extra"] = weather_danger_info["extra"]
            except KeyError: # this means that there was not an extra key, so i have nothing to add on the weather dict
                pass
        
        give_caution_if_needed(specific_weather)

        weather["duration"] = base_weather_duration
        weather["temperature"] = temperature
        weather["base weather"] = base_weather
        weather["specific weather"] = specific_weather

    @tasks.loop(hours=24)
    async def change_season(self):
        today = datetime.date.today()

        month = today.strftime('%M')
        day = today.strftime('%D')

        important_season_change_dates = {
            "3/1":"spring",
            "6/20":"summer",
            "9/22":"autumn",
            "12/21":"winter"
        }

        season_change_dates = list(important_season_change_dates.keys())

        all_seasons = []
        
        for key in season_change_dates:
            all_seasons.append(important_season_change_dates[key])

        for season_change_date in season_change_dates:
            today = f'{month}/{day}'
            if season_change_date == today:
                season_to_change = important_season_change_dates[season_change_date]

                index = all_seasons.index(season_to_change)

                try:
                    next_season = all_seasons[index+1]
                
                except IndexError:
                    next_season = all_seasons[0] # go back to beginning

                db.climate.update_one({"_id":"season"},{"$set":{"season":next_season}})
                Database.Weather["season"] = next_season
                break
  
def setup(client):
  client.add_cog(Weather(client))