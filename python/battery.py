"""
  ____  _           ____        _
 |  _ \(_) ___ ___ | __ )  ___ | |_
 | |_) | |/ __/ _ \|  _ \ / _ \| __|
 |  __/| | (_| (_) | |_) | (_) | |_
 |_|   |_|\___\___/|____/ \___/ \__|

 The Pico Bot battery monitor and meter

 By Matthew Page

"""
from machine import Pin, ADC
import math

# Battery levels in volts for each dot
BATTERY_LEVELS = (3.5, 3.65, 3.8, 3.95, 4.05)

class BatteryMeter():
    """ Class to read value and draw a battery meter on the display"""

    def __init__(self, pin):
        """ Initialise the battery meter
        pin: The pin to read the battery voltage from
        """
        self.vbat = ADC(Pin(pin))
        self.intervals = 36
        self.distance = 113
        self.red = 0x00F0
        self.yellow = 0x00FF
        self.green = 0x000F

    def draw(self, display):
        """ Draw the battery meter on the display
        display: The display to draw on
        """
        reading = self.read()
        colour = self.red
        if reading > BATTERY_LEVELS[3]:
            colour = self.green
        elif reading > BATTERY_LEVELS[1]:
            colour = self.yellow

        # Draw the black outlines first
        for dot in range(0, 5):
            dot += 16
            angle = math.pi * 2 * (dot / self.intervals) - math.pi / 2
            x = int(display.MID_X + math.cos(angle) * self.distance)
            y = int(display.MID_Y + math.sin(angle) * self.distance)
            display.ellipse(x, y, 20, 20, 0x0000, True)

        # Draw the dots over the top
        for dot in range(0, 5):
            fill = BATTERY_LEVELS[dot] < reading
            dot += 16
            angle = math.pi * 2 * (dot / self.intervals) - math.pi / 2
            x = int(display.MID_X + math.cos(angle) * self.distance)
            y = int(display.MID_Y + math.sin(angle) * self.distance)
            display.ellipse(x, y, 5, 5, colour, fill)

        # Draw the text value
        display.text("{:.2f}v".format(reading), 100, 210, 0xFFFF)

    def read(self):
        """ Read the ADC value and convert to voltage"""
        return self.vbat.read_u16() * 3.3 / 65535 * 2