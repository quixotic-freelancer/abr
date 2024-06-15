import sys
import random
import numpy as np
from PIL import Image

class World:
    def __init__(self, terrain_dicts, size, blob_rate=0.9, blob_percent = 0.9, blob_depth_range = (2,5)):
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
        
        self.set_seed_chunks([(self.size*0.5, self.size*0.5),(self.size*0.01, self.size*0.01),(self.size*0.99, self.size*0.01),(self.size*0.01, self.size*0.99),(self.size*0.99, self.size*0.99)],["lava","ocean","ocean","ocean","ocean"])
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
            current_type = parent_chunk.type
            current_chunk = TerrainChunk(self, current_pos, current_type, health = current_health)
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
        print("current chunks: " + str(len(self.current_chunks)))
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
        
    def generate_image(self, path):
        image_array = np.zeros((self.size,self.size,3), dtype=np.uint8)
        for x in range(self.size):
            for y in range(self.size):
                image_array[x][y]=self.number_dict[self.terrain_array[x][y]]["color"]
                
        im = Image.fromarray(image_array)
        im.save(path)
        
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
    def __init__(self, world, position, type, health = 100.0):
        self.world = world
        self.position = position
        self.type = type
        self.exists = True
        self.health = health
                       
        self.chunk_value = self.world.type_dict[self.type]["number"]
        self.chunk_decay_rate = self.world.type_dict[self.type]["decay_rate"]
        self.available_neighbor_indices = [0,1,2,3,4,5,6,7]
        self.neighboring_values = []
        
        if self.health <= 0:
            self.determine_new_type()
     
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
        possible_types = self.world.type_dict[current_type]["rules"]
        
        
        for value in self.neighboring_values:
            neighboring_type = self.world.number_dict[value]["type"]
            if neighboring_type is not None:
                possible_types.setdefault(neighboring_type, 0)
                possible_types[neighboring_type]+=1
        
        random_type_list = []
        for type in possible_types.keys():
            random_type_list.extend([type]*possible_types[type])
         
        random.shuffle(random_type_list)
        
        new_type = random.choice(random_type_list)
        #new_type =  max(set(random_type_list), key=random_type_list.count)
        #return new_type
        self.type = new_type
        self.health = 100.0
  
    def add_to_world(self):
        self.world.set_value(self.position, self.chunk_value)


def generate_world(terrain_dicts, size=10):
    #sys.setrecursionlimit(size**3)
    sys.setrecursionlimit(2147483647)
    world = World(terrain_dicts, size)
    return world