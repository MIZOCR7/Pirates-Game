from settings import *
from os import walk
from os.path import dirname, join


def import_image(*path, alpha = True, format = 'png'):
  full_path = join(dirname(__file__), *path)
  return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).conver() 


def import_folder(*path):
  frames = []
  base_path = join(dirname(__file__), *path)
  for folder_path, subfolders, image_names in walk(base_path):
    for image_name in sorted(image_names, key = lambda name: int(name.split('.')[0])):
      full_path = join(folder_path, image_name)
      frames.append(pygame.image.load(full_path).convert_alpha())
    
  return frames

def import_folder_dict(*path):
  frame_dict = {}
  for folder_path, _, image_names in walk(join(*path)):
    for image_name in image_names:
      full_path = join(folder_path, image_name)
      surface = pygame.image.load(full_path).convert_alpha()
      frame_dict[image_name.split('.')[0]] = surface
  
  return frame_dict
  

def import_sub_folders(*path):
  frame_dict = {}
  base_path = join(dirname(__file__), *path) 
  for _, sub_folders, __ in walk(base_path):
    if sub_folders:
      for sub_folder in sub_folders:
        frame_dict[sub_folder] = import_folder(*path, sub_folder)
      break 
  
  return frame_dict
