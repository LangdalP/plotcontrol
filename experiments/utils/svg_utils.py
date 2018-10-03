from svgpathtools import parse_path, smoothed_path, disvg

def line_tuple_to_command(line_tuple):
    return f'l {line_tuple[0]} {line_tuple[1]}'

def create_path(start_x, start_y, relative_lines):
    relative_line_commands = map(line_tuple_to_command, relative_lines)
    relative_lines_string = ' '.join(relative_line_commands)
    full_path = f'M {start_x} {start_y} {relative_lines_string}'
    path = parse_path(full_path)
    # smoothened = smoothed_path(path)
    return path

def save_and_open_svg(path):
    disvg(path)

