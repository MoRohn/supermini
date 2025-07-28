# Repository Reorganization Plan

## Current State Analysis

The SuperMini repository currently has:
- **Root directory clutter**: 30+ Python files mixed with documentation and configuration
- **Inconsistent naming**: Multiple launcher/builder scripts with similar functionality
- **Scattered components**: Related files spread across root directory
- **Good structure exists**: Already has organized directories for assets/, docs/, scripts/, tests/

## Proposed Structure

```
supermini/
├── README.md                    # Main documentation (keep)
├── LICENSE                      # License file (keep)
├── CHANGELOG.md                 # Version history (keep)
├── CONTRIBUTING.md              # Contribution guidelines (keep)
├── requirements.txt             # Python dependencies (keep)
├── setup.py                     # Package setup (keep)
├── .gitignore                   # Git ignore rules (keep)
├── VERSION                      # Version file (keep)
├── supermini.py                 # Main entry point (keep)
├── .claude/                     # Claude AI configuration (keep)
│   └── tasks/
├── assets/                      # UI assets and icons (keep as is)
├── docs/                        # Documentation (reorganize)
│   ├── guides/                  # Move user guides here
│   │   ├── BUILD_GUIDE.md
│   │   ├── EASY_LAUNCH_GUIDE.md
│   │   └── GITHUB_SETUP_INSTRUCTIONS.md
│   └── development/             # Development docs (keep as is)
├── scripts/                     # Build and launch scripts (consolidate)
├── src/                         # Source code (NEW)
│   ├── __init__.py
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── task_processor.py   # Main task processing
│   │   ├── memory_manager.py   # Memory management
│   │   └── activity_monitor.py
│   ├── autonomous/              # Autonomous agent components
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── enhancement.py
│   │   ├── orchestrator.py
│   │   └── intelligence.py
│   ├── ui/                      # UI components
│   │   ├── __init__.py
│   │   └── launcher.py
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── safety_framework.py
│   │   ├── recursive_engine.py
│   │   └── planning_components.py
│   └── integration/             # Release and integration
│       ├── __init__.py
│       ├── release_automation.py
│       └── release_integration.py
├── tests/                       # Test files (keep as is)
├── prompts/                     # AI prompts (keep as is)
├── dependencies/                # Dependency management (keep as is)
├── tools/                       # Development tools (keep as is)
└── build/                       # Build artifacts (git ignored)
```

## Reorganization Steps

### Phase 1: Create Directory Structure
1. Create src/ directory with subdirectories
2. Create __init__.py files for Python packages

### Phase 2: Move Core Components
1. Move activity_monitor.py → src/core/
2. Move enhanced_memory.py → src/core/memory_manager.py
3. Move enhanced_task_execution.py → src/core/task_processor.py

### Phase 3: Move Autonomous Components
1. Move autonomous_agent.py → src/autonomous/agent.py
2. Move autonomous_enhancement.py → src/autonomous/enhancement.py
3. Move autonomous_orchestrator.py → src/autonomous/orchestrator.py
4. Move task_intelligence.py → src/autonomous/intelligence.py

### Phase 4: Move Utilities
1. Move safety framework files → src/utils/
2. Move recursive_engine.py → src/utils/
3. Move dynamic_planning_components.py → src/utils/planning_components.py

### Phase 5: Move UI Components
1. Consolidate launcher files into src/ui/launcher.py
2. Remove duplicate launcher scripts

### Phase 6: Reorganize Documentation
1. Create docs/guides/ directory
2. Move user-facing guides to docs/guides/

### Phase 7: Clean Up Scripts
1. Remove duplicate build scripts
2. Keep only essential scripts in scripts/

### Phase 8: Update Imports
1. Update all import statements in moved files
2. Update supermini.py to import from new locations
3. Test application functionality

### Phase 9: Remove Redundant Files
1. Delete duplicate launcher files
2. Remove unnecessary temporary files
3. Clean up any obsolete scripts

## Files to Remove
- SuperMini_Launcher.py (duplicate of launcher.py)
- launcher.py (consolidate into src/ui/launcher.py)
- Multiple create_*.py scripts (consolidate in scripts/)
- icon_dev.py (appears to be development utility)

## Import Updates Required
- All files importing moved modules need path updates
- Main supermini.py needs to import from src/
- Test files may need import adjustments

## Testing Plan
1. Run supermini.py after each phase
2. Verify all imports work correctly
3. Test autonomous features
4. Run any existing tests
5. Ensure build scripts still function

## Rollback Plan
- Git status shows modified files - can revert if needed
- Create backup branch before major changes
- Test incrementally to catch issues early