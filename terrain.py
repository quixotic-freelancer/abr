import sys
import random
import numpy as np
from PIL import Image

class World:
    def __init__(self, size):
        self.size = size
        self.terrain_array = np.zeros((self.size,self.size), dtype=float)
        self.calculated_indices = []
        
        self.set_seed_chunk((self.size//2, self.size//2))
        
    def set_seed_chunk(self, position, type="lava"):
        print("Setting seed chunk at: " + str(position))
        self.seed_chunk = TerrainChunk(self, position, type)
        self.seed_chunk.add_to_world()
        self.seed_chunk.update_neighbor_indices()
        self.seed_chunk.propagate()
        
    def set_value(self, position, value):
        self.terrain_array[position[0]][position[1]]=value
        self.calculated_indices.append(position)
        
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
        terrain_colors = {12.0: (245, 177, 5), 11.0: (56, 38, 31), 10.0:(105, 98, 79), 9.0:(227, 232, 155), 8.0:(191, 224, 119), 7.0:(65, 145, 28), 6.0:(245, 242, 196), 5.0: (247, 229, 183), 4.0: (220, 250, 236), 3.0: (245, 254, 254), 2.0: (10,215,86), 1.0: (0,104,149)}
        image_array = np.zeros((self.size,self.size,3), dtype=np.uint8)
        
        for x in range(self.size):
            for y in range(self.size):
                image_array[x][y]=terrain_colors[self.terrain_array[x][y]]
                
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
        
        self.value_to_terrain = {12.0: "lava", 11.0: "burnt_rock", 10.0: "rock", 9.0: "plains", 8.0: "shrubs", 7.0: "forest", 6.0: "dry", 5.0: "desert", 4.0: "cold", 3.0: "glacier", 2.0: "shallows", 1.0: "ocean", None: None}
        self.possible_terrain = {"lava": {"number":12.0, "decay_rate":10.0},
                                 "burnt_rock": {"number":11.0, "decay_rate":20.0},
                                 "rock": {"number":10.0, "decay_rate":5.0},
                                 "plains": {"number":9.0, "decay_rate":3.0},
                                 "shrubs": {"number":8.0, "decay_rate":8.0},
                                 "forest": {"number":7.0, "decay_rate":4.0},
                                 "dry": {"number":6.0, "decay_rate":8.0},
                                 "desert": {"number":5.0, "decay_rate":4.0},
                                 "cold": {"number":4.0, "decay_rate":8.0},
                                 "glacier": {"number":3.0, "decay_rate":4.0},
                                 "shallows": {"number":2.0, "decay_rate":15.0},
                                 "ocean": {"number":1.0, "decay_rate":1.0}}
                                 
        self.transition_rules = {"lava": {"lava":0, "burnt_rock":9, "rock":0, "plains":0, "shrubs":0, "forest":0, "dry":0, "desert":0, "cold":0, "glacier":0, "shallows":0, "ocean":0},
                                 "burnt_rock": {"lava":1, "burnt_rock":0, "rock":9, "plains":0, "shrubs":0, "forest":0, "dry":0, "desert":0, "cold":0, "glacier":0, "shallows":0, "ocean":0},
                                 "rock": {"lava":0, "burnt_rock":1, "rock":0, "plains":10, "shrubs":0, "forest":0, "dry":10, "desert":0, "cold":4, "glacier":0, "shallows":0, "ocean":0},
                                 "plains":  {"lava":0, "burnt_rock":0, "rock":2, "plains":0, "shrubs":10, "forest":0, "dry":5, "desert":0, "cold":5, "glacier":0, "shallows":5, "ocean":0},
                                 "shrubs":  {"lava":0, "burnt_rock":0, "rock":0, "plains":2, "shrubs":0, "forest":10, "dry":2, "desert":0, "cold":0, "glacier":0, "shallows":1, "ocean":0},
                                 "forest":  {"lava":0, "burnt_rock":0, "rock":0, "plains":0, "shrubs":8, "forest":0, "dry":0, "desert":0, "cold":0, "glacier":0, "shallows":0, "ocean":0},
                                 "dry": {"lava":0, "burnt_rock":0, "rock":0, "plains":5, "shrubs":1, "forest":0, "dry":0, "desert":10, "cold":1, "glacier":0, "shallows":0, "ocean":0},
                                 "desert": {"lava":0, "burnt_rock":0, "rock":5, "plains":0, "shrubs":0, "forest":0, "dry":5, "desert":0, "cold":0, "glacier":0, "shallows":0, "ocean":0},
                                 "cold":  {"lava":0, "burnt_rock":0, "rock":0, "plains":1, "shrubs":0, "forest":0, "dry":2, "desert":0, "cold":0, "glacier":10, "shallows":1, "ocean":0},
                                 "glacier":  {"lava":0, "burnt_rock":0, "rock":0, "plains":0, "shrubs":0, "forest":0, "dry":0, "desert":0, "cold":4, "glacier":0, "shallows":1, "ocean":0},
                                 "shallows": {"lava":0, "burnt_rock":0, "rock":0, "plains":2, "shrubs":2, "forest":0, "dry":2, "desert":0, "cold":2, "glacier":0, "shallows":0, "ocean":10},
                                 "ocean":  {"lava":0, "burnt_rock":0, "rock":0, "plains":0, "shrubs":0, "forest":0, "dry":0, "desert":0, "cold":0, "glacier":0, "shallows":5, "ocean":10}}
                                 
        self.chunk_value = self.possible_terrain[self.type]["number"]
        self.chunk_decay_rate = self.possible_terrain[self.type]["decay_rate"]
        self.chunk_neighbors = [None]*8
        self.available_neighbor_indices = [0,1,2,3,4,5,6,7]
        self.neighboring_values = []
        
        #self.update_neighbor_indices()
        
    def update_neighbor_indices(self):
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
                
    def determine_new_type(self):
        current_type = self.type
        possible_types = self.transition_rules[current_type]
        for value in self.neighboring_values:
            neighboring_type = self.value_to_terrain[value]
            if neighboring_type is not None:
                possible_types[neighboring_type]+=1
        
        random_type_list = []
        for type in possible_types.keys():
            random_type_list.extend([type]*possible_types[type])
         
        random.shuffle(random_type_list)
        
        new_type = random.choice(random_type_list)
        #new_type =  max(set(random_type_list), key=random_type_list.count)
        return new_type
            
            
        
    def add_to_world(self):
        self.world.set_value(self.position, self.chunk_value)
    
    def propagate(self):
        neighboring_positions = [(self.position[0],self.position[1]-1), (self.position[0]+1,self.position[1]-1), (self.position[0]+1,self.position[1]), (self.position[0]+1,self.position[1]+1), (self.position[0],self.position[1]+1), (self.position[0]-1,self.position[1]+1), (self.position[0]-1,self.position[1]), (self.position[0]-1,self.position[1]-1)]
        chunks_to_propagate = []
        
        
        
        for ind in self.available_neighbor_indices:
            neighbor_pos = neighboring_positions[ind]
            if neighbor_pos not in self.world.calculated_indices:
                
                neighbor_health = self.health - self.chunk_decay_rate
                neighbor_type = self.type
                
                #print("calculating chunk at: " + str(neighbor_pos))
                
                if neighbor_health <= 0.0:
                    neighbor_type= self.determine_new_type()
                    neighbor_health = 100
                
                neighbor_chunk = TerrainChunk(self.world, neighbor_pos, neighbor_type, health = neighbor_health)
                neighbor_chunk.add_to_world()
                chunks_to_propagate.append(neighbor_chunk)
                
                num_completed_chunks = np.count_nonzero(self.world.terrain_array)
                print("Completed " + str(num_completed_chunks) + " of " + str(self.world.size**2))
                #neighbor_chunk.propagate()

        if len(chunks_to_propagate) > 0:
            #print("Indices to calculate: " + str(list([chunk.position for chunk in chunks_to_propagate])))
            for chunk in chunks_to_propagate:
                chunk.update_neighbor_indices()
            
            random.shuffle(chunks_to_propagate)
            for chunk in chunks_to_propagate:
                if len(chunk.available_neighbor_indices) > 0:
                    chunk.propagate()


def generate_world(size=50):
    #sys.setrecursionlimit(size**3)
    sys.setrecursionlimit(2147483647)
    world = World(size)
    return world