###############
##  Imports  ##
###############
from enum import Enum
import threading
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

def blink_alarm():
    print('Alarm Thread')

    # Gobals
    global g_alarm_on
    global g_alarm_delay

    # Alarm
    alarm_time = time.time()
    alarm_on = False

    while g_alarm_on:
        # blink timer
        if time.time() - alarm_time >= g_alarm_delay:
            alarm_time = time.time()
            alarm_on = not alarm_on

        # NOTE: This does not work 100%
        if alarm_on:
            # Make speaker bleep
            GPIO.output(SPEAKER_PIN, True)
            time.sleep(1.0 / 2000 / 2) # TODO: replace this with something else
            GPIO.output(SPEAKER_PIN, False)
            time.sleep(1.0 / 2000 / 2) # TODO: replace this with something else

        # Alarm LED
        GPIO.output(LED_RED, alarm_on)

    GPIO.output(LED_RED, False) # Turn Light off when thread ends

def main():
    # globals
    global g_alarm_on
    global g_alarm_delay

    # Second thread for alarm
    alarm_thread = threading.Thread(target = blink_alarm)

    # State (python's enum)
    class State(Enum):
        off = 1
        standby = 2
        triggered = 3
        settings = 4

    state = State.triggered

    # buttons
    button_a_pressed = False
    button_b_pressed = False
    button_c_pressed = False
    button_d_pressed = False

    # loop bool
    running = True

    while running:
        led_green_on = False
        led_yellow_on = False

        # Button input
        if GPIO.input(BUTTON_A):
            if not button_a_pressed:
                print("Button A")
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
                print("Button B")
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
                print("Button C")
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
                print("Button D")
                # Change blink speed
                if state == State.settings:
                    # swap between 1, 2 and 3 delay
                    g_alarm_delay = g_alarm_delay + 1 if g_alarm_delay < 3 else 1
                    print("Alarm delay:", g_alarm_delay)
                # Turn off program (can't turn on again)
                elif state == State.off:
                    running = False
            button_d_pressed = True
        else:
            button_d_pressed = False

        # Set variables based on states
        # NOTE: Python has no switch
        # Off
        if state == State.off:
            g_alarm_on = False # Turn off second thread for alarm
            led_green_on = True

        # Standby
        elif state == State.standby:
            g_alarm_on = False # Turn off second thread for alarm
            led_yellow_on = True

        # Triggered
        elif state == State.triggered:
            g_alarm_on = True # Turn on second thread for alarm

        # Settings
        elif state == State.settings:
            g_alarm_on = True # Turn on second thread for alarm
            led_green_on = True


        if g_alarm_on and not alarm_thread.isAlive():
            print('Dit > hallo')
            alarm_thread = threading.Thread(target = blink_alarm)
            alarm_thread.daemon = True # Tread dies when program ends
            alarm_thread.start()

        # LEDs
        GPIO.output(LED_GREEN, led_green_on)
        GPIO.output(LED_YELLOW, led_yellow_on)

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
##  Globals  ##
###############
g_alarm_on = False
g_alarm_delay = 1



###############
## Main Loop ##
###############
main()


# Turn every ting off when program closes
GPIO.cleanup()
