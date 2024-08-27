from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from enum import Enum
import random

class node_type(Enum):
    NONE = 0
    SOURCE = 1
    RIVER = 2
    LAKE = 3
    VOID = 4

class dir(Enum):
    NONE = (0, 0)
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    NE = (1, -1)
    NW = (-1, -1)
    SE = (1, 1)
    SW = (-1, 1)

class map_point:
    def __init__(self, height, aridity, point_type, row, col):
        self.height = height
        self.aridity = aridity
        self.point_type = point_type
        self.row = row
        self.col = col
    
class limnograph:
    def __init__(self, path_to_heightmap, path_to_ariditymap=None, output_path=None):
        self.path_to_heightmap = path_to_heightmap
        self.path_to_ariditymap = path_to_ariditymap
        self.rivers = []
        self.matrix = None # create logical matrix recording (height, aridity, river/node/none/lake, dir, x, y)
        self.heightmap = None
        self.ariditymap = None
        self.min_height=-1
        self.max_height=-1
        if output_path is None:
            self.output_path = path_to_heightmap + "/output"
        else:
            self.output_path = output_path

        

            
    def process_images(self, seed=None):
        #Verify/convert format - greyscale. no alpha (assume void or reject?); 
            #if ariditymap included, ensure same size as heightmap
        #iterate pixels of heightmap:
            #get min/max height
            #build nxm matrix for nxm pixel image
            #record (height=lightness value)
        #if ariditymap, iterate:
            #add data to matrix
        with Image.open(self.path_to_heightmap) as im:
            #Open Heightmap, convert to greyscale 8-bit and pre-process
            im = im.convert("L")
            blur = ImageFilter.GaussianBlur(2)
            im = im.filter(blur)

            self.matrix = np.array(im)
            self.matrix=self.matrix.astype('object') #Apparently casting PIL image to np array forces int8 by default
            # self.matrix.resize(len(self.matrix), len(self.matrix[0]), 6, refcheck=False)
            #Generate array of map_point objects representing each pixel with it's height
            for row_index, row in enumerate(self.matrix):
                for pixel_index, pixel in enumerate(row):
                    self.matrix[row_index][pixel_index] = map_point(pixel, 0, 0, row_index, pixel_index)
        #additionally encode aridity information if map is provided
        if self.path_to_ariditymap is not None:
            with Image.open(self.path_to_ariditymap) as im:
                for row_index, row in enumerate(self.matrix):
                    for pixel_index, pixel in enumerate(row):
                        self.matrix[row_index][pixel_index][1] = pixel[0]
        #identify the min and max heights on the map
        self.min_height = min([point.height for point in self.matrix.flatten()]) #use np max/min funcs?
        self.max_height = max([point.height for point in self.matrix.flatten()])


    def generate_sources(self, source_count, source_range_param=3):
        #Generate a number of river source points on the map. 
        # Limit them to the upper 1/nth elevation of the map where n = source_range_param
        generated = 0
        available_source_spots = [] 
        source_fraction = self.max_height//source_range_param
        source_range = (self.max_height-source_fraction,self.max_height)
        for row in self.matrix:
            for pixel in row:
                if (pixel.height >= source_range[0] and pixel.height <= source_range[1]) and pixel.row < len(self.matrix)-1 and pixel.col < len(self.matrix[0])-1 and pixel.row > 1 and pixel.col > 1:
                    available_source_spots.append([pixel.row, pixel.col])
        while generated < source_count and len(available_source_spots) > 0:
            new_source = random.choice(available_source_spots)
            available_source_spots.remove(new_source)
            generated += 1
            self.matrix[new_source[0]][new_source[1]].point_type = node_type.SOURCE.value           

    def generate_rivers(self):
        #wrapper to iterate over each source and call generate_river function
        for row in self.matrix:
            for pixel in row:
                if pixel.point_type == node_type.SOURCE.value:
                    self.generate_river(pixel)

    def generate_river(self, source, pathsize = None, seed = None):
        #trace river paths from source based on immediate discrete elevation change. 
        # Uses weighted random decisions to resolve ties and add variation
        ind = (source.row, source.col)
        #print("drawing river from source: " + str(ind))
        previous_dir = dir.NONE.value
        while True:
            dir_heights = {
            dir.NORTH.value  : self.matrix[ind[0]][ind[1]-1].height,
            dir.SOUTH.value  : self.matrix[ind[0]][ind[1]+1].height,
            dir.EAST.value  : self.matrix[ind[0]+1][ind[1]].height,
            dir.WEST.value  : self.matrix[ind[0]-1][ind[1]].height,
            dir.NE.value : self.matrix[ind[0]+1][ind[1]-1].height,
            dir.NW.value : self.matrix[ind[0]-1][ind[1]-1].height,
            dir.SE.value : self.matrix[ind[0]+1][ind[1]+1].height,
            dir.SW.value : self.matrix[ind[0]-1][ind[1]+1].height
            }
            if previous_dir == dir.NONE.value:
                lowest_dir = [key for key in dir_heights if all(dir_heights[temp] >= dir_heights[key] for temp in dir_heights)]
            else:
                lowest_dir = [key for key in dir_heights.copy().pop(self.opp_dir(previous_dir)) if all(dir_heights[temp] >= dir_heights[key] for temp in dir_heights)]


            
            if len(lowest_dir) == 1:
                ind = tuple(map(sum, zip(ind, lowest_dir[0])))
            elif len(lowest_dir) > 1:
                if previous_dir != dir.NONE.value and previous_dir in lowest_dir: # may change to not require prev in lowest
                    new_dir = random.choice(lowest_dir) #random.choice([random.choice(lowest_dir), previous_dir])
                else:
                    new_dir = random.choice(lowest_dir)
                ind = tuple(map(sum, zip(ind, new_dir)))
            #decide next step
            if ind[0] >= len(self.matrix)-1 or ind[1] >= len(self.matrix[0])-1:
                print("Hit edge of map... ending path")
                break
            elif dir_heights[lowest_dir[0]] > self.matrix[ind[0]][ind[1]].height:
                if random.randint(1,10) > 9:
                    print("Surroundings are higher... creating lake")
                    self.matrix[ind[0]][ind[1]].point_type = node_type.LAKE.value
                    break                
            #handle next step
            if self.matrix[ind[0]][ind[1]].point_type == node_type.RIVER.value or self.matrix[ind[0]][ind[1]].point_type == node_type.SOURCE.value:
                print("hit existing river... ending path")
                break
            elif self.matrix[ind[0]][ind[1]].height == self.min_height:
                print(f"hit lowest point ({self.matrix[ind[0]][ind[1]].height})... ending path")
                break
            print("new river point at " + str(ind))
            self.matrix[ind[0]][ind[1]].point_type = node_type.RIVER.value

    def opp_dir(direction):
        #helper: returns the opposite cardinal direction from the argument
        return (direction[0] * -1, direction[1] * -1)



    def render(self, scale=None):
        #using the pre-generated rivers and sources, reconstruct an image and save to file. Display to user.
        river_image = Image.new("RGBA", (len(self.matrix), len(self.matrix[0])), "#ffff5500")
        renderer = ImageDraw.Draw(river_image)
        for row in self.matrix:
            for pixel in row:
                if pixel.point_type == node_type.RIVER.value:
                    #print("drawing point " + str([(pixel[4], pixel[5])]))
                    #renderer.line([(pixel[4], pixel[5]), (pixel[4]+1, pixel[5]+1)], "#FF00FFFF", 3)
                    renderer.point([(pixel.row, pixel.col)], "#FF00FFFF")
                elif pixel.point_type == node_type.LAKE.value:
                    renderer.point([(pixel.row, pixel.col)], "#FFFF00FF")
                elif pixel.point_type == node_type.SOURCE.value:
                    renderer.point([(pixel.row, pixel.col)], "#00FFFFFF")
        with Image.open(self.path_to_heightmap) as output:
            output = output.convert("RGBA")
            output.paste(river_image, (0,0), mask=river_image)
            output.show()
            output.save(self.output_path)

    def render_sources(self):
        #produce image only showing sources
        river_image = Image.new("RGBA", (len(self.matrix), len(self.matrix[0])), "#ffff5500")
        renderer = ImageDraw.Draw(river_image)
        for row in self.matrix:
            for pixel in row:
                if pixel.point_type == node_type.SOURCE.value:
                    #print("drawing point " + str([(pixel[4], pixel[5])]))
                    renderer.point([(pixel.row, pixel.col)], "#FF00FFFF")
        with Image.open(self.path_to_heightmap) as output:
            output = output.convert("RGBA")
            output.paste(river_image, (0,0), mask=river_image)
            output.show()


    def printarray(self):
        #debug helper function
        print(self.max_height)
        for row in self.matrix:
            for pixel in row:
                if pixel.point_type == node_type.SOURCE.value:
                    print(pixel)
