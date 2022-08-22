# Name: aec-to-script.py
# Revision: 0.4
# Author: Taewon Kang
# Date: 2022-08-23
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


def convert_coord(coord, scale):
    # Convert coordinates to crazyflie coordinate system
    temp = coord[2]
    coord[2] = coord[1]
    coord[1] = temp

    # Set scale
    for i in range(len(coord)):
        coord[i] *= 0.01
    return coord


def get_yaw(keys):
    # Use Y_rotate value
    # Convert from degree to radian
    return math.radians(float(keys[6]))


def get_color(keys):
    # Get LED color values from KEY
    return float(keys[11]), float(keys[12]), float(keys[13])


def build_yaml(start_positions, channel_num):
    output_file = open("crazyflies.yaml", 'w')
    output_file.write("crazyflies:\n")
    for i in range(len(start_positions)):
        output_file.write("  - id: " + str(i + 1) + "\n")
        output_file.write("    channel: " + str(channel_num) + "\n")
        output_file.write("    initialPosition: " + str(start_positions[i][0]) + "\n")
        output_file.write("    type: default\n")


def build_script(positions, colors, frame_rate, led_rate):
    # TODO: Make user interface, process rebooting of drones

    output_file = open("flight_script.py", 'w')
    output_file.write("from pycrazyswarm import *\n"
                      "import numpy as np\n"
                      "import subprocess\n"
                      "import signal\n\n")

    # Rebooting drone: not verified
    # output_file.write("for i in range({}):\n".format(len(positions[0])) +
    #                   "    uri = \"radio://0/{}/2M/E7E7E7E7{}\".format(i)\n".format(channel, "{0:02X}") +
    #                   "    subprocess.call([\"rosrun crazyflie_tools reboot --uri \" + uri], shell=True)\n\n")

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

    for i in range(len(positions)):
        output_file.write("# keyframe " + str(i) + "\n")
        for j in range(len(positions[i])):
            output_file.write("pos = np.array(allcfs.crazyflies[" + str(j) + "].initialPosition)\n")
            output_file.write(
                "pos += np.array(" + str(positions[i][j][0]) + ") - np.array(" + str(positions[0][j][0]) + ")\n")
            output_file.write("allcfs.crazyflies[" + str(j) + "].cmdPosition(pos, " + str(positions[i][j][1]) + ")\n")

            # set LED color every 1 sec cycle
            if i % (frame_rate / led_rate) == 0:
                output_file.write("allcfs.crazyflies[" + str(j) + "].setLEDColor(" + str(colors[i][j])[1:-1] + ")\n")

        output_file.write("timeHelper.sleepForRate(" + str(frame_rate) + ")\n\n")

    output_file.write("for cf in allcfs.crazyflies:\n"
                      "    cf.cmdStop()\n")


if __name__ == '__main__':
    channel = 80
    framerate = 30
    ledrate = 1
    scale =
    file = open(sys.argv[1], 'r')
    pos_list, led_list = read_file(file)
    start_pos = pos_list[0]
    build_yaml(start_pos, channel)
    build_script(pos_list, led_list, framerate, ledrate)

    # Print for debuging
    # pprint(pos_list)
    # pprint(led_list)
