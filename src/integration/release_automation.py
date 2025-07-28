"""
Release Automation Module for SuperMini
Integrates with the 'Enhance Yourself' mode to provide automated release management
"""

import json
import logging
import subprocess
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import semantic_version
import requests
from threading import Lock

@dataclass
class ReleaseInfo:
    """Information about a release"""
    version: str
    type: str  # 'major', 'minor', 'patch'
    changes: List[str]
    enhancements: List[str]
    timestamp: float
    commit_hash: str
    approval_status: str  # 'pending', 'approved', 'rejected'
    created_by: str = "autonomous_enhancement"

@dataclass
class VersionBump:
    """Version bump information"""
    current_version: str
    new_version: str
    bump_type: str
    changelog_entries: List[str]
    
class ReleaseType(Enum):
    """Types of releases"""
    PATCH = "patch"      # Bug fixes, small improvements
    MINOR = "minor"      # New features, enhancements
    MAJOR = "major"      # Breaking changes, major refactors

class ReleaseManager:
    """Manages automated releases integrated with autonomous enhancement"""
    
    def __init__(self, repo_path: Path, github_token: Optional[str] = None):
        self.repo_path = repo_path
        self.github_token = github_token
        self.release_lock = Lock()
        
        # Paths
        self.version_file = repo_path / "VERSION"
        self.changelog_file = repo_path / "CHANGELOG.md"
        self.package_json = repo_path / "package.json"  # Alternative version source
        
        # State
        self.pending_releases = []
        self.release_history = []
        self.auto_approve_minor = False  # Whether to auto-approve minor releases
        self.auto_approve_patch = True   # Whether to auto-approve patch releases
        
        # Enhancement integration
        self.enhancement_threshold = 3   # Number of enhancements to trigger release
        self.accumulated_enhancements = []
        
        logging.info("Release Manager initialized")
    
    def get_current_version(self) -> str:
        """Get current version from version file or git tags"""
        try:
            # Try version file first
            if self.version_file.exists():
                with open(self.version_file, 'r') as f:
                    return f.read().strip()
            
            # Fall back to git tags
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().lstrip('v')
            
            # Default version if none found
            return "2.0.0"
            
        except Exception as e:
            logging.warning(f"Could not determine current version: {e}")
            return "2.0.0"
    
    def determine_version_bump(self, enhancements: List[Dict[str, Any]]) -> ReleaseType:
        """Determine what type of version bump is needed based on enhancements"""
        has_breaking_changes = False
        has_new_features = False
        has_bug_fixes = False
        
        for enhancement in enhancements:
            enhancement_type = enhancement.get('type', '').lower()
            description = enhancement.get('description', '').lower()
            
            # Check for breaking changes
            if ('breaking' in description or 
                'major' in enhancement_type or
                'api change' in description):
                has_breaking_changes = True
            
            # Check for new features
            elif ('feature' in enhancement_type or 
                  'enhancement' in enhancement_type or
                  'new' in description):
                has_new_features = True
            
            # Everything else is considered bug fixes/improvements
            else:
                has_bug_fixes = True
        
        # Determine bump type
        if has_breaking_changes:
            return ReleaseType.MAJOR
        elif has_new_features:
            return ReleaseType.MINOR
        else:
            return ReleaseType.PATCH
    
    def calculate_new_version(self, current_version: str, bump_type: ReleaseType) -> str:
        """Calculate new version based on current version and bump type"""
        try:
            version = semantic_version.Version(current_version)
            
            if bump_type == ReleaseType.MAJOR:
                new_version = version.next_major()
            elif bump_type == ReleaseType.MINOR:
                new_version = version.next_minor()
            else:  # PATCH
                new_version = version.next_patch()
            
            return str(new_version)
            
        except Exception as e:
            logging.error(f"Error calculating new version: {e}")
            # Fallback manual calculation
            parts = current_version.split('.')
            if len(parts) != 3:
                return "2.0.1"
            
            major, minor, patch = map(int, parts)
            
            if bump_type == ReleaseType.MAJOR:
                return f"{major + 1}.0.0"
            elif bump_type == ReleaseType.MINOR:
                return f"{major}.{minor + 1}.0"
            else:
                return f"{major}.{minor}.{patch + 1}"
    
    def on_enhancement_completed(self, enhancement_result: Dict[str, Any]):
        """Called when an autonomous enhancement is completed"""
        with self.release_lock:
            self.accumulated_enhancements.append({
                'id': enhancement_result.get('enhancement_id', 'unknown'),
                'type': enhancement_result.get('enhancement_type', 'improvement'),
                'description': enhancement_result.get('description', 'Code enhancement'),
                'timestamp': time.time(),
                'success': enhancement_result.get('success', False)
            })
            
            logging.info(f"Enhancement completed: {enhancement_result.get('enhancement_id')}")
            
            # Check if we should trigger a release
            successful_enhancements = [e for e in self.accumulated_enhancements if e.get('success', False)]
            
            if len(successful_enhancements) >= self.enhancement_threshold:
                self._trigger_release_process()
    
    def _trigger_release_process(self):
        """Trigger the release process based on accumulated enhancements"""
        try:
            current_version = self.get_current_version()
            bump_type = self.determine_version_bump(self.accumulated_enhancements)
            new_version = self.calculate_new_version(current_version, bump_type)
            
            # Create release info
            release_info = ReleaseInfo(
                version=new_version,
                type=bump_type.value,
                changes=[e['description'] for e in self.accumulated_enhancements],
                enhancements=[e['id'] for e in self.accumulated_enhancements],
                timestamp=time.time(),
                commit_hash=self._get_current_commit_hash(),
                approval_status='pending'
            )
            
            # Determine if auto-approval is appropriate
            should_auto_approve = (
                (bump_type == ReleaseType.PATCH and self.auto_approve_patch) or
                (bump_type == ReleaseType.MINOR and self.auto_approve_minor)
            )
            
            if should_auto_approve:
                release_info.approval_status = 'approved'
                self._execute_release(release_info)
            else:
                # Add to pending releases for manual approval
                self.pending_releases.append(release_info)
                self._request_release_approval(release_info)
            
            # Clear accumulated enhancements
            self.accumulated_enhancements = []
            
        except Exception as e:
            logging.error(f"Error triggering release process: {e}")
    
    def _request_release_approval(self, release_info: ReleaseInfo):
        """Request approval for a release (could integrate with UI or notifications)"""
        logging.info(f"Release approval requested for version {release_info.version}")
        logging.info(f"Type: {release_info.type}")
        logging.info(f"Changes: {len(release_info.changes)} enhancements")
        
        # In a GUI application, this could trigger a dialog
        # For now, we'll log the request and mark for manual review
        
        # Save pending release to file for review
        pending_file = self.repo_path / "pending_release.json"
        with open(pending_file, 'w') as f:
            json.dump(asdict(release_info), f, indent=2)
        
        logging.info(f"Pending release saved to {pending_file}")
    
    def approve_pending_release(self, version: str) -> bool:
        """Approve a pending release"""
        for release in self.pending_releases:
            if release.version == version:
                release.approval_status = 'approved'
                self._execute_release(release)
                self.pending_releases.remove(release)
                return True
        return False
    
    def reject_pending_release(self, version: str) -> bool:
        """Reject a pending release"""
        for release in self.pending_releases:
            if release.version == version:
                release.approval_status = 'rejected'
                self.pending_releases.remove(release)
                return True
        return False
    
    def _execute_release(self, release_info: ReleaseInfo):
        """Execute the actual release process"""
        try:
            logging.info(f"Executing release {release_info.version}")
            
            # 1. Update version file
            self._update_version_file(release_info.version)
            
            # 2. Update CHANGELOG.md
            self._update_changelog(release_info)
            
            # 3. Commit changes
            commit_hash = self._commit_release_changes(release_info)
            
            # 4. Create git tag
            self._create_git_tag(release_info.version)
            
            # 5. Push to remote (if configured)
            if self._is_git_remote_configured():
                self._push_to_remote(release_info.version)
            
            # 6. Create GitHub release (if token available)
            if self.github_token:
                self._create_github_release(release_info)
            
            # Update release info with final commit hash
            release_info.commit_hash = commit_hash
            self.release_history.append(release_info)
            
            logging.info(f"Release {release_info.version} completed successfully")
            
        except Exception as e:
            logging.error(f"Error executing release {release_info.version}: {e}")
            raise
    
    def _update_version_file(self, version: str):
        """Update the version file"""
        with open(self.version_file, 'w') as f:
            f.write(version)
        logging.info(f"Updated version file to {version}")
    
    def _update_changelog(self, release_info: ReleaseInfo):
        """Update CHANGELOG.md with release information"""
        if not self.changelog_file.exists():
            # Create new changelog
            changelog_content = """# Changelog

All notable changes to SuperMini will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
        else:
            with open(self.changelog_file, 'r') as f:
                changelog_content = f.read()
        
        # Create new release entry
        date_str = datetime.now().strftime('%Y-%m-%d')
        new_entry = f"""## [{release_info.version}] - {date_str}

### Enhanced
{chr(10).join(f"- {change}" for change in release_info.changes)}

"""
        
        # Insert after "## [Unreleased]" section
        unreleased_pattern = r'(## \[Unreleased\].*?\n\n)'
        if re.search(unreleased_pattern, changelog_content, re.DOTALL):
            changelog_content = re.sub(
                unreleased_pattern,
                f'\\1{new_entry}',
                changelog_content,
                flags=re.DOTALL
            )
        else:
            # If no unreleased section, add at the top after header
            lines = changelog_content.split('\n')
            insert_index = 7  # After standard header
            lines.insert(insert_index, new_entry.strip())
            changelog_content = '\n'.join(lines)
        
        with open(self.changelog_file, 'w') as f:
            f.write(changelog_content)
        
        logging.info(f"Updated CHANGELOG.md for version {release_info.version}")
    
    def _commit_release_changes(self, release_info: ReleaseInfo) -> str:
        """Commit release changes to git"""
        try:
            # Add version file and changelog
            subprocess.run(['git', 'add', str(self.version_file)], cwd=self.repo_path, check=True)
            subprocess.run(['git', 'add', str(self.changelog_file)], cwd=self.repo_path, check=True)
            
            # Commit with release message
            commit_message = f"""Release version {release_info.version}

Automated release generated by SuperMini Enhancement System

Changes:
{chr(10).join(f"- {change}" for change in release_info.changes[:5])}

🤖 Generated with SuperMini Auto-Release
Co-Authored-By: SuperMini Enhancement System <noreply@supermini.ai>"""
            
            subprocess.run([
                'git', 'commit', '-m', commit_message
            ], cwd=self.repo_path, check=True)
            
            # Get commit hash
            result = subprocess.run([
                'git', 'rev-parse', 'HEAD'
            ], cwd=self.repo_path, capture_output=True, text=True, check=True)
            
            commit_hash = result.stdout.strip()
            logging.info(f"Committed release changes: {commit_hash}")
            return commit_hash
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error committing release changes: {e}")
            raise
    
    def _create_git_tag(self, version: str):
        """Create git tag for release"""
        try:
            tag_name = f"v{version}"
            subprocess.run([
                'git', 'tag', '-a', tag_name, '-m', f"Release {version}"
            ], cwd=self.repo_path, check=True)
            
            logging.info(f"Created git tag: {tag_name}")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating git tag: {e}")
            raise
    
    def _is_git_remote_configured(self) -> bool:
        """Check if git remote is configured"""
        try:
            result = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            return result.returncode == 0 and result.stdout.strip()
            
        except Exception:
            return False
    
    def _push_to_remote(self, version: str):
        """Push release to remote repository"""
        try:
            # Push commits
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=self.repo_path, check=True)
            
            # Push tags
            subprocess.run(['git', 'push', 'origin', f"v{version}"], cwd=self.repo_path, check=True)
            
            logging.info(f"Pushed release {version} to remote")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error pushing to remote: {e}")
            raise
    
    def _create_github_release(self, release_info: ReleaseInfo):
        """Create GitHub release using API"""
        if not self.github_token:
            return
        
        try:
            # Get repository info from git remote
            result = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return
            
            remote_url = result.stdout.strip()
            
            # Parse GitHub repo from URL
            if 'github.com' not in remote_url:
                return
            
            # Extract owner/repo from URL
            if remote_url.startswith('git@github.com:'):
                repo_path = remote_url.replace('git@github.com:', '').replace('.git', '')
            elif 'github.com/' in remote_url:
                repo_path = remote_url.split('github.com/')[-1].replace('.git', '')
            else:
                return
            
            owner, repo = repo_path.split('/')
            
            # Create release
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            
            release_data = {
                "tag_name": f"v{release_info.version}",
                "target_commitish": "main",
                "name": f"SuperMini v{release_info.version}",
                "body": self._generate_release_notes(release_info),
                "draft": False,
                "prerelease": "alpha" in release_info.version or "beta" in release_info.version
            }
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            response = requests.post(api_url, json=release_data, headers=headers)
            
            if response.status_code == 201:
                logging.info(f"Created GitHub release for {release_info.version}")
            else:
                logging.error(f"Failed to create GitHub release: {response.status_code} - {response.text}")
            
        except Exception as e:
            logging.error(f"Error creating GitHub release: {e}")
    
    def _generate_release_notes(self, release_info: ReleaseInfo) -> str:
        """Generate release notes for GitHub release"""
        notes = f"""## SuperMini v{release_info.version}

### Autonomous Enhancements

This release was automatically generated by SuperMini's autonomous enhancement system after detecting and implementing {len(release_info.changes)} improvements.

### Changes

"""
        
        for change in release_info.changes:
            notes += f"- {change}\n"
        
        notes += f"""

### Technical Details

- **Release Type**: {release_info.type.title()}
- **Generated**: {datetime.fromtimestamp(release_info.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
- **Enhancement IDs**: {', '.join(release_info.enhancements)}

### Installation

Download the appropriate package for your platform and follow the installation instructions in the README.

🤖 **This release was automatically generated by SuperMini's autonomous enhancement system.**
"""
        
        return notes
    
    def _get_current_commit_hash(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run([
                'git', 'rev-parse', 'HEAD'
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            
        except Exception:
            pass
        
        return "unknown"
    
    def get_pending_releases(self) -> List[ReleaseInfo]:
        """Get list of pending releases"""
        return self.pending_releases.copy()
    
    def get_release_history(self) -> List[ReleaseInfo]:
        """Get release history"""
        return self.release_history.copy()
    
    def configure_auto_approval(self, patch: bool = True, minor: bool = False, major: bool = False):
        """Configure which release types should be auto-approved"""
        self.auto_approve_patch = patch
        self.auto_approve_minor = minor
        # Major releases should rarely be auto-approved
        if major:
            logging.warning("Auto-approval of major releases is not recommended")


# Integration helper functions
def integrate_with_enhancement_system(enhancement_loop, release_manager: ReleaseManager):
    """Integrate release manager with autonomous enhancement system"""
    
    # Store original apply_enhancement method
    original_apply = enhancement_loop.modifier.apply_enhancement
    
    def enhanced_apply_enhancement(enhancement):
        """Enhanced apply method that triggers release process"""
        result = original_apply(enhancement)
        
        # Notify release manager of completion
        if result.success:
            release_manager.on_enhancement_completed({
                'enhancement_id': enhancement.enhancement_id,
                'enhancement_type': enhancement.enhancement_type,
                'description': enhancement.description,
                'success': result.success,
                'timestamp': result.timestamp
            })
        
        return result
    
    # Replace the method
    enhancement_loop.modifier.apply_enhancement = enhanced_apply_enhancement
    
    logging.info("Release automation integrated with enhancement system")


# Example usage in main application
def setup_release_automation(repo_path: Path, github_token: Optional[str] = None) -> ReleaseManager:
    """Set up release automation for SuperMini"""
    
    # Create release manager
    release_manager = ReleaseManager(repo_path, github_token)
    
    # Configure sensible defaults
    release_manager.configure_auto_approval(
        patch=True,   # Auto-approve patch releases (bug fixes)
        minor=False,  # Require approval for minor releases (new features)
        major=False   # Always require approval for major releases
    )
    
    # Set enhancement threshold
    release_manager.enhancement_threshold = 5  # Trigger release after 5 enhancements
    
    return release_manager