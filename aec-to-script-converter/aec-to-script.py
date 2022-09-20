# Name: aec-to-script.py
# Revision: 0.5
# Author: Taewon Kang
# Date: 2022-09-02
# Description: .aec to crazyswarm flight script converter

import math
import subprocess
import sys
from pprint import pprint


def read_file(input_file):
    # Count number of drones
    num = 0
    while True:
        line = input_file.readline()
        if not line:
            break
        line = line.strip().split()
        if line and line[0] == "LIGHT":
            num += 1
    input_file.seek(0)

    # Get keyframe info
    start = 0
    end = 0
    while True:
        line = input_file.readline()
        if not line:
            break
        line = line.strip().split()
        if line and line[0] == "SHOWFROM":
            start = int(line[1])
        if line and line[0] == "SHOWTO":
            end = int(line[1])

        if start or end:
            break
    input_file.seek(0)

    # Build positions list for each drone
    positions = []
    colors = []
    for i in range(num):
        positions.append([])
        colors.append([])
        while True:
            line = input_file.readline()
            if not line:
                break
            line_list = line.strip().split()
            if line_list and line_list[0] == "KEY" and line_list[1] != "키프레임":
                break
        for j in range(start, end):
            ret = parse_line(line)
            positions[i].append(ret[:2])
            colors[i].append(ret[2:])
            line = input_file.readline()

    # Transpose both list: to make the structure of the list parallel to the keyframes
    positions = list(map(list, zip(*positions)))
    colors = list(map(list, zip(*colors)))

    return positions, colors


def parse_line(line):
    # Parse KEY lines and return parameters
    # line.strip()
    keys = line.split()
    pos = get_pos(keys)
    yaw = get_yaw(keys)
    r_color, g_color, b_color = get_color(keys)
    return [pos, yaw, r_color, g_color, b_color]


def get_pos(keys):
    # Get position info from parsed KEY
    return convert_coord(list(map(float, keys[2:5])))


def convert_coord(coord):
    # Convert coordinates to crazyflie coordinate system
    temp = coord[2]
    coord[2] = coord[1]
    coord[1] = temp

    # Set scale
    for i in range(len(coord)):
        coord[i] *= scale
    return coord


def get_yaw(keys):
    # Use Y_rotate value
    # Convert from degree to radian
    return math.radians(float(keys[6]))


def get_color(keys):
    # Get LED color values from KEY
    return float(keys[11]), float(keys[12]), float(keys[13])


def build_yaml():
    output_file = open("crazyflies.yaml", 'w')
    output_file.write("crazyflies:\n")
    for i in range(len(start_pos)):
        output_file.write("  - id: {}\n".format(str(i + 1)))
        output_file.write("    channel: {}\n".format(str(channel)))
        output_file.write("    initialPosition: {}\n".format(str(start_pos[i][0])))
        output_file.write("    type: default\n")


def build_script():
    # TODO: Make user interface, process rebooting of drones

    output_file = open("flight_script.py", 'w')
    output_file.write("from pycrazyswarm import *\n"
                      "from cflib.drivers.crazyradio import Crazyradio\n"
                      "import numpy as np\n"
                      "import subprocess\n"
                      "import sys\n"
                      "import signal\n\n")

    # Rebooting drones: not verified
    output_file.write("if len(sys.argv) < 1:\n"
                      "    print(\"rebooting drones...\")\n")
    output_file.write("    cr = Crazyradio()\n"
                      "    for i in range(len(allcfs.crazyflies)):\n"
                      "        cr.set_channel({})\n".format(channel) +
                      "        cr.set_data_rate(cr.DR_2MPS)\n"
                      "        cr.set_address(((0xE7,) * 4) + (i + 1,))\n"
                      "        print(cr.send_packet((0xff, 0xfe, 0xff)).ack)\n" +  # Init the reboot
                      "        print(cr.send_packet((0xff, 0xfe, 0xf0, 1)).ack)\n\n")  # Reboot to Firmware

    # Initialize crazyswarm_server
    output_file.write("print(\"initializing...\")\n")
    output_file.write("swarm = Crazyswarm()\n"
                      "timeHelper = swarm.timeHelper\n"
                      "allcfs = swarm.allcfs\n"
                      "\n")

    # SIGNAL event handling
    output_file.write("\ndef handler(signum, frame):\n"
                      "    print(\"\\nemergency stop!\")\n"
                      "    for cfs in allcfs.crazyflies:\n"
                      "        cfs.cmdStop()\n"
                      "    exit(-1)\n\n")

    output_file.write("\nsignal.signal(signal.SIGINT, handler)\n\n")
    output_file.write("print(\"press enter to start: \")\n")
    output_file.write("input()\n\n")

    for i in range(len(pos_list)):
        output_file.write("# keyframe {}\n".format(str(i)))
        for j in range(len(pos_list[i])):
            output_file.write("pos = np.array(allcfs.crazyflies[{}].initialPosition)\n".format(str(j)))
            output_file.write(
                "pos += np.array({}) - np.array({})\n".format(str(pos_list[i][j][0]), str(pos_list[0][j][0])))
            output_file.write("allcfs.crazyflies[{}].cmdPosition(pos, {})\n".format(str(j), str(pos_list[i][j][1])))

            # set LED color every 1 sec cycle
            if i % (framerate / ledrate) == 0:
                output_file.write("allcfs.crazyflies[{}].setLEDColor({})\n".format(str(j), str(led_list[i][j])[1:-1]))

        output_file.write("timeHelper.sleepForRate({})\n\n".format(str(framerate)))

    output_file.write("for cf in allcfs.crazyflies:\n"
                      "    cf.cmdStop()\n")


if __name__ == '__main__':
    channel = 80
    framerate = 30
    ledrate = 1
    scale = 0.01
    file = open(sys.argv[1], 'r')
    pos_list, led_list = read_file(file)
    start_pos = pos_list[0]
    build_yaml()
    build_script()

    # Print for debuging
    # pprint(pos_list)
    # pprint(led_list)
