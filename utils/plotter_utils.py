import sys
from pyaxidraw import axidraw


def init_plotter_interactive(spd, spu):
    ad = axidraw.AxiDraw()
    ad.interactive()
    ad_connected = ad.connect()
    if not ad_connected:
        return None
    ad.options.units = 1 # Bruker cm i stedet for inches
    ad.options.speed_pendown = spd
    ad.options.speed_penup = spu
    ad.update()
    print(f'Fant trolig plotter...')
    return ad

def disconnect_serial(plotter):
    plotter.disconnect()

def start_svg_plot(plotter, plot_fname):
    plotter.plot_setup(plot_fname)
    plotter.plot_run()

def go_back_to_interactive_mode(plotter):
    plotter.interactive()
    plotter_connected = plotter.connect()
    plotter.options.units = 1
    plotter.update()
