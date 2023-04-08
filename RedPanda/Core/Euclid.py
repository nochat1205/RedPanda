import math
import operator

from .data import RP_TOLERANCE
from OCC.Core.gp import (
    gp_Vec,
    gp_Pnt,
    gp_Dir,
    gp_Trsf,
    gp_Ax1,
    gp_Quaternion,
    gp_Pnt2d,
    gp_XYZ,
    gp_Ax3
)
from OCC.Core.TColgp import TColgp_Array1OfPnt

__all__ = [
    'RP_Pnt',
    'RP_Vec',
    'RP_Dir',
    'RP_Ax1',
    'RP_Trsf',
    'RP_Quaternion',
    'RP_Pnt_Array',
    'RP_Pnt2d',
    'RP_XYZ'
]

#TODO:
def point_equal(self:gp_Pnt, pnt):
    return self.IsEqual(pnt, RP_TOLERANCE)

def point_to_vector(self):
    return gp_Vec(self.XYZ())

def vector_to_point(self):
    return gp_Pnt(self.XYZ())

def dir_to_vec(self):
    return gp_Vec(self)


def vec_to_dir(self):
    return gp_Dir(self)


def add_vector_to_point(self, vec):
    return (self.as_vec() + vec).as_pnt()


def gp_Pnt_get_state(self):
    """pack as a tuple

    used for copying / serializing the instance
    """
    return self.XYZ().Coord()


def gp_Pnt_set_state(self, state):
    """unpack tuple and return instance...

    used for copying / serializing the instance
    """
    self.__init__(*state)


def gp_Pnt_equal(self, other):
    return self.IsEqual(other, RP_TOLERANCE)


def gp_pnt_print(self):
    x = self.X()
    y = self.Y()
    z = self.Z()
    return "< gp_Pnt: {0}, {1}, {2} >".format(x, y, z)


def gp_vec_print(self):
    x = self.X()
    y = self.Y()
    z = self.Z()
    magn = self.Magnitude()
    return "< gp_Vec: {0}, {1}, {2}, magnitude: {3} >".format(x, y, z, magn)


def gp_ax1_print(self):
    pX, pY, pZ = self.Location().Coord()
    dX, dY, dZ = self.Direction().Coord()
    return "< gp_Ax1: location: {pX}, {pY}, {pZ}, direction: {dX}, {dY}, {dZ} >".format(
        **vars()
    )


def gp_trsf_print(self):
    _f = lambda x: [self.Value(x, i) for i in range(1, 5)]
    a, b, c, d = _f(1)
    e, f, g, h = _f(2)
    i, j, k, l = _f(3)
    return "< gp_Trsf:\n {a:.3f}, {b:.3f}, {c:.3f}, {d:.3f}\n {e:.3f}, {f:.3f}, {g:.3f}, {h:.3f}\n {i:.3f}, {j:.3f}, {k:.3f}, {l:.3f} >".format(
        **vars()
    )


def gp_quat_print(self):
    w, x, y, z = self.W(), self.X(), self.Y(), self.Z()
    vec = gp_Vec()
    angle = math.degrees(self.GetVectorAndAngle(vec))
    return "< gp_Quaternion: w:{w}, x:{x}, y:{y}, z:{z} >\nvector:{vec} angle:{angle}".format(
        **vars()
    )


def _apply(pnt, other, _operator):
    if isinstance(other, gp_Pnt):
        return gp_Pnt(*map(lambda x: _operator(*x), zip(pnt.Coord(), other.Coord())))
    else:
        return gp_Pnt(*map(lambda x: _operator(x, other), pnt.Coord()))

def gp_pnt_add(self, other):
    return _apply(self, other, operator.add)

def gp_pnt_sub(self, other):
    return _apply(self, other, operator.sub)

def gp_pnt_mul(self, other):
    return _apply(self, other, operator.mul)

def gp_pnt_div(self, other):
    return _apply(self, other, operator.div)

# easier conversion between data types
gp_Vec.as_pnt = vector_to_point
gp_Pnt.as_vec = point_to_vector
gp_Pnt.add_vec = add_vector_to_point

gp_Dir.as_vec = dir_to_vec
gp_Vec.as_dir = vec_to_dir
# for copying / serializing
gp_Pnt.__getstate__ = gp_Pnt_get_state
gp_Pnt.__setstate__ = gp_Pnt_set_state
gp_Vec.__getstate__ = gp_Pnt_get_state
gp_Vec.__setstate__ = gp_Pnt_set_state
# equality, not identity comparison
gp_Pnt.__eq__ = gp_Pnt_equal
# print gp_Pnt() should return something informative...
gp_Vec.__repr__ = gp_vec_print
gp_Vec.__str__ = gp_vec_print
gp_Pnt.__repr__ = gp_pnt_print
gp_Pnt.__str__ = gp_pnt_print
gp_Ax1.__repr__ = gp_ax1_print
gp_Ax1.__str__ = gp_ax1_print
gp_Trsf.__repr__ = gp_trsf_print
gp_Trsf.__str__ = gp_trsf_print
gp_Quaternion.__repr__ = gp_quat_print
gp_Quaternion.__str__ = gp_quat_print
gp_Pnt.__eq__ = point_equal
gp_Pnt.__add__ = gp_pnt_add
gp_Pnt.__sub__ = gp_pnt_sub
gp_Pnt.__mul__ = gp_pnt_mul
gp_Pnt.__div__ = gp_pnt_div

RP_Pnt = gp_Pnt
RP_Vec = gp_Vec
RP_Dir = gp_Dir
RP_Ax1 = gp_Ax1
RP_Ax3 = gp_Ax3
RP_Trsf = gp_Trsf
RP_Pnt2d = gp_Pnt2d
RP_XYZ = gp_XYZ
RP_Quaternion = gp_Quaternion
RP_Pnt_Array = TColgp_Array1OfPnt
