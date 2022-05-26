import cv2
import numpy as np

for i in range(2,3):
    d = np.load(f"D:/Git/ME-test-repo/WTUM_06_2022/testing_env/game_play/{i}.npy")
    print(d)
    cv2.imshow("",d)
    cv2.waitKey(100000000000000)