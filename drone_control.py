import libardrone
import time
drone = libardrone.ARDrone()

drone.set_speed(0.3)
drone.turn_left()
time.sleep(2)
drone.hover()
drone.turn_right()
time.sleep(2)
drone.land()

drone.halt()