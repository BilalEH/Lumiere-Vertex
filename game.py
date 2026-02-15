import pygame
import random
import math
import json
import os
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Color Palettes
COLORS = {
    'neon': {
        'bg': (10, 10, 20),
        'primary': (0, 255, 255),
        'secondary': (255, 0, 255),
        'accent': (255, 255, 0),
        'grid': (30, 30, 50)
    },
    'cyberpunk': {
        'bg': (20, 0, 40),
        'primary': (255, 20, 147),
        'secondary': (0, 255, 128),
        'accent': (255, 140, 0),
        'grid': (40, 20, 60)
    },
    'retro': {
        'bg': (20, 20, 20),
        'primary': (57, 255, 20),
        'secondary': (255, 57, 20),
        'accent': (255, 255, 20),
        'grid': (40, 40, 40)
    },
    'ocean': {
        'bg': (0, 20, 40),
        'primary': (0, 200, 255),
        'secondary': (255, 200, 100),
        'accent': (100, 255, 200),
        'grid': (0, 40, 60)
    },
    'fire': {
        'bg': (40, 10, 0),
        'primary': (255, 100, 0),
        'secondary': (255, 255, 100),
        'accent': (255, 50, 0),
        'grid': (60, 30, 10)
    }
}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (147, 0, 211)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ping Pong Ultimate")
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 24)

class GameMode(Enum):
    CLASSIC = auto()
    ENDLESS = auto()
    TWO_PLAYER = auto()
    TIME_ATTACK = auto()
    CAMPAIGN = auto()

class GameState(Enum):
    MENU = auto()
    MODE_SELECT = auto()
    SKIN_SELECT = auto()
    SETTINGS = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    VICTORY = auto()
    SHOP = auto()

class BoosterType(Enum):
    SPEED_UP = auto()
    SLOW_DOWN = auto()
    ENLARGE = auto()
    SHRINK = auto()
    MULTI_BALL = auto()
    SCORE_BOOST = auto()
    MAGNET = auto()
    GHOST = auto()

class BallSkin(Enum):
    CLASSIC = ("Classic", WHITE, 0, True)
    NEON = ("Neon", CYAN, 100, False)
    FIRE = ("Fire", ORANGE, 150, False)
    GOLD = ("Gold", YELLOW, 300, False)
    DIAMOND = ("Diamond", (200, 230, 255), 500, False)
    PLASMA = ("Plasma", PURPLE, 400, False)
    RAINBOW = ("Rainbow", None, 750, False)
    BASKETBALL = ("Basketball", ORANGE, 200, False)
    EMOJI = ("Emoji", YELLOW, 250, False)
    PLANET = ("Planet", BLUE, 350, False)
    
    def __init__(self, display_name, color, cost, unlocked):
        self.display_name = display_name
        self.color = color
        self.cost = cost
        self.unlocked = unlocked

class PaddleSkin(Enum):
    CLASSIC = ("Classic", WHITE, 0, True)
    NEON = ("Neon", CYAN, 100, False)
    FIRE = ("Fire", ORANGE, 150, False)
    GOLD = ("Gold", YELLOW, 300, False)
    LASER = ("Laser", RED, 250, False)
    ICE = ("Ice", (200, 230, 255), 200, False)
    ROBOT = ("Robot", GRAY, 400, False)
    ENERGY = ("Energy", PURPLE, 350, False)
    
    def __init__(self, display_name, color, cost, unlocked):
        self.display_name = display_name
        self.color = color
        self.cost = cost
        self.unlocked = unlocked

class Environment(Enum):
    NEON = ("Neon Arena", "neon", True)
    CYBERPUNK = ("Cyber City", "cyberpunk", False)
    RETRO = ("Retro Arcade", "retro", False)
    OCEAN = ("Ocean Depths", "ocean", False)
    FIRE = ("Fire Pit", "fire", False)
    
    def __init__(self, display_name, theme_key, unlocked):
        self.display_name = display_name
        self.theme_key = theme_key
        self.unlocked = unlocked

@dataclass
class Settings:
    master_volume: float = 0.8
    sfx_volume: float = 1.0
    music_volume: float = 0.7
    fullscreen: bool = False
    show_fps: bool = False
    particles: bool = True
    screen_shake: bool = True
    current_theme: str = "neon"
    
    def save(self):
        try:
            with open('settings.json', 'w') as f:
                json.dump(asdict(self), f)
        except:
            pass
    
    @staticmethod
    def load():
        try:
            with open('settings.json', 'r') as f:
                data = json.load(f)
                return Settings(**data)
        except:
            return Settings()

class SoundManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sounds = {}
        self.music_playing = False
        self.load_sounds()
    
    def load_sounds(self):
        sound_definitions = {
            'paddle_hit': (600, 100),
            'wall_hit': (400, 80),
            'score': (800, 150),
            'booster': (1000, 200),
            'powerup': (1200, 250),
            'win': (1500, 500),
            'lose': (200, 300),
            'menu_select': (600, 50),
            'menu_confirm': (800, 80),
            'multi_ball': (900, 180)
        }
        
        for name, (freq, duration) in sound_definitions.items():
            self.sounds[name] = self.generate_beep(freq, duration)
    
    def generate_beep(self, frequency, duration_ms):
        sample_rate = 44100
        duration = duration_ms / 1000.0
        num_samples = int(sample_rate * duration)
        
        buf = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            value = int(127 * math.sin(2 * math.pi * frequency * t))
            value = int(value * self.settings.sfx_volume * self.settings.master_volume)
            buf.append(max(0, min(255, 128 + value)))
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(self.settings.sfx_volume * self.settings.master_volume)
        return sound
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def set_volumes(self):
        for sound in self.sounds.values():
            sound.set_volume(self.settings.sfx_volume * self.settings.master_volume)

class Particle:
    def __init__(self, x, y, color, velocity, size=5, lifetime=30, gravity=0.2):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        self.rotation += self.rotation_speed
    
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            color = self.color
            if isinstance(color, tuple) and len(color) == 3:
                color = (*color, alpha)
            pygame.draw.circle(surface, color[:3], (int(self.x), int(self.y)), size)

class GlowParticle:
    def __init__(self, x, y, color, radius=20, lifetime=20):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        self.lifetime -= 1
        self.radius *= 0.95
    
    def draw(self, surface):
        if self.radius > 0:
            alpha = int(128 * (self.lifetime / self.max_lifetime))
            glow_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(glow_surface, color_with_alpha, 
                             (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(glow_surface, (int(self.x - self.radius), int(self.y - self.radius)))

class Ball:
    def __init__(self, x, y, speed_multiplier=1.0, skin=BallSkin.CLASSIC):
        self.x = x
        self.y = y
        self.radius = 12
        self.skin = skin
        self.trail = []
        self.spin = 0
        self.glow_radius = 20
        self.reset(speed_multiplier)
    
    def reset(self, speed_multiplier=1.0):
        angle = random.choice([random.uniform(-45, 45), random.uniform(135, 225)])
        speed = 6 * speed_multiplier
        self.vx = speed * math.cos(math.radians(angle))
        self.vy = speed * math.sin(math.radians(angle))
        self.trail = []
        self.spin = 0
    
    def get_color(self, time: float = 0.0):
        if self.skin == BallSkin.RAINBOW:
            hue = (time * 2) % 360
            return self.hsv_to_rgb(hue / 360, 1.0, 1.0)
        return self.skin.color
    
    @staticmethod
    def hsv_to_rgb(h, s, v):
        if s == 0.0:
            return (int(v * 255), int(v * 255), int(v * 255))
        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        i = i % 6
        if i == 0: rgb = (v, t, p)
        elif i == 1: rgb = (q, v, p)
        elif i == 2: rgb = (p, v, t)
        elif i == 3: rgb = (p, q, v)
        elif i == 4: rgb = (t, p, v)
        else: rgb = (v, p, q)
        return tuple(int(c * 255) for c in rgb)
    
    def update(self):
        self.trail.append((self.x, self.y, pygame.time.get_ticks()))
        if len(self.trail) > 15:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
        self.spin += math.sqrt(self.vx**2 + self.vy**2) * 0.1
    
    def draw(self, surface, theme_colors):
        for i, (tx, ty, t_time) in enumerate(self.trail):
            progress = i / len(self.trail)
            alpha = int(100 * progress)
            size = int(self.radius * progress * 0.8)
            if size > 0:
                trail_color = self.get_color(t_time / 10)
                glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*trail_color[:3], alpha // 3), 
                                 (size * 2, size * 2), size * 2)
                surface.blit(glow_surface, (int(tx - size * 2), int(ty - size * 2)))
        
        glow_surface = pygame.Surface((self.glow_radius * 4, self.glow_radius * 4), pygame.SRCALPHA)
        glow_color = (*self.get_color(pygame.time.get_ticks() / 10)[:3], 50)
        pygame.draw.circle(glow_surface, glow_color, 
                          (self.glow_radius * 2, self.glow_radius * 2), self.glow_radius * 2)
        surface.blit(glow_surface, (int(self.x - self.glow_radius * 2), 
                                   int(self.y - self.glow_radius * 2)))
        
        color = self.get_color(pygame.time.get_ticks() / 10)
        
        if self.skin == BallSkin.BASKETBALL:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.arc(surface, BLACK, 
                           (self.x - self.radius, self.y - self.radius, 
                            self.radius * 2, self.radius * 2), 0.5, 2.5, 2)
            pygame.draw.arc(surface, BLACK, 
                           (self.x - self.radius, self.y - self.radius, 
                            self.radius * 2, self.radius * 2), 3.5, 5.5, 2)
            pygame.draw.line(surface, BLACK, 
                           (self.x - self.radius, self.y), 
                           (self.x + self.radius, self.y), 2)
        elif self.skin == BallSkin.EMOJI:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, BLACK, (int(self.x - 4), int(self.y - 3)), 2)
            pygame.draw.circle(surface, BLACK, (int(self.x + 4), int(self.y - 3)), 2)
            pygame.draw.arc(surface, BLACK, 
                           (self.x - 6, self.y - 4, 12, 10), 0.2, 2.9, 2)
        elif self.skin == BallSkin.PLANET:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
            ring_color = (200, 200, 255)
            pygame.draw.ellipse(surface, ring_color, 
                              (self.x - self.radius - 3, self.y - 5, 
                               self.radius * 2 + 6, 10), 2)
            pygame.draw.circle(surface, (100, 200, 255), 
                             (int(self.x - 3), int(self.y - 3)), 3)
        else:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
            highlight_color = (min(255, color[0] + 50), min(255, color[1] + 50), 
                             min(255, color[2] + 50))
            pygame.draw.circle(surface, highlight_color, 
                             (int(self.x - 3), int(self.y - 3)), self.radius // 3)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Paddle:
    def __init__(self, x, is_player=True, skin=PaddleSkin.CLASSIC):
        self.x = x
        self.y = SCREEN_HEIGHT // 2
        self.width = 18
        self.base_height = 110
        self.height = 110
        self.speed = 9
        self.is_player = is_player
        self.score = 0
        self.powerup_timer = 0
        self.skin = skin
        self.glow_intensity = 0
        self.combo = 0
        self.last_hit_time = 0
        self.energy = 0
        self.max_energy = 100
        self.magnet_active = False
        self.ghost_active = False
    
    def update(self, ball_y=None, keys=None):
        current_time = pygame.time.get_ticks()
        
        if self.is_player:
            if keys is None:
                keys = pygame.key.get_pressed()
            
            if self.is_player and self.x < SCREEN_WIDTH // 2:
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    self.y -= self.speed
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    self.y += self.speed
            elif self.is_player:
                if keys[pygame.K_UP]:
                    self.y -= self.speed
                if keys[pygame.K_DOWN]:
                    self.y += self.speed
        else:
            if ball_y is not None:
                target_y = ball_y
                diff = target_y - self.y
                
                ai_speed = self.speed * 0.85
                if diff > ai_speed:
                    self.y += ai_speed
                elif diff < -ai_speed:
                    self.y -= ai_speed
                else:
                    self.y = target_y
        
        self.y = max(self.height // 2, min(SCREEN_HEIGHT - self.height // 2, self.y))
        
        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            self.glow_intensity = min(255, self.glow_intensity + 10)
            if self.powerup_timer == 0:
                self.height = self.base_height
                self.glow_intensity = 0
                self.magnet_active = False
                self.ghost_active = False
        
        if current_time - self.last_hit_time > 2000:
            self.combo = 0
        
        if self.energy < self.max_energy:
            self.energy += 0.1
    
    def on_hit(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time < 1000:
            self.combo = min(5, self.combo + 1)
        else:
            self.combo = 1
        self.last_hit_time = current_time
        self.energy = min(self.max_energy, self.energy + 15)
    
    def draw(self, surface, theme_colors):
        rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                          self.width, self.height)
        
        if self.glow_intensity > 0 or self.energy > 50:
            glow_size = 20 + int(self.energy / 5)
            glow_surface = pygame.Surface((rect.width + glow_size * 2, 
                                          rect.height + glow_size * 2), pygame.SRCALPHA)
            alpha = min(100, self.glow_intensity)
            glow_color = theme_colors['primary']
            pygame.draw.rect(glow_surface, (*glow_color[:3], alpha), 
                           (glow_size, glow_size, rect.width, rect.height), 
                           border_radius=8)
            surface.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))
        
        color = self.skin.color if self.skin.color else theme_colors['primary']
        
        if self.skin == PaddleSkin.CLASSIC:
            pygame.draw.rect(surface, WHITE, rect, border_radius=5)
            pygame.draw.rect(surface, GRAY, rect, width=2, border_radius=5)
        elif self.skin == PaddleSkin.NEON:
            pygame.draw.rect(surface, CYAN, rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, rect.inflate(-4, -4), border_radius=3)
            pygame.draw.rect(surface, CYAN, rect, width=3, border_radius=5)
        elif self.skin == PaddleSkin.FIRE:
            for i in range(5):
                offset = i * 3
                alpha = 200 - i * 40
                fire_color = (255, max(0, 100 - i * 20), 0)
                fire_rect = rect.inflate(-offset, -offset)
                pygame.draw.rect(surface, fire_color, fire_rect, border_radius=5)
        elif self.skin == PaddleSkin.LASER:
            pygame.draw.rect(surface, RED, rect, border_radius=3)
            pygame.draw.rect(surface, WHITE, rect.inflate(-6, -6), border_radius=2)
            pygame.draw.line(surface, YELLOW, 
                           (rect.centerx, rect.top), (rect.centerx, rect.bottom), 2)
        elif self.skin == PaddleSkin.ICE:
            pygame.draw.rect(surface, (200, 230, 255), rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=8)
            for i in range(3):
                y = rect.top + 15 + i * 25
                pygame.draw.line(surface, (150, 200, 255), 
                               (rect.left + 3, y), (rect.right - 3, y), 2)
        elif self.skin == PaddleSkin.ROBOT:
            pygame.draw.rect(surface, (80, 80, 80), rect, border_radius=4)
            pygame.draw.rect(surface, (150, 150, 150), rect.inflate(-4, -4), border_radius=3)
            pygame.draw.circle(surface, RED, (rect.centerx, rect.centery), 5)
            pygame.draw.rect(surface, (100, 100, 100), 
                           (rect.left + 2, rect.top + 5, rect.width - 4, 8))
        elif self.skin == PaddleSkin.ENERGY:
            pygame.draw.rect(surface, PURPLE, rect, border_radius=5)
            inner_rect = rect.inflate(-4, -4)
            pygame.draw.rect(surface, (200, 100, 255), inner_rect, border_radius=4)
            for i in range(4):
                y = rect.top + 10 + i * 20
                pygame.draw.line(surface, (100, 0, 200), 
                               (rect.left, y), (rect.right, y), 2)
        else:
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=5)
        
        if self.combo > 1:
            combo_text = font_tiny.render(f"x{self.combo}", True, YELLOW)
            combo_rect = combo_text.get_rect(center=(rect.centerx, rect.top - 15))
            surface.blit(combo_text, combo_rect)
        
        if self.energy >= self.max_energy:
            pygame.draw.rect(surface, YELLOW, rect, width=3, border_radius=5)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)
    
    def apply_powerup(self, effect, duration):
        if effect == "enlarge":
            self.height = min(160, self.base_height + 40)
        elif effect == "shrink":
            self.height = max(70, self.base_height - 40)
        elif effect == "magnet":
            self.magnet_active = True
        elif effect == "ghost":
            self.ghost_active = True
        self.powerup_timer = duration

class Booster:
    def __init__(self, x, y, booster_type):
        self.x = x
        self.y = y
        self.type = booster_type
        self.radius = 22
        self.active = True
        self.pulse = 0
        self.pulse_direction = 1
        self.float_offset = 0
        
        self.colors = {
            BoosterType.SPEED_UP: (255, 50, 50),
            BoosterType.SLOW_DOWN: (50, 150, 255),
            BoosterType.ENLARGE: (50, 255, 100),
            BoosterType.SHRINK: (255, 150, 50),
            BoosterType.MULTI_BALL: (180, 50, 255),
            BoosterType.SCORE_BOOST: (255, 255, 50),
            BoosterType.MAGNET: (255, 100, 200),
            BoosterType.GHOST: (100, 255, 255)
        }
        
        self.symbols = {
            BoosterType.SPEED_UP: "⚡",
            BoosterType.SLOW_DOWN: "❄",
            BoosterType.ENLARGE: "↔",
            BoosterType.SHRINK: "→",
            BoosterType.MULTI_BALL: "○",
            BoosterType.SCORE_BOOST: "★",
            BoosterType.MAGNET: "🧲",
            BoosterType.GHOST: "👻"
        }
    
    def update(self):
        self.pulse += 0.15 * self.pulse_direction
        if self.pulse > 6 or self.pulse < 0:
            self.pulse_direction *= -1
        self.float_offset += 0.1
    
    def draw(self, surface):
        if not self.active:
            return
        
        color = self.colors[self.type]
        radius = self.radius + int(self.pulse)
        float_y = self.y + math.sin(self.float_offset) * 5
        
        for i in range(3):
            glow_radius = radius + i * 8
            alpha = 30 - i * 10
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color[:3], alpha), 
                             (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (int(self.x - glow_radius), int(float_y - glow_radius)))
        
        pygame.draw.circle(surface, color, (int(self.x), int(float_y)), radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(float_y)), radius - 3, 2)
        pygame.draw.circle(surface, (*color[:3], 100), (int(self.x), int(float_y)), radius - 6)
        
        text = font_small.render(self.symbols[self.type], True, WHITE)
        rect = text.get_rect(center=(self.x, float_y))
        surface.blit(text, rect)

class EnvironmentEffect:
    def __init__(self, theme_key):
        self.theme_key = theme_key
        self.particles = []
        self.time = 0
        self.generate_particles()
    
    def generate_particles(self):
        if self.theme_key == "neon":
            for _ in range(20):
                self.particles.append({
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(0, SCREEN_HEIGHT),
                    'size': random.randint(1, 3),
                    'speed': random.uniform(0.5, 2),
                    'color': random.choice([CYAN, PURPLE, YELLOW])
                })
        elif self.theme_key == "cyberpunk":
            for _ in range(30):
                self.particles.append({
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(0, SCREEN_HEIGHT),
                    'size': random.randint(2, 4),
                    'speed_y': random.uniform(1, 3),
                    'color': random.choice([(255, 20, 147), (0, 255, 128)])
                })
        elif self.theme_key == "ocean":
            for _ in range(25):
                self.particles.append({
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(0, SCREEN_HEIGHT),
                    'size': random.randint(3, 6),
                    'speed_x': random.uniform(-0.5, 0.5),
                    'speed_y': random.uniform(-0.3, 0.3),
                    'color': (100, 200, 255)
                })
        elif self.theme_key == "fire":
            for _ in range(40):
                self.particles.append({
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(SCREEN_HEIGHT - 100, SCREEN_HEIGHT),
                    'size': random.randint(2, 8),
                    'speed_y': random.uniform(-3, -1),
                    'color': random.choice([ORANGE, RED, YELLOW])
                })
    
    def update(self):
        self.time += 1
        colors = COLORS[self.theme_key]
        
        for p in self.particles:
            if self.theme_key == "neon":
                p['y'] -= p['speed']
                if p['y'] < 0:
                    p['y'] = SCREEN_HEIGHT
                    p['x'] = random.randint(0, SCREEN_WIDTH)
            elif self.theme_key == "cyberpunk":
                p['y'] -= p['speed_y']
                if p['y'] < 0:
                    p['y'] = SCREEN_HEIGHT
                    p['x'] = random.randint(0, SCREEN_WIDTH)
            elif self.theme_key == "ocean":
                p['x'] += p['speed_x'] + math.sin(self.time * 0.02) * 0.5
                p['y'] += p['speed_y']
                if p['x'] < 0 or p['x'] > SCREEN_WIDTH:
                    p['speed_x'] *= -1
                if p['y'] < 0 or p['y'] > SCREEN_HEIGHT:
                    p['speed_y'] *= -1
            elif self.theme_key == "fire":
                p['y'] += p['speed_y']
                p['x'] += math.sin(self.time * 0.1 + p['y'] * 0.01) * 0.5
                if p['y'] < 0:
                    p['y'] = SCREEN_HEIGHT
                    p['x'] = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, surface):
        for p in self.particles:
            alpha = int(100 + 50 * math.sin(self.time * 0.05 + p['x'] * 0.01))
            color = (*p['color'][:3], alpha)
            if self.theme_key == "fire":
                alpha = int(200 * (1 - (SCREEN_HEIGHT - p['y']) / 100))
                color = (*p['color'][:3], max(0, min(255, alpha)))
            
            glow_surface = pygame.Surface((p['size'] * 4, p['size'] * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, color, (p['size'] * 2, p['size'] * 2), p['size'] * 2)
            surface.blit(glow_surface, (int(p['x'] - p['size'] * 2), int(p['y'] - p['size'] * 2)))

class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.game_mode = GameMode.CLASSIC
        self.current_level = 1
        self.max_levels = 8
        self.settings = Settings.load()
        self.sound_manager = SoundManager(self.settings)
        
        self.player1 = Paddle(40, is_player=True)
        self.player2 = None
        self.ai = None
        self.balls = []
        self.boosters = []
        self.particles = []
        self.glow_particles = []
        self.environment_effect = None
        
        self.menu_selection = 0
        self.menu_options = ["Play", "Skins", "Settings", "Quit"]
        self.mode_options = ["Classic", "Endless", "2 Players", "Time Attack", "Campaign"]
        self.mode_selection = 0
        
        self.current_ball_skin = BallSkin.CLASSIC
        self.current_paddle_skin = PaddleSkin.CLASSIC
        self.current_environment = Environment.NEON
        
        self.coins = 0
        self.unlocked_skins = {'ball': [BallSkin.CLASSIC], 'paddle': [PaddleSkin.CLASSIC]}
        self.unlocked_environments = [Environment.NEON]
        
        self.shake_timer = 0
        self.shake_intensity = 0
        self.background_offset = 0
        
        self.load_progress()
        self.update_environment()
    
    def load_progress(self):
        try:
            with open('progress.json', 'r') as f:
                data = json.load(f)
                self.coins = data.get('coins', 0)
                self.unlocked_skins = {
                    'ball': [s for s in BallSkin if s.name in data.get('unlocked_ball_skins', ['CLASSIC'])],
                    'paddle': [s for s in PaddleSkin if s.name in data.get('unlocked_paddle_skins', ['CLASSIC'])]
                }
                for skin in self.unlocked_skins['ball']:
                    skin.unlocked = True
                for skin in self.unlocked_skins['paddle']:
                    skin.unlocked = True
        except:
            pass
    
    def save_progress(self):
        try:
            data = {
                'coins': self.coins,
                'unlocked_ball_skins': [s.name for s in self.unlocked_skins['ball']],
                'unlocked_paddle_skins': [s.name for s in self.unlocked_skins['paddle']]
            }
            with open('progress.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def update_environment(self):
        colors = COLORS[self.current_environment.theme_key]
        self.environment_effect = EnvironmentEffect(self.current_environment.theme_key)
    
    def start_game(self):
        self.player1 = Paddle(40, is_player=True, skin=self.current_paddle_skin)
        
        if self.game_mode == GameMode.TWO_PLAYER:
            self.player2 = Paddle(SCREEN_WIDTH - 40, is_player=True, skin=self.current_paddle_skin)
            self.ai = None
        else:
            self.player2 = None
            self.ai = Paddle(SCREEN_WIDTH - 40, is_player=False, skin=self.current_paddle_skin)
            
            if self.game_mode == GameMode.CLASSIC:
                self.ai.speed = 7
            elif self.game_mode == GameMode.ENDLESS:
                self.ai.speed = 7 + (self.player1.score // 5)
            elif self.game_mode == GameMode.TIME_ATTACK:
                self.ai.speed = 8
        
        self.balls = [Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 1.0, self.current_ball_skin)]
        self.boosters = []
        self.particles = []
        self.glow_particles = []
        self.state = GameState.PLAYING
        
        self.player1.score = 0
        if self.player2:
            self.player2.score = 0
        if self.ai:
            self.ai.score = 0
    
    def create_explosion(self, x, y, color, count=15):
        if not self.settings.particles:
            return
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(3, 8)
            vx = speed * math.cos(math.radians(angle))
            vy = speed * math.sin(math.radians(angle))
            size = random.randint(3, 8)
            self.particles.append(Particle(x, y, color, (vx, vy), size))
            
            if random.random() < 0.3:
                self.glow_particles.append(GlowParticle(x, y, color, random.randint(15, 30)))
    
    def screen_shake(self, intensity):
        if self.settings.screen_shake:
            self.shake_timer = 10
            self.shake_intensity = intensity
    
    def spawn_booster(self):
        if random.randint(1, 400) == 1:
            x = random.randint(250, SCREEN_WIDTH - 250)
            y = random.randint(150, SCREEN_HEIGHT - 150)
            booster_type = random.choice(list(BoosterType))
            self.boosters.append(Booster(x, y, booster_type))
    
    def apply_booster(self, booster, ball, paddle):
        self.sound_manager.play('booster')
        
        if booster.type == BoosterType.SPEED_UP:
            for b in self.balls:
                b.vx *= 1.4
                b.vy *= 1.4
            self.create_explosion(booster.x, booster.y, RED, 20)
        elif booster.type == BoosterType.SLOW_DOWN:
            for b in self.balls:
                b.vx *= 0.6
                b.vy *= 0.6
            self.create_explosion(booster.x, booster.y, BLUE, 20)
        elif booster.type == BoosterType.ENLARGE:
            paddle.apply_powerup("enlarge", 400)
            self.create_explosion(booster.x, booster.y, GREEN, 20)
        elif booster.type == BoosterType.SHRINK:
            if self.ai:
                self.ai.apply_powerup("shrink", 400)
            elif self.player2 and paddle == self.player1:
                self.player2.apply_powerup("shrink", 400)
            elif self.player2:
                self.player1.apply_powerup("shrink", 400)
            self.create_explosion(booster.x, booster.y, ORANGE, 20)
        elif booster.type == BoosterType.MULTI_BALL:
            new_balls = []
            for b in self.balls[:2]:
                new_ball = Ball(b.x, b.y, 1.0, self.current_ball_skin)
                new_ball.vx = -b.vx * random.uniform(0.8, 1.2)
                new_ball.vy = b.vy + random.uniform(-3, 3)
                new_balls.append(new_ball)
            self.balls.extend(new_balls)
            self.sound_manager.play('multi_ball')
            self.create_explosion(booster.x, booster.y, PURPLE, 25)
        elif booster.type == BoosterType.SCORE_BOOST:
            paddle.score += 1
            self.create_explosion(booster.x, booster.y, YELLOW, 25)
            self.coins += 5
        elif booster.type == BoosterType.MAGNET:
            paddle.apply_powerup("magnet", 300)
            self.create_explosion(booster.x, booster.y, (255, 100, 200), 20)
        elif booster.type == BoosterType.GHOST:
            paddle.apply_powerup("ghost", 250)
            self.create_explosion(booster.x, booster.y, (100, 255, 255), 20)
    
    def update(self):
        if self.state == GameState.PLAYING:
            self.background_offset += 0.3
            if self.background_offset > 50:
                self.background_offset = 0
            
            if self.shake_timer > 0:
                self.shake_timer -= 1
                self.shake_intensity *= 0.9
            
            if self.environment_effect:
                self.environment_effect.update()
            
            self.spawn_booster()
            
            for booster in self.boosters:
                booster.update()
            self.boosters = [b for b in self.boosters if b.active]
            
            for particle in self.particles:
                particle.update()
            self.particles = [p for p in self.particles if p.lifetime > 0]
            
            for glow in self.glow_particles:
                glow.update()
            self.glow_particles = [g for g in self.glow_particles if g.lifetime > 0]
            
            keys = pygame.key.get_pressed()
            self.player1.update(keys=keys)
            
            if self.player2:
                self.player2.update(keys=keys)
            elif self.ai:
                ball_y = self.balls[0].y if self.balls else SCREEN_HEIGHT // 2
                self.ai.update(ball_y=ball_y)
            
            for ball in self.balls:
                ball.update()
                
                if ball.y - ball.radius <= 0 or ball.y + ball.radius >= SCREEN_HEIGHT:
                    ball.vy *= -1
                    ball.y = max(ball.radius, min(SCREEN_HEIGHT - ball.radius, ball.y))
                    self.create_explosion(ball.x, ball.y, WHITE, 8)
                    self.sound_manager.play('wall_hit')
                
                ball_rect = ball.get_rect()
                
                player1_rect = self.player1.get_rect()
                if ball_rect.colliderect(player1_rect) and ball.vx < 0:
                    relative_y = (self.player1.y - ball.y) / (self.player1.height / 2)
                    angle = relative_y * 70
                    speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2) * 1.05
                    ball.vx = abs(speed * math.cos(math.radians(angle)))
                    ball.vy = -speed * math.sin(math.radians(angle))
                    self.player1.on_hit()
                    self.create_explosion(ball.x, ball.y, GREEN, 12)
                    self.sound_manager.play('paddle_hit')
                    self.screen_shake(5)
                    self.coins += self.player1.combo
                
                if self.player2:
                    player2_rect = self.player2.get_rect()
                    if ball_rect.colliderect(player2_rect) and ball.vx > 0:
                        relative_y = (self.player2.y - ball.y) / (self.player2.height / 2)
                        angle = relative_y * 70
                        speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2) * 1.05
                        ball.vx = -abs(speed * math.cos(math.radians(angle)))
                        ball.vy = -speed * math.sin(math.radians(angle))
                        self.player2.on_hit()
                        self.create_explosion(ball.x, ball.y, BLUE, 12)
                        self.sound_manager.play('paddle_hit')
                        self.screen_shake(5)
                elif self.ai:
                    ai_rect = self.ai.get_rect()
                    if ball_rect.colliderect(ai_rect) and ball.vx > 0:
                        relative_y = (self.ai.y - ball.y) / (self.ai.height / 2)
                        angle = relative_y * 70
                        speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2) * 1.05
                        ball.vx = -abs(speed * math.cos(math.radians(angle)))
                        ball.vy = -speed * math.sin(math.radians(angle))
                        self.create_explosion(ball.x, ball.y, RED, 12)
                        self.sound_manager.play('paddle_hit')
                
                for booster in self.boosters:
                    if booster.active:
                        float_y = booster.y + math.sin(pygame.time.get_ticks() * 0.001) * 5
                        dist = math.sqrt((ball.x - booster.x) ** 2 + (ball.y - float_y) ** 2)
                        if dist < ball.radius + booster.radius:
                            paddle = self.player1 if ball.vx > 0 else (self.ai if self.ai else self.player1)
                            self.apply_booster(booster, ball, paddle)
                            booster.active = False
                
                if ball.x < 0:
                    if self.player2:
                        self.player2.score += 1
                    elif self.ai:
                        self.ai.score += 1
                    self.check_game_over()
                    ball.reset()
                    self.sound_manager.play('score')
                elif ball.x > SCREEN_WIDTH:
                    self.player1.score += 1
                    self.check_game_over()
                    ball.reset()
                    self.sound_manager.play('score')
                    self.coins += 2 + self.player1.combo
            
            self.balls = [b for b in self.balls if 0 < b.x < SCREEN_WIDTH]
            if not self.balls:
                self.balls.append(Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 1.0, self.current_ball_skin))
    
    def check_game_over(self):
        if self.game_mode == GameMode.TWO_PLAYER:
            if self.player2 and (self.player1.score >= 10 or self.player2.score >= 10):
                self.state = GameState.GAME_OVER
                self.sound_manager.play('win' if self.player1.score >= 10 else 'lose')
        elif self.game_mode == GameMode.CLASSIC:
            if self.player1.score >= 10 or (self.ai and self.ai.score >= 10):
                self.state = GameState.GAME_OVER
                if self.player1.score >= 10:
                    self.sound_manager.play('win')
                    self.coins += 50
                else:
                    self.sound_manager.play('lose')
        elif self.game_mode == GameMode.ENDLESS:
            pass
        
        self.save_progress()
    
    def get_colors(self):
        return COLORS[self.current_environment.theme_key]
    
    def draw_background(self):
        colors = self.get_colors()
        screen.fill(colors['bg'])
        
        if self.environment_effect:
            self.environment_effect.draw(screen)
        
        for i in range(0, SCREEN_WIDTH, 50):
            offset = (i + int(self.background_offset)) % 50 - 25
            alpha = int(20 + 15 * math.sin(i * 0.03))
            color = (*colors['grid'][:3],)
            pygame.draw.line(screen, color, (i, 0), (i, SCREEN_HEIGHT), 1)
        
        for i in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, colors['grid'], (0, i), (SCREEN_WIDTH, i), 1)
        
        pygame.draw.line(screen, colors['primary'], (SCREEN_WIDTH // 2, 0), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 3)
        
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.rect(screen, colors['primary'], (SCREEN_WIDTH // 2 - 6, y, 12, 25))
        
        pygame.draw.rect(screen, colors['primary'], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 6)
    
    def draw(self):
        if self.shake_timer > 0:
            offset_x = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            offset_y = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
        else:
            offset_x, offset_y = 0, 0
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.MODE_SELECT:
            self.draw_mode_select()
        elif self.state == GameState.SKIN_SELECT:
            self.draw_skin_select()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.PLAYING:
            self.draw_game(offset_x, offset_y)
        elif self.state == GameState.PAUSED:
            self.draw_game(0, 0)
            self.draw_pause()
        elif self.state == GameState.GAME_OVER:
            self.draw_game(0, 0)
            self.draw_game_over()
        
        for glow in self.glow_particles:
            glow.draw(screen)
        
        for particle in self.particles:
            particle.draw(screen)
        
        if self.settings.show_fps:
            fps_text = font_tiny.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
            screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
        
        pygame.display.flip()
    
    def draw_menu(self):
        self.draw_background()
        colors = self.get_colors()
        
        title = font_large.render("PING PONG", True, colors['primary'])
        subtitle = font_medium.render("ULTIMATE", True, colors['secondary'])
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 190))
        
        glow_title = font_large.render("PING PONG", True, (*colors['primary'][:3], 100))
        for offset in range(3):
            screen.blit(glow_title, (title_rect.x + offset, title_rect.y + offset))
        
        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        
        coin_text = font_small.render(f"💰 {self.coins}", True, YELLOW)
        screen.blit(coin_text, (20, 20))
        
        for i, option in enumerate(self.menu_options):
            is_selected = i == self.menu_selection
            color = colors['accent'] if is_selected else WHITE
            text = font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 80))
            
            if is_selected:
                pygame.draw.rect(screen, colors['accent'], rect.inflate(50, 20), 
                               width=3, border_radius=12)
                arrow = font_medium.render(">", True, colors['accent'])
                screen.blit(arrow, (rect.left - 40, rect.centery - arrow.get_height() // 2))
            
            screen.blit(text, rect)
        
        info = font_tiny.render("WASD/Arrows: Navigate  |  ENTER: Select  |  ESC: Back", True, GRAY)
        screen.blit(info, (20, SCREEN_HEIGHT - 40))
    
    def draw_mode_select(self):
        self.draw_background()
        colors = self.get_colors()
        
        title = font_large.render("SELECT MODE", True, colors['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        descriptions = {
            "Classic": "First to 10 points wins!",
            "Endless": "Survive as long as possible",
            "2 Players": "Play against a friend",
            "Time Attack": "Most points in 2 minutes",
            "Campaign": "Progress through levels"
        }
        
        for i, option in enumerate(self.mode_options):
            is_selected = i == self.mode_selection
            color = colors['accent'] if is_selected else WHITE
            text = font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 70))
            
            if is_selected:
                pygame.draw.rect(screen, colors['accent'], rect.inflate(40, 15), 
                               width=3, border_radius=10)
                desc = font_small.render(descriptions[option], True, colors['secondary'])
                desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, 620))
                screen.blit(desc, desc_rect)
            
            screen.blit(text, rect)
    
    def draw_skin_select(self):
        self.draw_background()
        colors = self.get_colors()
        
        title = font_large.render("SKINS", True, colors['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        ball_text = font_medium.render("Ball Skins", True, colors['secondary'])
        screen.blit(ball_text, (100, 150))
        
        for i, skin in enumerate(BallSkin):
            x = 100 + (i % 5) * 220
            y = 200 + (i // 5) * 100
            
            color = skin.color if skin.color else WHITE
            if not skin.unlocked:
                color = DARK_GRAY
            
            if skin == self.current_ball_skin:
                pygame.draw.rect(screen, colors['accent'], (x - 10, y - 10, 200, 80), 
                               width=3, border_radius=10)
            
            pygame.draw.rect(screen, color if skin.unlocked else DARK_GRAY, 
                           (x, y, 180, 60), border_radius=8)
            name_text = font_small.render(skin.display_name, True, WHITE)
            screen.blit(name_text, (x + 10, y + 10))
            
            if not skin.unlocked:
                cost_text = font_tiny.render(f"{skin.cost}💰", True, YELLOW)
                screen.blit(cost_text, (x + 10, y + 35))
        
        paddle_text = font_medium.render("Paddle Skins", True, colors['secondary'])
        screen.blit(paddle_text, (100, 400))
        
        for i, skin in enumerate(PaddleSkin):
            x = 100 + (i % 4) * 280
            y = 450 + (i // 4) * 80
            
            color = skin.color if skin.color else WHITE
            if not skin.unlocked:
                color = DARK_GRAY
            
            if skin == self.current_paddle_skin:
                pygame.draw.rect(screen, colors['accent'], (x - 10, y - 10, 260, 60), 
                               width=3, border_radius=10)
            
            pygame.draw.rect(screen, color if skin.unlocked else DARK_GRAY, 
                           (x, y, 240, 40), border_radius=5)
            name_text = font_small.render(skin.display_name, True, WHITE)
            screen.blit(name_text, (x + 10, y + 10))
            
            if not skin.unlocked:
                cost_text = font_tiny.render(f"{skin.cost}💰", True, YELLOW)
                screen.blit(cost_text, (x + 140, y + 12))
        
        coin_text = font_small.render(f"Your Coins: {self.coins}💰", True, YELLOW)
        screen.blit(coin_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80))
        
        info = font_tiny.render("Click to select/buy skins", True, GRAY)
        screen.blit(info, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 40))
    
    def draw_settings(self):
        self.draw_background()
        colors = self.get_colors()
        
        title = font_large.render("SETTINGS", True, colors['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        settings_items = [
            ("Master Volume", f"{int(self.settings.master_volume * 100)}%"),
            ("SFX Volume", f"{int(self.settings.sfx_volume * 100)}%"),
            ("Music Volume", f"{int(self.settings.music_volume * 100)}%"),
            ("Particles", "ON" if self.settings.particles else "OFF"),
            ("Screen Shake", "ON" if self.settings.screen_shake else "OFF"),
            ("Show FPS", "ON" if self.settings.show_fps else "OFF"),
        ]
        
        for i, (name, value) in enumerate(settings_items):
            y = 180 + i * 70
            name_text = font_medium.render(name, True, WHITE)
            screen.blit(name_text, (200, y))
            
            value_text = font_medium.render(value, True, colors['accent'])
            value_rect = value_text.get_rect(right=SCREEN_WIDTH - 200, y=y)
            screen.blit(value_text, value_rect)
            
            pygame.draw.rect(screen, colors['primary'], (value_rect.x - 20, y - 5, 
                           value_rect.width + 40, value_rect.height + 10), 
                          width=2, border_radius=5)
        
        theme_text = font_medium.render(f"Theme: {self.current_environment.display_name}", True, WHITE)
        screen.blit(theme_text, (200, 600))
        
        info = font_tiny.render("Click setting to change  |  Left/Right arrows adjust values", True, GRAY)
        screen.blit(info, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 40))
    
    def draw_game(self, offset_x=0, offset_y=0):
        self.draw_background()
        colors = self.get_colors()
        
        for booster in self.boosters:
            booster.draw(screen)
        
        for ball in self.balls:
            ball.draw(screen, colors)
        
        self.player1.draw(screen, colors)
        
        if self.player2:
            self.player2.draw(screen, colors)
        elif self.ai:
            self.ai.draw(screen, colors)
        
        score1 = font_large.render(str(self.player1.score), True, colors['primary'])
        screen.blit(score1, (SCREEN_WIDTH // 4 + offset_x, 40 + offset_y))
        
        if self.player2:
            score2 = font_large.render(str(self.player2.score), True, colors['secondary'])
        elif self.ai:
            score2 = font_large.render(str(self.ai.score), True, colors['secondary'])
        else:
            score2 = None
        
        if score2:
            screen.blit(score2, (3 * SCREEN_WIDTH // 4 + offset_x, 40 + offset_y))
        
        coin_text = font_small.render(f"💰 {self.coins}", True, YELLOW)
        screen.blit(coin_text, (20 + offset_x, 20 + offset_y))
        
        if len(self.balls) > 1:
            multi_text = font_small.render(f"Multi-Ball x{len(self.balls)}", True, PURPLE)
            screen.blit(multi_text, (SCREEN_WIDTH - 200 + offset_x, 80 + offset_y))
        
        if self.game_mode == GameMode.TWO_PLAYER:
            p1_combo = font_tiny.render(f"P1 Combo: x{self.player1.combo}", True, YELLOW)
            screen.blit(p1_combo, (50 + offset_x, SCREEN_HEIGHT - 50 + offset_y))
            if self.player2:
                p2_combo = font_tiny.render(f"P2 Combo: x{self.player2.combo}", True, YELLOW)
                screen.blit(p2_combo, (SCREEN_WIDTH - 200 + offset_x, SCREEN_HEIGHT - 50 + offset_y))
    
    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        text = font_large.render("PAUSED", True, YELLOW)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, rect)
        
        continue_text = font_small.render("Press SPACE to continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(continue_text, continue_rect)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        if self.game_mode == GameMode.TWO_PLAYER:
            if self.player1.score >= 10:
                winner_text = "PLAYER 1 WINS!"
                winner_color = GREEN
            else:
                winner_text = "PLAYER 2 WINS!"
                winner_color = BLUE
        else:
            if self.player1.score >= 10:
                winner_text = "VICTORY!"
                winner_color = GREEN
            else:
                winner_text = "DEFEAT!"
                winner_color = RED
        
        text = font_large.render(winner_text, True, winner_color)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(text, rect)
        
        score_text = font_medium.render(f"{self.player1.score} - {self.player2.score if self.player2 else (self.ai.score if self.ai else 0)}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        coins_earned = (self.player1.score * 5) if self.player1.score >= 10 else (self.player1.score * 2)
        coin_text = font_small.render(f"+{coins_earned}💰", True, YELLOW)
        coin_rect = coin_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(coin_text, coin_rect)
        
        retry_text = font_small.render("Press ENTER to play again", True, WHITE)
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        screen.blit(retry_text, retry_rect)
        
        menu_text = font_small.render("Press ESC for menu", True, GRAY)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 190))
        screen.blit(menu_text, menu_rect)
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in [GameState.PLAYING, GameState.MODE_SELECT, 
                                     GameState.SKIN_SELECT, GameState.SETTINGS]:
                        self.state = GameState.MENU
                    elif self.state == GameState.MENU:
                        return False
                
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                        self.sound_manager.play('menu_select')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                        self.sound_manager.play('menu_select')
                    elif event.key == pygame.K_RETURN:
                        self.sound_manager.play('menu_confirm')
                        if self.menu_selection == 0:
                            self.state = GameState.MODE_SELECT
                        elif self.menu_selection == 1:
                            self.state = GameState.SKIN_SELECT
                        elif self.menu_selection == 2:
                            self.state = GameState.SETTINGS
                        elif self.menu_selection == 3:
                            return False
                
                elif self.state == GameState.MODE_SELECT:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.mode_selection = (self.mode_selection - 1) % len(self.mode_options)
                        self.sound_manager.play('menu_select')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.mode_selection = (self.mode_selection + 1) % len(self.mode_options)
                        self.sound_manager.play('menu_select')
                    elif event.key == pygame.K_RETURN:
                        self.sound_manager.play('menu_confirm')
                        mode_map = {
                            0: GameMode.CLASSIC,
                            1: GameMode.ENDLESS,
                            2: GameMode.TWO_PLAYER,
                            3: GameMode.TIME_ATTACK,
                            4: GameMode.CAMPAIGN
                        }
                        self.game_mode = mode_map[self.mode_selection]
                        self.start_game()
                
                elif self.state == GameState.SKIN_SELECT:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        pass
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        pass
                
                elif self.state == GameState.SETTINGS:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        pass
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        pass
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.SKIN_SELECT:
                    self.handle_skin_click(event.pos)
                elif self.state == GameState.SETTINGS:
                    self.handle_settings_click(event.pos)
        
        return True
    
    def handle_skin_click(self, pos):
        x, y = pos
        
        for i, skin in enumerate(BallSkin):
            bx = 100 + (i % 5) * 220
            by = 200 + (i // 5) * 100
            if bx <= x <= bx + 180 and by <= y <= by + 60:
                if skin.unlocked:
                    self.current_ball_skin = skin
                    self.sound_manager.play('menu_confirm')
                elif self.coins >= skin.cost:
                    self.coins -= skin.cost
                    skin.unlocked = True
                    self.unlocked_skins['ball'].append(skin)
                    self.current_ball_skin = skin
                    self.sound_manager.play('powerup')
                    self.save_progress()
                return
        
        for i, skin in enumerate(PaddleSkin):
            px = 100 + (i % 4) * 280
            py = 450 + (i // 4) * 80
            if px <= x <= px + 240 and py <= y <= py + 40:
                if skin.unlocked:
                    self.current_paddle_skin = skin
                    self.sound_manager.play('menu_confirm')
                elif self.coins >= skin.cost:
                    self.coins -= skin.cost
                    skin.unlocked = True
                    self.unlocked_skins['paddle'].append(skin)
                    self.current_paddle_skin = skin
                    self.sound_manager.play('powerup')
                    self.save_progress()
                return
    
    def handle_settings_click(self, pos):
        x, y = pos
        settings_y_positions = [180, 250, 320, 390, 460, 530]
        
        for i, sy in enumerate(settings_y_positions):
            if sy <= y <= sy + 50:
                if i == 0:
                    self.settings.master_volume = (self.settings.master_volume + 0.1) % 1.1
                elif i == 1:
                    self.settings.sfx_volume = (self.settings.sfx_volume + 0.1) % 1.1
                elif i == 2:
                    self.settings.music_volume = (self.settings.music_volume + 0.1) % 1.1
                elif i == 3:
                    self.settings.particles = not self.settings.particles
                elif i == 4:
                    self.settings.screen_shake = not self.settings.screen_shake
                elif i == 5:
                    self.settings.show_fps = not self.settings.show_fps
                
                self.sound_manager.set_volumes()
                self.settings.save()
                self.sound_manager.play('menu_confirm')
                return
        
        if 600 <= y <= 640:
            envs = list(Environment)
            current_idx = envs.index(self.current_environment)
            self.current_environment = envs[(current_idx + 1) % len(envs)]
            self.settings.current_theme = self.current_environment.theme_key
            self.update_environment()
            self.settings.save()
            self.sound_manager.play('menu_confirm')
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)
        
        self.save_progress()
        self.settings.save()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
