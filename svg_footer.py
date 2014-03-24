#  License  : MIT
#  Author   : Jarno Leppänen, Francesco Fantoni
#  Date     : 2014-03-24

import re
import bpy

_FOOTER = """\
</svg>
"""

path = re.sub(r'\.blend$|$', '.svg', bpy.data.filepath)
f = open(path, "a")
f.write(_FOOTER)
f.close()
