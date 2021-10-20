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
from bpy.types import ID, Object, Operator, Particle, ParticleSystem, ParticleSystems

class ChildGuides_GenChildGuides(Operator):
    bl_idname = "armature.bj_mark_bone_side"
    bl_label = "Generate Hair Guides from Children"
    bl_description = "Generates a new hair particle system with hair guides using child hairs of the selected hair particle system"
    bl_options = {'REGISTER', 'UNDO'}

    obj: Object = None # Object we are working with
    system: ParticleSystem = None # Primary particle system we are working with
    gen: ParticleSystem = None # Generated particle system to work with
    systemName: str
    filterStr: str = "%CHILDGUIDES_IGNORE%"

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
            self.report({'WARNING'}, "No valid modifier selected (must be Particle object with Hair enabled)")
            return {'FINISHED'}
        
        self.systemName = self.system.name # Store name
        self.system.name = "!CHILDGUIDES_DUPLICATION" # Override name for easy duplication
        for item in self.obj.particle_systems.values():
            item.name += self.filterStr
        
        bpy.ops.particle.duplicate_particle_system(use_duplicate_settings=True) # Create a clone of this system
        # This above method duplicates ALL particle systems in the object, but we only want to duplicate the active one
        # bpy.ops.particle.copy_particle_systems only copies particle systems from the active object to other objects
        #    in selection that are NOT the active object
        # Thus, we need to instead filter out what particles we don't want

        # Iterate through all particle systems
        for key in self.obj.particle_systems.keys():
            item: ParticleSystem = self.obj.particle_systems[key]

            # If the duplicate has a similar name to our active particle system, but isn't the same object...
            if item.name.startswith(self.system.name) and not item.name.endswith(self.system.name):
                self.gen = item # This is (very hopefully) our duplicated particle system!
            
            elif self.filterStr in item.name: # Otherwise, this is one of the other systems
                if item.name.endswith(self.filterStr): # This is an original system since it doesn't have a digit ending
                    item.name = item.name.replace(self.filterStr, "") # Rename it back to orignial
                else: # Otherwise, this is a clone, and we should delete it
                    self.obj.particle_systems.active_index = self.obj.particle_systems.values().index(item, 0)
                    bpy.ops.object.particle_system_remove()
        
        self.system.name = self.systemName # Reset system name
        if self.gen == None: # If we didn't get what we found, return before we break something
            self.report({'ERROR'}, "Could not find duplicate of active particle system!")
            return {'FINISHED'}
        
        self.gen.name = self.systemName + "_Regenerated" # Give duplicate copy a readable name
        systems: ParticleSystems = self.obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).particle_systems
        
        # Update systems to use new generated settings
        for item in systems.values():
            if item.name == self.system.name:
                self.system = item
            elif item.name == self.gen.name:
                self.gen = item

        # Set the count of the new system to the number of child particles of the old system
        self.gen.settings.count = len(self.system.child_particles.values())

        childArray = self.system.child_particles.values()
        guideArray = self.gen.particles.values()
        for idx in range(0, len(childArray)):
            child: Particle = childArray[idx]
            guide: Particle = guideArray[idx]

            print(child, guide)

            # guide.location = child.location
            # guide.rotation = child.rotation
            # guide.velocity = child.velocity
            # guide.angular_velocity = child.angular_velocity

            # childKeys = child.hair_keys.values()
            # guideKeys = guide.hair_keys.values()
            # for key in range(0, len(childKeys)):
            #     guideKeys[key].co = childKeys[key].co
            #     guideKeys[key].time = childKeys[key].time
            #     guideKeys[key].weight = childKeys[key].weight
        
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