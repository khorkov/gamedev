'''
Author: Alexander Khorkov - playrix
'''

bl_info = {
    "name": "Game Dev Toolset",
    "description": "Toolset for Game Dev",
    "author": "Alexander Khorkov",
    "version": (0, 0, 2),
    "blender": (2, 7, 9),
    "warning": "Beta Release",
    "location": "3D View > Toolbox",
    "category": "Object",
}

#-------------------------------------------------------
import bpy
import bmesh

from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        )

#-------------------------------------------------------

class Checker_Deselect(Operator):
    """Checker Deselect"""
    bl_idname = 'mesh.checker_deselect'
    bl_label = 'Checker Deselect'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects !=[]:
            return bpy.context.object.mode == 'EDIT' and bpy.context.object is not None

    def execute(self, context):
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.select_nth()
        return {"FINISHED"}

class Add_Bevel(Operator):
    """Add Bevel"""
    bl_idname = 'mesh.add_bevel'
    bl_label = 'Add Bevel'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects !=[]:
            return bpy.context.object.mode == 'OBJECT' and bpy.context.object is not None

    def execute(self, context):
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.context.object.modifiers["Bevel"].width = 0.05
        bpy.context.object.modifiers["Bevel"].segments = 4
        bpy.context.object.modifiers["Bevel"].profile = 1
        bpy.context.object.modifiers["Bevel"].use_clamp_overlap = True
        bpy.context.object.modifiers["Bevel"].loop_slide = False
        bpy.context.object.modifiers["Bevel"].limit_method = 'WEIGHT'
        bpy.context.object.modifiers["Bevel"].offset_type = 'WIDTH'
        return {"FINISHED"}

class Add_Subsurf(Operator):
    """Add Subsurf"""
    bl_idname = 'mesh.add_subsurf'
    bl_label = 'Add Subsurf'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects !=[]:
            return bpy.context.object.mode == 'OBJECT' and bpy.context.object is not None

    def execute(self, context):
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].render_levels = 3
        bpy.context.object.modifiers["Subdivision"].levels = 3
        bpy.context.object.modifiers["Subdivision"].show_on_cage = True
        bpy.ops.object.shade_smooth()
        return {"FINISHED"}

class Add_Triangulate(Operator):
    """Add Triangulate"""
    bl_idname = 'mesh.add_triangulate'
    bl_label = 'Add Tiangulate'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects !=[]:
            return bpy.context.object.mode == 'EDIT' and bpy.context.object is not None

    def execute(self, context):
        bpy.ops.mesh.quads_convert_to_tris()
        return {"FINISHED"}

class Add_UV_To_Hard_Edges(Operator):
    """UVs to Hard Edges"""
    bl_idname = 'mesh.add_uv_to_hard_edges'
    bl_label = 'UVs to Hard Edges'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects !=[]:
            return bpy.context.object.mode == 'EDIT' and bpy.context.object is not None

    def execute(self, context):
        sel_mode = bpy.context.scene.tool_settings.mesh_select_mode
        if sel_mode[1] == 1:

            if (len(bpy.context.active_object.data.uv_layers)==0):
                bpy.ops.mesh.uv_texture_add()

            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)

            bpy.ops.mesh.mark_seam(clear=True)
            bpy.ops.uv.seams_from_islands()

            obj = bpy.context.active_object
            mesh = obj.data
            bpy.ops.mesh.select_all(action='DESELECT')
            bm = bmesh.from_edit_mesh(mesh)
            for edge in bm.edges:
                if edge.seam:
                    edge.select_set(True)
                    break
            bpy.ops.mesh.select_similar(type='SEAM', threshold=0.01)
            bpy.ops.mesh.mark_sharp()
            self.report({'INFO'}, 'Hard on the borders of uv installed.')

        if sel_mode[1] == 0 or sel_mode[1] == 2:
            self.report({'ERROR'},'You need to switch to edge mode.')
        return {"FINISHED"}

class Add_Seam_To_Hard_Edges(Operator):
    """Seams to Hard Edges"""
    bl_idname = 'mesh.add_seams_to_hard_edges'
    bl_label = 'Seams to Hard Edges'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects !=[]:
            return bpy.context.object.mode == 'EDIT' and bpy.context.object is not None

    def execute(self, context):
        sel_mode = bpy.context.scene.tool_settings.mesh_select_mode
        if sel_mode[1] == 1:

            obj = bpy.context.active_object
            mesh = obj.data
            bpy.ops.mesh.select_all(action='DESELECT')
            bm = bmesh.from_edit_mesh(mesh)
            for edge in bm.edges:
                if not edge.smooth:
                    edge.select_set(True)
                    break

            bpy.ops.mesh.select_similar(type='SHARP', threshold=0.01)
            bpy.ops.mesh.mark_seam()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.editmode_toggle()
            bpy.ops.uv.smart_project()
            self.report({'INFO'}, 'Seams on the hard edges installed.')

        if sel_mode[1] == 0 or sel_mode[1] == 2:
            self.report({'ERROR'},'You need to switch to edge mode.')
        return {"FINISHED"}

#-------------------------------------------------------
class VIEW3D_PT_checker_deselect(Panel):
    bl_idname = "panel.panel3"
    bl_label = "Game Dev Toolset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Game Dev Toolset"

    def draw(self, context):
        self.layout.operator("mesh.checker_deselect", text="Checker Deselect")
        self.layout.operator("mesh.add_bevel", text="Add Bevel")
        self.layout.operator("mesh.add_subsurf", text="Add Subsurf")
        self.layout.operator("mesh.add_triangulate", text="Add Tiangulate")
        self.layout.operator("mesh.add_uv_to_hard_edges", text="UVs to Hard Edges")
        self.layout.operator("mesh.add_seams_to_hard_edges", text="Seams to Hard Edges")

#-------------------------------------------------------
classes = (
    VIEW3D_PT_checker_deselect,
    Checker_Deselect,
    Add_Bevel,
    Add_Subsurf,
    Add_Triangulate,
    Add_UV_To_Hard_Edges,
    Add_Seam_To_Hard_Edges
)

#-------------------------------------------------------
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
