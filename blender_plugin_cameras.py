# -*- coding: utf-8 -*-

"""
Manipulate models in Blender e.g. import components into output file.

The script must be run using the version Python 3.7.X with Blender API 2.82,
another API version should use related Python version
(https://docs.blender.org/api/current/) and doesn't support -m e.g.:

blender --background --python blender_plugin.py -- -i fileA fileB -o fileC

This script depends on the following packages:
    * argparse
    * logging
    * sys
    * os
    * json
    * re
    * bpy

This script can be imported as a module and contains the following
classes:
    * ArgParseBlender - Command line parser for Blender Plugin
    * BlenderImportData - Extract and load components from input files into output file

This script can be imported as a module and contains the following
functions:
    * _load_nouns - Load given nouns into output blender file
    * blender_files_list - Return full path to file
    * _handle_args - Extract args and call delegate function
    * main - Parse command line args and call handler
"""

import argparse
import json
import logging
import math
import os
import random
import re
import sys

import bpy

from plugins import camera_setup
from plugins import camera_ui


class ArgParseBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >> blender --python my_script.py -- -a 1 -b 2
    >> blender --python my_script.py --
    """

    def get_argv(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx + 1:]  # the list after '--'
        except ValueError as read_error:  # '--' not in the list:
            return read_error

    # overrides superclass
    def parse_args(self):  # pylint: disable=W0221
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self.get_argv())


class BlenderPlugin(object):
    """Extract and load components from input files into output file"""
    

    def preset_camera(shot_type,camera_angle_type):
        #Check params
        if not shot_type:
            raise ValueError("Shot type blank")
        if not camera_angle_type:
            raise ValueError("Camera angle type blank")

        try:
            file_name = "Z:\\Projects\\MTL\\SPR2\\kphan\\mtl_plugin_blender\\plugins\\preset_camera.json"
            with open(file_name) as json_file:    
                data = json.load(json_file)
        except OSError:
            raise ValueError(f"Cannot find {file_name}")

        camera = bpy.data.objects["camera"]
        base_ctrl = bpy.data.objects["base_ctrl"]
        stand_ctrl = bpy.data.objects["stand_ctrl"]
        aim = bpy.data.objects["aim_loc"]
        aim_offset = bpy.data.objects["aim_offset_grp"]
        # check these var
        if not camera:
        # Shot type
        aim_location = data.get('shot_type').get(shot_type).get('aim_location')
        ## do the same .get for those below
        base_location = data['shot_type'][shot_type]['base_location'] 
        # set Z axis of aim_loc 
        aim.location[2] = aim_location
        # set Y axis of base_ctrl
        base_ctrl.location[1] = base_location
        # Angle type
        stand_scale = data['angle_type'][camera_angle_type]['stand_scale']  
        cam_rotation = data['angle_type'][camera_angle_type]['cam_rotation']
        aim_influence = data['angle_type'][camera_angle_type]['aim_influence']
        aim_rotation = data['angle_type'][camera_angle_type]['aim_rotation']

        camera.rotation_euler[0] = 0
        stand_ctrl.scale[1] = stand_scale
        aim_offset.constraints["Track To"].influence = aim_influence
        camera.rotation_euler[2] = cam_rotation
        aim_offset.rotation_euler[0] = aim_rotation


    def save_as_with_name(output_path,scene_nr,shot_id):
        """Save given result to output_file

        Parameters
        ----------
        output_path: str
            Output file's name
        """
        if not output_path or not os.path.exists(os.path.dirname(output_path)):
            raise ValueError("invalid output file")
        file_name = os.path.join(output_path, f"{scene_nr}_{shot_id}_Previs.blend")
        bpy.ops.wm.save_as_mainfile(filepath=file_name)  # pylint: disable=I1101


    def setup_shot(line,output_path):
        """
        Setup shot from camera preset and save file.

        bla bla bla

        Parameters
        ----------
        line : dict
            Shot line parsed from script
        output_path : str
            Output dir to save files

        returns
        -------
        none
        """
        # Check params
        if not line:
            return
        
        shot_type = line.get('shot_type')
        camera_angle_type = line.get('camera_angle_type')
        scene_nr = line.get('scene_nr')
        shot_id = line.get('shot_id')
        if not shot_type or not camera_angle_type or not scene_nr or not shot_id:
            raise ValueError(f"Invalid data{line}")
        preset_camera(shot_type,camera_angle_type)
        save_as_with_name(output_path,scene_nr,shot_id)
    

    def load_blend_file(blender_file):
        """
        Load existing .blend file. Copied from DJ

        Parameters
        ----------
        blender_file : str
            Blender file to open (.blend)
        """
        # Check params
        if not os.path.isfile(blender_file):
            raise ValueError(f"invalid input file {blender_file}")

        # TODO: Empty the scene (clear the default cube, camera, light)
        # Note: bpy.ops.wm.read_homefile(use_empty=True) doesn't work
        # because it deletes the context leading to a runtime error
        bpy.ops.object.select_all(action="DESELECT")

        with bpy.data.libraries.load(blender_file) as (data_from, data_to):
            for attr in dir(data_to):
                if attr in ["objects", "scenes"]:
                    setattr(data_to, attr, getattr(data_from, attr))

        for obj in data_to.objects:
            bpy.context.collection.objects.link(obj)    


    def setup_shots(input_file,blender_file,output_path):
        # Check params
        if not os.path.exists(input_file):
            raise ValueError("Input file not found")    
        if not os.path.exists(blender_file):
            raise ValueError("Model blender file not found")   
        if not os.path.exists(output_path):
            raise ValueError("Output path not found")  
        

        # TODO: Empty scene
        bpy.ops.object.select_all(action="DESELECT")
        for name in ["Cube", "Camera", "Light"]:
            bpy.data.objects[name].select_set(True)
            bpy.ops.object.delete()
        # load asset as blend file (look into load more types)
        load_blend_file(blender_file)
        # add camera rig
        camera_setup.add_camera()
        # read jsonl
        try:
            with open(input_file) as json_file:
                data = json_file.readlines()
                json_file.close()
        except OSError:
            raise ValueError(f"invalid input path")
        lines = []
        for line in data:
            lines.append(json.loads(line))

        for line in lines:
            setup_shot(line,output_path)
  

def _handle_args(args):
    """
    Extract command line args and call delegate function.

    This handler keeps the delegate function clean from command line
    specifics to be more reusable and testable.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments
    """
    return setup_shots(args.input_file,
                       args.blender_file,
                 args.output_path
                )


def main(args=None):
    """
    Parse command line args and call handler when run as a script.

    This function is the main entry point when run as a script. It
    adds a command line parser and args, then parses the command
    line and calls the default handler.

    Parameters
    ----------
    args : list
        Command line arguments as a list of strings [optional]
    """
    # Add parser args and default handler
    parser = ArgParseBlender()
    parser.add_argument("-i", "--input_file", type=str,
                        required=True,
                        help="Input files to load")
    parser.add_argument("-b", "--blender_file", type=str,
                        help="Input files to load")
    parser.add_argument("-o", "--output_path", type=str,
                        help="Output blender file name")

    parser.set_defaults(func=_handle_args)

    # Parse args or command line if none
    args = parser.parse_args()

    # Call args default handler
    args.func(args)


# Call main entry point when run as a script, not when imported
if __name__ == "__main__":
    main()
