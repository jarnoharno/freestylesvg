#  License  : MIT
#  Author   : Jarno Leppänen
#  Date     : 2013-08-26

import re
import bpy

_FOOTER = """\
</svg>
"""

path = re.sub(r'\.blend$|$', '.svg', bpy.data.filepath)
f = open(path, "a")
f.write(_FOOTER)
f.close()
