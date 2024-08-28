import pyautogui
import pygetwindow as gw
from pynput import keyboard
from time import time, perf_counter
from dataclasses import dataclass
import os
from collections import Counter
import math
import random
from functools import wraps
import winsound
import pytesseract
import re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def makeAlert():
    # Frequency and duration in milliseconds
    frequency = 1000  # 1000 Hz
    duration = 500    # 500 milliseconds (0.5 seconds)

    # Play the sound
    winsound.Beep(frequency, duration)


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        # print(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper

@dataclass
class C:
    x: int
    y: int


start_time=time()

# Get the window by title
window = gw.getWindowsWithTitle("BlueStacks")[0]

# Get window coordinates and size
left = window.left
top = window.top
right = window.right
bottom = window.bottom
width = window.width
height = window.height

print(f"Window coordinates: (left: {left}, top: {top}, right: {right}, bottom: {bottom})")
print(f"Window size: (width: {width}, height: {height})")

win = C(window.left, window.top)
picker_block = [C(511, 500),
                C(571, 500),
                C(631, 500)]


def defineOctMap():
    x=505
    y=294
    f=32
    return [[C(x,y+f*0), C(x+f*1,y-f*0.5), C(x+f*2,y-f*1), None,             None          ],
            [C(x,y+f*1), C(x+f*1,y+f*0.5), C(x+f*2,y+f*0), C(x+f*3,y-f*0.5), None          ],
            [C(x,y+f*2), C(x+f*1,y+f*1.5), C(x+f*2,y+f*1), C(x+f*3,y+f*0.5), C(x+f*4,y+f*0)],
            [None,       C(x+f*1,y+f*2.5), C(x+f*2,y+f*2), C(x+f*3,y+f*1.5), C(x+f*4,y+f*1)],
            [None,       None,             C(x+f*2,y+f*3), C(x+f*3,y+f*2.5), C(x+f*4,y+f*2)]]

def get_most_common_color(screenshot, x, y, radius=16):
    # List to hold the colors found within the radius
    colors = []

    # Iterate over the square bounding box
    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            # Check if the point is within the circle (radius)
            if math.sqrt((i - x) ** 2 + (j - y) ** 2) <= radius:
                # Get the color of the pixel
                color = screenshot.getpixel((i, j))
                if color != (31,31,31):
                    colors.append(color)

    # Count the frequency of each color
    color_counts = Counter(colors)

    # Find the most common color
    if len(color_counts) > 0:
        most_common_color = color_counts.most_common(1)[0][0]
    else:
        most_common_color = (31,31,31)

    return most_common_color

octMap = defineOctMap()


def drugAndDrop(start: C, end: C):
    e = 32
    global win
    pyautogui.moveTo(win.x + start.x, win.y + start.y,duration=0)
    pyautogui.mouseDown(duration=0)
    pyautogui.moveTo(win.x + end.x, win.y + end.y + e,duration=0)
    pyautogui.mouseUp(duration=0)


def elapsed_time():
    global start_time
    return time() - start_time


def on_click(x, y, button, pressed):
    if pressed:
        global win
        print(f'pressed x:{x-win.x} y:{y-win.y} time:{elapsed_time()}')

def raise_exception():
    os._exit(0)

def on_press(key):
    try:
        print(f'key pressed {key.char} time:{elapsed_time()}')
    except:
        print(f'special key pressed {key} time:{elapsed_time()}')

def on_release(key):
    try:
        print(f'key released {key.char} time:{elapsed_time()}')
    except:
        print(f'special key released {key} time:{elapsed_time()}')

    if key == keyboard.Key.alt_gr:
        raise_exception()

def runListeners():
    
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    #listener.join()

def main():
    runListeners()

if __name__ == "__main__":
    main()


def isWhite(c):
    return c == (229,224,224)

@timeit
def readColorMap(screenshot):
    global win
    global octMap
    result = [[None,None,None,None,None] for _ in range(5)]
    for i in range(0,5):
        for j in range(0,5):
            if octMap[i][j] is not None:
                result[i][j] = get_most_common_color(screenshot, win.x + octMap[i][j].x, win.y + int(octMap[i][j].y))
    return result

@timeit
def readPicker(screenshot):
    global win
    global picker_block
    result = [None, None, None]
    for i in range(0,3):
        result[i] = get_most_common_color(screenshot, win.x + picker_block[i].x, win.y + picker_block[i].y)
    return result

def sameColor(c1, c2i, c2j):
    if c2i in range(0,5) and c2j in range(0,5):
        c2 = colMap[c2i][c2j]
        if c1 is not None and c2 is not None:
            if c1 == c2:
                return True
    return False

def goBack():
    click(22,79)
    click(446,411)

@timeit
def findSuitable(screenshot):
    global picker_block
    pickerCol = readPicker(screenshot)
    
    if isWhite(pickerCol[0]) and isWhite(pickerCol[1]) and isWhite(pickerCol[2]):
        goBack()
        return False
    
    for p in range(0,3):
        picker = pickerCol[p]
        for i in range(0,5):
            for j in range(0,5):        
                if octMap[i][j] is not None and isWhite(colMap[i][j]):
                    if (sameColor(picker, i-1, j)
                        or sameColor(picker, i+1,j)
                        or sameColor(picker, i,j-1)
                        or sameColor(picker, i,j+1)
                        or sameColor(picker, i-1,j-1)
                        or sameColor(picker, i+1,j+1)
                        ):
                        drugAndDrop(picker_block[p], octMap[i][j])
                        return True
    return False

@timeit
def findRandom():
    global picker_block
    global octMap
    global colMap
    
    choices = []
    for i in range(0,5):
        for j in range(0,5):
            if octMap[i][j] is not None and isWhite(colMap[i][j]):
                choices.append(octMap[i][j])
    if len(choices) > 0:
        item = random.choice(choices)
        drugAndDrop(picker_block[0], item)
        return True
    
    return False

def click(x, y):
    global win
    pyautogui.click(win.x+x, win.y+y,duration=1)

stuck = 0

def extractResult():
    global win
    pyautogui.sleep(1)
    screenshot = pyautogui.screenshot(region=(win.x+300, win.y+300, 600, 250))
    extracted_text = pytesseract.image_to_string(screenshot)
    numbers = re.findall(r'[\d,]+', extracted_text)
    if len(numbers) > 0:
        makeAlert()
        screenshot.save('screenshot.png')
        print("Result: ", numbers, datetime.now())

def restart():
    global stuck
    stuck += 1
    if stuck > 3:
        makeAlert()
    if stuck > 6:
        goBack()
    extractResult()
        
    click(354, 470)
    click(421, 321)
    click(434, 491)
    
    pyautogui.sleep(0.5)

print("start time: ", datetime.now())
while True:
    screenshot = pyautogui.screenshot()
    colMap = readColorMap(screenshot)
    
    
    
    # drop to suitable slot
    if findSuitable(screenshot) == False:
        # drop to random slot
        if findRandom() == False:
            # try to restart
            restart()
    else:
        stuck = 0
        pyautogui.sleep(0.3)
                