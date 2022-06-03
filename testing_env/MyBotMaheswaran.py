#Bot utworzony na podstawie rozwiązania Maheswarana Mootiringode'a. Opiera się na czyszczeniu mapy z halite'u w otoczeniu bazy. 
#Bot ogranicza ilość tworzonych statków. Na koniec gry wszystkie statki starają się rozbić w bazie, w celu odzyskania części surowców

from re import S
from turtle import position
import hlt
from hlt import constants
from hlt.positionals import Direction, Position
import random
import logging
import queue
import time
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

ship_status = {}
ship_still_count = {}
ship_targets = {}
ship_stuck_turn = {}
ship_previous = {}

all_next_positions = []

shipyard_spots = queue.PriorityQueue()
check_pos = []
my_max_ships = 10

my_halite_check = 10
spot_iters_stop = 3

# custom functions

training_data = []
direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

def check_ship_max(game, game_map, me):
    my_max_ships_new = my_max_ships

    for player in game.players:
        otherplayer = game.players[player]

        if len(otherplayer.get_ships()) >= my_max_ships_new + 2:
            my_max_ships_new = len(otherplayer.get_ships())

    return my_max_ships_new


def refresh_spots(game_map, me):
    width = game_map.width
    height = game_map.height

    count = 0
    for i in range(width):
        for j in range(height):
            pos = Position(i, j)

            shipyard_distance = game_map.calculate_distance(
                pos, me.shipyard.position)
            pos_halite = game_map[pos].halite_amount

            if pos_halite > my_halite_check:
                shipyard_spots.put(
                    (shipyard_distance, -pos_halite, count, pos))
            count += 1


def cleanup_spots(game_map, me):
    my_halite_check_out = my_halite_check
    checked = []

    for i in range(20):
        entry = shipyard_spots.get()
        pos = entry[3]

        if game_map[pos].halite_amount >= my_halite_check:
            checked.append(entry)

    for entry in checked:
        shipyard_spots.put(entry)
    logging.info("cleaned up " + str(20 - len(checked)))

    if shipyard_spots.empty():
        my_halite_check_out = 0
        logging.debug("all spots cleaned - reset value")

    return my_halite_check_out


def get_a_spot_from_shipyard(game_map, me, ship):
    outpos = ship_targets[ship.id]

    if shipyard_spots.empty() and outpos is None:
        outpos = ship.position

    if outpos is None:
        outpos = shipyard_spots.get(block=False)[3]
        ship_targets[ship.id] = outpos

    logging.info("ship " + str(ship.id) + " was assigned spot " + str(outpos))

    return outpos


def position_to_direction(ship, target):
    if ship.position == target or target is None:
        return Direction.Still

    for direction in Direction.get_all_cardinals():
        if ship.position.directional_offset(direction) == target:
            return direction


def navigate(game_map, me, ship, target):
    ship_distance = game_map.calculate_distance(ship.position, target)

    next_pos = ship.position

    min_halite_next = 1001

    for position in ship.position.get_surrounding_cardinals():
        next_pos_distance = game_map.calculate_distance(position, target)
        next_pos_halite = game_map[position].halite_amount

        if next_pos_halite < min_halite_next and next_pos_distance < ship_distance and not game_map[position].is_occupied:
            min_halite_next = next_pos_halite
            next_pos = position

    return next_pos


def move_ship(game_map, me, ship):
    next_pos = ship.position

    if ship_status[ship.id] == 'Returning':
        next_pos = navigate(game_map, me, ship, me.shipyard.position)
    else:
        if game_map[ship.position].halite_amount > my_halite_check or ship.halite_amount < game_map[ship.position].halite_amount / 10:
            next_pos = ship.position
        elif ship_stuck_turn[ship.id] == game.turn_number - 1:
            next_pos = ship.position
        else:
            max_halite_next = -1
            next_pos = None

            positions_to_check = queue.Queue()
            positions_to_check.put(ship.position)

            iters = 0

            while True:

                if positions_to_check.empty():
                    next_pos = ship.position
                    break

                next_to_check = positions_to_check.get(block=False)

                for position in next_to_check.get_surrounding_cardinals():
                    positions_to_check.put(position)
                    if game_map[position].halite_amount > my_halite_check and not game_map[position].is_occupied and game_map[position].halite_amount > max_halite_next:
                        max_halite_next = game_map[position].halite_amount
                        next_pos = position

                if iters >= spot_iters_stop and next_pos is None:
                    next_pos = get_a_spot_from_shipyard(game_map, me, ship)

                if next_pos is not None:
                    break

                iters += 1

            logging.info(str(ship.id) + " trying to move to " + str(next_pos))
            if next_pos not in ship.position.get_surrounding_cardinals():
                next_pos = navigate(game_map, me, ship, next_pos)
            logging.info(str(ship.id) +
                         " finished move_ship with --> " + str(next_pos))

    next_dir = position_to_direction(ship, next_pos)

    logging.info("ship " + str(ship.id) + " --> best if moving to " +
                 str(next_pos) + " - " + str(next_dir))

    return next_dir


def get_ship_movements(game_map, me):
    all_ship_moves = {}
    all_next_positions = []

    pq = queue.PriorityQueue()

    for ship in me.get_ships():
        prio = 2
        next_move = move_ship(game_map, me, ship)
        ship_halite = ship.halite_amount

        next_pos = ship.position.directional_offset(next_move)

        if ship.position == me.shipyard.position:
            prio = 1
        elif next_move == Direction.Still:
            prio = 2

        pq.put((prio, -ship_halite, ship.id, next_pos, next_move, ship))

    while not pq.empty():
        next_item = pq.get(block=False)

        next_pos = next_item[3]
        next_ship = next_item[5]
        next_move = next_item[4]

        if next_pos in all_next_positions:
            next_pos = next_ship.position
            next_move = Direction.Still

        all_next_positions.append(next_pos)
        all_ship_moves[next_ship.id] = next_move

    return all_ship_moves, all_next_positions


def unstuck_ship(game_map, me, ship, all_next_positions):
    next_pos = ship.position
    next_dir = Direction.Still

    for direction in Direction.get_all_cardinals():
        thispos = ship.position.directional_offset(direction)

        if not game_map[thispos].is_occupied and thispos not in all_next_positions:
            next_pos = thispos
            next_dir = direction
            break

    logging.debug("just unstuck ship " + str(ship.id))

    return next_dir, next_pos


""" <<<Game Begin>>> """
game = hlt.Game()

refresh_spots(game.game_map, game.me)

max_turns = hlt.constants.MAX_TURNS

#pre-processing

# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Maheswaran")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:

    game.update_frame()
    me = game.me
    game_map = game.game_map

    command_queue = []

    my_halite_check = cleanup_spots(game_map, me)

    dropoff_positions = [d.position for d in list(me.get_dropoffs()) + [me.shipyard]]
    ship_positions = [d.position for d in list(me.get_ships())]

    if my_halite_check == 0:
        logging.debug("all spots cleaned")
        spot_iters_stop = 6

    my_max_ships = check_ship_max(game, game_map, me)

    my_ship_in_shipyard = False

    turns_left = max_turns - game.turn_number

    for ship in me.get_ships():
        if ship.id not in ship_status:
            ship_status[ship.id] = 'Exploring'

        if ship.id not in ship_still_count:
            ship_still_count[ship.id] = 0

        if ship.id not in ship_targets:
            ship_targets[ship.id] = None

        if ship.position == me.shipyard.position:
            ship_status[ship.id] = 'Exploring'
            my_ship_in_shipyard = True

        if ship_targets[ship.id] is not None and ship_targets[ship.id] == ship.position:
            ship_targets[ship.id] = None

        if ship.id not in ship_stuck_turn:
            ship_stuck_turn[ship.id] = -1

        if ship.is_full:
            ship_status[ship.id] = 'Returning'

        shipyard_distance = game_map.calculate_distance(ship.position, me.shipyard.position)
        if turns_left <= shipyard_distance + 5:
            ship_status[ship.id] = 'Finishing'
            logging.debug('time to finish!! - ship ' + str(ship.id) + ' - ' + str(shipyard_distance))

    ship_moves, all_next_positions = get_ship_movements(game_map, me)

    logging.debug(ship_moves)

    for ship in me.get_ships():
        shipyard_distance = game_map.calculate_distance(ship.position, me.shipyard.position)
        if ship_moves[ship.id] == Direction.Still:
            ship_still_count[ship.id] += 1
        else:
            ship_still_count[ship.id] = 0

        if ship_still_count[ship.id] >= 2 and ship_status[ship.id] == "Exploring" and game_map[ship.position].halite_amount <= my_halite_check:
            unstuck_move, unstuck_pos = unstuck_ship(game_map, me, ship, all_next_positions)

            if unstuck_move != Direction.Still:
                ship_moves[ship.id] = unstuck_move
                all_next_positions.append(unstuck_pos)
                ship_still_count[ship.id] = 0
                ship_stuck_turn[ship.id] = game.turn_number
        elif ship_still_count[ship.id] >= 2 and ship_status[ship.id] == "Returning" and shipyard_distance == 1 and game_map[me.shipyard.position].is_occupied and not my_ship_in_shipyard:
            next_move = game_map.get_unsafe_moves(ship.position, me.shipyard.position)
            ship_moves[ship.id] = next_move[0]
            all_next_positions.append(me.shipyard.position)
            ship_still_count[ship.id] = 0
            ship_stuck_turn[ship.id] = game.turn_number

    for ship in me.get_ships():
        next_move = ship_moves[ship.id]
        logging.debug(str(ship.id) + ' got --> ' + str(next_move))

        if ship_status[ship.id] == 'Finishing':
            shipyard_distance = game_map.calculate_distance(ship.position, me.shipyard.position)
            next_naive = game_map.naive_navigate(ship, me.shipyard.position)
            next_moves = game_map.get_unsafe_moves(ship.position, me.shipyard.position)

            if next_naive != Direction.Still:
                next_move = next_naive
            elif shipyard_distance == 1:
                next_move = next_moves[0]
            elif turns_left < shipyard_distance and len(next_moves) > 0:
                next_move = next_moves[0]
            else:
                next_move = Direction.Still
            command_queue.append(ship.move(next_move))
        else:
            if next_move == Direction.Still:
                command_queue.append(ship.stay_still())
            else:
                command_queue.append(ship.move(next_move))

    # spawn ships
    # - atleast two
    # - only when shipyard is empty
    if (
        len(me.get_ships(
        )) < my_max_ships and not game_map[me.shipyard.position].is_occupied and me.shipyard.position not in all_next_positions and me.halite_amount >= constants.SHIP_COST and game.turn_number <= 200

    ):
        command_queue.append(me.shipyard.spawn())

    game.end_turn(command_queue)