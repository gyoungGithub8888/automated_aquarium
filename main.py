import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup( , GPIO.OUT)
GPIO.setup( , GPIO.OUT)

def time_check(timeOn,timeOff,timeCurrent,pin):
	if (timeCurrent > timeOn and timeCurrent < timeOff):
		if pin == False:
			print("Switched on at", time.asctime(time.localtime()))
		pinStatus = True	
	else:
		if pin == True:
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

#----------------------Variables---------------------------------
loopDelayInterval 	= 10

pinFerts 		= False
pinLC 			= False
pinReset 		= True
pinLights 		= False
pinInject 		= False

intervalFerts 	= 24 * 7 * 60 #fertilizer (in minutes)
intervalLC	 	= 24 * 60 #liquid carbon (in minutes)
runtimeFerts	= 5 #in seconds
runtimeLC 		= 1 #in seconds

timeLights 	= 	[600, 1200] #lights (input in minutes)
timeInject 	= 	[570, 1140] #co2 in ject (input in minutes)

lots = 1e6
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
	timeCurrent = time.localtime()[3]*60 + time.localtime()[4] # current time in minutes
	timeAbs 	= time.time()/60 # time in minutes
	dt 			= timeAbs - timeAbsPrev

	# lights check
	pinLights = time_check(timeLights[0],timeLights[1],timeCurrent,pinLights)
	# CO2 check
	pinInject = time_check(timeInject[0],timeLights[1],timeCurrent,pinInject)
	# Pumps--Ferts
	timerFerts	 += dt
	pinFerts = pump_check(timerFerts,intervalFerts,pinFerts)
	timerFerts,pinFerts = pump_run(timerFerts,pinFerts,runtimeFerts)
	# Pumps--LC
	timerLC	 += dt
	pinLC = pump_check(timerLC,intervalLC,pinLC)	
	timerLC,pinLC = pump_run(timerLC,pinLC,runtimeLC)
	# Timer reset
	if pinReset == True:
		timerFerts 	= lots
		timerLC 	= lots
		pinReset = False

	# end of loop iterations
	timeAbsPrev = time.time()/60
	time.sleep(loopDelayInterval)
#----------------------End Loop-----------------------------------------
