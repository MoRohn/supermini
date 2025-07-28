"""
Autonomous AI Avatar Generation System for SuperMini

This module provides multi-tier avatar generation with real-time emotional expression:
- Fast PIL-based procedural robot avatars for real-time use
- Optional AI-generated avatars for enhanced quality
- Emotion-aware generation with consistent styling
- Performance optimization with intelligent caching
"""

import time
import hashlib
import logging
from pathlib import Path
from functools import lru_cache
from typing import Dict, Optional, Tuple, Any
import io
import math
import random

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available - avatar generation disabled")

try:
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtCore import QThread, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logging.warning("PyQt6 not available")


class EmotionProfile:
    """Defines visual characteristics for each emotion"""
    
    def __init__(self, 
                 eye_color: Tuple[int, int, int] = (128, 128, 128),
                 eye_shape: str = 'circle',
                 eye_size_modifier: float = 1.0,
                 mouth_curve: int = 0,
                 mouth_color: Tuple[int, int, int] = (50, 50, 50),
                 glow_color: Optional[Tuple[int, int, int]] = None,
                 glow_intensity: float = 0.0,
                 head_tilt: int = 0,
                 antenna_style: str = 'normal',
                 special_effects: Dict[str, Any] = None):
        
        self.eye_color = eye_color
        self.eye_shape = eye_shape  # 'circle', 'square', 'diamond'
        self.eye_size_modifier = eye_size_modifier
        self.mouth_curve = mouth_curve  # positive = smile, negative = frown
        self.mouth_color = mouth_color
        self.glow_color = glow_color or eye_color
        self.glow_intensity = glow_intensity
        self.head_tilt = head_tilt
        self.antenna_style = antenna_style  # 'normal', 'excited', 'droopy'
        self.special_effects = special_effects or {}


class RobotAvatarGenerator:
    """Fast procedural robot avatar generator using PIL"""
    
    def __init__(self):
        self.emotions = self._define_emotions()
        self.cache = {}
        self.cache_dir = Path.home() / "SuperMini_Output" / "avatar_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _define_emotions(self) -> Dict[str, EmotionProfile]:
        """Define visual profiles for each emotion"""
        return {
            'idle': EmotionProfile(
                eye_color=(100, 150, 255),  # Calm blue
                eye_shape='circle',
                mouth_curve=2,
                glow_color=(100, 150, 255),
                glow_intensity=0.3
            ),
            'thinking': EmotionProfile(
                eye_color=(255, 200, 50),  # Warm yellow
                eye_shape='square',
                eye_size_modifier=1.2,
                mouth_curve=1,
                glow_color=(255, 200, 50),
                glow_intensity=0.6,
                antenna_style='excited',
                special_effects={'scanning_lines': True}
            ),
            'happy': EmotionProfile(
                eye_color=(50, 255, 100),  # Bright green
                eye_shape='circle',
                eye_size_modifier=1.3,
                mouth_curve=25,
                glow_color=(50, 255, 100),
                glow_intensity=0.8,
                special_effects={'sparkles': True}
            ),
            'working': EmotionProfile(
                eye_color=(255, 100, 50),  # Focused orange
                eye_shape='diamond',
                eye_size_modifier=0.9,
                mouth_curve=-2,
                glow_color=(255, 100, 50),
                glow_intensity=0.9,
                antenna_style='focused',
                special_effects={'progress_bars': True}
            ),
            'error': EmotionProfile(
                eye_color=(255, 50, 50),  # Alert red
                eye_shape='square',
                eye_size_modifier=1.1,
                mouth_curve=-15,
                glow_color=(255, 50, 50),
                glow_intensity=1.0,
                head_tilt=-5,
                special_effects={'warning_flash': True}
            ),
            'sleeping': EmotionProfile(
                eye_color=(150, 150, 200),  # Sleepy purple
                eye_shape='circle',
                eye_size_modifier=0.6,
                mouth_curve=5,
                glow_color=(150, 150, 200),
                glow_intensity=0.2,
                antenna_style='droopy',
                special_effects={'zzz_particles': True}
            ),
            'excited': EmotionProfile(
                eye_color=(255, 150, 255),  # Energetic magenta
                eye_shape='circle',
                eye_size_modifier=1.4,
                mouth_curve=20,
                glow_color=(255, 150, 255),
                glow_intensity=0.9,
                head_tilt=3,
                antenna_style='excited',
                special_effects={'energy_burst': True}
            ),
            'confused': EmotionProfile(
                eye_color=(200, 200, 100),  # Uncertain yellow
                eye_shape='diamond',
                eye_size_modifier=1.1,
                mouth_curve=-5,
                glow_color=(200, 200, 100),
                glow_intensity=0.4,
                head_tilt=-2,
                antenna_style='confused',
                special_effects={'question_marks': True}
            )
        }
    
    @lru_cache(maxsize=100)
    def generate_avatar(self, 
                       emotion: str = 'idle', 
                       size: int = 400, 
                       style: str = 'modern',
                       seed: Optional[int] = None) -> Image.Image:
        """
        Generate a robot avatar with specified emotion
        
        Args:
            emotion: Emotion to display ('idle', 'thinking', 'happy', etc.)
            size: Output image size in pixels
            style: Avatar style ('modern', 'retro', 'minimal')
            seed: Random seed for consistent generation
            
        Returns:
            PIL Image of the generated avatar
        """
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL/Pillow is required for avatar generation")
            
        if seed is not None:
            random.seed(seed)
            
        # Get emotion profile
        profile = self.emotions.get(emotion, self.emotions['idle'])
        
        # Create base image with transparency
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Generate avatar based on style
        if style == 'modern':
            avatar = self._generate_modern_robot(img, draw, profile, size)
        elif style == 'retro':
            avatar = self._generate_retro_robot(img, draw, profile, size)
        else:  # minimal
            avatar = self._generate_minimal_robot(img, draw, profile, size)
            
        # Apply special effects
        if profile.special_effects:
            avatar = self._apply_special_effects(avatar, profile, size)
            
        return avatar
    
    def _generate_modern_robot(self, img: Image.Image, draw: ImageDraw.Draw, 
                              profile: EmotionProfile, size: int) -> Image.Image:
        """Generate a modern-style robot avatar"""
        center_x, center_y = size // 2, size // 2
        head_size = int(size * 0.6)
        
        # Head with gradient effect
        head_rect = [
            center_x - head_size // 2, center_y - head_size // 2,
            center_x + head_size // 2, center_y + head_size // 2
        ]
        
        # Create head with rounded corners
        self._draw_rounded_rectangle(draw, head_rect, radius=20, 
                                   fill=(220, 220, 230, 255), 
                                   outline=(150, 150, 160, 255), width=3)
        
        # Add glow effect if specified
        if profile.glow_intensity > 0:
            glow_img = self._create_glow_effect(size, head_rect, profile.glow_color, 
                                              profile.glow_intensity)
            img = Image.alpha_composite(glow_img, img)
            draw = ImageDraw.Draw(img)
        
        # Eyes
        self._draw_eyes(draw, center_x, center_y - 20, head_size, profile)
        
        # Mouth
        self._draw_mouth(draw, center_x, center_y + 30, head_size, profile)
        
        # Antennas
        self._draw_antennas(draw, center_x, center_y - head_size // 2, profile)
        
        # Panel details
        self._draw_panel_details(draw, head_rect, profile)
        
        return img
    
    def _generate_retro_robot(self, img: Image.Image, draw: ImageDraw.Draw,
                             profile: EmotionProfile, size: int) -> Image.Image:
        """Generate a retro-style robot avatar"""
        center_x, center_y = size // 2, size // 2
        head_size = int(size * 0.65)
        
        # Boxy head
        head_rect = [
            center_x - head_size // 2, center_y - head_size // 2,
            center_x + head_size // 2, center_y + head_size // 2
        ]
        
        draw.rectangle(head_rect, fill=(200, 200, 210, 255), 
                      outline=(100, 100, 120, 255), width=4)
        
        # Retro-style eyes (square LEDs)
        eye_size = head_size // 8
        left_eye = [center_x - head_size // 4 - eye_size // 2, 
                   center_y - 15 - eye_size // 2,
                   center_x - head_size // 4 + eye_size // 2, 
                   center_y - 15 + eye_size // 2]
        right_eye = [center_x + head_size // 4 - eye_size // 2, 
                    center_y - 15 - eye_size // 2,
                    center_x + head_size // 4 + eye_size // 2, 
                    center_y - 15 + eye_size // 2]
        
        draw.rectangle(left_eye, fill=profile.eye_color)
        draw.rectangle(right_eye, fill=profile.eye_color)
        
        # Simple mouth
        mouth_width = head_size // 3
        mouth_rect = [center_x - mouth_width // 2, center_y + 20,
                     center_x + mouth_width // 2, center_y + 35]
        draw.rectangle(mouth_rect, fill=profile.mouth_color)
        
        return img
    
    def _generate_minimal_robot(self, img: Image.Image, draw: ImageDraw.Draw,
                               profile: EmotionProfile, size: int) -> Image.Image:
        """Generate a minimal-style robot avatar"""
        center_x, center_y = size // 2, size // 2
        head_size = int(size * 0.5)
        
        # Simple circle head
        head_rect = [
            center_x - head_size // 2, center_y - head_size // 2,
            center_x + head_size // 2, center_y + head_size // 2
        ]
        
        draw.ellipse(head_rect, fill=(240, 240, 245, 255), 
                    outline=(180, 180, 190, 255), width=2)
        
        # Minimal eyes (dots)
        eye_radius = 8
        draw.ellipse([center_x - 30 - eye_radius, center_y - 10 - eye_radius,
                     center_x - 30 + eye_radius, center_y - 10 + eye_radius], 
                    fill=profile.eye_color)
        draw.ellipse([center_x + 30 - eye_radius, center_y - 10 - eye_radius,
                     center_x + 30 + eye_radius, center_y - 10 + eye_radius], 
                    fill=profile.eye_color)
        
        # Minimal mouth (line)
        mouth_y = center_y + 25
        if profile.mouth_curve > 0:  # Smile
            draw.arc([center_x - 25, mouth_y - 10, center_x + 25, mouth_y + 10],
                    0, 180, fill=profile.mouth_color, width=3)
        elif profile.mouth_curve < 0:  # Frown
            draw.arc([center_x - 25, mouth_y - 10, center_x + 25, mouth_y + 10],
                    180, 360, fill=profile.mouth_color, width=3)
        else:  # Neutral
            draw.line([center_x - 20, mouth_y, center_x + 20, mouth_y],
                     fill=profile.mouth_color, width=3)
        
        return img
    
    def _draw_eyes(self, draw: ImageDraw.Draw, center_x: int, center_y: int,
                   head_size: int, profile: EmotionProfile):
        """Draw eyes based on emotion profile"""
        eye_size = int(head_size // 6 * profile.eye_size_modifier)
        eye_spacing = head_size // 3
        
        left_center = (center_x - eye_spacing // 2, center_y)
        right_center = (center_x + eye_spacing // 2, center_y)
        
        for eye_center in [left_center, right_center]:
            if profile.eye_shape == 'circle':
                eye_rect = [
                    eye_center[0] - eye_size // 2, eye_center[1] - eye_size // 2,
                    eye_center[0] + eye_size // 2, eye_center[1] + eye_size // 2
                ]
                draw.ellipse(eye_rect, fill=profile.eye_color)
                # Add highlight
                highlight_size = eye_size // 4
                highlight_rect = [
                    eye_center[0] - highlight_size // 2, 
                    eye_center[1] - eye_size // 3 - highlight_size // 2,
                    eye_center[0] + highlight_size // 2, 
                    eye_center[1] - eye_size // 3 + highlight_size // 2
                ]
                draw.ellipse(highlight_rect, fill=(255, 255, 255, 200))
                
            elif profile.eye_shape == 'square':
                eye_rect = [
                    eye_center[0] - eye_size // 2, eye_center[1] - eye_size // 2,
                    eye_center[0] + eye_size // 2, eye_center[1] + eye_size // 2
                ]
                draw.rectangle(eye_rect, fill=profile.eye_color)
                
            elif profile.eye_shape == 'diamond':
                points = [
                    (eye_center[0], eye_center[1] - eye_size // 2),  # Top
                    (eye_center[0] + eye_size // 2, eye_center[1]),  # Right
                    (eye_center[0], eye_center[1] + eye_size // 2),  # Bottom
                    (eye_center[0] - eye_size // 2, eye_center[1])   # Left
                ]
                draw.polygon(points, fill=profile.eye_color)
    
    def _draw_mouth(self, draw: ImageDraw.Draw, center_x: int, center_y: int,
                    head_size: int, profile: EmotionProfile):
        """Draw mouth based on emotion profile"""
        mouth_width = head_size // 3
        mouth_rect = [
            center_x - mouth_width // 2, center_y - 10,
            center_x + mouth_width // 2, center_y + 10
        ]
        
        if profile.mouth_curve > 0:  # Smile
            curve_amount = profile.mouth_curve
            draw.arc([mouth_rect[0], mouth_rect[1] - curve_amount,
                     mouth_rect[2], mouth_rect[3] + curve_amount],
                    0, 180, fill=profile.mouth_color, width=4)
        elif profile.mouth_curve < 0:  # Frown
            curve_amount = abs(profile.mouth_curve)
            draw.arc([mouth_rect[0], mouth_rect[1] - curve_amount,
                     mouth_rect[2], mouth_rect[3] + curve_amount],
                    180, 360, fill=profile.mouth_color, width=4)
        else:  # Neutral line
            draw.line([mouth_rect[0], center_y, mouth_rect[2], center_y],
                     fill=profile.mouth_color, width=4)
    
    def _draw_antennas(self, draw: ImageDraw.Draw, center_x: int, top_y: int,
                       profile: EmotionProfile):
        """Draw antennas based on style"""
        if profile.antenna_style == 'excited':
            # Upward antennas
            draw.line([center_x - 30, top_y, center_x - 25, top_y - 30],
                     fill=(150, 150, 150), width=3)
            draw.line([center_x + 30, top_y, center_x + 25, top_y - 30],
                     fill=(150, 150, 150), width=3)
            # Antenna tips
            draw.ellipse([center_x - 30, top_y - 35, center_x - 20, top_y - 25],
                        fill=profile.eye_color)
            draw.ellipse([center_x + 20, top_y - 35, center_x + 30, top_y - 25],
                        fill=profile.eye_color)
        elif profile.antenna_style == 'droopy':
            # Drooping antennas
            draw.line([center_x - 30, top_y, center_x - 35, top_y - 10],
                     fill=(150, 150, 150), width=3)
            draw.line([center_x + 30, top_y, center_x + 35, top_y - 10],
                     fill=(150, 150, 150), width=3)
    
    def _draw_panel_details(self, draw: ImageDraw.Draw, head_rect: list,
                           profile: EmotionProfile):
        """Draw panel details and indicators"""
        # Status LED
        led_x = head_rect[2] - 20
        led_y = head_rect[1] + 15
        draw.ellipse([led_x - 5, led_y - 5, led_x + 5, led_y + 5],
                    fill=profile.glow_color)
        
        # Panel lines
        for i in range(3):
            y = head_rect[3] - 40 + i * 10
            draw.line([head_rect[0] + 10, y, head_rect[2] - 10, y],
                     fill=(180, 180, 190, 100), width=1)
    
    def _create_glow_effect(self, size: int, head_rect: list, 
                           glow_color: Tuple[int, int, int], 
                           intensity: float) -> Image.Image:
        """Create glow effect around the head"""
        glow_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        
        # Create multiple glow layers
        for i in range(5):
            offset = (i + 1) * 3
            alpha = int(intensity * 50 / (i + 1))
            glow_rect = [
                head_rect[0] - offset, head_rect[1] - offset,
                head_rect[2] + offset, head_rect[3] + offset
            ]
            glow_draw.ellipse(glow_rect, fill=(*glow_color, alpha))
        
        # Apply blur
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=3))
        return glow_img
    
    def _apply_special_effects(self, img: Image.Image, profile: EmotionProfile,
                              size: int) -> Image.Image:
        """Apply special effects based on emotion"""
        effects = profile.special_effects
        
        if effects.get('sparkles'):
            img = self._add_sparkles(img, size)
        elif effects.get('scanning_lines'):
            img = self._add_scanning_lines(img, size)
        elif effects.get('zzz_particles'):
            img = self._add_sleep_particles(img, size)
        
        return img
    
    def _add_sparkles(self, img: Image.Image, size: int) -> Image.Image:
        """Add sparkle effects for happy emotion"""
        draw = ImageDraw.Draw(img)
        for _ in range(8):
            x = random.randint(20, size - 20)
            y = random.randint(20, size - 20)
            draw.polygon([
                (x, y - 8), (x + 3, y - 3), (x + 8, y),
                (x + 3, y + 3), (x, y + 8), (x - 3, y + 3),
                (x - 8, y), (x - 3, y - 3)
            ], fill=(255, 255, 255, 200))
        return img
    
    def _add_scanning_lines(self, img: Image.Image, size: int) -> Image.Image:
        """Add scanning line effects for thinking emotion"""
        draw = ImageDraw.Draw(img)
        for i in range(0, size, 20):
            draw.line([0, i, size, i], fill=(255, 255, 255, 30), width=2)
        return img
    
    def _add_sleep_particles(self, img: Image.Image, size: int) -> Image.Image:
        """Add Z particles for sleeping emotion"""
        draw = ImageDraw.Draw(img)
        # Draw "Z" letters floating around
        positions = [(size - 60, 40), (size - 40, 80), (size - 80, 120)]
        for i, (x, y) in enumerate(positions):
            alpha = 150 - i * 30
            # Simple Z shape
            draw.line([x, y, x + 15, y], fill=(200, 200, 255, alpha), width=3)
            draw.line([x + 15, y, x, y + 15], fill=(200, 200, 255, alpha), width=2)
            draw.line([x, y + 15, x + 15, y + 15], fill=(200, 200, 255, alpha), width=3)
        return img
    
    def _draw_rounded_rectangle(self, draw: ImageDraw.Draw, rect: list,
                               radius: int, **kwargs):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = rect
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], **kwargs)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], **kwargs)
        
        # Corners
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 
                     180, 270, **kwargs)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 
                     270, 360, **kwargs)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 
                     90, 180, **kwargs)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 
                     0, 90, **kwargs)
    
    def get_available_emotions(self) -> list:
        """Get list of available emotions"""
        return list(self.emotions.keys())
    
    def clear_cache(self):
        """Clear the avatar generation cache"""
        self.generate_avatar.cache_clear()
        self.cache.clear()


class AvatarGenerationThread(QThread):
    """Thread for non-blocking avatar generation"""
    avatar_generated = pyqtSignal(object, str)
    generation_failed = pyqtSignal(str)
    
    def __init__(self, generator: RobotAvatarGenerator, emotion: str, 
                 size: int = 400, style: str = 'modern'):
        super().__init__()
        self.generator = generator
        self.emotion = emotion
        self.size = size
        self.style = style
        
    def run(self):
        try:
            start_time = time.time()
            avatar = self.generator.generate_avatar(
                emotion=self.emotion,
                size=self.size,
                style=self.style
            )
            generation_time = time.time() - start_time
            logging.info(f"Avatar generated for '{self.emotion}' in {generation_time:.3f}s")
            self.avatar_generated.emit(avatar, self.emotion)
        except Exception as e:
            logging.error(f"Avatar generation failed: {e}")
            self.generation_failed.emit(str(e))


class AvatarManager:
    """High-level avatar management system"""
    
    def __init__(self, cache_size: int = 50):
        self.generator = RobotAvatarGenerator()
        self.current_emotion = 'idle'
        self.cache_size = cache_size
        self.generation_callbacks = []
        
    def generate_avatar_async(self, emotion: str, callback=None, 
                             size: int = 400, style: str = 'modern'):
        """Generate avatar asynchronously"""
        if callback:
            self.generation_callbacks.append(callback)
            
        thread = AvatarGenerationThread(
            self.generator, emotion, size, style
        )
        thread.avatar_generated.connect(self._on_avatar_generated)
        thread.generation_failed.connect(self._on_generation_failed)
        thread.start()
        return thread
    
    def generate_avatar_sync(self, emotion: str, size: int = 400, 
                            style: str = 'modern') -> Image.Image:
        """Generate avatar synchronously"""
        return self.generator.generate_avatar(emotion, size, style)
    
    def _on_avatar_generated(self, avatar: Image.Image, emotion: str):
        """Handle successful avatar generation"""
        self.current_emotion = emotion
        for callback in self.generation_callbacks:
            callback(avatar, emotion)
        self.generation_callbacks.clear()
    
    def _on_generation_failed(self, error: str):
        """Handle failed avatar generation"""
        logging.error(f"Avatar generation failed: {error}")
        self.generation_callbacks.clear()
    
    def get_available_emotions(self) -> list:
        """Get list of available emotions"""
        return self.generator.get_available_emotions()
    
    def pil_to_qpixmap(self, pil_image: Image.Image) -> QPixmap:
        """Convert PIL image to QPixmap for PyQt6"""
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt6 not available")
            
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        return pixmap


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Test the generator
    if PIL_AVAILABLE:
        generator = RobotAvatarGenerator()
        
        print("Available emotions:", generator.get_available_emotions())
        
        # Generate test avatars
        for emotion in ['idle', 'happy', 'thinking', 'error']:
            print(f"Generating {emotion} avatar...")
            start_time = time.time()
            avatar = generator.generate_avatar(emotion=emotion, size=400, style='modern')
            end_time = time.time()
            print(f"Generated in {end_time - start_time:.3f} seconds")
            
            # Save for testing
            output_path = f"/tmp/test_avatar_{emotion}.png"
            avatar.save(output_path)
            print(f"Saved to {output_path}")
    else:
        print("PIL not available - cannot test avatar generation")