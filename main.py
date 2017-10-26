# time in minutes unless specified otherwise
# Structure lights and CO2 as "keep on during time"
# Structure pumps as "run every X minutes"
# For reset, hold until pump begins

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
#----------------------Constants---------------------------------
LOOP_DELAY_INTERVAL = 10

TIME_LIGHTS 	= 	[600, 1200] #lights (input in minutes)
TIME_INJECT 	= 	[570, 1140] #co2 in ject (input in minutes)

LOTS = 1e6
# in order of:
#	Lights 	0
# 	Inject 	1
PINLIST_OUTPUT 	= [1, 2] 												##
# in order of:
# 	Ferts
# 	LC
PINLIST_PWM = [3, 4] 													##
DC 			= [50, 50] 													##
RUNTIME 	= [5, 1] # in seconds 										##
INTERVAL 	= [24*7*60, 24*60]
PINPWM 		= 18 														##
FREQ 		= 0		 													##
# in order of:
# 	Reset
PINLIST_INPUT 	= [5] 													##
#----------------------------------------------------------------
#-------------------------Functions------------------------------
def is_time(timeOn,timeOff,timeCurrent):
	return timeCurrent > timeOn and timeCurrent < timeOff
def is_output(pinNo):
	return GPIO.output(pinNo, not GPIO.input(pinNo))
def MDYT():
	return time.asctime(time.localtime())
def time_in_minutes():
	return time.localtime()[3]*60 + time.localtime()[4]

def timer_on_off(timeOn,timeOff,timeCurrent,pinNo):
	"""Timer for lights and CO2 inject"""
	if is_time(timeOn,timeOff,timeCurrent):
		if is_output(pinNo) == False:
			print("Pin number ",pinNo,
				" switched ON at", MDYT())
		pinStatus = True	
	else:
		if is_outout(pinNo) == True:
			print("Pin number ",pinNo,
				" switched OFF at", MDYT())
		pinStatus = False
	return pinStatus

def pump_on_off(timer,interval,runtime,pinNo,dc,pwm):
	"""Switch to correct pump and run for set time"""
	if (timer - interval) > 0:
		GPIO.output(pinNo, True)
		pwm.start(dc)
		print("Pump for ",pinNo," run on", MDYT())
		time.sleep(runtime)
		pwm.stop()
		GPIO.output(pinNo, False)
		timer = runtime/60
	else:
		timer = timer
	return timer
#----------------------------------------------------------------
#----------------------Setup-------------------------------------
GPIO.setup(PINLIST_OUTPUT[0], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(PINLIST_OUTPUT[1], 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(PINLIST_PWM[0],	 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(PINLIST_PWM[1],	 	GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(PINLIST_INPUT[0], 	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.add_event_detect(PINLIST_INPUT[0], GPIO.FALLING)
pwm = GPIO.PWM(PINPWM,FREQ[0])
# --------Initializing Variables
pwm.stop()
pinStatusOutput = [0, 0]
pinStatusPWM 	= [0, 0]
timerFerts 		= 0
timerLC 		= 0

timeAbsPrev 	= time.time()/60
#----------------------------------------------------------------
# ---------------------Begin Loop--------------------------------
while True:
	#--------fetch current time
	timeCurrent = time_in_minutes()
	timeAbs 	= time.time()/60
	dt 			= timeAbs - timeAbsPrev
	#--------lights, CO2 check
	pinStatusOutput[0] = timer_on_off(TIME_LIGHTS[0],TIME_LIGHTS[1],
									timeCurrent,PINLIST_OUTPUT[0])
	pinStatusOutput[1] = timer_on_off(TIME_INJECT[0],TIME_LIGHTS[1],
									timeCurrent,PINLIST_OUTPUT[1])
	# Write to output
	GPIO.output(PINLIST_OUTPUT,pinStatusOutput)
	#--------Pumps
	# Ferts
	timerFerts	+= dt
	timerFerts 	= pump_on_off(	timerFerts,INTERVAL[0],
								RUNTIME[0],PINLIST_PWM[0],
								DC[0],pwm)
	# LC
	timerLC += dt
	timerLC	= pump_on_off(	timerLC,INTERVAL[1],
							RUNTIME[1],PINLIST_PWM[1],
							DC[1],pwm)
	# Timer reset
	if GPIO.event_detected(PINLIST_INPUT[0]):
		timerFerts 	= LOTS
		timerLC 	= LOTS

	# end of loop iterations
	timeAbsPrev = time.time()/60
	time.sleep(LOOP_DELAY_INTERVAL)
#----------------------End Loop-----------------------------------