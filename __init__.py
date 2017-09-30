bl_info = { # TODO adapt to your project
    "name": "Example Addon",
    "category": "Add Mesh",
    "author": "Your Name",
    "version": (0, 0),
    }

import bpy
from .util import linkAndSelect
from .fruit import Fruit

def register():
    Fruit.registerOperators()
    
def unregister():
    Fruit.unregisterOperators()

if __name__ == "__main__": # lets you run the script from a Blender text block; useful during development
    register()
