import os
import time
import numpy as np

TERRAIN_MODE = 1

if TERRAIN_MODE == 0:
    from terrain import *
else:
    from terrain_optimized import *
    
from util_functions import *

def main():
    debug_mode = True
    terrain_version = TERRAIN_MODE
    
    print("yolo and swag")
    terrain_rules = parse_rules("terrain_rules.txt")
    vis_file = make_dir("./visualizations/map_*.png")
    
    if terrain_version == 0:
        world = generate_world(terrain_rules, size=200)
        world.generate_image(vis_file)
    else:
        start = time.time()
        world = generate_world(terrain_rules, size=1000)
        end = time.time()
        
        if debug_mode:
            world.generate_image(vis_file, count_time = end-start, save_world=True)
        else:
            world.generate_image(vis_file, count_time = None, save_world=True)
            
        
   

if __name__ == "__main__":
    main()
    
    
    
