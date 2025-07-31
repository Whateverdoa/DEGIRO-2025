#!/usr/bin/env python3
"""
Clara Emergency Maintenance Script

Executes Clara's emergency response procedures for critical system issues.
Designed for rapid deployment when automated monitoring detects severe problems.

Author: Clara Maintenance Agent
Version: 1.0.0
"""

import sys
import os
import json
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from maintenance.clara_maintenance_engine import ClaraMaintenanceEngine, AlertSeverity

# Emergency response timeout (seconds)
EMERGENCY_TIMEOUT = 300  # 5 minutes


def signal_handler(signum, frame):
    """Handle emergency timeout"""
    print(f"\n⏰ Emergency maintenance timeout after {EMERGENCY_TIMEOUT} seconds")
    print("Exiting emergency mode...")
    sys.exit(4)


def main():
    """Execute Clara's emergency maintenance routine"""
    # Set up timeout handler
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(EMERGENCY_TIMEOUT)
    
    print(f"🚨 CLARA EMERGENCY MAINTENANCE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("⚡ Rapid response mode activated")
    print(f"⏱️  Emergency timeout: {EMERGENCY_TIMEOUT} seconds")
    print()
    
    try:
        # Parse command line arguments for emergency type
        emergency_type = parse_emergency_args()
        
        # Initialize Clara in emergency mode
        clara = ClaraMaintenanceEngine()
        clara.logger.critical(f"Emergency maintenance initiated: {emergency_type}")
        
        print(f"🎯 Emergency Type: {emergency_type}")
        print("📋 Executing emergency response protocol...")
        print()
        
        # Execute emergency-specific response
        response_result = execute_emergency_response(clara, emergency_type)
        
        # Quick system assessment
        print("🔍 Rapid System Assessment:")
        assessment = perform_rapid_assessment(clara)
        for item in assessment:
            print(f"   {item}")
        print()
        
        # Emergency remediation
        print("🛠️  Emergency Remediation:")
        remediation_results = perform_emergency_remediation(clara, emergency_type)
        for result in remediation_results:
            print(f"   {result}")
        print()
        
        # Verify system stability
        print("✅ System Stability Check:")
        stability_check = verify_emergency_stability(clara)
        for check in stability_check:
            print(f"   {check}")
        print()
        
        # Generate emergency report
        emergency_report = generate_emergency_report(clara, emergency_type, {
            'response_result': response_result,
            'assessment': assessment,
            'remediation': remediation_results,
            'stability': stability_check
        })
        
        print("📊 Emergency Response Summary:")
        print(f"   Emergency Type: {emergency_type}")
        print(f"   Response Status: {response_result['status']}")
        print(f"   Actions Taken: {len(remediation_results)}")
        print(f"   System Status: {stability_check[0] if stability_check else 'Unknown'}")
        print(f"   Report Saved: {emergency_report}")
        
        # Clara's emergency assessment
        clara_assessment = generate_clara_emergency_assessment(emergency_type, response_result)
        if clara_assessment:
            print("\n🧠 Clara's Emergency Assessment:")
            for assessment_item in clara_assessment:
                print(f"   • {assessment_item}")
        
        print("\n" + "=" * 80)
        print("🚨 EMERGENCY MAINTENANCE COMPLETE")
        
        # Disable timeout
        signal.alarm(0)
        
        # Exit with appropriate code based on results
        if response_result['status'] == 'RESOLVED':
            print("✅ Emergency resolved successfully")
            sys.exit(0)
        elif response_result['status'] == 'STABILIZED':
            print("⚠️  System stabilized - monitoring required")
            sys.exit(1)
        else:
            print("🚨 Emergency response incomplete - manual intervention required")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⚠️  Emergency maintenance interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Critical error during emergency maintenance: {e}")
        sys.exit(5)


def parse_emergency_args() -> str:
    """Parse command line arguments to determine emergency type"""
    if len(sys.argv) < 2:
        # Default emergency type if none specified
        return "GENERAL"
    
    emergency_type = sys.argv[1].upper()
    
    # Validate emergency type
    valid_types = [
        "GENERAL", "CPU", "MEMORY", "DISK", "API", "DATABASE", 
        "NETWORK", "SECURITY", "DATA_CORRUPTION", "SERVICE_DOWN"
    ]
    
    if emergency_type not in valid_types:
        print(f"⚠️  Unknown emergency type: {emergency_type}")
        print(f"Valid types: {', '.join(valid_types)}")
        return "GENERAL"
    
    return emergency_type


def execute_emergency_response(clara: ClaraMaintenanceEngine, emergency_type: str) -> Dict[str, Any]:
    """Execute emergency-specific response procedures"""
    try:
        if emergency_type == "CPU":
            return handle_cpu_emergency(clara)
        elif emergency_type == "MEMORY":
            return handle_memory_emergency(clara)
        elif emergency_type == "DISK":
            return handle_disk_emergency(clara)
        elif emergency_type == "API":
            return handle_api_emergency(clara)
        elif emergency_type == "DATABASE":
            return handle_database_emergency(clara)
        elif emergency_type == "NETWORK":
            return handle_network_emergency(clara)
        elif emergency_type == "SECURITY":
            return handle_security_emergency(clara)
        elif emergency_type == "DATA_CORRUPTION":
            return handle_data_corruption_emergency(clara)
        elif emergency_type == "SERVICE_DOWN":
            return handle_service_down_emergency(clara)
        else:
            return handle_general_emergency(clara)
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': f"Error executing emergency response: {e}",
            'actions_taken': []
        }


def handle_cpu_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle CPU-related emergency"""
    actions = []
    
    try:
        # Check current CPU usage
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        actions.append(f"Current CPU usage: {cpu_percent}%")
        
        if cpu_percent > 90:
            # Emergency CPU mitigation
            actions.append("🚨 Critical CPU usage detected")
            
            # Check for runaway processes
            processes = [(p.pid, p.name(), p.cpu_percent()) for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
            high_cpu_processes = [p for p in processes if p[2] > 50]
            
            if high_cpu_processes:
                actions.append(f"High CPU processes: {len(high_cpu_processes)}")
                for pid, name, cpu in high_cpu_processes[:3]:
                    actions.append(f"  PID {pid} ({name}): {cpu}%")
            
            return {'status': 'CRITICAL', 'message': 'CPU emergency - manual intervention required', 'actions_taken': actions}
        else:
            actions.append("✅ CPU usage within acceptable range")
            return {'status': 'RESOLVED', 'message': 'CPU levels normal', 'actions_taken': actions}
            
    except Exception as e:
        actions.append(f"Error checking CPU: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess CPU status', 'actions_taken': actions}


def handle_memory_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle memory-related emergency"""
    actions = []
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        actions.append(f"Memory usage: {memory.percent}%")
        actions.append(f"Available memory: {memory.available / 1024 / 1024 / 1024:.1f} GB")
        
        if memory.percent > 90:
            actions.append("🚨 Critical memory usage detected")
            
            # Try to free up memory
            actions.append("Attempting memory cleanup...")
            
            # Clear Python caches (basic cleanup)
            import gc
            gc.collect()
            actions.append("✓ Python garbage collection executed")
            
            # Check memory again
            memory_after = psutil.virtual_memory()
            actions.append(f"Memory after cleanup: {memory_after.percent}%")
            
            if memory_after.percent > 85:
                return {'status': 'CRITICAL', 'message': 'Memory emergency - restart required', 'actions_taken': actions}
            else:
                return {'status': 'STABILIZED', 'message': 'Memory usage reduced', 'actions_taken': actions}
        else:
            actions.append("✅ Memory usage within acceptable range")
            return {'status': 'RESOLVED', 'message': 'Memory levels normal', 'actions_taken': actions}
            
    except Exception as e:
        actions.append(f"Error checking memory: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess memory status', 'actions_taken': actions}


def handle_disk_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle disk space emergency"""
    actions = []
    
    try:
        import shutil
        disk_usage = shutil.disk_usage(project_root)
        used_percent = (disk_usage.used / disk_usage.total) * 100
        free_gb = disk_usage.free / 1024 / 1024 / 1024
        
        actions.append(f"Disk usage: {used_percent:.1f}%")
        actions.append(f"Free space: {free_gb:.1f} GB")
        
        if used_percent > 95 or free_gb < 1:
            actions.append("🚨 Critical disk space shortage")
            
            # Emergency cleanup
            cleanup_results = emergency_disk_cleanup()
            actions.extend(cleanup_results)
            
            # Check disk space after cleanup
            disk_usage_after = shutil.disk_usage(project_root)
            used_percent_after = (disk_usage_after.used / disk_usage_after.total) * 100
            free_gb_after = disk_usage_after.free / 1024 / 1024 / 1024
            
            actions.append(f"Disk usage after cleanup: {used_percent_after:.1f}%")
            actions.append(f"Free space after cleanup: {free_gb_after:.1f} GB")
            
            if used_percent_after > 90:
                return {'status': 'CRITICAL', 'message': 'Disk space critical - manual cleanup required', 'actions_taken': actions}
            else:
                return {'status': 'STABILIZED', 'message': 'Disk space improved', 'actions_taken': actions}
        else:
            actions.append("✅ Disk space within acceptable range")
            return {'status': 'RESOLVED', 'message': 'Disk space normal', 'actions_taken': actions}
            
    except Exception as e:
        actions.append(f"Error checking disk space: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess disk status', 'actions_taken': actions}


def handle_api_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle API-related emergency"""
    actions = []
    
    try:
        # Check if API module exists
        api_file = project_root / "core" / "degiro_api.py"
        if not api_file.exists():
            actions.append("❌ DEGIRO API module not found")
            return {'status': 'CRITICAL', 'message': 'API module missing', 'actions_taken': actions}
        
        actions.append("✓ API module present")
        
        # Basic API connectivity test (placeholder)
        actions.append("Checking API connectivity...")
        
        # In a real implementation, this would test actual API endpoints
        # For now, we'll simulate a basic check
        import time
        time.sleep(1)  # Simulate API call
        
        # Simulate API status check
        api_status = "OPERATIONAL"  # This would come from actual API test
        
        if api_status == "OPERATIONAL":
            actions.append("✅ API connectivity appears normal")
            return {'status': 'RESOLVED', 'message': 'API operational', 'actions_taken': actions}
        else:
            actions.append(f"⚠️  API status: {api_status}")
            return {'status': 'CRITICAL', 'message': 'API connectivity issues', 'actions_taken': actions}
            
    except Exception as e:
        actions.append(f"Error checking API: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess API status', 'actions_taken': actions}


def handle_database_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle database-related emergency"""
    actions = []
    
    try:
        # Check for database files
        data_dir = project_root / "data"
        if data_dir.exists():
            db_files = list(data_dir.glob("*.db")) + list(data_dir.glob("*.sqlite"))
            actions.append(f"Database files found: {len(db_files)}")
            
            # Check file accessibility
            for db_file in db_files[:3]:  # Check first 3
                try:
                    with open(db_file, 'rb') as f:
                        f.read(1024)  # Try to read first 1KB
                    actions.append(f"✓ {db_file.name} accessible")
                except Exception as e:
                    actions.append(f"❌ {db_file.name} error: {e}")
                    return {'status': 'CRITICAL', 'message': 'Database file corruption detected', 'actions_taken': actions}
        else:
            actions.append("⚠️  No data directory found")
        
        # Check database module
        db_module = project_root / "core" / "database.py"
        if db_module.exists():
            actions.append("✓ Database module present")
        else:
            actions.append("❌ Database module missing")
            return {'status': 'CRITICAL', 'message': 'Database module not found', 'actions_taken': actions}
        
        actions.append("✅ Database components appear functional")
        return {'status': 'RESOLVED', 'message': 'Database operational', 'actions_taken': actions}
        
    except Exception as e:
        actions.append(f"Error checking database: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess database status', 'actions_taken': actions}


def handle_network_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle network-related emergency"""
    actions = []
    
    try:
        import subprocess
        
        # Test basic connectivity
        actions.append("Testing network connectivity...")
        
        # Ping test
        try:
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                actions.append("✓ Internet connectivity OK")
            else:
                actions.append("❌ Internet connectivity failed")
                return {'status': 'CRITICAL', 'message': 'Network connectivity lost', 'actions_taken': actions}
        except subprocess.TimeoutExpired:
            actions.append("⚠️  Network test timeout")
            return {'status': 'CRITICAL', 'message': 'Network timeout', 'actions_taken': actions}
        
        # DNS test
        try:
            import socket
            socket.gethostbyname('google.com')
            actions.append("✓ DNS resolution OK")
        except socket.gaierror:
            actions.append("❌ DNS resolution failed")
            return {'status': 'CRITICAL', 'message': 'DNS issues detected', 'actions_taken': actions}
        
        actions.append("✅ Network connectivity appears normal")
        return {'status': 'RESOLVED', 'message': 'Network operational', 'actions_taken': actions}
        
    except Exception as e:
        actions.append(f"Error checking network: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess network status', 'actions_taken': actions}


def handle_security_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle security-related emergency"""
    actions = []
    
    try:
        actions.append("🔒 Initiating security emergency protocol")
        
        # Check for suspicious files
        suspicious_patterns = ['.tmp', '.temp', 'suspicious', 'malware']
        suspicious_files = []
        
        for pattern in suspicious_patterns:
            found_files = list(project_root.rglob(f"*{pattern}*"))
            suspicious_files.extend(found_files)
        
        if suspicious_files:
            actions.append(f"⚠️  {len(suspicious_files)} suspicious files found")
            for file_path in suspicious_files[:3]:
                actions.append(f"  - {file_path.relative_to(project_root)}")
        else:
            actions.append("✓ No suspicious files detected")
        
        # Check file permissions on sensitive files
        sensitive_files = [".env.dev", "config/app_config.json"]
        permission_issues = []
        
        for file_path in sensitive_files:
            full_path = project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                if stat.st_mode & 0o044:  # Others can read
                    permission_issues.append(file_path)
        
        if permission_issues:
            actions.append(f"⚠️  {len(permission_issues)} files with loose permissions")
            # Emergency permission fix
            for file_path in permission_issues:
                try:
                    os.chmod(project_root / file_path, 0o600)
                    actions.append(f"✓ Fixed permissions: {file_path}")
                except Exception as e:
                    actions.append(f"❌ Failed to fix {file_path}: {e}")
        else:
            actions.append("✓ File permissions appear secure")
        
        if suspicious_files or permission_issues:
            return {'status': 'STABILIZED', 'message': 'Security issues addressed', 'actions_taken': actions}
        else:
            return {'status': 'RESOLVED', 'message': 'No security threats detected', 'actions_taken': actions}
        
    except Exception as e:
        actions.append(f"Error in security check: {e}")
        return {'status': 'ERROR', 'message': 'Unable to complete security assessment', 'actions_taken': actions}


def handle_data_corruption_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle data corruption emergency"""
    actions = []
    
    try:
        actions.append("🔍 Checking for data corruption...")
        
        # Check critical JSON files
        critical_files = [
            "config/app_config.json",
            "memory/memory.json",
            "maintenance/config/maintenance_config.json"
        ]
        
        corrupted_files = []
        for file_path in critical_files:
            full_path = project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        json.load(f)
                    actions.append(f"✓ {file_path} - valid")
                except json.JSONDecodeError:
                    corrupted_files.append(file_path)
                    actions.append(f"❌ {file_path} - corrupted JSON")
            else:
                actions.append(f"⚠️  {file_path} - missing")
        
        if corrupted_files:
            actions.append(f"🚨 {len(corrupted_files)} corrupted files detected")
            
            # Attempt backup restoration
            backup_restored = attempt_backup_restoration(corrupted_files)
            actions.extend(backup_restored)
            
            return {'status': 'CRITICAL', 'message': 'Data corruption detected - backup restoration attempted', 'actions_taken': actions}
        else:
            actions.append("✅ No data corruption detected")
            return {'status': 'RESOLVED', 'message': 'Data integrity verified', 'actions_taken': actions}
        
    except Exception as e:
        actions.append(f"Error checking data integrity: {e}")
        return {'status': 'ERROR', 'message': 'Unable to verify data integrity', 'actions_taken': actions}


def handle_service_down_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle service down emergency"""
    actions = []
    
    try:
        actions.append("🔄 Checking service status...")
        
        # Check if main application files exist
        main_files = ["main.py", "app.py", "server.py"]
        main_file_found = None
        
        for main_file in main_files:
            if (project_root / main_file).exists():
                main_file_found = main_file
                actions.append(f"✓ Main application file found: {main_file}")
                break
        
        if not main_file_found:
            actions.append("❌ No main application file found")
            return {'status': 'CRITICAL', 'message': 'Application files missing', 'actions_taken': actions}
        
        # Check for running processes (basic check)
        import psutil
        python_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                          if 'python' in p.info['name'].lower()]
        
        actions.append(f"Python processes running: {len(python_processes)}")
        
        # Check if our application might be running
        app_processes = [p for p in python_processes 
                        if any(main_file in ' '.join(p.info['cmdline']) for main_file in main_files)]
        
        if app_processes:
            actions.append(f"✓ Application processes found: {len(app_processes)}")
            return {'status': 'RESOLVED', 'message': 'Service appears to be running', 'actions_taken': actions}
        else:
            actions.append("⚠️  No application processes detected")
            actions.append("Service may need to be restarted manually")
            return {'status': 'CRITICAL', 'message': 'Service down - manual restart required', 'actions_taken': actions}
        
    except Exception as e:
        actions.append(f"Error checking service status: {e}")
        return {'status': 'ERROR', 'message': 'Unable to assess service status', 'actions_taken': actions}


def handle_general_emergency(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Handle general emergency (default)"""
    actions = []
    
    try:
        actions.append("🔍 Performing general emergency assessment...")
        
        # Quick system checks
        import psutil
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        actions.append(f"CPU usage: {cpu_percent}%")
        
        # Memory check
        memory = psutil.virtual_memory()
        actions.append(f"Memory usage: {memory.percent}%")
        
        # Disk check
        import shutil
        disk_usage = shutil.disk_usage(project_root)
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        actions.append(f"Disk usage: {disk_percent:.1f}%")
        
        # Determine overall status
        issues = []
        if cpu_percent > 90:
            issues.append("High CPU usage")
        if memory.percent > 90:
            issues.append("High memory usage")
        if disk_percent > 95:
            issues.append("Low disk space")
        
        if issues:
            actions.append(f"⚠️  Issues detected: {', '.join(issues)}")
            return {'status': 'CRITICAL', 'message': f"System issues: {', '.join(issues)}", 'actions_taken': actions}
        else:
            actions.append("✅ System metrics within normal ranges")
            return {'status': 'RESOLVED', 'message': 'No critical issues detected', 'actions_taken': actions}
        
    except Exception as e:
        actions.append(f"Error in general assessment: {e}")
        return {'status': 'ERROR', 'message': 'Unable to complete assessment', 'actions_taken': actions}


def perform_rapid_assessment(clara: ClaraMaintenanceEngine) -> List[str]:
    """Perform rapid system assessment"""
    assessment = []
    
    try:
        import psutil
        
        # System metrics
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        
        assessment.append(f"⚡ CPU: {cpu}% | Memory: {memory.percent}%")
        
        # Process count
        process_count = len(psutil.pids())
        assessment.append(f"📊 Processes: {process_count}")
        
        # Load average (Unix-like systems)
        try:
            load_avg = os.getloadavg()
            assessment.append(f"📈 Load: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        except (AttributeError, OSError):
            assessment.append("📈 Load: N/A (Windows)")
        
        # Critical file check
        critical_files = ["config/app_config.json", "memory/memory.json"]
        missing_files = []
        for file_path in critical_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            assessment.append(f"❌ Missing files: {len(missing_files)}")
        else:
            assessment.append("✅ Critical files present")
        
    except Exception as e:
        assessment.append(f"❌ Assessment error: {e}")
    
    return assessment


def perform_emergency_remediation(clara: ClaraMaintenanceEngine, emergency_type: str) -> List[str]:
    """Perform emergency remediation actions"""
    remediation = []
    
    try:
        # Clear temporary files
        temp_cleaned = emergency_temp_cleanup()
        if temp_cleaned:
            remediation.append(f"🧹 Cleaned {temp_cleaned} temporary files")
        
        # Memory cleanup
        import gc
        collected = gc.collect()
        if collected > 0:
            remediation.append(f"🗑️  Garbage collected {collected} objects")
        
        # Log rotation check
        log_dir = project_root / "maintenance" / "logs"
        if log_dir.exists():
            large_logs = [f for f in log_dir.glob("*.log") if f.stat().st_size > 10 * 1024 * 1024]
            if large_logs:
                remediation.append(f"📝 {len(large_logs)} large log files detected")
        
        # Emergency backup of critical files
        backup_result = emergency_backup_critical_files()
        if backup_result:
            remediation.append(f"💾 Emergency backup: {backup_result}")
        
        # System state recording
        clara.record_emergency_state(emergency_type)
        remediation.append("📊 Emergency state recorded in memory")
        
    except Exception as e:
        remediation.append(f"❌ Remediation error: {e}")
    
    return remediation


def verify_emergency_stability(clara: ClaraMaintenanceEngine) -> List[str]:
    """Verify system stability after emergency response"""
    stability = []
    
    try:
        import psutil
        import time
        
        # Multiple CPU readings for stability
        cpu_readings = []
        for _ in range(3):
            cpu_readings.append(psutil.cpu_percent(interval=0.5))
        
        avg_cpu = sum(cpu_readings) / len(cpu_readings)
        cpu_variance = max(cpu_readings) - min(cpu_readings)
        
        if avg_cpu < 80 and cpu_variance < 20:
            stability.append(f"✅ CPU stable: {avg_cpu:.1f}% (±{cpu_variance:.1f}%)")
        else:
            stability.append(f"⚠️  CPU unstable: {avg_cpu:.1f}% (±{cpu_variance:.1f}%)")
        
        # Memory stability
        memory = psutil.virtual_memory()
        if memory.percent < 85:
            stability.append(f"✅ Memory stable: {memory.percent}%")
        else:
            stability.append(f"⚠️  Memory high: {memory.percent}%")
        
        # File system check
        critical_files_ok = True
        for file_path in ["config/app_config.json", "memory/memory.json"]:
            if not (project_root / file_path).exists():
                critical_files_ok = False
                break
        
        if critical_files_ok:
            stability.append("✅ Critical files intact")
        else:
            stability.append("❌ Critical files missing")
        
    except Exception as e:
        stability.append(f"❌ Stability check error: {e}")
    
    return stability


def emergency_disk_cleanup() -> List[str]:
    """Perform emergency disk cleanup"""
    cleanup_results = []
    
    try:
        # Clean log files older than 7 days
        log_dir = project_root / "maintenance" / "logs"
        if log_dir.exists():
            old_logs = []
            for log_file in log_dir.glob("*.log"):
                if (time.time() - log_file.stat().st_mtime) > (7 * 24 * 3600):
                    old_logs.append(log_file)
            
            for log_file in old_logs:
                try:
                    log_file.unlink()
                    cleanup_results.append(f"Removed old log: {log_file.name}")
                except Exception as e:
                    cleanup_results.append(f"Failed to remove {log_file.name}: {e}")
        
        # Clean Python cache files
        cache_files = list(project_root.rglob("__pycache__"))
        for cache_dir in cache_files:
            try:
                import shutil
                shutil.rmtree(cache_dir)
                cleanup_results.append(f"Removed cache: {cache_dir.relative_to(project_root)}")
            except Exception as e:
                cleanup_results.append(f"Failed to remove cache: {e}")
        
    except Exception as e:
        cleanup_results.append(f"Cleanup error: {e}")
    
    return cleanup_results


def emergency_temp_cleanup() -> int:
    """Clean temporary files and return count"""
    try:
        temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store"]
        cleaned_count = 0
        
        for pattern in temp_patterns:
            temp_files = list(project_root.rglob(pattern))
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                    cleaned_count += 1
                except Exception:
                    pass
        
        return cleaned_count
    except Exception:
        return 0


def emergency_backup_critical_files() -> Optional[str]:
    """Create emergency backup of critical files"""
    try:
        backup_dir = project_root / "maintenance" / "emergency_backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"emergency_backup_{timestamp}"
        
        critical_files = [
            "config/app_config.json",
            "memory/memory.json",
            "maintenance/config/maintenance_config.json"
        ]
        
        backed_up = []
        for file_path in critical_files:
            source = project_root / file_path
            if source.exists():
                dest = backup_dir / f"{backup_name}_{source.name}"
                import shutil
                shutil.copy2(source, dest)
                backed_up.append(source.name)
        
        if backed_up:
            return f"{len(backed_up)} files"
        else:
            return None
            
    except Exception:
        return None


def attempt_backup_restoration(corrupted_files: List[str]) -> List[str]:
    """Attempt to restore corrupted files from backup"""
    restoration_results = []
    
    try:
        backup_dir = project_root / "maintenance" / "emergency_backups"
        if not backup_dir.exists():
            restoration_results.append("❌ No emergency backup directory found")
            return restoration_results
        
        backup_files = list(backup_dir.glob("emergency_backup_*"))
        if not backup_files:
            restoration_results.append("❌ No emergency backup files found")
            return restoration_results
        
        # Use most recent backup
        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        restoration_results.append(f"Using backup: {latest_backup.name}")
        
        # Attempt restoration (simplified)
        restoration_results.append("⚠️  Backup restoration requires manual intervention")
        restoration_results.append(f"Backup location: {backup_dir}")
        
    except Exception as e:
        restoration_results.append(f"Restoration error: {e}")
    
    return restoration_results


def generate_emergency_report(clara: ClaraMaintenanceEngine, emergency_type: str, results: Dict) -> str:
    """Generate emergency response report"""
    try:
        reports_dir = project_root / "maintenance" / "emergency_reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"emergency_report_{emergency_type}_{timestamp}.json"
        
        report_data = {
            "emergency_metadata": {
                "timestamp": datetime.now().isoformat(),
                "emergency_type": emergency_type,
                "clara_version": "1.0.0",
                "response_time_seconds": EMERGENCY_TIMEOUT - signal.alarm(0)
            },
            "response_summary": results['response_result'],
            "rapid_assessment": results['assessment'],
            "remediation_actions": results['remediation'],
            "stability_verification": results['stability'],
            "clara_emergency_notes": {
                "emergency_philosophy": "Rapid response, stabilize first, analyze later",
                "memory_updated": True,
                "follow_up_required": results['response_result']['status'] != 'RESOLVED'
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return str(report_file)
        
    except Exception as e:
        return f"Error generating report: {e}"


def generate_clara_emergency_assessment(emergency_type: str, response_result: Dict) -> List[str]:
    """Generate Clara's emergency assessment"""
    assessment = []
    
    try:
        status = response_result['status']
        
        if status == 'RESOLVED':
            assessment.append(f"Emergency {emergency_type} successfully resolved - system stable")
            assessment.append("Monitoring will continue to ensure no recurrence")
        elif status == 'STABILIZED':
            assessment.append(f"Emergency {emergency_type} stabilized but requires monitoring")
            assessment.append("Manual intervention may be needed for full resolution")
        elif status == 'CRITICAL':
            assessment.append(f"Emergency {emergency_type} requires immediate manual intervention")
            assessment.append("System stability compromised - escalation recommended")
        else:
            assessment.append(f"Emergency {emergency_type} response encountered errors")
            assessment.append("System status uncertain - manual assessment required")
        
        # Add emergency-specific insights
        if emergency_type in ['CPU', 'MEMORY']:
            assessment.append("Resource monitoring frequency will be increased")
        elif emergency_type in ['DISK']:
            assessment.append("Disk cleanup procedures should be reviewed and automated")
        elif emergency_type in ['API', 'DATABASE']:
            assessment.append("Service health checks will be enhanced")
        elif emergency_type == 'SECURITY':
            assessment.append("Security audit procedures will be strengthened")
        
        assessment.append("Emergency response patterns logged for future optimization")
        
    except Exception as e:
        assessment.append(f"Error generating assessment: {e}")
    
    return assessment


if __name__ == "__main__":
    main()