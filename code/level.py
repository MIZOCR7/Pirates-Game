from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Spike
from player import Player
from groups import AllSprites
from enemies import Tooth, Shell, Pearl

class Level:
  def __init__(self, tmx_map, level_frames):
    self.display_surface = pygame.display.get_surface()
    
    
    self.all_sprites = AllSprites()
    self.collosion_sprites = pygame.sprite.Group()
    self.semi_collosion_sprites = pygame.sprite.Group()
    self.damage_sprites = pygame.sprite.Group()
    self.tooth_sprites = pygame.sprite.Group() 
    self.pearl_sprites = pygame.sprite.Group() 
    
    self.setup(tmx_map, level_frames) 
    
    self.pearl_surf = level_frames['pearl']
    
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
    
  
    for layer_name in ['BG details', 'Objects', 'Decorations']:
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
            elif obj.name == 'static':
              Sprite((obj.x, obj.y), obj.image, self.all_sprites, Z_LAYERS['bg details'])
            else:  
                frames = level_frames['palms'][obj.name] if 'palm' in obj.name else level_frames[obj.name] 
                z = Z_LAYERS['bg details'] if layer_name == 'BG details' else Z_LAYERS['main']
                AnimatedSprite((obj.x, obj.y), frames, self.all_sprites, z)
      
      
    for obj in (tmx_map.get_layer_by_name("Moving Objects")):
      if obj.name == 'spike':
        Spike(
          pos = (obj.x + obj.width / 2, obj.y + obj.height / 2), 
          surf = level_frames['spike'], 
          radius = obj.properties['radius'],
          speed = obj.properties['speed'],
          start_angle = obj.properties['start_angle'],
          end_angle = obj.properties['end_angle'], 
          groups = (self.all_sprites, self.damage_sprites) 
        )
        for i in range(0, obj.properties['radius'], 20):
          Spike(
            pos = (obj.x + obj.width / 2, obj.y + obj.height / 2), 
            surf = level_frames['spike_chain'],
            radius = i,
            speed = obj.properties['speed'],
            start_angle = obj.properties['start_angle'],
            end_angle = obj.properties['end_angle'], 
            groups = self.all_sprites,
            z = Z_LAYERS['bg details'], 
            ) 
        
      else:
        frames = level_frames[obj.name] 
        groups = (self.all_sprites, self.semi_collosion_sprites) if obj.properties['platform'] else (self.all_sprites, self.damage_sprites) 
        
        if obj.width > obj.height: 
          move_dir = 'x'
          start_pos = (obj.x, obj.y + obj.height / 2)
          end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
        else:
          move_dir = 'y'
          start_pos = (obj.x + obj.width / 2, obj.y)
          end_pos = (obj.x + obj.width, obj.y + obj.height) 
        speed = obj.properties['speed']
        MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, obj.properties['flip']) 
        
  
        if obj.name == 'saw':
          if move_dir == 'x':
            y = start_pos[1] - level_frames['saw_chains'].get_height() / 2
            left, right = int(start_pos[0]), int(end_pos[0])  
            for x in range(left, right, 20):
              Sprite((x, y), level_frames['saw_chains'], self.all_sprites, Z_LAYERS['bg details'])  
        
          else:
            x = start_pos[0] - level_frames['saw_chains'].get_width() / 2
            top, bottom = int(start_pos[1]), int(end_pos[1])
            for y in range(top, bottom, 20):
              Sprite((x,y), level_frames['saw_chains'], self.all_sprites, Z_LAYERS['bg details']) 
    
    for obj in tmx_map.get_layer_by_name("Enemies"):
      if obj.name == 'tooth':
        Tooth((obj.x, obj.y), level_frames['tooth'], (self.all_sprites, self.damage_sprites, self.tooth_sprites), self.collosion_sprites)  
    
      if obj.name == 'shell':
        Shell((obj.x, obj.y), level_frames['shell'], (self.all_sprites, self.collosion_sprites), obj.properties['reverse'], self.player, self.create_pearl)  
  
  def create_pearl(self, pos, direction):
    Pearl(pos, (self.all_sprites, self.damage_sprites, self.pearl_sprites), self.pearl_surf, direction ,150)  
    
  def parel_collision(self):
    for sprite in self.collosion_sprites:
      pygame.sprite.spritecollide(sprite, self.pearl_sprites, True) 
      
  
  def hit_collision(self):
    for sprite in self.damage_sprites:
      if sprite.rect.colliderect(self.player.hitbox_rect):
        if hasattr(sprite, 'pearl'):
          sprite.kill() 
  
  
  def run(self, dt):
    self.display_surface.fill("black") 
    
    self.all_sprites.update(dt)
    self.parel_collision() 
    self.hit_collision() 
    
    self.all_sprites.draw(self.player.hitbox_rect.center) 
    
  
  

