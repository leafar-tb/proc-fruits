import bpy
import mathutils
import math
import random

from math import pi as PI
from mathutils import Vector
from .spline import HermiteInterpolator, screw
from .util import optional, makeDiffuseMaterial, MeshMerger
from .evolution import Evolvable
from .notnum import linspace


class FlowerResidueProps:
    # prefix fr_ for flower residue and to avoid name clashes
    
    fr_present = bpy.props.BoolProperty(
        name        = "Has flower residue",
        description = "Adds some decorations that look like the remains of the flower",
        default     = True
    )
    
    fr_openingAngle = bpy.props.FloatProperty(
        name        = "Residue Angle",
        description = "Where the petal remains should point",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.1*PI, soft_max   = .25*PI
    )
    
    fr_radius = bpy.props.FloatProperty(
        name        = "Flower Residue Position",
        description = "Where to place the FR along the fruit",
        default     = .2,
        min         = 0,
        soft_max    = .05
    )
    
    fr_length = bpy.props.FloatProperty(
        name        = "Flower Residue Length",
        description = "Length of the FR, relative to fruit size",
        default     = .2,
        min         = 0,
        soft_min    = 0.01, soft_max     = .1
    )
    
    fr_petals = bpy.props.IntProperty(
        name        = "Num Petals",
        description = "Number of petal remains",
        default     = 5,
        min         = 3,
        soft_max    = 13
    )

class FruitProperties(FlowerResidueProps):
        
    radius = bpy.props.FloatProperty(
        name        = "Width",
        description = "Width of the fruit",
        default     = .2,
        min         = 0,
        soft_min    = 0.01, soft_max     = .5
    )
    
    length = bpy.props.FloatProperty(
        name        = "Length",
        description = "Length of the fruit",
        default     = .5,
        min         = 0,
        soft_min    = 0.05, soft_max     = 1
    )
    
    symmetry = bpy.props.IntProperty(
        name        = "Symmetry",
        description = "The fruit will have this many bulges",
        default     = 2,
        min         = 0,
        soft_max    = 10
    )
    
    upperAngle = bpy.props.FloatProperty(
        name        = "Upper angle",
        description = "How broad or narrow the fruit is at the top",
        subtype     = 'ANGLE',
        default     = 0,
        min         = -PI/2,
        soft_max    = .375*PI
    )
    
    lowerAngle = bpy.props.FloatProperty(
        name        = "Lower angle",
        description = "How broad or narrow the fruit is at the bottom",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.375*PI, soft_max    = .375*PI,
    )
    
    colour = bpy.props.FloatVectorProperty(
        name        = "Colour",
        description = "Colour of the fruit",
        size        = 3,
        subtype     = 'COLOR',
        default     = (0, 0, 0),
        min         = 0, max = 1
    )

#############################################

class Fruit(Evolvable, FruitProperties):
    
    # the label is used in the bl_label of the operators provided by Evolvable
    label = "Fruit"

    # the identifier is used in the bl_idname of the operators provided by Evolvable
    # also, the data bpy.types.Object.<identifier> will be used for loading/storing instances of this Evolvable
    identifier = "fruit"
    
    # you should call Evolvable.__init__ to init all properties with their default value
    # if you need your own __init__, make sure it has no required parameters and accepts kwargs like Evolvable.__init__
    __init__ = Evolvable.__init__


    def _outerSpline(self):
        def angle2Vec(a):
            return Vector((math.cos(a), 0, math.sin(a)))
        
        x = 0, self.length
        y = Vector((0, 0, self.length)), Vector((0, 0, 0))
        dy = angle2Vec(self.upperAngle), angle2Vec(self.lowerAngle + PI)
                
        return HermiteInterpolator(x, y, dy)
    
    def _makeFlowerResidue(self):
        if not self.fr_present:
            return [], []
        
        petals = self.fr_petals
        rPoint = self._outerSpline()((1-self.fr_radius)*self.length)
        vertices = [rPoint, rPoint.copy(), rPoint.copy() - Vector((0, 0, self.fr_length*self.length))]
        vertices[0].rotate(mathutils.Euler((0, 0, -PI/petals)))
        vertices[1].rotate(mathutils.Euler((0, 0, PI/petals)))
        vertices[2].rotate(mathutils.Euler((0, -self.fr_openingAngle, 0)))
        
        for i in range(1, petals):
            vtmp = [v.copy() for v in vertices[0:3]]
            for v in vtmp: v.rotate( mathutils.Euler((0, 0, i*2*PI/petals)) )
            vertices.extend(vtmp)
        faces = [ (i, i+1, i+2) for i in range(0, 3*petals, 3)]
        return vertices, faces

    def toMesh(self, LOD=16):
        """
        Create a bpy.data.meshes instance from this Evolvable. Here you define how the properties translate into a mesh.
        The method must be callable without parameters, so provide meaningful default values (except for self, of course).
        LOD (level of detail) is just an example and can be omitted.
        It is usually called through Evolvable.toMeshObject, which does some decoration.
        """
        
        mm = MeshMerger()
        mm.add(*screw(self._outerSpline(), LODr=10, LODp=LOD, rScale=lambda a: (math.sin(self.symmetry*a)+2)/2), 
             makeDiffuseMaterial(self.colour))
        mm.add(*self._makeFlowerResidue(), makeDiffuseMaterial([.12,.06,0]))
        
        return mm.buildMesh("Fruit")

#############################################

# the generators are processed for use in an EnumProperty
generatorFuncs = []
generatorMap = {f.__name__ : f for f in generatorFuncs}
generatorEnums = [(f.__name__, f.__name__, optional(f.__doc__, "")) for f in generatorFuncs]
