#!/bin/sh


halite --replay-directory replays/ -vvv --width 10 --height 10 --turn-limit 50 "python3 MyBot-ML.py" "python3 MyBot-ML.py"
