import svgwrite
from svgpathtools import parse_path, smoothed_path, disvg

# TODO: Remove
import time

# Global state, fyfy
relative_lines = []
svg_drawing = svgwrite.Drawing('foo.svg', profile='tiny')

def add_line(rel_x, rel_y):
    global relative_lines
    relative_lines.append((rel_x, rel_y))

def create_path(start_x, start_y):
    relative_line_commands = map(lambda xy_tuple: f'l {xy_tuple[0]} {xy_tuple[1]}', relative_lines)
    relative_lines_string = ' '.join(relative_line_commands)
    full_path = f'M {start_x} {start_y} {relative_lines_string}'
    path = parse_path(full_path)
    smoothened = smoothed_path(path)
    return smoothened

def save_and_open_svg(path):
    disvg(path)

