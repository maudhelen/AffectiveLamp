from phue import Bridge

# Replace with your Hue Bridge IP
BRIDGE_IP = "192.168.1.102"

# Connect to the bridge (press the button first!)
b = Bridge(BRIDGE_IP)

# Save the connection so you don’t have to press the button again
b.connect()

print("Connected to Hue Bridge!")

#Get dictionary with lights
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
}

# Print light names
for l in lights:
    print(l)

# Set brightness of each light to 127
for l in lights:
    l.on = True
    l.brightness = 255
    l.xy = colors["green"]
