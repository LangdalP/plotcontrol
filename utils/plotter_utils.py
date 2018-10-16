import sys
from pyaxidraw import axidraw

def init_plotter_interactive():
    ad = axidraw.AxiDraw()
    ad.interactive()
    ad_connected = ad.connect()
    if not ad_connected:
        return None
    ad.options.units = 1 # Bruker cm i stedet for inches
    ad.update()
    print(f'Fant trolig plotter...')
    return ad
