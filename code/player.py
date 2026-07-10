from settings import *

class Player(pygame.sprite.Sprite):
  def __init__(self, pos, groups, collosion_sprites):
    super().__init__(groups)
    self.image = pygame.Surface((48,56))
    self.image.fill('red')
    
    self.rect = self.image.get_frect(topleft=pos)
    self.old_rect = self.rect.copy()
    
    self.direction = vector()
    self.speed = 200
    self.gravity = 1300
    
    self.collosion_sprites = collosion_sprites

  def input(self):
    keys = pygame.key.get_pressed()
    input_vector = vector(0,0) 
    if keys[pygame.K_d]:
      input_vector.x += 1
    if keys[pygame.K_a]:
      input_vector.x -= 1
    self.direction.x = input_vector.normalize().x if input_vector.x else input_vector.x
  
  def move(self, dt):
    self.rect.x += self.direction.x * self.speed * dt
    self.collosion('horizontal')
    
    self.direction.y += self.gravity * dt
    
    self.rect.y += self.direction.y * dt
    self.direction.y += self.gravity / 2 * dt 
    self.collosion('vertical')
  
  def collosion(self, axis):
    for sprite in self.collosion_sprites:
      if sprite.rect.colliderect(self.rect):
        if axis == 'horizontal':
          if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
            self.rect.left = sprite.rect.right
          
          if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
            self.rect.right = sprite.rect.left
        else:
          for sprite in self.collosion_sprites:
            if sprite.rect.colliderect(self.rect):
              if axis == 'vertical':
                if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                  self.rect.top = sprite.rect.bottom
                
                if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                  self.rect.bottom = sprite.rect.top 
                
                self.direction.y = 0
                
  def update(self, dt):
    self.old_rect = self.rect.copy()
    self.input()
    self.move(dt)
