from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Spike, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Tooth, Shell, Pearl

class Level:
  def __init__(self, tmx_map, level_frames, data):
    self.display_surface = pygame.display.get_surface()
    self.data = data 
    
    self.level_width = tmx_map.width * TILE_SIZE
    self.level_bottom = tmx_map.height * TILE_SIZE
    tmx_level_properties = tmx_map.get_layer_by_name('Data')[0].properties
    bg_prop = tmx_level_properties.get('bg')
    bg_key = str(bg_prop) if bg_prop is not None else None
    if bg_key and bg_key in level_frames['bg_tiles']:
        bg_tile = level_frames['bg_tiles'][bg_key]
    elif level_frames['bg_tiles']:
        bg_tile = list(level_frames['bg_tiles'].values())[0]
    else:
        bg_tile = None
    
    self.all_sprites = AllSprites(tmx_map.width, tmx_map.height, {'large': level_frames['cloud_large'], 'small': level_frames['cloud_small']}, tmx_level_properties['horizon_line'], None)
    self.collosion_sprites = pygame.sprite.Group()
    self.semi_collosion_sprites = pygame.sprite.Group()
    self.damage_sprites = pygame.sprite.Group()
    self.tooth_sprites = pygame.sprite.Group() 
    self.pearl_sprites = pygame.sprite.Group() 
    self.item_sprites = pygame.sprite.Group() 
    
    self.setup(tmx_map, level_frames) 
    
    self.pearl_surf = level_frames['pearl']
    self.particle_surf = level_frames['particle']
    
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
              frames = level_frames['player'],
              data=self.data, 
              ) 
          else: 
            if obj.name in ('barrel', 'crate'):
              Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collosion_sprites))
            elif obj.name == 'static':
              Sprite((obj.x, obj.y), obj.image, self.all_sprites, Z_LAYERS['bg details'])
            else:  
                frames = level_frames['palms'][obj.name] if 'palm' in obj.name else level_frames[obj.name] 
                z = Z_LAYERS['bg details'] if layer_name == 'BG details' else Z_LAYERS['main']
                AnimatedSprite((obj.x, obj.y), frames, self.all_sprites, z)
            
          if obj.name == 'flag':
             self.level_finish_rect = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))
      
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
    
    for obj in tmx_map.get_layer_by_name('Items'):
      Item(obj.name, (obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2), level_frames['items'][obj.name], (self.all_sprites, self.item_sprites), self.data) 
    
    
    for obj in tmx_map.get_layer_by_name('Water'):
      rows  = int(obj.height / TILE_SIZE)
      cols  = int(obj.width / TILE_SIZE) 
      for row in range(rows):
        for col in range(cols):
          x = obj.x + col * TILE_SIZE
          y = obj.y + row * TILE_SIZE 
          if row == 0:
            AnimatedSprite((x,y), level_frames['water_top'], self.all_sprites, Z_LAYERS['water'])
          else:
            Sprite((x,y), level_frames['water_body'], self.all_sprites, Z_LAYERS['water']) 
    
    
  def create_pearl(self, pos, direction):
    Pearl(pos, (self.all_sprites, self.damage_sprites, self.pearl_sprites), self.pearl_surf, direction ,150)  
    
  def parel_collision(self):
    for sprite in self.collosion_sprites:
      sprite = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True) 
      if sprite:
        ParticleEffectSprite((sprite[0].rect.center), self.particle_surf, self.all_sprites) 
  
  def hit_collision(self):
    for sprite in self.damage_sprites:
      if sprite.rect.colliderect(self.player.hitbox_rect):
        self.player.get_damage() 
        if hasattr(sprite, 'pearl'):
          sprite.kill() 
          ParticleEffectSprite((sprite.rect.center), self.particle_surf, self.all_sprites)
  
  
  def item_collision(self):
    if self.item_sprites:
      item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True) 
      if item_sprites:
        item_sprites[0].active() 
        ParticleEffectSprite((item_sprites[0].rect.center), self.particle_surf, self.all_sprites) 
        
  
  def attack_collision(self):
    for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites():
      facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or\
        self.player.rect.centerx > target.rect.centerx and not self.player.facing_right 
      if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
        target.reverse() 
  
  
  def check_constraint(self):
    if self.player.hitbox_rect.left <= 0:
      self.player.hitbox_rect.left = 0
    if self.player.hitbox_rect.right >= self.level_width:
      self.player.hitbox_rect.right = self.level_width 
      
    if self.player.hitbox_rect.bottom > self.level_bottom:
      pass 
    
    if self.player.hitbox_rect.colliderect(self.level_finish_rect):
      print('sucess')
    
  
  def run(self, dt):
    self.display_surface.fill("black") 
    
    self.all_sprites.update(dt)
    self.parel_collision() 
    self.hit_collision() 
    self.item_collision() 
    self.attack_collision() 
    self.check_constraint()
    self.all_sprites.draw(self.player.hitbox_rect.center, dt) 
    
  
  

