
# standard library
import time

# image processing library
import cv2

# MiR controller
from Integration.integration import Deliverirororirobot
from MiRCommunication.MiR.MiRCommunication import MIR



if __name__ == "__main__":

	mirinterface = MIR(auth_file="MiRCommunication/auth.json") # initialize MiR communication
	port = 1 # initialize camera port
	derobot = Deliverirororirobot(mirinterface,1) # initialize robot

	derobot.move_to_warehouse()
	boxlist = derobot.warehouse_scaning()
	print(boxlist)
	for box in boxlist:
		if box is not None:
			derobot.move_to_assemblystation('A')
			derobot.move_to_assemblysubpoint(box)
	derobot.return_to_warehouse()
	derobot.move_to_home()

	#derobot.move_to_assemblystation('A')
	#derobot.move_to_assemblysubpoint(1)

	#mir.start_mission_queue()
	



	