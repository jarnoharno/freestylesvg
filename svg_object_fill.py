#  License  : MIT
#  Author   : Jarno Leppänen
#  Date     : 2013-08-26

import os
import re
import bpy
from bpy_extras.object_utils import world_to_camera_view
from freestyle import *
from Functions0D import *
from PredicatesB1D import *
from PredicatesU0D import *
from PredicatesU1D import *
from logical_operators import *
from shaders import *
from parameter_editor import *
from ChainingIterators import *

scene = getCurrentScene()

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

get_shape_list = GetShapeF1D()
def get_shape(curve):
    return get_shape_list(curve)[0]

z_map = {}
def get_z(shape):
    global z_map
    global scene
    z = z_map.get(shape.id.first)
    if z == None:
        o = bpy.data.objects[shape.name]
        z = world_to_camera_view(scene, scene.camera, o.location)[2]
        z_map[shape.id.first] = z
    return z
def get_curve_z(curve):
    return get_z(get_shape(curve))

# sort
class ShapeZ(BinaryPredicate1D):
    def __call__(self, i1, i2):
        return get_curve_z(i1) < get_curve_z(i2)
Operators.sort(ShapeZ())

# shade and write svg
path = re.sub(r'\.blend$|$', '.svg', bpy.data.filepath)
f = open(path, "a")

w = scene.render.resolution_x * scene.render.resolution_percentage / 100
h = scene.render.resolution_y * scene.render.resolution_percentage / 100

shape_map = {}

class ViewShapeColorShader(StrokeShader):
    def shade(self, stroke):
        global shape_map
        shape = GetShapeF1D()(stroke)[0]
        shape = shape.id.first
        item = shape_map.get(shape)
        if item == None:
            material = CurveMaterialF0D()(
                Interface0DIterator(stroke.stroke_vertices_begin()))
            color = material.diffuse[0:3]
            alpha = material.diffuse[3]
            item = ([stroke], color, alpha)
            shape_map[shape] = item
        else:
            item[0].append(stroke)
        for v in stroke:
            v.attribute.color = item[1]

shaders_list = [
    SamplingShader(50),
    ViewShapeColorShader(),
    ConstantThicknessShader(5)
    ]
Operators.create(TrueUP1D(), shaders_list)

def write_fill(item):
    f.write('<path fill-rule="evenodd" fill="#%02x%02x%02x" fill-opacity="%.2f" stroke="none" d="\n'
        % (tuple(map(lambda c: c * 255, item[1])) + (item[2],)))
    for stroke in item[0]:
        points = []
        f.write('M ')
        for v in stroke:
            x, y = v.point
            f.write('%.3f,%.3f ' % (x, h - y))
        f.write('z\n')
    f.write('" />\n')

f.write('<g id="fills">\n')
if len(shape_map) == 1:
    write_fill(next(iter(shape_map.values())))
else:
    for k, item in sorted(shape_map.items(), key = lambda x: -z_map[x[0]]):
        write_fill(item)
f.write('</g>\n')
f.close()
