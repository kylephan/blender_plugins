import bpy

def add_camera():
    #Armature setup
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    armature = bpy.data.objects["Armature"]
    #armature.name = "camera_rig"
    #bpy.ops.object.select_all(action='DESELECT')
    
    #bpy.context.collection.objects.link(armature)
    
    bpy.context.view_layer.objects.active = armature  
    armature.select_set(True)
    #Must make armature active and in edit mode to create a bone
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    #Make extra bones through extrude joints
    bpy.ops.transform.translate(value=(0, 1, -1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False}, TRANSFORM_OT_translate={"value":(0, 0, 1), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False}, TRANSFORM_OT_translate={"value":(0, 1, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    # exit edit mode to save bones so they can be used in pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    ##add aim target
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 1, 0))
    bpy.context.object.name = "aim_loc"  
    aimLoc = bpy.data.objects["aim_loc"]   
    ## add camera object   
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(1.5708, 0, 0))
    bpy.context.object.name = "camera"  
    camera = bpy.data.objects["camera"]
    ## aim null object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    bpy.context.object.name = "aim_offset_grp" 
    aimOffset = bpy.data.objects["aim_offset_grp"]
    ## track aim object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    bpy.context.object.name = "camera_offset_grp" 
    cameraOffset = bpy.data.objects["camera_offset_grp"]  
    ## parent all the objects 
    camera.parent = aimOffset
    aimOffset.parent = cameraOffset  
    
    ## add constraint
    ## position constraint
    posConstraint = cameraOffset.constraints.new('COPY_LOCATION')
    posConstraint.target = bpy.data.objects["camera_rig"]
    posConstraint.subtarget = "Bone.002"
    posConstraint.head_tail = 1
    ## rotation constraint
    posConstraint = cameraOffset.constraints.new('COPY_ROTATION')
    posConstraint.target = bpy.data.objects["camera_rig"]
    posConstraint.subtarget = "Bone.002"
    ## aim constraint
    aimConstraint = aimOffset.constraints.new('TRACK_TO')
    aimConstraint.up_axis = 'UP_Y'
    aimConstraint.track_axis = 'TRACK_NEGATIVE_Z'
    aimConstraint.target = aimLoc
    aimConstraint.influence = 0 ## add a check box here to see if they want aim or not, toggle between 0 and 1

    ##control setup
    ## create 3 circle controls
    bpy.ops.surface.primitive_nurbs_surface_circle_add(enter_editmode=False, location=(0, 0, 0))
    bpy.context.object.name = "base_ctrl"
    bpy.ops.surface.primitive_nurbs_surface_circle_add(enter_editmode=False, location=(0, 0, 0))
    bpy.context.object.name = "stand_ctrl"
    bpy.ops.surface.primitive_nurbs_surface_circle_add(enter_editmode=False, location=(0, 0, 0))
    bpy.context.object.name = "arm_ctrl"
    ## parent them and set their location
    baseCtrl = bpy.data.objects["base_ctrl"]
    standCtrl = bpy.data.objects["stand_ctrl"]
    armCtrl = bpy.data.objects["arm_ctrl"]
    standCtrl.parent = baseCtrl
    armCtrl.parent = standCtrl
    standCtrl.location[1] = 1
    armCtrl.location[2] = 1
    ## access the bones and contraints
    bpy.context.view_layer.objects.active = bpy.data.objects['camera_rig']
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    arm = bpy.context.scene.objects.get("camera_rig")

    baseJnt = arm.pose.bones.get("Bone")
    consBase = baseJnt.constraints.new('COPY_LOCATION')
    consBase.target = baseCtrl

    standJnt = arm.pose.bones.get("Bone.001")
    consStand = standJnt.constraints.new('COPY_SCALE')
    consStand.target = standCtrl

    armJnt = arm.pose.bones.get("Bone.002")
    consArm = armJnt.constraints.new('COPY_ROTATION')
    consArm.target = armCtrl
    # exit edit mode to save bones so they can be used in pose mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
class AddCamera(bpy.types.Operator):
    bl_label = 'Add Camera'
    bl_idname = 'ops.add_camera'
    
    def __init__(self):
        print("works??")
        
        
def register():
    bpy.utils.register_class(AddCamera)
    
def unregister():
    bpy.utils.unregister_class(AddCamera)

    
if __name__ == '__main__':
    register()
    



    

    