#Robotgame basic strategy
by ramk13

##Individual Strategies:

So let's expand on examplebot, the move to center with attack bot. Here's a list of ideas:

Staying in spawn is bad. So let's check if we are in spawn, and if we are let's leave. We should leave even if there's someone to attack, because we don't want to get stuck/trapped in there.

* Idea 1 - Leave spawn

examplebot attacks until it dies. Since the score is only the number of bots you have and not their health, it's worth more to stay alive than to do 10 more damage to a bot. So how about we see if we are about to die, and if so we run for our lives instead of dying in vain.

* Idea 2 - Flee if we're going to die

If you watch any decent robots, you'll immediately notice that if you move into a space that someone else is attacking, you get hit. For that reason, if there's a chance someone might move into a spot next to us, we should attack towards them. That prevents anyone from getting next to us without taking a hit.

* Idea 3 - Attack towards enemies two steps away

examplebot moves towards the center, but there are several cases where it makes sense to do something else. It's more important to move where its safe so that we don't put ourselves in danger with no benefit. So what's not safe? Spawn, moving into an enemy, moving next to an enemy. We know we can't move into obstacles. Also, we can cut down on collisions if we don't move into teammates. Later we can find situations where it's worth moving somewhere that isn't explicitly safe, but for now let's stick with this.

* Idea 4 - Only move to safe spots

If we have a bunch of safe options, why move to center? We know staying in spawn is bad, but that doesn't make the center good. A better idea is moving towards (but not into) the enemy. This combined with attacking towards enemies will give us more territory that we occupy or have the potential to attack to. 

* Idea 5 - Move towards the enemy if there isn't one nearby

## Combining the ideas

Let's put these ideas together into pseudocode. We can put all the decision logic for our bot in a single if/else statement.

```
if we're in spawn:
    move somewhere safe (i.e. out of spawn)
else if there's an enemy next to us (1 step away):
    if we are low on health:
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

To implement this in code, we need some data structure with our game info and a few functions. Note: There are a lot of ways to do the same thing in python. This is not optimal in any way, just a functional example. 

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
team = {loc for loc in robots if robots[loc].player_id == self.player_id}
enemy = set(robots)-team
```

### Using the data structures to create useful sets/functions

For moving/attacking, there are only four possibilities for directions and the function rg.locs_around can give us those. We can exclude obstacle locations, since we'll never move or attack to those.

```python
adjacent = rg.locs_around(self.location) - obstacle
adjacent_enemy = adjacent & enemy
```

To figure where there are enemies two steps away, let's look at adjacent squares with an enemy next to that square. We'll exclude an adjacent square if a teammate is in the square. This cuts down on collisions.

```python
adjacent_enemy2 = {loc for loc in adjacent_enemy if around(loc) & enemy} - team
```

Then we need to check whether each of those is safe:

```python
safe = adjacent - adjacent_enemy - adjacent_enemy2 - spawn - team
```

We need a function that gives us the location from a set that is closest to what we specify. We can use this function find the closest enemy, but also to choose between our list of safe moves. We can pick the safe move that's closest to where we want to go.

```python
def mindist(bots, loc):
    return min(bots, key=lambda x: rg.dist(x, loc))
```
    
## Putting it all together
    
Let's put all this together in code (Note: this doesn't constitute a whole working bot):

```python
all_locs = {(x, y) for x in xrange(19) for y in xrange(19)}
spawn = {loc for loc in all_locs if 'spawn' in rg.loc_types(loc)}
obstacle = {loc for loc in all_locs if 'obstacle' in rg.loc_types(loc)}
team = {loc for loc in robots if robots[loc].player_id == self.player_id}
enemy = set(robots)-team

adjacent = rg.locs_around(self.location) - obstacle
adjacent_enemy = adjacent & enemy
adjacent_enemy2 = {loc for loc in adjacent_enemy if around(loc) & enemy} - team
safe = adjacent - adjacent_enemy - adjacent_enemy2 - spawn - team

def mindist(bots, loc):
    return min(bots, key=lambda x: rg.dist(x, loc))
    
closest_enemy = mindist(enemy,self.location)

# we'll overwrite this if there's something better to do
move = ['guard']

if self.location in spawn:
    if safe:
        move = mindist(safe, rg.CENTER_POINT)
elif adjacent_enemy:
    if attack_damage*len(adjacent_enemy) >= self.hp:
        if safe:
            move = mindist(safe, rg.CENTER_POINT)
        else:
            move = ['attack', adj_en.pop()]
elif adjacent_enemy2:
    move = ['attack', adjacent_enemy2.pop()]
elif safe:
    move = mindist(safe, closest_enemy)
```

    

    
            




