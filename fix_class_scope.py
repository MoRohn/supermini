#!/usr/bin/env python3
"""
Script to fix the SuperMini class scope issue by moving orphaned methods
back into the SuperMiniMainWindow class.
"""
import re

def fix_class_scope():
    """Fix the class scope issue by moving orphaned methods back to the correct class."""
    
    with open('/Users/rohnspringfield/supermini/supermini.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find the end of SuperMiniMainWindow class (line 9166)
    class_end_line = 9165  # 0-indexed (line 9166 - 1)
    
    # Find the start of ModernNeuralDashboard class (line 9167)
    neural_dashboard_start = 9166  # 0-indexed (line 9167 - 1)
    
    # Extract the orphaned methods (lines 10927-11450 approximately)
    # These are the methods that should be in SuperMiniMainWindow
    orphaned_methods_start = 10926  # 0-indexed (line 10927 - 1)
    orphaned_methods_end = 11600   # Safe end point
    
    # Extract the orphaned methods
    orphaned_methods = []
    current_method = []
    in_method = False
    
    for i in range(orphaned_methods_start, min(orphaned_methods_end, len(lines))):
        line = lines[i]
        
        # Check if this is a method definition that should be in the class
        if line.strip().startswith('def ') and line.startswith('    '):
            method_name = line.strip().split('(')[0].replace('def ', '')
            critical_methods = [
                'process_task', 'stop_task', 'task_finished', 'start_exploration', 
                'stop_exploration', 'start_enhancement', 'stop_enhancement', 
                'show_autonomous_suggestions', 'display_task_result', 
                'display_explore_result', 'exploration_finished', 'update_progress'
            ]
            
            if method_name in critical_methods:
                if current_method:
                    orphaned_methods.append('\n'.join(current_method))
                current_method = [line]
                in_method = True
                continue
        
        # If we're in a method, continue collecting lines
        if in_method:
            # Check if this line starts a new function or class at top level
            if line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                # We've hit the end of the method
                orphaned_methods.append('\n'.join(current_method))
                current_method = []
                in_method = False
            else:
                current_method.append(line)
    
    # Add the last method if we were in one
    if current_method:
        orphaned_methods.append('\n'.join(current_method))
    
    print(f"Found {len(orphaned_methods)} orphaned methods to move")
    
    # Now reconstruct the file
    new_lines = []
    
    # Add everything up to the end of SuperMiniMainWindow class
    new_lines.extend(lines[:class_end_line + 1])
    
    # Add the orphaned methods to the end of SuperMiniMainWindow class
    for method in orphaned_methods:
        new_lines.append('')  # Add blank line before method
        new_lines.extend(method.split('\n'))
    
    # Add everything from ModernNeuralDashboard onwards, skipping the orphaned methods
    # Skip the orphaned methods section
    skip_start = orphaned_methods_start
    skip_end = orphaned_methods_end
    
    # Find where to resume (after main() function)
    for i in range(skip_start, len(lines)):
        if lines[i].strip().startswith('def main():'):
            # Include main() and everything after
            new_lines.extend(lines[i:])
            break
        elif lines[i].strip().startswith('if __name__ == "__main__":'):
            # Include the if __name__ == "__main__": block
            new_lines.extend(lines[i:])
            break
    
    # Write the fixed content
    with open('/Users/rohnspringfield/supermini/supermini_fixed.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("Fixed file written to supermini_fixed.py")
    print("Please review the changes before replacing the original file.")

if __name__ == "__main__":
    fix_class_scope()