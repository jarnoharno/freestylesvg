from freestyle import *
from Functions0D import *
from PredicatesB1D import *
from PredicatesU0D import *
from PredicatesU1D import *
from logical_operators import *
from shaders import *
from parameter_editor import *
from ChainingIterators import *
import os

# select
preds = [
    ContourUP1D(),
    NotUP1D(pyIsOccludedByItselfUP1D())
]
upred = join_unary_predicates(preds, AndUP1D)
Operators.select(upred)

# chain
class ViewshapeChainingIterator(ChainingIterator):
    def init(self):
        pass
    def traverse(self, iter):
        global prev_point, last_point
        edge = self.current_edge
        viewshape = self.current_edge.viewshape
        it = AdjacencyIterator(iter)
        while not it.is_end:
            ve = it.object
            if viewshape.id == ve.viewshape.id:
                last_point = ve.last_viewvertex.point_2d
                return ve
            it.increment()
        return None
Operators.bidirectional_chain(ViewshapeChainingIterator())

# sort
Operators.sort(pyZBP1D())

# write svg
_HEADER = """\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"
    width="%d" height="%d" >
"""

scene = freestyle.getCurrentScene()
output_dir = bpy.path.abspath(scene.render.filepath)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
path = os.path.join(output_dir, "test_ft.svg")
f = open(path, "wt")
w = scene.render.resolution_x * scene.render.resolution_percentage / 100
h = scene.render.resolution_y * scene.render.resolution_percentage / 100

f.write(_HEADER % (w, h))

shape_map = {}

# shade
class ViewShapeColorShader(StrokeShader):
    def shade(self, stroke):
        global shape_map
        shape = GetShapeF1D()(stroke)[0].id.first
        item = shape_map.get(shape)
        if item == None:
            material = CurveMaterialF0D()(
                Interface0DIterator(stroke.stroke_vertices_begin()))
            color = material.diffuse[0:3]
            item = ([stroke], color)
            shape_map[shape] = item
        else:
            item[0].append(stroke)
        it = stroke.stroke_vertices_begin()
        while not it.is_end:
            att = it.object.attribute
            att.color = item[1]
            att.alpha = 1
            it.increment()
            
shaders_list = [
    SamplingShader(50),
    ConstantThicknessShader(10),
    ConstantColorShader(1,0,0),
    ViewShapeColorShader()
    ]
Operators.create(TrueUP1D(), shaders_list)

for shape in shape_map.values():
    f.write('<path fill-rule="evenodd" fill="#%02x%02x%02x" stroke="none" d="\n' % 
        tuple(map(lambda c: c * 255, shape[1])))
    for stroke in shape[0]:
        points = []
        f.write('M ')
        for v in stroke:
            x, y = v.point
            f.write('%.3f,%.3f ' % (x, h - y))
        f.write('z\n')
    f.write('" />\n')
f.write('</svg>\n')
f.close()
