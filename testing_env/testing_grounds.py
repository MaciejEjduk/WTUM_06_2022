import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

all_files = os.listdir('training_data')

print(len(all_files))

halite_amounts = []

for f in all_files:
    halite_amount = f.split("-")[0]
    halite_amounts.append(halite_amount)

plt.hist(halite_amounts, 5)
plt.show()
