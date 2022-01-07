#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2021 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import matplotlib.pyplot as plt

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    speed_area_1 = []
    speed_area_2 = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print(traci.edge.getLastStepVehicleIDs('slow_area'))
        #vehicles_id = traci.vehicle.getIDList()
        #target_vehicle = random.choice(vehicles_id)
        #current_speed = traci.vehicle.getSpeed(target_vehicle)
        
        vehicles = traci.edge.getLastStepVehicleIDs('event_area')
        if step > 0 and step % 800 == 0 : # and step%2500 <= 500:
            v_num = len(vehicles)
            for v in random.choices(vehicles, k = min(v_num, 3)):
                traci.vehicle.slowDown(v, 0, 3)
            plt.axvline(step, c='r')
                
        fastest_lane = -1
        fastest_speed = -1
        for i in range(3):
            if traci.lane.getLastStepMeanSpeed('event_area_' + str(i)) > fastest_speed:
                fastest_speed = traci.lane.getLastStepMeanSpeed('event_area_' + str(i))
                fastest_lane = i
                
        #if step % 500 == 0:
        #    for v in vehicles:
        #        if random.uniform(0, 1) < 0.5:
        #            traci.vehicle.changeLane(v, fastest_lane, 2)
            
        print(traci.edge.getLastStepMeanSpeed('effect_area_1'),traci.edge.getLastStepMeanSpeed('effect_area_2'))
        speed_area_1.append(traci.edge.getLastStepMeanSpeed('effect_area_1'))
        speed_area_2.append(traci.edge.getLastStepMeanSpeed('effect_area_2'))
        #if prev_target != "":
            #traci.vehicle.setSpeed(prev_target, -1)
        #prev_target = target_vehicle
        #print("set {}'s speed from {} to {}".format(target_vehicle, current_speed, traci.vehicle.getSpeed(target_vehicle)))
        step += 1
    plt.plot(speed_area_1, label='edge1')
    plt.plot(speed_area_2, label='edge2')
    plt.legend()
    plt.show()
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    #generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/highway.sumocfg",
                             "--tripinfo-output", "tripinfo.xml","--step-length","0.1"])
    run()
