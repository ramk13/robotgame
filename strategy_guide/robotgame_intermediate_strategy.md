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

```python
        # Function to find bot with the least health
        def minhp(bots):
            return min(bots, key=lambda x: robots[x].hp)
```

* Suicide if we have no better options

Right now we try to run away if we're going to die, but sometimes we won't run away successfully and we'll run into an enemy attack. If there's nowhere safe to move and we're going to die by staying still, we could suicide instead and possibly hit the enemy harder than just attacking.

* Run away from uneven matchups

When fighting one on one no one has an advantage because the enemy can attack you for every attack you make when you are adjacent. If an enemy outnumbers you by having two robots next to a single robot of yours, your robot will get hit twice for every hit you dish out. That's bad for you so, we should avoid those situations by moving away if we are outnumbered. As an aside this concept is critical to success in Robotgame even at the highest level. Fighting asymmetrically is important to success in almost any form of combat.

* Chase weak robots

If we know that weak robots are going to run, then instead of attacking them while they scurry away, we can chase them. This puts pressure on them to move again next turn and eventually you may be able to force them into a bad position.



If you are ready for advanced concepts check out the advanced strategy guide (coming soon...)