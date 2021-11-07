# Discord RPG storage for code
This is my place to write out all the ideas I have, and document the ideas that I thought of but had no time to implement.

## Monsters and Attack
Hunting monsters is easy in this game. All a player has to do is type `.hunt`. RPG Bot will then plop the player in a random coordinate on the monster map of the realm he is currently in, and spawn monsters on him. RPG Bot will only tell the player "Hey, found a monster for you to fight!" **Nothing more**. To preview the monster, player has to use `.monster` to look at the monster they are shown. `.monster` tells the player everything they need to know about the monster, from its ranking to the weapon it is using.

### How the code works.
In `setup.py`, RPG Bot sets the `monster` section as
```py
{
    "_id":int,
    "preview monster":dict,
    "engaged monster":dict,
    "total monsters defeated":int,
    "trophies":int
}
```

The command `.monster` takes in data in `preview monster` and forms a `discord.Embed` that contains all the data in there. When the player does `.hunt` and RPG Bot makes a monster and points it towards the player, no matter if the player declines engaging it or not, the data will appear in the dict.

To fight the monster in `preview monster`, player must use `.engage` to engage with the monster and fight it.

**Note**: if the player does not want to engage the monster, he must use `.skip` to skip the monster and continue in the monster loop.