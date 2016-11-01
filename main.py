###############
##  Imports  ##
###############
from enum import Enum

###############
## Constands ##
###############
# Buttons
BUTTON_A_PIN = 1
BUTTON_B_PIN = 2
BUTTON_C_PIN = 3
BUTTON_D_PIN = 4
# LEDs
LED_GREEN = 5
LED_YELLOW = 6
LED_RED = 7

###############
## Functions ##
###############
def ask_pin_code():
    pin = input('Pin please: ')
    return pin == '1337'

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

# LEDs
led_green_on = False
led_yellow_on = False
led_red_on = False
blink = False

###############
## Main Loop ##
###############
while True:
    led_green_on = False
    led_yellow_on = False
    led_red_on = False
    blink = False

    # INPUT
    optie = input('A, B, C, D? ')
    if optie == 'A' or optie == 'a':
        button_a_pressed = True
        button_b_pressed = False
        button_c_pressed = False
        button_d_pressed = False
    if optie == 'B' or optie == 'b':
        button_a_pressed = False
        button_b_pressed = True
        button_c_pressed = False
        button_d_pressed = False
    if optie == 'C' or optie == 'c':
        button_a_pressed = False
        button_b_pressed = False
        button_c_pressed = True
        button_d_pressed = False
    if optie == 'D' or optie == 'd':
        button_a_pressed = False
        button_b_pressed = False
        button_c_pressed = False
        button_d_pressed = True

    # LEDs
    if led_green_on:
        print('Green on')
    if led_yellow_on:
        print('Yellow on')
    if led_red_on:
        print('Red on')



    print(state)

    # Off
    if state == State.off:
        # TODO: Turn on LED_GREEN
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
        # TODO: Turn on LED_YELLOW
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
        # TODO: Blink LED_RED
        led_red_on = True
        print('Triggered')

        if button_b_pressed:
            if ask_pin_code():
                state = State.standby
                continue

    # Settings
    elif state == State.Settings:
        # TODO: Blink LED_RED and Turn on LED_GREEN
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
