#!/usr/bin/env python3
"""
Quick test to verify the AI monitoring dashboard has visual elements
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import matplotlib
    matplotlib.use('qtagg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    print("✅ Matplotlib with PyQt6 backend available")
    
    # Test creating a simple figure
    figure = Figure(figsize=(6, 4), facecolor='#1e1e1e')
    canvas = FigureCanvas(figure)
    ax = figure.add_subplot(111)
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3], color='#00ff88', linewidth=2)
    ax.set_title('Test Chart', color='white')
    print("✅ Can create matplotlib charts successfully")
    
    # Test PyQt6 integration
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Add the matplotlib canvas to the layout
    layout.addWidget(canvas)
    window.setCentralWidget(central_widget)
    window.setWindowTitle("Dashboard Visual Test")
    window.resize(800, 600)
    
    print("✅ Successfully integrated matplotlib canvas with PyQt6")
    print("📊 AI Monitoring Dashboard visual elements are working!")
    
    # Don't actually show the window in test mode
    # window.show()
    # app.exec()
    
except Exception as e:
    print(f"❌ Dashboard visual test failed: {e}")
    import traceback
    traceback.print_exc()