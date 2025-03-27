from phue import Bridge
import os
from dotenv import load_dotenv
from pathlib import Path
from time import sleep

env_path = Path(__file__).resolve().parent / ".env"
print("Expected .env path:", env_path)

load_dotenv(dotenv_path=env_path)

# Connect to the bridge (press the button first!)
b = Bridge(os.getenv("BRIDGE_IP"))
print("Bridge IP:", os.getenv("BRIDGE_IP"))

# Save the connection so you don’t have to press the button again
b.connect()

print("Connected to Hue Bridge!")

lights = b.lights

"""Color definitions"""
colors = {
    "red": (0.675, 0.322),
    "green": (0.409, 0.518),
    "blue": (0.167, 0.04),
    "white": (0.3227, 0.329),
    "yellow": (0.443, 0.515),
    "purple": (0.35, 0.168),
    "cyan": (0.225, 0.332),
    "pink": (0.2638, 0.1167),
}

for l in lights:
    print(l.name)

# for attr in dir(l):
#     # Filter out built-in attributes if desired
#     if not attr.startswith('__'):
#         print(f"{attr}: {getattr(l, attr)}")

"""     ATTRIBUTES
alert: none
bridge: <phue.Bridge object at 0x104de8b90>
brightness: 254
colormode: xy
colortemp: 367
colortemp_k: 2725
effect: none
hue: 47386
light_id: 1
name: MAUDS LAMP
on: True
reachable: True
saturation: 254
transitiontime: None
type: Extended color light
xy: [0.1614, 0.0515]
"""
for l in lights:
    l.on = True
    l.brightness = 255
    sleep(1)
    l.xy = colors["green"]
    sleep(1)
    l.xy = colors["blue"]
    sleep(1)
    l.xy = colors["red"]
    sleep(1)
    l.xy = colors["pink"]
    # sleep(1)
    # l.on = False
    

