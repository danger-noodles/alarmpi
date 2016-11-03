###############
##  Imports  ##
###############
from enum import Enum
import threading
import RPi.GPIO as GPIO
import time


###############
## Constants ##
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

# DIGIT DISPLAY
CHARACTERS = {
    ' ': (0,0,0,0,0,0,0,0),
    '0': (1,1,0,1,0,1,1,1),
    '1': (0,0,0,1,0,1,0,0),
    '2': (1,1,0,0,1,1,0,1),
    '3': (0,1,0,1,1,1,0,1),
    '4': (0,0,0,1,1,1,1,0),
    '5': (0,1,0,1,1,0,1,1),
    '6': (1,1,0,1,1,0,1,1),
    '7': (0,0,0,1,0,1,0,1),
    '8': (1,1,0,1,1,1,1,1),
    '9': (0,1,0,1,1,1,1,1),
    'B': (1,1,0,1,1,0,1,0),
    'O': (1,1,0,1,0,1,1,1),
    'E': (1,1,0,0,1,0,1,1),
    'F': (1,0,0,0,1,0,1,1),
    'S': (0,1,0,1,1,0,1,1),
    'A': (1,0,0,1,1,1,1,1),
    '-': (1,1,1,1,1,1,1,1)
}


# GPIO ports for the 7seg pins
SEGMENTS = (26, 19, 13, 6, 5, 9, 27, 17)
# GPIO ports for the digit 0-3 pins
DIGITS = (4, 22, 10, 11)


###############
## Functions ##
###############
# aks_and_validate_pin_code
# Aks pin code using the input method and the return if the pin code is correct
#
# @return Bool || If pin code is correct or not
def ask_and_validate_pin_code():
    pin = input('Pin please: ')
    return int(pin) == PIN_CODE


# display_seg
# Displays string on the 7 segment 4 digit display
#
# @param string display_string || The string that needs to be displayed, only char in the CHARACTERS constant allowed
# @return void
def display_seg(display_string):
    for digit in range(4):
        GPIO.output(SEGMENTS, (CHARACTERS[display_string[digit]]))
        GPIO.output(DIGITS[digit], 0)
        time.sleep(0.001)
        GPIO.output(DIGITS[digit], 1)


# blink_alarm
# Blinks alarm, 7 segment 4 digit display and activates speaker
# This function is used a a secondary thread
#
# @return void
def blink_alarm():
    print('Alarm Thread')

    # Globals
    global g_alarm_on
    global g_alarm_delay

    # Alarm
    alarm_time = time.time()
    alarm_on = False

    # Speaker
    speaker_wait_time = 1.0 / 2000 / 2

    while g_alarm_on:
        # blink timer
        # if current time - old time >= alarm delay
        if time.time() - alarm_time >= g_alarm_delay:
            alarm_time = time.time() # reset timer
            alarm_on = not alarm_on # invert alarm bool

        if alarm_on:
            # Display Boef on 7 segment 4 digit display
            display_seg('BOEF')

            # Make speaker bleep
            GPIO.output(SPEAKER_PIN, True)
            time.sleep(speaker_wait_time)
            GPIO.output(SPEAKER_PIN, False)
            time.sleep(speaker_wait_time)
        else:
            display_seg('    ')

        # Alarm LED
        GPIO.output(LED_RED, alarm_on)

    GPIO.output(LED_RED, False) # Turn Light off when thread ends
    display_seg('    ') # Clear display
    print('Alarm Thread killed')


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

    state = State.off # Default (starting) state is off

    # buttons
    button_a_pressed = False
    button_b_pressed = False
    button_c_pressed = False
    button_d_pressed = False

    # loop bool
    running = True

    # MAIN LOOP
    while running:
        led_green_on = False
        led_yellow_on = False

        # Button input
        # Check if the button is pressed and set button_a_pressed if it is
        # We do this so we can check if the button is released and the action is not fired multiple times if
        # the button is not released
        # We use This logic for every button

        # Button A
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

        # Button B
        if GPIO.input(BUTTON_B):
            if not button_b_pressed:
                print("Button B")
                if ask_and_validate_pin_code():
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

        # Button C
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

        # Button D
        if GPIO.input(BUTTON_D):
            if not button_d_pressed:
                print("Button D")
                # Change blink speed
                if state == State.settings:
                    # swap between 1, 2 and 3 second delay
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

        # Do not create thread if the old one is still alive
        if g_alarm_on and not alarm_thread.isAlive():
            # We can't reuse the old thread so we need to create a new one
            alarm_thread = threading.Thread(target = blink_alarm)
            alarm_thread.daemon = True # Tread dies when program ends
            alarm_thread.start()

        # LEDs
        GPIO.output(LED_GREEN, led_green_on)
        GPIO.output(LED_YELLOW, led_yellow_on)


###############
##    Init   ##
###############
# Set the GPIO mode
GPIO.setmode(GPIO.BCM)
# Turn of warnings to keep the console clean
GPIO.setwarnings(False)

# LEDS
GPIO.setup(LED_RED, GPIO.OUT, initial = False)
GPIO.setup(LED_YELLOW, GPIO.OUT, initial = False)
GPIO.setup(LED_GREEN, GPIO.OUT, initial = False)

# BUTTONS
GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_C, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_D, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# SPEAKER
GPIO.setup(SPEAKER_PIN, GPIO.OUT)

# DIGIT DISPLAY
GPIO.setup(SEGMENTS, GPIO.OUT, initial = 0)
GPIO.setup(DIGITS, GPIO.OUT, initial = 1)


###############
##  Globals  ##
###############
g_alarm_on = False
g_alarm_delay = 1



###############
## Main Loop ##
###############
main()

# Turn everything off when program closes
GPIO.cleanup()
