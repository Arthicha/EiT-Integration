
# standard library
import time

# image processing library
import cv2

# MiR controller
from MiRCommunication.MiR.MiRCommunication import MIR

# Barcode reader
from BarCoddunication.barcode_reader import *


class Deliverirororirobot:

	
	MiR = None # robot/robot interface object
	CamIdx = 1 # camera port

	# predefined parameter
	ROBOTDICT = {'ROBOT1':1,'ROBOT2':2,'ROBOT3':3} # robot QR code <-> box position
	BOXDICT = {'POSIT1':1,'POSIT2':2,'4465441':3} # box code <-> target
	SUBPOINTDICT = [-1.0,-1.5,-2.0] # target index (box code) <-> x-offset

	# variable
	robotstate = ['n/a',0] # [station name,subpoint idx]
	prebarcode = '' 

	def __init__(self,MiR,videoport):

		self.CamIdx = videoport
		self.MiR = MiR # robot/robot interface object
		self.boxlist = [None,None,None] # box code corresponding to the location on the robot
		self.robotstate = ['n/a',0] # set robot state to unknown


	# -------------------------------------------------------------------------------------
	# behaviors

	def move_to_home(self):
		self.MiR.stop_mission_queue()
		self.MiR.todolist_add(self.MiR.scream,'beep')
		self.MiR.todolist_add(self.MiR.move_to,'Home')
		self.MiR.todolist_add(self.MiR.scream,'beep')
		self.MiR.start_mission_queue()

		self.__run__()
		self.robotstate = ['home',0]

	def move_to_speed(self,index):
		self.MiR.stop_mission_queue()
		self.MiR.todolist_add(self.MiR.move_to,'highspeed'+str(index))
		#self.MiR.todolist_add(self.MiR.scream,'beep')
		self.MiR.start_mission_queue()

		self.__run__()
		self.robotstate = ['speed',index]

	def move_to_warehouse(self):
		self.MiR.stop_mission_queue()
		self.MiR.todolist_add(self.MiR.scream,'start')
		self.MiR.todolist_add(self.MiR.move_to,'Warehouse')
		self.MiR.todolist_add(self.MiR.scream,'beep')
		self.MiR.start_mission_queue()

		self.__run__()
		self.robotstate = ['warehouse',0]

	def move_to_assemblystation(self,name):
		self.MiR.stop_mission_queue()
		self.MiR.todolist_add(self.MiR.dock_to,'shelf'+str(name))
		self.MiR.start_mission_queue()

		self.__run__()
		self.robotstate = ['shelf'+str(name),0]

	def move_to_assemblysubpoint(self,subpoint):
		if self.robotstate[0] in ['shelfA']: 
			self.MiR.stop_mission_queue()
			self.MiR.todolist_add(self.MiR.move_for,self.SUBPOINTDICT[subpoint-1])
			self.MiR.todolist_add(self.MiR.scream,'beep')
			self.MiR.start_mission_queue()
			self.__run__()

			self.MiR.stop_mission_queue()
			time.sleep(3)
			self.MiR.start_mission_queue()
			self.__run__()
			self.MiR.todolist_add(self.MiR.scream,'beep')
			self.MiR.todolist_add(self.MiR.move_for,-self.SUBPOINTDICT[subpoint-1])

			self.robotstate = [self.robotstate[0],subpoint-1]

	def return_to_warehouse(self):
		self.MiR.stop_mission_queue()
		self.MiR.todolist_add(self.MiR.scream,'end')
		self.MiR.todolist_add(self.MiR.move_to,'Warehouse')
		self.MiR.todolist_add(self.MiR.scream,'beep')
		self.MiR.start_mission_queue()

		self.__run__()
		self.robotstate = ['warehouse',0]

		self.MiR.todolist_add(self.MiR.scream,'end')
		self.__run__()


	def warehouse_scaning(self):
		if self.robotstate[0] in ['warehouse']: 
			camera = cv2.VideoCapture(self.CamIdx)

			while 1:
				_, frame = camera.read()

				barcode, _ = adaptive_read(frame,imgsize=(1000,750),detectionparams=(13,10,100),binarizationparams=(10,30,101))
				
				if barcode != None:
					barcode = str(barcode)[2:-1]
					if (len(barcode) in [6,7]):
						if (barcode != self.prebarcode) and (self.prebarcode != None):
							self.__check_n_match__([barcode,self.prebarcode])
							time.sleep(0.2)
							self.MiR.todolist_add(self.MiR.scream,'beep')
						self.prebarcode = barcode

				self.MiR.handle()

				cv2.imshow('frame',frame)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break

			self.MiR.todolist_add(self.MiR.scream,'start')
			self.__run__()

			return self.boxlist
		else:
			return [None]*len(self.boxlist)



	# --------------------------------------------------------------------------------------
	# supporting private methods

	def __check_n_match__(self,barcodes):

		# initialize
		bidx = None
		sidx = None

		# searching
		for barcode in barcodes:
			if barcode in self.ROBOTDICT.keys():
				ridx = self.ROBOTDICT[barcode]-1
			elif barcode in self.BOXDICT.keys():
				bidx = self.BOXDICT[barcode]

		# update box list
		if (ridx != None) and (bidx != None):
			self.boxlist[ridx] = bidx

	def __run__(self):
		handle = True
		while(handle):
			handle = self.MiR.handle()




