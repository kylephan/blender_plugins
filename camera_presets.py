import bpy
import json

ogBaseLocation = []
temp_shot_type = ""
global shotType,shot_angle,shot_type
## jsonl_reader function
def test(a,b):
    print(a)
    print(b)

def save_scene(shot_name):
    dir_path = "D:\\MTL\\SRP2\\kphan\\Camera\\addons\\mtl\\output\\"
    file_path = dir_path + shot_name + "_Previs_v001" + ".blend"
    bpy.ops.wm.save_as_mainfile(filepath=file_path)

def scene_duration(shot_duration):
    frame_rate = 25  
    frame_start = 1
    shot_duration_frames = float(shot_duration) * frame_rate
    frame_end = frame_start + shot_duration_frames
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end

def get_shot_name(scene_nr,shot_id):
    shot_id_ext = ''
    padding = 3       
    temp_scene_nr = scene_nr
    temp_shot_id = shot_id
    if len(str(temp_shot_id)) < padding:
        pad = padding-len(str(temp_shot_id))
        i = 1
        while i <= pad:
            shot_id_ext += '0'
            i+=1                               
    shot_id_ext += str(temp_shot_id)
    shot_name = "SC" + str(temp_scene_nr) +  "SH" + str(shot_id_ext)
    return shot_name

def batch_export():
    list = []
    try:
        with open("D:\\MTL\\SRP2\\kphan\\Camera\\addons\\mtl\\data\\BSF_998-1047_shots.jsonl") as json_file:
            data = json_file.readlines()
            json_file.close()
    except OSError:
        raise ValueError(f"invalid input path")
    
    
    for line in data:
        list[:] = []
        list.append(json.loads(line))
        for l in list: 
             
            scene_nr = l['scene_nr']
            shot_id = l['shot_id']
            shot_type = l['shot_type']
            angle_type = l['camera_angle_type']
            shot_duration = l['duration']        
            shot_name = get_shot_name(scene_nr,shot_id)
            shot_type_presets(shot_type)
            shot_angle_presets(angle_type)
            scene_duration(shot_duration)
            save_scene(shot_name)
            
## getting data from json to use in SHOT_TYPE function
def shot_type_reader(shot_type):
    try:
        with open("D:\\MTL\\SRP2\\kphan\\Camera\\addons\\mtl\\data\\preset_camera.json") as json_file:    
            data = json.load(json_file)
    except OSError:
        raise ValueError(f"Cannot find Camera Preset")
    aim_location = data['shot_type'][shot_type]['aim_location']  
    base_location = data['shot_type'][shot_type]['base_location'] 
    return aim_location,base_location
## getting data from json to use in ANGLE_TYPE function
def angle_type_reader(angle_type):
    try:
        with open("D:\\MTL\\SRP2\\kphan\\Camera\\addons\\mtl\\data\\preset_camera.json") as json_file:    
            data = json.load(json_file)
    except OSError:
        raise ValueError(f"Cannot find Camera Preset")
    stand_scale = data['angle_type'][angle_type]['stand_scale']  
    cam_rotation = data['angle_type'][angle_type]['cam_rotation']
    aim_influence = data['angle_type'][angle_type]['aim_influence']
    aim_rotation = data['angle_type'][angle_type]['aim_rotation']
    return stand_scale,aim_influence,cam_rotation,aim_rotation     
## getting data from json to use in FRAMING function
def framing_reader(direction_x, direction_y,shot_type):
    try:
        with open("D:\\MTL\\SRP2\\kphan\\Camera\\addons\\mtl\\data\\preset_camera.json") as json_file:    
            data = json.load(json_file)
    except OSError:
        raise ValueError(f"Cannot find Camera Preset")
    cam_location_x = data['framing'][direction_x][direction_y][shot_type]['cam_location_x']
    cam_location_y = data['framing'][direction_x][direction_y][shot_type]['cam_location_y']

    return cam_location_x,cam_location_y 
                
## save the original location so we can go back after delete animation data
def saveLocation():
    baseCtrl = bpy.data.objects["base_ctrl"]
    tempBaseLocation = []
    tempBaseLocation[:] = []
    tempBaseLocation.append(baseCtrl.location[0])
    tempBaseLocation.append(baseCtrl.location[1])
    tempBaseLocation.append(baseCtrl.location[2])
    return tempBaseLocation
## focal length functions
def fl35mm(context):
    camera = bpy.data.objects["camera"]
    camera.data.lens = 35
def fl50mm(context):
    camera = bpy.data.objects["camera"]
    camera.data.lens = 50
def fl75mm(context):
    camera = bpy.data.objects["camera"]
    camera.data.lens = 75
## shot type function
def shot_type_presets(shot_type):
    global ogBaseLocation
    global temp_shot_type
    baseCtrl = bpy.data.objects["base_ctrl"]
    standCtrl = bpy.data.objects["stand_ctrl"]
    armCtrl = bpy.data.objects["arm_ctrl"]
    aim = bpy.data.objects["aim_loc"]
    clearBaseAnimation()
    baseCtrl.location[0] = 0
    baseCtrl.location[2] = 0
    presets = shot_type_reader(shot_type)
    aim.location[2] = presets[0]
    baseCtrl.location[1] = presets[1]  
    ogBaseLocation = saveLocation()
    temp_shot_type = shot_type
## angle type functions 
def shot_angle_presets(shot_angle):
    camera = bpy.data.objects["camera"]
    standCtrl = bpy.data.objects["stand_ctrl"]
    aimOffset = bpy.data.objects["aim_offset_grp"]
    camera.rotation_euler[0] = 0
    presets = angle_type_reader(shot_angle)
    standCtrl.scale[1] = presets[0]
    aimOffset.constraints["Track To"].influence = presets[1]
    camera.rotation_euler[2] = presets[2]
    aimOffset.rotation_euler[0] = presets[3]
## tilt function
def dutch_angle(direction):
    camera = bpy.data.objects["camera"]
    if direction == "left":      
        camera.rotation_euler[2] = -0.25
    elif direction == "right":
        camera.rotation_euler[2] = 0.25
    else: 
        camera.rotation_euler[2] = 0.0
## tracking function
## clear animation on arm_ctrl
def clearArmAnimation():
    armCtrl = bpy.data.objects["arm_ctrl"]
    armCtrl.animation_data_clear()
    cameraShp = bpy.data.cameras["camera_shape"]
    cameraShp.animation_data_clear()
    armCtrl.rotation_euler[0] = 0
    armCtrl.rotation_euler[1] = 0
    armCtrl.rotation_euler[2] = 0
## clear animation on base_ctrl
def clearBaseAnimation():
    baseCtrl = bpy.data.objects["base_ctrl"]
    baseCtrl.animation_data_clear()
    cameraShp = bpy.data.cameras["camera_shape"]
    cameraShp.animation_data_clear()  
## Fixed cam preset     
def trackFixed():
    global ogBaseLocation
    baseCtrl = bpy.data.objects["base_ctrl"] 
    cameraShp = bpy.data.cameras["camera_shape"]   
    clearArmAnimation()
    clearBaseAnimation()
    baseCtrl.location[0] = ogBaseLocation[0]
    baseCtrl.location[1] = ogBaseLocation[1]
    baseCtrl.location[2] = ogBaseLocation[2]
    cameraShp.lens = 50
## Pan cam preset 
def trackPan(duration,direction):
    frameStart = 1
    frameEnd = frameStart + duration
    clearArmAnimation()
    clearBaseAnimation()
    if direction == "Left":
        rotation = 0.5
    else:
            rotation = -0.5
    armCtrl = bpy.data.objects["arm_ctrl"]  
    armCtrl.rotation_euler[2] = 0.0
    armCtrl.keyframe_insert(data_path="rotation_euler", frame=frameStart, index=2)
    armCtrl.rotation_euler[2] = rotation
    armCtrl.keyframe_insert(data_path="rotation_euler", frame=frameEnd, index=2)
## Tilt cam preset 
def trackTilt(duration,direction):
    frameStart = 1
    frameEnd = frameStart + duration
    clearArmAnimation()
    clearBaseAnimation()
    if direction == "Up":
        rotation = 0.5
    else:
            rotation = -0.5
    armCtrl = bpy.data.objects["arm_ctrl"] 
    armCtrl.rotation_euler[0] = 0.0
    armCtrl.keyframe_insert(data_path="rotation_euler", frame=frameStart, index=0)
    armCtrl.rotation_euler[0] = rotation
    armCtrl.keyframe_insert(data_path="rotation_euler", frame=frameEnd, index=0)
## Truck cam preset
def trackTruck(duration,direction):
    global ogBaseLocation
    frameStart = 1
    frameEnd = frameStart + duration
    baseCtrl = bpy.data.objects["base_ctrl"]
    clearBaseAnimation()
    clearArmAnimation()
    if direction == "Backwards":
        location = -5
    else:
            location = 5
    baseCtrl.location[1] = ogBaseLocation[1]
    baseCtrl.keyframe_insert(data_path="location", frame=frameStart, index=1)
    baseCtrl.location[1] = ogBaseLocation[1] + location
    baseCtrl.keyframe_insert(data_path="location", frame=frameEnd, index=1)
## Dolly cam preset    
def trackDolly(duration,direction):
    global ogBaseLocation
    frameStart = 1
    frameEnd = frameStart + duration
    baseCtrl = bpy.data.objects["base_ctrl"]
    clearBaseAnimation()
    clearArmAnimation()
    if direction == "Left":
        location = -5
    else:
            location = 5
    baseCtrl.location[0] = ogBaseLocation[0]
    baseCtrl.keyframe_insert(data_path="location", frame=frameStart, index=0)
    baseCtrl.location[0] = ogBaseLocation[0] + location
    baseCtrl.keyframe_insert(data_path="location", frame=frameEnd, index=0)
## Zoom cam preset 
def trackZoom(duration,direction):
    frameStart = 1
    frameEnd = frameStart + duration
    cameraShp = bpy.data.cameras["camera_shape"]
    clearArmAnimation()
    clearBaseAnimation()
    if direction == "In":
        lens = 75
    else:
        lens = 25
    cameraShp.lens = 50
    cameraShp.keyframe_insert(data_path="lens", frame=frameStart)
    cameraShp.lens = lens
    cameraShp.keyframe_insert(data_path="lens", frame=frameEnd)

## framing (rule of third) functions
def rule_of_third(direction_x,direction_y):
    global temp_shot_type
    camera = bpy.data.objects["camera"]
    if direction_x == 'middle':
        camera.location[0] = 0.0
        camera.location[1] = 0.0
    else:
        presets = framing_reader(direction_x, direction_y,temp_shot_type)
        camera.location[0] = presets[0]
        camera.location[1] = presets[1]
## class start here
class CameraPresets(bpy.types.Operator):
    bl_label = 'Preset Camera'
    bl_idname = 'ops.presets_camera'
    id = bpy.props.IntProperty()
    duration = bpy.props.IntProperty()
    direction = bpy.props.StringProperty()
    direction_x = bpy.props.StringProperty()
    direction_y = bpy.props.StringProperty()

    def execute(self,context):
        scene = context.scene
        global ogBaseLocation,shotType,shot_angle
        ## focal length
        if self.id == 50:
            fl35mm(context)
        if self.id == 51:
            fl50mm(context)
        if self.id == 52:
            fl75mm(context)
        ## shot type
        if self.id == 0:
            shotType = "mid_full"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()
        if self.id == 1:
            shotType = "full"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()           
        if self.id == 3:
            shotType = "close up"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()
        if self.id == 4:
            shotType = "medium"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()
        if self.id == 5:
            shotType = "long"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()         
        if self.id == 6:
            shotType = "extreme close up"  
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()              
        if self.id == 7:
            shotType = "cowboy"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()         
        if self.id == 8:
            shotType = "medium close up"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()            
        if self.id == 9:
            shotType = "extreme wide shot"
            shot_type_presets(shotType)
            ogBaseLocation = saveLocation()
        ## angle type
        if self.id == 20:
            shot_angle = "high"
            shot_angle_presets(shot_angle)
        if self.id == 21:
            shot_angle = "low"
            shot_angle_presets(shot_angle)
        if self.id == 22:
            shot_angle = "shoulder_level"
            shot_angle_presets(shot_angle)
        if self.id == 23:
            shot_angle = "birds_eye"
            shot_angle_presets(shot_angle)
        if self.id == 25:
            shot_angle = "eye_level"
            shot_angle_presets(shot_angle) 
        ## dutch tilt
        if self.id == 24:
            direction = "left"
            dutch_angle(direction)
        if self.id == 26:
            direction = "no"
            dutch_angle(direction)
        if self.id == 27:
            direction = "right"
            dutch_angle(direction)
        ## track   
        if self.id == 400: 
            tempBaseLocation = ogBaseLocation
            trackFixed(tempBaseLocation)
        if self.id == 41:
            direction = "Left"
            duration = scene.trackDuration    
            trackPan(duration,direction)
        if self.id == 42:
            direction = "Up"
            duration = scene.trackDuration
            trackTilt(duration,direction)
        if self.id == 43:
            direction = "Backwards"
            duration = scene.trackDuration
            tempBaseLocation = ogBaseLocation
            trackTruck(duration,tempBaseLocation,direction)
        if self.id == 44:
            direction = "Left"
            duration = scene.trackDuration
            tempBaseLocation = ogBaseLocation
            trackDolly(duration,tempBaseLocation,direction)
        if self.id == 45:
            duration = scene.trackDuration
            direction = "In" 
            trackZoom(duration,direction)
        if self.id == 40:
            duration = scene.trackDuration
            direction = "Out" 
            trackZoom(duration,direction)
        if self.id == 46:
            direction = "Right"
            duration = scene.trackDuration
            trackPan(duration,direction)
        if self.id == 47:
            direction = "Down"
            duration = scene.trackDuration
            trackTilt(duration,direction)
        if self.id == 48:
            direction = "Forwards"
            duration = scene.trackDuration
            tempBaseLocation = ogBaseLocation
            trackTruck(duration,tempBaseLocation,direction)
        if self.id == 49:
            direction = "Right"
            duration = scene.trackDuration
            tempBaseLocation = ogBaseLocation
            trackDolly(duration,tempBaseLocation,direction)
        
        ## rule of third    
        if self.id == 30:
            direction_x = 'left'
            direction_y = 'top'
            rule_of_third(shotType,direction_x,direction_y)
        if self.id == 31:
            direction_x = 'middle'
            direction_y = 'middle'
            rule_of_third(shotType,direction_x,direction_y)
        if self.id == 32:
            direction_x = 'right'
            direction_y = 'top'
            rule_of_third(shotType,direction_x,direction_y)
        if self.id == 33:
            direction_x = 'left'
            direction_y = 'bottom'
            rule_of_third(shotType,direction_x,direction_y)
        if self.id == 34:
            direction_x = 'right'
            direction_y = 'bottom'
            rule_of_third(shotType,direction_x,direction_y)
        if self.id == 90:
            jsonl_reader()
            
        return {'FINISHED'}        
## register       
def register():
    bpy.utils.register_class(CameraPresets)
    
def unregister():
    bpy.utils.unregister_class(CameraPresets)    
if __name__ == '__main__':
    register()