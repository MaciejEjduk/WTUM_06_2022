# this bot goes to places where most halite is trying to avoid colisions

from turtle import position
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

""" <<<Game Begin>>> """
game = hlt.Game()

#pre-processing

directions = [ Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still ]

# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:

    game.update_frame()
    me = game.me
    game_map = game.game_map

    command_queue = []

    position_choices = []

    for ship in me.get_ships():

        move_options = ship.position.get_surrounding_cardinals() + [ship.position]

        move_dict = {}
        halite_dict = {}

        for n, direction in enumerate(directions):
            move_dict[direction] = move_options[n]

        for direction in move_dict:
            move = move_dict[direction]
            halite_amount = game_map[move].halite_amount
            if move_dict[direction] not in position_choices:
                halite_dict[direction] = halite_amount

        if game.turn_number%10 == 0:
            logging.info(move_options)

        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(move_dict[choice])
            command_queue.append(
                ship.move(
                    choice
                ))
        else:
            position_choices.append(move_dict[Direction.Still])
            command_queue.append(ship.stay_still())

    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)