#Robotgame basic strategy
by ramk13

##Intermediate concepts

In the previous guide we took the example bot which originally had these features:

* Stay put if at the center point
* Attack an enemy if its adjacent to us
* Move towards the center

And changed/added the following features:

* Leave spawn
* Flee if we're going to die
* Attack towards enemies two steps away
* Only move to safe spots which are unoccupied
* Move towards the enemy if there isn't one within two steps

## More features/ideas

* Keep track of spots that are taken by our previous moves

Our current bots can try to move into the same spot and also attack ourselves. We don't lose HP from self-attacking but there will (almost) always be a better choice of move. If we keep track of all of our previous moves on a given turn we can avoid these conflicts

* Instead of attacking a random bot from the bots next to us, we should attack the weakest one

Any successful attack reduces the enemy's total HP in the same way, but the game is scored by total bots alive, not by bot HP. For that reason it's more important to kill a weak bot that it is to attack/weaken a strong one.

* Suicide if we have no better options

Right now we try to run away if we're going to die, but sometimes we won't run away successfully and we'll run into an enemy attack. If there's nowhere safe to move and we're going to die by staying still, we could suicide instead and possibly hit the enemy harder than just attacking.

* Run away from uneven matchups

When fighting one on one no one has an advantage because the enemy can attack you for every attack you make when you are adjacent. If an enemy outnumbers you by having two robots next to a single robot of yours, your robot will get hit twice for every hit you dish out. That's bad for you so, we should avoid those situations by moving away if we are outnumbered. As an aside this concept is critical to success in Robotgame even at the highest level. Fighting asymmetrically is important to success in almost any form of combat.

* Chase weak robots

If we know that weak robots are going to run, then instead of attacking them while they scurry away, we can chase them. This puts pressure on them to move again next turn and eventually you may be able to force them into a bad position.



Let's put these ideas together into pseudocode. We can put all the decision logic for our bot in a single if/else statement.

```
if we're in spawn:
    move somewhere safe (i.e. out of spawn)
else if there's an enemy next to us (1 step away):
    if we are in danger of dying:
        move somewhere safe
    else:
        attack an enemy
else if there's an enemy two steps away:
    attack towards an enemy
else if there's somewhere safe to move: (there's no one near us)
    move somewhere safe, but towards the closest enemy
else:
    guard, since there's nowhere to move or attack
```
    
## Implementing it in code

To implement this in code, we need some data structures with our game info and a few functions. Note: There are a lot of ways to do the same thing in python. This is not optimal in any way, just a functional example. 

### Using sets instead of lists

To make things easier, we can use python sets instead of lists with the set() function or set comprehensions to start. This allows us to use the following set operators (more info here: https://docs.python.org/2/library/sets.html ):

* | or union - gives you a set with all elements in both sets
* - or difference - gives you a set with the second sets elements removed from the first
* & or intersection - gives you a set that only has elements that are in both sets

Let's start by saying that we have lists of the following: teammates, enemies, spawn locations 'spawn', obstacle locations 'obstacle'

### Base data structures

```python
all_locs = {(x, y) for x in xrange(19) for y in xrange(19)}
spawn = {loc for loc in all_locs if 'spawn' in rg.loc_types(loc)}
obstacle = {loc for loc in all_locs if 'obstacle' in rg.loc_types(loc)}
team = {loc for loc in game.robots if game.robots[loc].player_id == self.player_id}
enemy = set(game.robots)-team
```

You can see here how we made a set of the enemy robots by taking all the robots and substracting out our team.

### Using the data structures to create useful sets/functions

For moving/attacking, there are only four possibilities for directions and the function rg.locs_around can give us those. We can exclude obstacle locations, since we'll never move or attack to those. `adjacent & enemy` gives us the the adjacent squares that also are in the set of enemies.

```python
adjacent = set(rg.locs_around(self.location)) - obstacle
adjacent_enemy = adjacent & enemy
```

To figure out where there are enemies two steps away, let's look at adjacent squares with an enemy next to that square. We'll exclude an adjacent square if a teammate is in the square.

```python
adjacent_enemy2 = {loc for loc in adjacent if (set(rg.locs_around(loc)) & enemy)} - team
team
```

Then we need to check whether each of those is safe. We'll remove options where there's an enemy one or two steps away. We'll also exclude spawn so that we don't go back into it. Also, to cut down on collisions we can exclude moving into teammates. When we get more complex we can remove the team restriction, but we'll need to add another check in its place. For now this is best.

```python
safe = adjacent - adjacent_enemy - adjacent_enemy2 - spawn - team
```

We need a function that gives us the location from a set that is closest to what we specify. We can use this function find the closest enemy, but also to choose between our list of safe moves. We can pick the safe move that's closest to where we want to go.

```python
def mindist(bots, loc):
    return min(bots, key=lambda x: rg.dist(x, loc))
```

We can use the `pop()` method of a set to get an arbitrary element of that set. We can use that to pick an enemy to attack. Also to tell whether we are in danger of dying or not, we can multiply the number of enemies adjacent to us by the average damage of an attack (9 hit points) and see if we have more health than that. Because of the way we wrote our minimum distance function, we need to be sure that we always put a set with objects in it. For that reason, we need to make sure that `enemy` isn't empty or we'll get an error from `mindist`.
    
## Putting it all together
    
Let's put all this together in code (Note: this doesn't constitute a whole working bot):

```python
all_locs = {(x, y) for x in xrange(19) for y in xrange(19)}
spawn = {loc for loc in all_locs if 'spawn' in rg.loc_types(loc)}
obstacle = {loc for loc in all_locs if 'obstacle' in rg.loc_types(loc)}
team = {loc for loc in game.robots if game.robots[loc].player_id == self.player_id}
enemy = set(game.robots)-team

adjacent = set(rg.locs_around(self.location)) - obstacle
adjacent_enemy = adjacent & enemy
adjacent_enemy2 = {loc for loc in adjacent if (set(rg.locs_around(loc)) & enemy)} - team
safe = adjacent - adjacent_enemy - adjacent_enemy2 - spawn - team

def mindist(bots, loc):
    return min(bots, key=lambda x: rg.dist(x, loc))

if enemy:
    closest_enemy = mindist(enemy,self.location)
else
    closest_enemy = rg.CENTER_POINT

# we'll overwrite this if there's something better to do
move = ['guard']

if self.location in spawn:
    if safe:
        move = ['move', mindist(safe, rg.CENTER_POINT)]
elif adjacent_enemy:
    if 9*len(adjacent_enemy) >= self.hp:
        if safe:
            move = ['move', mindist(safe, rg.CENTER_POINT)]
    else:
        move = ['attack', adjacent_enemy.pop()]
elif adjacent_enemy2:
    move = ['attack', adjacent_enemy2.pop()]
elif safe:
    move = ['move', mindist(safe, closest_enemy)]
```

If you'd like to see this as a working bot, you just need to add the class and function definition at the top and have the `act` function return `move`

Here's the [intermediate strategy bot as a file](https://github.com/ramk13/robotgame/blob/master/strategy_guide/strategy-intermediate.py).

If you are ready for advanced concepts check out the advanced strategy guide.