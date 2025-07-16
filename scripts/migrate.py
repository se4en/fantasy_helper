#!/usr/bin/env python3
"""
Database migration script for development and production
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    
    cwd = str(project_root)    
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    
    # Print both stdout and stderr for debugging                                                                                                                                                                                                                                                                             
    if result.stdout:                                                                                                                                                                                                                                                                                                        
        print(f"STDOUT: {result.stdout}")                                                                                                                                                                                                                                                                                    
    if result.stderr:                                                                                                                                                                                                                                                                                                        
        print(f"STDERR: {result.stderr}")

    if result.returncode != 0:                                                                                                                                                                                                                                                                                               
        print(f"Error: {description} failed with return code {result.returncode}")                                                                                                                                                                                                                                           
        sys.exit(1)
    
    print(f"Success: {description}")                                                                                                                                                                                                                                                                                         
    print("-" * 50)                                                                                                                                                                                                                                                                                                          
    return result


def main():
    """Main migration function"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/migrate.py [generate|upgrade|downgrade|current|history] [args...]")
        print("Examples:")
        print("  python scripts/migrate.py generate 'Add new table'")
        print("  python scripts/migrate.py upgrade")
        print("  python scripts/migrate.py upgrade head")
        print("  python scripts/migrate.py downgrade -1")
        print("  python scripts/migrate.py current")
        print("  python scripts/migrate.py history")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "generate":
        if len(sys.argv) < 3:
            print("Error: Migration message required for generate")
            sys.exit(1)
        message = sys.argv[2]
        run_command(
            ["alembic", "revision", "--autogenerate", "-m", message],
            f"Generating migration: {message}"
        )
    
    elif action == "upgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        run_command(
            ["alembic", "upgrade", target],
            f"Upgrading database to {target}"
        )
    
    elif action == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        run_command(
            ["alembic", "downgrade", target],
            f"Downgrading database to {target}"
        )
    
    elif action == "current":
        run_command(
            ["alembic", "current"],
            "Showing current migration"
        )
    
    elif action == "history":
        run_command(
            ["alembic", "history"],
            "Showing migration history"
        )
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
