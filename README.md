# AffectiveLamp

## Connect the bridge

First visit https://discovery.meethue.com/ to find the bridge IP
returns:
[{"id":"XXX","internalipaddress":"XXX.XXX.X.XXX","port":XXX}]
paste into light/bridge.json and create an .env file with BRIDGE_IP variable = inetrnalipaddress.
run light/create_username.py

## Connect the bulb(s)
Manually follow the steps, when mobile is connected to the same network as the Philips bridge, to add a light

