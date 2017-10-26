import time
import RPi.GPIO as GPIO
#----------------------Constants---------------------------------
loopDelayInterval 	= 10

intervalFerts 	= 24 * 7 * 60 #fertilizer (in minutes)
intervalLC	 	= 24 * 60 #liquid carbon (in minutes)
runtimeFerts	= 5 #in seconds
runtimeLC 		= 1 #in seconds

timeLights 	= 	[600, 1200] #lights (input in minutes)
timeInject 	= 	[570, 1140] #co2 in ject (input in minutes)

lots = 1e6

# in order of:
#	Ferts 	0
#	LC 		1
#	Lights 	2
# 	Inject 	3
pinListOutput 	= [1 2 3 4]
pinStatusOutput = [0 0 0 0]

pinListInput 	= [5]
#----------------------------------------------------------------
#-------------------------Functions------------------------------
def time_check(timeOn,timeOff,timeCurrent,pinNo):
	if (timeCurrent > timeOn and timeCurrent < timeOff):
		if GPIO.output(pinNo, not GPIO.input(pinNo)) == False:
			print("Switched on at", time.asctime(time.localtime()))
		pinStatus = True	
	else:
		if GPIO.output(pinNo, not GPIO.input(pinNo)) == True:
			print("Switched off at", time.asctime(time.localtime()))
		pinStatus = False
	return pinStatus

def pump_check(timer,interval,pin):
	if (timer - interval) > 0:
		pin = True
	else:
		pin = False
	return pin

def pump_run(timer,pin,runtime):
	if pin == True:
		print("Pump run on", time.asctime(time.localtime()))
		time.sleep(runtime)
		pin = False
		timer = runtime/60
	return timer,pin
#----------------------------------------------------------------
#----------------------Setup-------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinListOutput[0], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListOutput[1], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListOutput[2], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListOutput[3], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListInput[0], 	GPIO.IN)

#----------------------------------------------------------------


# Structure lights and CO2 as "keep on during time"
# Structure pumps as "run every X minutes"
# For reset, hold until pump begins
# ---------------------Begin Loop------------------------------------
# --------Initializing
timerFerts 		= 0
timerLC 		= 0
timeAbsPrev 	= time.time()/60
# --------Loop
while True:
	# fetch current time
	timeCurrent = time.localtime()[3]*60 + time.localtime()[4] # in minutes
	timeAbs 	= time.time()/60 # minutes
	dt 			= timeAbs - timeAbsPrev

	# lights check
	pinStatusOutput[2] = time_check(timeLights[0],timeLights[1],
									timeCurrent,pinListOutput[2])
	GPIO.output(pinList[2],pinStatusOutput[2])
	# CO2 check
	pinStatusOutput[3] = time_check(timeInject[0],timeLights[1],
									timeCurrent,pinListOutput[3])
	GPIO.output(pinList[3],pinStatusOutput[3])
	# Pumps--Ferts
	timerFerts	 += dt
	pinFerts = pump_check(timerFerts,intervalFerts,pinFerts)
	timerFerts,pinFerts = pump_run(timerFerts,pinFerts,runtimeFerts)
	# Pumps--LC
	timerLC	 += dt
	pinLC = pump_check(timerLC,intervalLC,pinLC)	
	timerLC,pinLC = pump_run(timerLC,pinLC,runtimeLC)
	# Timer reset
	if GPIO.input(pinList[4]) == True:
		timerFerts 	= lots
		timerLC 	= lots

	# end of loop iterations
	timeAbsPrev = time.time()/60
	time.sleep(loopDelayInterval)
#----------------------End Loop-----------------------------------------
