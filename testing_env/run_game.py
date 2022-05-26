import os
import secrets

while True:
    command = 'halite.exe --replay-directory replays/ -vvv --no-logs --no-replay --width 32 --height 32 "python MyBot.py" "python MyBot.py"'

    os.system(command)