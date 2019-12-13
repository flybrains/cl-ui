import sys
import argparse
import time
import csv
import os
import logging
import serial
import numpy as np
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM

def establish_pi_connection(RPI_HOST, RPI_PORT):
	PACKET_SIZE = 1024
	sock=socket(AF_INET, SOCK_DGRAM)
	return sock

def convert_angle_for_arduino(inputVal, previousAngle, mult):
	inputVal = inputVal*(256/800)
	spr = 800
	conv1 = spr*(1000/256)
	newAngle1 = (inputVal*conv1)/1000
	highLimit = 500
	lowLimit = 300
	midPoint = 400
	if (newAngle1 < highLimit) and (newAngle1 > lowLimit):
		if(newAngle1 > midPoint):
			newAngle1 = highLimit
		else:
			newAngle1 = lowLimit
	newAngle1 = newAngle1 + offset
	if np.abs(newAngle1-previousAngle) > 400:
		if(newAngle1 > previousAngle):
			mult = mult-1
			offset = mult*spr
			newAngle1 = newAngle1 - spr
		else:
			mult = mult + 1
			offset = mult*spr
			newAngle1 = newAngle1 + spr
	previousAngle = newAngle1
	return int(newAngle1), mult

def run_fictrac_client(config_dict, gradient, replay=None):

	# RPI SOCKET CONNECTION
	RPI_SOCK  = establish_pi_connection(config_dict["RPI_HOST"], config_dict["RPI_HOST"])
	time.sleep(1)

	# LOGGING
	now = datetime.now() # current date and time
	dts = now.strftime("%m%d%Y-%H%M%S")
	logger = logging.getLogger('closed_loop_client_output')
	if sys.platform.startswith('l'):
		if 'closed-loop-client-logs' not in os.listdir("/home/{}".format(os.getcwd().split("/")[2])):
			os.mkdir(os.path.join("/home/{}".format(os.getcwd().split("/")[2]), 'closed-loop-client-logs'))
		hdlr = logging.FileHandler(os.path.join("/home/{}".format(os.getcwd().split("/")[2]), 'closed-loop-client-logs')+'/{}.log'.format(dts))
	else:
		if 'closed-loop-client-logs' not in os.listdir(r"C:\Users\{}".format(os.getcwd().split("\\")[2])):
			os.mkdir(os.path.join(r"C:\Users\{}".format(os.getcwd().split("\\")[2]),'closed-loop-client-logs'))
		hdlr = logging.FileHandler(r"C:\Users\{}".format(os.getcwd().split("\\")[2])+r'\closed-loop-client-logs'+r'\{}.log'.format(dts))
	logger.addHandler(hdlr)
	logger.setLevel(logging.DEBUG)
	logger.info('{}  {}, {}, {}, {}, {}, {}, {}, {}, {}'.format("timestamp", "ft_heading", "ft_xPos","ft_yPos", "motor_step_command", "mfc1_stpt", "mfc2_stpt", "mfc3_stpt", "led1_stpt", "led2_stpt"))

	if gradient is not None:
		w = gradient.shape[1]
		h = gradient.shape[0]


	if replay is not None:
		last_hard_send = datetime.now()
		last_virtual_send = datetime.strptime(replay[0][0], '%H:%M:%S.%f')

		for idx in range(len(replay[0])-1):

			virtual_current_time = datetime.strptime(replay[0][idx+1], '%H:%M:%S.%f')

			while (datetime.now() - last_hard_send) < (virtual_current_time - last_virtual_send):
				time.sleep(0.001)
			SENDSTRING = '<'+ '{},{},{},{},{},{},{}'.format(1,800000, replay[1][idx+1][2], replay[1][idx+1][3], replay[1][idx+1][4], 0.0, 0.0) +'>\n'
			# RPI_SOCK.sendto(str.encode('{}'.format(SENDSTRING)), ("192.168.137.10", 5000))
			print(idx, SENDSTRING)
			last_hard_send = datetime.now()
			last_virtual_send = virtual_current_time

	else:
		with socket(AF_INET, SOCK_STREAM) as sock:
			time.sleep(0.02)

			if replay == False:
				sock.connect((config_dict['LOCAL_HOST'], config_dict['LOCAL_PORT']))

			mfc1_sp, mfc2_sp, mfc3_sp = 0.0, 0.0, 0.0
			led1_sp, led2_sp = 0.0, 0.0
			motorSendVal = 800000
			lastMotorSendVal = motorSendVal
			expStartTime = time.time()
			LEDLastTime = expStartTime
			odorLastTime = expStartTime
			motorLastTime = expStartTime
			stimLastTime = expStartTime
			slidingWindow = [[0,0,0,0],[0,0,0,0]]
			activating=False
			stim = False
			previousAngle = 800000
			mult = 1000

			try:
				i = 0
				while True:
					data = sock.recv(1024)
					if not data:
						break
					line = data.decode('UTF-8')
					toks = line.split(',')

					if ((len(toks) < 24) | (toks[0] != "FT")):
						('Bad read')
						continue

					posx = float(toks[15])*3
					posy = -float(toks[16])*3
					net_vel = float(toks[19])*3
					heading = float(toks[17])

					heading = -heading
					motorHeadingMap = heading % (2*np.pi)
					propHead = motorHeadingMap/(2*np.pi)
					target = int(propHead*800)

					if len(slidingWindow) >= config_dict["SLIDING_WINDOW_LENGTH"]:
						slidingWindow.pop(0)
					slidingWindow.append([posx, posy, net_vel, heading])

					if (time.time() - motorLastTime) > (1/60000):
						correctedTarget, mult = convert_angle_for_arduino(target, previousAngle, mult)
						previousAngle, motorSendVal = correctedTarget, correctedTarget
						motorLastTime = time.time()

						if config_dict["CONSTANT_FLOW"]:

							mfc1_sp = 0.0								#empty
							mfc2_sp = (float(config_dict["MAX_FLOW_RATE"]) / 1000.)*(1.0-(float(config_dict["PERCENT_CONSTANT_ODOR1"])/100.0)) #air
							mfc3_sp = (float(config_dict["MAX_FLOW_RATE"]) / 1000.)*(float(config_dict["PERCENT_CONSTANT_ODOR1"])/100.0) #acv

						else:
							x_index = int(posx + 0.5*w)
							y_index = int(0.5*h - posy)
							mfc1_sp, mfc2_sp, mfc3_sp = gradient[y_index, x_index,:]

						if config_dict["LED_ACTIVATION_MODE"]=='temporal':
							if (time.time() - expStartTime) >= config_dict["LED_INITIAL_DELAY"]:
								if ((time.time() - LEDLastTime) >= config_dict["LED_PERIOD"]):
									if activating==False:
										activating = True
										pulseStarted = time.time()

										if config_dict["LED_COLOR"]=='red':
											led1_sp = config_dict["LED_INTENSITY"]/100.
											led2_sp = 0.0
										else:
											led1_sp = 0.0
											led2_sp = config_dict["LED_INTENSITY"]/100.

									elif activating==True and (time.time()-pulseStarted)<=config_dict["LED_DURATION"]:
										pass
									else:
										activating=False
										led1_sp = 0.0
										led2_sp = 0.0
										LEDLastTime = pulseStarted

							if config_dict["LED_ACTIVATION_MODE"]=='conditional':
								d = np.diff([i[1] for i in slidingWindow])
								da = np.mean(d)
								if da >= config_dict["LED_CONDITION_THRESHOLD"]:
									stim=True
								# ++++++++++++++++++++++++++++++++++++
								# ADD MORE KINEMATIC CONDITIONS HERE
								# ++++++++++++++++++++++++++++++++++++
								if stim and (time.time() - stimLastTime)>=config_dict["LED_POST_ACT_LOCK"]:
									if activating==False:
										activating = True
										pulseStarted = time.time()

										if config_dict["LED_COLOR"]=='red':
											led1_sp = config_dict["LED_INTENSITY"]/100.
											led2_sp = 0.0
										else:
											led1_sp = 0.0
											led2_sp = config_dict["LED_INTENSITY"]/100.

									elif activating and (time.time()-pulseStarted)<=config_dict["LED_DURATION"]:
										pass
									else:
										activating = False
										stim = False
										stimLastTime = pulseStarted
										led1_sp = 0.0
										led2_sp = 0.0

						else:
							led1_sp = 0.0
							led2_sp = 0.0

						SENDSTRING = '<'+ '{},{},{},{},{},{},{}'.format(1,motorSendVal, mfc1_sp, mfc2_sp, mfc3_sp, led1_sp, led2_sp) +'>\n'
						RPI_SOCK.sendto(str.encode('{}'.format(SENDSTRING)), ("192.168.137.10", 5000))
						now = datetime.now()
						dts = now.strftime("%m/%d/%Y-%H:%M:%S.%f")
						logger.info('{} -- {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(dts,heading, posx,posy, motorSendVal, mfc1_sp, mfc2_sp, mfc3_sp, led1_sp, led2_sp))


			except KeyboardInterrupt:
				pass
				# SENDSTRING = '<'+ '{},{},{},{},{},{},{}'.format(0, 'a', mfc1_sp, mfc2_sp, mfc3_sp, led1_sp, led2_sp) +'>\n'
				# RPI_SOCK.sendto(str.encode('{}'.format(SENDSTRING)), (RPI_HOST, RPI_PORT))
				# RPI_SOCK.close()

if __name__=='__main__':
	pass
