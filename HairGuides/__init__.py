bl_info = {
    "name" : "Blender Child Guides",
    "author" : "Alan O'Cull, cellomonster",
    "description" : "Generates a new hair particle system with hair guides using child hairs of the selected hair particle system",
    "blender" : (2, 93, 2),
    "version" : (0, 0, 1),
    "location" : "View3D > Object > Convert > Generate Hair Guides from Children",
    "warning" : "",
    "category" : "Particles"
}

import bpy
from bpy.types import Object, Operator, ParticleSystem

class ChildGuides_GenChildGuides(Operator):
    bl_idname = "armature.bj_mark_bone_side"
    bl_label = "Generate Hair Guides from Children"
    bl_description = "Generates a new hair particle system with hair guides using child hairs of the selected hair particle system"
    bl_options = {'REGISTER', 'UNDO'}

    obj: Object = None # Object we are working with
    system: ParticleSystem = None # Primary particle system we are working with
    gen: ParticleSystem = None # Generated particle system to work with

    def button(self, context):
        """Function for registering this class to a button in Blender's UI layout"""
        self.layout.operator(
            ChildGuides_GenChildGuides.bl_idname,
            text="Generate Hair Guides from Children",
            icon='MOD_MIRROR')

    def manual_map():
        """Manually binds this operator to a python syntax so hotkeys can be set to it inside Blender"""
        url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
        url_manual_mapping = (
            ("bpy.ops.armature.bj_mark_bone_side", "scene_layout/object/types.html"),
        )
        return url_manual_prefix, url_manual_mapping

    def execute(self, context: bpy.types.Context):
        """Actual execution of the operator, code goes here"""

        # First, find the modifier we want to work with
        self.obj = bpy.context.active_object
        if self.obj == None: # Return if we can't find what we want to work with
            self.report({'WARNING'}, "No active object selected")
            return {'FINISHED'}
        self.system = self.obj.particle_systems.active
        if self.system == None or self.system.settings.type != 'HAIR': # Return if there is no valid hair modifier
            self.report({'WARNING'}, "No valid modifier selected")
            return {'FINISHED'}
        
        bpy.ops.particle.duplicate_particle_system(use_duplicate_settings=True) # Create a clone of this system
        self.gen = self.obj.particle_systems.values()[len(self.obj.particle_systems) - 1] # Get newly created particle system and store it

        # Set the count of the new system to the number of child particles of the old system
        self.gen.settings.count = len(self.system.child_particles.values())
        print(self.system.child_particles.values())

        # TODO: Get children and do stuff
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ChildGuides_GenChildGuides)
    bpy.utils.register_manual_map(ChildGuides_GenChildGuides.manual_map)
    bpy.types.VIEW3D_MT_object_convert.append(ChildGuides_GenChildGuides.button)

def unregister():
    bpy.utils.unregister_class(ChildGuides_GenChildGuides)
    bpy.utils.unregister_manual_map(ChildGuides_GenChildGuides.manual_map)
    bpy.types.VIEW3D_MT_object_convert.remove(ChildGuides_GenChildGuides.button)

if __name__ == "__main__":
    register()