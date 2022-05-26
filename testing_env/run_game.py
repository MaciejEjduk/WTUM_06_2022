import os
import secrets

map_settings = {32:400,
                40:425,
                48:450,
                56:475,
                64:500,}

TOTAL_TURNS = 50

while True:
    map_size = 32
    command = 'halite.exe --replay-directory replays/ -vvv --width 32 --height 32 "python MyBot.py" "python MyBot.py"'

    os.system(command)