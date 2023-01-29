"""
  ____  _           ____        _
 |  _ \(_) ___ ___ | __ )  ___ | |_
 | |_) | |/ __/ _ \|  _ \ / _ \| __|
 |  __/| | (_| (_) | |_) | (_) | |_
 |_|   |_|\___\___/|____/ \___/ \__|

 Pico Bot is a robot that uses the Raspberry Pi Pico and a 1.28" LCD display
 to display a variety of information. It is a work in progress and is
 intended to be a fun project to learn about the Pico and the LCD display.

 By Matthew Page

"""
import utime
import math
from machine import Pin,I2C,PWM,ADC
from display import LCD_1inch28
from sensors import QMI8658
from battery import BatteryMeter
from heart import Heart

# QMI8658 Sensor
I2C_SDA = 6
I2C_SDL = 7

# LCD Display
DC = 8
CS = 9
SCK = 10
MOSI = 11
RST = 12
BL = 25

# Battery
BATTERY_PIN = 29

# Display settings
WIDTH = 240
HEIGHT = 240
MID_X = int(WIDTH / 2)
MID_Y = int(HEIGHT / 2)
FPS = 20
DISPLAY_BRIGHT = 65535
DISPLAY_DIM = 3000

# Bot states
STATE_SLEEPING = 0
STATE_AWAKE = 1

# Eye settings and defaults
EYE_TOP = 75
EYE_WIDTH = 50
EYE_HEIGHT = 40
EYE_SPACING = 10
EYE_CLOSED_HEIGHT = 3
EYE_BALL_WIDTH = 15
EYE_BALL_HEIGHT = 15
EYE_LEFT_X = int(MID_X - ((EYE_WIDTH + EYE_SPACING) / 2))
EYE_RIGHT_X = EYE_LEFT_X + EYE_WIDTH + EYE_SPACING
EYE_LEFT = 0
EYE_RIGHT = 1

# Heart beat settings
HEART_RESTING_RATE = 100
HEART_MAX_RATE = 300

# Graph and bar settings
XYZ_HEIGHT = 50
XYZ_TOP = 130
XYZ_SPACE = 25
XYZ_START = int((WIDTH - (XYZ_SPACE * 4)) / 2)
XYZ_MIN_MAX = ((-0.78, 1.47), (-0.77, 2.2), (-3.06, 2.26), (-512, 495), (-403, 437), (-10, 10))
GRAPH_SAMPLE_RATE = 2              # Frames between sampling
GRAPH_WIDTH = 24                   # Number of points on the graph

# Display modes
MODE_BARS = 0
MODE_GRAPH = 1
MODE_TIME = 150

class Eye():
    def __init__(self, x = EYE_LEFT_X, y = EYE_TOP, position = EYE_LEFT):
        self.position = position
        self.width = EYE_WIDTH
        self.height = EYE_CLOSED_HEIGHT
        self.x = x
        self.y = y
        self.ball = EyeBall(self)

    def draw(self, display):
        display.rect(
            int(self.x - (self.width / 2)),
            int(self.y - (self.height / 2)),
            int(self.width),
            int(self.height),
            display.white)
        self.ball.draw(display)

class EyeBall():
    def __init__(self, eye, x = 0, y = 0, width = EYE_BALL_WIDTH, height = EYE_BALL_HEIGHT):
        self.eye = eye
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, display):
        display.ellipse(
            int(self.eye.x + self.x),
            int(self.eye.y + self.y),
            int(min(self.width / 2, math.floor(self.eye.width / 2)-1)),
            int(min(self.height / 2, math.floor(self.eye.height / 2)-1)),
            display.white,
            True)

def wakeUp():
    global xyzPositionMinMax, state

    state = STATE_AWAKE
    xyzPositionMinMax = [[9999,-9999],[9999,-9999],[9999,-9999],[9999,-9999],[9999,-9999],[9999,-9999]]

# Start graph at zero
xyzGraph = [[0, 0, 0, 0, 0, 0]]

# Maximum and minimum values for each sensor
maxMins = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]

# Start the heart beat at resting rate
heart = Heart(HEART_RESTING_RATE, HEART_MAX_RATE, FPS)

# Start in graph mode
mode = MODE_GRAPH
modeCounter = 0

# Setup the default eyes
leftEye = Eye()
leftEyeTarget = None
rightEye = Eye(x = EYE_RIGHT_X)
rightEyeTarget = None

animationStack = []
timeAwake = 0
frame = 0

battery = BatteryMeter(BATTERY_PIN)

LCD = LCD_1inch28(DC, CS, SCK, MOSI, RST, BL)
LCD.set_bl_pwm(DISPLAY_BRIGHT)
qmi8658 = QMI8658(I2C_SDA, I2C_SDL)
Vbat = ADC(Pin(BATTERY_PIN))
state = STATE_SLEEPING
boredom = 0
boredomMax = 100
zzz = 1

while(True):

    # Read QMI8658 data
    xyz = qmi8658.Read_XYZ()
    xyz[0] = xyz[0] - 1

    # Store max and min values for each sensor
    for i in range(0, 5):
        maxMins[i] = [
            min(maxMins[i][0], xyz[i]),
            max(maxMins[i][1], xyz[i]),
        ]

    # Clear the display
    LCD.fill(0x0000)

    # Tick the heart beat
    heart.tick()

    if state == STATE_AWAKE:

        timeAwake += 1

        # BLINK Animation
        if timeAwake == 100:
            leftEyeTarget = Eye()
            leftEyeTarget.height = 3
        if timeAwake == 105:
            leftEyeTarget = Eye()
            leftEyeTarget.height = EYE_HEIGHT

        if timeAwake == 115:
            leftEyeTarget = Eye()
            leftEyeTarget.height = 10
        if timeAwake == 120:
            leftEyeTarget = Eye()
            leftEyeTarget.height = EYE_HEIGHT

        if timeAwake == 119:
            rightEyeTarget = Eye(x = EYE_RIGHT_X)
            rightEyeTarget.height = 3
        if timeAwake == 125:
            rightEyeTarget = Eye(x = EYE_RIGHT_X)
            rightEyeTarget.height = EYE_HEIGHT

        if timeAwake == 130:
            timeAwake = 0

    # Animate the eyes
    if leftEyeTarget:
        if int(leftEye.height) != int(leftEyeTarget.height):
            if int(leftEye.height) > int(leftEyeTarget.height):
                leftEye.height -= 8
            if int(leftEye.height) < int(leftEyeTarget.height):
                leftEye.height += 8
        else:
            leftEyeTarget = None

    if rightEyeTarget:
        if int(rightEye.height) != int(rightEyeTarget.height):
            if int(rightEye.height) > int(rightEyeTarget.height):
                rightEye.height -= 8
            if int(rightEye.height) < int(rightEyeTarget.height):
                rightEye.height += 8
        else:
            rightEyeTarget = None

    if state == STATE_SLEEPING:

        LCD.set_bl_pwm(DISPLAY_DIM)

        # Returning heart rate to normal
        heart.rest(5)

        #######################################################
        # Draw the ZZZ's
        #######################################################
        if zzz >= 1 and zzz < 2:
            zzzPosition = [150, 20]
        elif zzz >= 2 and zzz < 3:
            zzzPosition = [155, 30]
        elif zzz >= 3:
            zzzPosition = [160, 40]
        LCD.text("Z", zzzPosition[0], EYE_TOP - zzzPosition[1], LCD.white)
        zzz += 0.2
        if zzz > 4:
            zzz = 1

    if state == STATE_AWAKE:
        LCD.set_bl_pwm(DISPLAY_BRIGHT)

        boredom += 1

        # Returning heart rate to normal
        heart.rest(1)

    if xyz[0] > 0.8 or xyz[1] > 1 or xyz[2] > 0.8 or abs(xyz[3]) > 50 or abs(xyz[4]) > 50 or abs(xyz[5]) > 50:

        heart.work(5)

        if state == STATE_SLEEPING:
            leftEyeTarget = Eye()
            leftEyeTarget.height = 40
            rightEyeTarget = Eye(rightEye.x)
            rightEyeTarget.height = 40
            wakeUp()

        boredom = 0

    if boredom > boredomMax and heart.rate <= heart.restingRate:
        leftEyeTarget = Eye()
        leftEyeTarget.height = EYE_CLOSED_HEIGHT
        rightEyeTarget = Eye(rightEye.x)
        rightEyeTarget.height = EYE_CLOSED_HEIGHT
        boredom = 0
        state = 0

    #######################################################
    # XYZ Readings
    #######################################################

    if state == STATE_AWAKE:

        graphData = []

        # Each of the 5 readings
        for i in range(0, 5):

            if i == 0:
                colour = LCD.red
            elif i == 1:
                colour = LCD.green
            elif i == 2:
                colour = LCD.blue
            elif i == 3:
                colour = LCD.yellow
            elif i == 4:
                colour = LCD.purple

            colour = LCD.white

            # Calculate the scale based on height and max - min
            scale = XYZ_HEIGHT / (XYZ_MIN_MAX[i][1] - XYZ_MIN_MAX[i][0])

            # Position on the line scaled correctly: ( reading - min reading ) * scale
            position = int(abs((xyz[i] - XYZ_MIN_MAX[i][0]) * scale))

            graphData.append(position)

            # Remember max and min positions (not the reading, just the position)
            xyzPositionMinMax[i][0] = min(xyzPositionMinMax[i][0], position)
            xyzPositionMinMax[i][1] = max(xyzPositionMinMax[i][1], position)

            if mode == MODE_BARS:
                # Draw the center line
                LCD.line(XYZ_START + (XYZ_SPACE * i), XYZ_TOP, XYZ_START + (XYZ_SPACE * i), XYZ_TOP + XYZ_HEIGHT, colour)

                # Draw the max and min values
                LCD.line(XYZ_START + (XYZ_SPACE * i) - 2, XYZ_TOP + xyzPositionMinMax[i][0], XYZ_START + (XYZ_SPACE * i) + 2, XYZ_TOP + xyzPositionMinMax[i][0], colour)
                LCD.line(XYZ_START + (XYZ_SPACE * i) - 2, XYZ_TOP + xyzPositionMinMax[i][1], XYZ_START + (XYZ_SPACE * i) + 2, XYZ_TOP + xyzPositionMinMax[i][1], colour)

                # Draw the current value
                LCD.ellipse(XYZ_START + (XYZ_SPACE * i), XYZ_TOP + position, 5, 2, colour, True)

        # Add to graph data
        if frame % GRAPH_SAMPLE_RATE == 0:
            xyzGraph.append(graphData)

        # Remove old data
        if len(xyzGraph) > GRAPH_WIDTH:
            xyzGraph.pop(0)

        # Draw the graph
        if mode == MODE_GRAPH:
            w = int(WIDTH / GRAPH_WIDTH)
            for i in range(0, 5):
                lastPosition = int(xyzGraph[0][i])
                for x in range(0, len(xyzGraph) - 1):
                    LCD.line(x * w, (i * 10) + XYZ_TOP + lastPosition - 20, (x + 1) * w, (i * 10) + XYZ_TOP + int(xyzGraph[x][i]) - 20, LCD.white)
                    lastPosition = int(xyzGraph[x][i])

        # Flip the mode
        if modeCounter == MODE_TIME:
            modeCounter = 0
            if mode == MODE_BARS:
                mode = MODE_GRAPH
            else:
                mode = MODE_BARS

        modeCounter += 1

    # Draw the heart beat
    heart.draw(LCD)

    # Display the battery reading
    battery.draw(LCD)

    # Display the eyes
    leftEye.draw(LCD)
    rightEye.draw(LCD)

    LCD.show()
    frame += 1
    utime.sleep(1 / FPS)
