"""
Processing geometry in Blender and exporting Glb v011
"""
from ntpath import join
import sys
import os
import json
import bpy


# Removing all objects from the scene
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)


# Reading parameters from argvs
argvs = sys.argv[4:]
JSON_PATH = argvs[0]
work_dir = argvs[1]
task_name = argvs[2]
main_save_dir = os.path.join(work_dir, "Animation")

# Format save dir for Step
step_name = os.path.basename(JSON_PATH).split('.')[0]
step_save_dir = os.path.join(main_save_dir, step_name)
if not os.path.exists(step_save_dir):
    os.makedirs(step_save_dir)

# Creating directorys for animation glb
combine_animation_dir = os.path.join(step_save_dir, "Combine Animation")
if not os.path.exists(combine_animation_dir):
    os.makedirs(combine_animation_dir)

part_animation_dir = os.path.join(step_save_dir, "Separate animation")
if not os.path.exists(part_animation_dir):
    os.makedirs(part_animation_dir)

# Reading json file
with open(JSON_PATH, "r", encoding="utf-8") as file:
    json_data = json.load(file)

# Export file path
combine_file = os.path.join(combine_animation_dir, step_name)

# Сollection creation
root_collection = bpy.data.scenes['Scene'].collection
static_collection = bpy.context.blend_data.collections.new(name='Static')
bpy.context.collection.children.link(static_collection)
animated_collection = bpy.context.blend_data.collections.new(name='Animated')
bpy.context.collection.children.link(animated_collection)


# Create materials function
def material_create(mat_name, r, g, b,):
    """
    Create difuse material
    """
    material = bpy.data.materials.new(name=mat_name)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (r, g, b, 1)
    return material


# Creating new material with color
prim_mat = material_create('Primary', 0.091, 0.402, 1)
second_mat = material_create('Secondary', 0.216, 1, 0.216)
inactive_mat = material_create('Inactive', 0.6, 0.6, 0.6)

# Import models
parts = []


for glb_part in json_data:
    # Import part 3d model
    part_file_name = glb_part["PART NUMBER"] + '.glb'
    glb_path = os.path.join(work_dir, part_file_name)
    if os.path.exists(glb_path):  # Check glb file existings
        bpy.ops.import_scene.gltf(filepath=glb_path)
    else:
        print(glb_path + ' not found')
        continue

    # Set imported object name
    geo_object = bpy.context.selected_objects[0]
    geo_object.name = glb_part["PART NUMBER"]
    geo_object.data.name = glb_part["PART NUMBER"]
    geo_object.data["DIR"] = glb_part["DIRECTION"]
    parts.append(geo_object)

    # Set material
    if glb_part["COLOR CODING"] == "PRIMARY":
        if len(geo_object.material_slots) < 1:
            geo_object.data.materials.append(prim_mat)
        else:
            geo_object.material_slots[0].material = prim_mat
        prime_object = geo_object
        print(prime_object)

    elif glb_part["COLOR CODING"] == "SECONDARY":
        if len(geo_object.material_slots) < 1:
            geo_object.data.materials.append(second_mat)
        else:
            geo_object.material_slots[0].material = second_mat
    else:
        if len(geo_object.material_slots) < 1:
            geo_object.data.materials.append(inactive_mat)
        else:
            geo_object.material_slots[0].material = inactive_mat

# Creating text labels
for obj in parts:
    label = obj.name

    # Creating text object and set name
    bpy.ops.object.text_add(rotation=(1.57, 0, 0))
    text = bpy.context.selected_objects[0]
    text.data.body = label
    text.data.name = "Label " + label
    text.name = "Label " + label

    # Text object position and extrude
    text.data.align_x = 'CENTER'
    text.data.extrude = 0.03
    text.location = (0, 0, obj.bound_box[6][2] + 0.35)
    text.scale = (0.3, 0.3, 0.3)

    # Set text material
    mat = obj.active_material
    text.data.materials.append(mat)

    # Parent
    text.parent = obj

# Set start and end frame
F_START = 1
F_END = 100
bpy.context.scene.frame_start = F_START
bpy.context.scene.frame_end = F_END


for i, anim_obj in enumerate(parts, start=0):

    anim_direction = anim_obj.data["DIR"]
    prime_position = prime_object.location

    # Create animation data
    anim_obj.animation_data_create()
    anim_obj.animation_data.action = bpy.data.actions.new(name="Animation")
    anim_obj_location = anim_obj.location

    multiplayer = 0.75
    if anim_direction == "UP" or anim_direction == "DOWN":

        fc_z_location = anim_obj.animation_data.action.fcurves.new(data_path="location", index=2)

        if anim_direction == "UP":
            target_location = anim_obj_location[2] - multiplayer
        else:
            target_location = anim_obj_location[2] + multiplayer

        # Position animation
        key_start_location = fc_z_location.keyframe_points.insert(frame=F_START, value=target_location)
        key_mid_location = fc_z_location.keyframe_points.insert(frame=F_END / 2, value=anim_obj_location[2])
        key_end_location = fc_z_location.keyframe_points.insert(frame=F_END, value=target_location)
        key_start_location.interpolation = "LINEAR"
        key_mid_location.interpolation = "LINEAR"
        key_end_location.interpolation = "LINEAR"

    elif anim_direction == "IN" or anim_direction == "OUT":

        fc_x_location = anim_obj.animation_data.action.fcurves.new(data_path="location", index=0)
        fc_y_location = anim_obj.animation_data.action.fcurves.new(data_path="location", index=1)

        move_direction = prime_position - anim_obj_location
        move_direction.normalize()

        if anim_direction == "IN":
            target_xy_location = anim_obj_location - move_direction * multiplayer
        else:
            target_xy_location = anim_obj_location + move_direction * multiplayer

        key_x_start_location = fc_x_location.keyframe_points.insert(frame=F_START, value=target_xy_location[0])
        key_x_mid_location = fc_x_location.keyframe_points.insert(frame=F_END / 2, value=anim_obj_location[0])
        key_x_end_location = fc_x_location.keyframe_points.insert(frame=F_END, value=target_xy_location[0])
        key_x_start_location.interpolation = "LINEAR"
        key_x_mid_location.interpolation = "LINEAR"
        key_x_end_location.interpolation = "LINEAR"

        key_y_start_location = fc_y_location.keyframe_points.insert(frame=F_START, value=target_xy_location[1])
        key_y_mid_location = fc_y_location.keyframe_points.insert(frame=F_END / 2, value=anim_obj_location[1])
        key_y_end_location = fc_y_location.keyframe_points.insert(frame=F_END, value=target_xy_location[1])
        key_y_start_location.interpolation = "LINEAR"
        key_y_mid_location.interpolation = "LINEAR"
        key_y_end_location.interpolation = "LINEAR"

# Saving combine GLB file
bpy.ops.export_scene.gltf(filepath=combine_file,
                          export_format='GLB',
                          export_animations=True,
                          export_nla_strips=False)

# Saving separate GLB files
for obj in parts:
    bpy.ops.object.select_all(action='DESELECT')
    part_animation_path = os.path.join(part_animation_dir, obj.name + ".glb")
    obj.select_set(True)
    for child_obj in obj.children:
        child_obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=part_animation_path,
                              export_format='GLB',
                              export_animations=True,
                              export_nla_strips=False,
                              use_selection=True)

#blend_file = os.path.join(work_dir,"Blnd.blend")
#bpy.ops.wm.save_as_mainfile(filepath=blend_file)

# Remove Json file
#if os.path.exists(JSON_PATH):
#    os.remove(JSON_PATH)
