#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Position
from hlt.positionals import Direction

import random
import logging
import numpy
import math
import time

# This game object contains the initial game state.
game = hlt.Game()
starthalite = 0
for i in range(0, game.game_map.width):
    for j in range(0, game.game_map.height):
        starthalite += game.game_map[Position(i, j)].halite_amount
        
forecast = {}
for i in range (0, int(game.game_map.width)):
    for j in range(0, int(game.game_map.height)):
        areasum = 0
        good = 1
        if game.game_map.calculate_distance(game.me.shipyard.position, Position(i, j)) >= min(3*game.game_map.height/8, 20):
            for l in range(i- int(game.game_map.height/8), i + int(game.game_map.height/8) + 1):
                for k in range(j - int(game.game_map.height/8), j + int(game.game_map.height/8) + 1):
                    areasum += game.game_map[Position(l, k)].halite_amount
                    good += 165
            good -= 1
        if areasum >= good:
            forecast[(i, j)] = areasum
goodtup = (0, 0)
donealready = []


while goodtup[0] != -1:
    goodtup = (-1, -1)
    bigdense = 0
    for tup in forecast:
        if forecast[tup] > bigdense and tup not in donealready:
            bigdense = forecast[tup]
            goodtup = tup
    toremove = []
    if goodtup[0] != -1:
        donealready.append(goodtup)
        for tup in forecast:
            if not tup == goodtup and game.game_map.calculate_distance(Position(tup[0], tup[1]), Position(goodtup[0], goodtup[1])) < min(3*game.game_map.height/8, 20):
                toremove.append(tup)
        for tup in toremove:
            forecast.pop(tup)


            
# Respond with your name.
game.ready("Aggro")
shipsToReturn = []
threshold = 975
# vary this threshold with regard to halite available on map
shiptargets = {}
nextmap = []
mapscore = []
shipsOrdered = []
shipsToStay = []
nogozone = []
shipcounter = 0
turnamount = {64: 501, 56: 476, 48: 451, 40:426, 32: 401}
shipthreshold = {64: 20, 56: 18, 48: 16, 40: 14, 32: 12}
shipthreshold[game.game_map.width] += int(starthalite / 12500)
playersdead = {}
remainingTurns = turnamount[game.game_map.width]
shipsmade = 0
halitethreshold = int(starthalite/(game.game_map.width ** 2))
shipsbeen = {}
n = 0.9
nexthalite = 0
dropoffdistance = 0
switch = 0
distanceswitch = 1
highestdrop = 0
shipspawned = False
inspiration = []
crashed = []
playeramt = len(game.players)
for player in game.players:
        if player != game.me.id:
            playersdead[player] = False
            for x in range(game.players[player].shipyard.position.x-2, game.players[player].shipyard.position.x+3):
                for y in range(game.players[player].shipyard.position.y-2, game.players[player].shipyard.position.y+3):
                    nogozone.append(Position(x, y))

def closestForeDrop(ship):
    max = (locateClosestDropoff(ship).x, locateClosestDropoff(ship).y)
    for pos in forecast:
        if game.game_map.calculate_distance(ship.position, Position(pos[0], pos[1])) < game.game_map.calculate_distance(ship.position, Position(max[0], max[1])):
            max = pos
    return Position(max[0], max[1])

def updateForecast():
    toremove = []
    for tup in forecast:
        good = 0
        sum = 0
        enemyships = 0
        ourships = 0
        for i in range(tup[0]- int(game.game_map.height/8), tup[0] + int(game.game_map.height/8) + 1):
            for j in range(tup[1]- int(game.game_map.height/8), tup[1] + int(game.game_map.height/8) + 1):
                sum += game.game_map[Position(i, j)].halite_amount
                if game.game_map[Position(i, j)].is_occupied and game.game_map[Position(i, j)].ship.owner == me.id:
                    sum += 3 * game.game_map[Position(i, j)].ship.halite_amount
                    sum += 500
                    ourships += 1
                elif game.game_map[Position(i, j)].is_occupied and game.game_map[Position(i, j)].ship.owner == me.id:
                    enemyships += 1
        forecast[tup] = sum - 100 * min(enemyships - ourships, 0) ** 2
        if game.game_map[Position(tup[0], tup[1])].has_structure:
            toremove.append(tup)
    for tup in toremove:
        forecast.pop(tup)

def updatenogo():
    for player in game.players:
        if player != game.me.id and not playersdead[player]:
            for drop in game.players[player].get_dropoffs():
                if drop.position not in nogozone:
                    nogozone.append(drop.position)
    for player in game.players:
        # if the player is dead, remove that stuff from the nogozone
        if player != game.me.id and not playersdead[player] and game.players[player].halite_amount < 1000 and len(game.players[player].get_ships()) == 0:
            playersdead[player] = True
            for drop in game.players[player].get_dropoffs():
                nogozone.remove(drop.position)
            for x in range(game.players[player].shipyard.position.x-2, game.players[player].shipyard.position.x+3):
                for y in range(game.players[player].shipyard.position.y-2, game.players[player].shipyard.position.y+3):
                    nogozone.remove(Position(x, y))

def highestdrop():
    max = 0
    gtup = (game.me.shipyard.position.x, game.me.shipyard.position.y)
    for i in range(game.me.shipyard.position.x- int(game.game_map.height/8), game.me.shipyard.position.x + int(game.game_map.height/8) + 1):
        for j in range(game.me.shipyard.position.y - int(game.game_map.height/8), game.me.shipyard.position.y + int(game.game_map.height/8) + 1):
            max += game.game_map[Position(i, j)].halite_amount
    for tup in forecast:
        if switch * forecast[tup]/ (1 + distanceswitch * 0.001 * game.game_map.calculate_distance(game.me.shipyard.position, Position(tup[0], tup[1]))) > max:
            gtup = tup
            max = forecast[tup]/(1 + distanceswitch * 0.001 * game.game_map.calculate_distance(game.me.shipyard.position, Position(tup[0], tup[1])))
    for drop in game.me.get_dropoffs():
        areasum = 0
        enemyships = 0
        ourships = 0
        for i in range(drop.position.x- int(game.game_map.height/8), drop.position.x + int(game.game_map.height/8) + 1):
            for j in range(drop.position.y - int(game.game_map.height/8), drop.position.y + int(game.game_map.height/8) + 1):
                areasum += game.game_map[Position(i, j)].halite_amount
                if game.game_map[Position(i, j)].is_occupied and game.game_map[Position(i, j)].ship.owner == me.id:
                    areasum += 3 * game.game_map[Position(i, j)].ship.halite_amount
                    areasum += 500
                    ourships += 1
                elif game.game_map[Position(i, j)].is_occupied:
                    enemyships += 1
        if enemyships > ourships:
            areasum *= 1.05 ** (enemyships - ourships)
        if areasum * switch > max:
            gtup = (drop.position.x, drop.position.y)
            max = areasum
    return gtup



inithigh = highestdrop()
inspiration = []
for i in range(0, game.game_map.height):
    inspiration.append([])
    for j in range(0, game.game_map.width):
        inspiration[i].append(0)
for i in range(0, game.game_map.height):
    nextmap.append([])
    mapscore.append([])
    for j in range(0, game.game_map.width):
        nextmap[i].append(-1)
        areasum = 0
        for pos in Position(i, j).get_surrounding_cardinals():
            areasum += game.game_map[pos].halite_amount
        mapscore[i].append((4 * game.game_map[Position(i, j)].halite_amount + areasum)/ (7.5 + game.game_map.calculate_distance(Position(inithigh[0], inithigh[1]), Position(i, j))))

# id for my ship
# -1 if empty
# -2 for anyone else's ship
def updateNextMap():
    for i in range(0, game.game_map.height):
        for j in range(0, game.game_map.width):
            inspiration[i][j] = 0
    for player in game.players.values():
        if player.id != me.id:
            for ship in player.get_ships():
                for i in range(0, 5):
                    for j in range(ship.position.y - i, ship.position.y + i + 1):
                        temp = game_map.normalize(Position(ship.position.x - 4 + i, j))
                        if game.game_map.calculate_distance(ship.position, Position(ship.position.x-4 + i , j)) == 3 or game.game_map.calculate_distance(ship.position, Position(ship.position.x-4 + i , j)) == 2:
                            inspiration[temp.x][temp.y] += 45
                        elif game.game_map.calculate_distance(ship.position, Position(ship.position.x-4 + i , j)) <= 1 and inspiration[temp.x][temp.y] >= 0:
                            inspiration[temp.x][temp.y] -= 1349
                        else:
                             inspiration[temp.x][temp.y] += 1
                for i in range(1, 5):
                    for j in range(ship.position.y - (4 - i), ship.position.y + 4 - i + 1):
                        temp = game_map.normalize(Position(ship.position.x + i, j))
                        if game.game_map.calculate_distance(ship.position, Position(ship.position.x + i , j)) == 2 or game.game_map.calculate_distance(ship.position, Position(ship.position.x + i , j)) == 3:
                            inspiration[temp.x][temp.y] += 45
                        elif game.game_map.calculate_distance(ship.position, Position(ship.position.x + i , j)) <= 1 and inspiration[temp.x][temp.y] >= 0:
                            inspiration[temp.x][temp.y] -= 1349
                        else:
                            inspiration[temp.x][temp.y] += 1
    high = highestdrop()
    for i in range(0, game.game_map.height):
        for j in range(0, game.game_map.width):
            mod = 1
            if inspiration[i][j] >= 90:
                mod = 4
                if playeramt == 2:
                    mod = 1.4
            elif inspiration[i][j] < 0 and inspiration[i][j] >= -1348:
                mod = 2
                if playeramt == 2:
                    mod = 0.9
            elif inspiration[i][j] >= 2:
                mod = 1.5
                if playeramt == 2:
                    mod = 1
            if game.game_map[Position(i, j)].is_occupied and game.game_map[Position(i, j)].ship.owner != me.id:
                mod = 0.15
            inspiration[i][j] = mod
    for i in range(0, game.game_map.height):
        for j in range(0, game.game_map.width):
            areasum = 0
            for pos in Position(i, j).get_surrounding_cardinals():
                norm = game.game_map.normalize(pos)
                areasum += inspiration[norm.x][norm.y]*game.game_map[norm].halite_amount
                mapscore[i][j] = (inspiration[i][j] * 4 * game.game_map[Position(i, j)].halite_amount + areasum) / (7.5 + game.game_map.calculate_distance(Position(high[0], high[1]), Position(i, j)))
            if game.game_map[Position(i,j)].is_occupied:
                if game.game_map[Position(i,j)].ship.owner == game.me.id:
                    nextmap[i][j] = game.game_map[Position(i,j)].ship.id
                else:
                    nextmap[i][j] = -2
                if game_map.normalize(Position(i, j)) in crashed:
                    crashed.remove(game_map.normalize(Position(i, j)))
            else:
                if nextmap[i][j] >= 0 and game_map.normalize(Position(i, j)) not in crashed:
                        crashed.append(game_map.normalize(Position(i, j)))
                        logging.info(crashed)
                nextmap[i][j] = -1

# takes in a ship and a location, returns way to get to location through local minima if returning, maxima if leaving
def getBack(ship, drop):
    possPos = []
    returning = 1
    mustGetBack = False
    same = False
    for dir in game_map.get_unsafe_moves(ship.position, drop):
        possPos.append(ship.position.directional_offset(dir))
    if ship.position.x == drop.x and ship.position.y == drop.y:
        possPos.append(ship.position)
        same = True
    if ship.id not in shipsToReturn:
        returning = -1
    if returning == 1 and remainingTurns - game_map.calculate_distance(ship.position, locateClosestDropoff(ship)) <= 10:
        mustGetBack = True
    min = possPos[0]
    last = shipsbeen[ship.id]
    # Min for returning, make sure that it doesn't go into the enemy territory if possible
    # Max not returning, make sure that it doesn't go into the enemy territory if possible
    for pos in possPos:
        if (returning == 1 and game_map[pos].halite_amount < game_map[min].halite_amount and pos not in nogozone and last != pos) or (min in nogozone and pos not in nogozone) or (min == last):
            min = pos
        elif (returning == -1 and game_map[pos].halite_amount > game_map[min].halite_amount and pos not in nogozone  and last != pos) or (min in nogozone and pos not in nogozone) or (min == last):
            min = pos
    moves = game_map.get_unsafe_moves(ship.position, min)
    min = game_map.normalize(min)
    if not same:
        # Move if my ship isnt in the way
        if nextmap[min.x][min.y] == -1 or (nextmap[min.x][min.y] == -2 and min == drop):
                command_queue.append(ship.move(Direction.convert(moves[0])))
                shipsOrdered.append(ship.id)
                nextmap[min.x][min.y] = ship.id
                nextmap[ship.position.x][ship.position.y] = -1
                shipsbeen[ship.id] = Position(-1, -1)
        elif nextmap[min.x][min.y] == -2:
                badpos = list(map(lambda x: game_map.normalize(ship.position.directional_offset(Direction.invert(x))), game_map.get_unsafe_moves(ship.position, drop)))
                if returning == 1:
                    max = 22000
                    maxpos = Position(-1, -1)
                else:
                    max = -5
                    maxpos = Position(-1, -1)
                for pos in ship.position.get_surrounding_cardinals():
                    temp = game_map.normalize(pos)
                    if temp not in badpos and nextmap[temp.x][temp.y] == -1:
                        if returning == 1 and game_map[temp].halite_amount < max and temp != last:
                            max = game_map[temp].halite_amount
                            maxpos = temp
                        elif returning == -1 and game_map[temp].halite_amount > max and temp != last:
                            max = game_map[temp].halite_amount
                            maxpos = temp
                if (returning == 1 and max < 22000) or (returning == -1 and max > -5):
                    command_queue.append(ship.move(Direction.convert(game_map.get_unsafe_moves(ship.position, maxpos)[0])))
                    shipsOrdered.append(ship.id)
                    nextmap[ship.position.x][ship.position.y] = -1
                    nextmap[maxpos.x][maxpos.y] = ship.id
                    shipsbeen[ship.id] = ship.position
                else:
                    command_queue.append(ship.stay_still())
                    shipsOrdered.append(ship.id)
                    shipsToStay.append(ship.id)
                    shipsbeen[ship.id] = Position(-1, -1)
        elif mustGetBack and (min == me.shipyard.position or min in list(map(lambda x: x.position, me.get_dropoffs()))):
                command_queue.append(ship.move(Direction.convert(moves[0])))
                shipsOrdered.append(ship.id)
                nextmap[min.x][min.y] = ship.id
                nextmap[ship.position.x][ship.position.y] = -1
                shipsbeen[ship.id] = Position(-1, -1)
        # When you don't want to swap since it would make the other ship further from goal
        elif ship.id not in shipsToReturn and nextmap[min.x][min.y] >= 0 and game_map.calculate_distance(ship.position, shiptargets[nextmap[min.x][min.y]]) > game_map.calculate_distance(min, shiptargets[nextmap[min.x][min.y]]):
                if game_map[ship.position].halite_amount < halitethreshold:
                    #something I put in for testing purposes, get rid of it if it's bad
                    # Don't just sit there if there's someone ahead and the cell is almost empty, move to nearest highest halite location
                    max = game_map[ship.position].halite_amount
                    maxpos = ship.position
                    for pos in ship.position.get_surrounding_cardinals():
                        pos = game_map.normalize(pos)
                        if nextmap[pos.x][pos.y] == -1 and game_map[pos].halite_amount > max:
                            max = game_map[pos].halite_amount
                            maxpos = pos
                    if maxpos != ship.position and (max >= halitethreshold or ship.position == me.shipyard.position):
                        command_queue.append(ship.move(game_map.get_unsafe_moves(ship.position, maxpos)[0]))
                        shipsOrdered.append(ship.id)
                        nextmap[maxpos.x][maxpos.y] = ship.id
                        nextmap[ship.position.x][ship.position.y] = -1
                elif ship.position != me.shipyard.position:
                    command_queue.append(ship.stay_still())
                    shipsOrdered.append(ship.id)
                    shipsToStay.append(ship.id)
                shipsbeen[ship.id] = Position(-1, -1)
        # Swap positions of ships if first one is higher in priority
        elif nextmap[min.x][min.y] >= 0 and nextmap[min.x][min.y] not in shipsToStay and nextmap[min.x][min.y] not in shipsToReturn and nextmap[min.x][min.y] not in shipsOrdered:
                command_queue.append(ship.move(Direction.convert(moves[0])))
                command_queue.append(game.game_map[min].ship.move(Direction.invert(moves[0])))
                shipsOrdered.append(ship.id)
                shipsOrdered.append(game.game_map[min].ship.id)
                nextmap[ship.position.x][ship.position.y] = game.game_map[min].ship.id
                nextmap[min.x][min.y] = ship.id
                shipsbeen[ship.id] = Position(-1, -1)
    else:
        # if the destination is reached and it has less than 10 halite, go to the nearest highest halite square
        if game_map[drop].halite_amount < halitethreshold and (drop.x, drop.y) not in forecast:
            max = game_map[drop].halite_amount
            maxpos = ship.position
            for pos in ship.position.get_surrounding_cardinals():
                pos = game_map.normalize(pos)
                if nextmap[pos.x][pos.y] == -1 and game_map[pos].halite_amount > game_map[ship.position].halite_amount and game_map[pos].halite_amount > max:
                    max = game_map[pos].halite_amount
                    maxpos = pos
            if max > game_map[drop].halite_amount and max >= halitethreshold:
                command_queue.append(ship.move(game_map.get_unsafe_moves(ship.position, maxpos)[0]))
                shipsOrdered.append(ship.id)
                nextmap[maxpos.x][maxpos.y] = ship.id
                nextmap[ship.position.x][ship.position.y] = -1
            else:
                command_queue.append(ship.stay_still())
                shipsOrdered.append(ship.id)
                shipsToStay.append(ship.id)
        else:
            command_queue.append(ship.stay_still())
            shipsOrdered.append(ship.id)
            shipsToStay.append(ship.id)
        shipsbeen[ship.id] = Position(-1, -1)
    
def locateClosestDense(ship, blacklist, high):
    max = -1
    maxpos = (-1, -1)
    scanx0 = ship.position.x - 15
    scanx = ship.position.x + 16
    scany0 = ship.position.y - 15
    scany = ship.position.y + 16
    tempmap = []
    areascan = mappresence(ship)
    aggressive = (areascan[0] - areascan[1] > 5)
    if ship.id in shiptargets:
        blacklist.remove(shiptargets[ship.id])
    for i in range(0, 31):
        tempmap.append([])
        for j in range(0, 31):
            tpos = game.game_map.normalize(Position(scanx0 + i, scany0 + j))
            tempmap[i].append(mapscore[tpos.x][tpos.y])
    for pos in blacklist:
        if game.game_map.calculate_distance(Position(pos.x, 0), Position(ship.position.x, 0)) <= 15 and game.game_map.calculate_distance(Position(0, pos.y), Position(0, ship.position.y)) <= 15:
            x = pos.x
            if x < game_map.normalize(Position(scanx0, 0)).x:
                x = pos.x + game_map.height
            y = pos.y
            if y < game_map.normalize(Position(0, scany0)).y:
                y = pos.y + game_map.height
            tempmap[x-game_map.normalize(Position(scanx0, 0)).x][y - game_map.normalize(Position(0, scany0)).y] = 0
    # If another ship has that location as a target, don't go there
    for i in range(scanx0, scanx):
        for j in range (scany0, scany):
            temp = game_map.normalize(Position(i, j))
            newscore = tempmap[i - scanx0][j - scany0] / (10 + game_map.calculate_distance(ship.position, temp))
            if aggressive and game_map[temp].is_occupied and game_map[temp].ship.owner != me.id and game_map.calculate_distance(temp, ship.position) < game_map.height/16:
                newscore = (2 * game_map[temp].ship.halite_amount + game_map[temp].halite_amount - 2 * ship.halite_amount) / ((7.5 + game_map.calculate_distance(temp, Position(high[0], high[1]))) * (10 + game_map.calculate_distance(ship.position, temp)))
            if (newscore > max):
               maxpos = Position(i, j)
               max = newscore
            elif (newscore == max) and game.game_map.calculate_distance(ship.position, maxpos) > game.game_map.calculate_distance(ship.position, temp):
                maxpos = Position(i, j)
    return game.game_map.normalize(maxpos)

# Order the ship order based on distance
def sortShips(ships):
    ret = []
    notret = []
    result = []
    for ship in ships:
        if ship.id in shipsToReturn:
            ret.append(ship)
        else:
            notret.append(ship)
    ret = sorted(ret, key = distance)
    notret = sorted(notret, key = distance)
    result = ret + notret
    if game_map[me.shipyard.position].is_occupied and game_map[me.shipyard.position].ship.owner == me.id:
        return [game_map[me.shipyard.position].ship] + result
    else:
        return result
    
def distance(ship):
    return game_map.calculate_distance(ship.position, shiptargets[ship.id])

def rival():
    result = -1
    haliteamount = -1
    for player in game.players:
        if player != game.me.id and game.players[player].halite_amount > haliteamount:
            result = player
            haliteamount = game.players[player].halite_amount
    return result
    
def updateShipTargets():
    toremove = []
    for id in shiptargets:
        if not game.me.has_ship(id):
            toremove.append(id)
    for id in toremove:
        shiptargets.pop(id)
        shipsbeen.pop(id)

def locateClosestDropoff(ship):
    drops = []
    for drop in me.get_dropoffs():
        drops.append(drop.position)
    drops.append(me.shipyard.position)
    min = drops[0]
    for drop in drops:
        if game.game_map.calculate_distance(ship.position, drop) < game.game_map.calculate_distance(ship.position, min):
            min = drop
    return min

def closestDropoff(pos):
    drops = []
    for drop in me.get_dropoffs():
        drops.append(drop.position)
    drops.append(me.shipyard.position)
    min = drops[0]
    for drop in drops:
        if game.game_map.calculate_distance(pos, drop) < game.game_map.calculate_distance(pos, min):
            min = drop
    return min

def mappresence(ship):
    myships = 0
    enemyships = 0
    for i in range(ship.position.x - int(game_map.height/8), ship.position.x + int(game_map.height/8) + 1):
        for j in range(ship.position.y - int(game_map.height/8), ship.position.y + int(game_map.height/8) + 1):
            temp = game_map.normalize(Position(i, j))
            if game_map[temp].is_occupied:
                if game_map[temp].ship.owner == me.id:
                    myships += 1
                else:
                    enemyships += 1
    return (myships, enemyships)
    
def closeshipstoforecast():
    result = []
    for tup in forecast:
        mindist = 100000
        res = []
        for ship in me.get_ships():
            if game.game_map.calculate_distance(Position(tup[0], tup[1]), ship.position) < mindist:
                mindist = game.game_map.calculate_distance(Position(tup[0], tup[1]), ship.position)
                res = [ship]
            elif game.game_map.calculate_distance(Position(tup[0], tup[1]), ship.position) == mindist:
                res.append(ship)
        result += res
    return result

def highestforecast():
    initmax = (game_map.height/4 + 1) ** 2 * 165
    max = 0
    gtup = (-1, -1)
    for tup in forecast:
        if forecast[tup] > initmax and forecast[tup]/(1 + distanceswitch * 0.001 * game.game_map.calculate_distance(game.me.shipyard.position, Position(tup[0], tup[1]))) > max:
            gtup = tup
            max = forecast[tup]/(1 + distanceswitch * 0.001 * game.game_map.calculate_distance(game.me.shipyard.position, Position(tup[0], tup[1])))
    return gtup
            
while True:
    # Get the latest game state.
    game.update_frame()
    start = time.time()
    # You extract player metadata and the updated map metadata here for convenience.
    remainingTurns-=1
    updatenogo()
    updateForecast()
    me = game.me
    nexthalite = me.halite_amount
    game_map = game.game_map
    currenthalite = 0
    highdrop = highestdrop()
    for i in range(0, game_map.height):
        for j in range(0, game_map.width):
            currenthalite += game_map[Position(i, j)].halite_amount
    if currenthalite <= starthalite*n and threshold >= 900:
        threshold -= 25
        n -= .125
    updateNextMap()
    updateShipTargets()
    # A command queue holds all the commands you will run this turn.
    command_queue = []
    shipsOrdered = []
    shipsToStay = []
    if shipsmade == 12:
        switch = 1
    if game.turn_number % 50 == 0:
        logging.info(forecast)
        logging.info(highestforecast())
    if shipspawned and game_map[me.shipyard.position].is_occupied:
        shipsbeen[game_map[me.shipyard.position].ship.id] = Position(-1, -1)
    # Get rid of sectors if they don't have halite
    # When all sectors don't have halite reduce the staying threshold by 25
    if halitethreshold != 0 and currenthalite < 3*halitethreshold/4 * game_map.height * game_map.height:
        halitethreshold = int(3*halitethreshold/4)
    dropofftobe = []
    gships = closeshipstoforecast()
    hfore = highestforecast()
    dropoffmade = False
    for ship in me.get_ships():
        # Set destinations for all ships
        fore = closestForeDrop(ship)
        close = locateClosestDropoff(ship)
        inreturn = ship.id in shipsToReturn
        if nexthalite >= 3250 and ship in gships and fore == Position(hfore[0], hfore[1]) and game_map.calculate_distance(fore, close) >= min(3*game_map.height/8, 20):
            shiptargets[ship.id] = fore
            dropofftobe.append(ship.id)
        elif ship.halite_amount >= threshold and not inreturn:
            shipsToReturn.append(ship.id)
        if nexthalite + game_map[ship.position].halite_amount + ship.halite_amount >= 4000 and game_map.calculate_distance(ship.position, close) >= min(3*game_map.height/8, 20) and (ship.position.x, ship.position.y) == hfore:
            command_queue.append(ship.make_dropoff())
            if len(me.get_dropoffs()) == 0:
                halitethreshold = 100
                distanceswitch = 0
            shipsOrdered.append(ship.id)
            nexthalite -= 4000
            forecast.pop((ship.position.x, ship.position.y))
        elif hfore[0] == -1 and not dropoffmade and nexthalite + game_map[ship.position].halite_amount + ship.halite_amount >= 4000 and game_map.calculate_distance(ship.position, close) >= min(3*game_map.height/8, 20) and mappresence(ship)[0] > 19:
            command_queue.append(ship.make_dropoff())
            shipsOrdered.append(ship.id)
            nexthalite -= 4000
            dropoffmade = True
        if ship.halite_amount < 100 and inreturn:
            shipsToReturn.remove(ship.id)
        #Get back if you don't have time
        if remainingTurns - game_map.calculate_distance(ship.position, close) <= 10 and ship.id not in shipsToReturn and remainingTurns - game_map.calculate_distance(ship.position, close) > 0:
            shipsToReturn.append(ship.id)
        # If the ship doesn't have a lot of halite, crash it into adjacent squares from the leading player's shipyard
        inreturn = ship.id in shipsToReturn
        if ship.id not in dropofftobe and not inreturn:
            shiptargets[ship.id] = locateClosestDense(ship, list(shiptargets.values()), highdrop)
        if inreturn:
            shiptargets[ship.id] = close
    # Check which ships should stay
    for ship in me.get_ships():
        if ship.id not in shipsOrdered:
            tar = shiptargets[ship.id]
            if game_map[ship.position].has_structure and game_map[ship.position].structure.owner == me.id and remainingTurns <= 10:
                    shipsToStay.append(ship.id)
                    command_queue.append(ship.stay_still())
                    shipsOrdered.append(ship.id)
            elif (ship.id not in dropofftobe and ship.id not in shipsToReturn and game_map[ship.position].halite_amount >= halitethreshold/(1 + int(ship.halite_amount/450)/4) and not tar in crashed) or ship.halite_amount < round(game_map[ship.position].halite_amount/10):
                    shipsToStay.append(ship.id)
                    command_queue.append(ship.stay_still())
                    shipsOrdered.append(ship.id)
            elif ship.id not in shipsToReturn and ship.halite_amount + game_map[ship.position].halite_amount * 0.25 >= threshold:
                    shipsToStay.append(ship.id)
                    command_queue.append(ship.stay_still())
                    shipsOrdered.append(ship.id)
    # Act to reach destinations if ships should move
    shipList = sortShips(me.get_ships())
    for i in range (0, len(shipList)):
        if shipList[i].id not in shipsOrdered and shipList[i].id not in shipsToStay:
            getBack(shipList[i], shiptargets[shipList[i].id])
    # Increment halite threshold by 100 every 10 turns
    # If you have spawned less ships than the threshold and have enough halite, spawn a ship.
    # Don't spawn a ship if you will have a ship at port, though.
    shipspawned = False
    if shipsmade < 14 and nexthalite >= constants.SHIP_COST and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0:
        command_queue.append(game.me.shipyard.spawn()) 
        shipsmade+=1
        shipspawned = True
    elif shipsmade <= shipthreshold[game_map.width] and nexthalite >= constants.SHIP_COST and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0 and (nexthalite >= 5000 or len(me.get_dropoffs()) >= 1):
        command_queue.append(game.me.shipyard.spawn())
        shipsmade+=1
        shipspawned = True
    # Note to self: play around with these numbers
    # Spawn ships if you have at least halite and less than half of threshold ships on the board and the board has halite
    elif playeramt == 4 and shipsmade >= shipthreshold[game_map.width] and currenthalite > 55 * game_map.height * game_map.height and game.turn_number <= turnamount[game.game_map.width]- 50 and len(me.get_ships()) < 0.9 * shipthreshold[game_map.width] and nexthalite >= 1000 and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0:
        command_queue.append(game.me.shipyard.spawn())
        shipspawned = True
    elif playeramt == 4 and shipsmade >= shipthreshold[game_map.width] and currenthalite > 20 * game_map.height * game_map.height and game.turn_number <= turnamount[game.game_map.width]- 50 and len(me.get_ships()) < 0.25*shipthreshold[game_map.width] and nexthalite >= 1000 and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0:
        command_queue.append(game.me.shipyard.spawn())
        shipspawned = True
    elif shipsmade >= shipthreshold[game_map.width] and len(game.players)==2 and len(me.get_ships()) < len(game.players[rival()].get_ships()) and nexthalite >= constants.SHIP_COST and nextmap[me.shipyard.position.x][me.shipyard.position.y] < 0:
        command_queue.append(game.me.shipyard.spawn())
        shipspawned = True
    end = time.time()
    logging.info(end-start)
    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)