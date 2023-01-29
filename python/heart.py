"""
  ____  _           ____        _
 |  _ \(_) ___ ___ | __ )  ___ | |_
 | |_) | |/ __/ _ \|  _ \ / _ \| __|
 |  __/| | (_| (_) | |_) | (_) | |_
 |_|   |_|\___\___/|____/ \___/ \__|

 The Pico Bot heart

 By Matthew Page

"""
class Heart:
    """Class to draw a heart on the display and keep track of the rate of the heart"""

    def __init__(self, restingRate, maxRate, fps):
        """Initialise the heart
        restingRate: The resting rate of the heart
        maxRate: The maximum rate of the heart
        fps: The number of frames per second
        """
        self.fps = fps
        self.restingRate = restingRate
        self.maxRate = maxRate
        self.rate = restingRate
        self.counter = 0
        self.quad = 8
        self.colourLight = 0x07E0
        self.colourLight = 0xFFFF
        self.colourDark = 0x0030

    def draw(self, display):
        """Draw the heart on the display
        display: The display to draw on
        """
        if self.counter < 0 or self.counter / self.fps > 1 / ( self.rate / 60 ):

            if self.counter > 0:
                self.quad = int(self.quad / 2)
                if self.quad < 1:
                    self.quad = 8

            if self.counter > 0:
                self.counter = -3
            # Bright on beat
            display.ellipse(120, 120, 118, 118, self.colourLight, False, self.quad)
            display.ellipse(120, 120, 119, 119, self.colourLight, False, self.quad)
            display.ellipse(120, 120, 120, 120, self.colourLight, False, self.quad)
            #display.ellipse(120, 120, 118, 118, 0x0000, True, 15)
                
        else:
            # Dark off beat
            display.ellipse(120, 120, 118, 118, self.colourDark, False, self.quad)
            display.ellipse(120, 120, 119, 119, self.colourDark, False, self.quad)
            display.ellipse(120, 120, 120, 120, self.colourDark, False, self.quad)
            #display.ellipse(120, 120, 118, 118, 0x0000, True, 15)
        
        # Display the heart rate value
        #display.text("{}bpm".format(self.rate), 92, 10, 0x200a)

    def tick(self):
        """Tick the heart counter"""
        self.counter += 1

    def rest(self, rate):
        """Rest the heart / lower the rate
        rate: The rate to lower the heart by
        """
        if self.rate > self.restingRate:
            self.rate -= rate
        elif self.rate < self.restingRate:
            self.rate += 1

    def work(self, rate):
        """Work the heart / increase the rate to a maximum
        rate: The rate to increase the heart by
        """
        self.rate += rate
        self.rate = min(self.rate, self.maxRate)
