import sys
import math
import random
import numpy as np
from PIL import Image

class World:
    def __init__(self, terrain_dicts, size, blob_rate=1.0, blob_percent = 0.9, blob_depth_range = (2,5), decay_modifier = 0.1):
        self.type_dict = terrain_dicts[0]
        self.number_dict = terrain_dicts[1]
        
        self.size = size
        self.terrain_array = np.zeros((self.size,self.size), dtype=float)
        self.seed_chunk = None
        
        self.blob_rate=blob_rate
        self.blob_percent=blob_percent
        self.blob_depth_range=blob_depth_range
        
        self.dead_chunks = []
        self.parent_chunks = []
        self.current_chunks = []
        self.next_chunks = []
        
        #elf.set_seed_chunks([(self.size*0.5, self.size*0.5),(self.size*0.01, self.size*0.01),(self.size*0.99, self.size*0.01),(self.size*0.01, self.size*0.99),(self.size*0.99, self.size*0.99)],["lava","deep_ocean","deep_ocean","deep_ocean","deep_ocean"])
        #self.set_seed_chunks([(self.size*0.5, self.size*0.5)],["lava"])
        
        #set random chunks
        seed_types = ["lava"]
        seed_position_list = [(self.size*random.uniform(0.3,0.7), self.size*random.uniform(0.3,0.7)) for type in seed_types]
        seed_position_list[0] = (self.size*0.5, self.size*0.5)
        self.decay_modifier = decay_modifier#len(seed_types)/2
        self.set_seed_chunks(seed_position_list, seed_types)
        
        self.propagate_from_seed(0)
        
    def set_seed_chunks(self, positions, types):
        for i, position in enumerate(positions):
            position = (int(position[0]),int(position[1]))
            print("Setting seed chunk at: " + str(position))
            self.seed_chunk = TerrainChunk(self, position, types[i])
            self.seed_chunk.add_to_world()
            
            self.parent_chunks.append(self.seed_chunk)
    
    def propagate_helper(self, parent_chunk, return_mode = False):
        new_chunks = []
        current_chunk_positions = parent_chunk.calculate_neighbor_positions()
        for current_pos in current_chunk_positions:
            current_health = parent_chunk.health - parent_chunk.chunk_decay_rate
            #elevation_scale = self.type_dict[parent_chunk.type]["elevation_rule"]["hp_to_elevation"]*(math.log(10.0/(abs(current_pos[0]-self.size/2.0)+(self.size*0.1)))*0.3)
            elevation_scale = self.type_dict[parent_chunk.type]["elevation_rule"]["hp_to_elevation"]*(math.log(abs(1.0/(current_pos[0]-self.size/2.0+0.1))))
            current_elevation = elevation_scale*current_health 
            current_type = parent_chunk.type
            current_chunk = TerrainChunk(self, current_pos, current_type, health = current_health, elevation = current_elevation, parent_chunk = parent_chunk)
            if parent_chunk.type == current_type:
                current_elevation += random.uniform(current_elevation*-0.1*elevation_scale,current_elevation*0.1*elevation_scale)
                current_chunk.set_elevation(current_elevation)
            current_chunk.add_to_world()
        
            if current_chunk not in self.current_chunks:
                self.current_chunks.append(current_chunk)
                new_chunks.append(current_chunk)
        if return_mode:
            return new_chunks
    
    def propagate_from_seed(self, depth):
        print("depth: " + str(depth))
        print("dead chunks: " + str(len(self.dead_chunks)))
        print("parent chunks: " + str(len(self.parent_chunks)))
        print("chunks remaining: " + str(self.size**2 - len(self.dead_chunks)))
        
        if len(self.parent_chunks) == 0:
            print("Completed recursion")
        else:
            print("Beginning new recursion")
            for parent_chunk in self.parent_chunks:
                self.propagate_helper(parent_chunk)
   
            blob_chance = random.uniform(0,1)
            if blob_chance <= self.blob_rate:
                num_blobs = int(len(self.current_chunks)*self.blob_percent)
                for blob in range(num_blobs):
                    new_parent_chunks = []
                    new_parent_chunk = random.choice(self.current_chunks)
                    blob_chunks = self.propagate_helper(new_parent_chunk, return_mode = True)
                    new_parent_chunks.append(new_parent_chunk)
                    
                    depth = random.randint(self.blob_depth_range[0],self.blob_depth_range[1])
                    for i in range(depth):
                        if len(blob_chunks) == 0:
                            break
                        new_parent_chunk = random.choice(blob_chunks)
                        blob_chunks = self.propagate_helper(new_parent_chunk, return_mode = True)
                        new_parent_chunks.append(new_parent_chunk)

                    self.parent_chunks.extend(new_parent_chunks)
                    for new_parent_chunk in new_parent_chunks:
                        self.current_chunks.remove(new_parent_chunk)
                        
                    
            self.dead_chunks.extend(self.parent_chunks)
            self.parent_chunks = [chunk for chunk in self.current_chunks]
            
            random.shuffle(self.parent_chunks)
            
            self.current_chunks = []
            self.propagate_from_seed(depth+1)
        
        
        
    def set_value(self, position, value):
        self.terrain_array[position[0]][position[1]]=value
        #self.calculated_indices.append(position)
        
    def get_value(self, position):
        return self.terrain_array[position[0]][position[1]]
            
    def get_adjacent_values(self, position):
        check_indices = [(position[0],position[1]-1), (position[0]+1,position[1]-1), (position[0]+1,position[1]), (position[0]+1,position[1]+1), (position[0],position[1]+1), (position[0]-1,position[1]+1), (position[0]-1,position[1]), (position[0]-1,position[1]-1)]
        adjacent_values = []
        for index_tuple in check_indices:
            check_x, check_y = index_tuple
            if check_x >=0 and check_x <= self.size-1 and check_y >= 0 and check_y <= self.size-1:
                checked_val = self.terrain_array[check_x][check_y]
                if checked_val != 0.0:
                    adjacent_values.append(checked_val)
                else:
                    adjacent_values.append(None)
            else:
                adjacent_values.append(None)
        
        return adjacent_values
        
    def generate_image(self, path, count_time=None, save_world=True):
        image_array = np.zeros((self.size,self.size,3), dtype=np.uint8)
        for x in range(self.size):
            for y in range(self.size):
                elevation_difference = self.terrain_array[x][y] - int(self.terrain_array[x][y])
                tile_type_value = float(int(self.terrain_array[x][y]))
                
                color_modifier = 1.0+(elevation_difference/2)
                max_color_modifier = 1.0+(0.9/2)
                
                image_array[x][y]=self.number_dict[tile_type_value]["color"]
                image_array[x][y]=[int(max(0,min((c*(color_modifier),255)))) for c in self.number_dict[tile_type_value]["color"]]
                
        im = Image.fromarray(image_array)
        im.save(path)
        
        if count_time is not None:
            time_path = path.replace("png", "txt")
            time_file = open(time_path,"w")
            time_file.write(str(count_time)+" seconds\n")
            time_file.write("blob_rate: "+str(self.blob_rate))
            time_file.write("\nblob_percent: "+str(self.blob_percent))
            time_file.write("\nblob_depth_range: "+str(self.blob_depth_range))
            time_file.write("\ndecay_modifier: "+str(self.decay_modifier))
            time_file.write("\nsize: "+str(self.size))
            
            time_file.write("\n\n\nTERRAIN RULES\n")
            terrain_rules = open("terrain_rules.txt", "r")
            terrain_rules_lines = terrain_rules.readlines()
            for line in terrain_rules_lines:
                time_file.write(line)
            terrain_rules.close()
            
            time_file.close()
            
        if save_world == True:
            with open( path.replace("png", "npy"), 'wb') as f:
                np.save(f, self.terrain_array)
            f.close()
        
#####################################################
#####################################################
################### Chunk Diag ######################
#####################################################
########  Neighbor 7, Neighbor 0, Neighbor 1 ########
########  Neighbor 6,   Chunk   , Neighbor 2 ########
########  Neighbor 5, Neighbor 4, Neighbor 3 ########
#####################################################
#####################################################
#####################################################
 
class TerrainChunk:
    def __init__(self, world, position, type, health = 100.0, elevation = 100.0, parent_chunk = None):
        self.world = world
        self.position = position
        self.type = type
        self.exists = True
        self.health = health
        self.elevation = elevation
        self.parent_chunk = parent_chunk
        self.return_type = None
            
        self.chunk_value = self.world.type_dict[self.type]["number"]
        self.chunk_decay_rate = self.world.type_dict[self.type]["decay_rate"]*self.world.decay_modifier
        self.available_neighbor_indices = [0,1,2,3,4,5,6,7]
        self.neighboring_values = []
        
        if self.health <= 0:
            self.determine_new_type()
            
        ##apply region modifier to decay_rate
        cr_temp = self.world.type_dict[self.type]["region"]
        self.critical_regions = []
        if cr_temp is not None:
            for region_tuple in cr_temp:
                region, strength = region_tuple
                region_y_pos = None
                if region == "north":
                    region_y_pos = 0
                elif region == "north_center":
                    region_y_pos = self.world.size//4
                elif region == "equator":
                    region_y_pos = self.world.size//2
                elif region == "south_center":
                    region_y_pos = self.world.size-self.world.size//4
                elif region == "south":
                    region_y_pos = self.world.size
                else:
                    region_y_pos = None
                if region_y_pos is not None:
                    self.critical_regions.append((region_y_pos,strength))
                    
        ##determine closest critical region
        if len(self.critical_regions) > 0:

            y_pos, x_pos = self.position
            closest_dist = float('inf')
            region_strength = None
            for region_tuple in self.critical_regions:
                
                region_y_pos, strength = region_tuple
                dist=abs(y_pos-region_y_pos)
                if closest_dist >= dist:
                    closest_dist = dist
                    region_strength = strength

            distance_modifier = math.log(closest_dist/region_strength+0.001)
            self.chunk_decay_rate*=distance_modifier

            
        if self.chunk_decay_rate >= 100:
            self.determine_new_type()
            
    def set_elevation(self, new_elevation):
        self.elevation = new_elevation
        
    def calculate_neighbor_positions(self):
        #print("hello. updating neighbors for chunk at: " + str(self.position))
        x, y = self.position
        world_width = self.world.size
        world_height = self.world.size
        
        invalid_indices = []
        
        if x < 0 or x >= world_width:
            self.exists = False
        if y < 0 or y >= world_height:
            self.exists = False
        
        if self.exists:
            if x == 0:
                invalid_indices.extend([7,6,5])
            if x == world_width-1:
                invalid_indices.extend([1,2,3])
            if y == 0:
                invalid_indices.extend([7,0,1])
            if y == world_height-1:
                invalid_indices.extend([5,4,3])
                
            invalid_indices = list(set(invalid_indices))
            
            self.neighboring_values = self.world.get_adjacent_values(self.position)
            for i, value in enumerate(self.neighboring_values):
                if value is not None and i not in invalid_indices:
                    invalid_indices.append(i)
                    
            for ind in invalid_indices:
                if ind in self.available_neighbor_indices:
                    self.available_neighbor_indices.remove(ind)
        
        neighboring_positions = [(self.position[0],self.position[1]-1), (self.position[0]+1,self.position[1]-1), (self.position[0]+1,self.position[1]), (self.position[0]+1,self.position[1]+1), (self.position[0],self.position[1]+1), (self.position[0]-1,self.position[1]+1), (self.position[0]-1,self.position[1]), (self.position[0]-1,self.position[1]-1)]
        neighbor_coords = [neighboring_positions[ind] for ind in self.available_neighbor_indices]
        return neighbor_coords
                
    def determine_new_type(self):
        current_type = self.type
        
        if self.return_type is not current_type and self.return_type is not None:
            possible_types = self.world.type_dict[self.return_type]["rules"].copy()
        else:
            possible_types = self.world.type_dict[current_type]["rules"].copy()
        
        for value in self.neighboring_values:
            neighboring_type = self.world.number_dict[value]["type"]
            if neighboring_type is not None:
                possible_types.setdefault(neighboring_type, 0)
                possible_types[neighboring_type]+=1
        
        elevation_type_dict = self.world.type_dict[self.type]["elevation_rule"]["rules"]
        for elevation_type in elevation_type_dict.keys():
            possible_types.setdefault(elevation_type, 0)
            possible_types[elevation_type] += int(elevation_type_dict[elevation_type]*self.world.type_dict[self.type]["elevation_rule"]["elevation_impact"])
        
        random_type_list = []
        for type in possible_types.keys():
            random_type_list.extend([type]*possible_types[type])
         
        random.shuffle(random_type_list)
        
        new_type = random.choice(random_type_list)
        
        if new_type in elevation_type_dict.keys():
            self.return_type = self.parent_chunk.type
        elif new_type != current_type:
            self.return_type = new_type
            
        #new_type =  max(set(random_type_list), key=random_type_list.count)
        #return new_type
        self.type = new_type
        self.health = 100.0
  
    def add_to_world(self):
        elevation_value = min(0.99,max(0.0,self.elevation/100.0))
        self.world.set_value(self.position, self.chunk_value+elevation_value)


def generate_world(terrain_dicts, size=10):
    #sys.setrecursionlimit(size**3)
    sys.setrecursionlimit(2147483647)
    world = World(terrain_dicts, size)
    return world