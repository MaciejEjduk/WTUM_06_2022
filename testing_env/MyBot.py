# Python 3.6
import secrets
import hlt  #main halite stuff
from hlt import constants  # halite constants
from hlt.positionals import Direction, Position  # helper for moving
import random  # randomly picking a choice for now.
import logging
import time

import numpy as np

map_settings = {32:400,
                40:425,
                48:450,
                56:475,
                64:500,}

TOTAL_TURNS = 50
SAVE_THRESHOLD = 4100
MAX_SHIPS = 1

direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

training_data = []

game = hlt.Game()  # game object
# Initializes the game
game.ready("LearningBot")

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me

    '''comes from game, game comes from before the loop, hlt.Game points to networking, which is where you will
    find the actual Game class (hlt/networking.py). From here, GameMap is imported from hlt/game_map.py.

    open that file to seee all the things we do with game map.'''
    game_map = game.game_map  # game map data. Recall game is

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    surroundings = []

    # specify the order we know this all to be

    dropoff_positions = [d.position for d in list(me.get_dropoffs()) + [me.shipyard]]
    ship_positions = [d.position for d in list(me.get_ships())]


    for ship in me.get_ships():
        
        size = 16

        for y in range(-1*size, size+1):
            row = []
            for x in range(-1*size, size+1):
                current_cell = game_map[ship.position + Position(x, y)]

                if current_cell.position in dropoff_positions:
                    drop_friend_foe = 1
                else:
                    drop_friend_foe = -1

                if current_cell.position in ship_positions:
                    ship_friend_foe = 1
                else:
                    ship_friend_foe = -1

                halite_in_cell = round(current_cell.halite_amount / constants.MAX_HALITE, 2)

                ship_in_cell = current_cell.ship

                dropoff_in_cell = current_cell.structure

                if halite_in_cell is None:
                    halite_in_cell = 0
                if ship_in_cell is None:
                    ship_in_cell = 0
                else:
                    ship_in_cell = round(ship_friend_foe * (ship_in_cell.halite_amount / constants.MAX_HALITE), 2)
                if dropoff_in_cell is None:
                    dropoff_in_cell = 0
                else:
                    dropoff_in_cell = drop_friend_foe

                amounts = (halite_in_cell, ship_in_cell, dropoff_in_cell)

                row.append(amounts)
            surroundings.append(row)
            
        choice = secrets.choice(range(len(direction_order)))

        training_data.append([surroundings,choice])

        command_queue.append(ship.move(direction_order[choice]))

    # ship costs 1000, dont make a ship on a ship or they both sink
    if len(me.get_ships()) < MAX_SHIPS:
        if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    if game.turn_number == TOTAL_TURNS:
        if me.halite_amount >= SAVE_THRESHOLD:
            timed = int(time.time()*1000)
            hal = me.halite_amount
            np.save(f"training_data/{hal}-{timed}.npy", training_data)

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)