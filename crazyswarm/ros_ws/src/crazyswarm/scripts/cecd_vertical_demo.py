#!/usr/bin/env python

import numpy as np
from pycrazyswarm import *

Z = 1.0

if __name__ == "__main__":
    swarm = Crazyswarm()
    timeHelper = swarm.timeHelper
    allcfs = swarm.allcfs

    allcfs.takeoff(targetHeight=Z, duration=1.0+Z)
    timeHelper.sleep(1.5+Z)
    for cf in allcfs.crazyflies:
        pos = np.array(cf.initialPosition) + np.array([0, 0, Z])
        cf.goTo(pos, 0, 1.0)
    timeHelper.sleep(5.0)
    
    cf0, cf1 = allcfs.crazyflies
    
    cf0.goTo(np.array([0, 0, 1.0]), 0, 1.0)
    cf1.goTo(np.array(cf.initialPosition) + np.array([0, 0, 1.5]), 0, 1.0)
    timeHelper.sleep(1.0);
    
    cf1.goTo(np.array([0, 0, 1.5]), 0, 1.0)
    timeHelper.sleep(5.0);
    
    cf1.goTo(np.array(cf.initialPosition) + np.array([0, 0, 1.5]), 0, 1.0)
    timeHelper.sleep(1.0);
    
    cf1.goTo(np.array(cf.initialPosition) + np.array([0, 0, Z]), 0, 1.0)
    timeHelper.sleep(1.0);
    
    

    #allcfs.land(targetHeight=0.04, duration=1.0+Z)
    
    for cf in allcfs.crazyflies:
        cf.land(0.01, 1.0+Z)
    timeHelper.sleep(1.0+Z)
