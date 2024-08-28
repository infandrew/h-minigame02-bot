from pynput import mouse
from datetime import datetime
import pygetwindow as gw
from dataclasses import dataclass

@dataclass
class C:
    x: int
    y: int

# Get the window by title
window = gw.getWindowsWithTitle("BlueStacks")[0]

win = C(window.left, window.top)

def on_click(x, y, button, pressed):
    if pressed:
        global win
        print(f'pressed x:{x-win.x} y:{y-win.y} time:{datetime.now()}')

def runListeners():
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    mouse_listener.wait()
    mouse_listener.join()

def main():
    runListeners()

if __name__ == "__main__":
    main()
