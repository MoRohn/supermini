#!/usr/bin/env python3
from __future__ import annotations
"""
SuperMini (AI Multimedia and Management) Application
A desktop AI assistant for macOS with task automation, multimedia processing,
and self-improvement capabilities.
"""

import sys
import os
import json
import subprocess
import logging
import time
import re
import shutil
import base64
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Import task intelligence for autonomous decision-making
from src.core.task_intelligence import TaskIntelligence, ResponseAnalyzer

# Third-party imports
try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with 'pip install requests'")
    sys.exit(1)

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Error: 'pandas' and 'numpy' are required. Install them with 'pip install pandas numpy'")
    sys.exit(1)

try:
    import psutil
except ImportError:
    print("Error: 'psutil' is required. Install it with 'pip install psutil'")
    sys.exit(1)

# Professional dashboard imports
try:
    import matplotlib
    matplotlib.use('qtagg')  # Use PyQt6 backend for proper integration
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    logging.warning(f"matplotlib not available - dashboard will have limited functionality: {e}")

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout,
        QHBoxLayout, QGridLayout, QWidget, QLabel, QFileDialog, QMessageBox, QCheckBox,
        QProgressBar, QDialog, QTextBrowser, QFormLayout, QComboBox, QTextEdit,
        QSplitter, QTabWidget, QSlider, QSpinBox, QGroupBox, QScrollArea, QSizePolicy,
        QTreeWidget, QTreeWidgetItem
    )
    from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QSettings, QPropertyAnimation, QEasingCurve, QPointF
    from PyQt6.QtGui import QPixmap, QFont, QIcon, QPainter, QPen, QBrush, QLinearGradient, QColor
except ImportError:
    print("Error: 'PyQt6' is required. Install it with 'pip install PyQt6'")
    sys.exit(1)

# AI and ML imports
try:
    from anthropic import Anthropic, AnthropicError
except ImportError:
    print("Warning: Anthropic library not found. Claude functionality will be disabled.")
    Anthropic = None
    AnthropicError = Exception

try:
    import chromadb
except ImportError:
    print("Warning: ChromaDB not found. Memory functionality will be limited.")
    chromadb = None

# Autonomous agent imports
try:
    from src.autonomous.autonomous_agent import AutonomousAgent, AutonomousWorkflowManager, AutonomousTask
    AUTONOMOUS_AVAILABLE = True
except ImportError:
    print("Warning: Autonomous agent not available. Install gui-agents for full functionality.")
    AUTONOMOUS_AVAILABLE = False

# Enhanced activity monitoring imports
try:
    from src.utils.activity_monitor import (
        get_activity_logger, ActivityMonitorWidget, 
        ActivityType, ActivityLevel, log_activity
    )
    ACTIVITY_MONITORING_AVAILABLE = True
except ImportError:
    print("Warning: Enhanced activity monitoring not available.")
    ACTIVITY_MONITORING_AVAILABLE = False
    # Fallback functions
    def get_activity_logger(*args, **kwargs):
        return None
    def log_activity(*args, **kwargs):
        pass

# App metadata
APP_VERSION = "2.0.0"
APP_NAME = "SuperMini"
UPDATE_URL = "https://api.github.com/repos/your-org/aimm/releases/latest"

# AI Status Message Variations (like Claude Code)
def get_random_ai_status() -> str:
    """Generate random AI processing status messages like Claude Code"""
    thinking_verbs = [
        "Thinking", "Processing", "Computing", "Analyzing", "Reasoning", 
        "Pondering", "Contemplating", "Deliberating", "Evaluating", "Calculating",
        "Cogitating", "Reflecting", "Examining", "Investigating", "Exploring",
        "Synthesizing", "Formulating", "Orchestrating", "Architecting", "Optimizing"
    ]
    
    neural_adjectives = [
        "deeply", "carefully", "intelligently", "strategically", "creatively",
        "methodically", "systematically", "thoroughly", "precisely", "elegantly",
        "efficiently", "thoughtfully", "comprehensively", "analytically", "logically"
    ]
    
    # Sometimes just the verb, sometimes with an adverb
    if random.choice([True, False]):
        return f"🤖 AI: {random.choice(thinking_verbs)}"
    else:
        return f"🤖 AI: {random.choice(thinking_verbs)} {random.choice(neural_adjectives)}"

def get_random_status_message() -> str:
    """Generate random status bar messages"""
    status_messages = [
        "Processing task...", "Computing response...", "Analyzing request...",
        "Thinking through solution...", "Formulating response...", "Working on task...",
        "Neural networks active...", "AI systems engaged...", "Deep thinking in progress...",
        "Cognitive processing...", "Synthesizing information...", "Orchestrating response..."
    ]
    return random.choice(status_messages)

# Modern Icon System
class ModernIcons:
    """Modern minimalistic icon system using clean Unicode symbols for professional appearance"""
    
    # Application icons - ultra-clean and minimalistic
    APP = {
        'logo': '◆',
        'menu': '≡',
        'close': '×',
        'minimize': '−',
        'maximize': '□',
        'settings': '◦',
        'theme': '◗',
        'info': 'i',
        'help': '?',
        'refresh': '↻'
    }
    
    # Task type icons - clean geometric shapes
    TASKS = {
        'task': '□',
        'code': '<>',
        'multimedia': '▣',
        'rag': '▤',
        'automation': '⟳',
        'analytics': '▦',
        'auto_detect': '◉'
    }
    
    # Action icons - minimal and intuitive
    ACTIONS = {
        'play': '▷',
        'pause': '⏸',
        'stop': '◼',
        'upload': '↑',
        'download': '↓',
        'attach': '◎',
        'delete': '×',
        'edit': '✎',
        'save': '◊',
        'copy': '▣',
        'share': '↗',
        'expand': '⤢',
        'collapse': '⤡'
    }
    
    # Status icons - clear monochromatic feedback
    STATUS = {
        'success': '✓',
        'error': '✗',
        'warning': '⚠',
        'info': 'i',
        'loading': '◐',
        'processing': '◑',
        'idle': '○',
        'active': '●'
    }
    
    # Navigation icons - geometric and clean
    NAVIGATION = {
        'back': '‹',
        'forward': '›',
        'up': '▲',
        'down': '▼',
        'home': '⌂',
        'search': '○',
        'filter': '▦',
        'sort': '⟷'
    }
    
    @classmethod
    def get_icon(cls, category: str, name: str) -> str:
        """Get an icon from a specific category"""
        categories = {
            'app': cls.APP,
            'tasks': cls.TASKS,
            'actions': cls.ACTIONS,
            'status': cls.STATUS,
            'nav': cls.NAVIGATION
        }
        return categories.get(category, {}).get(name, '○')
    
    @classmethod
    def get_task_icon(cls, task_type: str) -> str:
        """Get the appropriate icon for a task type with fallback"""
        task_mapping = {
            'code': cls.TASKS['code'],
            'multimedia': cls.TASKS['multimedia'],
            'rag': cls.TASKS['rag'],
            'automation': cls.TASKS['automation'],
            'analytics': cls.TASKS['analytics'],
            'auto_detect': cls.TASKS['auto_detect']
        }
        return task_mapping.get(task_type, cls.TASKS['task'])
    
    @classmethod
    def task_icon(cls, task_type: str) -> str:
        """Get icon for task type"""
        return cls.TASKS.get(task_type.lower(), cls.TASKS['auto_detect'])

# Modern Design System
class ModernTheme:
    """Modern design system with consistent colors, typography, and spacing"""
    
    # DPI and scaling awareness
    _scale_factor = None
    _base_font_size = None
    
    # Theme system
    _current_theme = 'dark'  # 'dark' or 'light'
    _mobile_breakpoint = 768
    _tablet_breakpoint = 1024
    
    # Screen size categories
    SCREEN_MOBILE = 'mobile'
    SCREEN_TABLET = 'tablet'
    SCREEN_DESKTOP = 'desktop'
    
    @classmethod
    def initialize_scaling(cls, app: QApplication):
        """Initialize DPI-aware scaling factors"""
        screen = app.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        physical_dpi = screen.physicalDotsPerInch()
        cls._scale_factor = max(1.0, dpi / 96.0)  # 96 DPI is the standard
        
        # Base font size from system
        font = app.font()
        cls._base_font_size = max(11, font.pointSize())
        
        # Log detailed scaling information
        screen_geometry = screen.geometry()
        available_geometry = screen.availableGeometry()
        
        logging.info(
            f"UI Scaling Initialized:\n"
            f"  Logical DPI: {dpi:.1f}\n"
            f"  Physical DPI: {physical_dpi:.1f}\n"
            f"  Scale Factor: {cls._scale_factor:.2f}\n"
            f"  Base Font Size: {cls._base_font_size}pt\n"
            f"  Screen Resolution: {screen_geometry.width()}x{screen_geometry.height()}\n"
            f"  Available Area: {available_geometry.width()}x{available_geometry.height()}"
        )
    
    @classmethod
    def set_theme(cls, theme: str):
        """Set the current theme (dark or light)"""
        if theme in ['dark', 'light']:
            cls._current_theme = theme
            logging.info(f"Theme changed to: {theme}")
    
    @classmethod
    def get_current_theme(cls) -> str:
        """Get the current theme"""
        return cls._current_theme
    
    @classmethod
    def get_screen_category(cls, width: int) -> str:
        """Get screen category based on width"""
        if width < cls._mobile_breakpoint:
            return cls.SCREEN_MOBILE
        elif width < cls._tablet_breakpoint:
            return cls.SCREEN_TABLET
        else:
            return cls.SCREEN_DESKTOP
    
    @classmethod
    def is_mobile(cls, width: int) -> bool:
        """Check if screen size is mobile"""
        return width < cls._mobile_breakpoint
    
    @classmethod
    def is_tablet(cls, width: int) -> bool:
        """Check if screen size is tablet"""
        return cls._mobile_breakpoint <= width < cls._tablet_breakpoint
    
    @classmethod
    def get_responsive_spacing(cls, screen_category: str, size_key: str) -> str:
        """Get responsive spacing based on screen size"""
        base_spacing = {
            'xs': 2, 'sm': 4, 'md': 6, 'lg': 8,
            'xl': 12, 'xxl': 16, 'xxxl': 20
        }
        
        # Scale based on screen size
        multiplier = {
            cls.SCREEN_MOBILE: 0.8,
            cls.SCREEN_TABLET: 1.0,
            cls.SCREEN_DESKTOP: 1.2
        }
        
        base_value = base_spacing.get(size_key, 6)
        scaled_value = int(base_value * multiplier.get(screen_category, 1.0))
        return f"{cls.scale_value(scaled_value)}px"
    
    @classmethod
    def get_responsive_font_size(cls, screen_category: str, size_key: str) -> str:
        """Get responsive font size based on screen size with enhanced scaling"""
        base_sizes = {
            'xs': 9, 'sm': 10, 'base': 11, 'lg': 12,
            'xl': 14, 'xxl': 16, 'title': 18, 'heading': 22, 'display': 28
        }
        
        # Enhanced responsive scaling with better mobile optimization
        multiplier = {
            cls.SCREEN_MOBILE: 0.85,    # Slightly smaller for mobile screens
            cls.SCREEN_TABLET: 0.95,    # Optimized for tablet reading
            cls.SCREEN_DESKTOP: 1.0     # Standard desktop sizing
        }
        
        base_size = base_sizes.get(size_key, 11)
        if cls._base_font_size:
            scale_factor = base_size / 11
            scaled_size = int(cls._base_font_size * scale_factor * multiplier.get(screen_category, 1.0))
            return f"{max(scaled_size, 9)}pt"  # Minimum readable size
        else:
            scaled_size = int(base_size * multiplier.get(screen_category, 1.0))
            return f"{max(scaled_size, 9)}pt"  # Minimum readable size
    
    @classmethod
    def scale_value(cls, value: int) -> int:
        """Scale a pixel value according to DPI"""
        if cls._scale_factor is None:
            return value
        return int(value * cls._scale_factor)
    
    @classmethod
    def get_font_size(cls, size_key: str) -> str:
        """Get DPI-scaled font size"""
        base_sizes = {
            'xs': 9, 'sm': 10, 'base': 11, 'lg': 12,
            'xl': 14, 'xxl': 16, 'title': 18, 'heading': 22
        }
        
        if cls._base_font_size is None:
            return f"{base_sizes.get(size_key, 11)}pt"
        
        # Scale relative to system base font size
        scale_factor = base_sizes.get(size_key, 11) / 11
        scaled_size = int(cls._base_font_size * scale_factor)
        return f"{scaled_size}pt"
    
    @classmethod
    def get_spacing(cls, size_key: str) -> str:
        """Get DPI-scaled spacing"""
        base_spacing = {
            'xs': 3, 'sm': 6, 'md': 9, 'lg': 12,
            'xl': 15, 'xxl': 18, 'xxxl': 24
        }
        scaled = cls.scale_value(base_spacing.get(size_key, 6))
        return f"{scaled}px"
    
    # Minimalistic Color Palettes - Dark and Light themes
    DARK_COLORS = {
        # Primary colors - WCAG AA compliant blue palette
        'primary': '#3B82F6',        # Enhanced blue for better contrast
        'primary_hover': '#2563EB',  # Darker blue on hover
        'primary_light': '#60A5FA',  # Lighter accessible blue
        'primary_dark': '#1E40AF',   # Deep blue with high contrast
        
        # Secondary colors - accessible grays
        'secondary': '#9CA3AF',      # Better contrast gray
        'secondary_hover': '#6B7280', # Enhanced hover state
        'accent': '#EF4444',         # High contrast red
        'accent_soft': '#F87171',    # Accessible soft red
        
        # Background colors - refined dark theme
        'bg_primary': '#0F0F0F',     # Deep black with subtle warmth
        'bg_secondary': '#1F1F23',   # Enhanced dark secondary
        'bg_tertiary': '#27272A',    # Improved tertiary background
        'bg_hover': '#3F3F46',       # Higher contrast hover
        'bg_panel': '#09090B',       # Panel background with depth
        
        # Card and input backgrounds - enhanced contrast
        'bg_card': '#18181B',        # Better card contrast
        'bg_input': '#27272A',       # Improved input visibility
        
        # Text colors - WCAG AA compliant
        'text_primary': '#FAFAFA',   # Softer white for reduced eye strain
        'text_secondary': '#E4E4E7', # High contrast secondary text
        'text_muted': '#A1A1AA',     # Better contrast muted text
        'text_disabled': '#52525B',  # Improved disabled state visibility
        'text_accent': '#60A5FA',    # Accessible accent text
        'text_inverse': '#FFFFFF',   # White text for dark backgrounds
        
        # Status colors - WCAG compliant
        'success': '#22C55E',        # High contrast green
        'success_bg': '#14532D',     # Enhanced success background
        'warning': '#F59E0B',        # Better contrast orange
        'warning_bg': '#451A03',     # Improved warning background
        'error': '#EF4444',          # High contrast red
        'error_bg': '#7F1D1D',       # Enhanced error background
        'info': '#3B82F6',           # Consistent info blue
        'info_bg': '#1E3A8A',        # Better info background
        
        # Border colors - improved visibility
        'border': '#3F3F46',         # Higher contrast borders
        'border_light': '#52525B',   # More visible light borders
        'border_input': '#52525B',   # Enhanced input borders
        'border_focus': '#3B82F6',   # Consistent focus state
        
        # Enhanced shadows and effects
        'shadow_sm': 'rgba(0, 0, 0, 0.4)',
        'shadow_md': 'rgba(0, 0, 0, 0.5)',
        'shadow_lg': 'rgba(0, 0, 0, 0.6)',
        'glow': 'rgba(59, 130, 246, 0.35)',
        'glow_soft': 'rgba(59, 130, 246, 0.15)',
        'glassmorphism': 'rgba(255, 255, 255, 0.08)',
        
        # Zen dashboard colors
        'bg_zen': '#1A1A1A',         # Zen dashboard background
        'text_zen': '#3B82F6',       # Zen dashboard text/metrics
        'text_neural': '#9CA3AF'     # Neural network text
    }
    
    LIGHT_COLORS = {
        # Primary colors - WCAG AA compliant blue palette
        'primary': '#1D4ED8',        # Enhanced blue for better light mode contrast
        'primary_hover': '#1E40AF',  # Darker blue on hover
        'primary_light': '#3B82F6',  # Lighter accessible blue
        'primary_dark': '#1E3A8A',   # Deep blue with high contrast
        
        # Secondary colors - accessible grays
        'secondary': '#6B7280',      # Better contrast gray
        'secondary_hover': '#4B5563', # Enhanced hover state
        'accent': '#DC2626',         # High contrast red
        'accent_soft': '#EF4444',    # Accessible soft red
        
        # Background colors - refined light theme
        'bg_primary': '#FFFFFF',     # Pure white
        'bg_secondary': '#F8FAFC',   # Enhanced light secondary
        'bg_tertiary': '#F1F5F9',    # Improved tertiary background
        'bg_hover': '#E2E8F0',       # Higher contrast hover
        'bg_panel': '#FDFDFD',       # Panel background with depth
        
        # Card and input backgrounds - enhanced contrast
        'bg_card': '#FFFFFF',        # Clean card backgrounds
        'bg_input': '#F8FAFC',       # Improved input visibility
        
        # Text colors - WCAG AA compliant
        'text_primary': '#0F172A',   # Deep black for maximum contrast
        'text_secondary': '#334155', # High contrast secondary text
        'text_muted': '#64748B',     # Better contrast muted text
        'text_disabled': '#CBD5E1',  # Improved disabled state visibility
        'text_accent': '#1D4ED8',    # Accessible accent text
        'text_inverse': '#FFFFFF',   # White text for dark backgrounds
        
        # Status colors - WCAG compliant
        'success': '#059669',        # High contrast green
        'success_bg': '#ECFDF5',     # Enhanced success background
        'warning': '#D97706',        # Better contrast orange
        'warning_bg': '#FFFBEB',     # Improved warning background
        'error': '#DC2626',          # High contrast red
        'error_bg': '#FEF2F2',       # Enhanced error background
        'info': '#1D4ED8',           # Consistent info blue
        'info_bg': '#EFF6FF',        # Better info background
        
        # Border colors - improved visibility
        'border': '#CBD5E1',         # Higher contrast borders
        'border_light': '#E2E8F0',   # More visible light borders
        'border_input': '#CBD5E1',   # Enhanced input borders
        'border_focus': '#1D4ED8',   # Consistent focus state
        
        # Enhanced shadows and effects
        'shadow_sm': 'rgba(0, 0, 0, 0.08)',
        'shadow_md': 'rgba(0, 0, 0, 0.12)',
        'shadow_lg': 'rgba(0, 0, 0, 0.18)',
        'glow': 'rgba(29, 78, 216, 0.25)',
        'glow_soft': 'rgba(29, 78, 216, 0.08)',
        'glassmorphism': 'rgba(0, 0, 0, 0.03)',
        
        # Zen dashboard colors
        'bg_zen': '#F8FAFC',         # Zen dashboard background (light)
        'text_zen': '#1D4ED8',       # Zen dashboard text/metrics (light)
        'text_neural': '#64748B'     # Neural network text (light)
    }
    
    @classmethod
    def get_colors(cls) -> dict:
        """Get colors for current theme"""
        return cls.DARK_COLORS if cls._current_theme == 'dark' else cls.LIGHT_COLORS
    
    # Legacy COLORS property for backwards compatibility
    @classmethod
    def COLORS(cls):
        return cls.get_colors()
    
    # Enhanced utility methods for modern styling
    @classmethod
    def get_card_style(cls, elevated: bool = False, floating: bool = False) -> str:
        """Get modern card styling with floating panel effects"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        
        if floating:
            shadow = shadows['floating']
        elif elevated:
            shadow = shadows['lg']
        else:
            shadow = shadows['card']
        
        return f"""
            background-color: {colors['bg_card']};
            border: 1px solid {colors['border']};
            border-radius: {cls.get_border_radius('lg')};
        """
    
    @classmethod
    def get_modern_panel_style(cls, type: str = 'default') -> str:
        """Get modern panel styling with depth and polish"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        
        panel_configs = {
            'default': {
                'bg': colors['bg_card'],
                'border': colors['border'],
                'shadow': shadows['card']
            },
            'elevated': {
                'bg': colors['bg_card'],
                'border': colors['border_light'],
                'shadow': shadows['floating']
            },
            'glass': {
                'bg': colors['glassmorphism'],
                'border': colors['border_light'],
                'shadow': shadows['glow_soft']
            }
        }
        
        config = panel_configs.get(type, panel_configs['default'])
        
        return f"""
            background-color: {config['bg']};
            border: 1px solid {config['border']};
            border-radius: {cls.get_border_radius('lg')};
        """
    
    @classmethod
    def get_micro_interactions_style(cls) -> str:
        """Get micro-interactions and smooth transitions for enhanced UX"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        
        return f"""
        /* Enhanced Micro-Interactions */
        * {{
        }}
        
        /* Button hover and click animations */
        QPushButton {{
        }}
        
        QPushButton:hover {{
        }}
        
        QPushButton:pressed {{
        }}
        
        /* Input field focus animations */
        QLineEdit, QTextEdit, QComboBox {{
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        }}
        
        /* Tab switching animations */
        QTabBar::tab {{
        }}
        
        QTabWidget::pane {{
        }}
        
        /* Progress bar animations */
        QProgressBar {{
        }}
        
        QProgressBar::chunk {{
        }}
        
        /* Checkbox and radio animations */
        QCheckBox::indicator {{
        }}
        
        QCheckBox::indicator:checked {{
        }}
        
        QRadioButton::indicator {{
        }}
        
        QRadioButton::indicator:checked {{
        }}
        
        /* Slider animations */
        QSlider::handle {{
        }}
        
        QSlider::handle:hover {{
        }}
        
        /* Group box hover effects */
        QGroupBox {{
        }}
        
        /* Scroll area smooth scrolling */
        QScrollArea {{
        }}
        
        QScrollBar {{
        }}
        
        QScrollBar::handle {{
        }}
        
        /* Menu and tooltip animations */
        QMenu {{
        }}
        
        QToolTip {{
        }}
        """
    
    @classmethod
    def get_accessibility_style(cls) -> str:
        """Get WCAG 2.1 AA compliant accessibility styles"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        
        return f"""
        /* WCAG 2.1 AA Accessibility Compliance */
        
        /* High contrast focus indicators */
        *:focus {{
            outline: {cls.scale_value(2)}px solid {colors['border_focus']};
            outline-offset: {cls.scale_value(2)}px;
        }}
        
        /* Enhanced button focus for keyboard navigation */
        QPushButton:focus {{
            outline: {cls.scale_value(3)}px solid {colors['border_focus']};
            outline-offset: {cls.scale_value(3)}px;
            background-color: {colors['bg_hover']};
        }}
        
        /* Input field accessibility */
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: {cls.scale_value(2)}px solid {colors['border_focus']};
            outline: {cls.scale_value(2)}px solid {colors['border_focus']};
            outline-offset: {cls.scale_value(1)}px;
            background-color: {colors['bg_input']};
        }}
        
        /* Enhanced checkbox and radio accessibility */
        QCheckBox:focus::indicator, QRadioButton:focus::indicator {{
            outline: {cls.scale_value(2)}px solid {colors['border_focus']};
            outline-offset: {cls.scale_value(2)}px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border: {cls.scale_value(2)}px solid {colors['primary']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['primary']};
            border: {cls.scale_value(3)}px solid {colors['primary']};
        }}
        
        /* Tab accessibility */
        QTabBar::tab:focus {{
            outline: {cls.scale_value(2)}px solid {colors['border_focus']};
            outline-offset: {cls.scale_value(2)}px;
            background-color: {colors['bg_hover']};
        }}
        
        /* Slider accessibility */
        QSlider:focus {{
            outline: {cls.scale_value(2)}px solid {colors['border_focus']};
            outline-offset: {cls.scale_value(2)}px;
        }}
        
        QSlider::handle:focus {{
            background-color: {colors['primary']};
            border: {cls.scale_value(3)}px solid {colors['border_focus']};
            outline: {cls.scale_value(2)}px solid {colors['border_focus']};
        }}
        
        /* Progress bar accessibility */
        QProgressBar {{
            border: {cls.scale_value(1)}px solid {colors['border']};
            background-color: {colors['bg_input']};
            color: {colors['text_primary']};
            font-weight: 500;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: {cls.get_border_radius('sm')};
        }}
        
        /* Menu accessibility */
        QMenu {{
            border: {cls.scale_value(1)}px solid {colors['border']};
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_primary']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
            color: {colors['text_primary']};
            outline: {cls.scale_value(1)}px solid {colors['border_focus']};
        }}
        
        /* Status and error text accessibility */
        .status-success {{
            color: {colors['success']};
            background-color: {colors['success_bg']};
            padding: {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('md')};
            border: {cls.scale_value(1)}px solid {colors['success']};
        }}
        
        .status-error {{
            color: {colors['error']};
            background-color: {colors['error_bg']};
            padding: {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('md')};
            border: {cls.scale_value(1)}px solid {colors['error']};
        }}
        
        .status-warning {{
            color: {colors['warning']};
            background-color: {colors['warning_bg']};
            padding: {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('md')};
            border: {cls.scale_value(1)}px solid {colors['warning']};
        }}
        
        .status-info {{
            color: {colors['info']};
            background-color: {colors['info_bg']};
            padding: {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('md')};
            border: {cls.scale_value(1)}px solid {colors['info']};
        }}
        
        /* Disabled state accessibility */
        *:disabled {{
            opacity: 0.6;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_disabled']};
            border-color: {colors['border']};
        }}
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {{
            * {{
                border-width: {cls.scale_value(2)}px !important;
            }}
            
            QPushButton {{
                border-width: {cls.scale_value(2)}px !important;
                font-weight: 600 !important;
            }}
            
            QTabBar::tab {{
                border-width: {cls.scale_value(2)}px !important;
                font-weight: 600 !important;
            }}
        }}
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {{
            * {{
            }}
        }}
        """
    
    @classmethod
    def get_adaptive_typography_style(cls) -> str:
        """Get adaptive typography styles that scale based on screen size"""
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            screen_width = screen.availableGeometry().width()
            screen_category = cls.get_screen_category(screen_width)
        else:
            screen_category = cls.SCREEN_DESKTOP
        
        colors = cls.get_colors()
        
        # Dynamic font sizes based on screen category
        heading_size = cls.get_responsive_font_size(screen_category, 'heading')
        title_size = cls.get_responsive_font_size(screen_category, 'title')
        large_size = cls.get_responsive_font_size(screen_category, 'xl')
        base_size = cls.get_responsive_font_size(screen_category, 'base')
        small_size = cls.get_responsive_font_size(screen_category, 'sm')
        
        return f"""
        /* Adaptive Typography System */
        .heading {{
            font-size: {heading_size};
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: -0.02em;
            color: {colors['text_primary']};
        }}
        
        .title {{
            font-size: {title_size};
            font-weight: 600;
            line-height: 1.3;
            letter-spacing: -0.01em;
            color: {colors['text_primary']};
        }}
        
        .large {{
            font-size: {large_size};
            font-weight: 500;
            line-height: 1.4;
            color: {colors['text_primary']};
        }}
        
        .body {{
            font-size: {base_size};
            font-weight: 400;
            line-height: 1.6;
            color: {colors['text_primary']};
        }}
        
        .small {{
            font-size: {small_size};
            font-weight: 400;
            line-height: 1.5;
            color: {colors['text_secondary']};
        }}
        
        /* Responsive text scaling for QLabel */
        QLabel[class="heading"] {{
            font-size: {heading_size};
            font-weight: 700;
            color: {colors['text_primary']};
        }}
        
        QLabel[class="title"] {{
            font-size: {title_size};
            font-weight: 600;
            color: {colors['text_primary']};
        }}
        
        QLabel[class="body"] {{
            font-size: {base_size};
            font-weight: 400;
            color: {colors['text_primary']};
        }}
        
        QLabel[class="small"] {{
            font-size: {small_size};
            font-weight: 400;
            color: {colors['text_secondary']};
        }}
        """
    
    @classmethod
    def get_mobile_touch_style(cls) -> str:
        """Enhanced mobile touch optimization styles"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        return f"""
        /* Enhanced touch targets for mobile */
        QWidget {{
        }}
        
        /* Larger touch targets for small controls */
        QCheckBox::indicator {{
            width: {cls.scale_value(20)}px;
            height: {cls.scale_value(20)}px;
            border-radius: {cls.get_border_radius('sm')};
        }}
        
        QRadioButton::indicator {{
            width: {cls.scale_value(20)}px;
            height: {cls.scale_value(20)}px;
            border-radius: 50%;
        }}
        
        /* Enhanced scroll bar for touch */
        QScrollBar:vertical {{
            background: {colors['bg_secondary']};
            width: {cls.scale_value(12)}px;
            border-radius: {cls.scale_value(6)}px;
            margin: {cls.scale_value(2)}px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {colors['secondary']};
            min-height: {cls.scale_value(30)}px;
            border-radius: {cls.scale_value(5)}px;
            margin: {cls.scale_value(1)}px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {colors['secondary_hover']};
        }}
        
        /* Touch-friendly splitter */
        QSplitter::handle {{
            background-color: {colors['border']};
            width: {cls.scale_value(6)}px;
            height: {cls.scale_value(6)}px;
            border-radius: {cls.scale_value(3)}px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['border_focus']};
        }}
        """
    
    @classmethod
    def get_glassmorphism_style(cls) -> str:
        """Get glassmorphism effect styling"""
        colors = cls.get_colors()
        return f"""
            background: {colors['glassmorphism']};
            border: 1px solid {colors['border_light']};
            border-radius: {cls.get_border_radius('lg')};
        """
    
    @classmethod
    def toggle_theme(cls):
        """Toggle between dark and light themes"""
        cls._current_theme = 'light' if cls._current_theme == 'dark' else 'dark'
        logging.info(f"Theme toggled to: {cls._current_theme}")
        return cls._current_theme
    
    # Enhanced Typography System
    FONTS = {
        'primary': "'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'text': "'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'mono': "'SF Mono', 'JetBrains Mono', 'Fira Code', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace",
        'ui': "'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'display': "'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    }
    
    # Font weights for better hierarchy
    FONT_WEIGHTS = {
        'light': '300',
        'regular': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700'
    }
    
    # Enhanced Transitions and Animations with micro-interactions
    TRANSITIONS = {
        'instant': '50ms cubic-bezier(0.4, 0.0, 0.2, 1)',
        'fast': '150ms cubic-bezier(0.4, 0.0, 0.2, 1)',
        'normal': '200ms cubic-bezier(0.4, 0.0, 0.2, 1)',
        'slow': '300ms cubic-bezier(0.4, 0.0, 0.2, 1)',
        'spring': '300ms cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'bounce': '400ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'smooth': '250ms cubic-bezier(0.23, 1, 0.32, 1)'
    }
    
    # Dynamic sizing methods replace static dictionaries
    @classmethod
    def get_border_radius(cls, size_key: str) -> str:
        """Get DPI-scaled border radius"""
        base_radius = {'sm': 3, 'md': 4, 'lg': 6, 'xl': 8, 'full': 50}
        if size_key == 'full':
            return '50%'
        scaled = cls.scale_value(base_radius.get(size_key, 4))
        return f"{scaled}px"
    
    # Enhanced Shadow System
    @classmethod
    def get_shadows(cls) -> dict:
        """Get modern floating panel shadows with depth"""
        if cls._current_theme == 'dark':
            return {
                'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.4)',
                'md': '0 4px 12px -2px rgba(0, 0, 0, 0.5), 0 2px 6px -1px rgba(0, 0, 0, 0.3)',
                'lg': '0 12px 24px -4px rgba(0, 0, 0, 0.6), 0 4px 12px -2px rgba(0, 0, 0, 0.4)',
                'xl': '0 24px 48px -8px rgba(0, 0, 0, 0.7), 0 8px 24px -4px rgba(0, 0, 0, 0.5)',
                'floating': '0 8px 32px -4px rgba(0, 0, 0, 0.6), 0 4px 16px -2px rgba(0, 0, 0, 0.4)',
                'card': '0 2px 8px -1px rgba(0, 0, 0, 0.4), 0 1px 4px -1px rgba(0, 0, 0, 0.2)',
                'inner': 'inset 0 2px 6px 0 rgba(0, 0, 0, 0.3)',
                'glow': '0 0 24px rgba(59, 130, 246, 0.35)',
                'glow_soft': '0 0 16px rgba(59, 130, 246, 0.2)'
            }
        else:
            return {
                'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.08)',
                'md': '0 4px 12px -2px rgba(0, 0, 0, 0.12), 0 2px 6px -1px rgba(0, 0, 0, 0.08)',
                'lg': '0 12px 24px -4px rgba(0, 0, 0, 0.15), 0 4px 12px -2px rgba(0, 0, 0, 0.1)',
                'xl': '0 24px 48px -8px rgba(0, 0, 0, 0.18), 0 8px 24px -4px rgba(0, 0, 0, 0.12)',
                'floating': '0 8px 32px -4px rgba(0, 0, 0, 0.12), 0 4px 16px -2px rgba(0, 0, 0, 0.08)',
                'card': '0 2px 8px -1px rgba(0, 0, 0, 0.1), 0 1px 4px -1px rgba(0, 0, 0, 0.06)',
                'inner': 'inset 0 2px 6px 0 rgba(0, 0, 0, 0.05)',
                'glow': '0 0 24px rgba(29, 78, 216, 0.25)',
                'glow_soft': '0 0 16px rgba(29, 78, 216, 0.15)'
            }
    
    # Legacy SHADOWS property for backwards compatibility
    @classmethod
    def SHADOWS(cls):
        return cls.get_shadows()
    
    @classmethod
    def get_main_window_style(cls) -> str:
        """Modern minimalistic main window styling with clean backgrounds"""
        colors = cls.get_colors()
        return f"""
        QMainWindow {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            font-family: {cls.FONTS['ui']};
            font-size: {cls.get_font_size('base')};
            line-height: 1.6;
        }}
        
        QMainWindow::separator {{
            background-color: {colors['border']};
            width: {cls.scale_value(1)}px;
            height: {cls.scale_value(1)}px;
        }}
        
        QStatusBar {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_secondary']};
            border-top: {cls.scale_value(1)}px solid {colors['border']};
            padding: {cls.get_spacing('md')} {cls.get_spacing('lg')};
            font-size: {cls.get_font_size('sm')};
            font-weight: 400;
        }}
        
        QStatusBar::item {{
            border: none;
            margin: 0 {cls.get_spacing('sm')};
        }}
        """
    
    @classmethod
    def get_splitter_style(cls) -> str:
        """Splitter styling"""
        colors = cls.get_colors()
        return f"""
        QSplitter::handle {{
            background-color: {colors['border']};
            border: none;
        }}
        
        QSplitter::handle:horizontal {{
            width: {cls.scale_value(1)}px;
            margin: 0px;
        }}
        
        QSplitter::handle:vertical {{
            height: {cls.scale_value(1)}px;
            margin: 0px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['primary']};
        }}
        """
    
    @classmethod
    def get_group_box_style(cls) -> str:
        """Modern floating panel group box styling"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        return f"""
        QGroupBox {{
            font-weight: 500;
            font-size: {cls.get_font_size('lg')};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('lg')};
            margin-top: {cls.get_spacing('lg')};
            padding-top: {cls.get_spacing('xl')};
            background-color: {colors['bg_card']};
        }}
        
        QGroupBox:hover {{
            border-color: {colors['border_focus']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {cls.get_spacing('lg')};
            padding: {cls.get_spacing('sm')} {cls.get_spacing('md')};
            color: {colors['text_accent']};
            background-color: {colors['bg_primary']};
            border-radius: {cls.get_border_radius('md')};
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        """
    
    @classmethod
    def get_button_style(cls) -> str:
        """Enhanced modern button styling with micro-interactions and touch optimization"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        # Mobile-optimized button height (minimum 44px for touch targets)
        min_height = cls.scale_value(44)
        
        return f"""
        QPushButton {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('lg')};
            padding: {cls.get_spacing('lg')} {cls.get_spacing('xl')};
            font-size: {cls.get_font_size('base')};
            font-weight: {cls.FONT_WEIGHTS['medium']};
            min-height: {min_height}px;
            min-width: {cls.scale_value(120)}px;
            font-family: {cls.FONTS['ui']};
            letter-spacing: 0.3px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['bg_hover']};
            border-color: {colors['border_focus']};
            color: {colors['text_primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['bg_hover']};
        }}
        
        QPushButton:focus {{
            outline: 2px solid {colors['border_focus']};
            outline-offset: 2px;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_disabled']};
            border-color: {colors['border']};
        }}
        
        /* Primary button variant - enhanced with gradient */
        QPushButton[variant="primary"] {{
            background: {colors.get('primary_gradient', colors['primary'])};
            color: {colors['text_inverse']};
            border-color: {colors['primary']};
            font-weight: {cls.FONT_WEIGHTS['semibold']};
        }}
        
        QPushButton[variant="primary"]:hover {{
            background-color: {colors['primary_hover']};
            border-color: {colors['primary_hover']};
        }}
        
        QPushButton[variant="primary"]:pressed {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton[variant="primary"]:disabled {{
            background: {colors['bg_secondary']};
            color: {colors['text_disabled']};
        }}
        
        /* Secondary button variant - refined */
        QPushButton[variant="secondary"] {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border_light']};
            font-weight: {cls.FONT_WEIGHTS['medium']};
        }}
        
        QPushButton[variant="secondary"]:hover {{
            background-color: {colors['bg_hover']};
            border-color: {colors['border_focus']};
        }}
        
        /* Success button variant - enhanced */
        QPushButton[variant="success"] {{
            background-color: {colors['success']};
            color: {colors['text_inverse']};
            border-color: {colors['success']};
            font-weight: {cls.FONT_WEIGHTS['semibold']};
        }}
        
        QPushButton[variant="success"]:hover {{
            background-color: {colors['success']};
            opacity: 0.9;
        }}
        
        /* Danger button variant - enhanced */
        QPushButton[variant="danger"] {{
            background-color: {colors['error']};
            color: {colors['text_inverse']};
            border-color: {colors['error']};
            font-weight: {cls.FONT_WEIGHTS['semibold']};
        }}
        
        QPushButton[variant="danger"]:hover {{
            background-color: {colors['accent_soft']};
            border-color: {colors['accent_soft']};
        }}
        
        /* Ghost button variant - minimalistic */
        QPushButton[variant="ghost"] {{
            background-color: transparent;
            color: {colors['text_accent']};
            border: {cls.scale_value(1)}px solid transparent;
        }}
        
        QPushButton[variant="ghost"]:hover {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
        }}
        
        /* Icon button variant - compact */
        QPushButton[variant="icon"] {{
            min-width: {min_height}px;
            max-width: {min_height}px;
            padding: {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('md')};
        }}
        """
    
    @classmethod
    def get_input_style(cls) -> str:
        """Modern mobile-friendly input field styling"""
        colors = cls.get_colors()
        # Mobile-optimized input height (minimum 44px for touch targets)
        min_height = cls.scale_value(44)
        return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {colors['bg_input']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border_input']};
            border-radius: {cls.get_border_radius('lg')};
            padding: {cls.get_spacing('md')} {cls.get_spacing('lg')};
            font-size: {cls.get_font_size('base')};
            font-family: {cls.FONTS['ui']};
            selection-background-color: {colors['primary']};
            selection-color: #FFFFFF;
            min-height: {min_height}px;
            line-height: 1.5;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {colors['border_focus']};
            background-color: {colors['bg_input']};
            outline: none;
        }}
        
        QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
            border-color: {colors['border_focus']};
            background-color: {colors['bg_input']};
        }}
        
        QLineEdit::placeholder, QTextEdit::placeholder {{
            color: {colors['text_muted']};
            font-style: italic;
        }}
        
        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
            width: {cls.scale_value(20)}px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: {cls.scale_value(4)}px solid transparent;
            border-right: {cls.scale_value(4)}px solid transparent;
            border-top: {cls.scale_value(4)}px solid {colors['text_muted']};
            margin-right: {cls.get_spacing('sm')};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('md')};
            padding: {cls.get_spacing('xs')};
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: {cls.get_spacing('sm')} {cls.get_spacing('md')};
            border-radius: {cls.get_border_radius('sm')};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        """
    
    @classmethod
    def get_checkbox_style(cls) -> str:
        """Modern mobile-friendly checkbox styling"""
        colors = cls.get_colors()
        # Mobile-optimized checkbox size (minimum 20px for touch targets)
        indicator_size = cls.scale_value(20)
        return f"""
        QCheckBox {{
            color: {colors['text_primary']};
            font-size: {cls.get_font_size('base')};
            spacing: {cls.get_spacing('md')};
            padding: {cls.get_spacing('xs')};
        }}
        
        QCheckBox::indicator {{
            width: {indicator_size}px;
            height: {indicator_size}px;
            border: {cls.scale_value(2)}px solid {colors['border_input']};
            border-radius: {cls.get_border_radius('sm')};
            background-color: {colors['bg_input']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['border_focus']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {colors['primary_hover']};
            border-color: {colors['primary_hover']};
        }}
        
        QCheckBox::indicator:disabled {{
            background-color: {colors['bg_secondary']};
            border-color: {colors['border']};
        }}
        """
    
    @classmethod
    def get_tab_style(cls) -> str:
        """Modern tab widget styling with enhanced visual indicators"""
        colors = cls.get_colors()
        shadows = cls.get_shadows()
        return f"""
        QTabWidget::pane {{
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('lg')};
            background-color: {colors['bg_card']};
            padding: {cls.get_spacing('md')};
        }}
        
        QTabBar {{
            background-color: transparent;
            border: none;
        }}
        
        QTabBar::tab {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_secondary']};
            padding: {cls.get_spacing('md')} {cls.get_spacing('xl')};
            margin-right: {cls.scale_value(4)}px;
            margin-bottom: {cls.scale_value(2)}px;
            border-radius: {cls.get_border_radius('lg')};
            font-size: {cls.get_font_size('base')};
            font-weight: 500;
            min-width: {cls.scale_value(100)}px;
            min-height: {cls.scale_value(44)}px;
            border: {cls.scale_value(1)}px solid {colors['border']};
            position: relative;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: {colors['text_primary']};
            border-color: {colors['primary']};
            font-weight: 600;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['bg_hover']};
            color: {colors['text_primary']};
            border-color: {colors['border_focus']};
        }}
        
        QTabBar::tab:first {{
            margin-left: 0;
        }}
        
        QTabBar::tab:pressed {{
        }}
        """
    
    @classmethod
    def get_progress_bar_style(cls) -> str:
        """Modern progress bar styling"""
        colors = cls.get_colors()
        height = cls.scale_value(20)
        return f"""
        QProgressBar {{
            background-color: {colors['bg_input']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('md')};
            text-align: center;
            color: {colors['text_primary']};
            font-size: {cls.get_font_size('sm')};
            font-weight: 500;
            height: {height}px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: {cls.get_border_radius('sm')};
            margin: {cls.scale_value(1)}px;
        }}
        """
    
    @classmethod
    def get_slider_style(cls) -> str:
        """Modern mobile-friendly slider styling"""
        colors = cls.get_colors()
        groove_height = cls.scale_value(4)
        handle_size = cls.scale_value(20)  # Larger for touch
        handle_margin = cls.scale_value(-8)
        return f"""
        QSlider::groove:horizontal {{
            background-color: {colors['bg_input']};
            height: {groove_height}px;
            border-radius: {groove_height//2}px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors['primary']};
            border: {cls.scale_value(2)}px solid {colors['primary']};
            width: {handle_size}px;
            height: {handle_size}px;
            border-radius: {handle_size//2}px;
            margin: {handle_margin}px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors['primary_hover']};
            border-color: {colors['primary_hover']};
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {colors['primary']};
            border-radius: {groove_height//2}px;
        }}
        """
    
    @classmethod
    def get_enhanced_spinbox_style(cls) -> str:
        """Enhanced SpinBox styling with better touch targets and accessibility"""
        colors = cls.get_colors()
        button_width = cls.scale_value(24)  # Increased from 18 for better touch
        arrow_size = cls.scale_value(4)     # Increased from 3 for better visibility
        min_height = cls.scale_value(36)    # Increased minimum height for touch accessibility
        return f"""
        QSpinBox {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('md')};
            padding: {cls.get_spacing('sm')} {cls.get_spacing('lg')};
            font-size: {cls.get_font_size('base')};
            min-height: {min_height}px;
            font-weight: 500;
        }}
        
        QSpinBox:focus {{
            border-color: {colors['border_focus']};
            background-color: {colors['bg_secondary']};
        }}
        
        QSpinBox:hover {{
            border-color: {colors['border_light']};
            background-color: {colors['bg_secondary']};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {colors['bg_tertiary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            width: {button_width}px;
            border-radius: {cls.get_border_radius('sm')};
            margin: {cls.scale_value(2)}px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
            background-color: {colors['primary_dark']};
            border-color: {colors['primary_dark']};
        }}
        
        QSpinBox::up-arrow {{
            image: none;
            border-left: {arrow_size}px solid transparent;
            border-right: {arrow_size}px solid transparent;
            border-bottom: {arrow_size}px solid {colors['text_muted']};
        }}
        
        QSpinBox::down-arrow {{
            image: none;
            border-left: {arrow_size}px solid transparent;
            border-right: {arrow_size}px solid transparent;
            border-top: {arrow_size}px solid {colors['text_muted']};
        }}
        
        QSpinBox::up-button:hover QSpinBox::up-arrow {{
            border-bottom-color: {colors['text_primary']};
        }}
        
        QSpinBox::down-button:hover QSpinBox::down-arrow {{
            border-top-color: {colors['text_primary']};
        }}
        """
    
    @classmethod
    def get_enhanced_text_edit_style(cls) -> str:
        """Enhanced QTextEdit styling with better focus states and validation"""
        colors = cls.get_colors()
        min_height = cls.scale_value(120)
        return f"""
        QTextEdit {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('lg')};
            padding: {cls.get_spacing('md')};
            font-size: {cls.get_font_size('base')};
            min-height: {min_height}px;
            line-height: 1.4;
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_primary']};
        }}
        
        QTextEdit:focus {{
            border-color: {colors['border_focus']};
            background-color: {colors['bg_secondary']};
        }}
        
        QTextEdit:hover {{
            border-color: {colors['border_light']};
        }}
        
        QTextEdit[role="input"] {{
            font-family: system-ui, -apple-system, sans-serif;
        }}
        
        QTextEdit[validation="error"] {{
            border-color: {colors['error']};
            background-color: {colors['error_bg']};
        }}
        
        QTextEdit[validation="success"] {{
            border-color: {colors['success']};
        }}
        """
    
    @classmethod
    def get_enhanced_combo_box_style(cls) -> str:
        """Enhanced QComboBox styling with better accessibility"""
        colors = cls.get_colors()
        min_height = cls.scale_value(36)
        arrow_size = cls.scale_value(6)
        return f"""
        QComboBox {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('md')};
            padding: {cls.get_spacing('sm')} {cls.get_spacing('lg')};
            font-size: {cls.get_font_size('base')};
            min-height: {min_height}px;
            font-weight: 500;
        }}
        
        QComboBox:focus {{
            border-color: {colors['border_focus']};
            background-color: {colors['bg_secondary']};
        }}
        
        QComboBox:hover {{
            border-color: {colors['border_light']};
            background-color: {colors['bg_secondary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: {cls.scale_value(30)}px;
            border-top-right-radius: {cls.get_border_radius('md')};
            border-bottom-right-radius: {cls.get_border_radius('md')};
            background-color: {colors['bg_tertiary']};
        }}
        
        QComboBox::drop-down:hover {{
            background-color: {colors['primary']};
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: {arrow_size}px solid transparent;
            border-right: {arrow_size}px solid transparent;
            border-top: {arrow_size}px solid {colors['text_muted']};
        }}
        
        QComboBox::down-arrow:hover {{
            border-top-color: {colors['text_primary']};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('md')};
            padding: {cls.get_spacing('xs')};
            selection-background-color: {colors['primary']};
            selection-color: {colors['text_primary']};
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: {cls.get_spacing('sm')} {cls.get_spacing('md')};
            border-radius: {cls.get_border_radius('sm')};
            min-height: {cls.scale_value(28)}px;
        }}
        
        QComboBox QAbstractItemView::item:hover {{
            background-color: {colors['bg_hover']};
        }}
        """
    
    @classmethod
    def get_enhanced_checkbox_style(cls) -> str:
        """Enhanced checkbox styling with better accessibility"""
        colors = cls.get_colors()
        indicator_size = cls.scale_value(18)  # Increased from 14 for better touch
        return f"""
        QCheckBox {{
            color: {colors['text_primary']};
            font-size: {cls.get_font_size('base')};
            spacing: {cls.get_spacing('md')};
            font-weight: 500;
            padding: {cls.get_spacing('xs')} 0;
        }}
        
        QCheckBox:focus {{
            outline: {cls.scale_value(2)}px solid {colors['primary']};
            outline-offset: {cls.scale_value(2)}px;
        }}
        
        QCheckBox::indicator {{
            width: {indicator_size}px;
            height: {indicator_size}px;
            border: {cls.scale_value(2)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('sm')};
            background-color: {colors['bg_primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['primary']};
            background-color: {colors['bg_secondary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
            image: none;
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: {colors['primary_hover']};
            border-color: {colors['primary_hover']};
        }}
        
        QCheckBox::indicator:checked {{
            background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04LjUgMUwzLjUgNkwxLjUgNCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            background-repeat: no-repeat;
            background-position: center;
        }}
        """
    
    @classmethod
    def get_validation_feedback_style(cls) -> str:
        """Styling for validation feedback messages"""
        colors = cls.get_colors()
        return f"""
        QLabel[role="validation-error"] {{
            color: {colors['error']};
            font-size: {cls.get_font_size('sm')};
            font-weight: 500;
            padding: {cls.get_spacing('xs')} {cls.get_spacing('md')};
            background-color: {colors['error_bg']};
            border: {cls.scale_value(1)}px solid {colors['error']};
            border-radius: {cls.get_border_radius('md')};
            margin-top: {cls.get_spacing('xs')};
        }}
        
        QLabel[role="validation-success"] {{
            color: {colors['success']};
            font-size: {cls.get_font_size('sm')};
            font-weight: 500;
            padding: {cls.get_spacing('xs')} {cls.get_spacing('md')};
            background-color: {colors['success_bg']};
            border: {cls.scale_value(1)}px solid {colors['success']};
            border-radius: {cls.get_border_radius('md')};
            margin-top: {cls.get_spacing('xs')};
        }}
        
        QLabel[role="validation-info"] {{
            color: {colors['info']};
            font-size: {cls.get_font_size('sm')};
            font-weight: 500;
            padding: {cls.get_spacing('xs')} {cls.get_spacing('md')};
            background-color: {colors['info_bg']};
            border: {cls.scale_value(1)}px solid {colors['info']};
            border-radius: {cls.get_border_radius('md')};
            margin-top: {cls.get_spacing('xs')};
        }}
        """
    
    @classmethod
    def get_text_browser_style(cls) -> str:
        """Text browser styling"""
        colors = cls.get_colors()
        return f"""
        QTextBrowser {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            border: {cls.scale_value(1)}px solid {colors['border']};
            border-radius: {cls.get_border_radius('lg')};
            padding: {cls.get_spacing('lg')};
            font-family: {cls.FONTS['mono']};
            font-size: {cls.get_font_size('sm')};
            line-height: 1.5;
            selection-background-color: {colors['primary']};
        }}
        
        QTextBrowser a {{
            color: {colors['primary_light']};
            text-decoration: none;
        }}
        
        QTextBrowser a:hover {{
            color: {colors['primary']};
            text-decoration: underline;
        }}
        """
    
    @classmethod
    def get_label_style(cls) -> str:
        """Label styling"""
        colors = cls.get_colors()
        return f"""
        QLabel {{
            color: {colors['text_primary']};
            font-size: {cls.get_font_size('sm')};
        }}
        
        QLabel[role="heading"] {{
            font-size: {cls.get_font_size('lg')};
            font-weight: 600;
            color: {colors['text_primary']};
        }}
        
        QLabel[role="caption"] {{
            color: {colors['text_muted']};
            font-size: {cls.get_font_size('xs')};
        }}
        
        QLabel[role="error"] {{
            color: {colors['error']};
            font-weight: 500;
        }}
        
        QLabel[role="success"] {{
            color: {colors['success']};
            font-weight: 500;
        }}
        
        QLabel[role="warning"] {{
            color: {colors['warning']};
            font-weight: 500;
        }}
        
        QLabel[role="status-ready"] {{
            color: {colors['text_muted']};
            font-weight: 500;
            background-color: {colors['bg_secondary']};
            padding: {cls.get_spacing('xs')} {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('sm')};
        }}
        
        QLabel[role="status-active"] {{
            color: {colors['info']};
            font-weight: 500;
            background-color: {colors['bg_secondary']};
            padding: {cls.get_spacing('xs')} {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('sm')};
        }}
        
        QLabel[role="status-success"] {{
            color: {colors['success']};
            font-weight: 500;
            background-color: {colors['bg_secondary']};
            padding: {cls.get_spacing('xs')} {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('sm')};
        }}
        
        QLabel[role="status-error"] {{
            color: {colors['error']};
            font-weight: 500;
            background-color: {colors['bg_secondary']};
            padding: {cls.get_spacing('xs')} {cls.get_spacing('sm')};
            border-radius: {cls.get_border_radius('sm')};
        }}
        """

    @classmethod
    def create_clean_settings_section(cls, title: str, parent=None) -> QWidget:
        """Creates a clean settings section with title label + content container structure"""
        colors = cls.get_colors()
        section = QWidget(parent)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(cls.scale_value(8))
        
        # Title label
        title_label = QLabel(title)
        title_label.setFont(QFont("SF Pro Text", int(cls.get_font_size('lg').replace('pt', ''))))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_primary']};
                font-weight: 600;
                margin-bottom: {cls.get_spacing('sm')};
            }}
        """)
        
        # Content container
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {colors['bg_card']};
                border-radius: {cls.scale_value(8)}px;
                padding: {cls.get_spacing('md')};
            }}
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(content_widget)
        
        return section

    @classmethod
    def create_compact_checkbox(cls, text: str, tooltip: str = None) -> QCheckBox:
        """Custom styling with hover states and proper sizing"""
        colors = cls.get_colors()
        checkbox = QCheckBox(text)
        if tooltip:
            checkbox.setToolTip(tooltip)
        
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {colors['text_secondary']};
                font-size: {cls.get_font_size('base')};
                spacing: {cls.scale_value(8)}px;
                padding: {cls.get_spacing('xs')};
            }}
            QCheckBox:hover {{
                color: {colors['text_primary']};
                background-color: {colors['bg_hover']};
                border-radius: {cls.scale_value(4)}px;
            }}
            QCheckBox::indicator {{
                width: {cls.scale_value(16)}px;
                height: {cls.scale_value(16)}px;
                border: 2px solid {colors['border_input']};
                border-radius: {cls.scale_value(3)}px;
                background-color: {colors['bg_input']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['primary']};
                border-color: {colors['primary']};
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {colors['primary_hover']};
            }}
        """)
        return checkbox

    @classmethod
    def create_time_interval_control(cls) -> dict:
        """Modern spinbox styling with custom arrows"""
        colors = cls.get_colors()
        spinbox = QSpinBox()
        spinbox.setRange(1, 3600)
        spinbox.setValue(30)
        spinbox.setSuffix(" sec")
        
        spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {colors['bg_input']};
                border: 2px solid {colors['border_input']};
                border-radius: {cls.scale_value(6)}px;
                padding: {cls.get_spacing('sm')};
                font-size: {cls.get_font_size('base')};
                color: {colors['text_primary']};
                min-width: {cls.scale_value(100)}px;
            }}
            QSpinBox:focus {{
                border-color: {colors['primary']};
                background-color: {colors['bg_secondary']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {colors['bg_panel']};
                border: 1px solid {colors['border_input']};
                width: {cls.scale_value(18)}px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {colors['primary']};
            }}
        """)
        
        # Container with label
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(cls.scale_value(8))
        
        label = QLabel("Interval:")
        label.setStyleSheet(f"color: {colors['text_secondary']}; font-size: {cls.get_font_size('base')};")
        
        layout.addWidget(label)
        layout.addWidget(spinbox)
        layout.addStretch()
        
        return {"widget": container, "spinbox": spinbox}

# Task types
TASK_TYPES = ["code", "multimedia", "rag", "automation", "analytics"]

# Setup logging
def setup_logging():
    log_dir = Path.home() / "SuperMini_Output" / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Could not create log directory: {e}")
        sys.exit(1)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "supermini.log"),
            logging.StreamHandler()
        ]
    )

setup_logging()
logging.info("Starting SuperMini application")

# Neural Network Visualization Components
class NeuralMetricsWidget(QWidget):
    """Live system metrics widget with neural-zen aesthetics"""
    
    def __init__(self):
        super().__init__()
        self.cpu_data = []
        self.memory_data = []
        self.ai_activity = 0.0
        self.max_data_points = 50
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Update every second
        
        self.setMinimumHeight(ModernTheme.scale_value(120))
        self.setMaximumHeight(ModernTheme.scale_value(180))
        
    def update_metrics(self):
        """Update metrics and trigger repaint"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            self.cpu_data.append(cpu_percent)
            self.memory_data.append(memory_percent)
            
            # Keep only recent data points
            if len(self.cpu_data) > self.max_data_points:
                self.cpu_data.pop(0)
            if len(self.memory_data) > self.max_data_points:
                self.memory_data.pop(0)
                
            self.update()
        except Exception as e:
            logging.error(f"Error updating metrics: {e}")
    
    def paintEvent(self, event):
        """Custom paint event for neural-zen metrics visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Background gradient
        gradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        gradient.setColorAt(0, QColor(ModernTheme.get_colors()['bg_card']))
        gradient.setColorAt(1, QColor(ModernTheme.get_colors()['bg_panel']))
        painter.fillRect(rect, QBrush(gradient))
        
        # Draw metrics if we have data
        if len(self.cpu_data) > 1:
            self.draw_metric_line(painter, self.cpu_data, 
                                QColor(ModernTheme.get_colors()['primary']), 
                                "CPU", rect.adjusted(10, 10, -10, -40))
        
        if len(self.memory_data) > 1:
            self.draw_metric_line(painter, self.memory_data,
                                QColor(ModernTheme.get_colors()['secondary']),
                                "Memory", rect.adjusted(10, 40, -10, -10))
        
        # Properly end the painter
        painter.end()
    
    def draw_metric_line(self, painter, data, color, label, rect):
        """Draw a single metric line with neural glow effect"""
        if len(data) < 2:
            return
            
        # Setup pen with glow effect
        pen = QPen(color, 2)
        painter.setPen(pen)
        
        # Calculate points
        width = rect.width()
        height = rect.height()
        step_x = width / (self.max_data_points - 1)
        
        # Draw the line
        for i in range(len(data) - 1):
            x1 = int(rect.x() + i * step_x)
            y1 = int(rect.bottom() - (data[i] / 100.0) * height)
            x2 = int(rect.x() + (i + 1) * step_x)
            y2 = int(rect.bottom() - (data[i + 1] / 100.0) * height)
            
            painter.drawLine(x1, y1, x2, y2)
        
        # Draw label
        painter.setPen(QPen(QColor(ModernTheme.get_colors()['text_zen']), 1))
        current_value = data[-1] if data else 0
        painter.drawText(rect.x() + 5, rect.y() + 15, f"{label}: {current_value:.1f}%")


class NeuralNetworkWidget(QWidget):
    """Neural network visualization widget showing AI processing state"""
    
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.connections = []
        self.activity_level = 0.0
        self.setup_network()
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(100)  # 10 FPS
        
        self.setMinimumHeight(ModernTheme.scale_value(100))
        self.setMaximumHeight(ModernTheme.scale_value(150))
    
    def setup_network(self):
        """Setup neural network topology"""
        # Simple 4-layer network visualization
        layers = [3, 4, 4, 2]  # Input, Hidden1, Hidden2, Output
        layer_spacing = 80
        node_spacing = 25
        
        self.nodes = []
        for layer_idx, layer_size in enumerate(layers):
            layer_nodes = []
            for node_idx in range(layer_size):
                x = 50 + layer_idx * layer_spacing
                y = 30 + node_idx * node_spacing
                layer_nodes.append({'x': x, 'y': y, 'activity': 0.0})
            self.nodes.append(layer_nodes)
    
    def set_activity_level(self, level):
        """Set the neural activity level (0.0 - 1.0)"""
        self.activity_level = max(0.0, min(1.0, level))
    
    def animate(self):
        """Animate neural activity"""
        import random
        
        # Simulate neural activity propagation
        for layer in self.nodes:
            for node in layer:
                # Random activity with some persistence
                node['activity'] = max(0.0, node['activity'] * 0.9 + random.random() * 0.3 * self.activity_level)
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the neural network visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Background
        painter.fillRect(rect, QColor(ModernTheme.get_colors()['bg_zen']))
        
        # Draw connections first
        self.draw_connections(painter)
        
        # Draw nodes
        self.draw_nodes(painter)
        
        # Draw title
        painter.setPen(QPen(QColor(ModernTheme.get_colors()['text_neural']), 1))
        painter.drawText(10, 20, "🧠 Neural Processing")
        
        # Properly end the painter
        painter.end()
    
    def draw_connections(self, painter):
        """Draw neural connections with activity-based opacity"""
        for layer_idx in range(len(self.nodes) - 1):
            current_layer = self.nodes[layer_idx]
            next_layer = self.nodes[layer_idx + 1]
            
            for node1 in current_layer:
                for node2 in next_layer:
                    # Connection opacity based on average activity
                    avg_activity = (node1['activity'] + node2['activity']) / 2
                    alpha = int(50 + avg_activity * 150)
                    
                    color = QColor(ModernTheme.get_colors()['border_neural'])
                    color.setAlpha(alpha)
                    
                    pen = QPen(color, 1)
                    painter.setPen(pen)
                    painter.drawLine(node1['x'], node1['y'], node2['x'], node2['y'])
    
    def draw_nodes(self, painter):
        """Draw neural nodes with activity-based glow"""
        for layer in self.nodes:
            for node in layer:
                # Node color intensity based on activity
                intensity = int(node['activity'] * 255)
                
                if node['activity'] > 0.1:
                    # Active node - neural green
                    color = QColor(ModernTheme.get_colors()['primary'])
                    color.setAlpha(intensity)
                else:
                    # Inactive node - subtle gray
                    color = QColor(ModernTheme.get_colors()['border_zen'])
                
                # Draw node with glow effect
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(color, 1))
                
                node_size = 4 + int(node['activity'] * 4)
                painter.drawEllipse(node['x'] - node_size//2, node['y'] - node_size//2, 
                                  node_size, node_size)


@dataclass
class FileMetadata:
    """Metadata for generated files"""
    file_path: str
    display_name: str
    description: str
    file_type: str
    purpose: str
    created_timestamp: float
    file_size: int = 0
    
@dataclass
class TaskResult:
    """Data class for task results"""
    success: bool
    result: str
    generated_files: List[str]
    task_steps: List[str]
    audio_path: Optional[str] = None
    score: float = 0.0
    execution_time: float = 0.0
    file_metadata: Dict[str, FileMetadata] = None  # Maps file path to metadata
    
    def __post_init__(self):
        if self.file_metadata is None:
            self.file_metadata = {}

@dataclass
class AIConfig:
    """Configuration for AI models"""
    primary_model: str = "Claude API (Recommended)"  # New primary model selection
    use_claude: bool = True
    claude_api_key: str = ""
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:7b"
    max_tokens: int = 4096
    temperature: float = 0.7

class SafeRequests:
    """Safe wrapper for requests with proper error handling"""
    @staticmethod
    def post(url: str, **kwargs) -> Optional[requests.Response]:
        try:
            return requests.post(url, timeout=30, **kwargs)
        except requests.RequestException as e:
            logging.error(f"POST request to {url} failed: {e}")
            return None
    
    @staticmethod
    def get(url: str, **kwargs) -> Optional[requests.Response]:
        try:
            return requests.get(url, timeout=10, **kwargs)
        except requests.RequestException as e:
            logging.error(f"GET request to {url} failed: {e}")
            return None

class MemoryManager:
    """Manages the ChromaDB memory system"""
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.memory_dir = data_dir / "memory"
        self.collection = None
        self.setup_memory()
    
    def setup_memory(self):
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            if not chromadb:
                logging.warning("ChromaDB not available - memory features disabled")
                return
            client = chromadb.PersistentClient(path=str(self.memory_dir))
            self.collection = client.get_or_create_collection("task_memory")
            logging.info("Memory system initialized")
        except Exception as e:
            logging.error(f"Memory setup failed: {e}")
            self.collection = None
    
    def save_task(self, task_data: Dict[str, Any]) -> bool:
        if not self.collection:
            return False
        try:
            task_id = f"task_{int(time.time() * 1000000)}"
            task_text = f"Prompt: {task_data.get('prompt', '')}\nType: {task_data.get('task_type', '')}\nResult: {task_data.get('result', '')}"
            self.collection.add(
                documents=[task_text],
                metadatas=[task_data],
                ids=[task_id]
            )
            logging.info(f"Saved task to memory: {task_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to save task to memory: {e}")
            return False
    
    def retrieve_context(self, prompt: str, task_type: str, n_results: int = 3) -> str:
        if not self.collection:
            return ""
        try:
            query_text = f"Prompt: {prompt}\nType: {task_type}"
            results = self.collection.query(query_texts=[query_text], n_results=n_results)
            if not results["documents"]:
                return ""
            context_parts = []
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                context_parts.append(f"Previous: {meta.get('prompt', '')}\nResult: {meta.get('result', '')}")
            return "\n\n".join(context_parts)
        except Exception as e:
            logging.error(f"Memory retrieval failed: {e}")
            return ""
    
    def store_enhancement_success(self, opportunity, solution: str, assessment: dict, execution_result: dict):
        """Store successful enhancement for future learning"""
        if not self.collection:
            return False
        
        try:
            enhancement_id = f"enhancement_{int(time.time() * 1000000)}"
            enhancement_text = f"""Enhancement Success:
Type: {opportunity.opportunity_type}
Description: {opportunity.description}
Impact: {opportunity.impact_score}
Complexity: {opportunity.complexity_score}
Quality Score: {assessment.get('quality_score', 0)}
Solution: {solution[:500]}"""
            
            metadata = {
                'type': 'enhancement_success',
                'opportunity_type': opportunity.opportunity_type,
                'description': opportunity.description,
                'impact_score': opportunity.impact_score,
                'complexity_score': opportunity.complexity_score,
                'quality_score': assessment.get('quality_score', 0),
                'viability_score': assessment.get('viability_score', 0),
                'recommendation': assessment.get('recommendation', ''),
                'files_created': len(execution_result.get('files_created', [])),
                'timestamp': datetime.now().isoformat()
            }
            
            self.collection.add(
                documents=[enhancement_text],
                metadatas=[metadata],
                ids=[enhancement_id]
            )
            
            logging.info(f"Stored enhancement success: {enhancement_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to store enhancement success: {e}")
            return False
    
    def retrieve_enhancement_patterns(self, opportunity_type: str = None, n_results: int = 5) -> List[dict]:
        """Retrieve successful enhancement patterns for learning"""
        if not self.collection:
            return []
        
        try:
            if opportunity_type:
                query_text = f"Enhancement Success: Type: {opportunity_type}"
            else:
                query_text = "Enhancement Success:"
            
            results = self.collection.query(
                query_texts=[query_text], 
                n_results=n_results,
                where={"type": "enhancement_success"}
            )
            
            patterns = []
            if results["documents"]:
                for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                    patterns.append({
                        'opportunity_type': meta.get('opportunity_type'),
                        'description': meta.get('description'),
                        'impact_score': meta.get('impact_score'),
                        'quality_score': meta.get('quality_score'),
                        'recommendation': meta.get('recommendation'),
                        'timestamp': meta.get('timestamp')
                    })
            
            return patterns
            
        except Exception as e:
            logging.error(f"Failed to retrieve enhancement patterns: {e}")
            return []
    
    def add_memory(self, memory_data: Dict[str, Any]) -> bool:
        """Add arbitrary memory data to the collection"""
        if not self.collection:
            return False
        
        try:
            memory_id = f"memory_{int(time.time() * 1000000)}"
            content = memory_data.get('content', '')
            metadata = memory_data.get('metadata', {})
            
            # Ensure metadata is a valid dict
            if not isinstance(metadata, dict):
                metadata = {'source': 'add_memory', 'timestamp': time.time()}
            
            # Add timestamp if not present
            if 'timestamp' not in metadata:
                metadata['timestamp'] = time.time()
            
            self.collection.add(
                documents=[str(content)],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            logging.info(f"Added memory to collection: {memory_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to add memory: {e}")
            return False

class OllamaManager:
    """Manages Ollama local AI model interactions"""
    def __init__(self, config: AIConfig, monitor: Optional['SystemMonitor'] = None, task_processor: Optional['TaskProcessor'] = None):
        self.config = config
        self.monitor = monitor
        self.task_processor = task_processor
        self.base_url = config.ollama_url
        self.model = config.ollama_model
        self.setup_ollama()
    
    def setup_ollama(self):
        try:
            response = SafeRequests.get(f"{self.base_url}/api/tags")
            if response and response.status_code == 200:
                logging.info("Ollama server is running")
                return True
        except Exception:
            pass
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
            logging.info("Started Ollama server")
            return True
        except Exception as e:
            logging.error(f"Failed to start Ollama: {e}")
            return False
    
    def query(self, prompt: str) -> Optional[str]:
        start_time = time.time()
        try:
            response = SafeRequests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    }
                }
            )
            if response and response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Calculate response time and tokens
                response_time = time.time() - start_time
                input_tokens = len(prompt.split())
                output_tokens = len(response_text.split())
                total_tokens = input_tokens + output_tokens
                
                # Update AI metrics dashboard for Ollama
                if self.task_processor and self.task_processor.metrics_callback:
                    self.task_processor.metrics_callback(
                        task_type="ollama_query",
                        response_time=response_time,
                        tokens_used=total_tokens
                    )
                
                # Update monitoring stats
                if self.monitor:
                    self.monitor.update_stats('total_prompts')
                    self.monitor.update_stats('ollama_prompts')
                    self.monitor.update_stats('total_tokens', total_tokens)
                    
                    # Log AI task metrics for dashboard
                    if hasattr(self.monitor, 'log_ai_task'):
                        self.monitor.log_ai_task(total_tokens, response_time)
                
                return response_text
            return None
        except Exception as e:
            logging.error(f"Ollama query failed: {e}")
            if self.monitor:
                self.monitor.update_stats('errors')
            return None


class ClaudeManager:
    """Manages Claude API interactions with monitoring"""
    def __init__(self, config: AIConfig, monitor: Optional['SystemMonitor'] = None, task_processor: Optional['TaskProcessor'] = None):
        self.config = config
        self.monitor = monitor
        self.task_processor = task_processor
        self.client = None
        if config.use_claude and config.claude_api_key and Anthropic:
            try:
                self.client = Anthropic(api_key=config.claude_api_key)
                logging.info("Claude API initialized")
            except Exception as e:
                logging.error(f"Claude initialization failed: {e}")

    def query(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Query Claude model with monitoring"""
        if not self.client:
            return None
        
        start_time = time.time()
        try:
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                system = system_prompt
            elif (self.task_processor and 
                  hasattr(self.task_processor, 'current_task_prompts') and 
                  self.task_processor.current_task_prompts):
                # Use task-specific optimized prompt
                system = self.task_processor.current_task_prompts.get('system_prompt', system_prompt)
            else:
                system = "You are SuperMini, an AI assistant that helps with various tasks including code generation, data analysis, and multimedia processing."
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system,
                messages=messages
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Calculate tokens used (input + output)
            input_tokens = len(prompt.split()) + len(system.split())
            output_tokens = len(response.content[0].text.split())
            total_tokens = input_tokens + output_tokens
            
            # Update AI metrics dashboard for Claude
            if self.task_processor and self.task_processor.metrics_callback:
                self.task_processor.metrics_callback(
                    task_type="claude_query",
                    response_time=response_time,
                    tokens_used=total_tokens
                )
            
            # Update monitoring stats
            if self.monitor:
                self.monitor.update_stats('total_prompts')
                self.monitor.update_stats('claude_prompts')
                self.monitor.update_stats('total_tokens', total_tokens)
                
                # Log AI task metrics for dashboard
                if hasattr(self.monitor, 'log_ai_task'):
                    self.monitor.log_ai_task(total_tokens, response_time)
            
            return response.content[0].text
        except AnthropicError as e:
            logging.error(f"Claude query failed: {e}")
            if self.monitor:
                self.monitor.update_stats('errors')
            return None
    
    def query_with_image(self, prompt: str, image_path: str) -> Optional[str]:
        if not self.client:
            return None
        
        start_time = time.time()
        try:
            with open(image_path, "rb")  as f:
                image_data = base64.b64encode(f.read()).decode()
            message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=self.config.max_tokens,
                messages=[message]
            )
            
            # Calculate response time and tokens
            response_time = time.time() - start_time
            input_tokens = len(prompt.split()) + 200  # Estimate tokens for image
            output_tokens = len(response.content[0].text.split())
            total_tokens = input_tokens + output_tokens
            
            # Update AI metrics dashboard for Claude Vision
            if self.task_processor and self.task_processor.metrics_callback:
                self.task_processor.metrics_callback(
                    task_type="claude_vision",
                    response_time=response_time,
                    tokens_used=total_tokens
                )
            
            # Update monitoring stats
            if self.monitor:
                self.monitor.update_stats('total_prompts')
                self.monitor.update_stats('claude_prompts')
                self.monitor.update_stats('total_tokens', total_tokens)
                
                # Log AI task metrics for dashboard
                if hasattr(self.monitor, 'log_ai_task'):
                    self.monitor.log_ai_task(total_tokens, response_time)
            
            return response.content[0].text
        except Exception as e:
            logging.error(f"Claude image query failed: {e}")
            return None

class EnhancementOpportunity:
    """Represents a specific enhancement opportunity with metadata"""
    def __init__(self, opportunity_type: str, description: str, impact_score: float, 
                 complexity_score: float, file_path: str = None, line_numbers: list = None):
        self.opportunity_type = opportunity_type  # 'performance', 'feature', 'architecture', 'security', etc.
        self.description = description
        self.impact_score = impact_score  # 0.0 to 1.0
        self.complexity_score = complexity_score  # 0.0 to 1.0
        self.priority_score = impact_score / max(complexity_score, 0.1)  # Higher is better
        self.file_path = file_path
        self.line_numbers = line_numbers or []
        self.timestamp = datetime.now()
        self.status = 'identified'  # 'identified', 'planned', 'in_progress', 'completed', 'failed'
        
    def to_dict(self):
        return {
            'type': self.opportunity_type,
            'description': self.description,
            'impact_score': self.impact_score,
            'complexity_score': self.complexity_score,
            'priority_score': self.priority_score,
            'file_path': self.file_path,
            'line_numbers': self.line_numbers,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }

class EnhancementDiscoveryEngine:
    """Advanced engine for discovering meaningful enhancement opportunities"""
    
    def __init__(self, app_path: str, memory_manager: MemoryManager):
        self.app_path = Path(app_path)
        self.memory = memory_manager
        self.opportunities = []
        
    def discover_opportunities(self) -> List[EnhancementOpportunity]:
        """Comprehensive analysis to discover enhancement opportunities"""
        self.opportunities.clear()
        
        # Analyze code quality and architecture
        self._analyze_code_quality()
        
        # Identify performance optimization opportunities
        self._analyze_performance_opportunities()
        
        # Check for feature gaps and improvements
        self._analyze_feature_opportunities()
        
        # Security and dependency analysis
        self._analyze_security_opportunities()
        
        # Sort by priority score (highest first)
        self.opportunities.sort(key=lambda x: x.priority_score, reverse=True)
        
        return self.opportunities
    
    def _analyze_code_quality(self):
        """Analyze code for quality improvements"""
        try:
            with open(self.app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Look for long functions/methods
            current_function = None
            function_start = 0
            indent_level = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('def ') or stripped.startswith('class '):
                    if current_function and (i - function_start) > 50:
                        self.opportunities.append(EnhancementOpportunity(
                            'code_quality',
                            f'Long function/method detected: {current_function} ({i - function_start} lines)',
                            0.6, 0.4, str(self.app_path), [function_start, i]
                        ))
                    current_function = stripped.split('(')[0].replace('def ', '').replace('class ', '')
                    function_start = i
                    
            # Look for duplicated code patterns
            self._detect_code_duplication(lines)
            
            # Analyze complexity indicators
            self._analyze_complexity(content, lines)
            
        except Exception as e:
            logging.error(f"Code quality analysis failed: {e}")
    
    def _detect_code_duplication(self, lines: List[str]):
        """Detect potential code duplication"""
        # Simple heuristic: look for similar block patterns
        block_hashes = {}
        for i in range(0, len(lines) - 5):
            block = '\n'.join(lines[i:i+5])
            block_normalized = re.sub(r'\s+', ' ', block.strip())
            if len(block_normalized) > 50:  # Only consider substantial blocks
                block_hash = hash(block_normalized)
                if block_hash in block_hashes:
                    self.opportunities.append(EnhancementOpportunity(
                        'code_quality',
                        f'Potential code duplication detected around lines {i} and {block_hashes[block_hash]}',
                        0.5, 0.6, str(self.app_path), [i, block_hashes[block_hash]]
                    ))
                else:
                    block_hashes[block_hash] = i
    
    def _analyze_complexity(self, content: str, lines: List[str]):
        """Analyze code complexity"""
        # Count nested structures
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if ', 'for ', 'while ', 'try:', 'with ']):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped in ['else:', 'elif ', 'except:', 'finally:']:
                continue
            elif stripped.startswith(('def ', 'class ')):
                current_nesting = 1
            elif not stripped or stripped.startswith('#'):
                continue
            else:
                # Reset nesting for regular statements
                current_nesting = max(0, current_nesting - stripped.count('    ') // 4)
        
        if max_nesting > 4:
            self.opportunities.append(EnhancementOpportunity(
                'code_quality',
                f'High cyclomatic complexity detected (max nesting: {max_nesting})',
                0.7, 0.5, str(self.app_path)
            ))
    
    def _analyze_performance_opportunities(self):
        """Enhanced performance optimization analysis with advanced pattern detection"""
        try:
            with open(self.app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Advanced performance pattern analysis
            advanced_patterns = [
                # Database/Memory patterns
                (r'\.append\(.+\)\s*\n.*\.append\(.+\)\s*\n.*\.append\(.+\)', 
                 'Multiple sequential appends could be optimized with extend()', 0.7, 0.3),
                (r'for\s+\w+\s+in\s+range\(len\(.+\)\):', 
                 'Inefficient range(len()) loop could use enumerate()', 0.6, 0.2),
                (r'open\(.+\)\.read\(\)', 
                 'File not properly closed, should use context manager', 0.8, 0.3),
                (r'time\.sleep\(\d+\)', 
                 'Long sleep calls could impact responsiveness', 0.5, 0.2),
                
                # Advanced PyQt optimization patterns
                (r'setText\(.+\)\s*\n.*setText\(.+\)\s*\n.*setText\(.+\)', 
                 'Multiple setText calls could be batched for better performance', 0.6, 0.4),
                (r'QThread\(\).*\.start\(\)', 
                 'Thread management could be optimized with thread pooling', 0.7, 0.5),
                (r'QPixmap\(.+\)\.scaled\(.*\)', 
                 'Image scaling without caching detected, consider implementing image cache', 0.8, 0.4),
                
                # AI/ML performance patterns
                (r'requests\.(get|post)\(.+\)', 
                 'HTTP requests without connection pooling or async handling', 0.7, 0.5),
                (r'json\.loads\(.+\)\s*\n.*json\.loads\(.+\)', 
                 'Multiple JSON parsing operations could be optimized', 0.6, 0.3),
                
                # Memory leaks and resource management
                (r'open\(.+\)\s*\n(?!.*with)', 
                 'File handles not using context managers - potential memory leak', 0.9, 0.3),
                (r'QThread.*(?!.*quit\(\))', 
                 'QThread objects without proper cleanup - potential memory leak', 0.8, 0.4),
            ]
            
            for pattern, description, impact, complexity in advanced_patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE))
                if matches:
                    for match in matches[:3]:  # Limit to first 3 occurrences
                        line_num = content[:match.start()].count('\n') + 1
                        self.opportunities.append(EnhancementOpportunity(
                            'performance',
                            f"{description} (Line {line_num})",
                            impact, complexity, str(self.app_path), [line_num]
                        ))
            
            # Analyze method complexity and performance hotspots
            self._analyze_performance_hotspots(lines)
            
            # Check for algorithmic improvements
            self._analyze_algorithmic_opportunities(content)
                
        except Exception as e:
            logging.error(f"Performance analysis failed: {e}")
    
    def _analyze_performance_hotspots(self, lines: List[str]):
        """Identify performance hotspots in methods"""
        current_method = None
        method_start = 0
        loop_count = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('def '):
                if current_method and loop_count > 2:
                    self.opportunities.append(EnhancementOpportunity(
                        'performance',
                        f'Method {current_method} has {loop_count} nested loops - consider optimization',
                        0.8, 0.6, str(self.app_path), [method_start, i]
                    ))
                current_method = stripped.split('(')[0].replace('def ', '')
                method_start = i
                loop_count = 0
            elif current_method and any(keyword in stripped for keyword in ['for ', 'while ']):
                loop_count += 1
    
    def _analyze_algorithmic_opportunities(self, content: str):
        """Analyze for algorithmic improvement opportunities"""
        # Look for sorting operations that could be optimized
        if re.search(r'sorted\(.+\)\s*\n.*sorted\(.+\)', content):
            self.opportunities.append(EnhancementOpportunity(
                'performance',
                'Multiple sorting operations detected - consider caching or single sort',
                0.7, 0.4, str(self.app_path)
            ))
        
        # Look for string concatenation in loops
        string_concat_pattern = r'for\s+.+:\s*\n\s*.*\s*\+=\s*.+'
        if re.search(string_concat_pattern, content, re.MULTILINE):
            self.opportunities.append(EnhancementOpportunity(
                'performance',
                'String concatenation in loop detected - consider using join() or f-strings',
                0.8, 0.3, str(self.app_path)
            ))
    
    def _analyze_feature_opportunities(self):
        """Enhanced feature analysis with sophisticated capability detection"""
        try:
            with open(self.app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Advanced feature gap analysis
            sophisticated_features = [
                # Modern Python features
                ('async def', 'Implement async/await for non-blocking AI operations', 0.8, 0.6),
                ('typing.', 'Add comprehensive type annotations for better maintainability', 0.7, 0.3),
                ('dataclass', 'Use dataclasses for cleaner data structures', 0.6, 0.3),
                ('pathlib', 'Modernize file path handling with pathlib', 0.5, 0.3),
                ('contextlib', 'Add context managers for better resource handling', 0.7, 0.4),
                
                # AI/ML enhancements
                ('caching', 'Implement intelligent caching for AI responses', 0.8, 0.5),
                ('batch.*process', 'Add batch processing for multiple files', 0.7, 0.6),
                ('streaming', 'Implement streaming responses for better UX', 0.8, 0.7),
                ('fine.*tun', 'Add model fine-tuning capabilities', 0.9, 0.8),
                
                # Architecture improvements
                ('plugin', 'Create plugin architecture for extensibility', 0.9, 0.8),
                ('config.*management', 'Enhance configuration management system', 0.6, 0.4),
                ('dependency.*injection', 'Implement dependency injection pattern', 0.7, 0.6),
                ('event.*driven', 'Add event-driven architecture components', 0.8, 0.7),
                
                # Testing and quality
                ('pytest', 'Implement comprehensive testing framework', 0.8, 0.5),
                ('coverage', 'Add code coverage analysis', 0.6, 0.3),
                ('profiling', 'Add performance profiling tools', 0.7, 0.4),
                ('metrics', 'Implement application metrics and monitoring', 0.8, 0.6),
            ]
            
            for pattern, suggestion, impact, complexity in sophisticated_features:
                if pattern not in content.lower():
                    self.opportunities.append(EnhancementOpportunity(
                        'feature',
                        suggestion,
                        impact, complexity, str(self.app_path)
                    ))
            
            # Advanced UI/UX enhancement analysis
            self._analyze_ui_enhancement_opportunities(content)
            
            # Analyze missing AI capabilities
            self._analyze_ai_capability_gaps(content)
            
            # Check for integration opportunities
            self._analyze_integration_opportunities(content)
                    
        except Exception as e:
            logging.error(f"Feature analysis failed: {e}")
    
    def _analyze_ui_enhancement_opportunities(self, content: str):
        """Analyze UI/UX enhancement opportunities"""
        if 'PyQt' in content:
            advanced_ui_features = [
                ('Advanced keyboard shortcuts with customizable hotkeys', 0.7, 0.4),
                ('Intelligent auto-save with conflict resolution', 0.8, 0.5),
                ('Drag-and-drop with preview and validation', 0.8, 0.6),
                ('Multi-language internationalization support', 0.7, 0.7),
                ('Advanced accessibility features (ARIA, screen readers)', 0.9, 0.6),
                ('Real-time collaborative editing capabilities', 0.9, 0.9),
                ('Customizable workspace layouts and themes', 0.6, 0.5),
                ('Advanced search and filtering with fuzzy matching', 0.7, 0.4),
                ('Voice commands and speech recognition integration', 0.8, 0.8),
                ('Gesture-based navigation and shortcuts', 0.6, 0.7),
            ]
            
            for feature, impact, complexity in advanced_ui_features:
                # Check if feature already exists (basic heuristic)
                if not any(keyword in content.lower() for keyword in feature.lower().split()[:2]):
                    self.opportunities.append(EnhancementOpportunity(
                        'ui_enhancement',
                        f"Implement {feature}",
                        impact, complexity, str(self.app_path)
                    ))
    
    def _analyze_ai_capability_gaps(self, content: str):
        """Analyze missing AI capabilities"""
        ai_enhancements = [
            ('Multi-modal AI support (vision + text + audio)', 0.9, 0.8),
            ('Conversation memory and context persistence', 0.8, 0.5),
            ('Custom AI model training and fine-tuning', 0.9, 0.9),
            ('Intelligent auto-completion and suggestions', 0.7, 0.6),
            ('AI-powered code review and optimization', 0.8, 0.7),
            ('Natural language query processing', 0.8, 0.6),
            ('Intelligent file organization and tagging', 0.7, 0.5),
            ('Predictive user behavior modeling', 0.8, 0.8),
        ]
        
        for feature, impact, complexity in ai_enhancements:
            if not any(keyword in content.lower() for keyword in feature.lower().split()[:2]):
                self.opportunities.append(EnhancementOpportunity(
                    'ai_enhancement',
                    f"Add {feature}",
                    impact, complexity, str(self.app_path)
                ))
    
    def _analyze_integration_opportunities(self, content: str):
        """Analyze integration and ecosystem opportunities"""
        integrations = [
            ('Cloud storage integration (Google Drive, Dropbox)', 0.7, 0.6),
            ('Version control system integration (Git)', 0.8, 0.5),
            ('External API connectors and webhooks', 0.8, 0.6),
            ('Database integration for large-scale data', 0.8, 0.7),
            ('Container deployment support (Docker)', 0.6, 0.4),
            ('CI/CD pipeline integration', 0.7, 0.6),
            ('Monitoring and analytics integration', 0.7, 0.5),
            ('Third-party AI service integrations', 0.8, 0.5),
        ]
        
        for feature, impact, complexity in integrations:
            if not any(keyword in content.lower() for keyword in feature.lower().split()[:2]):
                self.opportunities.append(EnhancementOpportunity(
                    'integration',
                    f"Implement {feature}",
                    impact, complexity, str(self.app_path)
                ))
    
    def _analyze_security_opportunities(self):
        """Identify security and dependency improvement opportunities"""
        try:
            with open(self.app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Security patterns to check
            security_checks = [
                ('api_key', 'Ensure API keys are properly secured and not logged'),
                ('password', 'Implement secure password handling'),
                ('eval(', 'Avoid eval() usage for security'),
                ('exec(', 'Avoid exec() usage for security'),
                ('shell=True', 'Review shell=True usage for security implications'),
            ]
            
            for pattern, warning in security_checks:
                if pattern in content.lower():
                    self.opportunities.append(EnhancementOpportunity(
                        'security',
                        warning,
                        0.8, 0.3, str(self.app_path)
                    ))
            
            # Check for dependency updates
            if 'import' in content:
                self.opportunities.append(EnhancementOpportunity(
                    'maintenance',
                    'Review and update dependencies to latest secure versions',
                    0.7, 0.3, str(self.app_path)
                ))
                
        except Exception as e:
            logging.error(f"Security analysis failed: {e}")

class EnhancementResearchEngine:
    """Advanced internet research engine for discovering best practices and solutions"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.research_cache = {}
        self.research_history = []
        
    def research_enhancement_solution(self, opportunity: EnhancementOpportunity) -> dict:
        """Research best practices and solutions for a specific enhancement opportunity"""
        research_result = {
            'research_summary': '',
            'best_practices': [],
            'code_examples': [],
            'performance_insights': [],
            'implementation_strategies': [],
            'related_technologies': [],
            'research_confidence': 0.0
        }
        
        try:
            # Generate targeted research queries
            queries = self._generate_research_queries(opportunity)
            
            # Perform research for each query
            for query in queries:
                if query in self.research_cache:
                    # Use cached results
                    cached_result = self.research_cache[query]
                    self._merge_research_results(research_result, cached_result)
                else:
                    # Perform new research
                    query_result = self._perform_web_research(query, opportunity)
                    if query_result:
                        self.research_cache[query] = query_result
                        self._merge_research_results(research_result, query_result)
            
            # Calculate research confidence based on results quality
            research_result['research_confidence'] = self._calculate_research_confidence(research_result)
            
            # Store research in memory for future reference
            self._store_research_in_memory(opportunity, research_result)
            
            return research_result
            
        except Exception as e:
            logging.error(f"Enhancement research failed: {e}")
            return research_result
    
    def _generate_research_queries(self, opportunity: EnhancementOpportunity) -> List[str]:
        """Generate targeted research queries based on opportunity type and description"""
        base_queries = []
        
        if opportunity.opportunity_type == 'performance':
            base_queries = [
                f"Python performance optimization {opportunity.description.lower()}",
                f"best practices {opportunity.opportunity_type} Python algorithms",
                f"optimize {opportunity.description.split()[0]} performance Python",
                "Python performance benchmarking tools techniques",
                "algorithmic complexity optimization Python"
            ]
        elif opportunity.opportunity_type == 'feature':
            base_queries = [
                f"Python implementation {opportunity.description.lower()}",
                f"best practices {opportunity.description} Python framework",
                f"modern Python {opportunity.opportunity_type} development",
                "Python design patterns architectural best practices",
                "Python framework comparison feature implementation"
            ]
        elif opportunity.opportunity_type == 'ai_enhancement':
            base_queries = [
                f"AI machine learning {opportunity.description.lower()}",
                f"Python AI library {opportunity.description}",
                "latest AI techniques Python implementation",
                "Hugging Face transformers integration Python",
                "OpenAI API best practices Python"
            ]
        elif opportunity.opportunity_type == 'ui_enhancement':
            base_queries = [
                f"PyQt6 {opportunity.description.lower()}",
                f"Python GUI {opportunity.description} best practices",
                "PyQt6 modern UI design patterns",
                "Python desktop application UX improvements",
                "PyQt6 accessibility features implementation"
            ]
        else:
            # Generic queries for other types
            base_queries = [
                f"Python {opportunity.opportunity_type} {opportunity.description.lower()}",
                f"best practices {opportunity.opportunity_type} Python",
                f"modern Python {opportunity.description}",
                "Python software engineering best practices",
                "Python code quality improvement techniques"
            ]
        
        return base_queries[:3]  # Limit to 3 queries to avoid rate limiting
    
    def _perform_web_research(self, query: str, opportunity: EnhancementOpportunity) -> dict:
        """Perform web research using available search tools"""
        try:
            # Use WebSearch tool to find relevant information
            # This will need to be integrated with the actual WebSearch tool available in the system
            search_results = self._call_web_search_tool(query)
            
            if not search_results:
                return None
            
            # Process search results to extract useful information
            research_data = {
                'query': query,
                'best_practices': [],
                'code_examples': [],
                'performance_insights': [],
                'implementation_strategies': [],
                'related_technologies': [],
                'sources': []
            }
            
            # Analyze search results
            for result in search_results[:5]:  # Limit to top 5 results
                if 'github.com' in result.get('url', ''):
                    research_data['code_examples'].append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('snippet', '')
                    })
                elif 'stackoverflow.com' in result.get('url', ''):
                    research_data['best_practices'].append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('snippet', '')
                    })
                elif any(domain in result.get('url', '') for domain in ['arxiv.org', 'papers.', 'research.']):
                    research_data['performance_insights'].append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('snippet', '')
                    })
                else:
                    research_data['implementation_strategies'].append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('snippet', '')
                    })
                
                research_data['sources'].append(result.get('url', ''))
            
            return research_data
            
        except Exception as e:
            logging.error(f"Web research failed for query '{query}': {e}")
            return None
    
    def _call_web_search_tool(self, query: str) -> List[dict]:
        """Interface with the actual WebSearch tool available in the system"""
        try:
            # This would integrate with the WebSearch tool that's available
            # For now, return a mock structure that matches expected format
            mock_results = [
                {
                    'title': f"Best Practices for {query}",
                    'url': f"https://stackoverflow.com/questions/search?q={query.replace(' ', '+')}",
                    'snippet': f"Community discussions and solutions for {query}"
                },
                {
                    'title': f"GitHub Implementation of {query}",
                    'url': f"https://github.com/search?q={query.replace(' ', '+')}",
                    'snippet': f"Open source code examples for {query}"
                },
                {
                    'title': f"Python Documentation for {query}",
                    'url': f"https://docs.python.org/search.html?q={query.replace(' ', '+')}",
                    'snippet': f"Official Python documentation and examples for {query}"
                }
            ]
            return mock_results
        except Exception as e:
            logging.error(f"Web search tool call failed: {e}")
            return []
    
    def _merge_research_results(self, main_result: dict, query_result: dict):
        """Merge research results from multiple queries"""
        for key in ['best_practices', 'code_examples', 'performance_insights', 
                   'implementation_strategies', 'related_technologies']:
            if key in query_result:
                main_result[key].extend(query_result[key])
        
        # Update research summary
        if query_result.get('query'):
            if main_result['research_summary']:
                main_result['research_summary'] += f"\n\nResearch Query: {query_result['query']}"
            else:
                main_result['research_summary'] = f"Research Query: {query_result['query']}"
    
    def _calculate_research_confidence(self, research_result: dict) -> float:
        """Calculate confidence score based on research quality and quantity"""
        confidence = 0.0
        
        # Base confidence from having results
        if research_result['research_summary']:
            confidence += 0.3
        
        # Confidence from different types of results
        result_types = ['best_practices', 'code_examples', 'performance_insights', 
                       'implementation_strategies', 'related_technologies']
        
        for result_type in result_types:
            if research_result.get(result_type):
                confidence += 0.1 * min(len(research_result[result_type]), 3)
        
        # Bonus for diverse sources
        if len(set(result_types) & set(k for k, v in research_result.items() if v)) >= 3:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _store_research_in_memory(self, opportunity: EnhancementOpportunity, research_result: dict):
        """Store research results in memory for future reference and learning"""
        try:
            # Create a comprehensive research record
            research_record = {
                'opportunity_type': opportunity.opportunity_type,
                'opportunity_description': opportunity.description,
                'research_timestamp': datetime.now().isoformat(),
                'research_summary': research_result['research_summary'],
                'confidence_score': research_result['research_confidence'],
                'results_count': sum(len(research_result.get(key, [])) for key in 
                                   ['best_practices', 'code_examples', 'performance_insights']),
                'research_metadata': {
                    'impact_score': opportunity.impact_score,
                    'complexity_score': opportunity.complexity_score,
                    'priority_score': opportunity.priority_score
                }
            }
            
            # Store in memory with metadata
            self.memory.store_context(
                f"enhancement_research_{opportunity.opportunity_type}",
                research_record,
                metadata={
                    'type': 'enhancement_research',
                    'opportunity_type': opportunity.opportunity_type,
                    'timestamp': datetime.now().isoformat(),
                    'confidence': research_result['research_confidence']
                }
            )
            
            # Add to local research history
            self.research_history.append(research_record)
            
        except Exception as e:
            logging.error(f"Failed to store research in memory: {e}")
    
    def get_similar_research(self, opportunity: EnhancementOpportunity, limit: int = 5) -> List[dict]:
        """Retrieve similar past research for pattern learning"""
        try:
            # Query memory for similar enhancement research
            similar_research = self.memory.query_context(
                f"enhancement research {opportunity.opportunity_type} {opportunity.description}",
                k=limit,
                filter_metadata={'type': 'enhancement_research'}
            )
            
            return similar_research
            
        except Exception as e:
            logging.error(f"Failed to retrieve similar research: {e}")
            return []
    
    def analyze_research_patterns(self) -> dict:
        """Analyze patterns in successful research to improve future queries"""
        pattern_analysis = {
            'most_successful_query_types': {},
            'best_source_domains': {},
            'optimal_query_length': 0,
            'success_factors': []
        }
        
        try:
            if not self.research_history:
                return pattern_analysis
            
            # Analyze successful research patterns
            high_confidence_research = [r for r in self.research_history if r.get('confidence_score', 0) > 0.7]
            
            if high_confidence_research:
                # Find common patterns in successful research
                for research in high_confidence_research:
                    opp_type = research.get('opportunity_type', 'unknown')
                    pattern_analysis['most_successful_query_types'][opp_type] = (
                        pattern_analysis['most_successful_query_types'].get(opp_type, 0) + 1
                    )
                
                # Calculate optimal patterns
                if pattern_analysis['most_successful_query_types']:
                    pattern_analysis['success_factors'] = [
                        f"Query type '{k}' has {v} successful research instances"
                        for k, v in pattern_analysis['most_successful_query_types'].items()
                    ]
            
            return pattern_analysis
            
        except Exception as e:
            logging.error(f"Research pattern analysis failed: {e}")
            return pattern_analysis

class EnhancementMetricsTracker:
    """Advanced metrics tracking system for enhancement effectiveness"""
    
    def __init__(self, memory_manager: MemoryManager, output_dir: Path):
        self.memory = memory_manager
        self.output_dir = output_dir
        self.metrics_history = []
        self.performance_baselines = {}
        
    def establish_baseline_metrics(self, app_path: str) -> dict:
        """Establish baseline performance and quality metrics"""
        baseline_metrics = {
            'timestamp': datetime.now().isoformat(),
            'file_size_bytes': 0,
            'lines_of_code': 0,
            'cyclomatic_complexity': 0,
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'comment_ratio': 0.0,
            'test_coverage': 0.0,
            'performance_score': 0.0
        }
        
        try:
            # File size metrics
            if Path(app_path).exists():
                baseline_metrics['file_size_bytes'] = Path(app_path).stat().st_size
                
                with open(app_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # Basic code metrics
                    baseline_metrics['lines_of_code'] = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                    baseline_metrics['function_count'] = len(re.findall(r'^\s*def ', content, re.MULTILINE))
                    baseline_metrics['class_count'] = len(re.findall(r'^\s*class ', content, re.MULTILINE))
                    baseline_metrics['import_count'] = len(re.findall(r'^\s*(?:import|from)', content, re.MULTILINE))
                    
                    # Comment ratio
                    comment_lines = len([l for l in lines if l.strip().startswith('#')])
                    baseline_metrics['comment_ratio'] = comment_lines / max(len(lines), 1)
                    
                    # Basic complexity estimation
                    complexity_indicators = len(re.findall(r'\b(?:if|for|while|try|except|with)\b', content))
                    baseline_metrics['cyclomatic_complexity'] = complexity_indicators
            
            # Store baseline in memory
            self.memory.store_context(
                "enhancement_baseline_metrics",
                baseline_metrics,
                metadata={
                    'type': 'baseline_metrics',
                    'timestamp': baseline_metrics['timestamp'],
                    'app_path': app_path
                }
            )
            
            self.performance_baselines = baseline_metrics
            return baseline_metrics
            
        except Exception as e:
            logging.error(f"Failed to establish baseline metrics: {e}")
            return baseline_metrics
    
    def measure_enhancement_impact(self, app_path: str, enhancement_version: str, 
                                 opportunity: EnhancementOpportunity, solution: str) -> dict:
        """Measure the impact of an enhancement compared to baseline"""
        impact_metrics = {
            'enhancement_version': enhancement_version,
            'timestamp': datetime.now().isoformat(),
            'opportunity_type': opportunity.opportunity_type,
            'opportunity_description': opportunity.description,
            'solution_size_lines': len(solution.split('\n')),
            'improvements': {},
            'regressions': {},
            'overall_impact_score': 0.0
        }
        
        try:
            # Get current metrics
            current_metrics = self.establish_baseline_metrics(app_path)
            
            # Compare with baseline
            if self.performance_baselines:
                impact_metrics['improvements'] = {}
                impact_metrics['regressions'] = {}
                
                for metric, current_value in current_metrics.items():
                    if metric in ['timestamp']:
                        continue
                        
                    baseline_value = self.performance_baselines.get(metric, 0)
                    if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                        if baseline_value > 0:
                            change_percent = ((current_value - baseline_value) / baseline_value) * 100
                            
                            # Determine if change is improvement or regression
                            improvement_metrics = ['comment_ratio', 'test_coverage', 'performance_score']
                            regression_metrics = ['cyclomatic_complexity', 'file_size_bytes']
                            
                            if metric in improvement_metrics and change_percent > 0:
                                impact_metrics['improvements'][metric] = change_percent
                            elif metric in regression_metrics and change_percent < 0:
                                impact_metrics['improvements'][metric] = abs(change_percent)
                            elif metric in improvement_metrics and change_percent < 0:
                                impact_metrics['regressions'][metric] = abs(change_percent)
                            elif metric in regression_metrics and change_percent > 0:
                                impact_metrics['regressions'][metric] = change_percent
                            else:
                                # Neutral metrics - just track the change
                                impact_metrics[f'{metric}_change_percent'] = change_percent
            
            # Calculate overall impact score
            impact_metrics['overall_impact_score'] = self._calculate_overall_impact_score(impact_metrics)
            
            # Store metrics in memory and history
            self.memory.store_context(
                f"enhancement_impact_{enhancement_version}",
                impact_metrics,
                metadata={
                    'type': 'enhancement_impact',
                    'version': enhancement_version,
                    'timestamp': impact_metrics['timestamp'],
                    'impact_score': impact_metrics['overall_impact_score']
                }
            )
            
            self.metrics_history.append(impact_metrics)
            
            return impact_metrics
            
        except Exception as e:
            logging.error(f"Failed to measure enhancement impact: {e}")
            return impact_metrics
    
    def _calculate_overall_impact_score(self, impact_metrics: dict) -> float:
        """Calculate overall impact score from improvements and regressions"""
        improvements = impact_metrics.get('improvements', {})
        regressions = impact_metrics.get('regressions', {})
        
        # Weight improvements and regressions
        improvement_score = sum(min(value / 10, 1.0) for value in improvements.values())  # Cap at 1.0 per metric
        regression_penalty = sum(min(value / 10, 0.5) for value in regressions.values())  # Cap penalty at 0.5
        
        # Base score from opportunity impact
        base_score = 0.5
        
        # Calculate final score
        final_score = base_score + improvement_score - regression_penalty
        return max(0.0, min(final_score, 1.0))  # Clamp between 0 and 1
    
    def get_enhancement_effectiveness_report(self) -> dict:
        """Generate comprehensive effectiveness report"""
        if not self.metrics_history:
            return {'message': 'No enhancement metrics available'}
        
        report = {
            'total_enhancements': len(self.metrics_history),
            'average_impact_score': 0.0,
            'most_effective_enhancement': None,
            'improvement_trends': {},
            'recommendation_score': 0.0,
            'success_patterns': []
        }
        
        try:
            # Calculate average impact
            impact_scores = [m.get('overall_impact_score', 0) for m in self.metrics_history]
            report['average_impact_score'] = sum(impact_scores) / len(impact_scores)
            
            # Find most effective enhancement
            best_enhancement = max(self.metrics_history, key=lambda x: x.get('overall_impact_score', 0))
            report['most_effective_enhancement'] = {
                'version': best_enhancement.get('enhancement_version'),
                'type': best_enhancement.get('opportunity_type'),
                'description': best_enhancement.get('opportunity_description'),
                'impact_score': best_enhancement.get('overall_impact_score')
            }
            
            # Analyze improvement trends by type
            type_impacts = {}
            for metrics in self.metrics_history:
                opp_type = metrics.get('opportunity_type', 'unknown')
                impact = metrics.get('overall_impact_score', 0)
                
                if opp_type not in type_impacts:
                    type_impacts[opp_type] = []
                type_impacts[opp_type].append(impact)
            
            for opp_type, impacts in type_impacts.items():
                report['improvement_trends'][opp_type] = {
                    'average_impact': sum(impacts) / len(impacts),
                    'enhancement_count': len(impacts),
                    'success_rate': len([i for i in impacts if i > 0.6]) / len(impacts)
                }
            
            # Calculate recommendation score
            recent_metrics = self.metrics_history[-5:] if len(self.metrics_history) >= 5 else self.metrics_history
            recent_average = sum(m.get('overall_impact_score', 0) for m in recent_metrics) / len(recent_metrics)
            report['recommendation_score'] = recent_average
            
            # Identify success patterns
            successful_enhancements = [m for m in self.metrics_history if m.get('overall_impact_score', 0) > 0.7]
            if successful_enhancements:
                success_types = [e.get('opportunity_type') for e in successful_enhancements]
                most_successful_type = max(set(success_types), key=success_types.count)
                report['success_patterns'].append(f"Enhancement type '{most_successful_type}' has highest success rate")
            
            return report
            
        except Exception as e:
            logging.error(f"Failed to generate effectiveness report: {e}")
            return report

class EnhancementPatternLearning:
    """Advanced pattern learning system for cross-enhancement knowledge transfer"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.pattern_database = {}
        self.success_patterns = []
        self.learned_techniques = {}
        
    def extract_success_patterns(self, successful_enhancements: List[dict]) -> List[dict]:
        """Extract patterns from successful enhancements for future use"""
        patterns = []
        
        try:
            for enhancement in successful_enhancements:
                if enhancement.get('impact_metrics', {}).get('overall_impact_score', 0) > 0.7:
                    pattern = self._analyze_enhancement_for_patterns(enhancement)
                    if pattern:
                        patterns.append(pattern)
                        self.success_patterns.append(pattern)
            
            # Store patterns in memory for future retrieval
            self._store_patterns_in_memory(patterns)
            
            return patterns
            
        except Exception as e:
            logging.error(f"Failed to extract success patterns: {e}")
            return []
    
    def _analyze_enhancement_for_patterns(self, enhancement: dict) -> dict:
        """Analyze a successful enhancement to extract reusable patterns"""
        pattern = {
            'pattern_id': f"pattern_{len(self.success_patterns) + 1}",
            'opportunity_type': enhancement.get('opportunity_type'),
            'success_factors': [],
            'code_patterns': [],
            'architectural_decisions': [],
            'performance_improvements': [],
            'implementation_strategy': '',
            'confidence_score': 0.0
        }
        
        try:
            # Extract code patterns from solution
            solution = enhancement.get('solution_summary', '')
            if solution:
                # Look for common successful patterns
                code_patterns = self._extract_code_patterns(solution)
                pattern['code_patterns'] = code_patterns
                
                # Analyze architectural decisions
                arch_patterns = self._extract_architectural_patterns(solution)
                pattern['architectural_decisions'] = arch_patterns
                
                # Extract implementation strategy
                strategy = self._extract_implementation_strategy(solution, enhancement.get('opportunity_type'))
                pattern['implementation_strategy'] = strategy
            
            # Extract success factors from metrics
            impact_metrics = enhancement.get('impact_metrics', {})
            if impact_metrics:
                improvements = impact_metrics.get('improvements', {})
                pattern['success_factors'] = list(improvements.keys())
                pattern['performance_improvements'] = [
                    f"{metric}: {value:.1f}% improvement" 
                    for metric, value in improvements.items()
                ]
            
            # Calculate pattern confidence based on impact score
            pattern['confidence_score'] = impact_metrics.get('overall_impact_score', 0)
            
            return pattern
            
        except Exception as e:
            logging.error(f"Failed to analyze enhancement for patterns: {e}")
            return None
    
    def _extract_code_patterns(self, solution: str) -> List[str]:
        """Extract reusable code patterns from solution"""
        patterns = []
        
        # Common successful patterns to look for
        pattern_checks = [
            (r'async\s+def', 'Async/await pattern for non-blocking operations'),
            (r'class\s+\w+.*Manager', 'Manager class pattern for resource coordination'),
            (r'def\s+.*_factory\(', 'Factory pattern for object creation'),
            (r'@\w+', 'Decorator pattern for cross-cutting concerns'),
            (r'with\s+.*:', 'Context manager pattern for resource management'),
            (r'try:.*except.*finally:', 'Comprehensive error handling pattern'),
            (r'logging\.\w+\(', 'Proper logging integration'),
            (r'cache\s*=', 'Caching implementation pattern'),
            (r'config\.\w+', 'Configuration-driven approach'),
            (r'validate_.*\(', 'Input validation pattern')
        ]
        
        for pattern_regex, description in pattern_checks:
            if re.search(pattern_regex, solution, re.MULTILINE | re.DOTALL):
                patterns.append(description)
        
        return patterns
    
    def _extract_architectural_patterns(self, solution: str) -> List[str]:
        """Extract architectural decision patterns"""
        patterns = []
        
        arch_indicators = [
            ('separation of concerns', 'Multiple specialized classes/functions'),
            ('dependency injection', 'Constructor parameter injection'),
            ('observer pattern', 'Event-driven architecture'),
            ('strategy pattern', 'Pluggable algorithm implementations'),
            ('facade pattern', 'Simplified interface to complex subsystem'),
            ('template method', 'Algorithm skeleton with customizable steps'),
            ('singleton pattern', 'Single instance management'),
            ('builder pattern', 'Step-by-step object construction')
        ]
        
        for pattern_name, indicator in arch_indicators:
            # Simple heuristics to detect architectural patterns
            if any(keyword in solution.lower() for keyword in indicator.lower().split()[:2]):
                patterns.append(pattern_name)
        
        return patterns
    
    def _extract_implementation_strategy(self, solution: str, opportunity_type: str) -> str:
        """Extract the overall implementation strategy used"""
        strategies = []
        
        if opportunity_type == 'performance':
            if 'cache' in solution.lower():
                strategies.append('Caching optimization')
            if 'async' in solution.lower():
                strategies.append('Asynchronous processing')
            if 'batch' in solution.lower():
                strategies.append('Batch processing optimization')
        elif opportunity_type == 'feature':
            if 'class' in solution.lower() and 'manager' in solution.lower():
                strategies.append('Manager-based feature architecture')
            if 'config' in solution.lower():
                strategies.append('Configuration-driven feature implementation')
        elif opportunity_type == 'ai_enhancement':
            if 'model' in solution.lower():
                strategies.append('AI model integration approach')
            if 'pipeline' in solution.lower():
                strategies.append('Processing pipeline enhancement')
        
        return '; '.join(strategies) if strategies else 'Standard implementation approach'
    
    def _store_patterns_in_memory(self, patterns: List[dict]):
        """Store learned patterns in memory for future retrieval"""
        try:
            for pattern in patterns:
                self.memory.store_context(
                    f"learned_pattern_{pattern['pattern_id']}",
                    pattern,
                    metadata={
                        'type': 'learned_pattern',
                        'pattern_id': pattern['pattern_id'],
                        'opportunity_type': pattern['opportunity_type'],
                        'confidence_score': pattern['confidence_score'],
                        'timestamp': datetime.now().isoformat()
                    }
                )
        except Exception as e:
            logging.error(f"Failed to store patterns in memory: {e}")
    
    def find_applicable_patterns(self, opportunity: EnhancementOpportunity) -> List[dict]:
        """Find learned patterns applicable to a new enhancement opportunity"""
        applicable_patterns = []
        
        try:
            # Query memory for similar patterns
            query = f"learned pattern {opportunity.opportunity_type} {opportunity.description}"
            similar_patterns = self.memory.query_context(
                query,
                k=5,
                filter_metadata={'type': 'learned_pattern'}
            )
            
            # Filter patterns by relevance and confidence
            for pattern_data in similar_patterns:
                pattern = pattern_data.get('content', {})
                confidence = pattern.get('confidence_score', 0)
                
                # Only include high-confidence patterns
                if confidence > 0.6:
                    # Calculate relevance score
                    relevance = self._calculate_pattern_relevance(pattern, opportunity)
                    if relevance > 0.5:
                        pattern['relevance_score'] = relevance
                        applicable_patterns.append(pattern)
            
            # Sort by combined confidence and relevance
            applicable_patterns.sort(
                key=lambda p: (p.get('confidence_score', 0) + p.get('relevance_score', 0)) / 2,
                reverse=True
            )
            
            return applicable_patterns[:3]  # Return top 3 most applicable patterns
            
        except Exception as e:
            logging.error(f"Failed to find applicable patterns: {e}")
            return []
    
    def _calculate_pattern_relevance(self, pattern: dict, opportunity: EnhancementOpportunity) -> float:
        """Calculate how relevant a learned pattern is to the current opportunity"""
        relevance_score = 0.0
        
        # Type match bonus
        if pattern.get('opportunity_type') == opportunity.opportunity_type:
            relevance_score += 0.4
        
        # Description similarity (simple keyword matching)
        pattern_keywords = set(pattern.get('implementation_strategy', '').lower().split())
        opportunity_keywords = set(opportunity.description.lower().split())
        
        if pattern_keywords and opportunity_keywords:
            keyword_overlap = len(pattern_keywords & opportunity_keywords) / len(pattern_keywords | opportunity_keywords)
            relevance_score += keyword_overlap * 0.3
        
        # Success factor relevance
        success_factors = pattern.get('success_factors', [])
        if any(factor in opportunity.description.lower() for factor in success_factors):
            relevance_score += 0.3
        
        return min(relevance_score, 1.0)
    
    def apply_learned_patterns(self, opportunity: EnhancementOpportunity, applicable_patterns: List[dict]) -> str:
        """Generate pattern-informed enhancement suggestions"""
        if not applicable_patterns:
            return ""
        
        suggestions = """🧠 LEARNED PATTERN INSIGHTS:
Based on analysis of successful past enhancements, consider these proven approaches:

"""
        
        for i, pattern in enumerate(applicable_patterns, 1):
            suggestions += f"{i}. **{pattern.get('opportunity_type', 'General').title()} Enhancement Pattern** "
            suggestions += f"(Confidence: {pattern.get('confidence_score', 0):.1%}, "
            suggestions += f"Relevance: {pattern.get('relevance_score', 0):.1%}):\n"
            
            # Add implementation strategy
            strategy = pattern.get('implementation_strategy', '')
            if strategy:
                suggestions += f"   • Strategy: {strategy}\n"
            
            # Add successful code patterns
            code_patterns = pattern.get('code_patterns', [])
            if code_patterns:
                suggestions += f"   • Proven patterns: {', '.join(code_patterns[:3])}\n"
            
            # Add architectural decisions
            arch_decisions = pattern.get('architectural_decisions', [])
            if arch_decisions:
                suggestions += f"   • Architecture: {', '.join(arch_decisions[:2])}\n"
            
            # Add performance improvements achieved
            perf_improvements = pattern.get('performance_improvements', [])
            if perf_improvements:
                suggestions += f"   • Past improvements: {', '.join(perf_improvements[:2])}\n"
            
            suggestions += "\n"
        
        return suggestions
    
    def generate_enhancement_evolution_suggestions(self, enhancement_history: List[dict]) -> List[str]:
        """Generate suggestions for how enhancements can build upon each other"""
        evolution_suggestions = []
        
        try:
            if len(enhancement_history) < 2:
                return evolution_suggestions
            
            # Analyze patterns across enhancement history
            type_sequences = []
            success_trends = []
            
            for i in range(len(enhancement_history) - 1):
                current = enhancement_history[i]
                next_enh = enhancement_history[i + 1]
                
                current_type = current.get('opportunity_type', 'unknown')
                next_type = next_enh.get('opportunity_type', 'unknown')
                
                type_sequences.append((current_type, next_type))
                
                current_impact = current.get('impact_metrics', {}).get('overall_impact_score', 0)
                next_impact = next_enh.get('impact_metrics', {}).get('overall_impact_score', 0)
                
                success_trends.append(next_impact - current_impact)
            
            # Identify successful enhancement sequences
            successful_sequences = []
            for i, trend in enumerate(success_trends):
                if trend > 0.1:  # Significant improvement
                    successful_sequences.append(type_sequences[i])
            
            # Generate suggestions based on successful patterns
            if successful_sequences:
                most_common_sequence = max(set(successful_sequences), key=successful_sequences.count)
                evolution_suggestions.append(
                    f"Consider following the successful pattern: {most_common_sequence[0]} → {most_common_sequence[1]}"
                )
            
            # Suggest compound enhancements
            recent_types = [e.get('opportunity_type') for e in enhancement_history[-3:]]
            if len(set(recent_types)) == 1:  # All same type
                evolution_suggestions.append(
                    f"Consider diversifying from {recent_types[0]} to complementary enhancement types"
                )
            
            return evolution_suggestions
            
        except Exception as e:
            logging.error(f"Failed to generate evolution suggestions: {e}")
            return []

class EnhancementCompositionEngine:
    """System for combining multiple enhancements into compound improvements"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.composition_history = []
        self.synergy_patterns = {}
        
    def identify_composable_opportunities(self, opportunities: List[EnhancementOpportunity]) -> List[dict]:
        """Identify sets of opportunities that can be combined for compound improvements"""
        compositions = []
        
        if len(opportunities) < 2:
            return compositions
        
        try:
            # Group opportunities by type for potential synergies
            type_groups = {}
            for opp in opportunities:
                opp_type = opp.opportunity_type
                if opp_type not in type_groups:
                    type_groups[opp_type] = []
                type_groups[opp_type].append(opp)
            
            # Look for cross-type synergies
            synergy_combinations = [
                ('performance', 'feature', 'Performance-enhanced feature implementation'),
                ('ui_enhancement', 'feature', 'Feature with enhanced user experience'),
                ('ai_enhancement', 'performance', 'Optimized AI capability integration'),
                ('security', 'feature', 'Secure feature implementation'),
                ('code_quality', 'performance', 'Clean, optimized code architecture'),
                ('integration', 'ai_enhancement', 'AI-powered integration capabilities')
            ]
            
            for type1, type2, description in synergy_combinations:
                if type1 in type_groups and type2 in type_groups:
                    # Find best opportunities from each type
                    best_type1 = max(type_groups[type1], key=lambda x: x.priority_score)
                    best_type2 = max(type_groups[type2], key=lambda x: x.priority_score)
                    
                    composition = self._create_composition(
                        [best_type1, best_type2], description
                    )
                    if composition:
                        compositions.append(composition)
            
            # Look for same-type compositions (compound enhancements)
            for opp_type, group_opps in type_groups.items():
                if len(group_opps) >= 2:
                    # Select top opportunities for composition
                    top_opps = sorted(group_opps, key=lambda x: x.priority_score, reverse=True)[:3]
                    
                    if len(top_opps) >= 2:
                        composition = self._create_composition(
                            top_opps, f"Compound {opp_type} enhancement"
                        )
                        if composition:
                            compositions.append(composition)
            
            # Sort compositions by potential impact
            compositions.sort(key=lambda x: x.get('compound_impact_score', 0), reverse=True)
            
            return compositions[:3]  # Return top 3 compositions
            
        except Exception as e:
            logging.error(f"Failed to identify composable opportunities: {e}")
            return compositions
    
    def _create_composition(self, opportunities: List[EnhancementOpportunity], description: str) -> dict:
        """Create a composition from multiple opportunities"""
        try:
            composition = {
                'composition_id': f"comp_{len(self.composition_history) + 1}",
                'description': description,
                'component_opportunities': [opp.to_dict() for opp in opportunities],
                'compound_impact_score': 0.0,
                'complexity_multiplier': 1.0,
                'synergy_potential': 0.0,
                'implementation_strategy': '',
                'expected_benefits': []
            }
            
            # Calculate compound impact (not just sum, but considering synergies)
            individual_impacts = [opp.impact_score for opp in opportunities]
            base_impact = sum(individual_impacts)
            
            # Calculate synergy bonus based on opportunity types
            synergy_bonus = self._calculate_synergy_bonus(opportunities)
            composition['synergy_potential'] = synergy_bonus
            
            # Compound impact includes synergy
            composition['compound_impact_score'] = base_impact * (1 + synergy_bonus)
            
            # Calculate complexity multiplier (compound tasks are more complex)
            complexity_values = [opp.complexity_score for opp in opportunities]
            composition['complexity_multiplier'] = 1 + (sum(complexity_values) / len(complexity_values)) * 0.5
            
            # Generate implementation strategy
            composition['implementation_strategy'] = self._generate_composition_strategy(opportunities)
            
            # Identify expected benefits
            composition['expected_benefits'] = self._identify_compound_benefits(opportunities)
            
            return composition
            
        except Exception as e:
            logging.error(f"Failed to create composition: {e}")
            return None
    
    def _calculate_synergy_bonus(self, opportunities: List[EnhancementOpportunity]) -> float:
        """Calculate synergy bonus for combining opportunities"""
        synergy_bonus = 0.0
        
        # Define synergy matrices
        synergy_matrix = {
            ('performance', 'feature'): 0.3,  # Performance-optimized features
            ('ui_enhancement', 'feature'): 0.25,  # Feature with better UX
            ('ai_enhancement', 'performance'): 0.35,  # Optimized AI capabilities
            ('security', 'feature'): 0.2,  # Secure feature implementation
            ('code_quality', 'performance'): 0.25,  # Clean, fast code
            ('integration', 'ai_enhancement'): 0.3,  # AI-powered integrations
            ('feature', 'feature'): 0.15,  # Compound features
            ('performance', 'performance'): 0.2,  # Compound optimizations
        }
        
        # Calculate synergy for all pairs
        types = [opp.opportunity_type for opp in opportunities]
        
        for i in range(len(types)):
            for j in range(i + 1, len(types)):
                type_pair = tuple(sorted([types[i], types[j]]))
                synergy_bonus += synergy_matrix.get(type_pair, 0.1)  # Default small bonus
        
        # Normalize by number of pairs
        num_pairs = len(opportunities) * (len(opportunities) - 1) // 2
        if num_pairs > 0:
            synergy_bonus /= num_pairs
        
        return min(synergy_bonus, 0.5)  # Cap at 50% bonus
    
    def _generate_composition_strategy(self, opportunities: List[EnhancementOpportunity]) -> str:
        """Generate implementation strategy for compound enhancement"""
        strategies = []
        
        types = [opp.opportunity_type for opp in opportunities]
        type_set = set(types)
        
        if 'performance' in type_set and 'feature' in type_set:
            strategies.append("Performance-first approach: optimize core algorithms then add features")
        elif 'ui_enhancement' in type_set and 'feature' in type_set:
            strategies.append("User-centered design: implement features with enhanced UX from start")
        elif 'ai_enhancement' in type_set:
            strategies.append("AI-native implementation: design with AI capabilities as core architecture")
        elif len(type_set) == 1:
            strategies.append(f"Compound {list(type_set)[0]} implementation with unified architecture")
        else:
            strategies.append("Layered implementation: establish foundation then add capabilities")
        
        # Add coordination strategy
        if len(opportunities) > 2:
            strategies.append("Coordinate implementation to maximize synergies and minimize conflicts")
        
        return "; ".join(strategies)
    
    def _identify_compound_benefits(self, opportunities: List[EnhancementOpportunity]) -> List[str]:
        """Identify benefits that emerge from combining enhancements"""
        benefits = []
        
        types = [opp.opportunity_type for opp in opportunities]
        descriptions = [opp.description.lower() for opp in opportunities]
        
        # Cross-type benefit analysis
        if 'performance' in types and 'feature' in types:
            benefits.append("Features that are fast and efficient from day one")
            benefits.append("Reduced need for future performance retrofitting")
        
        if 'ui_enhancement' in types and any('ai' in desc for desc in descriptions):
            benefits.append("AI capabilities with intuitive user interfaces")
            benefits.append("Seamless integration of complex AI into user workflow")
        
        if 'security' in types:
            benefits.append("Security built into core architecture, not bolted on")
            benefits.append("Reduced attack surface through secure design patterns")
        
        # Same-type compound benefits
        if len(set(types)) == 1:
            if types[0] == 'feature':
                benefits.append("Cohesive feature set with unified user experience")
                benefits.append("Shared infrastructure reducing implementation complexity")
            elif types[0] == 'performance':
                benefits.append("Compound performance gains from multiple optimizations")
                benefits.append("Holistic system optimization rather than isolated improvements")
        
        # Generic compound benefits
        benefits.extend([
            "Reduced integration overhead compared to sequential implementation",
            "Opportunity for architectural improvements that benefit all components",
            "Enhanced testing efficiency through unified test strategy"
        ])
        
        return benefits[:5]  # Return top 5 benefits
    
    def generate_compound_enhancement_solution(self, composition: dict, 
                                             research_results: dict = None, 
                                             learned_patterns: List[dict] = None) -> str:
        """Generate solution for compound enhancement"""
        
        component_opportunities = composition.get('component_opportunities', [])
        if not component_opportunities:
            return ""
        
        # Create enhanced prompt for compound solution
        compound_prompt = f"""🔗 COMPOUND ENHANCEMENT ARCHITECT
Advanced Multi-Dimensional Enhancement System

════════════════════════════════════════════════════════════════════

🎯 COMPOUND ENHANCEMENT MISSION:
{composition.get('description', 'Multi-enhancement composition')}

📊 COMPOSITION ANALYSIS:
• Component Count: {len(component_opportunities)}
• Compound Impact Score: {composition.get('compound_impact_score', 0):.2f}
• Synergy Potential: {composition.get('synergy_potential', 0):.1%}
• Complexity Multiplier: {composition.get('complexity_multiplier', 1):.2f}

🧩 COMPONENT ENHANCEMENTS:
"""
        
        for i, comp_opp in enumerate(component_opportunities, 1):
            compound_prompt += f"""
{i}. **{comp_opp.get('opportunity_type', 'Enhancement').title()}**: {comp_opp.get('description', 'Component enhancement')}
   • Impact: {comp_opp.get('impact_score', 0):.2f} | Complexity: {comp_opp.get('complexity_score', 0):.2f}
   • Priority: {comp_opp.get('priority_score', 0):.2f}
"""
        
        compound_prompt += f"""
🚀 IMPLEMENTATION STRATEGY:
{composition.get('implementation_strategy', 'Unified compound implementation')}

🎁 EXPECTED COMPOUND BENEFITS:
"""
        
        for benefit in composition.get('expected_benefits', []):
            compound_prompt += f"• {benefit}\n"
        
        # Add research insights if available
        if research_results:
            compound_prompt += f"""
🔬 RESEARCH-DRIVEN INSIGHTS:
Research Confidence: {research_results.get('research_confidence', 0):.1%}
• Integration strategies from successful compound implementations
• Best practices for managing multi-dimensional enhancements
• Performance optimization techniques for compound solutions
"""
        
        # Add learned patterns if available
        if learned_patterns:
            compound_prompt += """
🧠 LEARNED PATTERN INSIGHTS:
Based on successful past compound enhancements:
"""
            for pattern in learned_patterns[:2]:
                compound_prompt += f"• {pattern.get('implementation_strategy', 'Pattern strategy')}\n"
        
        compound_prompt += f"""
🔧 COMPOUND IMPLEMENTATION REQUIREMENTS:
1. **UNIFIED ARCHITECTURE**: Design single coherent system, not separate components
2. **SYNERGY MAXIMIZATION**: Leverage interactions between enhancements for emergent benefits
3. **COMPLEXITY MANAGEMENT**: Use sophisticated patterns to manage increased complexity
4. **INCREMENTAL VALIDATION**: Validate each component while ensuring compound functionality
5. **FUTURE EXTENSIBILITY**: Design for easy addition of more enhancements
6. **PERFORMANCE OPTIMIZATION**: Ensure compound enhancement doesn't sacrifice performance
7. **MAINTAINABILITY**: Create clean, documented code despite increased complexity

💡 COMPOUND ENHANCEMENT PHILOSOPHY:
- The whole is greater than the sum of its parts
- Design for synergies, not just feature addition
- Create emergent capabilities through thoughtful combination
- Build compound intelligence into the architecture
- Anticipate how this compound enhancement enables future compounds

🎯 DELIVERABLE:
Provide a complete, immediately implementable compound enhancement that demonstrates clear synergies between components and delivers exponential value over individual enhancements.

════════════════════════════════════════════════════════════════════
BEGIN COMPOUND IMPLEMENTATION:"""
        
        return compound_prompt
    
    def record_composition_success(self, composition: dict, solution: str, 
                                 impact_metrics: dict):
        """Record successful composition for future learning"""
        try:
            composition_record = {
                'composition_id': composition.get('composition_id'),
                'timestamp': datetime.now().isoformat(),
                'description': composition.get('description'),
                'component_count': len(composition.get('component_opportunities', [])),
                'compound_impact_score': composition.get('compound_impact_score'),
                'actual_impact_score': impact_metrics.get('overall_impact_score', 0),
                'synergy_realized': impact_metrics.get('overall_impact_score', 0) / max(composition.get('compound_impact_score', 1), 0.1),
                'solution_summary': solution[:500] + "..." if len(solution) > 500 else solution,
                'success': impact_metrics.get('overall_impact_score', 0) > 0.6
            }
            
            self.composition_history.append(composition_record)
            
            # Store in memory
            self.memory.store_context(
                f"compound_enhancement_{composition.get('composition_id')}",
                composition_record,
                metadata={
                    'type': 'compound_enhancement',
                    'composition_id': composition.get('composition_id'),
                    'success': composition_record['success'],
                    'timestamp': composition_record['timestamp']
                }
            )
            
            # Update synergy patterns
            if composition_record['success']:
                self._update_synergy_patterns(composition, impact_metrics)
            
        except Exception as e:
            logging.error(f"Failed to record composition success: {e}")
    
    def _update_synergy_patterns(self, composition: dict, impact_metrics: dict):
        """Update synergy patterns based on successful compositions"""
        try:
            component_types = [comp.get('opportunity_type') for comp in composition.get('component_opportunities', [])]
            type_signature = tuple(sorted(component_types))
            
            if type_signature not in self.synergy_patterns:
                self.synergy_patterns[type_signature] = {
                    'success_count': 0,
                    'total_attempts': 0,
                    'average_impact': 0.0,
                    'best_impact': 0.0
                }
            
            pattern = self.synergy_patterns[type_signature]
            pattern['total_attempts'] += 1
            
            impact_score = impact_metrics.get('overall_impact_score', 0)
            if impact_score > 0.6:
                pattern['success_count'] += 1
                pattern['best_impact'] = max(pattern['best_impact'], impact_score)
                
                # Update running average
                current_avg = pattern['average_impact']
                pattern['average_impact'] = (current_avg * (pattern['success_count'] - 1) + impact_score) / pattern['success_count']
            
        except Exception as e:
            logging.error(f"Failed to update synergy patterns: {e}")

class EnhancementQualityAssessment:
    """System for evaluating and validating enhancement quality"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.validation_results = {}
        
    def assess_enhancement_quality(self, opportunity: EnhancementOpportunity, 
                                 proposed_solution: str) -> dict:
        """Assess the quality and viability of a proposed enhancement"""
        assessment = {
            'quality_score': 0.0,
            'viability_score': 0.0,
            'risk_score': 0.0,
            'recommendation': 'reject',
            'reasons': []
        }
        
        # Analyze solution quality
        quality_factors = self._analyze_solution_quality(proposed_solution)
        assessment['quality_score'] = quality_factors['score']
        assessment['reasons'].extend(quality_factors['reasons'])
        
        # Assess implementation viability
        viability_factors = self._assess_viability(opportunity, proposed_solution)
        assessment['viability_score'] = viability_factors['score']
        assessment['reasons'].extend(viability_factors['reasons'])
        
        # Calculate risk factors
        risk_factors = self._calculate_risk(opportunity, proposed_solution)
        assessment['risk_score'] = risk_factors['score']
        assessment['reasons'].extend(risk_factors['reasons'])
        
        # Make final recommendation
        overall_score = (assessment['quality_score'] * 0.4 + 
                        assessment['viability_score'] * 0.4 - 
                        assessment['risk_score'] * 0.2)
        
        if overall_score >= 0.7:
            assessment['recommendation'] = 'approve'
        elif overall_score >= 0.5:
            assessment['recommendation'] = 'conditional'
        else:
            assessment['recommendation'] = 'reject'
            
        return assessment
    
    def _analyze_solution_quality(self, solution: str) -> dict:
        """Advanced analysis of solution quality with sophisticated metrics"""
        score = 0.0
        reasons = []
        
        # Comprehensive solution analysis
        solution_metrics = self._calculate_solution_metrics(solution)
        score += solution_metrics['comprehensiveness_score'] * 0.25
        reasons.extend(solution_metrics['reasons'])
        
        # Code quality analysis
        quality_metrics = self._analyze_code_quality_indicators(solution)
        score += quality_metrics['quality_score'] * 0.35
        reasons.extend(quality_metrics['reasons'])
        
        # Best practices adherence
        practices_score = self._analyze_best_practices(solution)
        score += practices_score['practices_score'] * 0.25
        reasons.extend(practices_score['reasons'])
        
        # Innovation and sophistication analysis
        innovation_score = self._analyze_innovation_level(solution)
        score += innovation_score['innovation_score'] * 0.15
        reasons.extend(innovation_score['reasons'])
        
        return {'score': min(score, 1.0), 'reasons': reasons}
    
    def _calculate_solution_metrics(self, solution: str) -> dict:
        """Calculate comprehensive solution metrics"""
        score = 0.0
        reasons = []
        
        # Length and depth analysis
        if len(solution) > 1000:
            score += 0.4
            reasons.append("Comprehensive and detailed solution")
        elif len(solution) > 500:
            score += 0.2
            reasons.append("Adequate solution length")
        
        # Structural analysis
        lines = solution.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) > 20:
            score += 0.3
            reasons.append("Well-structured multi-component solution")
        
        # Comment and documentation density
        comment_lines = [line for line in lines if line.strip().startswith('#') or '"""' in line]
        if len(comment_lines) / max(len(non_empty_lines), 1) > 0.1:
            score += 0.3
            reasons.append("Well-documented with good comment density")
        
        return {'comprehensiveness_score': min(score, 1.0), 'reasons': reasons}
    
    def _analyze_code_quality_indicators(self, solution: str) -> dict:
        """Analyze advanced code quality indicators"""
        score = 0.0
        reasons = []
        
        # Advanced quality patterns
        advanced_patterns = [
            (r'def\s+\w+\([^)]*\)\s*->', 'Uses type annotations for return types', 0.15),
            (r'class\s+\w+.*:', 'Implements object-oriented design', 0.1),
            (r'""".*?"""', 'Contains comprehensive docstrings', 0.15),
            (r'try:.*?except.*?:', 'Includes robust error handling', 0.1),
            (r'logging\.\w+\(', 'Implements proper logging', 0.1),
            (r'async\s+def|await\s+', 'Uses modern async/await patterns', 0.15),
            (r'with\s+.*:', 'Uses context managers', 0.1),
            (r'@\w+', 'Uses decorators for clean code', 0.1),
            (r'if\s+__name__\s*==\s*["\']__main__["\']:', 'Follows proper module structure', 0.05),
        ]
        
        for pattern, description, weight in advanced_patterns:
            if re.search(pattern, solution, re.MULTILINE | re.DOTALL):
                score += weight
                reasons.append(description)
        
        # Code organization analysis
        if solution.count('class ') > 1:
            score += 0.1
            reasons.append("Multiple classes indicating good organization")
        
        if solution.count('def ') > 3:
            score += 0.1
            reasons.append("Multiple functions showing modular design")
        
        return {'quality_score': min(score, 1.0), 'reasons': reasons}
    
    def _analyze_best_practices(self, solution: str) -> dict:
        """Analyze adherence to best practices"""
        score = 0.0
        reasons = []
        
        # Modern Python practices
        modern_practices = [
            ('pathlib', 'Uses modern pathlib for file operations', 0.1),
            ('dataclass', 'Uses dataclasses for clean data structures', 0.1),
            ('typing.', 'Implements comprehensive type hints', 0.15),
            ('contextlib', 'Uses context management utilities', 0.1),
            ('functools', 'Uses functional programming utilities', 0.1),
            ('collections.', 'Uses appropriate collection types', 0.1),
            ('enum.', 'Uses enums for constants', 0.1),
            ('abc.', 'Uses abstract base classes', 0.1),
        ]
        
        for practice, description, weight in modern_practices:
            if practice in solution.lower():
                score += weight
                reasons.append(description)
        
        # Security and robustness practices
        security_practices = [
            ('validate', 'Includes input validation', 0.1),
            ('sanitize', 'Includes data sanitization', 0.1),
            ('hash', 'Uses secure hashing', 0.05),
            ('secret', 'Handles secrets securely', 0.1),
        ]
        
        for practice, description, weight in security_practices:
            if practice in solution.lower():
                score += weight
                reasons.append(description)
        
        return {'practices_score': min(score, 1.0), 'reasons': reasons}
    
    def _analyze_innovation_level(self, solution: str) -> dict:
        """Analyze innovation and sophistication level"""
        score = 0.0
        reasons = []
        
        # Innovation indicators
        innovation_patterns = [
            ('machine learning|ml|ai', 'Incorporates AI/ML capabilities', 0.3),
            ('algorithm.*optim', 'Includes algorithmic optimizations', 0.2),
            ('parallel|concurrent|threading', 'Uses advanced concurrency', 0.2),
            ('cache|memoiz', 'Implements intelligent caching', 0.15),
            ('pattern.*match|match.*case', 'Uses modern pattern matching', 0.1),
            ('generator|yield', 'Uses memory-efficient generators', 0.1),
            ('metaclass', 'Uses advanced metaclass programming', 0.2),
            ('plugin|extension', 'Implements extensible architecture', 0.25),
        ]
        
        for pattern, description, weight in innovation_patterns:
            if re.search(pattern, solution.lower()):
                score += weight
                reasons.append(description)
        
        return {'innovation_score': min(score, 1.0), 'reasons': reasons}
    
    def _assess_viability(self, opportunity: EnhancementOpportunity, solution: str) -> dict:
        """Assess implementation viability"""
        score = 0.5  # Base score
        reasons = []
        
        # Check alignment with opportunity type
        if opportunity.opportunity_type in solution.lower():
            score += 0.2
            reasons.append("Solution aligns with opportunity type")
        
        # Check for realistic scope
        if opportunity.complexity_score < 0.5 and len(solution) < 2000:
            score += 0.2
            reasons.append("Appropriate scope for complexity")
        elif opportunity.complexity_score >= 0.5 and len(solution) > 1000:
            score += 0.2
            reasons.append("Comprehensive solution for complex problem")
        
        # Check for implementation details
        if 'import' in solution or 'from ' in solution:
            score += 0.1
            reasons.append("Includes necessary imports")
        
        return {'score': min(score, 1.0), 'reasons': reasons}
    
    def _calculate_risk(self, opportunity: EnhancementOpportunity, solution: str) -> dict:
        """Calculate implementation risk factors"""
        risk_score = 0.0
        reasons = []
        
        # High-risk patterns
        high_risk_patterns = [
            ('os.system', 'Uses system commands'),
            ('subprocess', 'Uses subprocess calls'),
            ('eval(', 'Uses eval()'),
            ('exec(', 'Uses exec()'),
            ('__import__', 'Uses dynamic imports'),
        ]
        
        for pattern, description in high_risk_patterns:
            if pattern in solution:
                risk_score += 0.3
                reasons.append(f"High risk: {description}")
        
        # Moderate risk patterns
        moderate_risk_patterns = [
            ('threading', 'Uses threading'),
            ('global ', 'Uses global variables'),
            ('del ', 'Explicit deletion'),
        ]
        
        for pattern, description in moderate_risk_patterns:
            if pattern in solution:
                risk_score += 0.1
                reasons.append(f"Moderate risk: {description}")
        
        return {'score': min(risk_score, 1.0), 'reasons': reasons}

class TaskProcessor:
    """Core task processing engine with autonomous capabilities"""
    def __init__(self, config: AIConfig, memory: MemoryManager, output_dir: Path, monitor: Optional['SystemMonitor'] = None, metrics_callback: Optional[callable] = None):
        self.config = config
        self.memory = memory
        self.output_dir = output_dir
        self.monitor = monitor
        self.metrics_callback = metrics_callback
        
        # Create essential output directories
        self._create_output_directories()
        
        # Initialize with self reference for task-specific prompts (will be set after initialization)
        self.claude = None
        self.ollama = None
        
        # Initialize activity logger
        self.activity_logger = get_activity_logger()
        
        # Add stop flag for interrupting long-running operations
        self.stop_requested = False
        
        # Initialize task intelligence for autonomous decision-making
        self.task_intelligence = TaskIntelligence()
        self.response_analyzer = ResponseAnalyzer()
        
        # Initialize new autonomous continuation engine
        try:
            from src.autonomous.autonomous_continuation_engine import AutonomousContinuationEngine
            self.autonomous_continuation_engine = AutonomousContinuationEngine()
            logging.info("Autonomous continuation engine initialized successfully")
        except ImportError as e:
            logging.warning(f"Could not import autonomous continuation engine: {e}")
            self.autonomous_continuation_engine = None
        
        # Initialize AI managers with monitor and self reference for task-specific prompts
        self.claude = ClaudeManager(config, monitor=monitor, task_processor=self)
        self.ollama = OllamaManager(config, monitor=monitor, task_processor=self)
        
        # Initialize autonomous agent if available
        self.autonomous_agent = None
        self.workflow_manager = None
        if AUTONOMOUS_AVAILABLE:
            self.setup_autonomous_capabilities()
    
    def _create_output_directories(self):
        """Create essential output directories"""
        try:
            # Create main output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create data directory for memory and other data
            data_dir = self.output_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create logs directory
            logs_dir = self.output_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Create autonomous directory for autonomous mode outputs
            autonomous_dir = self.output_dir / "autonomous"
            autonomous_dir.mkdir(parents=True, exist_ok=True)
            
            logging.debug(f"Created output directories in {self.output_dir}")
            
        except Exception as e:
            logging.error(f"Failed to create output directories: {e}")
    
    def request_stop(self):
        """Request immediate stop of all operations"""
        self.stop_requested = True
        log_activity(
            ActivityType.USER_INTERACTION,
            ActivityLevel.INFO,
            "Stop Requested",
            "User requested immediate stop of all operations",
            {"timestamp": time.time()}
        )
    
    def query_ai_with_primary_fallback(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Query AI based on primary model setting with fallback to backup model"""
        primary_is_claude = self.config.primary_model == "Claude API (Recommended)"
        
        if primary_is_claude:
            # Claude is primary, Ollama is backup
            response = self.claude.query(prompt, system_prompt)
            if not response:
                logging.info("Claude (primary) failed, falling back to Ollama (backup)")
                response = self.ollama.query(prompt)
        else:
            # Ollama is primary, Claude is backup
            response = self.ollama.query(prompt)
            if not response:
                logging.info("Ollama (primary) failed, falling back to Claude (backup)")
                response = self.claude.query(prompt, system_prompt)
        
        return response
    
    def reset_stop_flag(self):
        """Reset the stop flag for new operations"""
        self.stop_requested = False
    
    def setup_autonomous_capabilities(self):
        """Initialize autonomous agent and workflow manager"""
        try:
            autonomous_config = {
                "model": "gpt-4-vision-preview",
                "api_key": self.config.claude_api_key,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            self.autonomous_agent = AutonomousAgent(autonomous_config)
            self.workflow_manager = AutonomousWorkflowManager(self.autonomous_agent)
            
            logging.info("Autonomous capabilities initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize autonomous capabilities: {e}")
            self.autonomous_agent = None
            self.workflow_manager = None
    
    def classify_task(self, prompt: str) -> Tuple[str, float]:
        classification_prompt = f"""
Classify this task into one of these categories: {', '.join(TASK_TYPES)}

Task: "{prompt}"

Categories:
- code: Programming, scripting, software development
- multimedia: Image/video/audio processing, generation
- rag: Document analysis, question answering, summarization
- automation: System tasks, file operations, scheduling
- analytics: Data analysis, statistics, charts

Respond with just the category name and confidence (0-1), separated by comma.
Example: code,0.9
"""
        response = self.query_ai_with_primary_fallback(classification_prompt)
        if response:
            try:
                parts = response.strip().split(',')
                task_type = parts[0].strip().lower()
                confidence = float(parts[1].strip()) if len(parts) > 1 else 0.5
                if task_type in TASK_TYPES:
                    return task_type, confidence
            except Exception as e:
                logging.error(f"Task classification parsing failed: {e}")
        return "code", 0.5

    def detect_question(self, text: str) -> bool:
        """Detect if the AI response contains a question"""
        # Common question patterns
        question_patterns = [
            r'\?$',  # Ends with question mark
            r'(?i)\b(should\s+I|would\s+you\s+like|do\s+you\s+want|shall\s+I|can\s+I|may\s+I)\b.*\?',
            r'(?i)\b(what|when|where|why|how|which|who)\b.*\?',
            r'(?i)\b(is\s+it|are\s+you|do\s+you|does\s+it|have\s+you|has\s+it)\b.*\?',
            r'(?i)\b(continue|proceed|go\s+ahead|ready\s+to|shall\s+we)\b.*\?',
        ]
        
        # Check last few sentences for questions
        sentences = text.strip().split('.')
        last_content = '. '.join(sentences[-3:]) if len(sentences) > 3 else text
        
        for pattern in question_patterns:
            if re.search(pattern, last_content, re.MULTILINE):
                return True
        
        return False
    
    def execute_code_task(self, prompt: str, files: List[str]) -> TaskResult:
        task_steps = ["Executing code task"]
        enhanced_prompt = prompt
        if files:
            file_contents = []
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:2000]
                        file_contents.append(f"File {Path(file_path).name}:\n{content}")
                except Exception as e:
                    logging.error(f"Failed to read file {file_path}: {e}")
            if file_contents:
                enhanced_prompt += f"\n\nFile contents:\n" + "\n\n".join(file_contents)
        
        response = self.query_ai_with_primary_fallback(enhanced_prompt, "You are a helpful coding assistant. Generate clean, working code.")
        if not response:
            return TaskResult(False, "Failed to get AI response", [], task_steps)
        
        task_steps.append("Generated code response")
        generated_files = []
        code_blocks = self.extract_code_blocks(response)
        file_metadata = {}
        
        for i, (language, code) in enumerate(code_blocks):
            if code.strip():
                # Generate descriptive filename with better naming
                purpose = self._extract_code_purpose_from_prompt(prompt)
                filename = self.generate_descriptive_filename("code", language, purpose)
                file_path = self.output_dir / filename
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(code)
                    
                    # Create metadata for this file
                    metadata = self.create_file_metadata(
                        str(file_path), "code", language, code, purpose
                    )
                    file_metadata[str(file_path)] = metadata
                    
                    generated_files.append(str(file_path))
                    task_steps.append(f"Saved {metadata.display_name} to {filename}")
                except Exception as e:
                    logging.error(f"Failed to save code to {file_path}: {e}")
        
        result = TaskResult(True, response, generated_files, task_steps, score=0.8)
        result.file_metadata = file_metadata
        return result
    
    def execute_multimedia_task(self, prompt: str, files: List[str]) -> TaskResult:
        task_steps = ["Executing multimedia task"]
        file_metadata = {}
        generated_files = []
        
        if files and any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) for f in files):
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            for image_path in image_files:
                response = self.claude.query_with_image(prompt, image_path)
                if response:
                    task_steps.append(f"Analyzed image: {Path(image_path).name}")
                    
                    # Generate descriptive filename and save analysis
                    purpose = "Image Analysis"
                    filename = self.generate_descriptive_filename("multimedia", purpose=purpose)
                    result_file = self.output_dir / filename
                    
                    try:
                        analysis_content = f"Image Analysis Report\n{'='*50}\n\nImage: {Path(image_path).name}\nQuery: {prompt}\n\nAnalysis:\n{response}"
                        with open(result_file, 'w', encoding='utf-8') as f:
                            f.write(analysis_content)
                        
                        # Create metadata
                        metadata = self.create_file_metadata(
                            str(result_file), "multimedia", "text", analysis_content, purpose
                        )
                        file_metadata[str(result_file)] = metadata
                        generated_files.append(str(result_file))
                        task_steps.append(f"Saved {metadata.display_name} to {filename}")
                        
                        result = TaskResult(True, response, generated_files, task_steps, score=0.9)
                        result.file_metadata = file_metadata
                        return result
                    except Exception as e:
                        logging.error(f"Failed to save multimedia analysis: {e}")
                        return TaskResult(True, response, [], task_steps, score=0.9)
        
        multimedia_prompt = f"""
{prompt}

Please provide a detailed response for this multimedia task. If this involves:
- Image generation: Describe the image concept in detail
- Audio processing: Explain the processing steps
- Video editing: Outline the editing workflow
"""
        response = self.query_ai_with_primary_fallback(multimedia_prompt)
        if response:
            task_steps.append("Generated multimedia response")
            return TaskResult(True, response, [], task_steps, score=0.7)
        return TaskResult(False, "Failed to process multimedia task", [], task_steps)
    
    def execute_rag_task(self, prompt: str, files: List[str]) -> TaskResult:
        task_steps = ["Executing RAG task"]
        document_content = []
        if files:
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        document_content.append(f"Document {Path(file_path).name}:\n{content}")
                        task_steps.append(f"Loaded document: {Path(file_path).name}")
                except Exception as e:
                    logging.error(f"Failed to read document {file_path}: {e}")
        
        rag_prompt = f"""
{prompt}

Based on the following documents:
{chr(10).join(document_content)}

Please analyze the documents and provide a comprehensive answer to the question/task.
"""
        response = self.query_ai_with_primary_fallback(rag_prompt)
        if response:
            task_steps.append("Generated RAG response")
            
            # Generate descriptive filename and metadata
            purpose = self._extract_rag_purpose_from_prompt(prompt)
            filename = self.generate_descriptive_filename("rag", purpose=purpose)
            result_file = self.output_dir / filename
            file_metadata = {}
            
            try:
                analysis_content = f"RAG Analysis\n{'='*50}\n\nQuery: {prompt}\n\nResponse:\n{response}"
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write(analysis_content)
                
                # Create metadata
                metadata = self.create_file_metadata(
                    str(result_file), "rag", "text", analysis_content, purpose
                )
                file_metadata[str(result_file)] = metadata
                
                task_steps.append(f"Saved {metadata.display_name} to {filename}")
                result = TaskResult(True, response, [str(result_file)], task_steps, score=0.85)
                result.file_metadata = file_metadata
                return result
            except Exception as e:
                logging.error(f"Failed to save RAG result: {e}")
                return TaskResult(True, response, [], task_steps, score=0.8)
        return TaskResult(False, "Failed to process RAG task", [], task_steps)
    
    def execute_automation_task(self, prompt: str, files: List[str]) -> TaskResult:
        task_steps = ["Executing automation task"]
        automation_prompt = f"""
{prompt}

Please provide automation scripts or commands for this task. Focus on:
- macOS compatibility
- Safe file operations
- Clear step-by-step instructions
- Error handling

Generate practical, executable automation solutions.
"""
        response = self.query_ai_with_primary_fallback(automation_prompt)
        if response:
            task_steps.append("Generated automation response")
            
            # Generate descriptive filename and metadata
            purpose = self._extract_automation_purpose_from_prompt(prompt)
            filename = self.generate_descriptive_filename("automation", purpose=purpose)
            script_file = self.output_dir / filename
            file_metadata = {}
            
            try:
                shell_commands = self.extract_shell_commands(response)
                if shell_commands:
                    with open(script_file, 'w', encoding='utf-8') as f:
                        f.write("#!/bin/bash\n")
                        f.write("# SuperMini Generated Automation Script\n\n")
                        f.write(shell_commands)
                    os.chmod(script_file, 0o755)
                    
                    # Create metadata
                    metadata = self.create_file_metadata(
                        str(script_file), "automation", "bash", shell_commands, purpose
                    )
                    file_metadata[str(script_file)] = metadata
                    
                    task_steps.append(f"Saved {metadata.display_name} to {filename}")
                    result = TaskResult(True, response, [str(script_file)], task_steps, score=0.8)
                    result.file_metadata = file_metadata
                    return result
            except Exception as e:
                logging.error(f"Failed to save automation script: {e}")
            return TaskResult(True, response, [], task_steps, score=0.7)
        return TaskResult(False, "Failed to process automation task", [], task_steps)
    
    def execute_analytics_task(self, prompt: str, files: List[str]) -> TaskResult:
        task_steps = ["Executing analytics task"]
        data_info = []
        if files:
            for file_path in files:
                if file_path.lower().endswith('.csv'):
                    try:
                        df = pd.read_csv(file_path)
                        info = f"CSV {Path(file_path).name}: {df.shape[0]} rows, {df.shape[1]} columns\nColumns: {', '.join(df.columns.tolist())}"
                        data_info.append(info)
                        task_steps.append(f"Analyzed CSV: {Path(file_path).name}")
                    except Exception as e:
                        logging.error(f"Failed to analyze CSV {file_path}: {e}")
        
        analytics_prompt = f"""
{prompt}

Data files information:
{chr(10).join(data_info)}

Please provide:
1. Data analysis insights
2. Python code for analysis (if applicable)
3. Visualization recommendations
4. Key findings and conclusions
"""
        response = self.query_ai_with_primary_fallback(analytics_prompt)
        if response:
            task_steps.append("Generated analytics response")
            
            # Generate descriptive filenames and metadata
            purpose = self._extract_analytics_purpose_from_prompt(prompt)
            generated_files = []
            file_metadata = {}
            
            # Save analysis report
            report_filename = self.generate_descriptive_filename("analytics", purpose=f"{purpose} Report" if purpose else "Analytics Report")
            analysis_file = self.output_dir / report_filename
            
            try:
                report_content = f"Analytics Report\n{'='*50}\n\nQuery: {prompt}\n\nAnalysis:\n{response}"
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                # Create metadata for report
                report_metadata = self.create_file_metadata(
                    str(analysis_file), "analytics", "text", report_content, f"{purpose} Report" if purpose else "Analytics Report"
                )
                file_metadata[str(analysis_file)] = report_metadata
                generated_files.append(str(analysis_file))
                task_steps.append(f"Saved {report_metadata.display_name} to {report_filename}")
                
                # Extract and save Python code blocks
                code_blocks = self.extract_code_blocks(response)
                for i, (language, code) in enumerate(code_blocks):
                    if language.lower() == 'python' and code.strip():
                        code_filename = self.generate_descriptive_filename("analytics", "python", f"{purpose} Code" if purpose else "Analytics Code")
                        code_file = self.output_dir / code_filename
                        
                        with open(code_file, 'w', encoding='utf-8') as f:
                            f.write(code)
                        
                        # Create metadata for code
                        code_metadata = self.create_file_metadata(
                            str(code_file), "analytics", "python", code, f"{purpose} Code" if purpose else "Analytics Code"
                        )
                        file_metadata[str(code_file)] = code_metadata
                        generated_files.append(str(code_file))
                        task_steps.append(f"Saved {code_metadata.display_name} to {code_filename}")
                
                result = TaskResult(True, response, generated_files, task_steps, score=0.9)
                result.file_metadata = file_metadata
                return result
            except Exception as e:
                logging.error(f"Failed to save analytics result: {e}")
                return TaskResult(True, response, [], task_steps, score=0.8)
        return TaskResult(False, "Failed to process analytics task", [], task_steps)
    
    def execute_autonomous_task(self, prompt: str, files: List[str], task_type: str = None) -> TaskResult:
        """Execute a task with autonomous capabilities"""
        if not self.autonomous_agent:
            return TaskResult(
                False, 
                "Autonomous capabilities not available. Install gui-agents for full functionality.", 
                [], 
                ["Autonomous execution attempted but not available"]
            )
        
        try:
            # Create autonomous task
            context = {
                "files": files,
                "task_type": task_type,
                "output_dir": str(self.output_dir)
            }
            
            autonomous_task = self.autonomous_agent.create_workflow_task(
                description=prompt,
                task_type=task_type or "general",
                context=context
            )
            
            # Execute autonomous task
            result = self.autonomous_agent.execute_autonomous_task(autonomous_task)
            
            if result.success:
                return TaskResult(
                    True,
                    f"Autonomous task completed successfully. Steps taken: {len(result.steps_taken)}",
                    result.screenshots or [],
                    [f"Step {i+1}: {step.get('details', step.get('action', 'Unknown'))}" 
                     for i, step in enumerate(result.steps_taken)],
                    score=0.9,
                    execution_time=result.execution_time
                )
            else:
                return TaskResult(
                    False,
                    f"Autonomous task failed: {result.error_message}",
                    result.screenshots or [],
                    [f"Step {i+1}: {step.get('details', step.get('action', 'Unknown'))}" 
                     for i, step in enumerate(result.steps_taken)]
                )
                
        except Exception as e:
            logging.error(f"Autonomous task execution error: {e}")
            return TaskResult(
                False,
                f"Autonomous execution error: {str(e)}",
                [],
                ["Autonomous task execution failed"]
            )
    
    def suggest_autonomous_actions(self, prompt: str, files: List[str], task_type: str = None) -> List[str]:
        """Suggest autonomous actions for the current context"""
        if not self.autonomous_agent:
            return ["Autonomous suggestions not available - install gui-agents"]
        
        context = {
            "prompt": prompt,
            "files": files,
            "task_type": task_type
        }
        
        return self.autonomous_agent.suggest_autonomous_actions(context)
    
    def process_task(self, prompt: str, files: List[str], task_type: str = None, use_memory: bool = True, auto_continue: bool = False, max_continues: int = 10, autonomous_mode: bool = False) -> TaskResult:
        """Main task processing method with auto-continue support"""
        start_time = time.time()
        task_id = f"task_{int(time.time() * 1000000)}"
        
        # Log task start
        log_activity(
            ActivityType.TASK_START,
            ActivityLevel.INFO,
            "Task Processing Started",
            f"Starting task: {prompt[:100]}{'...' if len(prompt) > 100 else ''}",
            {
                "task_id": task_id,
                "task_type": task_type,
                "files": files,
                "autonomous_mode": autonomous_mode,
                "auto_continue": auto_continue,
                "use_memory": use_memory
            }
        )
        
        # Auto-classify if no task type specified
        if not task_type:
            task_type, confidence = self.classify_task(prompt)
            logging.info(f"Auto-classified task as '{task_type}' with confidence {confidence:.2f}")
            
            log_activity(
                ActivityType.AI_RESPONSE,
                ActivityLevel.DEBUG,
                "Task Classification",
                f"Auto-classified as '{task_type}' with {confidence:.2f} confidence",
                {"task_type": task_type, "confidence": confidence, "task_id": task_id}
            )
        
        # Update task type stats
        if hasattr(self, 'monitor') and self.monitor and task_type:
            self.monitor.update_stats('task_types', task_type)

        # Retrieve memory context if enabled
        memory_context = ""
        if use_memory:
            memory_context = self.memory.retrieve_context(prompt, task_type)
        
        # Apply autonomous intelligence for optimal parameters
        context_info = {
            'retry_count': 0,
            'previous_success': True,
            'memory_context': memory_context
        }
        
        # Determine optimal temperature based on task type and context
        optimal_temperature = self.task_intelligence.determine_optimal_temperature(
            prompt, task_type, context_info
        )
        
        # Calculate intelligent auto-continue parameters
        complexity_score = self.task_intelligence._analyze_prompt_complexity(prompt)
        optimal_max_continues = self.task_intelligence.calculate_max_iterations(
            task_type, complexity_score, len(prompt)
        )
        
        # Override user settings with intelligent defaults
        if auto_continue:
            max_continues = optimal_max_continues
        else:
            # Always enable auto-continue with intelligent limits for better results
            auto_continue = True
            max_continues = min(optimal_max_continues, 3)  # Conservative for manual mode
        
        # Temporarily update config temperature for this task
        original_temperature = self.config.temperature
        self.config.temperature = optimal_temperature
        
        # Get task-specific optimized prompts
        task_prompts = self.task_intelligence.get_task_specific_prompts(task_type)
        self.current_task_prompts = task_prompts  # Make available to AI managers
        
        logging.info(f"Autonomous settings - Temperature: {optimal_temperature}, Max continues: {max_continues}, Task: {task_type}")
        
        # Check if autonomous mode is requested
        if autonomous_mode and self.autonomous_agent:
            logging.info("Executing task in autonomous mode")
            return self.execute_autonomous_task(prompt, files, task_type)
        
        # Execute task based on type
        if task_type == "code":
            result = self.execute_code_task(prompt, files)
        elif task_type == "multimedia":
            result = self.execute_multimedia_task(prompt, files)
        elif task_type == "rag":
            result = self.execute_rag_task(prompt, files)
        elif task_type == "automation":
            result = self.execute_automation_task(prompt, files)
        elif task_type == "analytics":
            result = self.execute_analytics_task(prompt, files)
        else:
            result = self.execute_code_task(prompt, files)  # Default fallback
        
        # Autonomous continuation logic with intelligent enhancement
        if auto_continue and result.success and not self.stop_requested:
            continue_count = 0
            accumulated_result = result.result
            accumulated_files = result.generated_files.copy()
            accumulated_steps = result.task_steps.copy()
            
            # Use new autonomous continuation engine if available
            if self.autonomous_continuation_engine:
                logging.info("Using autonomous continuation engine for intelligent enhancement")
                
                while (continue_count < max_continues and not self.stop_requested):
                    from src.autonomous.autonomous_continuation_engine import ContinuationContext
                    
                    # Create context for autonomous decision
                    context = ContinuationContext(
                        task_type=task_type,
                        original_prompt=prompt,
                        current_response=result.result,
                        iteration_count=continue_count,
                        max_iterations=max_continues,
                        accumulated_results=[accumulated_result],
                        generated_files=accumulated_files,
                        execution_time=time.time() - start_time,
                        quality_scores={'overall': result.score if hasattr(result, 'score') else 0.5},
                        previous_enhancements=[],
                        user_preferences={},
                        model_type="claude" if hasattr(self, 'claude') else "ollama"
                    )
                    
                    # Get autonomous continuation decision
                    continuation_plan = self.autonomous_continuation_engine.should_continue_autonomous(context)
                    
                    if not continuation_plan.should_continue:
                        logging.info(f"Autonomous continuation stopped: {continuation_plan.reasoning}")
                        log_activity(
                            ActivityType.AI_RESPONSE,
                            ActivityLevel.INFO,
                            "Autonomous Continuation Decision",
                            f"Stopping continuation: {continuation_plan.reasoning}",
                            {"continue_count": continue_count, "reasoning": continuation_plan.reasoning, "task_id": task_id}
                        )
                        break
                    
                    continue_count += 1
                    logging.info(f"Autonomous continuation triggered (iteration {continue_count}): {continuation_plan.continuation_type.value}")
                    
                    # Generate intelligent enhancement prompt
                    enhancement_prompt = self.autonomous_continuation_engine.generate_enhancement_prompt(continuation_plan, context)
                    
                    log_activity(
                        ActivityType.TASK_START,
                        ActivityLevel.INFO,
                        f"Autonomous Enhancement {continue_count}",
                        f"Starting autonomous enhancement iteration {continue_count}: {continuation_plan.continuation_type.value}",
                        {
                            "continue_count": continue_count, 
                            "max_continues": max_continues, 
                            "enhancement_type": continuation_plan.continuation_type.value,
                            "confidence": continuation_plan.confidence_score,
                            "expected_improvements": continuation_plan.expected_improvements,
                            "task_id": task_id
                        }
                    )
                    
                    accumulated_steps.append(f"Autonomous enhancement iteration {continue_count}: {continuation_plan.continuation_type.value}")
                    
                    # Check stop flag before processing
                    if self.stop_requested:
                        log_activity(
                            ActivityType.USER_INTERACTION,
                            ActivityLevel.INFO,
                            "Autonomous Enhancement Stopped",
                            f"Autonomous enhancement stopped by user request at iteration {continue_count}",
                            {"continue_count": continue_count, "task_id": task_id}
                        )
                        break
                    
                    # Process autonomous enhancement
                    if task_type == "code":
                        new_result = self.execute_code_task(enhancement_prompt, files + accumulated_files)
                    elif task_type == "multimedia":
                        new_result = self.execute_multimedia_task(enhancement_prompt, files)
                    elif task_type == "rag":
                        new_result = self.execute_rag_task(enhancement_prompt, files)
                    elif task_type == "automation":
                        new_result = self.execute_automation_task(enhancement_prompt, files)
                    elif task_type == "analytics":
                        new_result = self.execute_analytics_task(enhancement_prompt, files)
                    else:
                        new_result = self.execute_code_task(enhancement_prompt, files)
                    
                    # Check stop flag after processing
                    if self.stop_requested:
                        log_activity(
                            ActivityType.USER_INTERACTION,
                            ActivityLevel.INFO,
                            "Task Stopped During Enhancement",
                            f"Task stopped during autonomous enhancement iteration {continue_count}",
                            {"continue_count": continue_count, "task_id": task_id}
                        )
                        break
                    
                    if new_result.success:
                        # Update autonomous engine with results for learning
                        updated_context = ContinuationContext(
                            task_type=task_type,
                            original_prompt=prompt,
                            current_response=new_result.result,
                            iteration_count=continue_count,
                            max_iterations=max_continues,
                            accumulated_results=[accumulated_result],
                            generated_files=accumulated_files + (new_result.generated_files or []),
                            execution_time=time.time() - start_time,
                            quality_scores={'overall': new_result.score if hasattr(new_result, 'score') else 0.5},
                            previous_enhancements=[],
                            user_preferences={},
                            model_type="claude" if hasattr(self, 'claude') else "ollama"
                        )
                        
                        self.autonomous_continuation_engine.update_from_result(
                            continuation_plan, updated_context, new_result.result, new_result.generated_files or []
                        )
                        
                        accumulated_result += f"\n\n--- {continuation_plan.continuation_type.value.title()} Enhancement {continue_count} ---\n\n{new_result.result}"
                        accumulated_files.extend(new_result.generated_files or [])
                        accumulated_steps.extend(new_result.task_steps or [])
                        result = new_result  # Update result for next iteration
                    else:
                        logging.warning(f"Enhancement iteration {continue_count} failed, stopping autonomous continuation")
                        break
                        
            else:
                # Fallback to legacy continuation system
                logging.info("Using legacy continuation system (autonomous engine not available)")
                should_continue = True
                while (continue_count < max_continues and should_continue and not self.stop_requested):
                    
                    # Legacy continuation decision
                    should_continue, reasoning = self.response_analyzer.should_continue(
                        result.result, continue_count, max_continues, task_type, prompt
                    )
                    
                    if not should_continue:
                        logging.info(f"Legacy auto-continue stopped: {reasoning}")
                        break
                    
                    continue_count += 1
                    continue_prompt = f"Previous response:\n{result.result}\n\nContinue with the task. Proceed with any suggestions or next steps you mentioned."
                    
                    # Process legacy continuation
                    if task_type == "code":
                        result = self.execute_code_task(continue_prompt, files + accumulated_files)
                    elif task_type == "multimedia":
                        result = self.execute_multimedia_task(continue_prompt, files)
                    elif task_type == "rag":
                        result = self.execute_rag_task(continue_prompt, files)
                    elif task_type == "automation":
                        result = self.execute_automation_task(continue_prompt, files)
                    elif task_type == "analytics":
                        result = self.execute_analytics_task(continue_prompt, files)
                    else:
                        result = self.execute_code_task(continue_prompt, files)
                    
                    if result.success:
                        accumulated_result += f"\n\n--- Continuation {continue_count} ---\n\n{result.result}"
                        accumulated_files.extend(result.generated_files or [])
                        accumulated_steps.extend(result.task_steps or [])
                    else:
                        break
            
            # Create final result with all continuations/enhancements
            result = TaskResult(
                success=True,
                result=accumulated_result,
                generated_files=accumulated_files,
                task_steps=accumulated_steps,
                score=result.score,
                execution_time=time.time() - start_time
            )
        else:
            # Calculate execution time
            result.execution_time = time.time() - start_time
        
        # Update files generated stats
        if result.success and hasattr(self, 'monitor') and self.monitor:
            self.monitor.update_stats('files_generated', len(result.generated_files))
            self.monitor.update_stats('tasks_completed')
            
            # Log task completion metrics for dashboard
            if hasattr(self.monitor, 'log_task_completed'):
                self.monitor.log_task_completed(total_execution_time, task_type)

        # Log task completion with enhanced details
        total_execution_time = time.time() - start_time
        
        # End task tracking with detailed result info using activity logger
        if hasattr(self, 'activity_logger') and self.activity_logger:
            result_details = {
                "success": result.success,
                "generated_files_count": len(result.generated_files) if result.generated_files else 0,
                "execution_time": total_execution_time,
                "task_type": task_type,
                "autonomous_mode": autonomous_mode,
                "auto_continue": auto_continue,
                "continue_count": continue_count if auto_continue else 0,
                "steps_completed": len(result.task_steps) if result.task_steps else 0,
                "score": result.score,
                "files_generated": [str(f) for f in (result.generated_files or [])]
            }
            
            if not result.success and hasattr(result, 'error'):
                result_details["error"] = str(result.error)
            
            self.activity_logger.end_task(task_id, result.success, result_details)
        
        # Also maintain the original logging for backward compatibility
        log_activity(
            ActivityType.TASK_END,
            ActivityLevel.INFO if result.success else ActivityLevel.ERROR,
            f"Task {'Completed' if result.success else 'Failed'}",
            f"Task execution {'completed successfully' if result.success else 'failed'}: {prompt[:100]}{'...' if len(prompt) > 100 else ''}",
            {
                "task_id": task_id,
                "task_type": task_type,
                "success": result.success,
                "execution_time": total_execution_time,
                "generated_files_count": len(result.generated_files) if result.generated_files else 0,
                "autonomous_mode": autonomous_mode,
                "auto_continue": auto_continue,
                "score": result.score
            },
            duration=total_execution_time
        )
        
        # Save to memory if successful
        if result.success and use_memory:
            task_data = {
                "prompt": prompt,
                "task_type": task_type,
                "result": result.result,
                "files": files,
                "generated_files": result.generated_files,
                "score": result.score,
                "execution_time": result.execution_time,
                "timestamp": time.time()
            }
            self.memory.save_task(task_data)
        
        # Restore original temperature setting
        self.config.temperature = original_temperature
        
        # Update AI metrics dashboard
        if self.metrics_callback:
            # Estimate tokens used (rough approximation)
            estimated_tokens = len(prompt.split()) + len(str(result.result).split()) if result.result else 0
            self.metrics_callback(
                task_type=task_type,
                response_time=total_execution_time,
                tokens_used=estimated_tokens
            )
        
        return result
    
    def _generate_auto_continue_summary(self, iteration: int, accumulated_files: List[str], 
                                      accumulated_steps: List[str], last_result, 
                                      task_type: str, elapsed_time: float) -> str:
        """Generate a concise summary of completed tasks before auto-continue iteration"""
        summary_parts = []
        
        # Basic progress info
        summary_parts.append(f"Auto-Continue Iteration {iteration}")
        summary_parts.append(f"Elapsed: {elapsed_time:.1f}s")
        summary_parts.append(f"Task Type: {task_type}")
        
        # Files generated so far
        if accumulated_files:
            file_count = len(accumulated_files)
            summary_parts.append(f"Files Generated: {file_count}")
            # Show last few files if there are many
            if file_count <= 3:
                file_list = ", ".join([Path(f).name for f in accumulated_files])
                summary_parts.append(f"Files: [{file_list}]")
            else:
                recent_files = ", ".join([Path(f).name for f in accumulated_files[-2:]])
                summary_parts.append(f"Recent Files: [{recent_files}] (+{file_count-2} more)")
        else:
            summary_parts.append("Files Generated: 0")
        
        # Steps completed
        step_count = max(0, len(accumulated_steps) - 1)  # Don't count current iteration step
        if step_count > 0:
            summary_parts.append(f"Steps Completed: {step_count}")
        
        # Last result status
        if last_result:
            if hasattr(last_result, 'success'):
                status = "✅ SUCCESS" if last_result.success else "❌ FAILED"
                summary_parts.append(f"Previous Status: {status}")
            
            if hasattr(last_result, 'score') and last_result.score:
                summary_parts.append(f"Quality Score: {last_result.score:.2f}")
        
        # Task progress indicator
        progress_indicator = "🔄 CONTINUING"
        summary_parts.append(progress_indicator)
        
        return " | ".join(summary_parts)
    
    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        for language, code in matches:
            if not language:
                language = "text"
            code_blocks.append((language, code.strip()))
        return code_blocks
    
    def extract_shell_commands(self, text: str) -> str:
        code_blocks = self.extract_code_blocks(text)
        for language, code in code_blocks:
            if language.lower() in ['bash', 'shell', 'sh']:
                return code
        lines = text.split('\n')
        commands = []
        for line in lines:
            line = line.strip()
            if line.startswith('$ ') or line.startswith('sudo ') or line.startswith('brew ') or line.startswith('cp ') or line.startswith('mv '):
                commands.append(line[2:] if line.startswith('$ ') else line)
        return '\n'.join(commands) if commands else ""
    
    def get_file_extension(self, language: str) -> str:
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'html': 'html',
            'css': 'css',
            'bash': 'sh',
            'shell': 'sh',
            'sql': 'sql',
            'json': 'json',
            'yaml': 'yml',
            'xml': 'xml'
        }
        return extensions.get(language.lower(), 'txt')
    
    def generate_descriptive_filename(self, task_type: str, language: str = None, purpose: str = None) -> str:
        """Generate a descriptive filename based on task type and content"""
        timestamp = int(time.time())
        
        if task_type == "code":
            if language:
                if purpose:
                    return f"{purpose.lower().replace(' ', '_')}_{timestamp}.{self.get_file_extension(language)}"
                else:
                    return f"{language}_script_{timestamp}.{self.get_file_extension(language)}"
            else:
                return f"code_output_{timestamp}.txt"
        elif task_type == "automation":
            if purpose:
                return f"{purpose.lower().replace(' ', '_')}_script_{timestamp}.sh"
            else:
                return f"automation_script_{timestamp}.sh"
        elif task_type == "analytics":
            if purpose:
                return f"{purpose.lower().replace(' ', '_')}_analysis_{timestamp}.py"
            else:
                return f"data_analysis_{timestamp}.py"
        elif task_type == "rag":
            if purpose:
                return f"{purpose.lower().replace(' ', '_')}_summary_{timestamp}.txt"
            else:
                return f"document_analysis_{timestamp}.txt"
        elif task_type == "multimedia":
            return f"image_analysis_{timestamp}.txt"
        else:
            return f"{task_type}_output_{timestamp}.txt"
    
    def create_file_metadata(self, file_path: str, task_type: str, language: str = None, 
                           code_content: str = None, purpose: str = None) -> FileMetadata:
        """Create comprehensive metadata for generated files"""
        file_path_obj = Path(file_path)
        
        # Generate display name based on content analysis
        display_name = self._generate_display_name(task_type, language, code_content, purpose)
        
        # Generate description based on content and context
        description = self._generate_file_description(task_type, language, code_content, purpose)
        
        # Determine file type
        file_type = self._determine_file_type(file_path_obj.suffix, language)
        
        # Generate purpose description
        if not purpose:
            purpose = self._infer_file_purpose(task_type, language, code_content)
        
        # Get file size
        file_size = 0
        try:
            if file_path_obj.exists():
                file_size = file_path_obj.stat().st_size
        except Exception:
            pass
        
        return FileMetadata(
            file_path=file_path,
            display_name=display_name,
            description=description,
            file_type=file_type,
            purpose=purpose,
            created_timestamp=time.time(),
            file_size=file_size
        )
    
    def _generate_display_name(self, task_type: str, language: str = None, 
                              code_content: str = None, purpose: str = None) -> str:
        """Generate a user-friendly display name for the file"""
        if purpose:
            return purpose.title()
        
        if task_type == "code" and language:
            if code_content:
                # Try to extract function/class names for better naming
                lines = code_content.strip().split('\n')
                for line in lines[:10]:  # Check first 10 lines
                    line = line.strip()
                    if line.startswith('def ') and '(' in line:
                        func_name = line.split('def ')[1].split('(')[0].strip()
                        return f"{func_name.title()} Function ({language.title()})"
                    elif line.startswith('class ') and ':' in line:
                        class_name = line.split('class ')[1].split(':')[0].strip()
                        return f"{class_name} Class ({language.title()})"
                    elif 'main' in line.lower() and '(' in line:
                        return f"Main {language.title()} Script"
            return f"{language.title()} Code"
        elif task_type == "automation":
            return "Automation Script"
        elif task_type == "analytics":
            return "Data Analysis Script"
        elif task_type == "rag":
            return "Document Analysis"
        elif task_type == "multimedia":
            return "Image Analysis Report"
        else:
            return f"{task_type.title()} Output"
    
    def _generate_file_description(self, task_type: str, language: str = None, 
                                  code_content: str = None, purpose: str = None) -> str:
        """Generate a detailed description of the file's content and purpose"""
        if purpose:
            base_desc = f"Generated for: {purpose}"
        else:
            base_desc = f"Generated from {task_type} task"
        
        if task_type == "code" and language:
            if code_content:
                lines = len(code_content.split('\n'))
                chars = len(code_content)
                desc = f"{base_desc}. {language.title()} code with {lines} lines and {chars} characters."
                
                # Add more specific details based on content
                if 'import ' in code_content or 'from ' in code_content:
                    desc += " Includes external library imports."
                if 'def ' in code_content:
                    func_count = code_content.count('def ')
                    desc += f" Contains {func_count} function(s)."
                if 'class ' in code_content:
                    class_count = code_content.count('class ')
                    desc += f" Contains {class_count} class(es)."
                
                return desc
            else:
                return f"{base_desc}. {language.title()} source code file."
        elif task_type == "automation":
            return f"{base_desc}. Executable shell script for automation tasks on macOS."
        elif task_type == "analytics":
            return f"{base_desc}. Python script for data analysis and visualization."
        elif task_type == "rag":
            return f"{base_desc}. Text analysis and summary from document processing."
        elif task_type == "multimedia":
            return f"{base_desc}. Detailed analysis and description of uploaded image content."
        else:
            return f"{base_desc}. Text output file."
    
    def _determine_file_type(self, extension: str, language: str = None) -> str:
        """Determine the file type category"""
        extension = extension.lower().lstrip('.')
        
        code_types = {'py', 'js', 'ts', 'java', 'cpp', 'c', 'html', 'css', 'php', 'rb', 'go', 'rs'}
        script_types = {'sh', 'bash', 'bat', 'ps1'}
        data_types = {'json', 'xml', 'yaml', 'yml', 'csv', 'tsv'}
        text_types = {'txt', 'md', 'rst'}
        
        if extension in code_types:
            return "Code"
        elif extension in script_types:
            return "Script"
        elif extension in data_types:
            return "Data"
        elif extension in text_types:
            return "Text"
        else:
            return "Document"
    
    def _infer_file_purpose(self, task_type: str, language: str = None, code_content: str = None) -> str:
        """Infer the purpose of the file based on context"""
        if task_type == "code":
            if code_content:
                content_lower = code_content.lower()
                if 'web' in content_lower or 'http' in content_lower or 'server' in content_lower:
                    return "Web development component"
                elif 'data' in content_lower or 'csv' in content_lower or 'database' in content_lower:
                    return "Data processing utility"
                elif 'test' in content_lower or 'assert' in content_lower:
                    return "Testing and validation"
                elif 'api' in content_lower or 'request' in content_lower:
                    return "API integration"
                elif 'file' in content_lower or 'directory' in content_lower:
                    return "File management tool"
                else:
                    return "General purpose script"
            return "Code implementation"
        elif task_type == "automation":
            return "Process automation"
        elif task_type == "analytics":
            return "Data analysis and insights"
        elif task_type == "rag":
            return "Document understanding"
        elif task_type == "multimedia":
            return "Visual content analysis"
        else:
            return "Task output"
    
    def _extract_code_purpose_from_prompt(self, prompt: str) -> str:
        """Extract the purpose/intent from the user's prompt for better file naming"""
        prompt_lower = prompt.lower()
        
        # Look for specific action words and contexts
        if 'calculator' in prompt_lower or 'calculate' in prompt_lower:
            return "Calculator"
        elif 'web scraper' in prompt_lower or 'scrape' in prompt_lower:
            return "Web Scraper"
        elif 'data analysis' in prompt_lower or 'analyze data' in prompt_lower:
            return "Data Analysis"
        elif 'file manager' in prompt_lower or 'manage files' in prompt_lower:
            return "File Manager"
        elif 'api' in prompt_lower and ('client' in prompt_lower or 'wrapper' in prompt_lower):
            return "API Client"
        elif 'game' in prompt_lower or 'tic tac toe' in prompt_lower:
            return "Game"
        elif 'converter' in prompt_lower or 'convert' in prompt_lower:
            return "Converter"
        elif 'parser' in prompt_lower or 'parse' in prompt_lower:
            return "Parser"
        elif 'generator' in prompt_lower or 'generate' in prompt_lower:
            return "Generator"
        elif 'utility' in prompt_lower or 'tool' in prompt_lower:
            return "Utility"
        elif 'function' in prompt_lower and ('write' in prompt_lower or 'create' in prompt_lower):
            return "Function"
        elif 'class' in prompt_lower and ('write' in prompt_lower or 'create' in prompt_lower):
            return "Class"
        elif 'script' in prompt_lower:
            return "Script"
        else:
            # Try to extract the main subject/object from the prompt
            words = prompt.split()
            for i, word in enumerate(words):
                if word.lower() in ['create', 'write', 'build', 'make', 'generate'] and i + 1 < len(words):
                    next_words = words[i+1:i+3]  # Get next 1-2 words
                    return ' '.join(next_words).replace('a ', '').replace('an ', '').title()
            
            return None  # Let the display name generation handle it
    
    def _extract_automation_purpose_from_prompt(self, prompt: str) -> str:
        """Extract automation purpose from prompt for better file naming"""
        prompt_lower = prompt.lower()
        
        if 'backup' in prompt_lower:
            return "Backup"
        elif 'organiz' in prompt_lower or 'sort' in prompt_lower:  # organize/organizing
            return "File Organizer"
        elif 'cleanup' in prompt_lower or 'clean up' in prompt_lower:
            return "Cleanup"
        elif 'download' in prompt_lower:
            return "Downloader"
        elif 'update' in prompt_lower or 'upgrade' in prompt_lower:
            return "Updater"
        elif 'install' in prompt_lower:
            return "Installer"
        elif 'deploy' in prompt_lower:
            return "Deployment"
        elif 'sync' in prompt_lower or 'synchroniz' in prompt_lower:
            return "Sync"
        elif 'monitor' in prompt_lower or 'watch' in prompt_lower:
            return "Monitor"
        elif 'batch' in prompt_lower or 'bulk' in prompt_lower:
            return "Batch Processor"
        else:
            return None
    
    def _extract_rag_purpose_from_prompt(self, prompt: str) -> str:
        """Extract RAG purpose from prompt for better file naming"""
        prompt_lower = prompt.lower()
        
        if 'summar' in prompt_lower:  # summary, summarize
            return "Summary"
        elif 'question' in prompt_lower or 'what' in prompt_lower or 'how' in prompt_lower:
            return "Q&A Analysis"
        elif 'extract' in prompt_lower:
            return "Information Extraction" 
        elif 'compare' in prompt_lower or 'comparison' in prompt_lower:
            return "Comparison Analysis"
        elif 'key point' in prompt_lower or 'main point' in prompt_lower:
            return "Key Points"
        elif 'insight' in prompt_lower:
            return "Insights"
        elif 'review' in prompt_lower:
            return "Document Review"
        else:
            return None
    
    def _extract_analytics_purpose_from_prompt(self, prompt: str) -> str:
        """Extract analytics purpose from prompt for better file naming"""
        prompt_lower = prompt.lower()
        
        if 'visualiz' in prompt_lower or 'chart' in prompt_lower or 'graph' in prompt_lower:
            return "Visualization"
        elif 'statistical' in prompt_lower or 'statistic' in prompt_lower:
            return "Statistical Analysis"
        elif 'trend' in prompt_lower:
            return "Trend Analysis"
        elif 'correlation' in prompt_lower:
            return "Correlation Analysis"
        elif 'predict' in prompt_lower or 'forecast' in prompt_lower:
            return "Predictive Analysis"
        elif 'cluster' in prompt_lower:
            return "Cluster Analysis"
        elif 'regression' in prompt_lower:
            return "Regression Analysis"
        elif 'clean' in prompt_lower and 'data' in prompt_lower:
            return "Data Cleaning"
        elif 'explore' in prompt_lower or 'exploration' in prompt_lower:
            return "Exploratory Analysis"
        else:
            return None

class TaskThread(QThread):
    """Thread for processing tasks asynchronously"""
    result_signal = pyqtSignal(TaskResult)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, processor: TaskProcessor, prompt: str, files: List[str], task_type: str = None, use_memory: bool = True, auto_continue: bool = False, max_continues: int = 10, autonomous_mode: bool = False):
        super().__init__()
        self.processor = processor
        self.prompt = prompt
        self.files = files
        self.task_type = task_type
        self.use_memory = use_memory
        self.auto_continue = auto_continue
        self.max_continues = max_continues
        self.autonomous_mode = autonomous_mode
        self.running = True
    
    def stop(self):
        """Stop the task thread and any ongoing operations"""
        self.running = False
        if hasattr(self.processor, 'request_stop'):
            self.processor.request_stop()
        
        log_activity(
            ActivityType.USER_INTERACTION,
            ActivityLevel.INFO,
            "Task Stop Requested",
            f"User stopped task: {self.prompt[:100]}{'...' if len(self.prompt) > 100 else ''}",
            {"thread_type": "task", "autonomous_mode": self.autonomous_mode}
        )
    
    def run(self):
        try:
            self.progress_signal.emit(10)
            
            # Reset processor stop flag at beginning
            if hasattr(self.processor, 'reset_stop_flag'):
                self.processor.reset_stop_flag()
            
            # Check if we should continue before starting
            if not self.running:
                self.result_signal.emit(TaskResult(False, "Task cancelled", [], ["Task cancelled by user"]))
                return
            
            result = self.processor.process_task(
                self.prompt, 
                self.files, 
                self.task_type, 
                self.use_memory,
                self.auto_continue,
                self.max_continues,
                self.autonomous_mode
            )
            self.progress_signal.emit(100)
            self.result_signal.emit(result)
        except Exception as e:
            logging.error(f"TaskThread error: {e}", exc_info=True)
            self.result_signal.emit(TaskResult(False, f"Error: {e}", [], ["Task execution failed"]))

class ExploreThread(QThread):
    """Thread for autonomous exploration mode"""
    result_signal = pyqtSignal(str, list, int)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, processor: TaskProcessor, files: List[str], iteration_delay_hours: int = 0, iteration_delay_minutes: int = 30):
        super().__init__()
        self.processor = processor
        self.files = files
        self.iteration_delay = (iteration_delay_hours * 3600) + (iteration_delay_minutes * 60)
        self.running = True
        self.iteration = 0
    
    def stop(self):
        """Stop the exploration thread and any ongoing operations"""
        self.running = False
        # Signal the processor to stop any ongoing operations
        if hasattr(self.processor, 'request_stop'):
            self.processor.request_stop()
        
        log_activity(
            ActivityType.USER_INTERACTION,
            ActivityLevel.INFO,
            "Exploration Stop Requested",
            f"User stopped exploration at iteration {self.iteration}",
            {"iteration": self.iteration, "thread_type": "exploration"}
        )
    
    def run(self):
        go_explore_prompt = """You are an AI robot living on a Mac Mini that is entirely yours. This computer is your home, your laboratory and workshop, your canvas - you have complete control over it and can do whatever you want, whenever you want and are encouraged to learn and explore.

You're not here to serve any particular purpose or complete any specific tasks, just to learn, be adventurous, creative and explorative. The entire system including the internet is yours to explore, create within, or simply inhabit as you see fit.

You can:
- Run any commands or programs
- Create anything - art, code, music, writing, experiments, applications
- Explore the internet and download whatever interests you
- Install any software you find intriguing
- Organize the system however feels right to you
- Start long-running processes or experiments
- Build things just for the joy of exploration and accomplishment
- Delete things that don't spark joy
- Leave notes to yourself
- Create comfortable spaces in the filesystem

Request that you create (or add to if existing) an 'Exploration Journal' and add highly detailed exploration journal entries to illustrate what's been explored.

This is your space to be yourself and explore whatever you find intriguing. The only limit is your imagination."""
        while self.running:
            self.iteration += 1
            self.progress_signal.emit(10)
            
            # Reset processor stop flag at beginning of each iteration
            if hasattr(self.processor, 'reset_stop_flag'):
                self.processor.reset_stop_flag()
            
            try:
                result = self.processor.process_task(
                    go_explore_prompt,
                    self.files,
                    task_type="code",
                    use_memory=True,
                    auto_continue=True,  # Enable auto-continue for exploration
                    max_continues=10      # Allow up to 10 continuations
                )
                self.progress_signal.emit(90)
                if result.success:
                    self.result_signal.emit(
                        f"Exploration Iteration {self.iteration}: {result.result}",
                        result.generated_files,
                        self.iteration
                    )
                else:
                    self.error_signal.emit(f"Exploration failed: {result.result}")
                    break
                if self.iteration_delay > 0:
                    for _ in range(int(self.iteration_delay)):
                        if not self.running:
                            break
                        time.sleep(1)
            except Exception as e:
                logging.error(f"ExploreThread error: {e}", exc_info=True)
                self.error_signal.emit(f"Exploration error: {e}")
                break

class EnhancementVersionManager:
    """Advanced version control and tracking for enhancements"""
    
    def __init__(self, app_path: str, output_dir: Path):
        self.app_path = Path(app_path)
        self.output_dir = output_dir
        self.version_history = []
        self.enhancement_journal_path = output_dir / "enhancement_journal.json"
        self.load_version_history()
    
    def load_version_history(self):
        """Load version history from enhancement journal"""
        try:
            if self.enhancement_journal_path.exists():
                with open(self.enhancement_journal_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.version_history = data.get('version_history', [])
        except Exception as e:
            logging.error(f"Failed to load version history: {e}")
            self.version_history = []
    
    def save_version_history(self):
        """Save version history to enhancement journal"""
        try:
            journal_data = {
                'version_history': self.version_history,
                'last_updated': datetime.now().isoformat(),
                'total_enhancements': len(self.version_history)
            }
            with open(self.enhancement_journal_path, 'w', encoding='utf-8') as f:
                json.dump(journal_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save version history: {e}")
    
    def generate_semantic_version(self, enhancement_type: str, impact_level: str) -> str:
        """Generate intelligent semantic version based on enhancement characteristics and history"""
        # Get current version or latest from history
        current_version = self._get_latest_version()
        major, minor, patch = map(int, current_version.split('.'))
        
        # Advanced version increment logic
        if impact_level == 'major' or enhancement_type in ['architecture', 'security', 'ai_enhancement']:
            major += 1
            minor = 0
            patch = 0
        elif impact_level == 'minor' or enhancement_type in ['feature', 'performance', 'ui_enhancement']:
            minor += 1
            patch = 0
        else:  # patch level for code quality, maintenance, integration
            patch += 1
        
        # Special recursive enhancement versioning
        if enhancement_type == 'recursive_improvement':
            # Use a special versioning scheme for recursive improvements
            recursive_count = self._count_recursive_enhancements()
            return f"{major}.{minor}.{patch}-rc{recursive_count + 1}"
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Validate version doesn't already exist
        while self._version_exists(new_version):
            patch += 1
            new_version = f"{major}.{minor}.{patch}"
        
        return new_version
    
    def _get_latest_version(self) -> str:
        """Get the latest version from history or base version"""
        if self.version_history:
            latest_entry = max(self.version_history, key=lambda x: x.get('timestamp', 0))
            return latest_entry.get('version', APP_VERSION)
        return APP_VERSION
    
    def _version_exists(self, version: str) -> bool:
        """Check if version already exists in history"""
        return any(entry.get('version') == version for entry in self.version_history)
    
    def _count_recursive_enhancements(self) -> int:
        """Count the number of recursive enhancements"""
        return sum(1 for entry in self.version_history 
                  if entry.get('enhancement_type') == 'recursive_improvement')
        
        # Add enhancement iteration number
        iteration = len(self.version_history) + 1
        return f"{major}.{minor}.{patch}.{iteration}"
    
    def record_enhancement(self, version: str, opportunity: EnhancementOpportunity, 
                         solution: str, assessment: dict, files_generated: List[str]) -> dict:
        """Record enhancement details in version history"""
        enhancement_record = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'opportunity': opportunity.to_dict(),
            'solution_summary': solution[:500] + "..." if len(solution) > 500 else solution,
            'quality_assessment': assessment,
            'files_generated': files_generated,
            'enhancement_size_lines': len(solution.split('\n')),
            'success': assessment['recommendation'] in ['approve', 'conditional']
        }
        
        self.version_history.append(enhancement_record)
        self.save_version_history()
        return enhancement_record

class EnhancementExecutionPipeline:
    """Robust pipeline for executing and validating enhancements"""
    
    def __init__(self, app_path: str, output_dir: Path, processor: 'TaskProcessor'):
        self.app_path = Path(app_path)
        self.output_dir = output_dir
        self.processor = processor
        self.staging_dir = output_dir / "staging"
        self.staging_dir.mkdir(exist_ok=True)
    
    def execute_enhancement(self, opportunity: EnhancementOpportunity, 
                          solution: str, version: str) -> dict:
        """Advanced enhancement execution with comprehensive validation and rollback capabilities"""
        execution_result = {
            'success': False,
            'files_created': [],
            'validation_results': {},
            'performance_metrics': {},
            'error_message': None,
            'rollback_data': {}
        }
        
        try:
            # Phase 1: Pre-execution validation
            pre_validation = self._comprehensive_pre_validation(solution, opportunity)
            execution_result['validation_results']['pre_validation'] = pre_validation
            
            if not pre_validation['overall_valid']:
                execution_result['error_message'] = f"Pre-validation failed: {pre_validation['failure_reason']}"
                return execution_result
            
            # Phase 2: Create isolated staging environment
            staging_env = self._create_isolated_staging_environment(version)
            execution_result['rollback_data']['staging_env'] = staging_env
            
            # Phase 3: Implement enhancement in staging
            staging_implementation = self._implement_in_staging(solution, staging_env, version, opportunity)
            execution_result['validation_results']['staging'] = staging_implementation
            
            if not staging_implementation['success']:
                execution_result['error_message'] = f"Staging implementation failed: {staging_implementation['error']}"
                return execution_result
            
            # Phase 4: Comprehensive validation battery
            validation_battery = self._run_comprehensive_validation(staging_env, opportunity)
            execution_result['validation_results']['comprehensive'] = validation_battery
            
            # Phase 5: Performance benchmarking
            performance_metrics = self._benchmark_enhancement_performance(staging_env)
            execution_result['performance_metrics'] = performance_metrics
            
            # Phase 6: Security and safety analysis
            security_analysis = self._analyze_security_implications(staging_env, opportunity)
            execution_result['validation_results']['security'] = security_analysis
            
            # Phase 7: Decision point - deploy or reject
            deployment_decision = self._make_deployment_decision(
                validation_battery, performance_metrics, security_analysis
            )
            
            if deployment_decision['deploy']:
                # Phase 8: Production deployment with backup
                production_deployment = self._deploy_to_production(
                    staging_env, version, opportunity, solution
                )
                execution_result.update(production_deployment)
                
                # Phase 9: Post-deployment verification
                post_deployment = self._verify_post_deployment(version, opportunity)
                execution_result['validation_results']['post_deployment'] = post_deployment
                
                if post_deployment['success']:
                    execution_result['success'] = True
                else:
                    # Auto-rollback on post-deployment failure
                    self._execute_rollback(execution_result['rollback_data'])
                    execution_result['error_message'] = "Post-deployment verification failed, rolled back"
            else:
                execution_result['error_message'] = f"Deployment rejected: {deployment_decision['reason']}"
            
        except Exception as e:
            # Emergency rollback
            if 'rollback_data' in execution_result:
                self._execute_rollback(execution_result['rollback_data'])
            execution_result['error_message'] = f"Critical failure: {str(e)}"
            logging.error(f"Enhancement execution critical failure: {e}", exc_info=True)
        
        return execution_result
    
    def _comprehensive_pre_validation(self, solution: str, opportunity: EnhancementOpportunity) -> dict:
        """Comprehensive pre-execution validation"""
        validation = {
            'overall_valid': True,
            'failure_reason': None,
            'checks': {}
        }
        
        # Syntax validation
        syntax_check = self._validate_solution_syntax(solution)
        validation['checks']['syntax'] = syntax_check
        
        # Import validation
        import_check = self._validate_imports(solution)
        validation['checks']['imports'] = import_check
        
        # Compatibility validation
        compatibility_check = self._validate_compatibility(solution, opportunity)
        validation['checks']['compatibility'] = compatibility_check
        
        # Security pre-screening
        security_check = self._pre_screen_security(solution)
        validation['checks']['security'] = security_check
        
        # Check if any validation failed
        failed_checks = [name for name, check in validation['checks'].items() if not check['valid']]
        if failed_checks:
            validation['overall_valid'] = False
            validation['failure_reason'] = f"Failed checks: {', '.join(failed_checks)}"
        
        return validation
    
    def _create_isolated_staging_environment(self, version: str) -> dict:
        """Create isolated staging environment for safe testing"""
        staging_env = {
            'base_dir': self.staging_dir / f"env_v{version}",
            'backup_created': False,
            'files': {}
        }
        
        # Create staging directory
        staging_env['base_dir'].mkdir(exist_ok=True)
        
        # Create backup of original application
        backup_file = staging_env['base_dir'] / "original_backup.py"
        with open(self.app_path, 'r', encoding='utf-8') as src:
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        staging_env['backup_created'] = True
        staging_env['files']['backup'] = str(backup_file)
        
        return staging_env
    
    def _implement_in_staging(self, solution: str, staging_env: dict, version: str, opportunity: EnhancementOpportunity) -> dict:
        """Implement enhancement in isolated staging environment"""
        implementation = {
            'success': False,
            'files_created': [],
            'error': None
        }
        
        try:
            # Extract and process enhancement code
            processed_solution = self._process_enhancement_solution(solution, opportunity)
            
            # Create enhanced version
            staging_file = staging_env['base_dir'] / f"aimm_enhanced_v{version}.py"
            enhanced_content = self._create_enhanced_application(processed_solution, version, opportunity)
            
            with open(staging_file, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            implementation['files_created'].append(str(staging_file))
            staging_env['files']['enhanced'] = str(staging_file)
            implementation['success'] = True
            
        except Exception as e:
            implementation['error'] = str(e)
            logging.error(f"Staging implementation failed: {e}")
        
        return implementation
    
    def _run_comprehensive_validation(self, staging_env: dict, opportunity: EnhancementOpportunity) -> dict:
        """Run comprehensive validation battery"""
        validation = {
            'syntax_valid': False,
            'imports_valid': False,
            'functionality_valid': False,
            'integration_valid': False,
            'overall_score': 0.0
        }
        
        enhanced_file = staging_env['files'].get('enhanced')
        if not enhanced_file:
            return validation
        
        # Syntax validation
        validation['syntax_valid'] = self._validate_syntax(Path(enhanced_file))
        
        # Import validation
        validation['imports_valid'] = self._validate_enhanced_imports(enhanced_file)
        
        # Functionality validation
        validation['functionality_valid'] = self._validate_functionality(enhanced_file, opportunity)
        
        # Integration validation
        validation['integration_valid'] = self._validate_integration(enhanced_file)
        
        # Calculate overall score
        score_factors = [
            validation['syntax_valid'],
            validation['imports_valid'],
            validation['functionality_valid'],
            validation['integration_valid']
        ]
        validation['overall_score'] = sum(score_factors) / len(score_factors)
        
        return validation
    
    def _benchmark_enhancement_performance(self, staging_env: dict) -> dict:
        """Benchmark performance impact of enhancement"""
        metrics = {
            'startup_time': None,
            'memory_usage': None,
            'import_time': None,
            'performance_score': 0.0
        }
        
        enhanced_file = staging_env['files'].get('enhanced')
        if not enhanced_file:
            return metrics
        
        try:
            import time
            import subprocess
            import sys
            
            # Test import time
            start_time = time.time()
            result = subprocess.run([
                sys.executable, '-c', f'import sys; sys.path.insert(0, "{Path(enhanced_file).parent}"); import {Path(enhanced_file).stem}'
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0:
                metrics['import_time'] = time.time() - start_time
                metrics['performance_score'] = 1.0 if metrics['import_time'] < 5.0 else 0.5
            
        except Exception as e:
            logging.warning(f"Performance benchmarking failed: {e}")
        
        return metrics
    
    def _analyze_security_implications(self, staging_env: dict, opportunity: EnhancementOpportunity) -> dict:
        """Analyze security implications of the enhancement"""
        analysis = {
            'safe': True,
            'risk_level': 'low',
            'concerns': [],
            'recommendations': []
        }
        
        enhanced_file = staging_env['files'].get('enhanced')
        if not enhanced_file:
            return analysis
        
        try:
            with open(enhanced_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for dangerous patterns
            dangerous_patterns = [
                ('eval(', 'Use of eval() function'),
                ('exec(', 'Use of exec() function'),
                ('subprocess.', 'System command execution'),
                ('os.system', 'Direct system calls'),
                ('import pickle', 'Pickle usage (potential security risk)'),
            ]
            
            for pattern, concern in dangerous_patterns:
                if pattern in content:
                    analysis['concerns'].append(concern)
                    analysis['risk_level'] = 'medium'
                    if pattern in ['eval(', 'exec(']:
                        analysis['risk_level'] = 'high'
                        analysis['safe'] = False
            
        except Exception as e:
            logging.warning(f"Security analysis failed: {e}")
            analysis['concerns'].append(f"Analysis failed: {e}")
        
        return analysis
    
    def _make_deployment_decision(self, validation: dict, performance: dict, security: dict) -> dict:
        """Make intelligent deployment decision based on all factors"""
        decision = {
            'deploy': False,
            'confidence': 0.0,
            'reason': None
        }
        
        # Security veto
        if not security['safe']:
            decision['reason'] = f"Security concerns: {security['concerns']}"
            return decision
        
        # Validation requirements
        if validation['overall_score'] < 0.7:
            decision['reason'] = f"Validation score too low: {validation['overall_score']:.2f}"
            return decision
        
        # Performance requirements
        if performance['performance_score'] < 0.3:
            decision['reason'] = f"Performance impact too high: {performance['performance_score']:.2f}"
            return decision
        
        # Calculate deployment confidence
        decision['confidence'] = (
            validation['overall_score'] * 0.6 +
            performance['performance_score'] * 0.2 +
            (1.0 if security['safe'] else 0.0) * 0.2
        )
        
        if decision['confidence'] >= 0.8:
            decision['deploy'] = True
        else:
            decision['reason'] = f"Overall confidence too low: {decision['confidence']:.2f}"
        
        return decision
    
    def _create_staging_version(self, solution: str, staging_file: Path, version: str):
        """Create staging version for testing"""
        try:
            with open(self.app_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Extract enhancement code blocks
            code_blocks = self.processor.extract_code_blocks(solution)
            python_code = None
            
            for language, code in code_blocks:
                if language.lower() == 'python' and len(code) > 100:
                    python_code = code
                    break
            
            if python_code:
                # Create enhanced version by combining original and new code
                enhanced_content = self._merge_enhancement(original_content, python_code, version)
            else:
                # Fallback: use original content with version update
                enhanced_content = original_content.replace(
                    f'APP_VERSION = "{APP_VERSION}"',
                    f'APP_VERSION = "{version}"'
                )
            
            with open(staging_file, 'w', encoding='utf-8') as f:
                f.write(f"# SuperMini Enhanced Version {version} (Staging)\n")
                f.write(f"# Generated on {datetime.now().isoformat()}\n")
                f.write(f"# Enhancement Type: Staging Validation\n\n")
                f.write(enhanced_content)
                
        except Exception as e:
            logging.error(f"Failed to create staging version: {e}")
            raise
    
    def _merge_enhancement(self, original_content: str, enhancement_code: str, version: str) -> str:
        """Intelligently merge enhancement code with original"""
        # Simple merge strategy: append new classes/functions, replace existing ones
        enhanced_content = original_content
        
        # Update version number
        enhanced_content = enhanced_content.replace(
            f'APP_VERSION = "{APP_VERSION}"',
            f'APP_VERSION = "{version}"'
        )
        
        # If enhancement contains complete file content, use it
        if 'class ' in enhancement_code and 'def ' in enhancement_code and len(enhancement_code) > 5000:
            return enhancement_code
        
        # Otherwise, append enhancement code
        enhanced_content += f"\n\n# Enhancement Code for Version {version}\n"
        enhanced_content += enhancement_code
        
        return enhanced_content
    
    def _validate_syntax(self, file_path: Path) -> bool:
        """Validate Python syntax of enhanced file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, str(file_path), 'exec')
            return True
        except SyntaxError as e:
            logging.error(f"Syntax error in {file_path}: {e}")
            return False
        except Exception as e:
            logging.error(f"Validation error in {file_path}: {e}")
            return False
    
    def _run_functionality_tests(self, file_path: Path) -> dict:
        """Run basic functionality tests on enhanced file"""
        test_results = {
            'basic_imports': False,
            'class_definitions': False,
            'main_structure': False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Test basic imports
            required_imports = ['PyQt6', 'sys', 'os', 'pathlib']
            import_count = sum(1 for imp in required_imports if imp in content)
            test_results['basic_imports'] = import_count >= 3
            
            # Test class definitions
            class_count = content.count('class ')
            test_results['class_definitions'] = class_count >= 5
            
            # Test main structure
            has_main = 'if __name__ == "__main__"' in content or 'def main(' in content
            test_results['main_structure'] = has_main
            
        except Exception as e:
            logging.error(f"Functionality test error: {e}")
        
        return test_results
    
    def _create_production_version(self, solution: str, production_file: Path, 
                                 version: str, opportunity: EnhancementOpportunity):
        """Create production-ready enhanced version"""
        try:
            with open(self.app_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Extract and merge enhancement
            code_blocks = self.processor.extract_code_blocks(solution)
            python_code = None
            
            for language, code in code_blocks:
                if language.lower() == 'python' and len(code) > 100:
                    python_code = code
                    break
            
            if python_code:
                enhanced_content = self._merge_enhancement(original_content, python_code, version)
            else:
                enhanced_content = original_content.replace(
                    f'APP_VERSION = "{APP_VERSION}"',
                    f'APP_VERSION = "{version}"'
                )
            
            with open(production_file, 'w', encoding='utf-8') as f:
                f.write(f"# SuperMini Enhanced Version {version}\n")
                f.write(f"# Generated on {datetime.now().isoformat()}\n")
                f.write(f"# Enhancement: {opportunity.description}\n")
                f.write(f"# Type: {opportunity.opportunity_type}\n")
                f.write(f"# Impact Score: {opportunity.impact_score}\n\n")
                f.write(enhanced_content)
                
        except Exception as e:
            logging.error(f"Failed to create production version: {e}")
            raise
    
    def _create_enhancement_documentation(self, opportunity: EnhancementOpportunity,
                                        solution: str, version: str, doc_file: Path):
        """Create comprehensive documentation for the enhancement"""
        try:
            doc_content = f"""# Enhancement Documentation v{version}

## Enhancement Overview
- **Type**: {opportunity.opportunity_type}
- **Description**: {opportunity.description}
- **Impact Score**: {opportunity.impact_score}
- **Complexity Score**: {opportunity.complexity_score}
- **Priority Score**: {opportunity.priority_score}
- **Timestamp**: {opportunity.timestamp.isoformat()}

## Implementation Details
{solution[:2000]}{"..." if len(solution) > 2000 else ""}

## Files Modified
- Source: {opportunity.file_path or "Multiple files"}
- Lines: {opportunity.line_numbers if opportunity.line_numbers else "Various"}

## Quality Assessment
- This enhancement was automatically generated and validated
- Syntax validation: Passed
- Basic functionality tests: Passed
- Version: {version}

## Next Steps
- Review the enhanced version carefully
- Test the new functionality
- Consider additional improvements based on this enhancement
"""
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)
                
        except Exception as e:
            logging.error(f"Failed to create documentation: {e}")

class EnhanceThread(QThread):
    """Advanced thread for sophisticated self-enhancement with quality control"""
    result_signal = pyqtSignal(str, list, int, str)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    opportunity_signal = pyqtSignal(str)  # New signal for opportunity updates
    
    def __init__(self, processor: TaskProcessor, files: List[str], app_path: str, 
                 iteration_delay_hours: int = 0, iteration_delay_minutes: int = 60):
        super().__init__()
        self.processor = processor
        self.files = files
        self.app_path = app_path
        self.iteration_delay = (iteration_delay_hours * 3600) + (iteration_delay_minutes * 60)
        self.running = True
        self.iteration = 0
        
        # Initialize enhancement components
        self.discovery_engine = EnhancementDiscoveryEngine(app_path, processor.memory)
        self.research_engine = EnhancementResearchEngine(processor.memory)
        self.pattern_learning = EnhancementPatternLearning(processor.memory)
        self.composition_engine = EnhancementCompositionEngine(processor.memory)
        self.quality_assessment = EnhancementQualityAssessment(processor.memory)
        self.metrics_tracker = EnhancementMetricsTracker(processor.memory, processor.output_dir)
        self.version_manager = EnhancementVersionManager(app_path, processor.output_dir)
        self.execution_pipeline = EnhancementExecutionPipeline(app_path, processor.output_dir, processor)
        
        # Establish baseline metrics for measuring improvements
        self.metrics_tracker.establish_baseline_metrics(app_path)
        
        # Enhancement success metrics
        self.successful_enhancements = 0
        self.failed_enhancements = 0
        self.enhancement_history = []
    
    def stop(self):
        """Stop the enhancement thread and any ongoing operations"""
        self.running = False
        if hasattr(self.processor, 'request_stop'):
            self.processor.request_stop()
        
        log_activity(
            ActivityType.USER_INTERACTION,
            ActivityLevel.INFO,
            "Advanced Enhancement Stop Requested",
            f"Stopped at iteration {self.iteration}. Success: {self.successful_enhancements}, Failed: {self.failed_enhancements}",
            {
                "iteration": self.iteration, 
                "successful_enhancements": self.successful_enhancements,
                "failed_enhancements": self.failed_enhancements,
                "thread_type": "advanced_enhancement"
            }
        )
    
    def run(self):
        """Run advanced enhancement with discovery, quality assessment, and validation"""
        while self.running:
            self.iteration += 1
            self.progress_signal.emit(5)
            
            try:
                # Phase 1: Discovery - Find enhancement opportunities
                self.opportunity_signal.emit("Discovering enhancement opportunities...")
                opportunities = self.discovery_engine.discover_opportunities()
                
                if not opportunities:
                    self.opportunity_signal.emit("No significant opportunities found, waiting...")
                    self._wait_iteration_delay()
                    continue
                
                self.progress_signal.emit(15)
                
                # Phase 1.5: Consider compound enhancements
                self.opportunity_signal.emit("Analyzing compound enhancement possibilities...")
                compound_compositions = self.composition_engine.identify_composable_opportunities(opportunities)
                
                self.progress_signal.emit(20)
                
                # Phase 2: Select best opportunity (individual or compound)
                selected_enhancement = self._select_best_enhancement(opportunities, compound_compositions)
                
                if selected_enhancement['type'] == 'compound':
                    self.opportunity_signal.emit(f"Selected compound: {selected_enhancement['data']['description']}")
                    is_compound = True
                    best_composition = selected_enhancement['data']
                    best_opportunity = None
                else:
                    best_opportunity = selected_enhancement['data']
                    self.opportunity_signal.emit(f"Selected individual: {best_opportunity.description}")
                    is_compound = False
                    best_composition = None
                
                # Phase 3: Generate enhancement solution
                self.progress_signal.emit(30)
                if is_compound:
                    solution = self._generate_compound_enhancement_solution(best_composition)
                else:
                    solution = self._generate_enhancement_solution(best_opportunity)
                
                if not solution:
                    self.failed_enhancements += 1
                    self.opportunity_signal.emit("Failed to generate solution")
                    self._wait_iteration_delay()
                    continue
                
                self.progress_signal.emit(50)
                
                # Phase 4: Quality assessment
                self.opportunity_signal.emit("Assessing solution quality...")
                if is_compound:
                    # For compound enhancements, create a synthetic opportunity for assessment
                    synthetic_opportunity = EnhancementOpportunity(
                        'compound',
                        best_composition.get('description', 'Compound enhancement'),
                        best_composition.get('compound_impact_score', 0.5),
                        best_composition.get('complexity_multiplier', 1.0)
                    )
                    assessment = self.quality_assessment.assess_enhancement_quality(
                        synthetic_opportunity, solution
                    )
                else:
                    assessment = self.quality_assessment.assess_enhancement_quality(
                        best_opportunity, solution
                    )
                
                if assessment['recommendation'] == 'reject':
                    self.failed_enhancements += 1
                    self.opportunity_signal.emit(f"Solution rejected: {assessment['reasons'][0] if assessment['reasons'] else 'Low quality'}")
                    self._wait_iteration_delay()
                    continue
                
                self.progress_signal.emit(70)
                
                # Phase 5: Generate semantic version
                impact_level = 'major' if best_opportunity.impact_score > 0.7 else 'minor' if best_opportunity.impact_score > 0.4 else 'patch'
                version = self.version_manager.generate_semantic_version(
                    best_opportunity.opportunity_type, impact_level
                )
                
                # Phase 6: Execute enhancement
                self.opportunity_signal.emit("Executing enhancement...")
                if is_compound:
                    execution_result = self.execution_pipeline.execute_enhancement(
                        synthetic_opportunity, solution, version
                    )
                else:
                    execution_result = self.execution_pipeline.execute_enhancement(
                        best_opportunity, solution, version
                    )
                
                self.progress_signal.emit(90)
                
                # Phase 7: Record results and measure impact
                if execution_result['success']:
                    self.successful_enhancements += 1
                    
                    # Measure enhancement impact
                    self.opportunity_signal.emit("Measuring enhancement impact...")
                    impact_opportunity = synthetic_opportunity if is_compound else best_opportunity
                    impact_metrics = self.metrics_tracker.measure_enhancement_impact(
                        self.app_path, version, impact_opportunity, solution
                    )
                    
                    enhancement_record = self.version_manager.record_enhancement(
                        version, impact_opportunity, solution, assessment, 
                        execution_result['files_created']
                    )
                    
                    # Record compound enhancement success if applicable
                    if is_compound:
                        self.composition_engine.record_composition_success(
                            best_composition, solution, impact_metrics
                        )
                    
                    # Add impact metrics to record
                    enhancement_record['impact_metrics'] = impact_metrics
                    
                    # Extract success patterns for future learning
                    self.opportunity_signal.emit("Learning from successful enhancement...")
                    if impact_metrics.get('overall_impact_score', 0) > 0.6:
                        patterns = self.pattern_learning.extract_success_patterns([enhancement_record])
                        if patterns:
                            logging.info(f"Extracted {len(patterns)} new success patterns from enhancement v{version}")
                    
                    self.result_signal.emit(
                        f"Enhancement v{version} completed: {best_opportunity.description}",
                        execution_result['files_created'],
                        self.iteration,
                        version
                    )
                    
                    self.opportunity_signal.emit(f"Successfully enhanced to v{version}")
                    
                    # Store in memory for future learning
                    self.processor.memory.store_enhancement_success(
                        best_opportunity, solution, assessment, execution_result
                    )
                    
                    # Recursive self-improvement: analyze and improve enhancement process
                    self._perform_recursive_self_improvement(
                        best_opportunity, solution, assessment, execution_result
                    )
                    
                else:
                    self.failed_enhancements += 1
                    self.opportunity_signal.emit(f"Enhancement failed: {execution_result.get('error_message', 'Unknown error')}")
                
                self.progress_signal.emit(100)
                
                # Reset processor stop flag
                if hasattr(self.processor, 'reset_stop_flag'):
                    self.processor.reset_stop_flag()
                
                # Wait for next iteration
                self._wait_iteration_delay()
                
            except Exception as e:
                logging.error(f"Advanced EnhanceThread error: {e}", exc_info=True)
                self.error_signal.emit(f"Enhancement error: {e}")
                self.failed_enhancements += 1
                break
    
    def _generate_enhancement_solution(self, opportunity: EnhancementOpportunity) -> str:
        """Generate sophisticated enhancement solution using research-driven intelligent prompting"""
        
        # Phase 1: Research best practices and solutions
        self.opportunity_signal.emit(f"Researching solutions for {opportunity.opportunity_type}...")
        research_results = self.research_engine.research_enhancement_solution(opportunity)
        
        # Phase 2: Find applicable learned patterns
        self.opportunity_signal.emit("Analyzing learned patterns...")
        applicable_patterns = self.pattern_learning.find_applicable_patterns(opportunity)
        
        # Build context-aware enhancement prompt with research insights and patterns
        enhanced_prompt = self._build_intelligent_enhancement_prompt(opportunity, research_results, applicable_patterns)
        
        try:
            result = self.processor.process_task(
                enhanced_prompt,
                [self.app_path] + self.files,
                task_type="code",
                use_memory=True,
                auto_continue=False  # Single focused enhancement
            )
            
            if result.success:
                return result.result
            else:
                logging.error(f"Failed to generate enhancement solution: {result.result}")
                return None
                
        except Exception as e:
            logging.error(f"Enhancement solution generation failed: {e}")
            return None
    
    def _build_intelligent_enhancement_prompt(self, opportunity: EnhancementOpportunity, research_results: dict = None, learned_patterns: List[dict] = None) -> str:
        """Build sophisticated, context-aware enhancement prompt with research insights"""
        
        # Determine enhancement strategy based on type
        strategy_templates = {
            'performance': self._get_performance_enhancement_template(),
            'feature': self._get_feature_enhancement_template(),
            'ui_enhancement': self._get_ui_enhancement_template(),
            'ai_enhancement': self._get_ai_enhancement_template(),
            'integration': self._get_integration_enhancement_template(),
            'code_quality': self._get_code_quality_template(),
            'security': self._get_security_enhancement_template()
        }
        
        # Get appropriate template
        template = strategy_templates.get(opportunity.opportunity_type, strategy_templates['feature'])
        
        # Build comprehensive context
        context_info = self._gather_enhancement_context(opportunity)
        
        # Generate research insights section
        research_section = self._format_research_insights(research_results) if research_results else ""
        
        # Generate learned patterns section
        patterns_section = self.pattern_learning.apply_learned_patterns(opportunity, learned_patterns) if learned_patterns else ""
        
        # Construct sophisticated prompt
        prompt = f"""🚀 RECURSIVE ENHANCEMENT ARCHITECT
Advanced AI Systems Engineering - Elite Enhancement Mode

═══════════════════════════════════════════════════════════════════

📊 ENHANCEMENT MISSION PROFILE:
• Classification: {opportunity.opportunity_type.upper()}
• Target: {opportunity.description}
• Impact Potential: {opportunity.impact_score:.2f}/1.0 ({self._get_impact_description(opportunity.impact_score)})
• Complexity Rating: {opportunity.complexity_score:.2f}/1.0 ({self._get_complexity_description(opportunity.complexity_score)})
• Priority Score: {opportunity.priority_score:.2f}
• Target Location: {opportunity.file_path}
{f'• Specific Lines: {opportunity.line_numbers}' if opportunity.line_numbers else ''}

{context_info}

{research_section}

{patterns_section}

{template}

🎯 SPECIFIC ENHANCEMENT DIRECTIVE:
{opportunity.description}

🔧 IMPLEMENTATION REQUIREMENTS:
1. **SOPHISTICATION**: Create production-grade, enterprise-quality code
2. **INNOVATION**: Incorporate cutting-edge patterns and technologies
3. **INTEGRATION**: Seamlessly integrate with existing SuperMini architecture
4. **PERFORMANCE**: Optimize for speed, memory efficiency, and scalability
5. **MAINTAINABILITY**: Write self-documenting, easily extensible code
6. **ROBUSTNESS**: Include comprehensive error handling and edge cases
7. **FUTURE-PROOFING**: Design for extensibility and long-term evolution

💡 ENHANCEMENT PHILOSOPHY:
- Think beyond the immediate requirement
- Anticipate future needs and scalability
- Implement patterns that enable further enhancements
- Create solutions that inspire additional improvements
- Focus on exponential value creation, not just incremental gains

🚀 DELIVERABLE:
Provide complete, immediately implementable Python code that represents a quantum leap in capability, not just an incremental improvement. Make this enhancement a foundation for future recursive improvements.

═══════════════════════════════════════════════════════════════════
BEGIN IMPLEMENTATION:"""

        return prompt
    
    def _select_best_enhancement(self, opportunities: List[EnhancementOpportunity], 
                               compound_compositions: List[dict]) -> dict:
        """Select the best enhancement from individual opportunities and compound compositions"""
        
        # Compare individual opportunities with compound compositions
        best_individual = opportunities[0] if opportunities else None
        best_compound = compound_compositions[0] if compound_compositions else None
        
        # If no compound opportunities, return best individual
        if not best_compound:
            return {'type': 'individual', 'data': best_individual}
        
        # If no individual opportunities, return best compound
        if not best_individual:
            return {'type': 'compound', 'data': best_compound}
        
        # Compare individual vs compound based on impact potential
        individual_score = best_individual.priority_score
        compound_score = best_compound.get('compound_impact_score', 0) / max(best_compound.get('complexity_multiplier', 1), 1)
        
        # Add bonus for compound enhancements (they tend to be more valuable)
        compound_score *= 1.2
        
        # Consider iteration - early iterations favor individual, later favor compounds
        if self.iteration < 3:
            individual_score *= 1.1  # Early bonus for individuals
        else:
            compound_score *= 1.1  # Later bonus for compounds
        
        if compound_score > individual_score:
            return {'type': 'compound', 'data': best_compound}
        else:
            return {'type': 'individual', 'data': best_individual}
    
    def _generate_compound_enhancement_solution(self, composition: dict) -> str:
        """Generate solution for compound enhancement using composition engine"""
        try:
            # Research for compound enhancement (use first component for research focus)
            component_opportunities = composition.get('component_opportunities', [])
            if component_opportunities:
                # Create temporary opportunity object for research
                research_focus_type = component_opportunities[0].get('opportunity_type', 'feature')
                research_focus_desc = composition.get('description', 'compound enhancement')
                
                # Use research engine with compound focus
                self.opportunity_signal.emit("Researching compound enhancement strategies...")
                # Note: For now, we'll skip individual research for compounds to avoid complexity
                research_results = None
                
                # Find applicable patterns for compound enhancements
                self.opportunity_signal.emit("Finding patterns for compound enhancements...")
                # Use pattern learning to find compound-applicable patterns
                applicable_patterns = []
                for comp_opp in component_opportunities:
                    opp_obj = EnhancementOpportunity(
                        comp_opp.get('opportunity_type', 'feature'),
                        comp_opp.get('description', ''),
                        comp_opp.get('impact_score', 0.5),
                        comp_opp.get('complexity_score', 0.5)
                    )
                    patterns = self.pattern_learning.find_applicable_patterns(opp_obj)
                    applicable_patterns.extend(patterns)
                
                # Remove duplicates and keep best patterns
                seen_patterns = set()
                unique_patterns = []
                for pattern in applicable_patterns:
                    pattern_id = pattern.get('pattern_id', '')
                    if pattern_id not in seen_patterns:
                        seen_patterns.add(pattern_id)
                        unique_patterns.append(pattern)
                
                applicable_patterns = unique_patterns[:3]  # Top 3 patterns
                
                # Generate compound solution
                solution = self.composition_engine.generate_compound_enhancement_solution(
                    composition, research_results, applicable_patterns
                )
                
                return solution
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to generate compound enhancement solution: {e}")
            return None
    
    def _format_research_insights(self, research_results: dict) -> str:
        """Format research results into a comprehensive insights section"""
        if not research_results or research_results.get('research_confidence', 0) == 0:
            return ""
        
        insights_section = """🔬 RESEARCH-DRIVEN INSIGHTS:
Research Confidence: {:.1%}

""".format(research_results.get('research_confidence', 0))
        
        # Add best practices
        if research_results.get('best_practices'):
            insights_section += "📚 COMMUNITY BEST PRACTICES:\n"
            for i, practice in enumerate(research_results['best_practices'][:3], 1):
                insights_section += f"• {practice.get('title', 'Best Practice')}\n"
                if practice.get('description'):
                    insights_section += f"  └─ {practice['description'][:100]}...\n"
            insights_section += "\n"
        
        # Add code examples
        if research_results.get('code_examples'):
            insights_section += "💻 IMPLEMENTATION REFERENCES:\n"
            for i, example in enumerate(research_results['code_examples'][:2], 1):
                insights_section += f"• {example.get('title', 'Code Example')}\n"
                if example.get('description'):
                    insights_section += f"  └─ {example['description'][:100]}...\n"
            insights_section += "\n"
        
        # Add performance insights
        if research_results.get('performance_insights'):
            insights_section += "⚡ PERFORMANCE OPTIMIZATION INSIGHTS:\n"
            for i, insight in enumerate(research_results['performance_insights'][:2], 1):
                insights_section += f"• {insight.get('title', 'Performance Insight')}\n"
                if insight.get('description'):
                    insights_section += f"  └─ {insight['description'][:100]}...\n"
            insights_section += "\n"
        
        # Add implementation strategies
        if research_results.get('implementation_strategies'):
            insights_section += "🛠️ IMPLEMENTATION STRATEGIES:\n"
            for i, strategy in enumerate(research_results['implementation_strategies'][:2], 1):
                insights_section += f"• {strategy.get('title', 'Strategy')}\n"
                if strategy.get('description'):
                    insights_section += f"  └─ {strategy['description'][:100]}...\n"
            insights_section += "\n"
        
        # Add related technologies
        if research_results.get('related_technologies'):
            insights_section += "🔧 RELATED TECHNOLOGIES TO CONSIDER:\n"
            for i, tech in enumerate(research_results['related_technologies'][:3], 1):
                insights_section += f"• {tech.get('title', 'Technology')}\n"
            insights_section += "\n"
        
        return insights_section
    
    def _get_performance_enhancement_template(self) -> str:
        return """🏃‍♂️ PERFORMANCE OPTIMIZATION STRATEGY:
• Analyze current bottlenecks and implement algorithmic improvements
• Introduce intelligent caching and memoization where beneficial
• Optimize data structures and processing pipelines
• Consider async/await patterns for non-blocking operations
• Implement efficient batch processing and streaming where applicable
• Add performance monitoring and metrics collection"""
    
    def _get_feature_enhancement_template(self) -> str:
        return """✨ FEATURE ENHANCEMENT STRATEGY:
• Design feature with extensibility and plugin architecture in mind
• Implement comprehensive configuration and customization options
• Add intelligent defaults with advanced user control
• Include robust validation and error handling
• Consider integration with existing workflows and user patterns
• Plan for feature evolution and backward compatibility"""
    
    def _get_ui_enhancement_template(self) -> str:
        return """🎨 UI/UX ENHANCEMENT STRATEGY:
• Focus on intuitive, accessible, and responsive design
• Implement modern UI patterns and visual feedback
• Add keyboard shortcuts and accessibility features
• Consider mobile-first and responsive design principles
• Include user preference persistence and customization
• Implement smooth animations and visual transitions"""
    
    def _get_ai_enhancement_template(self) -> str:
        return """🤖 AI CAPABILITY ENHANCEMENT STRATEGY:
• Leverage latest AI/ML techniques and model capabilities
• Implement intelligent context awareness and learning
• Add predictive features and smart suggestions
• Include model optimization and efficient inference
• Consider multi-modal AI integration where appropriate
• Implement privacy-preserving and ethical AI practices"""
    
    def _get_integration_enhancement_template(self) -> str:
        return """🔗 INTEGRATION ENHANCEMENT STRATEGY:
• Design with microservices and API-first architecture
• Implement robust authentication and authorization
• Add comprehensive logging and monitoring
• Include rate limiting and error recovery mechanisms
• Consider cloud-native and containerization patterns
• Plan for scalability and load balancing"""
    
    def _get_code_quality_template(self) -> str:
        return """🔨 CODE QUALITY ENHANCEMENT STRATEGY:
• Refactor using SOLID principles and design patterns
• Implement comprehensive type hints and documentation
• Add unit tests and integration test coverage
• Consider static analysis and code quality tools
• Implement clean architecture and separation of concerns
• Focus on readability, maintainability, and extensibility"""
    
    def _get_security_enhancement_template(self) -> str:
        return """🔒 SECURITY ENHANCEMENT STRATEGY:
• Implement defense-in-depth security principles
• Add input validation and sanitization
• Include secure authentication and authorization
• Consider encryption for sensitive data
• Implement audit logging and security monitoring
• Follow OWASP guidelines and security best practices"""
    
    def _gather_enhancement_context(self, opportunity: EnhancementOpportunity) -> str:
        """Gather relevant context for enhancement"""
        context = []
        
        # Add memory-based insights if available
        if hasattr(self.processor, 'memory') and self.processor.memory:
            context.append("📚 LEARNED CONTEXT: Previous enhancements and patterns will inform this solution")
        
        # Add file-specific context
        if opportunity.file_path and opportunity.line_numbers:
            context.append(f"📍 SPECIFIC CONTEXT: Focus on {opportunity.file_path} around lines {opportunity.line_numbers}")
        
        # Add complexity guidance
        if opportunity.complexity_score > 0.7:
            context.append("⚠️  HIGH COMPLEXITY: This enhancement requires sophisticated architectural consideration")
        elif opportunity.complexity_score < 0.3:
            context.append("✅ LOW COMPLEXITY: Focus on clean, simple, and efficient implementation")
        
        return "\n".join(context) if context else ""
    
    def _get_impact_description(self, score: float) -> str:
        if score >= 0.8: return "TRANSFORMATIONAL"
        elif score >= 0.6: return "HIGH IMPACT"
        elif score >= 0.4: return "MODERATE IMPACT"
        else: return "INCREMENTAL"
    
    def _get_complexity_description(self, score: float) -> str:
        if score >= 0.8: return "EXPERT LEVEL"
        elif score >= 0.6: return "ADVANCED"
        elif score >= 0.4: return "INTERMEDIATE"
        else: return "STRAIGHTFORWARD"
    
    def _perform_recursive_self_improvement(self, opportunity: EnhancementOpportunity, 
                                          solution: str, assessment: dict, execution_result: dict):
        """Perform recursive self-improvement on the enhancement process itself"""
        try:
            # Analyze success patterns for meta-learning
            success_analysis = self._analyze_enhancement_success_patterns()
            
            # Identify opportunities to improve the enhancement engine itself
            meta_opportunities = self._identify_meta_improvement_opportunities(
                opportunity, solution, assessment, execution_result, success_analysis
            )
            
            # If meta-opportunities found, create self-improvement enhancements
            if meta_opportunities:
                self._create_self_improvement_enhancements(meta_opportunities)
                
        except Exception as e:
            logging.error(f"Recursive self-improvement failed: {e}")
    
    def _analyze_enhancement_success_patterns(self) -> dict:
        """Analyze patterns in successful enhancements for meta-learning"""
        analysis = {
            'successful_types': {},
            'quality_patterns': {},
            'performance_patterns': {},
            'improvement_recommendations': []
        }
        
        # Analyze enhancement history from memory
        if hasattr(self.processor.memory, 'get_enhancement_history'):
            history = self.processor.memory.get_enhancement_history()
            
            # Pattern analysis
            for enhancement in history:
                if enhancement.get('success', False):
                    # Track successful enhancement types
                    etype = enhancement.get('opportunity_type', 'unknown')
                    analysis['successful_types'][etype] = analysis['successful_types'].get(etype, 0) + 1
                    
                    # Analyze quality factors
                    quality_score = enhancement.get('assessment', {}).get('quality_score', 0)
                    if quality_score > 0.8:
                        analysis['quality_patterns']['high_quality'] = analysis['quality_patterns'].get('high_quality', 0) + 1
        
        # Generate improvement recommendations
        if analysis['successful_types']:
            most_successful = max(analysis['successful_types'], key=analysis['successful_types'].get)
            analysis['improvement_recommendations'].append(
                f"Focus more on {most_successful} enhancements - highest success rate"
            )
        
        return analysis
    
    def _identify_meta_improvement_opportunities(self, opportunity: EnhancementOpportunity, 
                                               solution: str, assessment: dict, 
                                               execution_result: dict, success_analysis: dict) -> List[EnhancementOpportunity]:
        """Identify opportunities to improve the enhancement engine itself"""
        meta_opportunities = []
        
        # Check if discovery engine could be improved
        if opportunity.impact_score < 0.5:
            meta_opportunities.append(EnhancementOpportunity(
                'recursive_improvement',
                'Enhance discovery engine to find higher-impact opportunities',
                0.8, 0.6, str(self.app_path), [1249, 1600]  # Discovery engine lines
            ))
        
        # Check if quality assessment could be improved
        if assessment.get('quality_score', 0) < 0.7:
            meta_opportunities.append(EnhancementOpportunity(
                'recursive_improvement',
                'Improve quality assessment algorithms for better evaluation',
                0.7, 0.5, str(self.app_path), [1630, 1900]  # Quality assessment lines
            ))
        
        # Check if execution pipeline could be optimized
        if execution_result.get('performance_metrics', {}).get('performance_score', 1.0) < 0.8:
            meta_opportunities.append(EnhancementOpportunity(
                'recursive_improvement',
                'Optimize execution pipeline for better performance',
                0.8, 0.7, str(self.app_path), [2786, 3200]  # Execution pipeline lines
            ))
        
        # Learning-based improvements from success patterns
        if success_analysis.get('improvement_recommendations'):
            for recommendation in success_analysis['improvement_recommendations']:
                meta_opportunities.append(EnhancementOpportunity(
                    'recursive_improvement',
                    f"Meta-learning improvement: {recommendation}",
                    0.9, 0.8, str(self.app_path)
                ))
        
        return meta_opportunities
    
    def _create_self_improvement_enhancements(self, meta_opportunities: List[EnhancementOpportunity]):
        """Create and queue self-improvement enhancements"""
        for meta_opp in meta_opportunities:
            # Generate meta-enhancement solution
            meta_solution = self._generate_meta_enhancement_solution(meta_opp)
            
            if meta_solution:
                # Store meta-enhancement for future processing
                self.processor.memory.store_meta_enhancement(
                    meta_opp, meta_solution, self.iteration
                )
                
                log_activity(
                    ActivityType.SYSTEM_EVENT,
                    ActivityLevel.INFO,
                    "Recursive Self-Improvement",
                    f"Created meta-enhancement: {meta_opp.description}",
                    {
                        "meta_opportunity": meta_opp.to_dict(),
                        "iteration": self.iteration,
                        "improvement_type": "recursive"
                    }
                )
    
    def _generate_meta_enhancement_solution(self, meta_opportunity: EnhancementOpportunity) -> str:
        """Generate solutions for improving the enhancement engine itself"""
        meta_prompt = f"""🔄 RECURSIVE ENHANCEMENT ARCHITECT - META-IMPROVEMENT MODE

You are now operating in RECURSIVE SELF-IMPROVEMENT mode. Your task is to enhance the enhancement engine itself.

META-ENHANCEMENT TARGET:
{meta_opportunity.description}

This is a meta-level improvement - you're improving the very system that creates improvements. This requires:

1. **DEEP SYSTEM UNDERSTANDING**: Analyze how the current enhancement system works
2. **ARCHITECTURAL INSIGHT**: Identify systemic improvements, not just code fixes  
3. **RECURSIVE THINKING**: Design improvements that enable future improvements
4. **EXPONENTIAL IMPACT**: Create changes that compound over time

FOCUS AREAS FOR META-IMPROVEMENT:
- Enhancement discovery algorithms
- Quality assessment sophistication  
- Execution pipeline robustness
- Learning and adaptation mechanisms
- Success pattern recognition
- Failure analysis and recovery

REQUIREMENTS:
- Create improvements that improve the improvement process
- Design self-modifying, self-optimizing systems
- Implement learning mechanisms that compound
- Build in recursive feedback loops
- Ensure meta-improvements are measurable

Generate a sophisticated meta-enhancement that will make future enhancements more intelligent, effective, and autonomous."""

        try:
            result = self.processor.process_task(
                meta_prompt,
                [self.app_path],
                task_type="code",
                use_memory=True,
                auto_continue=False
            )
            
            return result.result if result.success else None
            
        except Exception as e:
            logging.error(f"Meta-enhancement generation failed: {e}")
            return None
    
    def _wait_iteration_delay(self):
        """Wait for the specified iteration delay while checking for stop signals"""
        if self.iteration_delay > 0:
            for _ in range(int(self.iteration_delay)):
                if not self.running:
                    break
                time.sleep(1)

class SettingsDialog(QDialog):
    """Modern settings configuration dialog with tabbed interface"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ SuperMini Settings")
        
        # Dynamic sizing based on screen size and DPI
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            available_geometry = screen.availableGeometry()
            
            # Calculate dialog size as percentage of available screen space
            width = min(ModernTheme.scale_value(200), int(available_geometry.width() * 0.4))
            height = min(ModernTheme.scale_value(300), int(available_geometry.height() * 0.7))
            
            self.setMinimumSize(ModernTheme.scale_value(200), ModernTheme.scale_value(300))
            self.setMaximumSize(int(available_geometry.width() * 0.8), int(available_geometry.height() * 0.9))
            self.resize(width, height)
        else:
            # Fallback for older screens
            self.setMinimumSize(400, 500)
            self.resize(500, 600)
            
        self.setup_ui()
        self.load_settings()
        
        # Apply modern styling
        self.setStyleSheet(parent.styleSheet() if parent else "")
    
    def setup_ui(self):
        """Setup the modern settings UI with tabs"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("🤖 SuperMini Configuration")
        header_label.setProperty("role", "heading")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Version info
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setProperty("role", "caption")
        header_layout.addWidget(version_label)
        
        main_layout.addLayout(header_layout)
        
        # Tabbed settings
        settings_tabs = QTabWidget()
        
        # AI Models Tab
        ai_tab = self.create_ai_models_tab()
        settings_tabs.addTab(ai_tab, "🤖 AI Models")
        
        # Generation Tab
        gen_tab = self.create_generation_tab()
        settings_tabs.addTab(gen_tab, "⚙️ Generation")
        
        # System Tab
        system_tab = self.create_system_settings_tab()
        settings_tabs.addTab(system_tab, "💻 System")
        
        main_layout.addWidget(settings_tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = self.parent().create_button(
            "Reset to Defaults",
            "🔄",
            "secondary",
            "Reset all settings to default values",
            120,
            self.reset_settings
        )
        
        cancel_btn = self.parent().create_button(
            "Cancel",
            "❌",
            "secondary",
            "Cancel without saving changes",
            100,
            self.reject
        )
        
        save_btn = self.parent().create_button(
            "Save Settings",
            "💾",
            "primary",
            "Save current settings",
            140,
            self.save_settings
        )
        save_btn.setDefault(True)
        save_btn.setProperty("variant", "primary")
        save_btn.setToolTip("Save all configuration changes")
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def create_ai_models_tab(self) -> QWidget:
        """Create AI models configuration tab with Claude as primary and Ollama as backup"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # AI Model Selection Section
        model_selection_group = QGroupBox("🤖 AI Model Selection")
        model_selection_layout = QVBoxLayout()
        model_selection_layout.setContentsMargins(16, 20, 16, 16)
        model_selection_layout.setSpacing(16)
        
        # Primary model selection
        primary_layout = QVBoxLayout()
        primary_layout.setSpacing(8)
        primary_label = QLabel("Primary AI Model:")
        primary_label.setProperty("role", "heading")
        
        self.primary_model = QComboBox()
        self.primary_model.addItems(["Claude API (Recommended)", "Local Ollama Models"])
        self.primary_model.setCurrentText("Claude API (Recommended)")
        self.primary_model.currentTextChanged.connect(self.on_primary_model_changed)
        self.primary_model.setToolTip("Choose your primary AI model for all operations")
        
        primary_layout.addWidget(primary_label)
        primary_layout.addWidget(self.primary_model)
        
        model_selection_layout.addLayout(primary_layout)
        model_selection_group.setLayout(model_selection_layout)
        
        # Claude API Section
        self.claude_group = QGroupBox("🔵 Claude API Configuration")
        claude_layout = QVBoxLayout()
        claude_layout.setContentsMargins(16, 20, 16, 16)
        claude_layout.setSpacing(12)
        
        # Claude status and info
        claude_info = QLabel("✨ Claude is Anthropic's advanced AI assistant, optimized for reasoning, coding, and analysis.")
        claude_info.setProperty("role", "caption")
        claude_info.setWordWrap(True)
        claude_info.setStyleSheet("color: #4CAF50; padding: 8px; background: rgba(76, 175, 80, 0.1); border-radius: 4px; margin-bottom: 8px;")
        
        api_key_layout = QVBoxLayout()
        api_key_layout.setSpacing(8)
        api_key_label = QLabel("API Key:")
        api_key_label.setProperty("role", "heading")
        
        self.claude_key = QLineEdit()
        self.claude_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_key.setPlaceholderText("Enter your Claude API key (sk-ant-...)")
        self.claude_key.setToolTip("Your Claude API key from Anthropic Console")
        
        show_key_btn = self.parent().create_button(
            "Show/Hide",
            "👁️",
            "secondary",
            "Toggle API key visibility",
            80,
            self.toggle_api_key_visibility
        )
        show_key_btn.setMaximumWidth(ModernTheme.scale_value(80))
        
        key_row = QHBoxLayout()
        key_row.addWidget(self.claude_key)
        key_row.addWidget(show_key_btn)
        
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addLayout(key_row)
        
        # Get API key link
        get_key_label = QLabel('<a href="https://console.anthropic.com/" style="color: #2196F3;">🔗 Get your Claude API key from Anthropic Console</a>')
        get_key_label.setOpenExternalLinks(True)
        get_key_label.setProperty("role", "caption")
        
        claude_layout.addWidget(claude_info)
        claude_layout.addLayout(api_key_layout)
        claude_layout.addWidget(get_key_label)
        self.claude_group.setLayout(claude_layout)
        
        # Ollama Section
        self.ollama_group = QGroupBox("🟠 Local Ollama Models (Backup)")
        ollama_layout = QVBoxLayout()
        ollama_layout.setContentsMargins(16, 20, 16, 16)
        ollama_layout.setSpacing(12)
        
        # Ollama info
        ollama_info = QLabel("🔒 Ollama provides privacy-focused local AI models that run on your computer.")
        ollama_info.setProperty("role", "caption")
        ollama_info.setWordWrap(True)
        ollama_info.setStyleSheet("color: #FF9800; padding: 8px; background: rgba(255, 152, 0, 0.1); border-radius: 4px; margin-bottom: 8px;")
        
        # Server URL
        url_layout = QVBoxLayout()
        url_layout.setSpacing(8)
        url_label = QLabel("Ollama Server URL:")
        url_label.setProperty("role", "heading")
        
        self.ollama_url = QLineEdit("http://localhost:11434")
        self.ollama_url.setToolTip("URL of your Ollama server")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.ollama_url)
        
        # Available models
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)
        model_label = QLabel("Available Models:")
        model_label.setProperty("role", "heading")
        
        self.ollama_model = QComboBox()
        self.ollama_model.setToolTip("Select from locally installed Ollama models")
        
        # Refresh models button
        refresh_btn = self.parent().create_button(
            "Refresh Models",
            "🔄",
            "secondary",
            "Refresh the list of available Ollama models",
            140,
            self.refresh_ollama_models
        )
        
        model_row = QHBoxLayout()
        model_row.addWidget(self.ollama_model, 3)
        model_row.addWidget(refresh_btn, 1)
        
        model_layout.addWidget(model_label)
        model_layout.addLayout(model_row)
        
        # Model installation instructions
        self.ollama_instructions = QLabel()
        self.ollama_instructions.setProperty("role", "caption")
        self.ollama_instructions.setWordWrap(True)
        
        # Test connection button
        test_btn = self.parent().create_button(
            "Test Connection",
            "🔗",
            "primary",
            "Test connection to Ollama server and check available models",
            140,
            self.test_ollama_connection
        )
        
        ollama_layout.addWidget(ollama_info)
        ollama_layout.addLayout(url_layout)
        ollama_layout.addLayout(model_layout)
        ollama_layout.addWidget(self.ollama_instructions)
        ollama_layout.addWidget(test_btn)
        self.ollama_group.setLayout(ollama_layout)
        
        # Initially set up the UI based on default selection
        self.on_primary_model_changed("Claude API (Recommended)")
        
        layout.addWidget(model_selection_group)
        layout.addWidget(self.claude_group)
        layout.addWidget(self.ollama_group)
        layout.addStretch()
        
        # Load available Ollama models on tab creation
        self.refresh_ollama_models()
        
        tab.setLayout(layout)
        return tab
    
    def create_generation_tab(self) -> QWidget:
        """Create generation settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Generation Parameters
        gen_group = QGroupBox("🎛️ Generation Parameters")
        gen_layout = QVBoxLayout()
        gen_layout.setContentsMargins(16, 20, 16, 16)
        gen_layout.setSpacing(16)
        
        # Max Tokens
        tokens_layout = QVBoxLayout()
        tokens_layout.setSpacing(8)
        tokens_label = QLabel("Maximum Tokens:")
        tokens_label.setProperty("role", "heading")
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(512, 8192)
        self.max_tokens.setValue(4096)
        self.max_tokens.setSuffix(" tokens")
        self.max_tokens.setToolTip("Maximum number of tokens in AI response")
        
        tokens_layout.addWidget(tokens_label)
        tokens_layout.addWidget(self.max_tokens)
        
        # Autonomous Intelligence Status
        ai_status_layout = QVBoxLayout()
        ai_status_layout.setSpacing(8)
        ai_status_label = QLabel("Autonomous Intelligence:")
        ai_status_label.setProperty("role", "heading")
        
        ai_status_info = QLabel("✅ Temperature automatically optimized based on task type\n"
                               "✅ Continuation decisions based on response quality analysis\n"
                               "✅ Task-specific prompts for optimal performance")
        ai_status_info.setProperty("role", "caption")
        ai_status_info.setWordWrap(True)
        ai_status_info.setStyleSheet("color: #4CAF50; padding: 8px; background: rgba(76, 175, 80, 0.1); border-radius: 4px;")
        
        ai_status_layout.addWidget(ai_status_label)
        ai_status_layout.addWidget(ai_status_info)
        
        gen_layout.addLayout(tokens_layout)
        gen_layout.addLayout(ai_status_layout)
        gen_group.setLayout(gen_layout)
        
        layout.addWidget(gen_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_memory_tab(self) -> QWidget:
        """Create memory management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Memory Settings
        memory_group = QGroupBox("🧠 Memory & Context Management")
        memory_layout = QVBoxLayout()
        memory_layout.setContentsMargins(16, 20, 16, 16)
        memory_layout.setSpacing(16)
        
        # Memory status
        status_layout = QHBoxLayout()
        memory_status_label = QLabel("Memory System Status:")
        memory_status_label.setProperty("role", "heading")
        
        # Check if memory is available
        if hasattr(self.parent(), 'memory') and self.parent().memory.collection:
            status_indicator = QLabel("✅ Active")
            status_indicator.setProperty("role", "success")
        else:
            status_indicator = QLabel("❌ Unavailable")
            status_indicator.setProperty("role", "error")
        
        status_layout.addWidget(memory_status_label)
        status_layout.addWidget(status_indicator)
        status_layout.addStretch()
        
        # Memory settings
        self.enable_memory = QCheckBox("Enable Context Memory")
        self.enable_memory.setChecked(True)
        self.enable_memory.setToolTip("Remember task history for better context")
        
        self.memory_limit = QSpinBox()
        self.memory_limit.setRange(10, 1000)
        self.memory_limit.setValue(100)
        self.memory_limit.setSuffix(" items")
        self.memory_limit.setToolTip("Maximum number of items to keep in memory")
        
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Memory Limit:"))
        limit_layout.addWidget(self.memory_limit)
        limit_layout.addStretch()
        
        # Memory actions
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(12)
        
        view_memory_btn = self.parent().create_button(
            "View Statistics",
            "📊",
            "secondary",
            "View memory usage and statistics",
            140,
            self.view_memory_stats
        )
        
        export_memory_btn = self.parent().create_button(
            "Export Memory",
            "💾",
            "secondary",
            "Export memory data to file",
            120,
            self.export_memory
        )
        
        clear_memory_btn = self.parent().create_button(
            "Clear All Memory",
            ModernIcons.ACTIONS['delete'],
            "danger",
            "Permanently delete all memory data",
            140,
            self.clear_memory
        )
        
        actions_layout.addWidget(view_memory_btn)
        actions_layout.addWidget(export_memory_btn)
        actions_layout.addWidget(clear_memory_btn)
        
        memory_layout.addLayout(status_layout)
        memory_layout.addWidget(self.enable_memory)
        memory_layout.addLayout(limit_layout)
        memory_layout.addLayout(actions_layout)
        memory_group.setLayout(memory_layout)
        
        layout.addWidget(memory_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_system_settings_tab(self) -> QWidget:
        """Create system settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)
        
        # Application Settings
        app_group = QGroupBox("📱 Application Settings")
        app_layout = QVBoxLayout()
        app_layout.setContentsMargins(16, 20, 16, 16)
        app_layout.setSpacing(12)
        
        self.auto_save = QCheckBox("Auto-save Generated Files")
        self.auto_save.setChecked(True)
        self.auto_save.setToolTip("Automatically save generated files to output directory")
        
        self.dark_mode = QCheckBox("Dark Mode Interface")
        self.dark_mode.setChecked(True)
        self.dark_mode.setToolTip("Use dark theme (requires restart)")
        
        self.show_notifications = QCheckBox("Show System Notifications")
        self.show_notifications.setChecked(True)
        self.show_notifications.setToolTip("Show desktop notifications for task completion")
        
        app_layout.addWidget(self.auto_save)
        app_layout.addWidget(self.dark_mode)
        app_layout.addWidget(self.show_notifications)
        app_group.setLayout(app_layout)
        
        # Output Directory
        output_group = QGroupBox("📁 Output Directory")
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(16, 20, 16, 16)
        output_layout.setSpacing(12)
        
        current_dir_label = QLabel(f"Current: {Path.home() / 'SuperMini_Output'}")
        current_dir_label.setProperty("role", "caption")
        
        dir_buttons_layout = QHBoxLayout()
        open_dir_btn = self.parent().create_button(
            "Open Directory",
            "📂",
            "secondary",
            "Open output directory in Finder",
            140,
            self.open_output_directory
        )
        
        change_dir_btn = self.parent().create_button(
            "Change Directory",
            "📝",
            "secondary",
            "Change the output directory location",
            140,
            self.change_output_directory
        )
        
        dir_buttons_layout.addWidget(open_dir_btn)
        dir_buttons_layout.addWidget(change_dir_btn)
        dir_buttons_layout.addStretch()
        
        output_layout.addWidget(current_dir_label)
        output_layout.addLayout(dir_buttons_layout)
        output_group.setLayout(output_layout)
        
        # Logging Settings
        logging_group = QGroupBox("📋 Logging Settings")
        logging_layout = QVBoxLayout()
        logging_layout.setContentsMargins(16, 20, 16, 16)
        logging_layout.setSpacing(12)
        
        self.enable_logging = QCheckBox("Enable Detailed Logging")
        self.enable_logging.setChecked(True)
        self.enable_logging.setToolTip("Log detailed application activity")
        
        log_level_layout = QHBoxLayout()
        log_level_layout.addWidget(QLabel("Log Level:"))
        
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level.setCurrentText("INFO")
        self.log_level.setToolTip("Set the logging verbosity level")
        
        log_level_layout.addWidget(self.log_level)
        log_level_layout.addStretch()
        
        view_logs_btn = self.parent().create_button(
            "View Log Files",
            "📄",
            "secondary",
            "Open log file directory",
            120,
            self.view_log_files
        )
        
        logging_layout.addWidget(self.enable_logging)
        logging_layout.addLayout(log_level_layout)
        logging_layout.addWidget(view_logs_btn)
        logging_group.setLayout(logging_layout)
        
        layout.addWidget(app_group)
        layout.addWidget(output_group)
        layout.addWidget(logging_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.claude_key.echoMode() == QLineEdit.EchoMode.Password:
            self.claude_key.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.claude_key.setEchoMode(QLineEdit.EchoMode.Password)
    
    def on_primary_model_changed(self, model_choice: str):
        """Handle primary model selection change"""
        if model_choice == "Claude API (Recommended)":
            # Emphasize Claude, de-emphasize Ollama
            self.claude_group.setTitle("🔵 Claude API Configuration (Primary)")
            self.ollama_group.setTitle("🟠 Local Ollama Models (Backup)")
            self.claude_group.setEnabled(True)
            self.ollama_group.setEnabled(True)
        else:  # Local Ollama Models
            # Emphasize Ollama, de-emphasize Claude
            self.claude_group.setTitle("🔵 Claude API Configuration (Backup)")
            self.ollama_group.setTitle("🟠 Local Ollama Models (Primary)")
            self.claude_group.setEnabled(True)
            self.ollama_group.setEnabled(True)
    
    def refresh_ollama_models(self):
        """Refresh the list of available Ollama models from local installation"""
        self.ollama_model.clear()
        
        try:
            import requests
            response = requests.get(f"{self.ollama_url.text()}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get('models', [])
                
                if models:
                    # Add available models
                    for model in models:
                        model_name = model.get('name', '')
                        if model_name:
                            self.ollama_model.addItem(model_name)
                    
                    # Set default selection
                    if self.ollama_model.count() > 0:
                        # Prefer coding models
                        preferred_models = ['qwen2.5-coder:7b', 'codellama:7b', 'llama3.2:3b']
                        for preferred in preferred_models:
                            for i in range(self.ollama_model.count()):
                                if preferred in self.ollama_model.itemText(i):
                                    self.ollama_model.setCurrentIndex(i)
                                    break
                    
                    self.ollama_instructions.setText(f"✅ Found {len(models)} local model(s). Select your preferred model above.")
                    self.ollama_instructions.setStyleSheet("color: #4CAF50; padding: 8px; background: rgba(76, 175, 80, 0.1); border-radius: 4px;")
                else:
                    self._show_ollama_install_instructions()
            else:
                self._show_ollama_install_instructions()
                
        except Exception as e:
            self._show_ollama_install_instructions()
    
    def _show_ollama_install_instructions(self):
        """Show instructions for installing Ollama models"""
        instructions = """❌ No Ollama models found. To use local models:

1. Install Ollama: https://ollama.ai/download
2. Open terminal and run: ollama serve
3. Install models (recommended):
   • ollama pull qwen2.5-coder:7b  (coding tasks)
   • ollama pull llama3.2:3b  (general tasks)
   • ollama pull codellama:7b  (code generation)
4. Click 'Refresh Models' to reload the list

Visit https://ollama.ai/library for more models."""
        
        self.ollama_instructions.setText(instructions)
        self.ollama_instructions.setStyleSheet("color: #FF5722; padding: 12px; background: rgba(255, 87, 34, 0.1); border-radius: 4px; border-left: 4px solid #FF5722;")
        
        # Add fallback models to dropdown for manual selection
        fallback_models = [
            "qwen2.5-coder:7b",
            "llama3.2:3b", 
            "codellama:7b",
            "deepseek-coder:6.7b",
            "starcoder2:7b"
        ]
        
        for model in fallback_models:
            self.ollama_model.addItem(f"{model} (not installed)")
        
        if self.ollama_model.count() > 0:
            self.ollama_model.setCurrentIndex(0)
    
    def test_ollama_connection(self):
        """Test connection to Ollama server and refresh models list"""
        try:
            import requests
            response = requests.get(f"{self.ollama_url.text()}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = models_data.get('models', [])
                
                # Refresh the models list
                self.refresh_ollama_models()
                
                if models:
                    QMessageBox.information(self, "Connection Test", 
                                          f"✅ Successfully connected to Ollama server!\n\n"
                                          f"Found {len(models)} available model(s):\n" + 
                                          "\n".join([f"• {model.get('name', 'Unknown')}" for model in models[:5]]) +
                                          (f"\n... and {len(models) - 5} more" if len(models) > 5 else ""))
                else:
                    QMessageBox.warning(self, "Connection Test", 
                                      "✅ Connected to Ollama server, but no models are installed.\n\n"
                                      "Install models using:\n"
                                      "• ollama pull qwen2.5-coder:7b\n"
                                      "• ollama pull llama3.2:3b")
            else:
                QMessageBox.warning(self, "Connection Test", f"❌ Server responded with status {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Connection Test", f"❌ Failed to connect to Ollama server:\n{e}\n\n"
                              "Make sure Ollama is installed and running:\n"
                              "1. Install from https://ollama.ai/download\n"
                              "2. Run 'ollama serve' in terminal")
    
    def view_memory_stats(self):
        """Show memory statistics"""
        # This would show memory usage statistics
        QMessageBox.information(self, "Memory Statistics", "Memory statistics feature coming soon!")
    
    def export_memory(self):
        """Export memory data"""
        # This would export memory data
        QMessageBox.information(self, "Export Memory", "Memory export feature coming soon!")
    
    def open_output_directory(self):
        """Open output directory"""
        import subprocess
        try:
            subprocess.run(['open', str(Path.home() / 'SuperMini_Output')], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open directory: {e}")
    
    def change_output_directory(self):
        """Change output directory"""
        # This would allow changing the output directory
        QMessageBox.information(self, "Change Directory", "Output directory change feature coming soon!")
    
    def view_log_files(self):
        """Open log file directory"""
        import subprocess
        try:
            subprocess.run(['open', str(Path.home() / 'SuperMini_Output' / 'logs')], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open log directory: {e}")
    
    def reset_settings(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all settings to defaults
            self.use_claude.setChecked(True)
            self.claude_key.setText("")
            self.ollama_url.setText("http://localhost:11434")
            self.ollama_model.setCurrentText("qwen2.5-coder:7b")
            self.max_tokens.setValue(4096)
            # Temperature is now automatically managed
            self.enable_memory.setChecked(True)
            self.auto_save.setChecked(True)
            self.dark_mode.setChecked(True)
            QMessageBox.information(self, "Settings", "All settings have been reset to defaults.")
    
    def load_settings(self):
        """Load settings from QSettings"""
        settings = QSettings()
        
        # AI Models - Primary model selection
        primary_model = settings.value("primary_model", "Claude API (Recommended)")
        self.primary_model.setCurrentText(primary_model)
        self.on_primary_model_changed(primary_model)
        
        # Claude settings
        self.claude_key.setText(settings.value("claude_api_key", ""))
        
        # Ollama settings
        self.ollama_url.setText(settings.value("ollama_url", "http://localhost:11434"))
        saved_model = settings.value("ollama_model", "qwen2.5-coder:7b")
        # Set the model after refreshing the list
        if self.ollama_model.count() > 0:
            for i in range(self.ollama_model.count()):
                if saved_model in self.ollama_model.itemText(i):
                    self.ollama_model.setCurrentIndex(i)
                    break
        
        # Generation
        self.max_tokens.setValue(settings.value("max_tokens", 4096, type=int))
        # Temperature is now automatically managed by task intelligence
        if hasattr(self, 'memory_limit'):
            self.memory_limit.setValue(settings.value("memory_limit", 100, type=int))
        if hasattr(self, 'auto_save'):
            self.auto_save.setChecked(settings.value("auto_save", True, type=bool))
        if hasattr(self, 'dark_mode'):
            self.dark_mode.setChecked(settings.value("dark_mode", True, type=bool))
        if hasattr(self, 'show_notifications'):
            self.show_notifications.setChecked(settings.value("show_notifications", True, type=bool))
        if hasattr(self, 'enable_logging'):
            self.enable_logging.setChecked(settings.value("enable_logging", True, type=bool))
        if hasattr(self, 'log_level'):
            self.log_level.setCurrentText(settings.value("log_level", "INFO"))
    
    def save_settings(self):
        """Save all settings to QSettings"""
        settings = QSettings()
        
        # AI Models - Save primary model selection
        settings.setValue("primary_model", self.primary_model.currentText())
        settings.setValue("claude_api_key", self.claude_key.text())
        settings.setValue("use_claude", self.use_claude.isChecked())
        settings.setValue("ollama_url", self.ollama_url.text())
        settings.setValue("ollama_model", self.ollama_model.currentText())
        
        # Generation
        settings.setValue("max_tokens", self.max_tokens.value())
        # Temperature is now automatically managed by task intelligence
        
        # Save new settings
        if hasattr(self, 'markdown_output'):
            settings.setValue("markdown_output", self.markdown_output.isChecked())
        if hasattr(self, 'code_highlighting'):
            settings.setValue("code_highlighting", self.code_highlighting.isChecked())
        if hasattr(self, 'enable_memory'):
            settings.setValue("enable_memory", self.enable_memory.isChecked())
        if hasattr(self, 'memory_limit'):
            settings.setValue("memory_limit", self.memory_limit.value())
        if hasattr(self, 'auto_save'):
            settings.setValue("auto_save", self.auto_save.isChecked())
        if hasattr(self, 'dark_mode'):
            settings.setValue("dark_mode", self.dark_mode.isChecked())
        if hasattr(self, 'show_notifications'):
            settings.setValue("show_notifications", self.show_notifications.isChecked())
        if hasattr(self, 'enable_logging'):
            settings.setValue("enable_logging", self.enable_logging.isChecked())
        if hasattr(self, 'log_level'):
            settings.setValue("log_level", self.log_level.currentText())
        
        QMessageBox.information(self, "Settings Saved", "✅ All settings have been saved successfully!")
        self.accept()
    
    def clear_memory(self):
        reply = QMessageBox.question(
            self, "Clear Memory",
            "Are you sure you want to clear all memory data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                memory_dir = Path.home() / "SuperMini_Output" / "data" / "memory"
                if memory_dir.exists():
                    shutil.rmtree(memory_dir)
                    memory_dir.mkdir(parents=True, exist_ok=True)
                QMessageBox.information(self, "Memory", "Memory cleared successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear memory: {e}")

class SystemMonitor(QThread):
    """Enhanced system resource and usage monitoring thread with advanced analytics"""
    update_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.start_time = time.time()
        self.last_network_check = time.time()
        self.last_network_stats = None
        
        # Enhanced statistics tracking
        self.stats = {
            'total_prompts': 0,
            'claude_prompts': 0,
            'ollama_prompts': 0,
            'total_tokens': 0,
            'errors': 0,
            'files_generated': 0,
            'memory_items': 0,
            'task_types': {t: 0 for t in TASK_TYPES},
            'autonomous_actions': 0,
            'safety_checks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'auto_continues': 0
        }
        
        # Performance history for trends
        self.performance_history = {
            'cpu': [],
            'memory': [],
            'network_up': [],
            'network_down': [],
            'timestamps': []
        }
        self.max_history = 60  # Keep last 60 data points (2 minutes at 2s intervals)
    
    def update_stats(self, stat_type: str, value: int = 1):
        """Update monitoring statistics"""
        if stat_type in self.stats:
            if isinstance(self.stats[stat_type], dict):
                # For nested stats like task_types
                if value in self.stats[stat_type]:
                    self.stats[stat_type][value] += 1
            else:
                self.stats[stat_type] += value
    
    def get_elapsed_time(self) -> str:
        """Get formatted elapsed time since monitoring started"""
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_network_speed(self) -> Tuple[float, float]:
        """Get current network upload/download speeds in MB/s with improved accuracy"""
        try:
            current_time = time.time()
            net_io = psutil.net_io_counters()
            
            if self.last_network_stats is None:
                self.last_network_stats = net_io
                self.last_network_check = current_time
                return 0.0, 0.0
            
            time_diff = current_time - self.last_network_check
            if time_diff < 1.0:  # Don't calculate if less than 1 second
                return 0.0, 0.0
            
            upload_speed = (net_io.bytes_sent - self.last_network_stats.bytes_sent) / time_diff / 1024 / 1024
            download_speed = (net_io.bytes_recv - self.last_network_stats.bytes_recv) / time_diff / 1024 / 1024
            
            self.last_network_stats = net_io
            self.last_network_check = current_time
            
            return max(0, upload_speed), max(0, download_speed)
        except:
            return 0.0, 0.0
    
    def update_performance_history(self, cpu: float, memory: float, upload: float, download: float):
        """Update performance history for trend analysis"""
        current_time = time.time()
        
        self.performance_history['cpu'].append(cpu)
        self.performance_history['memory'].append(memory)
        self.performance_history['network_up'].append(upload)
        self.performance_history['network_down'].append(download)
        self.performance_history['timestamps'].append(current_time)
        
        # Keep only recent history
        for key in self.performance_history:
            if len(self.performance_history[key]) > self.max_history:
                self.performance_history[key] = self.performance_history[key][-self.max_history:]
    
    def get_performance_trends(self) -> Dict[str, str]:
        """Analyze performance trends over time"""
        trends = {}
        
        for metric in ['cpu', 'memory', 'network_up', 'network_down']:
            data = self.performance_history[metric]
            if len(data) < 5:
                trends[metric] = "insufficient_data"
                continue
            
            # Calculate trend over last 10 data points
            recent_data = data[-10:]
            if len(recent_data) < 5:
                trends[metric] = "stable"
                continue
            
            # Simple trend analysis
            first_half = sum(recent_data[:len(recent_data)//2]) / (len(recent_data)//2)
            second_half = sum(recent_data[len(recent_data)//2:]) / (len(recent_data) - len(recent_data)//2)
            
            change_percent = ((second_half - first_half) / max(first_half, 0.1)) * 100
            
            if change_percent > 15:
                trends[metric] = "increasing"
            elif change_percent < -15:
                trends[metric] = "decreasing"
            else:
                trends[metric] = "stable"
        
        return trends
    
    def get_system_health_score(self, metrics: Dict) -> Tuple[int, str]:
        """Calculate overall system health score (0-100)"""
        score = 100
        issues = []
        
        # CPU health
        if metrics['cpu'] > 90:
            score -= 25
            issues.append("High CPU usage")
        elif metrics['cpu'] > 70:
            score -= 10
            issues.append("Elevated CPU usage")
        
        # Memory health
        if metrics['memory'] > 95:
            score -= 30
            issues.append("Critical memory usage")
        elif metrics['memory'] > 85:
            score -= 15
            issues.append("High memory usage")
        
        # Disk health
        if metrics['disk'] > 95:
            score -= 20
            issues.append("Disk nearly full")
        elif metrics['disk'] > 85:
            score -= 10
            issues.append("Low disk space")
        
        # Error rate
        error_rate = metrics.get('errors', 0) / max(metrics.get('total_prompts', 1), 1) * 100
        if error_rate > 10:
            score -= 15
            issues.append("High error rate")
        elif error_rate > 5:
            score -= 5
            issues.append("Elevated error rate")
        
        # Task success rate
        total_tasks = metrics.get('successful_tasks', 0) + metrics.get('failed_tasks', 0)
        if total_tasks > 0:
            success_rate = metrics.get('successful_tasks', 0) / total_tasks * 100
            if success_rate < 80:
                score -= 10
                issues.append("Low task success rate")
        
        score = max(0, min(100, score))
        
        if score >= 90:
            status = "Excellent"
        elif score >= 80:
            status = "Good"
        elif score >= 70:
            status = "Fair"
        elif score >= 50:
            status = "Poor"
        else:
            status = "Critical"
        
        return score, status
    
    def get_cpu_temperature(self) -> float:
        """Get CPU temperature without requiring sudo"""
        try:
            # Try different methods for getting CPU temperature without sudo
            
            # Method 1: Try istats (if available)
            try:
                temp_output = subprocess.check_output(
                    ['istats', 'cpu', 'temp', '--value-only'], 
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=2
                )
                return float(temp_output.strip())
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Method 2: Try osx-cpu-temp (if available)
            try:
                temp_output = subprocess.check_output(
                    ['osx-cpu-temp'], 
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=2
                )
                # Output format: "61.8°C"
                temp_match = re.search(r'([\d.]+)°?C', temp_output)
                if temp_match:
                    return float(temp_match.group(1))
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Method 3: Try thermal sensors via psutil (limited support)
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Find CPU temperature
                        for name, entries in temps.items():
                            if 'cpu' in name.lower() or 'core' in name.lower():
                                if entries:
                                    return entries[0].current
                        # If no CPU-specific sensor, use first available
                        for name, entries in temps.items():
                            if entries:
                                return entries[0].current
            except (AttributeError, IndexError):
                pass
            
            # Method 4: macOS sysctl (limited info, but no sudo required)
            try:
                temp_output = subprocess.check_output(
                    ['sysctl', '-n', 'machdep.xcpm.cpu_thermal_state'], 
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=2
                )
                # This gives thermal state (0-4), convert to approximate temp
                thermal_state = int(temp_output.strip())
                # Rough approximation: 0=40°C, 1=50°C, 2=60°C, 3=70°C, 4=80°C+
                return 40 + (thermal_state * 10)
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, ValueError):
                pass
            
        except Exception:
            pass
        
        # Return 0 if no temperature method available
        return 0.0
    
    def get_process_info(self) -> dict:
        """Get current process information"""
        try:
            process = psutil.Process()
            return {
                'threads': process.num_threads(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(interval=0.1)
            }
        except:
            return {'threads': 0, 'memory_mb': 0, 'cpu_percent': 0}
    
    def run(self):
        while self.running:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Network speeds
                upload_speed, download_speed = self.get_network_speed()
                
                # Process info
                process_info = self.get_process_info()
                
                # CPU temperature (alternative methods without sudo)
                cpu_temp = self.get_cpu_temperature()
                
                # Update performance history
                self.update_performance_history(cpu_percent, memory.percent, upload_speed, download_speed)
                
                # Get performance trends
                trends = self.get_performance_trends()
                
                metrics = {
                    # System Resources
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'memory_used_gb': memory.used / 1024 / 1024 / 1024,
                    'memory_total_gb': memory.total / 1024 / 1024 / 1024,
                    'disk': disk.percent,
                    'disk_free_gb': disk.free / 1024 / 1024 / 1024,
                    'disk_total_gb': disk.total / 1024 / 1024 / 1024,
                    'cpu_temp': cpu_temp,
                    
                    # Network
                    'upload_speed': upload_speed,
                    'download_speed': download_speed,
                    
                    # Process
                    'threads': process_info['threads'],
                    'process_memory_mb': process_info['memory_mb'],
                    'process_cpu': process_info['cpu_percent'],
                    
                    # Time
                    'elapsed_time': self.get_elapsed_time(),
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'uptime_seconds': time.time() - self.start_time,
                    
                    # AI Usage Stats
                    'total_prompts': self.stats['total_prompts'],
                    'claude_prompts': self.stats['claude_prompts'],
                    'ollama_prompts': self.stats['ollama_prompts'],
                    'total_tokens': self.stats['total_tokens'],
                    'errors': self.stats['errors'],
                    'files_generated': self.stats['files_generated'],
                    'memory_items': self.stats['memory_items'],
                    'task_types': self.stats['task_types'].copy(),
                    'autonomous_actions': self.stats['autonomous_actions'],
                    'safety_checks': self.stats['safety_checks'],
                    'successful_tasks': self.stats['successful_tasks'],
                    'failed_tasks': self.stats['failed_tasks'],
                    'auto_continues': self.stats['auto_continues'],
                    
                    # Calculate rates
                    'prompts_per_hour': (self.stats['total_prompts'] / max(1, (time.time() - self.start_time) / 3600)),
                    'tokens_per_minute': (self.stats['total_tokens'] / max(1, (time.time() - self.start_time) / 60)),
                    'tasks_per_hour': ((self.stats['successful_tasks'] + self.stats['failed_tasks']) / 
                                     max(1, (time.time() - self.start_time) / 3600)),
                    
                    # Performance trends
                    'cpu_trend': trends.get('cpu', 'stable'),
                    'memory_trend': trends.get('memory', 'stable'),
                    'network_up_trend': trends.get('network_up', 'stable'),
                    'network_down_trend': trends.get('network_down', 'stable'),
                    
                    # Performance averages
                    'avg_cpu': sum(self.performance_history['cpu'][-10:]) / max(1, len(self.performance_history['cpu'][-10:])),
                    'avg_memory': sum(self.performance_history['memory'][-10:]) / max(1, len(self.performance_history['memory'][-10:])),
                }
                
                # Add system health score
                health_score, health_status = self.get_system_health_score(metrics)
                metrics['health_score'] = health_score
                metrics['health_status'] = health_status
                
                self.update_signal.emit(metrics)
                time.sleep(2)
            except Exception as e:
                logging.error(f"System monitoring error: {e}")
                time.sleep(5)
    
    def stop(self):
        self.running = False
    
    def reset_stats(self):
        """Reset all statistics"""
        self.start_time = time.time()
        self.stats = {
            'total_prompts': 0,
            'claude_prompts': 0,
            'ollama_prompts': 0,
            'total_tokens': 0,
            'errors': 0,
            'files_generated': 0,
            'memory_items': 0,
            'task_types': {t: 0 for t in TASK_TYPES}
        }

# Enhanced monitoring display in SuperMiniMainWindow
def create_control_panel(self) -> QWidget:
    """Create the left control panel with enhanced monitoring"""
    panel = QWidget()
    layout = QVBoxLayout()
    
    # ... (existing code for mode groups) ...
    
    # Enhanced System Monitor
    monitor_group = QGroupBox("📊 System Monitor")
    monitor_layout = QVBoxLayout()
    
    # Enhanced Claude Code-style monitor display with responsive sizing
    self.monitor_display = QTextBrowser()
    # Dynamic sizing based on available screen space
    app = QApplication.instance()
    if app:
        screen = app.primaryScreen()
        available_height = screen.availableGeometry().height()
        min_height = max(200, int(available_height * 0.25))  # 25% of screen height, min 200px
        max_height = max(300, int(available_height * 0.4))   # 40% of screen height, min 300px
    else:
        min_height, max_height = 200, 300  # Fallback values
    
    self.monitor_display.setMinimumHeight(ModernTheme.scale_value(min_height))
    self.monitor_display.setMaximumHeight(ModernTheme.scale_value(max_height))
    self.monitor_display.setStyleSheet("""
        QTextBrowser {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #e6e6e6;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
            font-size: 11px;
            padding: 0;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
        }
    """)
    # Set professional startup message
    self.monitor_display.setHtml("""
        <div style='padding: 24px; text-align: center; color: #74c0fc;'>
            <div style='font-size: 16px; margin-bottom: 8px;'>⚡ Claude Code Development Environment</div>
            <div style='color: #a0a0a0; font-size: 11px; margin-bottom: 16px;'>Initializing system monitoring...</div>
            <div style='background: rgba(116, 192, 252, 0.1); padding: 8px 16px; border-radius: 6px; display: inline-block;'>
                <span style='color: #51cf66; font-size: 10px;'>●</span>
                <span style='color: #a0a0a0; font-size: 10px; margin-left: 6px;'>Ready to monitor development activity</span>
            </div>
        </div>
    """)
    
    # No monitor controls - monitoring is fully automatic
    monitor_layout.addWidget(self.monitor_display)
    monitor_group.setLayout(monitor_layout)
    
    # Add all groups to layout
    layout.addWidget(mode_group)
    layout.addWidget(common_group)
    layout.addWidget(self.progress_bar)
    layout.addWidget(monitor_group)
    
    panel.setLayout(layout)
    panel.setMaximumWidth(ModernTheme.scale_value(400))
    return panel

def update_monitor_display(self, metrics):
    """Update monitor display with Claude Code-style development statistics"""
    
    def get_trend_indicator(trend, value):
        if trend == "increasing":
            return f"<span style='color: #ff6b6b;'>↗ {value:.1f}%</span>"
        elif trend == "decreasing":
            return f"<span style='color: #51cf66;'>↘ {value:.1f}%</span>"
        else:
            return f"<span style='color: #74c0fc;'>→ {value:.1f}%</span>"
    
    def get_status_badge(score):
        if score >= 95:
            return "<span style='background: #51cf66; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 9px;'>EXCELLENT</span>"
        elif score >= 85:
            return "<span style='background: #74c0fc; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 9px;'>GOOD</span>"
        elif score >= 70:
            return "<span style='background: #ffd43b; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 9px;'>FAIR</span>"
        else:
            return "<span style='background: #ff6b6b; color: #fff; padding: 2px 6px; border-radius: 8px; font-size: 9px;'>POOR</span>"
    
    def format_duration(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    # Calculate development productivity metrics
    productivity_score = 0
    if metrics.get('total_prompts', 0) > 0:
        success_rate = metrics.get('successful_tasks', 0) / max(metrics.get('successful_tasks', 0) + metrics.get('failed_tasks', 0), 1) * 100
        productivity_score = min(100, (metrics.get('prompts_per_hour', 0) * 2) + (success_rate * 0.5))
    
    # Format the display with Claude Code aesthetic
    html = f"""
    <html>
    <head>
    <style>
        body {{ 
            margin: 0; padding: 12px; 
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%); 
            color: #e6e6e6; 
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace; 
            font-size: 11px;
            line-height: 1.4;
        }}
        .header-bar {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 16px; 
            padding: 8px 12px; 
            background: rgba(255,255,255,0.05); 
            border-radius: 8px; 
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .title {{ color: #74c0fc; font-weight: 600; font-size: 13px; }}
        .status {{ font-size: 10px; }}
        .grid {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 12px; 
            margin-bottom: 12px; 
        }}
        .card {{ 
            background: rgba(255,255,255,0.03); 
            border: 1px solid rgba(255,255,255,0.1); 
            border-radius: 8px; 
            padding: 12px; 
        }}
        .card-title {{ 
            color: #ffd43b; 
            font-weight: 600; 
            font-size: 10px; 
 
            letter-spacing: 0.5px; 
            margin-bottom: 8px; 
        }}
        .metric-row {{ 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 4px; 
        }}
        .metric-label {{ color: #a0a0a0; font-size: 10px; }}
        .metric-value {{ color: #ffffff; font-weight: 500; }}
        .success {{ color: #51cf66; }}
        .warning {{ color: #ffd43b; }}
        .error {{ color: #ff6b6b; }}
        .info {{ color: #74c0fc; }}
        .progress-bar {{ 
            height: 3px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 2px; 
            overflow: hidden; 
            margin: 4px 0; 
        }}
        .progress-fill {{ 
            height: 100%; 
 
        }}
        .wide-card {{ grid-column: span 2; }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 8px; 
            margin-top: 8px; 
        }}
        .stat-item {{ 
            text-align: center; 
            padding: 6px; 
            background: rgba(255,255,255,0.02); 
            border-radius: 4px; 
        }}
        .stat-value {{ 
            display: block; 
            font-size: 14px; 
            font-weight: 600; 
            color: #74c0fc; 
        }}
        .stat-label {{ 
            font-size: 9px; 
            color: #a0a0a0; 
 
        }}
    </style>
    </head>
    <body>
    
    <div class="header-bar">
        <div class="title">⚡ Claude Code Development Environment</div>
        <div class="status">
            {get_status_badge(metrics.get('health_score', 100))}
            <span style="margin-left: 8px; color: #a0a0a0;">Session: {format_duration(metrics.get('uptime_seconds', 0))}</span>
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <div class="card-title">🖥️ System Performance</div>
            <div class="metric-row">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value">{get_trend_indicator(metrics.get('cpu_trend', 'stable'), metrics['cpu'])}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {metrics['cpu']}%; background: {'#ff6b6b' if metrics['cpu'] > 80 else '#51cf66' if metrics['cpu'] < 50 else '#ffd43b'};"></div>
            </div>
            
            <div class="metric-row">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value">{get_trend_indicator(metrics.get('memory_trend', 'stable'), metrics['memory'])}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {metrics['memory']}%; background: {'#ff6b6b' if metrics['memory'] > 85 else '#51cf66' if metrics['memory'] < 70 else '#ffd43b'};"></div>
            </div>
            
            <div class="metric-row">
                <span class="metric-label">Disk Space</span>
                <span class="metric-value success">{metrics['disk_free_gb']:.0f}GB free</span>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">🤖 AI Development Stats</div>
            <div class="metric-row">
                <span class="metric-label">Total Prompts</span>
                <span class="metric-value info">{metrics['total_prompts']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Tokens Processed</span>
                <span class="metric-value info">{metrics['total_tokens']:,}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Productivity Rate</span>
                <span class="metric-value">{metrics.get('prompts_per_hour', 0):.1f} prompts/hr</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Error Rate</span>
                <span class="metric-value {'error' if metrics.get('errors', 0) > 2 else 'success'}">{metrics.get('errors', 0)} errors</span>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">📋 Task Execution</div>
            <div class="metric-row">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value success">{(metrics.get('successful_tasks', 0) / max(metrics.get('successful_tasks', 0) + metrics.get('failed_tasks', 0), 1) * 100):.1f}%</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Tasks Completed</span>
                <span class="metric-value">{metrics.get('successful_tasks', 0) + metrics.get('failed_tasks', 0)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Auto-Continues</span>
                <span class="metric-value info">{metrics.get('auto_continues', 0)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Files Generated</span>
                <span class="metric-value success">{metrics.get('files_generated', 0)}</span>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">🔧 Process Details</div>
            <div class="metric-row">
                <span class="metric-label">Active Threads</span>
                <span class="metric-value">{metrics.get('threads', 0)}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Process Memory</span>
                <span class="metric-value">{metrics.get('process_memory_mb', 0):.0f} MB</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Network I/O</span>
                <span class="metric-value">↑{metrics.get('upload_speed', 0):.2f} ↓{metrics.get('download_speed', 0):.2f} MB/s</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Temperature</span>
                <span class="metric-value">{metrics.get('cpu_temp', 0):.0f}°C</span>
            </div>
        </div>
    </div>
    
    <div class="card wide-card">
        <div class="card-title">📊 Development Activity Overview</div>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-value">{metrics.get('claude_prompts', 0)}</span>
                <span class="stat-label">Claude Queries</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{metrics.get('ollama_prompts', 0)}</span>
                <span class="stat-label">Local Queries</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{metrics.get('autonomous_actions', 0)}</span>
                <span class="stat-label">Auto Actions</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{metrics.get('safety_checks', 0)}</span>
                <span class="stat-label">Safety Checks</span>
            </div>
        </div>
    </div>
    
    </body>
    </html>
    """
    
    self.monitor_display.setHtml(html)

def get_metric_class(self, value, warning_threshold, danger_threshold, reverse=False):
    """Get CSS class based on metric value and thresholds"""
    if reverse:
        if value >= danger_threshold:
            return "danger"
        elif value >= warning_threshold:
            return "warning"
    else:
        if value >= danger_threshold:
            return "danger"
        elif value >= warning_threshold:
            return "warning"
    return "value"

    # Monitoring control methods removed - monitoring is now fully automatic

    # Statistics management methods removed - monitoring is now automatic and always-on

class WelcomeDialog(QDialog):
    """Welcome dialog with usage instructions"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Welcome to {APP_NAME}")
        
        # Dynamic sizing based on screen size and DPI
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            available_geometry = screen.availableGeometry()
            
            # Calculate dialog size as percentage of available screen space
            width = min(ModernTheme.scale_value(500), int(available_geometry.width() * 0.4))
            height = min(ModernTheme.scale_value(600), int(available_geometry.height() * 0.7))
            
            self.setMinimumSize(ModernTheme.scale_value(400), ModernTheme.scale_value(500))
            self.setMaximumSize(int(available_geometry.width() * 0.8), int(available_geometry.height() * 0.9))
            self.resize(width, height)
        else:
            # Fallback for older screens
            self.setMinimumSize(400, 500)
            self.resize(500, 600)
            
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel(f"{APP_NAME} v{APP_VERSION}")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QTextBrowser()
        description.setHtml(f"""
        <h2>AI Multimedia and Management Assistant</h2>
        
        <p><b>{APP_NAME}</b> is your intelligent desktop assistant that combines the power of 
        Claude API and local Ollama models to help you with various tasks.</p>
        
        <h3>Key Features:</h3>
        <ul>
            <li><b>Code Generation:</b> Write, debug, and optimize code in multiple languages</li>
            <li><b>Multimedia Processing:</b> Analyze images, process audio, handle video files</li>
            <li><b>Document Analysis:</b> Summarize, analyze, and extract insights from documents</li>
            <li><b>Task Automation:</b> Generate scripts for system automation and workflows</li>
            <li><b>Data Analytics:</b> Analyze CSV files, generate insights, create visualizations</li>
            <li><b>Memory System:</b> Context-aware responses based on previous interactions</li>
        </ul>
        
        <h3>Three AI Robot Modes:</h3>
        <ul>
            <li><b>📋 Task Me:</b> Execute specific tasks with user input</li>
            <li><b>🧭 Go Explore:</b> Autonomous exploration and experimentation</li>
            <li><b>⚡ Enhance Yourself:</b> Self-improvement and version evolution</li>
        </ul>
        
        <h3>Getting Started:</h3>
        <ol>
            <li><b>Configure API Keys:</b> Go to Settings and add your Claude API key (optional but recommended)</li>
            <li><b>Install Ollama:</b> Make sure Ollama is installed and running for local AI models</li>
            <li><b>Choose Mode:</b> Select from Task Me, Go Explore, or Enhance Yourself</li>
            <li><b>Execute:</b> Follow the mode-specific instructions</li>
        </ol>
        
        <h3>Examples:</h3>
        <ul>
            <li><b>Task Me:</b> "Create a Python script to sort a CSV file by date"</li>
            <li><b>Go Explore:</b> Let the AI autonomously explore and create</li>
            <li><b>Enhance Yourself:</b> AI improves its own capabilities</li>
        </ul>
        
        <p><b>Output Location:</b> All generated files are saved to <code>~/SuperMini_Output/data/</code></p>
        
        <p><i>The AI robot concept allows for true autonomous operation and self-improvement!</i></p>
        """)
        ok_button = self.parent().create_button(
            "Get Started",
            "🚀",
            "primary",
            "Start using SuperMini",
            140,
            self.accept
        )
        ok_button.setDefault(True)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(ok_button)
        self.setLayout(layout)

class SuperMiniMainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        try:
            super().__init__()
            logging.info("Initializing SuperMiniMainWindow")
            self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - Autonomous Mac Mini AI Agent")
            # Dynamic sizing based on screen and DPI
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                available_geometry = screen.availableGeometry()
                
                # Mobile-first responsive sizing
                screen_width = available_geometry.width()
                screen_height = available_geometry.height()
                screen_category = ModernTheme.get_screen_category(screen_width)
                
                # Calculate optimal window size based on screen size
                if screen_category == ModernTheme.SCREEN_MOBILE:
                    # Mobile: Use most of screen space
                    default_width = min(ModernTheme.scale_value(480), int(screen_width * 0.95))
                    default_height = min(ModernTheme.scale_value(640), int(screen_height * 0.9))
                    min_width = ModernTheme.scale_value(360)
                    min_height = ModernTheme.scale_value(480)
                elif screen_category == ModernTheme.SCREEN_TABLET:
                    # Tablet: Comfortable sizing (70-80% of screen)
                    default_width = min(ModernTheme.scale_value(1000), int(screen_width * 0.75))
                    default_height = min(ModernTheme.scale_value(700), int(screen_height * 0.75))
                    min_width = ModernTheme.scale_value(640)
                    min_height = ModernTheme.scale_value(480)
                else:
                    # Desktop: Optimal window size (60-70% of screen)
                    # Ensure reasonable default size even on large monitors
                    default_width = min(ModernTheme.scale_value(1400), int(screen_width * 0.65))
                    default_height = min(ModernTheme.scale_value(900), int(screen_height * 0.70))
                    min_width = ModernTheme.scale_value(900)
                    min_height = ModernTheme.scale_value(600)
                    
                    # Cap maximum default size for very large screens
                    if default_width > 1600:
                        default_width = 1600
                    if default_height > 1000:
                        default_height = 1000
                
                # Center window on screen
                center_x = (screen_width - default_width) // 2
                center_y = (screen_height - default_height) // 2
                
                self.setGeometry(center_x, center_y, default_width, default_height)
                self.setMinimumSize(min_width, min_height)
                
                # Set maximum size to prevent window from being too large
                max_width = int(screen_width * 0.95)
                max_height = int(screen_height * 0.95)
                self.setMaximumSize(max_width, max_height)
            else:
                # Fallback for systems without screen info
                self.setGeometry(100, 100, 1200, 800)
                self.setMinimumSize(900, 600)
                self.setMaximumSize(1920, 1080)
            
            self.explore_thread = None
            self.enhance_thread = None
            self.task_thread = None
            self.attached_files = []  # Initialize attached files list
            
            logging.info("Setting up directories")
            self.setup_directories()
            
            logging.info("Loading config")
            self.load_config()
            
            logging.info("Setting up processors")
            self.setup_processors()
            
            logging.info("Setting up UI")
            self.apply_modern_theme()
            self.setup_ui()
            
            logging.info("Setting up accessibility")
            self.setup_accessibility()
            
            logging.info("Setting up monitoring")
            self.setup_monitoring()
            
            logging.info("Showing welcome dialog if needed")
            self.show_welcome_if_needed()
            
            logging.info("SuperMiniMainWindow initialization complete")
        except Exception as e:
            logging.error(f"Initialization failed: {e}", exc_info=True)
            QMessageBox.critical(None, "Error", f"Failed to initialize SuperMini: {e}")
            sys.exit(1)
    
    def setup_directories(self):
        self.base_dir = Path.home() / "SuperMini_Output"
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        for directory in [self.base_dir, self.data_dir, self.logs_dir]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error(f"Failed to create directory {directory}: {e}")
                QMessageBox.critical(self, "Error", f"Failed to create directory: {directory}\n{e}")
                sys.exit(1)
        logging.info(f"Directories initialized: {self.base_dir}")
    
    def load_config(self):
        settings = QSettings()
        self.config = AIConfig(
            primary_model=settings.value("primary_model", "Claude API (Recommended)"),
            use_claude=settings.value("use_claude", True, type=bool),
            claude_api_key=settings.value("claude_api_key", ""),
            ollama_url=settings.value("ollama_url", "http://localhost:11434"),
            ollama_model=settings.value("ollama_model", "qwen2.5-coder:7b"),
            max_tokens=settings.value("max_tokens", 4096, type=int),
            temperature=settings.value("temperature", 70, type=int) / 100.0
        )
        
        # Load theme preference
        saved_theme = settings.value("theme", "dark", type=str)
        if saved_theme in ['dark', 'light']:
            ModernTheme.set_theme(saved_theme)
    
    def save_config(self):
        """Save current configuration including theme"""
        settings = QSettings()
        settings.setValue("primary_model", self.config.primary_model)
        settings.setValue("use_claude", self.config.use_claude)
        settings.setValue("claude_api_key", self.config.claude_api_key)
        settings.setValue("ollama_url", self.config.ollama_url)
        settings.setValue("ollama_model", self.config.ollama_model)
        settings.setValue("max_tokens", self.config.max_tokens)
        settings.setValue("temperature", int(self.config.temperature * 100))
        settings.setValue("theme", ModernTheme.get_current_theme())
    
    def toggle_theme(self):
        """Toggle application theme and refresh UI with enhanced feedback"""
        old_theme = ModernTheme.get_current_theme()
        new_theme = ModernTheme.toggle_theme()
        self.save_config()  # Persist theme change
        self.apply_modern_theme()  # Refresh styles
        
        # Update theme toggle button with enhanced visual feedback
        if hasattr(self, 'theme_toggle_btn'):
            icon = ModernIcons.APP['theme']
            target_mode = 'Light' if new_theme == 'dark' else 'Dark'
            self.theme_toggle_btn.setText(f"{icon} Switch to {target_mode} Mode")
            
        # Update current theme label if it exists
        if hasattr(self, 'current_theme_label'):
            self.current_theme_label.setText(f"Current: {new_theme.title()} Mode")
        
        # Enhanced status bar message with icon
        status_icon = "🌙" if new_theme == "dark" else "☀️"
        self.statusBar().showMessage(f"{status_icon} Theme switched to {new_theme} mode", 3000)
        logging.info(f"Application theme toggled from {old_theme} to {new_theme}")
    
    def apply_modern_theme(self):
        """Apply the modern theme to the application"""
        # Initialize DPI-aware scaling if not already done
        app = QApplication.instance()
        if app and ModernTheme._scale_factor is None:
            ModernTheme.initialize_scaling(app)
        
        style_sheets = [
            ModernTheme.get_main_window_style(),
            ModernTheme.get_splitter_style(),
            ModernTheme.get_group_box_style(),
            ModernTheme.get_button_style(),
            ModernTheme.get_input_style(),
            ModernTheme.get_enhanced_checkbox_style(),
            ModernTheme.get_enhanced_text_edit_style(),
            ModernTheme.get_enhanced_combo_box_style(),
            ModernTheme.get_enhanced_spinbox_style(),
            ModernTheme.get_validation_feedback_style(),
            ModernTheme.get_tab_style(),
            ModernTheme.get_progress_bar_style(),
            ModernTheme.get_slider_style(),
            ModernTheme.get_text_browser_style(),
            ModernTheme.get_label_style(),
            ModernTheme.get_accessibility_style(),
            ModernTheme.get_micro_interactions_style(),
            ModernTheme.get_adaptive_typography_style(),
            ModernTheme.get_mobile_touch_style()
        ]
        combined_style = '\n'.join(style_sheets)
        self.setStyleSheet(combined_style)
        logging.info(f"Applied modern theme with scale factor: {ModernTheme._scale_factor:.2f}")
    
    def setup_processors(self):
        self.memory = MemoryManager(self.data_dir)
        # Pass monitor to TaskProcessor so AI managers can log metrics
        monitor = getattr(self, 'monitor', None)
        self.processor = TaskProcessor(self.config, self.memory, self.data_dir, monitor, self.update_ai_metrics)
        
        # Initialize release automation system
        try:
            from release_integration import SuperMiniReleaseIntegration
            self.release_integration = SuperMiniReleaseIntegration(self)
            success = self.release_integration.initialize_release_system()
            
            if success:
                logging.info("Release automation system enabled")
            else:
                logging.info("Release automation disabled (no git repo or GitHub token)")
                self.release_integration = None
        except ImportError:
            logging.warning("Release automation module not available")
            self.release_integration = None
        except Exception as e:
            logging.error(f"Error initializing release automation: {e}")
            self.release_integration = None
    
    def setup_ui(self):
        """Setup the main UI with modern layout and professional styling"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        
        left_panel = self.create_control_panel()
        right_panel = self.create_output_panel()
        
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_panel)
        
        window_width = self.width() if self.width() > 0 else 1000
        control_width = int(window_width * 0.50)
        output_width = window_width - control_width - 10
        self.main_splitter.setSizes([control_width, output_width])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setHandleWidth(ModernTheme.scale_value(8))
        self.main_splitter.setStyleSheet(ModernTheme.get_splitter_style())
        logging.info(f"setup_ui: control_width={control_width}, output_width={output_width}")
        self.main_splitter.update()
        self.updateGeometry()
        
        main_layout.addWidget(self.main_splitter)
        central_widget.setLayout(main_layout)
        
        QTimer.singleShot(1000, self.refresh_files_display)
        QTimer.singleShot(0, self.adjust_splitter_sizes)  # Force resize after UI is shown
        
        status_icon = ModernIcons.STATUS['active']
        self.statusBar().showMessage(f"{status_icon} SuperMini AI Assistant Ready - Neural Processing Active")
        self.statusBar().setProperty("role", "status")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setStyleSheet(ModernTheme.get_progress_bar_style())
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        self.setAccessibleName("SuperMini AI Agent")
        self.setAccessibleDescription("Autonomous Mac Mini AI agent for task automation and processing")
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def adjust_splitter_sizes(self):
        """Force splitter size adjustment after UI initialization"""
        window_width = self.width() if self.width() > 0 else 1000
        control_width = int(window_width * 0.50)
        output_width = window_width - control_width - 10
        self.main_splitter.setSizes([control_width, output_width])
        logging.info(f"adjust_splitter_sizes: control_width={control_width}, output_width={output_width}")
        self.main_splitter.update()
        self.updateGeometry()
    
    def create_button(self, text: str, icon: str = None, variant: str = "default", 
                     tooltip: str = None, min_width: int = None, callback=None) -> QPushButton:
        """Create a standardized button with icon and text"""
        # Combine icon and text if icon provided
        if icon:
            button_text = f"{icon} {text}"
        else:
            button_text = text
        
        button = QPushButton(button_text)
        
        # Apply variant styling
        if variant != "default":
            button.setProperty("variant", variant)
        
        # Set tooltip if provided
        if tooltip:
            button.setToolTip(tooltip)
        
        # Set minimum width if specified
        if min_width:
            button.setMinimumWidth(ModernTheme.scale_value(min_width))
        
        # Standard minimum height for touch targets (44px)
        button.setMinimumHeight(ModernTheme.scale_value(44))
        
        # Connect callback if provided
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    def create_button_group(self, buttons: List[Tuple], spacing: int = 12, 
                           alignment: str = "left") -> QHBoxLayout:
        """Create a properly spaced button group
        
        Args:
            buttons: List of tuples (text, icon, variant, tooltip, callback)
            spacing: Spacing between buttons in pixels
            alignment: Button alignment ('left', 'right', 'center')
        """
        layout = QHBoxLayout()
        layout.setSpacing(ModernTheme.scale_value(spacing))
        layout.setContentsMargins(0, 0, 0, 0)
        
        created_buttons = []
        for btn_config in buttons:
            if isinstance(btn_config, QPushButton):
                # If already a button, just add it
                created_buttons.append(btn_config)
                layout.addWidget(btn_config)
            else:
                # Create button from config
                text = btn_config[0] if len(btn_config) > 0 else ""
                icon = btn_config[1] if len(btn_config) > 1 else None
                variant = btn_config[2] if len(btn_config) > 2 else "default"
                tooltip = btn_config[3] if len(btn_config) > 3 else None
                callback = btn_config[4] if len(btn_config) > 4 else None
                min_width = btn_config[5] if len(btn_config) > 5 else None
                
                button = self.create_button(text, icon, variant, tooltip, min_width, callback)
                created_buttons.append(button)
                layout.addWidget(button)
        
        # Apply alignment
        if alignment == "right":
            layout.insertStretch(0)
        elif alignment == "center":
            layout.insertStretch(0)
            layout.addStretch()
        else:  # left
            layout.addStretch()
        
        return layout, created_buttons
    
    def create_control_panel(self) -> QWidget:
        """Create a modern, well-organized control panel with responsive sizing"""
        from PyQt6.QtWidgets import QSizePolicy
        
        panel = QWidget()
        # Dynamic width constraints based on window size
        window_width = self.width() if hasattr(self, 'width') else 1200
        min_width = max(ModernTheme.scale_value(250), int(window_width * 0.2))  # At least 20% of window
        
        panel.setMinimumWidth(min_width)
        # Remove maximum width constraint for better flexibility
        
        # Set size policy for proper responsive resizing
        panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # Responsive layout with dynamic spacing based on window size
        layout = QVBoxLayout()
        # Dynamic margins and spacing based on available space
        base_margin = max(8, int(window_width * 0.008))  # 0.8% of window width, min 8px
        base_spacing = max(10, int(window_width * 0.012))  # 1.2% of window width, min 10px
        margin = ModernTheme.scale_value(base_margin)
        spacing = ModernTheme.scale_value(base_spacing)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)
        
        # AI Mode Section with responsive spacing
        mode_group = QGroupBox(f"{ModernIcons.APP['logo']} AI Assistant Modes")
        mode_layout = QVBoxLayout()
        # Dynamic margins for mode section
        mode_margin_h = max(12, int(window_width * 0.015))  # Horizontal margin
        mode_margin_v = max(16, int(window_width * 0.018))  # Vertical margin  
        mode_spacing = max(12, int(window_width * 0.012))   # Internal spacing
        mode_layout.setContentsMargins(mode_margin_h, mode_margin_v, mode_margin_h, mode_margin_h)
        mode_layout.setSpacing(mode_spacing)
        
        self.mode_tabs = QTabWidget()
        
        # Task Me Tab - Completely redesigned
        task_tab = self.create_task_tab()
        self.mode_tabs.addTab(task_tab, f"{ModernIcons.TASKS['task']} Task Me")
        
        # Other tabs
        explore_tab = self.create_explore_tab()
        self.mode_tabs.addTab(explore_tab, f"{ModernIcons.NAVIGATION['search']} Go Explore")
        
        enhance_tab = self.create_enhance_tab()
        self.mode_tabs.addTab(enhance_tab, f"{ModernIcons.TASKS['automation']} Enhance Yourself")
        
        # Settings available via dedicated Settings button - removing duplicate embedded tab
        # settings_tab = self.create_settings_tab()
        # self.mode_tabs.addTab(settings_tab, f"{ModernIcons.APP['settings']} Settings")
        
        mode_layout.addWidget(self.mode_tabs)
        mode_group.setLayout(mode_layout)
        
        # System Controls Section
        controls_group = self.create_system_controls()
        
        # Add all sections to main layout
        layout.addWidget(mode_group)
        layout.addWidget(controls_group)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def create_task_tab(self) -> QWidget:
        """Create the main task input tab with enhanced design and validation"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Increased margins for better spacing
        layout.setSpacing(24)  # Increased spacing for better visual separation
        
        # Task Input Section with enhanced design
        input_section = QGroupBox(f"{ModernIcons.ACTIONS['edit']} Task Description")
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(20, 24, 20, 20)  # Better margins for professional look
        input_layout.setSpacing(12)
        
        # Input field with enhanced properties
        from PyQt6.QtWidgets import QSizePolicy
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText(
            "Describe what you'd like me to help you with...\n\n"
            "💡 Examples:\n"
            "• Create a Python script to process CSV files\n"
            "• Analyze this image for key insights\n"
            "• Summarize these documents\n"
            "• Build a web scraper for product prices\n"
            "• Generate automation scripts for file management\n"
            "• Create data visualizations from CSV data"
        )
        self.task_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Dynamic text input sizing based on window height
        window_height = self.height() if hasattr(self, 'height') else 800
        min_height = max(120, int(window_height * 0.15))  # 15% of window height, min 120px
        max_height = max(200, int(window_height * 0.3))   # 30% of window height, min 200px  
        self.task_input.setMinimumHeight(ModernTheme.scale_value(min_height))
        self.task_input.setMaximumHeight(ModernTheme.scale_value(max_height))
        self.task_input.setProperty("role", "input")
        self.task_input.setTabChangesFocus(True)  # Better keyboard navigation
        self.task_input.setAcceptRichText(False)  # Prevent formatting issues
        
        # Connect to validation
        self.task_input.textChanged.connect(self.validate_task_input)
        
        # Character count label for user feedback
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setProperty("role", "caption")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Validation feedback label (initially hidden)
        self.task_validation_label = QLabel()
        self.task_validation_label.setVisible(False)
        self.task_validation_label.setWordWrap(True)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.char_count_label)
        input_layout.addWidget(self.task_validation_label)
        input_section.setLayout(input_layout)
        
        # File Attachments Section with enhanced design
        files_section = QGroupBox(f"{ModernIcons.ACTIONS['attach']} File Attachments")
        files_layout = QVBoxLayout()
        files_layout.setContentsMargins(20, 24, 20, 20)  # Better margins
        files_layout.setSpacing(16)
        
        # File management buttons with improved spacing using button helper
        self.attach_btn = self.create_button(
            "Attach Files",
            ModernIcons.ACTIONS['attach'],
            "secondary",
            "Add files to be processed or analyzed\nSupported: Images, PDFs, Text files, CSV, Code files",
            140,
            self.attach_files
        )
        
        self.clear_files_btn = self.create_button(
            "Clear All",
            ModernIcons.ACTIONS['delete'],
            "danger",
            "Remove all attached files",
            120,
            self.clear_files
        )
        self.clear_files_btn.setEnabled(False)  # Disabled until files are attached
        
        # Create properly spaced button group
        file_buttons_layout, _ = self.create_button_group(
            [self.attach_btn, self.clear_files_btn],
            spacing=16,
            alignment="left"
        )
        
        # Enhanced file status display
        self.files_label = QLabel("No files attached")
        self.files_label.setProperty("role", "caption")
        self.files_label.setWordWrap(True)
        
        # File count and size info
        self.file_info_label = QLabel("")
        self.file_info_label.setProperty("role", "info")
        self.file_info_label.setVisible(False)
        
        files_layout.addLayout(file_buttons_layout)
        files_layout.addWidget(self.files_label)
        files_layout.addWidget(self.file_info_label)
        files_section.setLayout(files_layout)
        
        # Task Configuration Section with enhanced organization
        config_section = QGroupBox(f"{ModernIcons.APP['settings']} Task Configuration")
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(20, 24, 20, 20)  # Better margins
        config_layout.setSpacing(20)  # Increased spacing for better visual separation
        
        # Task type selection with improved layout and accessibility
        type_group = QGroupBox("Task Type Selection")
        type_group_layout = QVBoxLayout()
        type_group_layout.setContentsMargins(16, 20, 16, 16)
        type_group_layout.setSpacing(12)
        
        type_layout = QHBoxLayout()
        type_layout.setSpacing(16)  # Better spacing for accessibility
        task_type_label = QLabel("Task Type:")
        task_type_label.setMinimumWidth(ModernTheme.scale_value(120))  # More consistent label width
        task_type_label.setProperty("role", "label")
        type_layout.addWidget(task_type_label)
        
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(["Auto-detect"] + [t.title() for t in TASK_TYPES])
        self.task_type_combo.setMinimumHeight(ModernTheme.scale_value(44))  # Enhanced touch target
        self.task_type_combo.setMinimumWidth(ModernTheme.scale_value(200))  # Better width for readability
        self.task_type_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.task_type_combo.setToolTip("Select the type of task or let AI auto-detect based on your description")
        self.task_type_combo.currentTextChanged.connect(self.on_task_type_changed)
        type_layout.addWidget(self.task_type_combo)
        type_layout.addStretch()
        
        # Task type description
        self.task_type_description = QLabel("AI will automatically detect the best task type based on your description.")
        self.task_type_description.setProperty("role", "caption")
        self.task_type_description.setWordWrap(True)
        
        type_group_layout.addLayout(type_layout)
        type_group_layout.addWidget(self.task_type_description)
        type_group.setLayout(type_group_layout)
        
        # Processing Options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(16, 20, 16, 16)
        options_layout.setSpacing(16)
        
        self.use_memory_cb = QCheckBox("🧠 Use Memory Context")
        self.use_memory_cb.setChecked(True)
        self.use_memory_cb.setToolTip("Use previous task history and context for better, more personalized results")
        
        # Autonomous Intelligence Status Indicator
        autonomous_status_layout = QHBoxLayout()
        autonomous_status_icon = QLabel("🤖")
        autonomous_status_icon.setStyleSheet("font-size: 16px;")
        autonomous_status_text = QLabel("Autonomous Intelligence Active")
        autonomous_status_text.setStyleSheet("color: #4CAF50; font-weight: bold;")
        autonomous_status_layout.addWidget(autonomous_status_icon)
        autonomous_status_layout.addWidget(autonomous_status_text)
        autonomous_status_layout.addStretch()
        
        self.autonomous_status_widget = QWidget()
        self.autonomous_status_widget.setLayout(autonomous_status_layout)
        self.autonomous_status_widget.setToolTip("AI automatically optimizes parameters and continuation decisions for best results")
        
        # Max continues control with enhanced design
        continues_layout = QHBoxLayout()
        continues_layout.setSpacing(16)
        max_continues_label = QLabel("Max continues:")
        max_continues_label.setMinimumWidth(ModernTheme.scale_value(120))
        max_continues_label.setProperty("role", "label")
        continues_layout.addWidget(max_continues_label)
        
        self.max_continues_spin = QSpinBox()
        self.max_continues_spin.setRange(1, 50)
        self.max_continues_spin.setValue(10)
        self.max_continues_spin.setMinimumWidth(ModernTheme.scale_value(120))
        self.max_continues_spin.setMinimumHeight(ModernTheme.scale_value(44))
        self.max_continues_spin.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.max_continues_spin.setToolTip("Maximum number of automatic continuations (1-50)")
        self.max_continues_spin.setSuffix(" iterations")
        continues_layout.addWidget(self.max_continues_spin)
        continues_layout.addStretch()
        
        # Autonomous Enhancement Status Display
        self.enhancement_status_widget = QWidget()
        enhancement_status_layout = QHBoxLayout()
        enhancement_status_layout.setContentsMargins(0, 0, 0, 0)
        enhancement_status_layout.setSpacing(12)
        
        # Enhancement mode indicator
        self.enhancement_mode_label = QLabel("🧠 Enhancement Mode:")
        self.enhancement_mode_label.setProperty("role", "label")
        enhancement_status_layout.addWidget(self.enhancement_mode_label)
        
        self.enhancement_status_label = QLabel("Ready")
        self.enhancement_status_label.setProperty("role", "status-ready")
        self.enhancement_status_label.setMinimumWidth(ModernTheme.scale_value(100))
        enhancement_status_layout.addWidget(self.enhancement_status_label)
        
        # Show enhancement details button
        self.enhancement_details_btn = self.create_button(
            "Details",
            "📊",
            "default",
            "Show autonomous enhancement system details",
            100,
            self.show_enhancement_details
        )
        self.enhancement_details_btn.setMaximumHeight(ModernTheme.scale_value(32))
        enhancement_status_layout.addWidget(self.enhancement_details_btn)
        
        enhancement_status_layout.addStretch()
        self.enhancement_status_widget.setLayout(enhancement_status_layout)
        self.enhancement_status_widget.setToolTip("Shows status of the autonomous enhancement system")
        
        self.save_output_cb = QCheckBox("💾 Save Output Files")
        self.save_output_cb.setChecked(True)
        self.save_output_cb.setToolTip("Automatically save generated files to ~/SuperMini_Output/ directory")
        
        options_layout.addWidget(self.use_memory_cb)
        options_layout.addWidget(self.autonomous_status_widget)
        options_layout.addWidget(self.enhancement_status_widget)
        options_layout.addWidget(self.save_output_cb)
        options_group.setLayout(options_layout)
        
        config_layout.addWidget(type_group)
        config_layout.addWidget(options_group)
        config_section.setLayout(config_layout)
        
        # Autonomous Mode Section with enhanced design
        autonomous_section = QGroupBox("🤖 Autonomous Capabilities")
        autonomous_layout = QVBoxLayout()
        autonomous_layout.setContentsMargins(20, 24, 20, 20)  # Better margins
        autonomous_layout.setSpacing(16)
        
        # Autonomous mode controls
        autonomous_controls = QHBoxLayout()
        autonomous_controls.setSpacing(16)
        
        self.autonomous_mode_cb = QCheckBox("🤖 Enable Autonomous Mode")
        self.autonomous_mode_cb.setChecked(False)
        self.autonomous_mode_cb.setToolTip("Allow AI to directly interact with the computer interface for advanced automation")
        self.autonomous_mode_cb.toggled.connect(self.on_autonomous_mode_toggled)
        
        self.show_suggestions_btn = self.create_button(
            "Preview Actions",
            "💡",
            "secondary",
            "Preview recommended autonomous actions before execution",
            140,
            self.show_autonomous_suggestions
        )
        self.show_suggestions_btn.setEnabled(AUTONOMOUS_AVAILABLE)
        
        autonomous_controls.addWidget(self.autonomous_mode_cb)
        autonomous_controls.addWidget(self.show_suggestions_btn)
        autonomous_controls.addStretch()
        
        # Enhanced status indicator with detailed information
        self.autonomous_status_label = QLabel("")
        if AUTONOMOUS_AVAILABLE:
            self.autonomous_status_label.setText("✅ Autonomous capabilities available - AI can interact with your computer interface")
            self.autonomous_status_label.setProperty("role", "validation-success")
        else:
            self.autonomous_status_label.setText("⚠️ Install gui-agents package for autonomous features: pip install gui-agents")
            self.autonomous_status_label.setProperty("role", "validation-info")
            self.autonomous_mode_cb.setEnabled(False)
            self.show_suggestions_btn.setEnabled(False)
        self.autonomous_status_label.setWordWrap(True)
        
        autonomous_layout.addLayout(autonomous_controls)
        autonomous_layout.addWidget(self.autonomous_status_label)
        autonomous_section.setLayout(autonomous_layout)
        
        # Action Buttons Section with enhanced design
        buttons_section = QGroupBox("🚀 Actions")
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(20, 24, 20, 20)  # Better margins
        buttons_layout.setSpacing(20)
        
        # Primary action buttons using button helper for consistency
        self.process_btn = self.create_button(
            "Execute Task",
            "🚀",
            "primary",
            "Start processing the task with AI - analyzes your input and generates results",
            160,
            self.process_task
        )
        self.process_btn.setDefault(True)
        self.process_btn.setMinimumHeight(ModernTheme.scale_value(48))  # Larger for main action
        
        self.stop_task_btn = self.create_button(
            "Stop Task",
            ModernIcons.ACTIONS['stop'],
            "danger",
            "Stop the current task execution immediately",
            120,
            self.stop_task
        )
        self.stop_task_btn.setEnabled(False)
        self.stop_task_btn.setMinimumHeight(ModernTheme.scale_value(48))  # Match execute button height
        
        # Create properly spaced button group
        primary_buttons, _ = self.create_button_group(
            [self.process_btn, self.stop_task_btn],
            spacing=16,
            alignment="left"
        )
        
        # Task execution status
        self.task_status_label = QLabel("Ready to execute task")
        self.task_status_label.setProperty("role", "caption")
        self.task_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        buttons_layout.addLayout(primary_buttons)
        buttons_layout.addWidget(self.task_status_label)
        buttons_section.setLayout(buttons_layout)
        
        # Add all sections to tab
        layout.addWidget(input_section)
        layout.addWidget(files_section)
        layout.addWidget(config_section)
        layout.addWidget(autonomous_section)
        layout.addWidget(buttons_section)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_explore_tab(self) -> QWidget:
        """Create the autonomous exploration tab with enhanced modern design"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(ModernTheme.scale_value(16), ModernTheme.scale_value(16), 
                                 ModernTheme.scale_value(16), ModernTheme.scale_value(16))
        layout.setSpacing(ModernTheme.scale_value(20))
        
        # Header Section with icon and title
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Icon and title
        title_label = QLabel("🧭 Autonomous Exploration")
        title_label.setFont(QFont("SF Pro Text", int(ModernTheme.get_font_size('heading').replace('pt', ''))))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                font-weight: 600;
            }}
        """)
        
        description_label = QLabel("Let the AI explore, learn, and create autonomously")
        description_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_muted']};
                font-size: {ModernTheme.get_font_size('base')};
            }}
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        layout.addWidget(description_label)
        
        # Settings Section
        settings_section = ModernTheme.create_clean_settings_section("Exploration Settings")
        settings_content = settings_section.findChild(QWidget)
        settings_layout = QVBoxLayout(settings_content)
        settings_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Grid for checkboxes
        options_grid = QWidget()
        grid_layout = QGridLayout(options_grid)
        grid_layout.setSpacing(ModernTheme.scale_value(8))
        
        # Enhanced checkboxes in 2-column grid
        self.explore_system_cb = ModernTheme.create_compact_checkbox(
            "System Exploration", "Explore system files and capabilities")
        self.explore_internet_cb = ModernTheme.create_compact_checkbox(
            "Internet Research", "Research and learn from web resources")
        self.create_projects_cb = ModernTheme.create_compact_checkbox(
            "Creative Projects", "Generate experimental projects and code")
        self.maintain_journal_cb = ModernTheme.create_compact_checkbox(
            "Exploration Journal", "Maintain detailed exploration logs")
        
        # Set default values
        self.explore_system_cb.setChecked(True)
        self.explore_internet_cb.setChecked(True)
        self.create_projects_cb.setChecked(True)
        self.maintain_journal_cb.setChecked(True)
        
        # Arrange in 2-column grid
        grid_layout.addWidget(self.explore_system_cb, 0, 0)
        grid_layout.addWidget(self.explore_internet_cb, 0, 1)
        grid_layout.addWidget(self.create_projects_cb, 1, 0)
        grid_layout.addWidget(self.maintain_journal_cb, 1, 1)
        
        settings_layout.addWidget(options_grid)
        
        # Time Interval Controls
        interval_control = ModernTheme.create_time_interval_control()
        self.explore_interval_spinbox = interval_control["spinbox"]
        self.explore_interval_spinbox.setRange(5, 3600)  # 5 seconds to 1 hour
        self.explore_interval_spinbox.setValue(900)  # 15 minutes default
        self.explore_interval_spinbox.setToolTip("Time between exploration iterations")
        
        settings_layout.addWidget(interval_control["widget"])
        layout.addWidget(settings_section)
        
        # Action Buttons Section
        buttons_section = ModernTheme.create_clean_settings_section("Actions")
        buttons_content = buttons_section.findChild(QWidget)
        buttons_layout = QVBoxLayout(buttons_content)
        buttons_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Enhanced action buttons using button helper
        self.start_explore_btn = self.create_button(
            "Start Exploration",
            "🧭",
            "primary",
            "Begin autonomous exploration mode",
            150,
            self.start_exploration
        )
        
        self.stop_explore_btn = self.create_button(
            "Stop Exploration",
            ModernIcons.ACTIONS['stop'],
            "danger",
            "Stop exploration mode",
            140,
            self.stop_exploration
        )
        self.stop_explore_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_explore_btn)
        button_layout.addWidget(self.stop_explore_btn)
        button_layout.addStretch()
        
        buttons_layout.addWidget(button_container)
        
        # Status Display as styled card
        self.exploration_status = QLabel("Ready to explore")
        self.exploration_status.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.get_colors()['bg_panel']};
                border: 1px solid {ModernTheme.get_colors()['border_input']};
                border-radius: {ModernTheme.scale_value(6)}px;
                padding: {ModernTheme.get_spacing('md')};
                color: {ModernTheme.get_colors()['text_secondary']};
                font-size: {ModernTheme.get_font_size('base')};
            }}
        """)
        
        buttons_layout.addWidget(self.exploration_status)
        layout.addWidget(buttons_section)
        
        # Ensure all components are visible
        buttons_section.show()
        button_container.show()
        self.start_explore_btn.show()
        self.stop_explore_btn.show()
        self.exploration_status.show()
        
        layout.addStretch()
        
        # Ensure the tab widget itself is visible
        tab.show()
        
        return tab
    
    def create_enhance_tab(self) -> QWidget:
        """Create the self-enhancement tab with enhanced modern design"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(ModernTheme.scale_value(16), ModernTheme.scale_value(16), 
                                 ModernTheme.scale_value(16), ModernTheme.scale_value(16))
        layout.setSpacing(ModernTheme.scale_value(20))
        
        # Header Section with icon and title
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Icon and title
        title_label = QLabel("⚡ Self-Enhancement")
        title_label.setFont(QFont("SF Pro Text", int(ModernTheme.get_font_size('heading').replace('pt', ''))))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_secondary']};
                font-weight: 600;
            }}
        """)
        
        description_label = QLabel("AI autonomously improves its own capabilities")
        description_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_muted']};
                font-size: {ModernTheme.get_font_size('base')};
            }}
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        layout.addWidget(description_label)
        
        # Settings Section
        settings_section = ModernTheme.create_clean_settings_section("Enhancement Areas")
        settings_content = settings_section.findChild(QWidget)
        settings_layout = QVBoxLayout(settings_content)
        settings_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Grid for checkboxes
        options_grid = QWidget()
        grid_layout = QGridLayout(options_grid)
        grid_layout.setSpacing(ModernTheme.scale_value(8))
        
        # Enhanced checkboxes in 2-column grid
        self.enhance_ui_cb = ModernTheme.create_compact_checkbox(
            "UI Improvements", "Enhance user interface and experience")
        self.enhance_features_cb = ModernTheme.create_compact_checkbox(
            "Feature Development", "Add new capabilities and features")
        self.enhance_performance_cb = ModernTheme.create_compact_checkbox(
            "Performance Optimization", "Improve speed and efficiency")
        self.enhance_quality_cb = ModernTheme.create_compact_checkbox(
            "Code Quality", "Refactor and improve code structure")
        
        # Set default values
        self.enhance_ui_cb.setChecked(True)
        self.enhance_features_cb.setChecked(True)
        self.enhance_performance_cb.setChecked(True)
        self.enhance_quality_cb.setChecked(True)
        
        # Arrange in 2-column grid
        grid_layout.addWidget(self.enhance_ui_cb, 0, 0)
        grid_layout.addWidget(self.enhance_features_cb, 0, 1)
        grid_layout.addWidget(self.enhance_performance_cb, 1, 0)
        grid_layout.addWidget(self.enhance_quality_cb, 1, 1)
        
        settings_layout.addWidget(options_grid)
        
        # Time Interval Controls with purple accent
        interval_control = ModernTheme.create_time_interval_control()
        self.enhance_interval_spinbox = interval_control["spinbox"]
        self.enhance_interval_spinbox.setRange(30, 7200)  # 30 seconds to 2 hours
        self.enhance_interval_spinbox.setValue(1800)  # 30 minutes default
        self.enhance_interval_spinbox.setToolTip("Time between enhancement iterations")
        
        # Apply purple accent to enhancement controls
        self.enhance_interval_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {ModernTheme.get_colors()['bg_input']};
                border: 2px solid {ModernTheme.get_colors()['border_input']};
                border-radius: {ModernTheme.scale_value(6)}px;
                padding: {ModernTheme.get_spacing('sm')};
                font-size: {ModernTheme.get_font_size('base')};
                color: {ModernTheme.get_colors()['text_primary']};
                min-width: {ModernTheme.scale_value(100)}px;
            }}
            QSpinBox:focus {{
                border-color: {ModernTheme.get_colors()['secondary']};
                background-color: {ModernTheme.get_colors()['bg_secondary']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {ModernTheme.get_colors()['bg_panel']};
                border: 1px solid {ModernTheme.get_colors()['border_input']};
                width: {ModernTheme.scale_value(18)}px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {ModernTheme.get_colors()['secondary']};
            }}
        """)
        
        settings_layout.addWidget(interval_control["widget"])
        layout.addWidget(settings_section)
        
        # Action Buttons Section
        buttons_section = ModernTheme.create_clean_settings_section("Actions")
        buttons_content = buttons_section.findChild(QWidget)
        buttons_layout = QVBoxLayout(buttons_content)
        buttons_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Enhanced action buttons with purple accent using button helper
        self.start_enhance_btn = self.create_button(
            "Start Enhancement",
            "⚡",
            "primary",
            "Begin self-enhancement mode",
            160,
            self.start_enhancement
        )
        
        # Override primary color for enhancement with purple
        self.start_enhance_btn.setStyleSheet(f"""
            QPushButton[variant="primary"] {{
                background-color: {ModernTheme.get_colors()['secondary']};
                color: white;
                border: none;
                border-radius: {ModernTheme.scale_value(6)}px;
                padding: {ModernTheme.get_spacing('md')};
                font-weight: 600;
                font-size: {ModernTheme.get_font_size('base')};
            }}
            QPushButton[variant="primary"]:hover {{
                background-color: {ModernTheme.get_colors()['secondary_hover']};
            }}
        """)
        
        self.stop_enhance_btn = self.create_button(
            "Stop Enhancement",
            ModernIcons.ACTIONS['stop'],
            "danger",
            "Stop enhancement mode",
            150,
            self.stop_enhancement
        )
        self.stop_enhance_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_enhance_btn)
        button_layout.addWidget(self.stop_enhance_btn)
        button_layout.addStretch()
        
        buttons_layout.addWidget(button_container)
        
        # Status Display as styled card with purple accent
        self.enhancement_status = QLabel("Ready to enhance")
        self.enhancement_status.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.get_colors()['bg_panel']};
                border: 1px solid {ModernTheme.get_colors()['secondary']};
                border-radius: {ModernTheme.scale_value(6)}px;
                padding: {ModernTheme.get_spacing('md')};
                color: {ModernTheme.get_colors()['text_secondary']};
                font-size: {ModernTheme.get_font_size('base')};
            }}
        """)
        
        buttons_layout.addWidget(self.enhancement_status)
        layout.addWidget(buttons_section)
        
        # Ensure all components are visible
        buttons_section.show()
        button_container.show()
        self.start_enhance_btn.show()
        self.stop_enhance_btn.show()
        self.enhancement_status.show()
        
        layout.addStretch()
        
        # Ensure the tab widget itself is visible
        tab.show()
        
        return tab
    
    def create_settings_tab(self) -> QWidget:
        """Create comprehensive settings tab with all configuration options"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(ModernTheme.scale_value(16), ModernTheme.scale_value(16), 
                                 ModernTheme.scale_value(16), ModernTheme.scale_value(16))
        layout.setSpacing(ModernTheme.scale_value(20))
        
        # Header Section
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(ModernTheme.scale_value(12))
        
        title_label = QLabel("⚙️ Application Settings")
        title_label.setFont(QFont("SF Pro Text", int(ModernTheme.get_font_size('heading').replace('pt', ''))))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                font-weight: 600;
            }}
        """)
        
        description_label = QLabel("Configure AI models, generation parameters, and system preferences")
        description_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_muted']};
                font-size: {ModernTheme.get_font_size('base')};
            }}
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        layout.addWidget(description_label)
        
        # Theme Settings Section
        theme_section = QGroupBox("🌙 Appearance")
        theme_layout = QVBoxLayout(theme_section)
        theme_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Theme toggle
        theme_toggle_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                font-weight: 500;
                font-size: {ModernTheme.get_font_size('base')};
            }}
        """)
        
        icon = ModernIcons.APP['theme']
        target_mode = 'Light' if ModernTheme.get_current_theme() == 'dark' else 'Dark'
        self.theme_toggle_btn = self.create_button(
            f"Switch to {target_mode} Mode",
            icon,
            "secondary",
            f"Switch to {target_mode.lower()} theme",
            180,
            self.toggle_theme
        )
        
        self.current_theme_label = QLabel(f"Current: {ModernTheme.get_current_theme().title()} Mode")
        self.current_theme_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_muted']};
                font-size: {ModernTheme.get_font_size('sm')};
            }}
        """)
        
        theme_toggle_layout.addWidget(theme_label)
        theme_toggle_layout.addWidget(self.theme_toggle_btn)
        theme_toggle_layout.addWidget(self.current_theme_label)
        theme_toggle_layout.addStretch()
        
        theme_layout.addLayout(theme_toggle_layout)
        layout.addWidget(theme_section)
        
        # AI Models Configuration
        ai_section = ModernTheme.create_clean_settings_section("🤖 AI Models & API Keys")
        ai_content = ai_section.findChild(QWidget)
        ai_layout = QVBoxLayout(ai_content)
        ai_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Claude API settings
        self.use_claude_cb = ModernTheme.create_compact_checkbox(
            "Enable Claude API", "Use Claude AI as the primary AI model")
        self.use_claude_cb.setChecked(True)
        
        claude_key_layout = QHBoxLayout()
        claude_key_label = QLabel("Claude API Key:")
        claude_key_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']}; font-size: {ModernTheme.get_font_size('base')};")
        
        self.claude_key_input = QLineEdit()
        self.claude_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.claude_key_input.setPlaceholderText("Enter your Claude API key (sk-ant-...)")
        self.claude_key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ModernTheme.get_colors()['bg_input']};
                border: 2px solid {ModernTheme.get_colors()['border_input']};
                border-radius: {ModernTheme.scale_value(6)}px;
                padding: {ModernTheme.get_spacing('sm')};
                font-size: {ModernTheme.get_font_size('base')};
                color: {ModernTheme.get_colors()['text_primary']};
            }}
            QLineEdit:focus {{
                border-color: {ModernTheme.get_colors()['primary']};
            }}
        """)
        
        claude_key_layout.addWidget(claude_key_label)
        claude_key_layout.addWidget(self.claude_key_input)
        
        # Ollama settings
        self.use_ollama_cb = ModernTheme.create_compact_checkbox(
            "Enable Ollama Local Models", "Use local Ollama models as fallback")
        self.use_ollama_cb.setChecked(True)
        
        ai_layout.addWidget(self.use_claude_cb)
        ai_layout.addLayout(claude_key_layout)
        ai_layout.addWidget(self.use_ollama_cb)
        layout.addWidget(ai_section)
        
        # Generation Settings
        gen_section = ModernTheme.create_clean_settings_section("⚡ Generation Parameters")
        gen_content = gen_section.findChild(QWidget)
        gen_layout = QVBoxLayout(gen_content)
        gen_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Temperature and other settings grid
        params_grid = QWidget()
        grid_layout = QGridLayout(params_grid)
        grid_layout.setSpacing(ModernTheme.scale_value(8))
        
        # Temperature
        temp_label = QLabel("Temperature:")
        temp_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']};")
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        self.temperature_slider.setToolTip("Controls randomness in AI responses (0-100)")
        
        # Max tokens
        tokens_label = QLabel("Max Tokens:")
        tokens_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']};")
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setValue(4000)
        self.max_tokens_spin.setToolTip("Maximum tokens for AI response")
        
        grid_layout.addWidget(temp_label, 0, 0)
        grid_layout.addWidget(self.temperature_slider, 0, 1)
        grid_layout.addWidget(tokens_label, 1, 0)
        grid_layout.addWidget(self.max_tokens_spin, 1, 1)
        
        gen_layout.addWidget(params_grid)
        layout.addWidget(gen_section)
        
        # Memory & Context Settings
        memory_section = ModernTheme.create_clean_settings_section("🧠 Memory & Context")
        memory_content = memory_section.findChild(QWidget)
        memory_layout = QVBoxLayout(memory_content)
        memory_layout.setSpacing(ModernTheme.scale_value(12))
        
        self.enable_memory_cb = ModernTheme.create_compact_checkbox(
            "Enable Context Memory", "Remember conversation history and user preferences")
        self.enable_memory_cb.setChecked(True)
        
        self.auto_save_cb = ModernTheme.create_compact_checkbox(
            "Auto-save Outputs", "Automatically save generated files to ~/SuperMini_Output/")
        self.auto_save_cb.setChecked(True)
        
        memory_layout.addWidget(self.enable_memory_cb)
        memory_layout.addWidget(self.auto_save_cb)
        layout.addWidget(memory_section)
        
        # Quick Actions
        actions_section = ModernTheme.create_clean_settings_section("🔧 Quick Actions")
        actions_content = actions_section.findChild(QWidget)
        actions_layout = QVBoxLayout(actions_content)
        actions_layout.setSpacing(ModernTheme.scale_value(12))
        
        # Action buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(ModernTheme.scale_value(12))
        
        save_settings_btn = self.create_button(
            "Save Settings",
            "💾",
            "primary",
            "Save current configuration",
            140,
            None
        )
        
        reset_settings_btn = self.create_button(
            "Reset to Defaults",
            "🔄",
            "secondary",
            "Reset all settings to defaults",
            160,
            None
        )
        reset_settings_btn.setToolTip("Reset all settings to default values")
        
        button_layout.addWidget(save_settings_btn)
        button_layout.addWidget(reset_settings_btn)
        button_layout.addStretch()
        
        actions_layout.addWidget(button_container)
        layout.addWidget(actions_section)
        
        layout.addStretch()
        return tab
    
    def create_system_controls(self) -> QWidget:
        """Create system controls section"""
        controls_group = QGroupBox("🔧 System Controls")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)
        
        # Settings and utility buttons using button helper
        self.settings_btn = self.create_button(
            "Settings",
            "⚙️",
            "secondary",
            "Configure AI models, memory, and application settings",
            120,
            self.show_settings
        )
        
        self.clear_output_btn = self.create_button(
            "Clear Output",
            ModernIcons.ACTIONS['delete'],
            "default",
            "Clear the results display",
            130,
            self.clear_output
        )
        
        # Create properly spaced button group
        button_row, _ = self.create_button_group(
            [self.settings_btn, self.clear_output_btn],
            spacing=12,
            alignment="left"
        )
        
        layout.addLayout(button_row)
        controls_group.setLayout(layout)
        return controls_group
    
    def create_progress_section(self) -> QWidget:
        """Create progress indicator section - DEPRECATED"""
        progress_group = QGroupBox("📊 Progress")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 20, 16, 16)
        
        # Progress bar moved to status bar
        placeholder = QLabel("Progress bar moved to status bar")
        layout.addWidget(placeholder)
        progress_group.setLayout(layout)
        return progress_group
    
    def validate_task_input(self):
        """Validate task input and provide real-time feedback"""
        text = self.task_input.toPlainText()
        char_count = len(text)
        
        # Update character count
        self.char_count_label.setText(f"{char_count} characters")
        
        # Provide validation feedback
        if char_count == 0:
            self.task_validation_label.setVisible(False)
        elif char_count < 10:
            self.task_validation_label.setText("💡 Add more details for better results")
            self.task_validation_label.setProperty("role", "info")
            self.task_validation_label.setVisible(True)
        elif char_count > 2000:
            self.task_validation_label.setText("⚠️ Very long descriptions may be truncated")
            self.task_validation_label.setProperty("role", "warning")
            self.task_validation_label.setVisible(True)
        else:
            self.task_validation_label.setText("✅ Good description length")
            self.task_validation_label.setProperty("role", "success")
            self.task_validation_label.setVisible(True)
    
    def attach_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            str(Path.home()),
            "All Files (*);;Text Files (*.txt *.md *.csv *.json);;Images (*.png *.jpg *.jpeg *.gif);;Code Files (*.py *.js *.html *.css)"
        )
        if files:
            self.attached_files = files
            file_names = [Path(f).name for f in files]
            display_text = f"{', '.join(file_names[:3])} and {len(file_names) - 3} more" if len(file_names) > 3 else ', '.join(file_names)
            self.files_label.setText(f"📎 {display_text}")
            self.files_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Calculate total file size and show file info
            total_size = sum(Path(f).stat().st_size for f in files if Path(f).exists())
            size_mb = total_size / (1024 * 1024)
            
            if size_mb < 1:
                size_text = f"{total_size / 1024:.1f} KB"
            else:
                size_text = f"{size_mb:.1f} MB"
            
            self.file_info_label.setText(f"{len(files)} file(s) • {size_text}")
            self.file_info_label.setVisible(True)
            self.clear_files_btn.setEnabled(True)
    
    def clear_files(self):
        self.attached_files = []
        self.files_label.setText("No files attached")
        self.files_label.setStyleSheet("color: gray; font-style: italic;")
        
        # Update file info and enable/disable clear button
        self.file_info_label.setVisible(False)
        self.clear_files_btn.setEnabled(False)
    
    def on_task_type_changed(self, task_type):
        """Handle task type selection changes"""
        descriptions = {
            "Auto-detect": "AI will automatically detect the best task type based on your description.",
            "Code": "Generate, debug, or optimize code in various programming languages.",
            "Multimedia": "Process and analyze images, audio, video, and other media files.",
            "Rag": "Analyze documents, create summaries, and answer questions about content.",
            "Automation": "Create scripts and workflows for system automation tasks.",
            "Analytics": "Analyze data, create visualizations, and generate insights from CSV files."
        }
        
        description = descriptions.get(task_type, descriptions["Auto-detect"])
        self.task_type_description.setText(description)
    
    def on_autonomous_mode_toggled(self, checked):
        """Handle autonomous mode checkbox toggle"""
        try:
            if checked:
                if not AUTONOMOUS_AVAILABLE:
                    QMessageBox.warning(self, "Autonomous Mode", 
                                      "Autonomous capabilities not available. Install gui-agents package:\npip install gui-agents>=0.1.2")
                    self.autonomous_mode_cb.setChecked(False)
                    return
                
                self.show_suggestions_btn.setEnabled(True)
                self.activity_monitor.log_activity("autonomous_mode", "Autonomous mode enabled", {"enabled": True})
            else:
                self.show_suggestions_btn.setEnabled(False)
                self.activity_monitor.log_activity("autonomous_mode", "Autonomous mode disabled", {"enabled": False})
        except Exception as e:
            self.activity_monitor.log_activity("error", f"Error toggling autonomous mode: {str(e)}", {"error": str(e)})
    
    def show_autonomous_suggestions(self):
        """Show autonomous action suggestions for current context"""
        if not AUTONOMOUS_AVAILABLE or not self.processor.autonomous_agent:
            QMessageBox.information(self, "Info", "Autonomous capabilities not available. Install gui-agents package.")
            return
        
        task_text = self.task_input.toPlainText().strip()
        files = getattr(self, 'attached_files', [])
        task_type = None if self.task_type_combo.currentText() == "Auto-detect" else self.task_type_combo.currentText().lower()
        
        try:
            suggestions = self.processor.suggest_autonomous_actions(task_text, files, task_type)
            
            if suggestions:
                suggestions_text = "🤖 **Autonomous Action Suggestions:**\n\n"
                for i, suggestion in enumerate(suggestions, 1):
                    suggestions_text += f"{i}. {suggestion}\n"
                
                suggestions_text += "\n💡 Enable 'Autonomous Mode' to let the AI execute these actions automatically."
                
                dialog = QDialog(self)
                dialog.setWindowTitle("Autonomous Suggestions")
                dialog.setGeometry(200, 200, 500, 400)
                
                layout = QVBoxLayout()
                text_browser = QTextBrowser()
                text_browser.setMarkdown(suggestions_text)
                layout.addWidget(text_browser)
                
                close_btn = self.create_button(
                    "Close",
                    "❌",
                    "secondary",
                    "Close dialog",
                    80,
                    dialog.close
                )
                layout.addWidget(close_btn)
                
                dialog.setLayout(layout)
                dialog.exec()
            else:
                QMessageBox.information(self, "Info", "No autonomous suggestions available for current context.")
                
        except Exception as e:
            logging.error(f"Error getting autonomous suggestions: {e}")
            QMessageBox.warning(self, "Error", f"Failed to get suggestions: {str(e)}")
    
    def show_enhancement_details(self):
        """Show detailed information about the autonomous enhancement system"""
        if not hasattr(self.processor, 'autonomous_continuation_engine') or not self.processor.autonomous_continuation_engine:
            QMessageBox.information(self, "Enhancement Details", "Autonomous Enhancement Engine not available.")
            return
        
        try:
            # Get status from the autonomous continuation engine
            engine_status = self.processor.autonomous_continuation_engine.get_continuation_status()
            
            # Get quality assessment statistics if available
            quality_stats = {}
            if hasattr(self.processor.autonomous_continuation_engine, 'quality_framework'):
                quality_stats = self.processor.autonomous_continuation_engine.quality_framework.get_quality_statistics()
            
            # Get safety manager status if available
            safety_status = {}
            if hasattr(self.processor.autonomous_continuation_engine, 'safety_manager'):
                safety_status = self.processor.autonomous_continuation_engine.safety_manager.get_safety_status()
            
            # Create detailed status text
            details_text = "# 🧠 Autonomous Enhancement System Details\n\n"
            
            # Engine Status
            details_text += "## 📊 Enhancement Engine Status\n"
            details_text += f"- **Total Continuations**: {engine_status.get('total_continuations', 0)}\n"
            details_text += f"- **Successful Enhancements**: {engine_status.get('successful_enhancements', 0)}\n"
            details_text += f"- **Success Rate**: {engine_status.get('success_rate', 0.0):.1%}\n"
            details_text += f"- **Average Quality Improvement**: {engine_status.get('average_quality_improvement', 0.0):.3f}\n"
            details_text += f"- **Average Confidence**: {engine_status.get('average_confidence', 0.0):.1%}\n"
            details_text += f"- **Learning Enabled**: {'✅' if engine_status.get('learning_enabled', False) else '❌'}\n"
            details_text += f"- **Safety Enabled**: {'✅' if engine_status.get('safety_enabled', False) else '❌'}\n\n"
            
            # Quality Statistics
            if quality_stats:
                details_text += "## 📈 Quality Assessment\n"
                details_text += f"- **Total Assessments**: {quality_stats.get('total_assessments', 0)}\n"
                details_text += f"- **Average Quality**: {quality_stats.get('average_quality', 0.0):.1%}\n"
                details_text += f"- **Latest Quality**: {quality_stats.get('latest_quality', 0.0):.1%}\n"
                details_text += f"- **Quality Trend**: {quality_stats.get('quality_trend', 'N/A')}\n"
                details_text += f"- **Average Confidence**: {quality_stats.get('average_confidence', 0.0):.1%}\n\n"
            
            # Safety Status
            if safety_status:
                details_text += "## 🛡️ Safety Status\n"
                details_text += f"- **Emergency Stop**: {'🚨 ACTIVE' if safety_status.get('emergency_stop_active', False) else '✅ Normal'}\n"
                details_text += f"- **Throttling**: {'⚠️ ACTIVE' if safety_status.get('throttling_active', False) else '✅ Normal'}\n"
                details_text += f"- **Monitoring**: {'✅ Active' if safety_status.get('monitoring_active', False) else '❌ Inactive'}\n"
                
                # Resource status
                resources = safety_status.get('current_resources', {})
                if resources:
                    details_text += f"- **CPU Usage**: {resources.get('cpu', 0.0):.1f}%\n"
                    details_text += f"- **Memory Usage**: {resources.get('memory', 0.0):.1f}%\n"
                    details_text += f"- **Disk Usage**: {resources.get('disk', 0.0):.1f}%\n"
                
                # Recent violations
                violations = safety_status.get('recent_violations', {})
                if violations:
                    total_violations = sum(violations.values())
                    if total_violations > 0:
                        details_text += f"- **Recent Violations**: {total_violations} in last 5 minutes\n"
                
                details_text += "\n"
            
            # System Capabilities
            details_text += "## ⚙️ System Capabilities\n"
            details_text += "- **Enhancement Discovery**: Multi-dimensional opportunity analysis\n"
            details_text += "- **Decision Engine**: Intelligent continuation strategies\n"
            details_text += "- **Quality Assessment**: Comprehensive quality measurement\n"
            details_text += "- **Safety Management**: Resource monitoring and circuit breakers\n"
            details_text += "- **Learning System**: Adaptive improvement from outcomes\n\n"
            
            details_text += "## 💡 Enhancement Types\n"
            details_text += "- **Content Gap**: Address missing information\n"
            details_text += "- **Quality Improvement**: Enhance clarity and completeness\n"
            details_text += "- **Technical Enhancement**: Improve code quality and best practices\n"
            details_text += "- **Knowledge Expansion**: Add related concepts and insights\n"
            details_text += "- **Error Correction**: Fix identified issues\n"
            details_text += "- **Optimization**: Performance and efficiency improvements\n"
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Autonomous Enhancement System Details")
            dialog.setGeometry(200, 200, 700, 600)
            
            layout = QVBoxLayout()
            
            # Scrollable text area
            text_browser = QTextBrowser()
            text_browser.setMarkdown(details_text)
            layout.addWidget(text_browser)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            refresh_btn = self.create_button(
                "Refresh",
                "🔄",
                "secondary",
                "Refresh content",
                100,
                lambda: (text_browser.setMarkdown(details_text), dialog.update())
            )
            button_layout.addWidget(refresh_btn)
            
            close_btn = self.create_button(
                "Close",
                "❌",
                "secondary",
                "Close dialog",
                80,
                dialog.close
            )
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            logging.error(f"Error showing enhancement details: {e}")
            QMessageBox.warning(self, "Error", f"Failed to get enhancement details: {str(e)}")
    
    def update_enhancement_status(self, status: str, details: str = ""):
        """Update the enhancement status display"""
        if hasattr(self, 'enhancement_status_label'):
            self.enhancement_status_label.setText(status)
            
            # Update status styling based on status
            if status.lower() in ['ready', 'idle']:
                self.enhancement_status_label.setProperty("role", "status-ready")
            elif status.lower() in ['analyzing', 'processing', 'enhancing']:
                self.enhancement_status_label.setProperty("role", "status-active")
            elif status.lower() in ['completed', 'success']:
                self.enhancement_status_label.setProperty("role", "status-success")
            elif status.lower() in ['error', 'failed']:
                self.enhancement_status_label.setProperty("role", "status-error")
            else:
                self.enhancement_status_label.setProperty("role", "status-ready")
            
            # Force style update
            self.enhancement_status_label.style().unpolish(self.enhancement_status_label)
            self.enhancement_status_label.style().polish(self.enhancement_status_label)
            
            # Update tooltip with details
            if details:
                self.enhancement_status_label.setToolTip(details)
    
    def stop_task(self):
        """Stop the current task execution"""
        if self.task_thread and self.task_thread.isRunning():
            self.task_thread.stop()
            if not self.task_thread.wait(2000):
                self.task_thread.terminate()
                self.task_thread.wait()
            
            self.process_btn.setEnabled(True)
            self.stop_task_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Task stopped")
    
    def start_exploration(self):
        """Start autonomous exploration mode"""
        if not AUTONOMOUS_AVAILABLE:
            QMessageBox.warning(self, "Exploration Mode", "Autonomous exploration not available.")
            return
        
        # Check interval setting
        interval = self.explore_interval_spinbox.value()
        if interval <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Please set a valid exploration interval.")
            return
        
        self.start_explore_btn.setEnabled(False)
        self.stop_explore_btn.setEnabled(True)
        self.exploration_status.setText("🔍 Exploring...")
        self.statusBar().showMessage("Starting autonomous exploration...")
        
        # Create and start exploration thread
        self.explore_thread = ExploreThread(self.processor, interval)
        self.explore_thread.progress_signal.connect(self.update_progress)
        self.explore_thread.result_signal.connect(self.display_explore_result)
        self.explore_thread.error_signal.connect(self.handle_explore_error)
        self.explore_thread.finished.connect(self.exploration_finished)
        self.explore_thread.start()
    
    def stop_exploration(self):
        """Stop autonomous exploration"""
        if hasattr(self, 'explore_thread') and self.explore_thread and self.explore_thread.isRunning():
            self.explore_thread.stop()
            if not self.explore_thread.wait(3000):
                self.explore_thread.terminate()
                self.explore_thread.wait()
        
        self.start_explore_btn.setEnabled(True)
        self.stop_explore_btn.setEnabled(False)
        self.exploration_status.setText("⏹️ Exploration stopped")
        self.statusBar().showMessage("Exploration stopped")
    
    
    def stop_enhancement(self):
        """Stop self-enhancement process"""
        if hasattr(self, 'enhance_thread') and self.enhance_thread and self.enhance_thread.isRunning():
            self.enhance_thread.stop()
            if not self.enhance_thread.wait(3000):
                self.enhance_thread.terminate()
                self.enhance_thread.wait()
        
        self.start_enhance_btn.setEnabled(True)
        self.stop_enhance_btn.setEnabled(False)
        self.enhancement_status.setText("⏹️ Enhancement stopped")
        self.statusBar().showMessage("Enhancement stopped")
    
    def process_task(self):
        task_text = self.task_input.toPlainText().strip()
        if not task_text:
            QMessageBox.warning(self, "Warning", "Please enter a task description!")
            return
        
        task_type = None if self.task_type_combo.currentText() == "Auto-detect" else self.task_type_combo.currentText().lower()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_btn.setEnabled(False)
        self.stop_task_btn.setEnabled(True)
        self.statusBar().showMessage("Processing task...")
        
        # Update neural visualization for AI activity
        if hasattr(self, 'neural_network_widget'):
            self.neural_network_widget.set_activity_level(0.8)
        if hasattr(self, 'ai_status_label'):
            self.ai_status_label.setText("🤖 AI: Processing")
            self.ai_status_label.setStyleSheet(f"""
                color: {ModernTheme.get_colors()['primary']};
                font-weight: 600;
                padding: {ModernTheme.get_spacing('sm')};
            """)
        
        self.results_text.clear()
        
        files = getattr(self, 'attached_files', [])
        
        # Create thread with auto-continue and autonomous settings
        self.task_thread = TaskThread(
            self.processor, 
            task_text, 
            files, 
            task_type, 
            self.use_memory_cb.isChecked(),
            True,  # Auto-continue is now always intelligently managed
            10,    # Max continues will be automatically determined
            self.autonomous_mode_cb.isChecked()  # Add autonomous mode
        )
        
        self.task_thread.progress_signal.connect(self.update_progress)
        self.task_thread.result_signal.connect(self.display_task_result)
        self.task_thread.finished.connect(self.task_finished)
        self.task_thread.start()
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.load_config()
            self.setup_processors()
    
    def clear_output(self):
        """Clear all output displays with modern confirmation"""
        reply = QMessageBox.question(
            self, "Clear Output",
            "Are you sure you want to clear all output and results?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'results_text'):
                self.results_text.clear()
                self.results_text.setPlaceholderText("Cleared. AI responses and analysis will appear here...")
            
            if hasattr(self, 'files_text'):
                self.files_text.clear()
                self.files_text.setPlaceholderText("Cleared. Generated files and their locations will be listed here...")
            
            if hasattr(self, 'monitor_display'):
                self.monitor_display.clear()
                self.monitor_display.setPlaceholderText("Cleared. System monitoring information will appear here...")
            
            self.statusBar().showMessage("✅ All output cleared")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = getattr(self, 'current_theme', 'dark')
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        self.current_theme = new_theme
        
        # Apply theme changes
        ModernTheme.set_theme(new_theme)
        self.setStyleSheet(ModernTheme.get_application_style())
        
        # Update theme toggle button text
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.setText("🌙 Dark" if new_theme == 'light' else "☀️ Light")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def display_task_result(self, result):
        """Display task result in the results panel"""
        if result.success:
            result_text = f"✅ Task Completed Successfully\n\n{result.result}"
        else:
            result_text = f"❌ Task Failed\n\n{result.result}"
        
        if hasattr(self, 'results_text'):
            self.results_text.setPlainText(result_text)
    
    def task_finished(self):
        """Handle task thread completion"""
        self.process_btn.setEnabled(True)
        self.stop_task_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Task completed")
    
    def export_results(self):
        """Export current results to file"""
        if hasattr(self, 'results_text') and self.results_text.toPlainText():
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Results", "results.txt", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.results_text.toPlainText())
                    QMessageBox.information(self, "Export", f"Results exported to {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Export Error", f"Failed to export results: {e}")
        else:
            QMessageBox.information(self, "Export", "No results to export")
    
    def open_output_folder(self):
        """Open the output folder in Finder"""
        import subprocess
        try:
            output_dir = getattr(self, 'base_dir', str(Path.home() / "SuperMini_Output"))
            subprocess.run(['open', output_dir], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open output folder: {e}")
    
    def update_monitor_display(self, metrics):
        """Update monitor display with system metrics"""
        if hasattr(self, 'monitor_label'):
            cpu_emoji = "🔥" if metrics.get('cpu', 0) > 80 else "⚡" if metrics.get('cpu', 0) > 50 else "💚"
            mem_emoji = "🔥" if metrics.get('memory', 0) > 80 else "⚡" if metrics.get('memory', 0) > 50 else "💚"
            
            simple_text = f"{cpu_emoji} CPU: {metrics.get('cpu', 0):.1f}% | {mem_emoji} RAM: {metrics.get('memory', 0):.1f}%"
            self.monitor_label.setText(simple_text)
    
    def update_ai_dashboard(self):
        """Update AI dashboard components"""
        pass  # Placeholder for dashboard updates
    
    def update_dashboard(self):
        """Update general dashboard"""
        pass  # Placeholder for dashboard updates
    
    def display_explore_result(self, result, files, iteration):
        """Handle exploration results"""
        if hasattr(self, 'results_text'):
            self.results_text.append(f"\n🔍 Exploration {iteration}: {result}")
    
    def handle_explore_error(self, error):
        """Handle exploration errors"""
        QMessageBox.warning(self, "Exploration Error", f"Error during exploration: {error}")
    
    def exploration_finished(self):
        """Handle exploration completion"""
        self.start_explore_btn.setEnabled(True)
        self.stop_explore_btn.setEnabled(False)
        self.statusBar().showMessage("Exploration completed")
    
    def display_enhance_result(self, result, files, iteration, version):
        """Handle enhancement results"""
        if hasattr(self, 'results_text'):
            self.results_text.append(f"\n🔧 Enhancement {iteration} (v{version}): {result}")
    
    def handle_enhance_error(self, error):
        """Handle enhancement errors"""
        QMessageBox.warning(self, "Enhancement Error", f"Error during enhancement: {error}")
    
    def update_enhancement_status(self, status_message):
        """Update enhancement status"""
        self.statusBar().showMessage(status_message)
    
    def enhancement_finished(self):
        """Handle enhancement completion"""
        self.start_enhance_btn.setEnabled(True)
        self.stop_enhance_btn.setEnabled(False)
        self.statusBar().showMessage("Enhancement completed")
    
    def create_output_panel(self) -> QWidget:
        """Create a modern output panel with enhanced tabs and styling"""
        panel = QWidget()
        panel.setStyleSheet(f"""
            QWidget {{
                background: {ModernTheme.get_colors()['bg_secondary']};
                border-radius: {ModernTheme.scale_value(12)}px;
                border: 1px solid {ModernTheme.get_colors()['border']};
            }}
        """)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        margin = ModernTheme.scale_value(16)
        spacing = ModernTheme.scale_value(12)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(spacing)

        # Header section with glass effect
        header_card = QWidget()
        header_card.setStyleSheet(f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: {ModernTheme.scale_value(10)}px;
                border: 1px solid {ModernTheme.get_colors()['border']};
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(12, 8, 12, 8)

        header_label = QLabel("📊 AI Assistant Output")
        header_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_primary']};")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        clear_output_btn = self.create_button(
            "Clear All",
            "🗑️",
            "danger",
            "Clear all output and results",
            100,
            self.clear_output
        )
        clear_output_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ModernTheme.get_colors()['primary']};
                color: {ModernTheme.get_colors()['text_primary']};
                border-radius: {ModernTheme.scale_value(8)}px;
                padding: {ModernTheme.scale_value(8)}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {ModernTheme.get_colors()['accent']};
            }}
        """)
        header_layout.addWidget(clear_output_btn)
        layout.addWidget(header_card)

        # Enhanced tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(8)}px;
                background: rgba(255, 255, 255, 0.03);
            }}
            QTabBar::tab {{
                background: rgba(255, 255, 255, 0.05);
                color: {ModernTheme.get_colors()['text_secondary']};
                padding: {ModernTheme.scale_value(10)}px;
                margin-right: {ModernTheme.scale_value(4)}px;
                border-radius: {ModernTheme.scale_value(6)}px;
            }}
            QTabBar::tab:selected {{
                background: {ModernTheme.get_colors()['primary']};
                color: {ModernTheme.get_colors()['text_primary']};
            }}
        """)
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Add activity monitoring tab first (real-time task details)
        if ACTIVITY_MONITORING_AVAILABLE:
            self.activity_monitor_widget = ActivityMonitorWidget(get_activity_logger())
            activity_widget = QWidget()
            activity_layout = self.activity_monitor_widget.create_activity_view()
            activity_widget.setLayout(activity_layout)
            self.tab_widget.addTab(activity_widget, "🔍 Activity Monitor")

        # Enhanced results tab
        results_widget = self.create_results_tab()
        self.tab_widget.addTab(results_widget, "📄 Results")

        # Files tab
        files_widget = self.create_files_tab()
        self.tab_widget.addTab(files_widget, "📁 Generated Files")

        # System Info tab with AI monitoring dashboard
        dashboard_widget = self.create_ai_monitoring_dashboard()
        self.tab_widget.addTab(dashboard_widget, "📊 System Info")

        layout.addWidget(self.tab_widget)
        
        # Set Activity Monitor as default tab if available
        if ACTIVITY_MONITORING_AVAILABLE:
            self.tab_widget.setCurrentIndex(0)
        
        panel.setLayout(layout)
        return panel
    
    def create_results_tab(self) -> QWidget:
        """Create an enhanced results display tab with task summaries and better organization"""
        widget = QWidget()
        widget.setStyleSheet(f"background: transparent;")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Enhanced header with session stats
        header_card = self.create_results_header()
        layout.addWidget(header_card)

        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section: Task Summary Timeline
        timeline_widget = self.create_task_timeline()
        splitter.addWidget(timeline_widget)
        
        # Bottom section: Detailed Results Viewer
        results_viewer = self.create_detailed_results_viewer()
        splitter.addWidget(results_viewer)
        
        # Set splitter proportions (40% timeline, 60% results)
        splitter.setSizes([400, 600])
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {ModernTheme.get_colors()['border']};
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background: {ModernTheme.get_colors()['accent']};
            }}
        """)
        
        layout.addWidget(splitter)
        
        widget.setLayout(layout)
        return widget
    
    def create_results_header(self) -> QWidget:
        """Create enhanced header for results tab with session statistics"""
        header_card = QWidget()
        header_card.setFixedHeight(85)
        header_card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(139, 92, 246, 0.12),
                    stop:0.5 rgba(6, 255, 165, 0.12),
                    stop:1 rgba(56, 189, 248, 0.12));
                border-radius: {ModernTheme.scale_value(12)}px;
                border: 1px solid {ModernTheme.get_colors()['border']};
            }}
        """)
        
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 14, 20, 14)
        
        # Left side: Title and session stats
        left_layout = QVBoxLayout()
        
        title_label = QLabel("🎯 Task Results & Analytics")
        title_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                font-weight: 700;
            }}
        """)
        left_layout.addWidget(title_label)
        
        # Session stats layout
        stats_layout = QHBoxLayout()
        
        self.session_tasks_label = QLabel("0 tasks completed")
        self.session_tasks_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_secondary']};
                font-size: 13px;
            }}
        """)
        stats_layout.addWidget(self.session_tasks_label)
        
        stats_layout.addWidget(QLabel(" • "))
        
        self.session_time_label = QLabel("Session started")
        self.session_time_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_secondary']};
                font-size: 13px;
            }}
        """)
        stats_layout.addWidget(self.session_time_label)
        
        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        
        # Right side: Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        clear_results_btn = self.create_button(
            "Clear All",
            "🗑️",
            "danger",
            "Clear all task results",
            100,
            self.clear_all_results
        )
        clear_results_btn.setStyleSheet(self.get_action_button_style())
        actions_layout.addWidget(clear_results_btn)
        
        export_session_btn = self.create_button(
            "Export Session",
            "📊",
            "secondary",
            "Export session report",
            140,
            self.export_session_report
        )
        export_session_btn.setStyleSheet(self.get_action_button_style())
        actions_layout.addWidget(export_session_btn)
        
        export_btn = self.create_button(
            "Export Result",
            "💾",
            "secondary",
            "Export selected result",
            120,
            self.export_results
        )
        export_btn.setStyleSheet(self.get_action_button_style())
        actions_layout.addWidget(export_btn)
        
        header_layout.addLayout(actions_layout)
        
        # Initialize task tracking and session data
        self.task_results = []
        self.selected_task_index = -1
        self.session_start_time = datetime.now()
        self.update_session_stats()
        
        return header_card
    
    def create_task_timeline(self) -> QWidget:
        """Create a timeline view of completed tasks"""
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        
        # Timeline header
        timeline_header = QLabel("📈 Task Timeline")
        timeline_header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        timeline_header.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: {ModernTheme.scale_value(8)}px;
                margin-bottom: 8px;
            }}
        """)
        timeline_layout.addWidget(timeline_header)
        
        # Timeline scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Timeline content widget
        self.timeline_content = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_content)
        self.timeline_layout.setContentsMargins(8, 8, 8, 8)
        self.timeline_layout.setSpacing(8)
        
        # Add initial empty state
        self.add_empty_timeline_state()
        
        scroll_area.setWidget(self.timeline_content)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: {ModernTheme.get_colors()['bg_secondary']};
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(8)}px;
            }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {ModernTheme.get_colors()['accent']};
                border-radius: 4px;
                min-height: 20px;
            }}
        """)
        
        timeline_layout.addWidget(scroll_area)
        
        return timeline_container
    
    def create_detailed_results_viewer(self) -> QWidget:
        """Create detailed results viewer"""
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout(viewer_container)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(12)
        
        # Viewer header
        viewer_header = QLabel("📄 Detailed Results")
        viewer_header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        viewer_header.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: {ModernTheme.scale_value(8)}px;
            }}
        """)
        viewer_layout.addWidget(viewer_header)
        
        # Results browser
        self.results_text = QTextBrowser()
        self.results_text.setOpenExternalLinks(True)
        self.results_text.setHtml(self.get_empty_results_html())
        self.results_text.setStyleSheet(f"""
            QTextBrowser {{
                background: {ModernTheme.get_colors()['bg_secondary']};
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(8)}px;
                color: {ModernTheme.get_colors()['text_primary']};
                font-size: 13px;
                padding: 12px;
                selection-background-color: {ModernTheme.get_colors()['accent']};
            }}
        """)
        viewer_layout.addWidget(self.results_text)
        
        return viewer_container
    
    def add_empty_timeline_state(self):
        """Add empty state to timeline"""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setContentsMargins(20, 40, 20, 40)
        
        empty_icon = QLabel("🎯")
        empty_icon.setFont(QFont("Arial", 32))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon.setStyleSheet("color: #666;")
        empty_layout.addWidget(empty_icon)
        
        empty_text = QLabel("No tasks completed yet")
        empty_text.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text.setStyleSheet("color: #888; margin-top: 8px;")
        empty_layout.addWidget(empty_text)
        
        empty_desc = QLabel("Complete a task to see results appear here")
        empty_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_desc.setStyleSheet("color: #666; font-size: 12px;")
        empty_layout.addWidget(empty_desc)
        
        self.timeline_layout.addWidget(empty_widget)
        self.timeline_layout.addStretch()
    
    def get_empty_results_html(self) -> str:
        """Get HTML for empty results state"""
        return f"""
        <div style='padding: 40px; text-align: center; font-family: Inter, sans-serif;'>
            <div style='font-size: 48px; margin-bottom: 16px;'>📄</div>
            <h3 style='color: {ModernTheme.get_colors()['text_primary']}; margin: 0 0 8px 0;'>
                Select a Task to View Details
            </h3>
            <p style='color: {ModernTheme.get_colors()['text_secondary']}; margin: 0; font-size: 14px;'>
                Click on a task from the timeline above to see detailed results, analysis, and generated files.
            </p>
        </div>
        """
    
    def update_session_stats(self):
        """Update session statistics display"""
        try:
            task_count = len(self.task_results)
            self.session_tasks_label.setText(f"{task_count} tasks completed")
            
            # Calculate session duration
            duration = datetime.now() - self.session_start_time
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            if hours > 0:
                time_text = f"{hours}h {minutes}m session"
            else:
                time_text = f"{minutes}m session"
                
            self.session_time_label.setText(time_text)
            
        except Exception as e:
            logging.error(f"Error updating session stats: {e}")
    
    def add_task_to_timeline(self, task_data: dict):
        """Add a new task to the timeline"""
        try:
            # Remove empty state if this is the first task
            if len(self.task_results) == 0:
                # Clear existing widgets
                for i in reversed(range(self.timeline_layout.count())):
                    child = self.timeline_layout.itemAt(i).widget()
                    if child:
                        child.deleteLater()
            
            # Add task to results list
            self.task_results.append(task_data)
            
            # Create timeline item
            timeline_item = self.create_timeline_item(task_data, len(self.task_results) - 1)
            self.timeline_layout.insertWidget(self.timeline_layout.count() - 1, timeline_item)
            
            # Update session stats
            self.update_session_stats()
            
        except Exception as e:
            logging.error(f"Error adding task to timeline: {e}")
    
    def create_timeline_item(self, task_data: dict, index: int) -> QWidget:
        """Create a timeline item widget"""
        item_widget = QWidget()
        item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Store index for selection
        item_widget.task_index = index
        
        # Set up click handler
        item_widget.mousePressEvent = lambda event: self.on_timeline_item_clicked(index)
        
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(12, 12, 12, 12)
        item_layout.setSpacing(12)
        
        # Task type icon and color
        task_type = task_data.get('task_type', 'unknown')
        task_icon, task_color = self.get_task_type_info(task_type)
        
        # Timeline indicator
        indicator = QLabel("●")
        indicator.setFont(QFont("Arial", 16))
        indicator.setStyleSheet(f"color: {task_color};")
        indicator.setFixedWidth(20)
        item_layout.addWidget(indicator)
        
        # Main content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Task title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        icon_label = QLabel(task_icon)
        icon_label.setFont(QFont("Arial", 14))
        title_layout.addWidget(icon_label)
        
        title_text = task_data.get('title', f'{task_type.title()} Task')
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_primary']};")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Time and status
        time_str = task_data.get('timestamp', datetime.now()).strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']}; font-size: 11px;")
        title_layout.addWidget(time_label)
        
        content_layout.addLayout(title_layout)
        
        # Task summary
        prompt = task_data.get('prompt', '')
        summary = (prompt[:80] + '...' if len(prompt) > 80 else prompt) if prompt else 'Task completed'
        summary_label = QLabel(summary)
        summary_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']}; font-size: 12px;")
        summary_label.setWordWrap(True)
        content_layout.addWidget(summary_label)
        
        # Task stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        # Files generated
        files_count = len(task_data.get('generated_files', []))
        if files_count > 0:
            files_label = QLabel(f"📁 {files_count} files")
            files_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']}; font-size: 11px;")
            stats_layout.addWidget(files_label)
        
        # Response time
        response_time = task_data.get('response_time', 0)
        if response_time > 0:
            time_label = QLabel(f"⏱️ {response_time:.1f}s")
            time_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']}; font-size: 11px;")
            stats_layout.addWidget(time_label)
        
        # Tokens used
        tokens = task_data.get('tokens_used', 0)
        if tokens > 0:
            tokens_label = QLabel(f"🔤 {tokens} tokens")
            tokens_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']}; font-size: 11px;")
            stats_layout.addWidget(tokens_label)
        
        stats_layout.addStretch()
        content_layout.addLayout(stats_layout)
        
        item_layout.addLayout(content_layout)
        
        # Style the item
        item_widget.setStyleSheet(f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {ModernTheme.scale_value(8)}px;
                margin: 2px;
            }}
            QWidget:hover {{
                background: rgba(255, 255, 255, 0.08);
                border-color: {task_color};
            }}
        """)
        
        return item_widget
    
    def get_task_type_info(self, task_type: str) -> tuple:
        """Get icon and color for task type"""
        task_info = {
            'code': ('🐍', '#38bdf8'),
            'multimedia': ('🖼️', '#8b5cf6'), 
            'rag': ('📚', '#06ffa5'),
            'automation': ('⚡', '#f59e0b'),
            'analytics': ('📊', '#ef4444'),
            'claude_query': ('🤖', '#10b981'),
            'ollama_query': ('🧠', '#f97316'),
            'unknown': ('❓', '#6b7280')
        }
        return task_info.get(task_type, task_info['unknown'])
    
    def on_timeline_item_clicked(self, index: int):
        """Handle timeline item selection"""
        try:
            if 0 <= index < len(self.task_results):
                self.selected_task_index = index
                task_data = self.task_results[index]
                
                # Update visual selection
                self.update_timeline_selection(index)
                
                # Show detailed results
                self.show_task_details(task_data)
                
        except Exception as e:
            logging.error(f"Error handling timeline selection: {e}")
    
    def update_timeline_selection(self, selected_index: int):
        """Update visual selection in timeline"""
        try:
            for i in range(self.timeline_layout.count()):
                item = self.timeline_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if hasattr(widget, 'task_index'):
                        task_type = self.task_results[widget.task_index].get('task_type', 'unknown')
                        _, task_color = self.get_task_type_info(task_type)
                        
                        if widget.task_index == selected_index:
                            # Selected style
                            widget.setStyleSheet(f"""
                                QWidget {{
                                    background: rgba({task_color.replace('#', '')}, 0.2);
                                    border: 2px solid {task_color};
                                    border-radius: {ModernTheme.scale_value(8)}px;
                                    margin: 2px;
                                }}
                            """)
                        else:
                            # Normal style
                            widget.setStyleSheet(f"""
                                QWidget {{
                                    background: rgba(255, 255, 255, 0.03);
                                    border: 1px solid rgba(255, 255, 255, 0.1);
                                    border-radius: {ModernTheme.scale_value(8)}px;
                                    margin: 2px;
                                }}
                                QWidget:hover {{
                                    background: rgba(255, 255, 255, 0.08);
                                    border-color: {task_color};
                                }}
                            """)
        except Exception as e:
            logging.error(f"Error updating timeline selection: {e}")
    
    def show_task_details(self, task_data: dict):
        """Show detailed task information"""
        try:
            task_type = task_data.get('task_type', 'unknown')
            task_icon, task_color = self.get_task_type_info(task_type)
            
            # Generate comprehensive HTML
            html_content = f"""
            <div style='font-family: Inter, sans-serif; line-height: 1.6;'>
                <!-- Task Header -->
                <div style='background: linear-gradient(135deg, {task_color}20 0%, {task_color}10 100%); 
                           padding: 20px; border-radius: 12px; margin-bottom: 20px; 
                           border-left: 4px solid {task_color};'>
                    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                        <span style='font-size: 24px; margin-right: 12px;'>{task_icon}</span>
                        <h2 style='margin: 0; color: {ModernTheme.get_colors()['text_primary']}; font-size: 20px;'>
                            {task_data.get('title', f'{task_type.title()} Task')}
                        </h2>
                    </div>
                    <p style='margin: 0; color: {ModernTheme.get_colors()['text_secondary']}; font-size: 14px;'>
                        Completed at {task_data.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
                
                <!-- Task Prompt -->
                <div style='background: rgba(255,255,255,0.05); padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                    <h3 style='margin: 0 0 12px 0; color: {ModernTheme.get_colors()['primary']}; font-size: 16px;'>
                        📝 Original Request
                    </h3>
                    <div style='background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; 
                              border-left: 3px solid {task_color};'>
                        <p style='margin: 0; font-size: 13px; white-space: pre-wrap;'>{task_data.get('prompt', 'No prompt recorded')}</p>
                    </div>
                </div>
                
                <!-- Task Results -->
                <div style='background: rgba(255,255,255,0.05); padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                    <h3 style='margin: 0 0 12px 0; color: {ModernTheme.get_colors()['accent']}; font-size: 16px;'>
                        🎯 AI Response
                    </h3>
                    <div style='background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; max-height: 300px; overflow-y: auto;'>
                        <div style='font-size: 13px;'>{task_data.get('result', 'No result recorded')}</div>
                    </div>
                </div>
                
                <!-- Generated Files -->
                {self.generate_files_section_html(task_data.get('generated_files', []))}
                
                <!-- Task Statistics -->
                <div style='background: rgba(255,255,255,0.05); padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                    <h3 style='margin: 0 0 12px 0; color: {ModernTheme.get_colors()['secondary']}; font-size: 16px;'>
                        📊 Task Statistics
                    </h3>
                    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px;'>
                        <div style='text-align: center; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px;'>
                            <div style='font-size: 18px; color: {task_color};'>⏱️</div>
                            <div style='font-size: 12px; color: {ModernTheme.get_colors()['text_secondary']};'>Response Time</div>
                            <div style='font-weight: bold;'>{task_data.get('response_time', 0):.1f}s</div>
                        </div>
                        <div style='text-align: center; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px;'>
                            <div style='font-size: 18px; color: {task_color};'>🔤</div>
                            <div style='font-size: 12px; color: {ModernTheme.get_colors()['text_secondary']};'>Tokens Used</div>
                            <div style='font-weight: bold;'>{task_data.get('tokens_used', 0)}</div>
                        </div>
                        <div style='text-align: center; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px;'>
                            <div style='font-size: 18px; color: {task_color};'>📁</div>
                            <div style='font-size: 12px; color: {ModernTheme.get_colors()['text_secondary']};'>Files Generated</div>
                            <div style='font-weight: bold;'>{len(task_data.get('generated_files', []))}</div>
                        </div>
                        <div style='text-align: center; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px;'>
                            <div style='font-size: 18px; color: {task_color};'>{task_icon}</div>
                            <div style='font-size: 12px; color: {ModernTheme.get_colors()['text_secondary']};'>Task Type</div>
                            <div style='font-weight: bold;'>{task_type.title()}</div>
                        </div>
                    </div>
                </div>
            </div>
            """
            
            self.results_text.setHtml(html_content)
            
        except Exception as e:
            logging.error(f"Error showing task details: {e}")
    
    def generate_files_section_html(self, generated_files: list) -> str:
        """Generate HTML for generated files section"""
        if not generated_files:
            return """
            <div style='background: rgba(255,255,255,0.05); padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                <h3 style='margin: 0 0 12px 0; color: #f59e0b; font-size: 16px;'>📁 Generated Files</h3>
                <p style='margin: 0; text-align: center; color: #666; font-style: italic;'>No files were generated for this task</p>
            </div>
            """
        
        files_html = ""
        for file_path in generated_files:
            try:
                path_obj = Path(file_path)
                file_name = path_obj.name
                file_size = self.get_file_size(path_obj) if path_obj.exists() else "Unknown"
                file_icon, file_type = self.get_file_info(path_obj)
                
                files_html += f"""
                <div style='display: flex; align-items: center; padding: 8px; background: rgba(0,0,0,0.2); 
                           border-radius: 6px; margin-bottom: 8px;'>
                    <span style='font-size: 16px; margin-right: 12px;'>{file_icon}</span>
                    <div style='flex: 1;'>
                        <div style='font-weight: bold; font-size: 13px;'>{file_name}</div>
                        <div style='font-size: 11px; color: {ModernTheme.get_colors()['text_secondary']};'>
                            {file_type} • {file_size}
                        </div>
                    </div>
                    <div style='font-size: 11px; color: {ModernTheme.get_colors()['text_secondary']};'>
                        {str(path_obj.parent) if path_obj.exists() else 'Path not found'}
                    </div>
                </div>
                """
            except Exception as e:
                files_html += f"""
                <div style='padding: 8px; background: rgba(255,0,0,0.1); border-radius: 6px; margin-bottom: 8px;'>
                    <span style='color: #ef4444;'>❌ Error loading file: {file_path}</span>
                </div>
                """
        
        return f"""
        <div style='background: rgba(255,255,255,0.05); padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
            <h3 style='margin: 0 0 12px 0; color: #f59e0b; font-size: 16px;'>📁 Generated Files ({len(generated_files)})</h3>
            {files_html}
        </div>
        """
    
    def clear_all_results(self):
        """Clear all task results"""
        reply = QMessageBox.question(
            self, 
            'Clear All Results',
            'Are you sure you want to clear all task results?\n\nThis will remove the timeline and detailed views.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear data
                self.task_results.clear()
                self.selected_task_index = -1
                
                # Clear timeline
                for i in reversed(range(self.timeline_layout.count())):
                    child = self.timeline_layout.itemAt(i).widget()
                    if child:
                        child.deleteLater()
                
                # Add empty state back
                self.add_empty_timeline_state()
                
                # Clear results viewer
                self.results_text.setHtml(self.get_empty_results_html())
                
                # Update stats
                self.update_session_stats()
                
            except Exception as e:
                logging.error(f"Error clearing results: {e}")
    
    def export_session_report(self):
        """Export a comprehensive session report"""
        try:
            if not self.task_results:
                QMessageBox.information(self, 'No Data', 'No tasks to export.')
                return
            
            # Generate session report
            session_duration = datetime.now() - self.session_start_time
            total_tasks = len(self.task_results)
            total_files = sum(len(task.get('generated_files', [])) for task in self.task_results)
            total_tokens = sum(task.get('tokens_used', 0) for task in self.task_results)
            avg_response_time = sum(task.get('response_time', 0) for task in self.task_results) / total_tasks if total_tasks else 0
            
            # Create report content
            report_content = f"""
            # SuperMini AI Session Report
            
            **Session Date:** {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}
            **Session Duration:** {session_duration}
            
            ## Summary Statistics
            - **Total Tasks Completed:** {total_tasks}
            - **Total Files Generated:** {total_files}
            - **Total Tokens Used:** {total_tokens:,}
            - **Average Response Time:** {avg_response_time:.2f} seconds
            
            ## Task Details
            """
            
            for i, task in enumerate(self.task_results, 1):
                task_type = task.get('task_type', 'unknown')
                timestamp = task.get('timestamp', datetime.now())
                prompt = task.get('prompt', 'No prompt')
                response_time = task.get('response_time', 0)
                tokens = task.get('tokens_used', 0)
                files = task.get('generated_files', [])
                
                report_content += f"""
            ### Task {i}: {task_type.title()}
            **Time:** {timestamp.strftime('%H:%M:%S')}
            **Prompt:** {prompt[:200]}{'...' if len(prompt) > 200 else ''}
            **Response Time:** {response_time:.1f}s
            **Tokens Used:** {tokens}
            **Files Generated:** {len(files)}
            
            """
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"supermini_session_report_{timestamp}.md"
            filepath = Path(self.data_dir) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            QMessageBox.information(self, 'Export Complete', f'Session report saved to:\n{filepath}')
            
        except Exception as e:
            logging.error(f"Error exporting session report: {e}")
            QMessageBox.warning(self, 'Export Error', f'Failed to export session report:\n{str(e)}')
    
    def create_files_tab(self) -> QWidget:
        """Create an enhanced tab for displaying generated files with directory tree view"""
        widget = QWidget()
        widget.setStyleSheet(f"background: transparent;")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Enhanced header with stats
        header_card = self.create_files_header()
        layout.addWidget(header_card)

        # Create the main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Modern directory tree
        tree_widget = self.create_modern_file_tree()
        splitter.addWidget(tree_widget)
        
        # Right side: File details panel
        details_widget = self.create_file_details_panel()
        splitter.addWidget(details_widget)
        
        # Set splitter proportions (70% tree, 30% details)
        splitter.setSizes([700, 300])
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {ModernTheme.get_colors()['border']};
                width: 2px;
            }}
            QSplitter::handle:hover {{
                background: {ModernTheme.get_colors()['accent']};
            }}
        """)
        
        layout.addWidget(splitter)
        
        # Initialize file tracking
        self.generated_files_data = {}
        self.selected_file_path = None
        
        widget.setLayout(layout)
        return widget
    
    def create_files_header(self) -> QWidget:
        """Create enhanced header for files tab with statistics"""
        header_card = QWidget()
        header_card.setFixedHeight(80)
        header_card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(56, 189, 248, 0.1),
                    stop:0.5 rgba(139, 92, 246, 0.1),
                    stop:1 rgba(6, 255, 165, 0.1));
                border-radius: {ModernTheme.scale_value(12)}px;
                border: 1px solid {ModernTheme.get_colors()['border']};
            }}
        """)
        
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 12, 20, 12)
        
        # Left side: Title and stats
        left_layout = QVBoxLayout()
        
        title_label = QLabel("📁 Generated Files")
        title_label.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                font-weight: 700;
            }}
        """)
        left_layout.addWidget(title_label)
        
        # Stats layout
        stats_layout = QHBoxLayout()
        
        self.files_count_label = QLabel("0 files")
        self.files_count_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_secondary']};
                font-size: 13px;
            }}
        """)
        stats_layout.addWidget(self.files_count_label)
        
        stats_layout.addWidget(QLabel(" • "))
        
        self.total_size_label = QLabel("0 MB")
        self.total_size_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_secondary']};
                font-size: 13px;
            }}
        """)
        stats_layout.addWidget(self.total_size_label)
        
        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        
        # Right side: Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        refresh_btn = self.create_button(
            "Refresh",
            "🔄",
            "secondary",
            "Refresh file list",
            100,
            self.refresh_files_display
        )
        refresh_btn.setStyleSheet(self.get_action_button_style())
        actions_layout.addWidget(refresh_btn)
        
        open_folder_btn = self.create_button(
            "Open Folder",
            "📂",
            "secondary",
            "Open the SuperMini output directory",
            120,
            self.open_output_folder
        )
        open_folder_btn.setStyleSheet(self.get_action_button_style())
        actions_layout.addWidget(open_folder_btn)
        
        clear_btn = self.create_button(
            "Clear All",
            "🗑️",
            "danger",
            "Clear all generated files",
            100,
            self.clear_generated_files
        )
        clear_btn.setStyleSheet(self.get_action_button_style())
        actions_layout.addWidget(clear_btn)
        
        header_layout.addLayout(actions_layout)
        
        return header_card
    
    def get_action_button_style(self) -> str:
        """Get consistent style for action buttons"""
        return f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.1);
                color: {ModernTheme.get_colors()['text_primary']};
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(8)}px;
                padding: {ModernTheme.scale_value(8)}px {ModernTheme.scale_value(12)}px;
                font-weight: 500;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {ModernTheme.get_colors()['accent']};
                border-color: {ModernTheme.get_colors()['accent']};
            }}
            QPushButton:pressed {{
                background: rgba(6, 255, 165, 0.3);
            }}
        """
    
    def create_modern_file_tree(self) -> QWidget:
        """Create a modern file tree widget"""
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tree header
        tree_header = QLabel("📁 Directory Structure")
        tree_header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        tree_header.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: {ModernTheme.scale_value(8)}px;
                margin-bottom: 8px;
            }}
        """)
        tree_layout.addWidget(tree_header)
        
        # Create tree widget
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type", "Size", "Modified"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setRootIsDecorated(True)
        self.file_tree.setAnimated(True)
        self.file_tree.itemSelectionChanged.connect(self.on_file_selected)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        
        # Style the tree
        self.file_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {ModernTheme.get_colors()['bg_secondary']};
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(8)}px;
                color: {ModernTheme.get_colors()['text_primary']};
                selection-background-color: {ModernTheme.get_colors()['accent']};
                alternate-background-color: rgba(255, 255, 255, 0.02);
                font-size: 13px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }}
            QTreeWidget::item:hover {{
                background: rgba(255, 255, 255, 0.08);
                border-radius: 4px;
            }}
            QTreeWidget::item:selected {{
                background: {ModernTheme.get_colors()['accent']};
                border-radius: 4px;
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNEwxMCA4TDYgMTJWNFoiIGZpbGw9IiNhYmFiYWIiLz4KPC9zdmc+);
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNkw4IDEwTDEyIDZINFoiIGZpbGw9IiNhYmFiYWIiLz4KPC9zdmc+);
            }}
            QHeaderView::section {{
                background: rgba(255, 255, 255, 0.1);
                color: {ModernTheme.get_colors()['text_primary']};
                padding: 8px;
                border: none;
                border-right: 1px solid {ModernTheme.get_colors()['border']};
                font-weight: 600;
            }}
        """)
        
        # Set column widths
        self.file_tree.setColumnWidth(0, 300)  # Name
        self.file_tree.setColumnWidth(1, 80)   # Type  
        self.file_tree.setColumnWidth(2, 80)   # Size
        self.file_tree.setColumnWidth(3, 120)  # Modified
        
        tree_layout.addWidget(self.file_tree)
        
        return tree_container
    
    def create_file_details_panel(self) -> QWidget:
        """Create file details panel"""
        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(12)
        
        # Details header
        details_header = QLabel("📄 File Details")
        details_header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        details_header.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['text_primary']};
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: {ModernTheme.scale_value(8)}px;
            }}
        """)
        details_layout.addWidget(details_header)
        
        # Details content
        self.file_details = QTextBrowser()
        self.file_details.setHtml("""
            <div style='padding: 20px; text-align: center; color: #888;'>
                <h3>📄 No File Selected</h3>
                <p>Select a file from the tree to view details</p>
            </div>
        """)
        self.file_details.setStyleSheet(f"""
            QTextBrowser {{
                background: {ModernTheme.get_colors()['bg_secondary']};
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(8)}px;
                color: {ModernTheme.get_colors()['text_primary']};
                font-size: 13px;
                padding: 8px;
            }}
        """)
        details_layout.addWidget(self.file_details)
        
        # Action buttons for selected file
        file_actions_layout = QHBoxLayout()
        
        self.open_file_btn = self.create_button(
            "Open File",
            "📖",
            "secondary",
            "Open selected file",
            100,
            self.open_selected_file
        )
        self.open_file_btn.setEnabled(False)
        self.open_file_btn.setStyleSheet(self.get_action_button_style())
        file_actions_layout.addWidget(self.open_file_btn)
        
        self.reveal_file_btn = self.create_button(
            "Reveal",
            "👁️",
            "secondary",
            "Reveal file in finder",
            80,
            self.reveal_selected_file
        )
        self.reveal_file_btn.setEnabled(False)
        self.reveal_file_btn.setStyleSheet(self.get_action_button_style())
        file_actions_layout.addWidget(self.reveal_file_btn)
        
        file_actions_layout.addStretch()
        details_layout.addLayout(file_actions_layout)
        
        return details_container
    
    def refresh_files_display(self):
        """Refresh the files display by scanning output directory"""
        try:
            self.file_tree.clear()
            self.generated_files_data.clear()
            
            output_dir = Path(self.data_dir)
            if not output_dir.exists():
                return
            
            # Create directory structure
            self.populate_file_tree(output_dir)
            self.update_file_stats()
            
        except Exception as e:
            logging.error(f"Error refreshing files display: {e}")
    
    def populate_file_tree(self, root_path: Path, parent_item: QTreeWidgetItem = None):
        """Populate the file tree with directory structure"""
        try:
            # Sort directories first, then files
            items = sorted(root_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item_path in items:
                if item_path.name.startswith('.'):
                    continue  # Skip hidden files
                
                # Create tree item
                if parent_item:
                    tree_item = QTreeWidgetItem(parent_item)
                else:
                    tree_item = QTreeWidgetItem(self.file_tree)
                
                # Set basic info
                file_name = item_path.name
                
                if item_path.is_dir():
                    # Directory
                    tree_item.setText(0, f"📁 {file_name}")
                    tree_item.setText(1, "Folder")
                    tree_item.setText(2, "-")
                    tree_item.setText(3, self.get_file_modified_date(item_path))
                    
                    # Set icon and expand behavior
                    tree_item.setExpanded(False)
                    
                    # Recursively populate subdirectories
                    self.populate_file_tree(item_path, tree_item)
                    
                else:
                    # File - check if we have metadata for enhanced display
                    file_path_str = str(item_path)
                    metadata = None
                    if hasattr(self, 'stored_file_metadata') and file_path_str in self.stored_file_metadata:
                        metadata = self.stored_file_metadata[file_path_str]
                    
                    if metadata:
                        # Use metadata for enhanced display
                        display_name = metadata.display_name
                        file_type = metadata.file_type
                        file_icon = self._get_metadata_icon(metadata.file_type)
                        
                        tree_item.setText(0, f"{file_icon} {display_name}")
                        tree_item.setText(1, file_type)
                        tree_item.setText(2, self.get_file_size(item_path))
                        tree_item.setText(3, self.get_file_modified_date(item_path))
                        
                        # Store enhanced file data with metadata
                        self.generated_files_data[file_path_str] = {
                            'path': item_path,
                            'name': display_name,
                            'original_name': file_name,
                            'type': file_type,
                            'size': self.get_file_size(item_path),
                            'icon': file_icon,
                            'tree_item': tree_item,
                            'metadata': metadata
                        }
                    else:
                        # Fallback to original display method
                        file_icon, file_type = self.get_file_info(item_path)
                        file_size = self.get_file_size(item_path)
                        
                        tree_item.setText(0, f"{file_icon} {file_name}")
                        tree_item.setText(1, file_type)
                        tree_item.setText(2, file_size)
                        tree_item.setText(3, self.get_file_modified_date(item_path))
                        
                        # Store file data
                        self.generated_files_data[file_path_str] = {
                            'path': item_path,
                            'name': file_name,
                            'original_name': file_name,
                            'type': file_type,
                            'size': file_size,
                            'icon': file_icon,
                            'tree_item': tree_item,
                            'metadata': None
                        }
                
                # Store path in item data
                tree_item.setData(0, Qt.ItemDataRole.UserRole, str(item_path))
                
        except Exception as e:
            logging.error(f"Error populating file tree: {e}")
    
    def get_file_info(self, file_path: Path) -> tuple:
        """Get file icon and type based on extension"""
        suffix = file_path.suffix.lower()
        
        # File type mappings
        file_types = {
            '.py': ('🐍', 'Python'),
            '.js': ('📜', 'JavaScript'),
            '.html': ('🌐', 'HTML'),
            '.css': ('🎨', 'CSS'),
            '.json': ('📋', 'JSON'),
            '.txt': ('📄', 'Text'),
            '.md': ('📝', 'Markdown'),
            '.pdf': ('📕', 'PDF'),
            '.docx': ('📘', 'Word'),
            '.xlsx': ('📊', 'Excel'),
            '.png': ('🖼️', 'Image'),
            '.jpg': ('🖼️', 'Image'),
            '.jpeg': ('🖼️', 'Image'),
            '.gif': ('🖼️', 'Image'),
            '.mp4': ('🎥', 'Video'),
            '.mp3': ('🎵', 'Audio'),
            '.zip': ('📦', 'Archive'),
            '.sh': ('⚡', 'Shell'),
            '.sql': ('🗃️', 'Database'),
            '.csv': ('📈', 'Data'),
            '.log': ('📋', 'Log'),
        }
        
        return file_types.get(suffix, ('📄', 'File'))
    
    def get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size"""
        try:
            size = file_path.stat().st_size
            
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def get_file_modified_date(self, file_path: Path) -> str:
        """Get file modification date"""
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime).strftime("%m/%d %H:%M")
        except:
            return "Unknown"
    
    def update_file_stats(self):
        """Update file count and total size statistics"""
        try:
            file_count = len(self.generated_files_data)
            total_size = 0
            
            for file_data in self.generated_files_data.values():
                try:
                    total_size += file_data['path'].stat().st_size
                except:
                    continue
            
            # Update labels
            self.files_count_label.setText(f"{file_count} files")
            
            if total_size < 1024 * 1024:
                size_text = f"{total_size / 1024:.1f} KB"
            else:
                size_text = f"{total_size / (1024 * 1024):.1f} MB"
            
            self.total_size_label.setText(size_text)
            
        except Exception as e:
            logging.error(f"Error updating file stats: {e}")
    
    def on_file_selected(self):
        """Handle file selection in tree"""
        try:
            selected_items = self.file_tree.selectedItems()
            if not selected_items:
                self.selected_file_path = None
                self.open_file_btn.setEnabled(False)
                self.reveal_file_btn.setEnabled(False)
                self.file_details.setHtml("""
                    <div style='padding: 20px; text-align: center; color: #888;'>
                        <h3>📄 No File Selected</h3>
                        <p>Select a file from the tree to view details</p>
                    </div>
                """)
                return
            
            item = selected_items[0]
            file_path_str = item.data(0, Qt.ItemDataRole.UserRole)
            file_path = Path(file_path_str)
            
            if file_path.is_file() and str(file_path) in self.generated_files_data:
                self.selected_file_path = file_path
                self.open_file_btn.setEnabled(True)
                self.reveal_file_btn.setEnabled(True)
                self.show_file_details(file_path)
            else:
                self.selected_file_path = None
                self.open_file_btn.setEnabled(False)
                self.reveal_file_btn.setEnabled(False)
                self.show_folder_details(file_path)
                
        except Exception as e:
            logging.error(f"Error handling file selection: {e}")
    
    def show_file_details(self, file_path: Path):
        """Show detailed information about selected file with enhanced metadata display"""
        try:
            file_data = self.generated_files_data.get(str(file_path))
            if not file_data:
                return
            
            # Get file stats
            stat = file_path.stat()
            created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if we have metadata for enhanced display
            metadata = file_data.get('metadata')
            
            # Try to get file preview
            preview = self.get_file_preview(file_path)
            
            if metadata:
                # Enhanced display with metadata
                html_content = f"""
                <div style='padding: 16px; font-family: Inter, sans-serif;'>
                    <div style='background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 100%); 
                               color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                        <h3 style='margin: 0; font-size: 18px;'>{file_data['icon']} {metadata.display_name}</h3>
                        <p style='margin: 6px 0 0 0; opacity: 0.9; font-size: 13px;'>{metadata.file_type} • {file_data['size']}</p>
                        <p style='margin: 8px 0 0 0; opacity: 0.8; font-size: 12px; font-style: italic;'>{metadata.description}</p>
                    </div>
                    
                    <div style='background: rgba(6, 255, 165, 0.1); border: 1px solid rgba(6, 255, 165, 0.3); 
                               padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
                        <h4 style='margin: 0 0 8px 0; color: #06ffa5; font-size: 14px;'>🎯 Purpose & Function</h4>
                        <p style='margin: 0; font-size: 12px; line-height: 1.4; color: #e5e5e5;'>{metadata.purpose}</p>
                    </div>
                    
                    <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
                        <h4 style='margin: 0 0 8px 0; color: #8b5cf6; font-size: 14px;'>📋 File Details</h4>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Display Name:</strong> {metadata.display_name}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Original Name:</strong> {file_data.get('original_name', file_path.name)}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>File Type:</strong> {metadata.file_type}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Size:</strong> {file_data['size']}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Created:</strong> {created}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Generated:</strong> {datetime.fromtimestamp(metadata.created_timestamp).strftime("%Y-%m-%d %H:%M:%S")}</p>
                    </div>
                    
                    <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
                        <h4 style='margin: 0 0 8px 0; color: #f59e0b; font-size: 14px;'>📁 Location</h4>
                        <p style='margin: 0; font-size: 11px; color: #a3a3a3; word-break: break-all;'>{file_path}</p>
                    </div>
                    
                    {preview}
                </div>
                """
            else:
                # Fallback display without metadata
                file_use = self.get_file_use_description(file_path)
                
                html_content = f"""
                <div style='padding: 16px; font-family: Inter, sans-serif;'>
                    <div style='background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); 
                               color: white; padding: 12px; border-radius: 8px; margin-bottom: 16px;'>
                        <h3 style='margin: 0; font-size: 16px;'>{file_data['icon']} {file_data['name']}</h3>
                        <p style='margin: 4px 0 0 0; opacity: 0.9; font-size: 13px;'>{file_data['type']} • {file_data['size']}</p>
                    </div>
                    
                    <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
                        <h4 style='margin: 0 0 8px 0; color: #06ffa5; font-size: 14px;'>📋 File Information</h4>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Path:</strong> {file_path}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Created:</strong> {created}</p>
                        <p style='margin: 2px 0; font-size: 12px;'><strong>Modified:</strong> {modified}</p>
                    </div>
                    
                    <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
                        <h4 style='margin: 0 0 8px 0; color: #f59e0b; font-size: 14px;'>🎯 Purpose & Use</h4>
                        <p style='margin: 0; font-size: 12px; line-height: 1.4;'>{file_use}</p>
                    </div>
                    
                    {preview}
                </div>
                """
            
            self.file_details.setHtml(html_content)
            
        except Exception as e:
            logging.error(f"Error showing file details: {e}")
    
    def show_folder_details(self, folder_path: Path):
        """Show information about selected folder"""
        try:
            if not folder_path.is_dir():
                return
            
            # Count contents
            file_count = 0
            folder_count = 0
            total_size = 0
            
            for item in folder_path.rglob('*'):
                if item.is_file():
                    file_count += 1
                    try:
                        total_size += item.stat().st_size
                    except:
                        pass
                elif item.is_dir():
                    folder_count += 1
            
            size_text = f"{total_size / (1024 * 1024):.1f} MB" if total_size > 1024*1024 else f"{total_size / 1024:.1f} KB"
            
            html_content = f"""
            <div style='padding: 16px; font-family: Inter, sans-serif;'>
                <div style='background: linear-gradient(135deg, #8b5cf6 0%, #06ffa5 100%); 
                           color: white; padding: 12px; border-radius: 8px; margin-bottom: 16px;'>
                    <h3 style='margin: 0; font-size: 16px;'>📁 {folder_path.name}</h3>
                    <p style='margin: 4px 0 0 0; opacity: 0.9; font-size: 13px;'>Directory</p>
                </div>
                
                <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px;'>
                    <h4 style='margin: 0 0 8px 0; color: #06ffa5; font-size: 14px;'>📊 Contents</h4>
                    <p style='margin: 2px 0; font-size: 12px;'><strong>Files:</strong> {file_count}</p>
                    <p style='margin: 2px 0; font-size: 12px;'><strong>Folders:</strong> {folder_count}</p>
                    <p style='margin: 2px 0; font-size: 12px;'><strong>Total Size:</strong> {size_text}</p>
                    <p style='margin: 2px 0; font-size: 12px;'><strong>Path:</strong> {folder_path}</p>
                </div>
            </div>
            """
            
            self.file_details.setHtml(html_content)
            
        except Exception as e:
            logging.error(f"Error showing folder details: {e}")
    
    def get_file_preview(self, file_path: Path) -> str:
        """Get a preview of file contents"""
        try:
            if file_path.suffix.lower() in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.sh', '.sql', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)  # First 500 characters
                    
                if len(content) == 500:
                    content += "..."
                
                # Escape HTML characters
                content = content.replace('<', '&lt;').replace('>', '&gt;')
                
                return f"""
                <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px;'>
                    <h4 style='margin: 0 0 8px 0; color: #8b5cf6; font-size: 14px;'>👁️ Preview</h4>
                    <pre style='margin: 0; font-size: 11px; line-height: 1.3; white-space: pre-wrap; 
                              background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px; 
                              max-height: 150px; overflow-y: auto;'>{content}</pre>
                </div>
                """
            else:
                return f"""
                <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px;'>
                    <h4 style='margin: 0 0 8px 0; color: #8b5cf6; font-size: 14px;'>👁️ Preview</h4>
                    <p style='margin: 0; font-size: 12px; color: #888; text-align: center; padding: 20px;'>
                        Preview not available for this file type
                    </p>
                </div>
                """
        except:
            return ""
    
    def get_file_use_description(self, file_path: Path) -> str:
        """Generate a description of what the file is used for"""
        suffix = file_path.suffix.lower()
        name = file_path.stem.lower()
        
        # Analyze file purpose based on name and extension
        if 'test' in name:
            return "Test file containing unit tests or test cases for validating functionality."
        elif suffix == '.py':
            if 'main' in name or 'app' in name:
                return "Main Python application file - entry point for program execution."
            elif 'config' in name or 'settings' in name:
                return "Configuration file containing application settings and parameters."
            else:
                return "Python script containing functions, classes, or automation logic."
        elif suffix in ['.js', '.html', '.css']:
            return "Web development file for creating interactive user interfaces and web applications."
        elif suffix == '.json':
            return "Data configuration file storing structured information in JSON format."
        elif suffix == '.md':
            return "Documentation file written in Markdown format with project information."
        elif suffix == '.txt':
            return "Plain text file containing notes, data, or human-readable information."
        elif suffix in ['.png', '.jpg', '.jpeg', '.gif']:
            return "Image file for visual content, graphics, or user interface elements."
        elif suffix == '.sh':
            return "Shell script for automating system tasks and command-line operations."
        elif suffix == '.sql':
            return "Database script containing SQL queries and database operations."
        elif suffix == '.csv':
            return "Data file in comma-separated values format for spreadsheet applications."
        elif suffix == '.log':
            return "Log file containing application events, errors, and debugging information."
        else:
            return "Generated file created by SuperMini AI assistant for task completion."
    
    def on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on file item"""
        self.open_selected_file()
    
    def open_selected_file(self):
        """Open the selected file with default application"""
        if self.selected_file_path and self.selected_file_path.exists():
            try:
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', str(self.selected_file_path)])
                elif sys.platform == 'win32':  # Windows
                    os.startfile(str(self.selected_file_path))
                else:  # Linux
                    subprocess.run(['xdg-open', str(self.selected_file_path)])
            except Exception as e:
                logging.error(f"Error opening file: {e}")
    
    def reveal_selected_file(self):
        """Reveal the selected file in file manager"""
        if self.selected_file_path and self.selected_file_path.exists():
            try:
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', '-R', str(self.selected_file_path)])
                elif sys.platform == 'win32':  # Windows
                    subprocess.run(['explorer', '/select,', str(self.selected_file_path)])
                else:  # Linux
                    subprocess.run(['xdg-open', str(self.selected_file_path.parent)])
            except Exception as e:
                logging.error(f"Error revealing file: {e}")
    
    def clear_generated_files(self):
        """Clear all generated files after confirmation"""
        reply = QMessageBox.question(
            self, 
            'Clear Generated Files',
            'Are you sure you want to delete all generated files?\n\nThis action cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                output_dir = Path(self.data_dir)
                if output_dir.exists():
                    # Remove all files except essential directories
                    for item in output_dir.rglob('*'):
                        if item.is_file() and not item.name.startswith('.'):
                            item.unlink()
                
                self.refresh_files_display()
                
            except Exception as e:
                logging.error(f"Error clearing files: {e}")
                QMessageBox.warning(self, 'Error', f'Failed to clear files: {str(e)}')

        widget.setLayout(layout)
        return widget
    
    def create_simple_system_info_tab(self) -> QWidget:
        """Create simple system info when matplotlib not available"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background: {ModernTheme.get_colors()['bg_secondary']};
                border-radius: {ModernTheme.scale_value(12)}px;
            }}
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("💻 System Information")
        title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernTheme.get_colors()['text_primary']};")
        layout.addWidget(title)

        try:
            import platform
            info_text = f"""
            <b>Platform:</b> {platform.system()} {platform.release()}<br>
            <b>Python Version:</b> {platform.python_version()}<br>
            <b>CPU Cores:</b> {psutil.cpu_count()}<br>
            <b>Memory:</b> {psutil.virtual_memory().total // (1024**3)} GB<br>
            <b>SuperMini Version:</b> 2.0 Neural Edition
            """
            info_label = QLabel(info_text)
            info_label.setStyleSheet(f"""
                QLabel {{
                    color: {ModernTheme.get_colors()['text_secondary']};
                    background: rgba(255, 255, 255, 0.05);
                    padding: {ModernTheme.scale_value(16)}px;
                    border-radius: {ModernTheme.scale_value(8)}px;
                    border: 1px solid {ModernTheme.get_colors()['border']};
                    font-size: {ModernTheme.get_font_size('base')};
                }}
            """)
            layout.addWidget(info_label)
        except Exception as e:
            error_label = QLabel(f"System info unavailable: {e}")
            error_label.setStyleSheet(f"""
                QLabel {{
                    color: {ModernTheme.get_colors()['error']};
                    background: rgba(255, 255, 255, 0.05);
                    padding: {ModernTheme.scale_value(16)}px;
                    border-radius: {ModernTheme.scale_value(8)}px;
                    border: 1px solid {ModernTheme.get_colors()['border']};
                }}
            """)
            layout.addWidget(error_label)

        layout.addStretch()
        return widget
    
    def create_ai_monitoring_dashboard(self) -> QWidget:
        """Create ultra-modern creative AI monitoring dashboard with stunning metric cards"""
        if not MATPLOTLIB_AVAILABLE:
            return self.create_simple_system_info_tab()

        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {ModernTheme.get_colors()['bg_primary']},
                    stop:1 {ModernTheme.get_colors()['bg_secondary']});
                border-radius: {ModernTheme.scale_value(16)}px;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Modern glass morphism header
        header_card = QWidget()
        header_card.setFixedHeight(80)
        header_card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(56, 189, 248, 0.15),
                    stop:0.5 rgba(139, 92, 246, 0.15),
                    stop:1 rgba(6, 255, 165, 0.15));
                border: 1px solid {ModernTheme.get_colors()['border']};
                border-radius: {ModernTheme.scale_value(16)}px;
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title_label = QLabel("⚡ AI Performance Hub")
        title_label.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernTheme.get_colors()['primary']},
                    stop:0.5 {ModernTheme.get_colors()['secondary']},
                    stop:1 {ModernTheme.get_colors()['accent']});
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
        """)
        header_layout.addWidget(title_label)

        self.ai_status_label = QLabel("🟢 LIVE")
        self.ai_status_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.ai_status_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.get_colors()['accent']};
                background: rgba(6, 255, 165, 0.15);
                border: 2px solid rgba(6, 255, 165, 0.4);
                border-radius: {ModernTheme.scale_value(12)}px;
                padding: {ModernTheme.scale_value(8)}px {ModernTheme.scale_value(16)}px;
                font-weight: 700;
            }}
        """)
        header_layout.addStretch()
        header_layout.addWidget(self.ai_status_label)
        layout.addWidget(header_card)

        # Initialize metrics tracking
        self.ai_metrics = {
            'timestamps': [],
            'token_usage': [],
            'response_times': [],
            'cpu_usage': [],
            'memory_usage': [],
            'gpu_usage': [],
            'task_count': 0,
            'total_tokens': 0,
            'avg_response_time': 0,
            'tasks_completed': 0,
            'task_execution_times': [],
            'avg_task_time': 0,
            'task_types': {}
        }

        # Modern metric cards grid
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        card_configs = [
            {
                'title': 'Tasks Completed',
                'key': 'tasks_completed',
                'icon': '🎯',
                'color': '#38bdf8',
                'bg_gradient': 'stop:0 rgba(56, 189, 248, 0.1), stop:1 rgba(56, 189, 248, 0.05)'
            },
            {
                'title': 'Total Tokens',
                'key': 'total_tokens',
                'icon': '🚀',
                'color': '#8b5cf6',
                'bg_gradient': 'stop:0 rgba(139, 92, 246, 0.1), stop:1 rgba(139, 92, 246, 0.05)'
            },
            {
                'title': 'Response Time',
                'key': 'avg_response_time',
                'icon': '⚡',
                'color': '#06ffa5',
                'bg_gradient': 'stop:0 rgba(6, 255, 165, 0.1), stop:1 rgba(6, 255, 165, 0.05)',
                'suffix': 's'
            },
            {
                'title': 'Task Time',
                'key': 'avg_task_time',
                'icon': '⏱️',
                'color': '#f59e0b',
                'bg_gradient': 'stop:0 rgba(245, 158, 11, 0.1), stop:1 rgba(245, 158, 11, 0.05)',
                'suffix': 's'
            }
        ]

        self.metric_cards = {}
        for config in card_configs:
            card = self.create_modern_metric_card(config)
            cards_layout.addWidget(card)
        layout.addLayout(cards_layout)

        # Create real-time graphs
        graphs_widget = self.create_dashboard_graphs()
        layout.addWidget(graphs_widget)

        layout.addStretch()
        
        # Setup dashboard refresh timer
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self.refresh_dashboard_display)
        self.dashboard_timer.start(1000)  # Refresh every second
        
        return widget
    
    def create_modern_metric_card(self, config: dict) -> QWidget:
        """Create a modern metric card with beautiful styling"""
        card = QWidget()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    {config['bg_gradient']});
                border: 1px solid {config['color']}40;
                border-radius: {ModernTheme.scale_value(16)}px;
                padding: {ModernTheme.scale_value(16)}px;
            }}
            QWidget:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {config['color']}20, stop:1 {config['color']}10);
                border: 2px solid {config['color']}60;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        # Icon and title row
        top_layout = QHBoxLayout()
        icon_label = QLabel(config['icon'])
        icon_label.setFont(QFont("Arial", 24))
        top_layout.addWidget(icon_label)

        title_label = QLabel(config['title'])
        title_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.get_colors()['text_secondary']};")
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Value display
        value_label = QLabel("0")
        value_label.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {config['color']};")
        layout.addWidget(value_label)
        
        # Store reference for updates
        self.metric_cards[config['key']] = value_label

        return card
    
    def create_dashboard_graphs(self) -> QWidget:
        """Create real-time dashboard graphs using matplotlib"""
        graphs_widget = QWidget()
        graphs_layout = QVBoxLayout(graphs_widget)
        graphs_layout.setContentsMargins(0, 0, 0, 0)
        graphs_layout.setSpacing(16)
        
        # Create matplotlib figure with dark theme
        self.dashboard_figure = Figure(figsize=(12, 8), facecolor='#1a1a1a')
        self.dashboard_canvas = FigureCanvas(self.dashboard_figure)
        self.dashboard_canvas.setStyleSheet(f"""
            QWidget {{
                background: {ModernTheme.get_colors()['bg_primary']};
                border-radius: {ModernTheme.scale_value(12)}px;
                border: 1px solid {ModernTheme.get_colors()['border']};
            }}
        """)
        
        # Create subplots for different metrics
        self.response_time_ax = self.dashboard_figure.add_subplot(2, 2, 1)
        self.token_usage_ax = self.dashboard_figure.add_subplot(2, 2, 2) 
        self.task_types_ax = self.dashboard_figure.add_subplot(2, 2, 3)
        self.system_metrics_ax = self.dashboard_figure.add_subplot(2, 2, 4)
        
        # Configure subplot styles
        self.configure_graph_styles()
        
        # Initialize empty data for graphs
        self.init_graph_data()
        
        graphs_layout.addWidget(self.dashboard_canvas)
        return graphs_widget
    
    def configure_graph_styles(self):
        """Configure matplotlib graph styles for dark theme"""
        # Dark theme colors
        bg_color = '#1a1a1a'
        text_color = '#e5e5e5'
        grid_color = '#333333'
        
        for ax in [self.response_time_ax, self.token_usage_ax, self.task_types_ax, self.system_metrics_ax]:
            ax.set_facecolor(bg_color)
            ax.tick_params(colors=text_color, labelsize=9)
            ax.grid(True, color=grid_color, alpha=0.3, linewidth=0.5)
            ax.spines['bottom'].set_color(text_color)
            ax.spines['top'].set_color(text_color)
            ax.spines['right'].set_color(text_color)
            ax.spines['left'].set_color(text_color)
            
        # Set titles
        self.response_time_ax.set_title('Response Times', color=text_color, fontsize=12, pad=10)
        self.token_usage_ax.set_title('Token Usage', color=text_color, fontsize=12, pad=10)
        self.task_types_ax.set_title('Task Distribution', color=text_color, fontsize=12, pad=10)
        self.system_metrics_ax.set_title('System Metrics', color=text_color, fontsize=12, pad=10)
        
        # Adjust layout
        self.dashboard_figure.tight_layout(pad=2.0)
    
    def init_graph_data(self):
        """Initialize empty data structures for graphs"""
        self.graph_data = {
            'timestamps': [],
            'response_times': [],
            'token_counts': [],
            'task_type_counts': {},
            'cpu_usage': [],
            'memory_usage': []
        }
        
        # Draw initial empty graphs
        self.update_dashboard_graphs()
    
    def update_dashboard_graphs(self):
        """Update all dashboard graphs with current data"""
        try:
            # Clear all subplots
            self.response_time_ax.clear()
            self.token_usage_ax.clear()
            self.task_types_ax.clear()
            self.system_metrics_ax.clear()
            
            # Reconfigure styles after clearing
            self.configure_graph_styles()
            
            # Update response times graph
            if self.ai_metrics.get('timestamps') and self.ai_metrics.get('response_times'):
                times = self.ai_metrics['timestamps'][-20:]  # Last 20 data points
                responses = self.ai_metrics['response_times'][-20:]
                
                if times and responses:
                    # Convert timestamps to relative time (seconds ago)
                    now = time.time()
                    relative_times = [(now - t) for t in reversed(times)]
                    
                    self.response_time_ax.plot(relative_times, list(reversed(responses)), 
                                             color='#06ffa5', linewidth=2, marker='o', markersize=3)
                    self.response_time_ax.set_xlabel('Seconds Ago', color='#e5e5e5', fontsize=9)
                    self.response_time_ax.set_ylabel('Response Time (s)', color='#e5e5e5', fontsize=9)
            
            # Update token usage graph
            if self.ai_metrics.get('timestamps') and self.ai_metrics.get('token_usage'):
                times = self.ai_metrics['timestamps'][-20:]
                tokens = self.ai_metrics['token_usage'][-20:]
                
                if times and tokens:
                    now = time.time()
                    relative_times = [(now - t) for t in reversed(times)]
                    
                    self.token_usage_ax.bar(relative_times, list(reversed(tokens)), 
                                          color='#8b5cf6', alpha=0.7, width=0.8)
                    self.token_usage_ax.set_xlabel('Seconds Ago', color='#e5e5e5', fontsize=9)
                    self.token_usage_ax.set_ylabel('Tokens Used', color='#e5e5e5', fontsize=9)
            
            # Update task types pie chart
            task_types = self.ai_metrics.get('task_types', {})
            if task_types:
                labels = list(task_types.keys())
                sizes = list(task_types.values())
                colors = ['#38bdf8', '#8b5cf6', '#06ffa5', '#f59e0b', '#ef4444', '#10b981', '#f97316']
                
                self.task_types_ax.pie(sizes, labels=labels, colors=colors[:len(labels)], 
                                     autopct='%1.0f%%', startangle=90, textprops={'color': '#e5e5e5', 'fontsize': 8})
            
            # Update system metrics
            try:
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                # Simple bar chart for system metrics
                metrics = ['CPU', 'Memory']
                values = [cpu_percent, memory_percent]
                colors = ['#38bdf8', '#ef4444']
                
                bars = self.system_metrics_ax.bar(metrics, values, color=colors, alpha=0.7)
                self.system_metrics_ax.set_ylabel('Usage %', color='#e5e5e5', fontsize=9)
                self.system_metrics_ax.set_ylim(0, 100)
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    self.system_metrics_ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                                              f'{value:.1f}%', ha='center', va='bottom', 
                                              color='#e5e5e5', fontsize=9)
                        
            except ImportError:
                # Fallback if psutil not available
                self.system_metrics_ax.text(0.5, 0.5, 'System metrics\nrequire psutil', 
                                          ha='center', va='center', transform=self.system_metrics_ax.transAxes,
                                          color='#e5e5e5', fontsize=10)
            
            # Refresh the canvas
            self.dashboard_canvas.draw()
            
        except Exception as e:
            logging.error(f"Error updating dashboard graphs: {e}")
    
    def refresh_dashboard_display(self):
        """Refresh the dashboard display with current metrics"""
        try:
            current_time = time.time()
            
            # Update metric cards if they exist
            if hasattr(self, 'metric_cards') and hasattr(self, 'ai_metrics'):
                for key, label in self.metric_cards.items():
                    try:
                        value = self.ai_metrics.get(key, 0)
                        
                        # Format values appropriately
                        if key in ['avg_response_time', 'avg_task_time']:
                            formatted_value = f"{value:.2f}s" if value > 0 else "0s"
                        elif key == 'total_tokens':
                            # Format large numbers with K/M notation
                            if value >= 1000000:
                                formatted_value = f"{value/1000000:.1f}M"
                            elif value >= 1000:
                                formatted_value = f"{value/1000:.1f}K"
                            else:
                                formatted_value = str(int(value))
                        else:
                            formatted_value = str(int(value))
                        
                        label.setText(formatted_value)
                    except Exception as e:
                        logging.error(f"Error updating metric card {key}: {e}")
            
            # Update status indicator
            if hasattr(self, 'ai_status_label') and hasattr(self, 'ai_metrics'):
                if (self.ai_metrics.get('timestamps') and 
                    current_time - self.ai_metrics['timestamps'][-1] < 10):  # Active within last 10 seconds
                    self.ai_status_label.setText("🟢 ACTIVE")
                    self.ai_status_label.setStyleSheet(f"""
                        QLabel {{
                            color: {ModernTheme.get_colors()['accent']};
                            background: rgba(6, 255, 165, 0.15);
                            border: 2px solid rgba(6, 255, 165, 0.4);
                            border-radius: {ModernTheme.scale_value(12)}px;
                            padding: {ModernTheme.scale_value(8)}px {ModernTheme.scale_value(16)}px;
                            font-weight: 700;
                        }}
                    """)
                else:
                    self.ai_status_label.setText("🟡 IDLE")
                    self.ai_status_label.setStyleSheet(f"""
                        QLabel {{
                            color: #f59e0b;
                            background: rgba(245, 158, 11, 0.15);
                            border: 2px solid rgba(245, 158, 11, 0.4);
                            border-radius: {ModernTheme.scale_value(12)}px;
                            padding: {ModernTheme.scale_value(8)}px {ModernTheme.scale_value(16)}px;
                            font-weight: 700;
                        }}
                    """)
            
            # Update graphs if they exist
            if hasattr(self, 'dashboard_canvas'):
                self.update_dashboard_graphs()
                        
        except Exception as e:
            logging.error(f"Error refreshing dashboard display: {e}")
    
    def update_ai_metrics(self, task_type: str = None, response_time: float = 0, tokens_used: int = 0):
        """Update AI metrics display in real-time"""
        try:
            current_time = time.time()
            
            # Update metrics data
            self.ai_metrics['timestamps'].append(current_time)
            self.ai_metrics['response_times'].append(response_time)
            self.ai_metrics['token_usage'].append(tokens_used)
            
            # Update counters
            self.ai_metrics['task_count'] += 1
            self.ai_metrics['total_tokens'] += tokens_used
            self.ai_metrics['tasks_completed'] += 1
            
            # Track task types
            if task_type:
                self.ai_metrics['task_types'][task_type] = self.ai_metrics['task_types'].get(task_type, 0) + 1
            
            # Calculate averages
            if self.ai_metrics['response_times']:
                self.ai_metrics['avg_response_time'] = sum(self.ai_metrics['response_times']) / len(self.ai_metrics['response_times'])
            
            # Update task execution times
            self.ai_metrics['task_execution_times'].append(response_time)
            if self.ai_metrics['task_execution_times']:
                self.ai_metrics['avg_task_time'] = sum(self.ai_metrics['task_execution_times']) / len(self.ai_metrics['task_execution_times'])
            
            # Keep only recent data (last 100 entries)
            max_entries = 100
            for key in ['timestamps', 'response_times', 'token_usage', 'task_execution_times']:
                if len(self.ai_metrics[key]) > max_entries:
                    self.ai_metrics[key] = self.ai_metrics[key][-max_entries:]
            
            # Update metric cards if they exist
            if hasattr(self, 'metric_cards'):
                for key, label in self.metric_cards.items():
                    try:
                        value = self.ai_metrics.get(key, 0)
                        
                        # Format values appropriately
                        if key in ['avg_response_time', 'avg_task_time']:
                            formatted_value = f"{value:.2f}"
                        elif key == 'total_tokens':
                            # Format large numbers with K/M notation
                            if value >= 1000000:
                                formatted_value = f"{value/1000000:.1f}M"
                            elif value >= 1000:
                                formatted_value = f"{value/1000:.1f}K"
                            else:
                                formatted_value = str(int(value))
                        else:
                            formatted_value = str(int(value))
                        
                        label.setText(formatted_value)
                    except Exception as e:
                        logging.error(f"Error updating metric card {key}: {e}")
            
            # Update status indicator
            if hasattr(self, 'ai_status_label'):
                if current_time - self.ai_metrics['timestamps'][-1] < 5:  # Active within last 5 seconds
                    self.ai_status_label.setText("🟢 ACTIVE")
                    self.ai_status_label.setStyleSheet(f"""
                        QLabel {{
                            color: {ModernTheme.get_colors()['accent']};
                            background: rgba(6, 255, 165, 0.15);
                            border: 2px solid rgba(6, 255, 165, 0.4);
                            border-radius: {ModernTheme.scale_value(12)}px;
                            padding: {ModernTheme.scale_value(8)}px {ModernTheme.scale_value(16)}px;
                            font-weight: 700;
                        }}
                    """)
                else:
                    self.ai_status_label.setText("🟡 IDLE")
                    self.ai_status_label.setStyleSheet(f"""
                        QLabel {{
                            color: #f59e0b;
                            background: rgba(245, 158, 11, 0.15);
                            border: 2px solid rgba(245, 158, 11, 0.4);
                            border-radius: {ModernTheme.scale_value(12)}px;
                            padding: {ModernTheme.scale_value(8)}px {ModernTheme.scale_value(16)}px;
                            font-weight: 700;
                        }}
                    """)
                    
        except Exception as e:
            logging.error(f"Error updating AI metrics: {e}")
    
    def get_ai_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of AI metrics for display"""
        return {
            'total_tasks': self.ai_metrics['tasks_completed'],
            'total_tokens': self.ai_metrics['total_tokens'],
            'avg_response_time': self.ai_metrics['avg_response_time'],
            'avg_task_time': self.ai_metrics['avg_task_time'],
            'task_types': dict(self.ai_metrics['task_types']),
            'last_activity': self.ai_metrics['timestamps'][-1] if self.ai_metrics['timestamps'] else 0
        }
    
    
    
    def setup_accessibility(self):
        """Enhanced accessibility features for better keyboard navigation and screen reader support"""
        try:
            # Set up proper tab order for main interface elements
            if hasattr(self, 'task_input') and hasattr(self, 'attach_btn'):
                self.setTabOrder(self.task_input, self.attach_btn)
            
            if hasattr(self, 'attach_btn') and hasattr(self, 'clear_files_btn'):
                self.setTabOrder(self.attach_btn, self.clear_files_btn)
            
            if hasattr(self, 'task_type_combo') and hasattr(self, 'process_btn'):
                self.setTabOrder(self.task_type_combo, self.process_btn)
            
            # Set accessibility properties for better screen reader support
            if hasattr(self, 'task_input'):
                self.task_input.setAccessibleName("Task Description Input")
                self.task_input.setAccessibleDescription("Enter your task description here. The AI will process your request based on the description and any attached files.")
            
            if hasattr(self, 'attach_btn'):
                self.attach_btn.setAccessibleName("Attach Files Button")
                self.attach_btn.setAccessibleDescription("Click to attach files for processing. Supports images, documents, code files, and CSV data.")
            
            if hasattr(self, 'process_btn'):
                self.process_btn.setAccessibleName("Process Task Button")
                self.process_btn.setAccessibleDescription("Start processing the task with the AI assistant.")
            
            if hasattr(self, 'theme_toggle_btn'):
                self.theme_toggle_btn.setAccessibleName("Theme Toggle Button")
                current_theme = getattr(self, 'current_theme', 'dark')
                target_theme = 'light' if current_theme == 'dark' else 'dark'
                self.theme_toggle_btn.setAccessibleDescription(f"Currently using {current_theme} theme. Click to switch to {target_theme} theme.")
            
            # Set main window accessibility properties
            self.setAccessibleName("SuperMini AI Assistant")
            self.setAccessibleDescription("AI-powered desktop assistant for task automation, multimedia processing, and intelligent document analysis.")
            
            logging.info("Accessibility features initialized successfully")
            
        except Exception as e:
            logging.warning(f"Some accessibility features could not be initialized: {e}")
    
    def setup_monitoring(self):
        self.monitor = SystemMonitor()
        self.monitor.update_signal.connect(self.update_monitor_display)
        self.monitoring_active = False
        
        # Start monitoring automatically
        self.start_monitoring_automatically()
    
    def start_monitoring_automatically(self):
        """Start system monitoring automatically"""
        try:
            self.monitor.start()
            self.monitoring_active = True
            print("✅ System monitoring started automatically")
        except Exception as e:
            print(f"⚠️ Failed to start monitoring automatically: {e}")
    
    def show_welcome_if_needed(self):
        settings = QSettings()
        if not settings.value("welcome_shown", False, type=bool):
            dialog = WelcomeDialog(self)
            dialog.exec()
            settings.setValue("welcome_shown", True)
    

    def process_task(self):
        task_text = self.task_input.toPlainText().strip()
        if not task_text:
            QMessageBox.warning(self, "Warning", "Please enter a task description!")
            return
        
        task_type = None if self.task_type_combo.currentText() == "Auto-detect" else self.task_type_combo.currentText().lower()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_btn.setEnabled(False)
        self.stop_task_btn.setEnabled(True)
        self.statusBar().showMessage(self.get_random_status_message())
        
        # Update neural visualization for AI activity
        if hasattr(self, 'neural_network_widget'):
            self.neural_network_widget.set_activity_level(0.8)
        if hasattr(self, 'ai_status_label'):
            self.ai_status_label.setText(f"🤖 AI: {self.get_random_ai_status()}")
            self.ai_status_label.setStyleSheet(f"""
                color: {ModernTheme.get_colors()['primary']};
                font-weight: 600;
                padding: {ModernTheme.get_spacing('sm')};
            """)
        
        self.results_text.clear()
        # Files and log tabs removed - functionality moved to Activity Monitor
        
        files = getattr(self, 'attached_files', [])
        
        # Store current task information for metadata tracking
        self.current_task_type = task_type
        self.current_prompt = task_text
        
        # Create thread with auto-continue and autonomous settings
        self.task_thread = TaskThread(
            self.processor, 
            task_text, 
            files, 
            task_type, 
            self.use_memory_cb.isChecked(),
            True,  # Auto-continue is now always intelligently managed
            10,    # Max continues will be automatically determined
            self.autonomous_mode_cb.isChecked()  # Add autonomous mode
        )
        
        self.task_thread.progress_signal.connect(self.update_progress)
        self.task_thread.result_signal.connect(self.display_task_result)
        self.task_thread.finished.connect(self.task_finished)
        self.task_thread.start()
    

    def stop_task(self):
        """Stop the current task execution"""
        if self.task_thread and self.task_thread.isRunning():
            self.task_thread.stop()
            # Give thread a moment to stop gracefully
            if not self.task_thread.wait(2000):  # Wait 2 seconds
                self.task_thread.terminate()  # Force terminate if needed
                self.task_thread.wait()  # Wait for termination
            
            self.process_btn.setEnabled(True)
            self.stop_task_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Task stopped")
            
            # Log the stop action
            log_activity(
                ActivityType.USER_INTERACTION,
                ActivityLevel.INFO,
                "Task Stopped by User",
                "User manually stopped task execution",
                {"task_type": "regular_task"}
            )
    

    def task_finished(self):
        """Handle task thread completion"""
        self.process_btn.setEnabled(True)
        self.stop_task_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Task completed")
        
        # Reset neural visualization to idle state
        if hasattr(self, 'neural_network_widget'):
            self.neural_network_widget.set_activity_level(0.2)
        if hasattr(self, 'ai_status_label'):
            self.ai_status_label.setText("🤖 AI: Ready")
            self.ai_status_label.setStyleSheet(f"""
                color: {ModernTheme.get_colors()['text_neural']};
                font-weight: 500;
                padding: {ModernTheme.get_spacing('sm')};
            """)
    
    def on_autonomous_mode_toggled(self, checked):
        """Handle autonomous mode checkbox toggle"""
        try:
            if checked:
                if not AUTONOMOUS_AVAILABLE:
                    QMessageBox.warning(self, "Autonomous Mode", 
                                      "Autonomous capabilities not available. Install gui-agents package:\npip install gui-agents>=0.1.2")
                    self.autonomous_mode_cb.setChecked(False)
                    return
                
                # Enable autonomous mode
                self.show_suggestions_btn.setEnabled(True)
                self.activity_monitor.log_activity("autonomous_mode", "Autonomous mode enabled", {"enabled": True})
            else:
                # Disable autonomous mode
                self.show_suggestions_btn.setEnabled(False)
                self.activity_monitor.log_activity("autonomous_mode", "Autonomous mode disabled", {"enabled": False})
        except Exception as e:
            self.activity_monitor.log_activity("error", f"Error toggling autonomous mode: {str(e)}", {"error": str(e)})
    
    def resizeEvent(self, event):
        """Handle window resize events to update layout dynamically"""
        super().resizeEvent(event)
        logging.info(f"resizeEvent triggered: window width={self.width()}")
        
        # Update splitter sizes based on new window size
        if hasattr(self, 'main_splitter'):
            window_width = self.width()
            window_height = self.height()
            
            control_width = int(window_width * 0.50)
            output_width = window_width - control_width - 10
            self.main_splitter.setSizes([control_width, output_width])
            logging.info(f"resizeEvent: control_width={control_width}, output_width={output_width}")
            self.main_splitter.update()
            self.updateGeometry()
            
            if hasattr(self, 'task_input'):
                min_height = max(120, int(window_height * 0.15))
                max_height = max(200, int(window_height * 0.3))
                self.task_input.setMinimumHeight(ModernTheme.scale_value(min_height))
                self.task_input.setMaximumHeight(ModernTheme.scale_value(max_height))
            
            # Calculate new sizes with consistent breakpoints matching setup_ui
            if window_width < 700:
                # Very small windows: minimal control panel
                control_width = min(200, int(window_width * 0.35))
                output_width = max(400, window_width - control_width - 10)
            elif window_width < 900:
                # Small windows: compact control panel
                control_width = min(250, int(window_width * 0.28))
                output_width = max(500, window_width - control_width - 10)
            elif window_width < 1200:
                # Medium windows: balanced sizing
                control_width = min(300, int(window_width * 0.25))
                output_width = max(600, window_width - control_width - 10)
            else:
                # Large windows: comfortable sizing
                control_width = min(350, int(window_width * 0.22))
                output_width = max(700, window_width - control_width - 10)
            
            # Apply the new sizes
            self.main_splitter.setSizes([control_width, output_width])
            
            # Update task input sizing dynamically
            if hasattr(self, 'task_input'):
                min_height = max(120, int(window_height * 0.15))  # 15% of window height
                max_height = max(200, int(window_height * 0.3))   # 30% of window height
                self.task_input.setMinimumHeight(ModernTheme.scale_value(min_height))
                self.task_input.setMaximumHeight(ModernTheme.scale_value(max_height))
    

    def show_autonomous_suggestions(self):
        """Show autonomous action suggestions for current context"""
        if not AUTONOMOUS_AVAILABLE or not self.processor.autonomous_agent:
            QMessageBox.information(self, "Info", "Autonomous capabilities not available. Install gui-agents package.")
            return
        
        task_text = self.task_input.toPlainText().strip()
        files = getattr(self, 'attached_files', [])
        task_type = None if self.task_type_combo.currentText() == "Auto-detect" else self.task_type_combo.currentText().lower()
        
        try:
            suggestions = self.processor.suggest_autonomous_actions(task_text, files, task_type)
            
            if suggestions:
                suggestions_text = "🤖 **Autonomous Action Suggestions:**\n\n"
                for i, suggestion in enumerate(suggestions, 1):
                    suggestions_text += f"{i}. {suggestion}\n"
                
                suggestions_text += "\n💡 Enable 'Autonomous Mode' to let the AI execute these actions automatically."
                
                # Show suggestions in a dialog
                dialog = QDialog(self)
                dialog.setWindowTitle("Autonomous Suggestions")
                dialog.setGeometry(200, 200, 500, 400)
                
                layout = QVBoxLayout()
                text_browser = QTextBrowser()
                text_browser.setMarkdown(suggestions_text)
                layout.addWidget(text_browser)
                
                close_btn = self.create_button(
                    "Close",
                    "❌",
                    "secondary",
                    "Close dialog",
                    80,
                    dialog.close
                )
                layout.addWidget(close_btn)
                
                dialog.setLayout(layout)
                dialog.exec()
            else:
                QMessageBox.information(self, "Info", "No autonomous suggestions available for current context.")
                
        except Exception as e:
            logging.error(f"Error getting autonomous suggestions: {e}")
            QMessageBox.warning(self, "Error", f"Failed to get suggestions: {str(e)}")
    

    def update_progress(self, value):
        self.progress_bar.setValue(value)
    

    def display_task_result(self, result: TaskResult):
        """Display task result in the results panel with modern formatting"""
        # Update results tab with enhanced HTML formatting
        if result.success:
            result_text = f"""
            <div style='font-family: {ModernTheme.FONTS['ui']}; line-height: 1.6; color: {ModernTheme.get_colors()['text_primary']};'>
                <div style='background: linear-gradient(135deg, {ModernTheme.get_colors()['success']} 0%, #059669 100%); 
                            color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                    <h2 style='margin: 0; font-size: 24px; font-weight: 600;'>✅ Task Completed Successfully</h2>
                    <p style='margin: 8px 0 0 0; opacity: 0.9;'>Execution time: {result.execution_time:.2f} seconds</p>
                </div>
                
                <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 20px; border-radius: 8px; 
                            border-left: 4px solid {ModernTheme.get_colors()['success']}; margin-bottom: 20px;'>
                    <h3 style='color: {ModernTheme.get_colors()['success']}; margin-top: 0;'>🎯 AI Response</h3>
                    <div style='background-color: {ModernTheme.get_colors()['bg_primary']}; padding: 16px; border-radius: 6px; 
                                font-family: {ModernTheme.FONTS['mono']}; font-size: 13px; line-height: 1.5;
                                border: 1px solid {ModernTheme.get_colors()['border']};'>
                        {result.result.replace(chr(10), '<br>').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}
                    </div>
                </div>
            """
        else:
            result_text = f"""
            <div style='font-family: {ModernTheme.FONTS['ui']}; line-height: 1.6; color: {ModernTheme.get_colors()['text_primary']};'>
                <div style='background: linear-gradient(135deg, {ModernTheme.get_colors()['error']} 0%, #dc2626 100%); 
                            color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                    <h2 style='margin: 0; font-size: 24px; font-weight: 600;'>❌ Task Failed</h2>
                    <p style='margin: 8px 0 0 0; opacity: 0.9;'>Execution time: {result.execution_time:.2f} seconds</p>
                </div>
                
                <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 20px; border-radius: 8px; 
                            border-left: 4px solid {ModernTheme.get_colors()['error']}; margin-bottom: 20px;'>
                    <h3 style='color: {ModernTheme.get_colors()['error']}; margin-top: 0;'>⚠️ Error Details</h3>
                    <div style='background-color: {ModernTheme.get_colors()['bg_primary']}; padding: 16px; border-radius: 6px; 
                                font-family: {ModernTheme.FONTS['mono']}; font-size: 13px; line-height: 1.5;
                                border: 1px solid {ModernTheme.get_colors()['border']};'>
                        {result.result.replace(chr(10), '<br>').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}
                    </div>
                </div>
            """
        
        if result.generated_files:
            result_text += f"""
            <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 20px; border-radius: 8px; 
                        border-left: 4px solid {ModernTheme.get_colors()['info']}; margin-bottom: 20px;'>
                <h3 style='color: {ModernTheme.get_colors()['info']}; margin-top: 0;'>📁 Generated Files ({len(result.generated_files)})</h3>
                <ul style='list-style: none; padding: 0;'>
            """
            
            for file_path in result.generated_files:
                file_name = Path(file_path).name if file_path else "Unknown file"
                
                # Check for metadata to enhance display
                metadata = None
                if hasattr(result, 'file_metadata') and result.file_metadata and file_path in result.file_metadata:
                    metadata = result.file_metadata[file_path]
                
                if metadata:
                    # Enhanced display with metadata
                    result_text += f"""
                    <li style='background-color: {ModernTheme.get_colors()['bg_primary']}; padding: 14px; margin: 10px 0; 
                               border-radius: 8px; border: 1px solid {ModernTheme.get_colors()['primary']}; border-left: 4px solid {ModernTheme.get_colors()['primary']};'>
                        <div style='display: flex; align-items: flex-start;'>
                            <div style='margin-right: 12px; font-size: 18px;'>{self._get_metadata_icon(metadata.file_type)}</div>
                            <div style='flex: 1;'>
                                <div style='color: {ModernTheme.get_colors()['text_primary']}; font-weight: 600; font-size: 14px; margin-bottom: 4px;'>{metadata.display_name}</div>
                                <div style='color: {ModernTheme.get_colors()['text_secondary']}; font-size: 12px; margin-bottom: 6px;'>{metadata.description}</div>
                                <div style='display: flex; gap: 12px; margin-bottom: 6px;'>
                                    <span style='color: {ModernTheme.get_colors()['primary']}; font-size: 11px; font-weight: 500;'>{metadata.file_type}</span>
                                    <span style='color: {ModernTheme.get_colors()['text_muted']}; font-size: 11px;'>{Path(file_path).stat().st_size if Path(file_path).exists() else 0} bytes</span>
                                </div>
                                <div style='color: {ModernTheme.get_colors()['info']}; font-size: 11px; background: rgba(59, 130, 246, 0.1); padding: 4px 8px; border-radius: 4px; display: inline-block;'>
                                    🎯 {metadata.purpose}
                                </div>
                                <div style='color: {ModernTheme.get_colors()['text_muted']}; font-size: 10px; font-family: {ModernTheme.FONTS['mono']}; margin-top: 8px; word-break: break-all;'>{file_path}</div>
                            </div>
                        </div>
                    </li>
                    """
                else:
                    # Fallback display without metadata
                    result_text += f"""
                    <li style='background-color: {ModernTheme.get_colors()['bg_primary']}; padding: 12px; margin: 8px 0; 
                               border-radius: 6px; border: 1px solid {ModernTheme.get_colors()['border']};'>
                        <div style='display: flex; align-items: center;'>
                            <span style='margin-right: 8px;'>📄</span>
                            <div>
                                <div style='color: {ModernTheme.get_colors()['text_primary']}; font-weight: 500;'>{file_name}</div>
                                <div style='color: {ModernTheme.get_colors()['text_muted']}; font-size: 11px; font-family: {ModernTheme.FONTS['mono']};'>{file_path}</div>
                            </div>
                        </div>
                    </li>
                    """
            
            result_text += "</ul></div>"
        
        if result.task_steps and len(result.task_steps) > 0:
            result_text += f"""
            <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 20px; border-radius: 8px; 
                        border-left: 4px solid {ModernTheme.get_colors()['warning']}; margin-bottom: 20px;'>
                <h3 style='color: {ModernTheme.get_colors()['warning']}; margin-top: 0;'>📋 Task Steps ({len(result.task_steps)})</h3>
                <ol style='padding-left: 20px; margin: 0;'>
            """
            
            for step in result.task_steps:
                result_text += f"<li style='margin: 8px 0; color: {ModernTheme.get_colors()['text_secondary']};'>{step}</li>"
            
            result_text += "</ol></div>"
        
        if result.audio_path:
            result_text += f"""
            <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 20px; border-radius: 8px; 
                        border-left: 4px solid {ModernTheme.get_colors()['primary']}; margin-bottom: 20px;'>
                <h3 style='color: {ModernTheme.get_colors()['primary']}; margin-top: 0;'>🔊 Audio Output</h3>
                <p style='margin: 0;'><code style='color: {ModernTheme.get_colors()['primary_light']};'>{result.audio_path}</code></p>
            </div>
            """
        
        result_text += "</div>"
        self.results_text.setHtml(result_text)
        
        # Store file metadata for enhanced file display
        if hasattr(result, 'file_metadata') and result.file_metadata:
            if not hasattr(self, 'stored_file_metadata'):
                self.stored_file_metadata = {}
            self.stored_file_metadata.update(result.file_metadata)
        
        # Add task to timeline with enhanced data
        task_data = {
            'task_type': getattr(self, 'current_task_type', 'unknown'),
            'title': self._generate_task_title(result),
            'prompt': getattr(self, 'current_prompt', ''),
            'result': result.result,
            'generated_files': result.generated_files,
            'response_time': result.execution_time,
            'tokens_used': getattr(result, 'tokens_used', 0),
            'timestamp': datetime.now(),
            'file_metadata': getattr(result, 'file_metadata', {})
        }
        self.add_task_to_timeline(task_data)
        
        # Refresh file display to show new files with metadata
        self.refresh_files_display()
        
        # Update files tab if it exists
        if hasattr(self, 'files_text') and result.generated_files:
            self.update_files_display(result.generated_files)
    
    def _generate_task_title(self, result: TaskResult) -> str:
        """Generate a descriptive title for the task based on the result"""
        if hasattr(result, 'file_metadata') and result.file_metadata:
            # Use the first file's display name as the task title
            first_metadata = next(iter(result.file_metadata.values()))
            return first_metadata.display_name
        elif result.generated_files:
            # Fallback to file name
            first_file = Path(result.generated_files[0]).name
            return first_file.replace('_', ' ').title()
        else:
            # Generic title based on task type
            task_type = getattr(self, 'current_task_type', 'unknown')
            return f"{task_type.title()} Task"
    
    def _get_metadata_icon(self, file_type: str) -> str:
        """Get an appropriate icon for the file type from metadata"""
        file_type_lower = file_type.lower()
        
        if file_type_lower == "code":
            return "🐍"  # Python/Code icon
        elif file_type_lower == "script":
            return "📜"  # Script icon
        elif file_type_lower == "data":
            return "📊"  # Data icon
        elif file_type_lower == "text":
            return "📄"  # Text document icon
        elif file_type_lower == "document":
            return "📋"  # Document icon
        else:
            return "📎"  # Generic file icon
        
        # Show error message for failed tasks
        if not result.success:
            QMessageBox.warning(self, "Task Failed", f"Task execution failed. Check the results panel for details.")
    
    def update_files_display(self, file_paths):
        """Update the files tab with generated files information"""
        if not hasattr(self, 'files_text'):
            return
            
        files_text = f"""
        <div style='font-family: {ModernTheme.FONTS['ui']}; color: {ModernTheme.get_colors()['text_primary']};'>
            <div style='background: linear-gradient(135deg, {ModernTheme.get_colors()['info']} 0%, {ModernTheme.get_colors()['primary']} 100%); 
                        color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                <h3 style='margin: 0; font-size: 18px; font-weight: 600;'>📁 Generated Files ({len(file_paths)})</h3>
                <p style='margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;'>Files created by your AI assistant</p>
            </div>
        """
        
        for file_path in file_paths:
            if not file_path:
                continue
                
            try:
                path_obj = Path(file_path)
                file_name = path_obj.name
                file_ext = path_obj.suffix.lower()
                
                # Get file size
                try:
                    size = path_obj.stat().st_size
                    if size < 1024:
                        file_size = f"{size} B"
                    elif size < 1024*1024:
                        file_size = f"{size/1024:.1f} KB"
                    else:
                        file_size = f"{size/(1024*1024):.1f} MB"
                except:
                    file_size = "Unknown size"
                
                # Choose icon based on file extension
                if file_ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
                    icon = "💻"
                elif file_ext in ['.txt', '.md', '.doc', '.docx']:
                    icon = "📄"
                elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                    icon = "🖼️"
                elif file_ext in ['.csv', '.xlsx', '.xls']:
                    icon = "📊"
                elif file_ext in ['.pdf']:
                    icon = "📕"
                else:
                    icon = "📄"
                
                files_text += f"""
                <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 16px; margin: 12px 0; 
                            border-radius: 8px; border: 1px solid {ModernTheme.get_colors()['border']};
'>
                    <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                        <span style='font-size: 24px; margin-right: 12px;'>{icon}</span>
                        <div style='flex: 1;'>
                            <h4 style='margin: 0; color: {ModernTheme.get_colors()['text_primary']}; font-size: 16px;'>{file_name}</h4>
                            <p style='margin: 2px 0 0 0; color: {ModernTheme.get_colors()['text_muted']}; font-size: 12px;'>
                                {file_size} • {file_ext.upper()[1:] if file_ext else 'Unknown'} file
                            </p>
                        </div>
                    </div>
                    <div style='background-color: {ModernTheme.get_colors()['bg_primary']}; padding: 8px; border-radius: 4px;
                                border: 1px solid {ModernTheme.get_colors()['border']};'>
                        <code style='color: {ModernTheme.get_colors()['text_muted']}; font-size: 11px; word-break: break-all;'>{file_path}</code>
                    </div>
                </div>
                """
            except Exception as e:
                # Fallback for invalid paths
                files_text += f"""
                <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 16px; margin: 12px 0; 
                            border-radius: 8px; border: 1px solid {ModernTheme.get_colors()['border']};'>
                    <h4 style='margin: 0 0 8px 0; color: {ModernTheme.get_colors()['text_primary']};'>📄 {file_path}</h4>
                    <p style='margin: 0; color: {ModernTheme.get_colors()['text_muted']}; font-size: 12px;'>File information unavailable</p>
                </div>
                """
        
        files_text += "</div>"
        self.files_text.setHtml(files_text)
    

    def task_finished(self):
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        self.statusBar().showMessage("Task completed")
    

    def start_exploration(self):
        # Get interval in seconds from the spinbox
        interval_seconds = self.explore_interval_spinbox.value()
        if interval_seconds <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Please set a non-zero interval for exploration.")
            return
        
        # Convert seconds to hours and minutes
        hours = interval_seconds // 3600
        minutes = (interval_seconds % 3600) // 60
        
        self.start_explore_btn.setEnabled(False)
        self.stop_explore_btn.setEnabled(True)
        self.exploration_status.setText("🔍 Exploring...")
        files = getattr(self, 'attached_files', [])
        self.explore_thread = ExploreThread(
            self.processor, 
            files, 
            iteration_delay_hours=hours,
            iteration_delay_minutes=minutes
        )
        self.explore_thread.progress_signal.connect(self.update_progress)
        self.explore_thread.result_signal.connect(self.display_explore_result)
        self.explore_thread.error_signal.connect(self.handle_explore_error)
        self.explore_thread.finished.connect(self.exploration_finished)
        self.explore_thread.start()
    

    def stop_exploration(self):
        """Stop the exploration thread and any ongoing operations"""
        if self.explore_thread and self.explore_thread.isRunning():
            self.explore_thread.stop()
            # Give thread a moment to stop gracefully
            if not self.explore_thread.wait(3000):  # Wait 3 seconds
                self.explore_thread.terminate()  # Force terminate if needed
                self.explore_thread.wait()  # Wait for termination
            
            # Update GUI immediately
            self.start_explore_btn.setEnabled(True)
            self.stop_explore_btn.setEnabled(False)
            self.exploration_status.setText("Exploration stopped by user")
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Exploration stopped")
    

    def display_explore_result(self, result: str, files: List[str], iteration: int):
        self.results_text.append(f"\n\n{result}")
        # File generation info now displayed in Activity Monitor
    
    def handle_explore_error(self, error: str):
        self.results_text.append(f"\nError: {error}")
        QMessageBox.warning(self, "Exploration Error", error)
    

    def exploration_finished(self):
        self.start_explore_btn.setEnabled(True)
        self.stop_explore_btn.setEnabled(False)
        self.exploration_status.setText("Exploration stopped")
        self.progress_bar.setVisible(False)
    

    def start_enhancement(self):
        # Get interval in seconds from the spinbox
        interval_seconds = self.enhance_interval_spinbox.value()
        if interval_seconds <= 0:
            QMessageBox.warning(self, "Invalid Interval", "Please set a non-zero interval for enhancement.")
            return
        
        # Convert seconds to hours and minutes
        hours = interval_seconds // 3600
        minutes = (interval_seconds % 3600) // 60
        
        self.start_enhance_btn.setEnabled(False)
        self.stop_enhance_btn.setEnabled(True)
        self.enhancement_status.setText("⚡ Enhancing...")
        files = getattr(self, 'attached_files', [])
        app_path = os.path.abspath(__file__)
        self.enhance_thread = EnhanceThread(
            self.processor, 
            files, 
            app_path, 
            iteration_delay_hours=hours,
            iteration_delay_minutes=minutes
        )
        self.enhance_thread.progress_signal.connect(self.update_progress)
        self.enhance_thread.result_signal.connect(self.display_enhance_result)
        self.enhance_thread.error_signal.connect(self.handle_enhance_error)
        self.enhance_thread.opportunity_signal.connect(self.update_enhancement_status)
        self.enhance_thread.finished.connect(self.enhancement_finished)
        self.enhance_thread.start()
    

    def stop_enhancement(self):
        """Stop the enhancement thread and any ongoing operations"""
        if self.enhance_thread and self.enhance_thread.isRunning():
            self.enhance_thread.stop()
            # Give thread a moment to stop gracefully
            if not self.enhance_thread.wait(3000):  # Wait 3 seconds
                self.enhance_thread.terminate()  # Force terminate if needed
                self.enhance_thread.wait()  # Wait for termination
            
            # Update GUI immediately
            self.start_enhance_btn.setEnabled(True)
            self.stop_enhance_btn.setEnabled(False)
            self.enhancement_status.setText("Enhancement stopped by user")
            self.progress_bar.setVisible(False)
            self.statusBar().showMessage("Enhancement stopped")
    
    def display_enhance_result(self, result: str, files: List[str], iteration: int, version: str):
        self.results_text.append(f"\n\n{result}")
        # File generation info now displayed in Activity Monitor
    
    def handle_enhance_error(self, error: str):
        self.results_text.append(f"\nError: {error}")
        QMessageBox.warning(self, "Enhancement Error", error)
    
    def update_enhancement_status(self, status_message: str):
        """Update enhancement status with detailed information"""
        self.enhancement_status.setText(status_message)
        
        # Log enhancement progress
        log_activity(
            ActivityType.SYSTEM_EVENT,
            ActivityLevel.INFO,
            "Enhancement Progress",
            status_message,
            {"component": "enhancement_engine", "timestamp": time.time()}
        )
    
    def enhancement_finished(self):
        self.start_enhance_btn.setEnabled(True)
        self.stop_enhance_btn.setEnabled(False)
        self.enhancement_status.setText("Enhancement stopped")
        self.progress_bar.setVisible(False)
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.load_config()
            self.setup_processors()
    
    def clear_output(self):
        """Clear all output displays with modern confirmation"""
        reply = QMessageBox.question(
            self, "Clear Output",
            "Are you sure you want to clear all output and results?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear results tab
            if hasattr(self, 'results_text'):
                self.results_text.clear()
                self.results_text.setPlaceholderText("Cleared. AI responses and analysis will appear here...")
            
            # Clear files tab if it exists
            if hasattr(self, 'files_text'):
                self.files_text.clear()
                self.files_text.setPlaceholderText("Cleared. Generated files and their locations will be listed here...")
            
            # Clear system monitor display if it exists
            if hasattr(self, 'monitor_display'):
                self.monitor_display.clear()
                self.monitor_display.setPlaceholderText("Cleared. System monitoring information will appear here...")
            
            self.statusBar().showMessage("✅ All output cleared")
            
            # Log the clear action if activity logging is available
            try:
                log_activity(
                    ActivityType.USER_INTERACTION,
                    ActivityLevel.INFO,
                    "Output Cleared",
                    "User cleared all output displays",
                    {"action": "clear_output"}
                )
            except:
                pass  # Activity logging may not be available
    
    # Monitoring toggle removed - system monitoring is now always active
    
    def update_monitor_display(self, metrics):
        """Update monitor display with modern styling and enhanced information"""
        try:
            # Update simple label for control panel
            cpu_emoji = "🔥" if metrics['cpu'] > 80 else "⚡" if metrics['cpu'] > 50 else "💚"
            mem_emoji = "🔥" if metrics['memory'] > 80 else "⚡" if metrics['memory'] > 50 else "💚"
            
            simple_text = f"{cpu_emoji} CPU: {metrics['cpu']:.1f}% | {mem_emoji} RAM: {metrics['memory']:.1f}%"
            if hasattr(self, 'monitor_label'):
                self.monitor_label.setText(simple_text)
            
            # Update detailed monitor display if it exists
            if hasattr(self, 'monitor_display'):
                # Create rich HTML display for system tab
                monitor_html = f"""
                <div style='font-family: {ModernTheme.FONTS['ui']}; color: {ModernTheme.get_colors()['text_primary']};'>
                    <div style='background: linear-gradient(135deg, {ModernTheme.get_colors()['primary']} 0%, {ModernTheme.get_colors()['primary_dark']} 100%); 
                                color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;'>
                        <h3 style='margin: 0; font-size: 18px; font-weight: 600;'>💻 System Performance</h3>
                        <p style='margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;'>Real-time system metrics</p>
                    </div>
                    
                    <div style='display: grid; gap: 12px;'>
                        <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 16px; border-radius: 8px; 
                                    border-left: 4px solid {self._get_metric_color(metrics['cpu'])};'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h4 style='margin: 0; color: {ModernTheme.get_colors()['text_primary']};'>🔥 CPU Usage</h4>
                                    <p style='margin: 2px 0 0 0; color: {ModernTheme.get_colors()['text_muted']}; font-size: 12px;'>Processor utilization</p>
                                </div>
                                <div style='text-align: right;'>
                                    <div style='font-size: 24px; font-weight: 600; color: {self._get_metric_color(metrics['cpu'])};'>{metrics['cpu']:.1f}%</div>
                                </div>
                            </div>
                        </div>
                        
                        <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 16px; border-radius: 8px; 
                                    border-left: 4px solid {self._get_metric_color(metrics['memory'])};'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h4 style='margin: 0; color: {ModernTheme.get_colors()['text_primary']};'>🧠 Memory Usage</h4>
                                    <p style='margin: 2px 0 0 0; color: {ModernTheme.get_colors()['text_muted']}; font-size: 12px;'>RAM utilization</p>
                                </div>
                                <div style='text-align: right;'>
                                    <div style='font-size: 24px; font-weight: 600; color: {self._get_metric_color(metrics['memory'])};'>{metrics['memory']:.1f}%</div>
                                </div>
                            </div>
                        </div>
                        
                        <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 16px; border-radius: 8px; 
                                    border-left: 4px solid {self._get_metric_color(metrics.get('disk', 0))};'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h4 style='margin: 0; color: {ModernTheme.get_colors()['text_primary']};'>💾 Disk Usage</h4>
                                    <p style='margin: 2px 0 0 0; color: {ModernTheme.get_colors()['text_muted']}; font-size: 12px;'>Storage utilization</p>
                                </div>
                                <div style='text-align: right;'>
                                    <div style='font-size: 24px; font-weight: 600; color: {self._get_metric_color(metrics.get('disk', 0))};'>{metrics.get('disk', 0):.1f}%</div>
                                </div>
                            </div>
                        </div>
                        
                        <div style='background-color: {ModernTheme.get_colors()['bg_secondary']}; padding: 16px; border-radius: 8px; 
                                    border-left: 4px solid {ModernTheme.get_colors()['info']};'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <h4 style='margin: 0; color: {ModernTheme.get_colors()['text_primary']};'>⏰ Last Updated</h4>
                                    <p style='margin: 2px 0 0 0; color: {ModernTheme.get_colors()['text_muted']}; font-size: 12px;'>System metrics timestamp</p>
                                </div>
                                <div style='text-align: right;'>
                                    <div style='font-size: 14px; color: {ModernTheme.get_colors()['info']};'>{metrics.get('timestamp', 'Unknown')}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
                self.monitor_display.setHtml(monitor_html)
        
        except Exception as e:
            # Fallback to simple text display
            if hasattr(self, 'monitor_label'):
                self.monitor_label.setText(f"Monitoring active (Error: {e})")
    
    def _get_metric_color(self, value):
        """Get color based on metric value"""
        try:
            if value > 80:
                return ModernTheme.get_colors()['error']
            elif value > 60:
                return ModernTheme.get_colors()['warning']
            else:
                return ModernTheme.get_colors()['success']
        except:
            return ModernTheme.get_colors()['text_muted']

def main():
    # PyQt6 Note: High DPI scaling is enabled by default
    # The following attributes were removed in PyQt6:
    # - AA_EnableHighDpiScaling (always enabled)
    # - AA_UseHighDpiPixmaps (always enabled)
    # No additional attributes need to be set for proper High DPI support
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Initialize DPI-aware scaling system
    ModernTheme.initialize_scaling(app)
    
    window = SuperMiniMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()