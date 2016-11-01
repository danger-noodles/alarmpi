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
alarm_speed = 1
alarm_time = 0

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
    button_a_pressed = GPIO.input(BUTTON_A)
    button_b_pressed = GPIO.input(BUTTON_B)
    button_c_pressed = GPIO.input(BUTTON_C)
    button_d_pressed = GPIO.input(BUTTON_D)

    print("Button A", button_a_pressed)
    print("Button B", button_b_pressed)
    print("Button C", button_c_pressed)
    print("Button D", button_d_pressed)

    print("State", state)

    # Off
    if state == State.off:
        led_green_on = True
        print('Off')

        # Button to set on standby
        if button_b_pressed:
            # set on standby if code is correct
            if ask_pin_code():
                state = State.standby
                continue

        elif button_c_pressed:
            state = State.settings
            continue

    # Standby
    elif state == State.standby:
        led_yellow_on = True
        print('Standby')

        # Trigger button
        if button_a_pressed:
            print('A pressed while Standby')
            state = State.triggered
            continue

        # Button to turn off
        elif button_b_pressed:
            print('B pressed while Standby')
            # turn off if code is correct
            if ask_pin_code():
                state = State.off
                continue

    # Triggered
    elif state == State.triggered:
        led_red_on = True
        blink = True
        print('Triggered')

        if button_b_pressed:
            if ask_pin_code():
                state = State.standby
                continue

    # Settings
    elif state == State.settings:
        led_green_on = True
        led_red_on = True
        blink = True
        print('Settings')

        # button to "save" alarm speed
        if button_c_pressed:
            state = State.off
            continue
        # button to change alarm speed
        elif button_d_pressed:
            # swap between 1, 2 and 3 speed
            alarm_speed = alarm_speed + 1 if alarm_speed < 3 else 1

    # blink timer
    alarm_on = False
    if alarm_time > alarm_speed * 1000:
        alarm_time = 0
        alarm_on = True
    else:
        alarm_time += 1

    print("SNELHEIDIIDIDIDIDI DIDIDIDIDIIDIDIDIDI", alarm_speed)
    # LEDs
    GPIO.output(GREEN_LED, led_green_on)
    GPIO.output(YELLOW_LED, led_yellow_on)
    GPIO.output(RED_LED, led_red_on and alarm_on)
    print("Green", led_green_on)
    print("Yellow", led_yellow_on)
    print("Red", led_red_on)
