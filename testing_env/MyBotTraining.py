# Python 3.6
import secrets
import hlt  #main halite stuff
from hlt import constants  # halite constants
from hlt.positionals import Direction, Position  # helper for moving
import random  # randomly picking a choice for now.
import logging
import time

import numpy as np

direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

game = hlt.Game()  # game object
# Initializes the game
game.ready("LearningBot")

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me

    game_map = game.game_map  # game map data. Recall game is

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
            
        choice = secrets.choice(range(len(direction_order)))

        command_queue.append(ship.move(direction_order[choice]))

    if len(me.get_ships()) < 1:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)