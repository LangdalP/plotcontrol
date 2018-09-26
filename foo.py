import sys
from pyaxidraw import axidraw

### AxiDraw setup
ad = axidraw.AxiDraw() # Initialize class

ad.interactive()            # Enter interactive mode
ad_connected = ad.connect()    # Open serial port to AxiDraw 

if not ad_connected:
    sys.exit() # end script

ad.goto(0,0)
ad.moveto(2,2)
ad.goto(0,0)


ad.disconnect()
