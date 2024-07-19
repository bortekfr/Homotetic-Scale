bl_info = {
    "name": "Homothetic Scale",
    "author": "Franck Carlichi",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Item Tab",
    "description": "Resize objects homothetically by percentage based on their original scale",
    "warning": "Blender 3.6.13",
    "doc_url": "http://example.com/your_addon_documentation",
    "category": "Object",
}

import bpy
from mathutils import Vector

# Global variables to manage updates and store reference scales
is_updating = False
reference_scales = {}

def get_scalable_objects(context):
    return [obj for obj in context.selected_objects if obj.type in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META', 'ARMATURE'}]

def store_reference_scales(context):
    """Store the current scales of selected objects as the new reference."""
    global reference_scales
    reference_scales = {obj.name: obj.scale.copy() for obj in get_scalable_objects(context)}

def apply_scale_to_object(obj, percentage):
    """Apply scaling to an object based on its reference scale and the given percentage."""
    if obj.name in reference_scales:
        original_scale = reference_scales[obj.name]
        scale_factor = percentage / 100.0
        new_scale = original_scale * scale_factor
        obj.scale = new_scale

def scale_objects_by_percentage(context, percentage):
    """Resize selected objects by percentage."""
    global is_updating
    if is_updating:
        return
    is_updating = True
    try:
        for obj in get_scalable_objects(context):
            apply_scale_to_object(obj, percentage)
        # Force update of the viewport
        context.view_layer.update()
    finally:
        is_updating = False

def update_percentage_property(self, context):
    """Update objects based on the specified percentage."""
    scale_objects_by_percentage(context, context.scene.scale_percentage)

def handle_selection_change(scene):
    """Handle selection changes."""
    global reference_scales
    current_selected = set(obj.name for obj in get_scalable_objects(bpy.context))
    
    # If selection has changed
    if current_selected != set(reference_scales.keys()):
        # Store new reference scales
        store_reference_scales(bpy.context)
        # Reset percentage to 100%
        scene.scale_percentage = 100.0

class OBJECT_PT_scaling_panel(bpy.types.Panel):
    bl_label = "Homothetic Scale"
    bl_idname = "OBJECT_PT_scaling_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column()
        col.prop(context.scene, "scale_percentage", text="Percentage")

class ResizeByPercentagePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Homothetic Scale Addon")
        #layout.label(text="Version: 1.0")
        layout.label(text="Tested on Blender 3.6.13")
        #layout.label(text="Author: Your Name")
        #layout.operator("wm.url_open", text="Documentation").url = "http://example.com/your_addon_documentation"
        layout.label(text="How to use:")
        box = layout.box()
        col = box.column()
        col.label(text="1. Select one or more objects in the 3D viewport")
        col.label(text="2. Find the Homothetic Scale panel in the sidebar (press N to open if not visible > View3D > Sidebar > Item Tab)")
        col.label(text="3. Adjust the percentage value to resize the selected objects")
        col.label(text="4. The resizing is applied in real-time as you adjust the value")
        col.label(text="5. To apply scale deselect the object")

def register():
    bpy.utils.register_class(OBJECT_PT_scaling_panel)
    bpy.utils.register_class(ResizeByPercentagePreferences)
    bpy.types.Scene.scale_percentage = bpy.props.FloatProperty(
        name="Percentage", 
        default=100.0, 
        min=0.1,  # Avoid division by zero
        max=1000.0,  # Limit maximum value to avoid excessively large scales
        update=update_percentage_property,
        subtype='PERCENTAGE',
        precision=3
    )
    # Add handler to manage selection changes
    bpy.app.handlers.depsgraph_update_post.append(handle_selection_change)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_scaling_panel)
    bpy.utils.unregister_class(ResizeByPercentagePreferences)
    del bpy.types.Scene.scale_percentage
    # Remove event handler
    if handle_selection_change in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(handle_selection_change)

if __name__ == "__main__":
    register()