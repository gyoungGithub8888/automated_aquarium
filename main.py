# time in minutes unless specified otherwise
import time
import RPi.GPIO as GPIO
#----------------------Constants---------------------------------
loopDelayInterval 	= 10

intervalFerts 	= 24 * 7 * 60 #fertilizer
intervalLC	 	= 24 * 60 #liquid carbon

timeLights 	= 	[600, 1200] #lights (input in minutes)
timeInject 	= 	[570, 1140] #co2 in ject (input in minutes)

lots = 1e6
# in order of:
#	Lights 	0
# 	Inject 	1
pinListOutput 	= [1, 2] 												##
pinStatusOutput = [0, 0]
# in order of:
# 	Ferts
# 	LC
pinListPWM 		= [3, 4] 												##
pinStatusPWM 	= [0, 0]
dcPWM 			= [50, 50] 												##
freqPWM 		= [0, 0] 												##
runtimePWM 		= [5, 1] # in seconds 									##
intervalPWM 	= [24*7*60, 24*60]
# in order of:
# 	Reset
pinListInput 	= [5] 													##
#----------------------------------------------------------------
#-------------------------Functions------------------------------
def time_check(timeOn,timeOff,timeCurrent,pinNo):
	if (timeCurrent > timeOn and timeCurrent < timeOff):
		if GPIO.output(pinNo, not GPIO.input(pinNo)) == False:
			print("Pin number",pinNo,
				"Switched ON at", time.asctime(time.localtime()))
		pinStatus = True	
	else:
		if GPIO.output(pinNo, not GPIO.input(pinNo)) == True:
			print("Pin number",pinNo,
				"Switched OFF at", time.asctime(time.localtime()))
		pinStatus = False
	return pinStatus

def pump_check(timer,interval,runtime,pwm,dc):
	if (timer - interval) > 0:
		pwm.start(dc)
		print("Pump run on", time.asctime(time.localtime()))
		time.sleep(runtime)
		pwm.stop()
		timer = runtime/60
	else:
		timer = timer
	return timer
#----------------------------------------------------------------
#----------------------Setup-------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinListOutput[0], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListOutput[1], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListPWM[0],	 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListPWM[1],	 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(pinListInput[0], 	GPIO.IN)

fertPWM = GPIO.PWM(pinListPWM[0],freqPWM[0])
LCPWM 	= GPIO.PWM(pinListPWM[1],freqPWM[1])
fertPWM.stop()
LCPWM.stop()
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
	#--------fetch current time
	timeCurrent = time.localtime()[3]*60 + time.localtime()[4]
	timeAbs 	= time.time()/60
	dt 			= timeAbs - timeAbsPrev
	#--------lights, CO2 check
	pinStatusOutput[0] = time_check(timeLights[0],timeLights[1],
									timeCurrent,pinListOutput[0])
	pinStatusOutput[1] = time_check(timeInject[0],timeLights[1],
									timeCurrent,pinListOutput[1])
	# Write to output
	GPIO.output(pinListOutput,pinStatusOutput)
	#--------Pumps
	# Ferts
	timerFerts	+= dt
	timerFerts 	= pump_check(	timerFerts,intervalPWM[0],
								runtimePWM[0],fertPWM,dcPWM[0])
	# LC
	timerLC += dt
	timerLC	= pump_check(	timerLC,intervalPWM[1],
								runtimePWM[1],LCPWM,dcPWM[1])
	# Timer reset
	if GPIO.input(pinList[4]) == True:
		timerFerts 	= lots
		timerLC 	= lots

	# end of loop iterations
	timeAbsPrev = time.time()/60
	time.sleep(loopDelayInterval)
#----------------------End Loop-----------------------------------------
