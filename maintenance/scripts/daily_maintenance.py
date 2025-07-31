#!/usr/bin/env python3
"""
Clara Daily Maintenance Script

Executes Clara's daily maintenance routine with systematic checks and logging.
This script embodies Clara's methodical approach to preventive maintenance.

Author: Clara Maintenance Agent
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from maintenance.clara_maintenance_engine import ClaraMaintenanceEngine, AlertSeverity


def main():
    """Execute Clara's daily maintenance routine"""
    print(f"Clara Daily Maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Initialize Clara
        clara = ClaraMaintenanceEngine()
        clara.logger.info("Starting daily maintenance routine...")
        
        # Execute daily maintenance
        incidents = clara.run_daily_maintenance()
        
        # Report results
        if incidents:
            print(f"\n📋 Daily Maintenance Summary:")
            print(f"   Total incidents found: {len(incidents)}")
            
            # Group by severity
            critical = [i for i in incidents if i.severity == AlertSeverity.CRITICAL.value]
            warnings = [i for i in incidents if i.severity == AlertSeverity.WARNING.value]
            info = [i for i in incidents if i.severity == AlertSeverity.INFO.value]
            
            if critical:
                print(f"   🚨 Critical: {len(critical)}")
                for incident in critical:
                    print(f"      - {incident.description}")
            
            if warnings:
                print(f"   ⚠️  Warnings: {len(warnings)}")
                for incident in warnings:
                    print(f"      - {incident.description}")
            
            if info:
                print(f"   ℹ️  Info: {len(info)}")
                for incident in info:
                    print(f"      - {incident.description}")
        else:
            print("\n✅ Daily Maintenance Complete: No incidents found. System healthy.")
        
        # Additional daily checks
        print("\n🔍 Additional Daily Checks:")
        
        # Check core files
        core_files_status = check_core_files()
        print(f"   Core files: {'✅ All present' if core_files_status else '❌ Missing files'}")
        
        # Check disk space
        disk_status = check_disk_space()
        print(f"   Disk space: {disk_status}")
        
        # Check log files
        log_status = check_log_files()
        print(f"   Log files: {log_status}")
        
        # Check dependencies
        deps_status = check_dependencies()
        print(f"   Dependencies: {deps_status}")
        
        print("\n" + "=" * 60)
        print("Clara's Daily Maintenance Complete")
        print(f"Next daily maintenance: Tomorrow at 09:00")
        
        # Exit with appropriate code
        if critical:
            print("\n⚠️  ATTENTION: Critical incidents require immediate review!")
            sys.exit(2)  # Critical issues found
        elif warnings:
            print("\n📝 Note: Warning-level incidents logged for review.")
            sys.exit(1)  # Warnings found
        else:
            sys.exit(0)  # All good
            
    except Exception as e:
        print(f"\n❌ Error during daily maintenance: {e}")
        print("Clara will attempt recovery on next scheduled run.")
        sys.exit(3)  # Maintenance error


def check_core_files() -> bool:
    """Check if all core files are present"""
    core_files = [
        "core/degiro_api.py",
        "core/database.py",
        "core/portfolio_service.py",
        "core/config.py",
        "core/logging_config.py",
        "core/models.py"
    ]
    
    missing_files = []
    for file_path in core_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"      Missing: {', '.join(missing_files)}")
        return False
    
    return True


def check_disk_space() -> str:
    """Check disk space usage"""
    try:
        import psutil
        disk = psutil.disk_usage('/')
        usage_percent = (disk.used / disk.total) * 100
        
        if usage_percent >= 90:
            return f"❌ Critical ({usage_percent:.1f}% used)"
        elif usage_percent >= 85:
            return f"⚠️  Warning ({usage_percent:.1f}% used)"
        else:
            return f"✅ Good ({usage_percent:.1f}% used)"
    except Exception as e:
        return f"❌ Error checking disk: {e}"


def check_log_files() -> str:
    """Check log file status"""
    try:
        log_dirs = [project_root / "logs", project_root / "maintenance" / "logs"]
        total_size = 0
        file_count = 0
        
        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.glob("*.log*"):
                    total_size += log_file.stat().st_size
                    file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        
        if size_mb > 500:
            return f"⚠️  Large ({file_count} files, {size_mb:.1f}MB)"
        else:
            return f"✅ Normal ({file_count} files, {size_mb:.1f}MB)"
    except Exception as e:
        return f"❌ Error checking logs: {e}"


def check_dependencies() -> str:
    """Check if key dependencies are available"""
    try:
        # Check key imports
        import requests
        import pandas
        import psutil
        import schedule
        
        # Check if requirements.txt exists
        req_file = project_root / "requirements.txt"
        if not req_file.exists():
            return "⚠️  requirements.txt missing"
        
        return "✅ Key dependencies available"
    except ImportError as e:
        return f"❌ Missing dependency: {e}"
    except Exception as e:
        return f"❌ Error checking dependencies: {e}"


if __name__ == "__main__":
    main()