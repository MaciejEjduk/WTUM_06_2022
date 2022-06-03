from re import S
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

ship_states = {}

ship_standstill_time = {}

# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Panicing")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:

    game.update_frame()
    me = game.me
    game_map = game.game_map

    command_queue = []

    position_choices = []

    for ship in me.get_ships():

        if ship.id not in ship_states:
            ship_states[ship.id] = "collecting"

        if ship.id not in ship_standstill_time:
            ship_standstill_time[ship.id] = 0

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

        logging.info(ship_standstill_time)

        if ship_states[ship.id] == "panic":
            command_queue.append(ship.move(random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])))
            ship_standstill_time[ship.id] -= 1
            if ship_standstill_time[ship.id] == 0:
                ship_states[ship.id] = "collecting"

        elif ship_states[ship.id] == "depositing":
            choice = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(move_dict[choice])
            command_queue.append(ship.move(choice))
            if ship.position == me.shipyard.position:
                ship_states[ship.id] = "collecting"

        elif ship_states[ship.id] == "collecting":
            choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(move_dict[choice])
            choice = game_map.naive_navigate(ship, move_dict[choice])
            command_queue.append(ship.move(choice))
            if choice == Direction.Still:
                ship_standstill_time[ship.id] += 1
            else:
                ship_standstill_time[ship.id] = 0
            if ship_standstill_time[ship.id] >= 7:
                ship_states[ship.id] = "panic"
            elif ship.halite_amount > constants.MAX_HALITE / 1.5:
                ship_states[ship.id] = "depositing"

    if game.turn_number <= 300 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)