import rg

class Robot:
    def act(self, game):

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

        closest_enemy = mindist(enemy,self.location)

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
            
        return move