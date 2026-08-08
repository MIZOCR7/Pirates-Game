from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import dirname, join
from data import Data 
from debug import debug
from ui import UI 
from world import World

from support import *



class Game: 
  def __init__(self):
    pygame.init()
    self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pirate World")
    self.clock = pygame.time.Clock()
    self.import_assets()
    self.ui = UI(self.font, self.ui_frames)
    self.data = Data(self.ui) 
    self.tmx_maps = {
      0: load_pygame(join(dirname(__file__), '..', 'data', 'levels', '0.tmx')),
      1: load_pygame(join(dirname(__file__), '..', 'data', 'levels', '1.tmx')),
      2: load_pygame(join(dirname(__file__), '..', 'data', 'levels', '2.tmx')),
      3: load_pygame(join(dirname(__file__), '..', 'data', 'levels', '3.tmx')),
      4: load_pygame(join(dirname(__file__), '..', 'data', 'levels', '4.tmx')),
      5: load_pygame(join(dirname(__file__), '..', 'data', 'levels', '6.tmx')),
      } 
    self.tmx_overworld = load_pygame(join(dirname(__file__), '..', 'data', 'overworld', 'overworld.tmx'))
    self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.audio_files, self.data, self.switch_stage) 
    
    self.bg_music.play(-1)
    
  def switch_stage(self, target, unlock = 0):
    if target == 'level':
      self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
      
    else:
      if unlock > 0:
        self.data.unlocked_level = unlock
      else:
        self.data.health -= 1
        self.audio_files['health'].set_volume(0.4)
        self.audio_files['health'].play()
      self.current_stage = World(self.tmx_overworld, self.data, self.overworld_frames, self.switch_stage)
      
  
  
  def import_assets(self):
    self.level_frames = {
            'flag': import_folder('..', 'graphics', 'level', 'flag'),
            'saw': import_folder('..', 'graphics', 'enemies', 'saw', 'animation'),
            'floor_spike': import_folder('..', 'graphics', 'enemies', 'floor_spikes'),
            'palms': import_sub_folders('..', 'graphics', 'level', 'palms'),
            'candle': import_folder('..', 'graphics', 'level', 'candle'),
            'window': import_folder('..', 'graphics', 'level', 'window'),
            'big_chain': import_folder('..', 'graphics', 'level', 'big_chains'),
            'small_chain': import_folder('..', 'graphics', 'level', 'small_chains'),
            'candle_light': import_folder('..', 'graphics', 'level', 'candle_light'),
            'player': import_sub_folders('..', 'graphics', 'player'),
            'helicopter': import_folder('..', 'graphics', 'level', 'helicopter'),
            'boat': import_folder('..', 'graphics', 'objects', 'boat'), 
            'saw_chains': pygame.image.load(join(dirname(__file__), '..', 'graphics', 'enemies', 'saw', 'saw_chain.png')).convert_alpha(),
            'spike': import_image('..', 'graphics', 'enemies', 'spike_ball', 'Spiked Ball.png'), 
            'spike_chain': import_image('..', 'graphics', 'enemies', 'spike_ball', 'spiked_chain.png'), 
            'tooth': import_folder('..', 'graphics', 'enemies', 'tooth', 'run'), 
            'shell': import_sub_folders('..', 'graphics', 'enemies', 'shell'), 
            'pearl': import_image('..', 'graphics', 'enemies', 'bullets', 'pearl.png'), 
            'items': import_sub_folders('..', 'graphics', 'items'), 
            'particle': import_folder('..', 'graphics', 'effects', 'particle'), 
            'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
            'water_body': import_image('..', 'graphics', 'level', 'water', 'body.png'), 
            'bg_tiles': import_folder_dict('..', 'graphics', 'level', 'bg', 'tiles'), 
            'cloud_small': import_folder('..', 'graphics', 'level', 'clouds', 'small'),
            'cloud_large': import_image('..', 'graphics', 'level', 'clouds', 'large_cloud.png'),
             
    }
    
    self.font = pygame.font.Font(join(dirname(__file__), '..', 'graphics', 'ui', 'RUNESCAPE_UF.ttf'), 40)
    self.ui_frames = {
      'heart': import_folder('..', 'graphics', 'ui', 'heart'), 
      'coin': import_image('..', 'graphics', 'ui', 'coin.png'),
    }
    
    self.overworld_frames = {
      'palm': import_folder('..', 'graphics', 'overworld', 'palm'),
      'water': import_folder('..', 'graphics', 'overworld', 'water'), 
      'path': import_folder_dict('..', 'graphics', 'overworld', 'path'),
      'icon': import_sub_folders('..', 'graphics', 'overworld', 'icon'),
    }
    
    self.audio_files = {
      'coin': pygame.mixer.Sound(join('audio', 'coin.mp3')),
      'attack': pygame.mixer.Sound(join('audio', 'attack.wav')),
      'jump': pygame.mixer.Sound(join('audio', 'jump.mp3')),
      'damage': pygame.mixer.Sound(join('audio', 'damage.wav')),
      'health': pygame.mixer.Sound(join('audio', 'damage.mp3')),
      'pearl': pygame.mixer.Sound(join('audio', 'pearl.mp3')),
    }
    self.bg_music = pygame.mixer.Sound(join('audio', 'background.mp3'))
    self.bg_music.set_volume(0.3)
  def check_game_over(self):
    if self.data.health <= 0:
      pygame.quit()
      sys.exit
  
  def run(self):
    while True:
      dt = self.clock.tick() / 1000
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          sys.exit()
      
      self.check_game_over()
      self.current_stage.run(dt)
      self.ui.update(dt) 
      
      pygame.display.update() 
      


if __name__ == "__main__":
  game = Game()
  game.run()
