#  License  : MIT
#  Author   : Jarno Leppänen, Francesco Fantoni
#  Date     : 2014-03-24

import re
import bpy
import os
from freestyle import *
from freestyle.functions import *
from freestyle.predicates import *
from freestyle.types import *
from freestyle.shaders import *
from parameter_editor import *
from freestyle.chainingiterators import *

_FOOTER = """\
</svg>
"""

scene = getCurrentScene()
current_frame = scene.frame_current

path = re.sub(r'\.blend$|$', '%06d.svg' % current_frame, bpy.data.filepath)
f = open(path, "a")
f.write(_FOOTER)
f.close()
