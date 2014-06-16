# Simplebot by ramk13
# contibutions from mpeterv
# Open source bot with simple rules
# This was the approximate starting point for littlebot/fastbot
# Feel free to use this as the starting point for a bot
# Please give credit if you do though...

# Moves out of spawn, Flees if in danger,
# Chases dying enemies, Attacks adjacent enemies
# Attacks towards enemies two steps away
# Only moves to safe spots
# No two teammates should move into the same square
# Some teammates may move into stationary teammates

# Uses sets instead of lists for bot data structures
# This makes union/intersection a lot easier (credit to WALL-E for this idea)

# Ways to improve:
#   Instead of using pop() to attack in an arbitrary direction, pick intelligently
#   Instead of just moving to the closest enemy move to the closest weak enemy
#   In some cases it's worth moving into an enemy attack to be aggressive
#       (This really separates good bots from mediocre bots)
#   Try to trap enemy bots in spawn
#   Allow bots in trouble to move first and push other bots
#       (requires all moves to be decided on the first act call)
#   When fleeing look for the safest direction

import rg

turn_number = -1
attack_damage = 10

all_locs = [(x, y) for x in xrange(19) for y in xrange(19)]
# set of all spawn locations
spawn = {loc for loc in all_locs if 'spawn' in rg.loc_types(loc)}
# set of all obstacle locations
obstacle = {loc for loc in all_locs if 'obstacle' in rg.loc_types(loc)}
center = rg.CENTER_POINT


# function to find the locations around a spot
# removes obstacle locations from output
def around((x, y)):
    offsets = ((0, 1), (1, 0), (0, -1), (-1, 0))
    return {(x + dx, y + dy) for dx, dy in offsets}-obstacle


# Function to find the closest bot to a specific location by diagonal distance
# Also used to pick the direction closest to the movement goal
def mindist(bots, loc):
    return min(bots, key=lambda x: rg.dist(x, loc))


class Robot:
    def act(self, game):

        # Used to make the code a little more readable
        robots = game.robots

        # Use turn_number to tell if this is the first robot called this turn
        # If so, then clear the list of taken moves
        # The list of taken moves is used to prevent bots from running into each other
        # Each bot called adds its move to the list and all the subsequent bots
        #   shouldn't use a conflicting move
        # Credit to RageMkI for this method
        global turn_number, taken_moves
        if game.turn != turn_number:
            turn_number = game.turn
            taken_moves = set()

        # If moving save the location we are moving to
        def moving(loc):
            taken_moves.add(loc)
            return ['move', loc]

        # If staying save the location that we are at
        def staying(act, loc=None):
            taken_moves.add(me)
            return [act, loc]

        # Function to find bot with the least health
        def minhp(bots):
            return min(bots, key=lambda x: robots[x].hp)

        # Setup basic sets of robots
        me = self.location
        team = {loc for loc in robots if robots[loc].player_id == self.player_id}
        enemy = set(robots)-team

        adjacent = around(me)
        # adjacent squares with an enemy (enemy is one step away)
        adjacent_enemy = adjacent & enemy
        # adjacent squares with an enemy next to that square
        # excludes square if a teammate is in the square
        # (enemy is two steps away)
        adjacent_enemy2 = {loc for loc in adjacent if around(loc) & enemy} - team
        # set of squares that are safe to move to
        # spawn is bad, and moving into an enemy is bad
        # if an enemy is two steps away it might be attacking towards us
        # excludes teammates to prevent collisions
        safemove = adjacent-adjacent_enemy-adjacent_enemy2-spawn-team-taken_moves
        # semisafemove allows for moves into attacking enemies
        semisafemove = adjacent-adjacent_enemy-spawn-team-taken_moves
        safemove_withspawn = adjacent-adjacent_enemy-adjacent_enemy2-team-taken_moves

        # Move towards the closest enemy unless leaving spawn or fleeing
        # This line is in place in the case there are no enemy bots alive
        if enemy:
            closest_enemy = mindist(enemy, me)
        else:
            closest_enemy = center

        move = []

        if me in spawn:
            if safemove:
                # Try to get out of spawn...
                move = moving(mindist(safemove, center))
            elif semisafemove:
                # ...even if we have to run into an attacked square
                move = moving(mindist(semisafemove, center))
            elif turn_number % 10 == 0:
                # if it's the spawn turn and we can't leave, suicide
                move = staying('suicide')
            elif safemove_withspawn:
                # can't get out where we are, so lets move around to try to get out
                move = moving(mindist(safemove_withspawn, center))
            elif adjacent_enemy:
                # we're stuck, so we might as well attack
                move = staying('attack', minhp(adjacent_enemy))
        elif adjacent_enemy:
            if attack_damage*len(adjacent_enemy) >= self.hp:
                # we're about to die, so flee or suicide if we can't
                if safemove:
                    move = moving(mindist(safemove, center))
                else:
                    # nowhere safe to go, so might as well hit the enemy while dying
                    move = staying('suicide')
            elif len(adjacent_enemy) > 1:
                # there is more than one enemy around us, so let's avoid fighting
                if safemove:
                    move = moving(mindist(safemove, center))
                elif semisafemove:
                    move = moving(mindist(semisafemove, center))

            # No reason to run, so let's attack the weakest neighbor
            # If the enemy would die by collision, let's chase instead
            # This puts pressure on weak bots
            if not move:
                target = minhp(adjacent_enemy)
                if robots[target].hp <= 5:
                    move = moving(target)
                else:
                    move = staying('attack', target)

        elif adjacent_enemy2 and me not in taken_moves:
            # check to see if someone wants to move into this square
            # if not and there's an enemy two steps away, attack towards
            # pop() chooses an arbitrary direction
            move = staying('attack', adjacent_enemy2.pop())

        if not move:
            # There's no one next to us, so lets go find someone to attack
            if safemove:
                move = moving(mindist(safemove, closest_enemy))
            else:
                # Nowhere safe to move, no one nearby, so let's sit tight
                move = staying('guard')

        return move
