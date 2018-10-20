from svgpathtools import parse_path, smoothed_path, disvg, wsvg

def line_tuple_to_command(line_tuple):
    return f'L {line_tuple[0]} {line_tuple[1]}'

def create_full_paths(paths):
    svg_paths = []
    for path in paths:
        p = create_path(path)
        if p:
            svg_paths.append(p)
    if len(svg_paths):
        relative_lines_string = ' '.join(svg_paths)
        path = parse_path(relative_lines_string)
        # smoothened = smoothed_path(path)
        return path
    return False


def create_path(relative_lines):

    if len(relative_lines):
        relative_line_commands = map(line_tuple_to_command, relative_lines)
        relative_lines_string = ' '.join(relative_line_commands)
        (x,y) = relative_lines [0]
        return f'M {x} {y} {relative_lines_string} '
        return ""
    print("empty path")
    return ""


def save_svg(svg_paths, file_path):
    wsvg(svg_paths, filename=file_path)

def save_and_open_svg(path):
    disvg(path)
