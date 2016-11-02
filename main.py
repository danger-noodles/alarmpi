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
LED_RED = 25
LED_YELLOW = 8
LED_GREEN = 7

# Buttons
BUTTON_A = 21
BUTTON_B = 20
BUTTON_C = 16
BUTTON_D = 12

# Speaker
SPEAKER_PIN = 24

# PinCode
PIN_CODE = 1337


###############
## Functions ##
###############
def ask_pin_code():
    pin = input('Pin please: ')
    return int(pin) == PIN_CODE


###############
##    Init   ##
###############
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LEDS
GPIO.setup(LED_RED, GPIO.OUT)
GPIO.setup(LED_YELLOW, GPIO.OUT)
GPIO.setup(LED_GREEN, GPIO.OUT)

# BUTTONS
GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_C, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_D, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Speaker
GPIO.setup(SPEAKER_PIN, GPIO.OUT)

# Turn lights of by default
GPIO.output(LED_RED, False)
GPIO.output(LED_YELLOW, False)
GPIO.output(LED_GREEN, False)


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

# Speaker
speaker_time = 0
speaker_up = True

# LEDs
led_green_on = False
led_yellow_on = False
led_red_on = False


###############
## Main Loop ##
###############
while True:
    led_red_on = False
    led_green_on = False
    led_yellow_on = False

    # Button input
    if GPIO.input(BUTTON_A):
        if not button_a_pressed:
            print("Button A", button_a_pressed)
            # Trigger alarm
            if state == State.standby:
                state = State.triggered
                print('Triggered')

        button_a_pressed = True
    else:
        button_a_pressed = False

    # B
    if GPIO.input(BUTTON_B):
        if not button_b_pressed:
            print("Button B", button_b_pressed)
            if ask_pin_code():
                # Set alarm on standby
                if state == State.off:
                    state = State.standby
                    print('Standby')
                # Set alarm on Off
                elif state == State.standby:
                    state = State.off
                    print('Off')
                # Set alarm to standby from trigger
                elif state == State.triggered:
                    state = State.standby
                    print('Standby')

        button_b_pressed = True
    else:
        button_b_pressed = False

    # C
    if GPIO.input(BUTTON_C):
        if not button_c_pressed:
            print("Button C", button_c_pressed)
            # Go to settings
            if state == State.off:
                state = State.settings
                print('Setting')
            # Exit settings
            elif state == State.settings:
                state = State.off
                print('Off')

        button_c_pressed = True
    else:
        button_c_pressed = False

    # D
    if GPIO.input(BUTTON_D):
        if not button_d_pressed:
            print("Button D", button_d_pressed)
            # Change blink speed
            if state == State.settings:
                # swap between 1, 2 and 3 delay
                alarm_delay = alarm_delay + 1 if alarm_delay < 3 else 1
                print("Alarm delay:", alarm_delay)
        button_d_pressed = True
    else:
        button_d_pressed = False

    # Set variables based on states
    # NOTE: Python has no switch
    # Off
    if state == State.off:
        led_green_on = True

    # Standby
    elif state == State.standby:
        led_yellow_on = True

    # Triggered
    elif state == State.triggered:
        led_red_on = True

    # Settings
    elif state == State.settings:
        led_green_on = True
        led_red_on = True


    # blink timer
    if time.time() - alarm_time >= alarm_delay:
        alarm_time = time.time()
        alarm_on = not alarm_on

    # Speaker timer
    if speaker_time > 1000:
        speaker_time = 10
    elif led_red_on and alarm_on:
        GPIO.output(SPEAKER_PIN, True)
        time.sleep(1.0 / 2000 / 2)
        GPIO.output(SPEAKER_PIN, False)
        time.sleep(1.0 / 2000 / 2)
        speaker_time += 1
    else:
        speaker_time += 1

    # LEDs
    GPIO.output(LED_GREEN, led_green_on)
    GPIO.output(LED_YELLOW, led_yellow_on)
    GPIO.output(LED_RED, led_red_on and alarm_on)


# Turn every ting off when program closes
GPIO.output(LED_GREEN, False)
GPIO.output(LED_YELLOW, False)
GPIO.output(LED_RED, False)
GPIO.output(SPEAKER_PIN, False)
