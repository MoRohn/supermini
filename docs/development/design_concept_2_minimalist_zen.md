# Design Concept 2: "Minimalist Zen Garden"
*Ultra-clean interface focusing on content and workflow*

## Visual Mockup Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ◉ ◯ ◯  SuperMini                                               ⚙️ ❓    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                             SuperMini AI                               │
│                        Your thoughtful AI companion                     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  What would you like me to help you with today?                    │ │
│  │                                                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────┐   │ │
│  │  │ Type your request here...                                   │   │ │
│  │  │                                                             │   │ │
│  │  │ • Create a Python script to analyze CSV data               │   │ │
│  │  │ • Summarize the attached research papers                    │   │ │
│  │  │ • Build an automation workflow for file management         │   │ │
│  │  └─────────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │  📎 Attach files     🎯 Auto-detect     ⚙️ Advanced                │ │
│  │                                                                     │ │
│  │                            ⟨ Execute ⟩                             │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│                                                                         │
│  ┌─ Response ──────────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  I'll help you create a Python script for CSV data analysis.       │ │
│  │                                                                     │ │
│  │  Based on your requirements, I'll generate:                        │ │
│  │  • Data loading and validation functions                            │ │
│  │  • Statistical analysis and visualization                           │ │
│  │  • Clean, documented code with error handling                      │ │
│  │                                                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────┐   │ │
│  │  │ ```python                                                   │   │ │
│  │  │ import pandas as pd                                         │   │ │
│  │  │ import matplotlib.pyplot as plt                             │   │ │
│  │  │                                                             │   │ │
│  │  │ def analyze_csv_data(file_path):                            │   │ │
│  │  │     """Load and analyze CSV data with comprehensive         │   │ │
│  │  │     statistical insights and visualizations."""             │   │ │
│  │  │     ...                                                     │   │ │
│  │  │ ```                                                         │   │ │
│  │  └─────────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │  📄 data_analyzer.py    📊 visualization_report.html               │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│                                                                         │
│  ┌─ Quick Actions ────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  🧭 Explore Mode        ⚡ Enhance AI        📊 View Metrics       │  │
│  │  Let AI discover        Improve capabilities   System performance    │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│                                                                         │
│                           AI Status: Ready • Memory: Active             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Design Elements

### 🎨 Color Implementation
- **Background**: Pure white (#ffffff) with subtle warm gray (#f8f9fa)
- **Primary**: Sophisticated purple (#6366f1) following AI trends
- **Text**: Deep charcoal (#1f2937) with strategic lighter grays
- **Accents**: Soft blue (#3b82f6) for interactive elements

### 🔤 Typography Hierarchy
- **Headers**: SF Pro Display, 32px, regular weight
- **Subheaders**: SF Pro Display, 18px, medium weight
- **Body text**: SF Pro Text, 16px, regular, 1.6 line height
- **Code**: SF Mono, 14px, with syntax highlighting
- **Captions**: SF Pro Text, 14px, secondary color

### 📐 Spacing & Layout
- **Generous margins**: 48px on desktop, 24px on smaller screens
- **Component spacing**: 32px between major sections
- **Content padding**: 24px internal padding for cards
- **Button spacing**: 16px between related actions
- **Micro-spacing**: 8px for related elements

### 🎯 Interactive Elements
- **Input focus**: Soft purple glow with smooth transition
- **Button states**: Subtle scale (1.02x) on hover
- **Card elevation**: Gentle shadow increase on interaction
- **Progress**: Animated progress bar with soft curves

### 🏗️ Layout Structure
- **Single column**: Focused attention with maximum 800px width
- **Card system**: Content organized in clean, elevated cards
- **Progressive disclosure**: Advanced options hidden by default
- **Contextual sidebar**: Appears only when needed
- **Floating actions**: Primary actions accessible via elegant positioning

### 💫 Animations
- **Breathing**: Gentle scale animation for active elements
- **Fade transitions**: 300ms ease-in-out for state changes
- **Slide reveals**: Content slides in from bottom when appearing
- **Micro-interactions**: Subtle feedback for all user actions

## Implementation Strategy

### PyQt6 Layout System
```python
class ZenMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text';
            }
        """)
        
        # Central widget with generous margins
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(32)
        
        # Create main content card
        self.main_card = self.create_main_card()
        layout.addWidget(self.main_card)
        
        central.setLayout(layout)
        self.setCentralWidget(central)

class ZenCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #f1f5f9;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            QFrame:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        """)
```

### CSS Theme System
```css
/* Primary input field */
QTextEdit {
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    font-size: 16px;
    background-color: #ffffff;
    selection-background-color: #6366f1;
}

QTextEdit:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

/* Primary button */
QPushButton[variant="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    font-weight: 600;
    font-size: 16px;
}

QPushButton[variant="primary"]:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
}
```

### Accessibility Features
- **High contrast**: 4.5:1 minimum ratio for all text
- **Focus indicators**: Clear visual focus for keyboard navigation
- **Screen reader support**: Proper ARIA labels and structure
- **Touch targets**: Minimum 44px for all interactive elements
- **Reduced motion**: Respect system preferences for animations

### Progressive Enhancement
- **Base experience**: Fully functional without animations
- **Enhanced interactions**: Smooth animations for capable devices
- **Responsive text**: Font size scaling based on system preferences
- **Dark mode ready**: Color variables for easy theme switching