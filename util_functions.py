import os
import ast

def make_dir(path):
    sub_paths = path.split("/")
    
    final_file = None
    if path[-1] != "/":
        final_file = sub_paths.pop()
    path = ""
    
    for sub_path in sub_paths:
        path+=sub_path+"/"
        if not os.path.exists(path):
            os.mkdir(path)
            
    if final_file is not None:
        if "_*" in final_file:
            present_files = list(os.listdir(path))
            max_num = 0
            for file in present_files:
                name,num_ext = file.split("_")
                num,ext = num_ext.split(".")
                if int(num) > max_num:
                    max_num = int(num)
            final_file = final_file.replace("*",str(max_num+1))
        path+=final_file
        
    return path
    
def parse_rules(path, delim="|"):
    file = open(path, "r")
    lines = file.readlines()
    file.close
    
    header = lines[0].strip()
    keys = header.split(delim)
    
    type_dict = {}
    number_dict = {}
    
    for line in lines[1:]:
        line = line.strip()
        data = line.split(delim)
        data[1] = float(data[1])
        data[2] = float(data[2])
        data[3]=ast.literal_eval(data[3])
        data[4]=ast.literal_eval(data[4])
        data[5]=ast.literal_eval(data[5])
        data[6]=ast.literal_eval(data[6])
        
        type_subdict = {}
        number_subdict = {}
        
        for i,key in enumerate(keys):
            if i != 0:
                type_subdict.setdefault(key,data[i])
            if i != 1:
                number_subdict.setdefault(key,data[i])
        
        type_dict.setdefault(data[0], type_subdict)
        number_dict.setdefault(data[1], number_subdict)
    return type_dict, number_dict