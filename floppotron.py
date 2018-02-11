#!/usr/bin/env python3
import usb.core
import usb.util
import array
import RPi.GPIO as GPIO
import threading
import time

headPos = 0
delay = 0
DRIVEMAP = [[17,18],[22,23],[26,20]]
delays = [0,0,0]
notes = [0,0,0]

def calcFreq(keyPressed):
	return 55 * (2 ** ((keyPressed - 57) / 12))

def runDrive(driveNum):
	global delays
	direct = DRIVEMAP[driveNum][0]
	stp = DRIVEMAP[driveNum][1]
	while(True):
		if(delays[driveNum] == 0):
			time.sleep(0.05)
		else:
			GPIO.output(direct, not GPIO.input(direct))
			GPIO.output(stp, 1)
			time.sleep(delays[driveNum]/2)
			GPIO.output(stp, 0)
			time.sleep(delays[driveNum]/2)
	
def playNote(data):
	global delays, notes
	if(data[3] == 0):
		if data[2] in notes:
			n = notes.index(data[2])
			notes[n] = 0
			delays[n] = 0
	else:
		if 0 in notes:
			n = notes.index(0)
			notes[n] = data[2]
			delays[n] = 1/calcFreq(data[2])
		
				

def main():
	global delays
	GPIO.setmode(GPIO.BCM)
	for d,s in DRIVEMAP:
		GPIO.setup(d, GPIO.OUT)
		GPIO.setup(s, GPIO.OUT)
		GPIO.output(d,1)
	t0 = threading.Thread(target=runDrive, args=[0], daemon=True)
	t0.start()
	t1 = threading.Thread(target=runDrive, args=[1], daemon=True)
	t1.start()
	t2 = threading.Thread(target=runDrive, args=[2], daemon=True)
	t2.start()
	device = usb.core.find(idVendor=0x0499, idProduct=0x1030)
	try:
		device.detach_kernel_driver(0)
	except:
		pass
	endpoint = device[0][(0,0)][0]

	data = None
	while True:
		try:
			data = device.read(0x82, 0x4)
			if(data[0] == 0x9):
				print("playing note " + str(data[2]))
				playNote(data)
		except usb.core.USBError as e:
			data = None
			if e.args == ('Operation timed out',):
				print('Timed out')
				continue
if __name__ == '__main__':
	main()
