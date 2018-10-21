import os
import random
import uuid
from svgpathtools import svg2paths, wsvg, disvg
from svgpathtools.paths2svg import big_bounding_box


def align_components(eyes, nose, mouth, height):
    nose_min, nose_max, _, _ = big_bounding_box(nose)
    eyes_min, eyes_max, _, _ = big_bounding_box(eyes)
    _, mouth_max, _, _ = big_bounding_box(mouth)

    nose_height = nose_max - nose_min
    nose_top = (height + nose_height) / 2
    nose_delta = nose_top - nose_max

    eyes_height = eyes_max - eyes_min
    eyes_top = nose_top + eyes_height
    eyes_delta = eyes_top - eyes_max

    mouth_top = nose_top - nose_height
    mouth_delta = mouth_top - mouth_max

    face = []
    list(map(lambda path: face.append(path.translated(complex(nose_delta, 0))), nose))
    list(map(lambda path: face.append(path.translated(complex(eyes_delta, 0))), eyes))
    list(map(lambda path: face.append(path.translated(complex(mouth_delta, 0))), mouth))

    return face


def get_paths_from_directory(dirpath, feature_type):
    svgs = list(filter(lambda fi: fi.endswith(".svg"), os.listdir(dirpath)))
    chosen_svg = random.choice(svgs)
    paths, _ = svg2paths(dirpath + chosen_svg)
    return paths

def get_svg_attributes():
    return {
        'xmlns': u'http://www.w3.org/2000/svg',
        u'baseProfile': u'full',
        u'xmlns:ev': u'http://www.w3.org/2001/xml-events',
        u'width': u'240mm',
        u'height': u'160mm',
        u'version': u'1.1',
        u'xmlns:xlink': u'http://www.w3.org/1999/xlink',
        u'viewBox': u'3.5 3.5 24 16'}

def generate_face():
    height = 30
    folder = './input'

    eyepaths = get_paths_from_directory(folder + '/eyes/', 'EYES')
    nosepaths = get_paths_from_directory(folder + '/nose/', 'NOSE')
    mouthpaths = get_paths_from_directory(folder + '/mouth/', 'MOUTH')

    facepaths = align_components(eyepaths, nosepaths, mouthpaths, height)
    filename = 'output/' + uuid.uuid4().hex + '.svg'

    wsvg(facepaths, filename=filename, svg_attributes=get_svg_attributes())

    return filename


if __name__ == "__main__":
    generate_face()