###############
##  Imports  ##
###############
from enum import Enum
import RPi.GPIO as GPIO
import time


###############
## Constands ##
###############

# LEDs
RED_LED = 25
YELLOW_LED = 8
GREEN_LED = 7

# Buttons
BUTTON_A = 21
BUTTON_B = 20
BUTTON_C = 16
BUTTON_D = 12


###############
## Functions ##
###############
def ask_pin_code():
    pin = input('Pin please: ')
    return pin == '1337'


###############
##    Init   ##
###############
GPIO.setmode(GPIO.BCM)

GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)

GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_C, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_D, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(RED_LED, False)
GPIO.output(YELLOW_LED, False)
GPIO.output(GREEN_LED, False)


###############
## Variables ##
###############
# State
class State(Enum):
    off = 1
    standby = 2
    triggered = 3
    settings = 4

state = State.off
button_a_pressed = False
button_b_pressed = False
button_c_pressed = False
button_d_pressed = False

# alarm
alarm_delay = 1
alarm_time = time.time()
alarm_on = False

# LEDs
led_green_on = False
led_yellow_on = False
led_red_on = False
blink = False


###############
## Main Loop ##
###############
while True:
    led_red_on = False
    led_green_on = False
    led_yellow_on = False
    blink = False

    # Button input
    if GPIO.input(BUTTON_A):
        if not button_a_pressed:
            # Trigger alarm
            if state == State.standby:
                state = State.triggered

        button_a_pressed = True
    else:
        button_a_pressed = False

    # B
    if GPIO.input(BUTTON_B):
        if not button_b_pressed:
            if ask_pin_code():
                # Set alarm on standby
                if state == State.off:
                    state = State.standby
                # Set alarm on Off
                elif state == State.standby:
                    state = State.off
                # Set alarm to standby from trigger
                elif state == State.triggered:
                    state = State.standby

        button_b_pressed = True
    else:
        button_b_pressed = False

    # C
    if GPIO.input(BUTTON_C):
        if not button_c_pressed:
            # Go to settings
            if state == State.off:
                state = State.settings
            # Exit settings
            elif state == State.settings:
                state = State.off

        button_c_pressed = True
    else:
        button_c_pressed = False

    # D
    if GPIO.input(BUTTON_D):
        if not button_d_pressed:
            # Change blink speed
            if state == State.settings:
                # swap between 1, 2 and 3 delay
                alarm_delay = alarm_delay + 1 if alarm_delay < 3 else 1
        button_d_pressed = True
    else:
        button_d_pressed = False


    # Set variables based on states
    # NOTE: Python has no switch
    # Off
    if state == State.off:
        led_green_on = True
        print('Off')

    # Standby
    elif state == State.standby:
        led_yellow_on = True
        print('Standby')

    # Triggered
    elif state == State.triggered:
        led_red_on = True
        blink = True
        print('Triggered')

    # Settings
    elif state == State.settings:
        led_green_on = True
        led_red_on = True
        blink = True
        print('Settings')


    # blink timer
    if time.time() - alarm_time >= alarm_delay:
        alarm_time = time.time()
        alarm_on = not alarm_on

    # LEDs
    GPIO.output(GREEN_LED, led_green_on)
    GPIO.output(YELLOW_LED, led_yellow_on)
    GPIO.output(RED_LED, led_red_on and alarm_on)

    # Debug prints
    print("Button A", button_a_pressed)
    print("Button B", button_b_pressed)
    print("Button C", button_c_pressed)
    print("Button D", button_d_pressed)

    print("State", state)

    print("SNELHEIDIIDIDIDIDI DIDIDIDIDIIDIDIDIDI", alarm_delay)

    print("Green", led_green_on)
    print("Yellow", led_yellow_on)
    print("Red", led_red_on)
