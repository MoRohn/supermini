"""
Release Integration for SuperMini
Integrates automated release management with the existing SuperMini application
"""

import logging
import os
from pathlib import Path
from typing import Optional

try:
    from src.integration.release_automation import ReleaseManager, integrate_with_enhancement_system
    RELEASE_AUTOMATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Release automation not available: {e}")
    RELEASE_AUTOMATION_AVAILABLE = False
    ReleaseManager = None
    integrate_with_enhancement_system = None

class SuperMiniReleaseIntegration:
    """Integrates release automation with SuperMini's existing architecture"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.release_manager: Optional[ReleaseManager] = None
        self._integration_active = False
        
    def initialize_release_system(self):
        """Initialize the release management system"""
        if not RELEASE_AUTOMATION_AVAILABLE:
            logging.info("Release automation not available - skipping initialization")
            return False
            
        try:
            # Get repository path (assuming it's the current directory or parent)
            repo_path = Path.cwd()
            if not (repo_path / '.git').exists():
                # Check parent directory
                repo_path = repo_path.parent
                if not (repo_path / '.git').exists():
                    logging.warning("Git repository not found, release automation disabled")
                    return False
            
            # Get GitHub token from environment or config
            github_token = self._get_github_token()
            
            # Create release manager
            self.release_manager = ReleaseManager(repo_path, github_token)
            
            # Configure release settings
            self._configure_release_settings()
            
            # Integrate with enhancement system if available
            self._integrate_with_enhancement_system()
            
            self._integration_active = True
            logging.info("Release automation system initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize release system: {e}")
            return False
    
    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment or configuration"""
        # Try environment variable first
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
        
        # Try SuperMini config if available
        if hasattr(self.app, 'config') and hasattr(self.app.config, 'github_token'):
            return getattr(self.app.config, 'github_token', None)
        
        # Could also check for stored credentials file
        credentials_file = Path.home() / '.supermini' / 'github_token'
        if credentials_file.exists():
            try:
                with open(credentials_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        return None
    
    def _configure_release_settings(self):
        """Configure release manager settings"""
        if not self.release_manager:
            return
        
        # Configure auto-approval based on user preferences
        self.release_manager.configure_auto_approval(
            patch=True,   # Auto-approve patch releases (safe)
            minor=False,  # Require approval for minor releases
            major=False   # Always require approval for major releases
        )
        
        # Set enhancement threshold - trigger release after N enhancements
        self.release_manager.enhancement_threshold = 3
    
    def _integrate_with_enhancement_system(self):
        """Integrate with SuperMini's existing enhancement system"""
        if not self.release_manager:
            return
        
        # Look for autonomous enhancement components
        enhancement_loop = self._find_enhancement_loop()
        
        if enhancement_loop:
            integrate_with_enhancement_system(enhancement_loop, self.release_manager)
            logging.info("Release automation integrated with enhancement system")
        else:
            # Set up manual integration hooks
            self._setup_manual_integration_hooks()
    
    def _find_enhancement_loop(self):
        """Find the autonomous enhancement loop in the application"""
        # Check if app has enhancement-related attributes
        if hasattr(self.app, 'autonomous_enhancement'):
            return self.app.autonomous_enhancement
        
        if hasattr(self.app, 'enhancement_loop'):
            return self.app.enhancement_loop
        
        # Check processor for enhancement capabilities
        if hasattr(self.app, 'processor'):
            processor = self.app.processor
            if hasattr(processor, 'enhancement_system'):
                return processor.enhancement_system
            if hasattr(processor, 'autonomous_enhancement'):
                return processor.autonomous_enhancement
        
        return None
    
    def _setup_manual_integration_hooks(self):
        """Set up manual hooks for release integration"""
        # This would be used if automatic integration fails
        # We can patch existing methods to notify the release manager
        pass
    
    def on_enhancement_completed(self, enhancement_data: dict):
        """Called when an enhancement is completed (manual hook)"""
        if self.release_manager and self._integration_active:
            self.release_manager.on_enhancement_completed(enhancement_data)
    
    def get_pending_releases(self):
        """Get pending releases for UI display"""
        if self.release_manager:
            return self.release_manager.get_pending_releases()
        return []
    
    def approve_release(self, version: str) -> bool:
        """Approve a pending release"""
        if self.release_manager:
            return self.release_manager.approve_pending_release(version)
        return False
    
    def reject_release(self, version: str) -> bool:
        """Reject a pending release"""
        if self.release_manager:
            return self.release_manager.reject_pending_release(version)
        return False
    
    def is_active(self) -> bool:
        """Check if release integration is active"""
        return self._integration_active
    
    def get_current_version(self) -> str:
        """Get current version"""
        if self.release_manager:
            return self.release_manager.get_current_version()
        return "unknown"


# Monkey patch to add release integration to SuperMini
def add_release_integration_to_supermini():
    """Add release integration to existing SuperMini classes"""
    
    # This function can be called to patch the existing SuperMini application
    # It adds release functionality without modifying the original code
    
    def enhanced_setup_processors(self):
        """Enhanced version of setup_processors that includes release integration"""
        # Call original setup
        original_setup_processors(self)
        
        # Add release integration
        if not hasattr(self, 'release_integration'):
            self.release_integration = SuperMiniReleaseIntegration(self)
            success = self.release_integration.initialize_release_system()
            
            if success:
                logging.info("Release automation added to SuperMini")
            else:
                logging.info("Release automation unavailable (no git repo or config)")
    
    # Store original method and replace it
    try:
        from supermini import SuperMiniMainWindow
        original_setup_processors = SuperMiniMainWindow.setup_processors
        SuperMiniMainWindow.setup_processors = enhanced_setup_processors
        
        logging.info("SuperMini enhanced with release automation")
        
    except ImportError:
        logging.error("Could not import SuperMiniMainWindow for release integration")


# UI Integration Components
def create_release_status_widget(parent, release_integration):
    """Create a widget to show release status"""
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
    from PyQt6.QtCore import QTimer
    
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Status label
    status_label = QLabel("Release Status: Ready")
    layout.addWidget(status_label)
    
    # Pending releases area
    pending_area = QWidget()
    pending_layout = QVBoxLayout()
    pending_area.setLayout(pending_layout)
    layout.addWidget(pending_area)
    
    def update_release_status():
        """Update the release status display"""
        if not release_integration.is_active():
            status_label.setText("Release Status: Disabled")
            return
        
        pending_releases = release_integration.get_pending_releases()
        
        if pending_releases:
            status_label.setText(f"Release Status: {len(pending_releases)} Pending")
            
            # Clear previous pending items
            for i in reversed(range(pending_layout.count())): 
                pending_layout.itemAt(i).widget().setParent(None)
            
            # Add pending release items
            for release in pending_releases:
                item_widget = QWidget()
                item_layout = QHBoxLayout()
                
                info_label = QLabel(f"v{release.version} ({release.type})")
                approve_btn = QPushButton("Approve")
                reject_btn = QPushButton("Reject")
                
                approve_btn.clicked.connect(
                    lambda checked, v=release.version: release_integration.approve_release(v)
                )
                reject_btn.clicked.connect(
                    lambda checked, v=release.version: release_integration.reject_release(v)
                )
                
                item_layout.addWidget(info_label)
                item_layout.addWidget(approve_btn)
                item_layout.addWidget(reject_btn)
                item_widget.setLayout(item_layout)
                
                pending_layout.addWidget(item_widget)
        else:
            status_label.setText("Release Status: Ready")
            # Clear pending area
            for i in reversed(range(pending_layout.count())): 
                pending_layout.itemAt(i).widget().setParent(None)
    
    # Update timer
    timer = QTimer()
    timer.timeout.connect(update_release_status)
    timer.start(5000)  # Update every 5 seconds
    
    # Initial update
    update_release_status()
    
    widget.setLayout(layout)
    return widget


# Example integration for existing SuperMini
def integrate_release_automation():
    """Main function to integrate release automation with SuperMini"""
    try:
        # Add the integration to SuperMini
        add_release_integration_to_supermini()
        
        logging.info("Release automation integration completed")
        return True
        
    except Exception as e:
        logging.error(f"Failed to integrate release automation: {e}")
        return False


if __name__ == "__main__":
    # Test integration
    integrate_release_automation()