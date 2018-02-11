import usb.core
import usb.util
import array
import RPi.GPIO as GPIO
from threading import Timer
import time

headPos = 0
delay = 0

def calcFreq(keyPressed):
	return 55 * (2 ** ((keyPressed - 57) / 12))

def startTimer():
	global headPos
	global delay
	if(delay == 0):
		return
	t = Timer(delay,startTimer)
	if(GPIO.input(5)):
		headPos = headPos + 1
		if(headPos == 70):
			GPIO.output(5,0)
	else:
		headPos = headPos - 1
		if(headPos == 0):
			GPIO.output(5,1)
	t.start()
	return

def playNote(data, device):
	global delay
	freq = calcFreq(float(data[2]))
	delay = 1/freq
	notes = [delay]
	p = GPIO.PWM(3,freq)
	p.start(50)
	startTimer()
	while(True):
		d = device.read(0x82, 0x4)
		if(d[0] == 0x9):
			if(d[3] == 0x0):
				notes.remove(1/calcFreq(float(d[2])))
				if(len(notes) == 0):
					delay = 0
					p.stop()
					return
				else:
					delay = notes[len(notes)-1]
			else:
				freq = calcFreq(float(d[2]))
				delay = 1/freq
				notes.append(delay)
				p.stop()
				p = GPIO.PWM(3,freq)
				p.start(50)
				startTimer()
		
				

def main():
	device = usb.core.find(idVendor=0x0499, idProduct=0x1030)
	try:
		device.detach_kernel_driver(0)
	except:
		pass
	endpoint = device[0][(0,0)][0]
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(3, GPIO.OUT)
	GPIO.setup(5, GPIO.OUT)
	GPIO.output(5,1)
	p = GPIO.PWM(3,500)
	p.start(50)
	time.sleep(0.5)
	p.stop()

	data = None
	while True:
		try:
			data = device.read(0x82, 0x4)
			if(data[0] == 0x9):
				print("playing note " + str(data[2]))
				playNote(data, device)
		except usb.core.USBError as e:
			data = None
			if e.args == ('Operation timed out',):
				print('Timed out')
				continue
if __name__ == '__main__':
	main()
