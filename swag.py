import os
import numpy as np

#from terrain import *
from terrain_optimized import *
from util_functions import *

def main():
    print("yolo and swag")
    terrain_rules = parse_rules("terrain_rules.txt")
    vis_file = make_dir("./visualizations/map_*.png")
    world = generate_world(terrain_rules, size=1000)
    world.generate_image(vis_file)
   

if __name__ == "__main__":
    main()
    
    
    
