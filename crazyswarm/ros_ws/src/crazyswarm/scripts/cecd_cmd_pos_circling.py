from pycrazyswarm import *
import numpy as np
import math

swarm = Crazyswarm()
timeHelper = swarm.timeHelper
allcfs = swarm.allcfs

x = []
y = []

rad = 0.5

for theta in range(0, 360):
    x.append(0.0 + rad * math.cos(math.radians(theta)))
    y.append(0.0 + rad * math.sin(math.radians(theta)))

Z = 0

print("Press Enter to start")
input()

# takeoff
while Z < 1.0:
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([0, 0, Z])
        cf.cmdPosition(pos)
    timeHelper.sleep(0.05)
    Z += 0.01
    
timeHelper.sleep(1.0)

# goto circling start position
i = 0
while i < 1.0:
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([rad * i, 0.0, Z])
        cf.cmdPosition(pos)
    timeHelper.sleep(0.05)
    i += 0.01
    
timeHelper.sleep(1.0)
    
# circling
for theta in range(0, 360):
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([x[theta], y[theta], Z])
        cf.cmdPosition(pos)
    timeHelper.sleep(0.05)
    
timeHelper.sleep(1.0)

# goto initial position
while i > 0.0:
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([rad * i, 0.0, Z])
        cf.cmdPosition(pos)
    timeHelper.sleep(0.05)
    i -= 0.01
    
timeHelper.sleep(1.0)

# land
while Z > 0.0:
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([0, 0, Z])
        cf.cmdPosition(pos)
    timeHelper.sleep(0.05)
    Z -= 0.01
    
timeHelper.sleep(0.5)

# turn-off motors
for cf in allcfs.crazyflies:
    cf.cmdStop()
