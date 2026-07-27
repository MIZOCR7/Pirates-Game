from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite
from player import Player
from groups import AllSprites

class Level:
  def __init__(self, tmx_map, level_frames):
    self.display_surface = pygame.display.get_surface()
    
    
    self.all_sprites = AllSprites()
    self.collosion_sprites = pygame.sprite.Group()
    self.semi_collosion_sprites = pygame.sprite.Group()
    
    self.setup(tmx_map, level_frames) 
    
  def setup(self, tmx_map, level_frames):
    
    for layer in ['BG', "Terrain", "FG", "Platforms"]:
      for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
        groups = [self.all_sprites]
        if layer == 'Terrain': groups.append(self.collosion_sprites)
        if layer == 'Platforms': groups.append(self.semi_collosion_sprites)
        match layer: 
          case 'BG' : z = Z_LAYERS['bg tiles'] 
          case 'FG' : z = Z_LAYERS['fg']
          case _ : z = Z_LAYERS['main'] 
        Sprite((x * TILE_SIZE,y * TILE_SIZE), surf, groups, z) 
    
  
    for layer_name in ['Objects', 'Decorations']:
      if layer_name in [layer.name for layer in tmx_map.layers]:
        for obj in tmx_map.get_layer_by_name(layer_name): 
          if obj.name == 'player': 
            self.player = Player(
              pos = (obj.x, obj.y), 
              groups = self.all_sprites, 
              collosion_sprites = self.collosion_sprites, 
              semi_collosion_sprites = self.semi_collosion_sprites,
              frames = level_frames['player']) 
          else: 
            if obj.name in ('barrel', 'crate'):
              Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collosion_sprites))
            else:  
                frames = level_frames['palms'][obj.name] if 'palm' in obj.name else level_frames[obj.name] 
                AnimatedSprite((obj.x, obj.y), frames, self.all_sprites)
      
      
    for obj in (tmx_map.get_layer_by_name("Moving Objects")):
      if obj.name == 'helicopter':
        if obj.width > obj.height:
          move_dir = 'x'
          start_pos = (obj.x, obj.y + obj.height / 2)
          end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
        else:
          move_dir = 'y'
          start_pos = (obj.x + obj.width / 2, obj.y)
          end_pos = (obj.x + obj.width, obj.y + obj.height) 
        speed = obj.properties['speed']
        MovingSprite((self.all_sprites, self.semi_collosion_sprites), start_pos, end_pos, move_dir, speed) 
        
    
  def run(self, dt):
    self.display_surface.fill("black")
    self.all_sprites.update(dt)
    self.all_sprites.draw(self.player.hitbox_rect.center)
