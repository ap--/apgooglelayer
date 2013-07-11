
import array
import cairo
import requests
import StringIO
from PIL import Image
from gi.repository import Pango, PangoCairo


def pil_from_url(url):
    imdata = requests.get(url).content
    return Image.open(StringIO.StringIO(imdata))


def cairo_ImageSurface_from_pil(im):
    arr = array.array('B', im.tostring('raw', 'BGRA'))
    narr = array.array('B')
    for r,g,b,a in zip(*[arr[i::4] for i in range(4)]):
        A = a/255.
        narr.extend((int(r*A), int(g*A), int(b*A), a))
    return cairo.ImageSurface.create_for_data(narr,
                cairo.FORMAT_ARGB32, im.size[0], im.size[1])


