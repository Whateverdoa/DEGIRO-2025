#!/usr/bin/env python3
"""
Clara Monthly Maintenance Script

Executes Clara's comprehensive monthly maintenance routine with deep system analysis,
long-term trend evaluation, capacity planning, and strategic optimization.

Author: Clara Maintenance Agent
Version: 1.0.0
"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from maintenance.clara_maintenance_engine import ClaraMaintenanceEngine, AlertSeverity


def main():
    """Execute Clara's monthly maintenance routine"""
    print(f"Clara Monthly Maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Initialize Clara
        clara = ClaraMaintenanceEngine()
        clara.logger.info("Starting monthly maintenance routine...")
        
        # Execute monthly maintenance (includes weekly and daily checks)
        incidents = clara.run_monthly_maintenance()
        
        # Monthly-specific deep analysis
        print("\n📊 Monthly Deep System Analysis:")
        
        # Long-term performance analysis
        performance_report = analyze_monthly_performance(clara)
        print(f"   Performance trends: {performance_report['status']}")
        
        # Capacity planning analysis
        capacity_analysis = perform_capacity_planning(clara)
        print(f"   Capacity planning: {capacity_analysis['status']}")
        
        # Dependency security audit
        security_report = perform_comprehensive_security_audit()
        print(f"   Security audit: {security_report['status']}")
        
        # System optimization opportunities
        optimization_report = identify_optimization_opportunities(clara)
        print(f"   Optimization opportunities: {optimization_report['status']}")
        
        # Data integrity verification
        data_integrity = verify_data_integrity()
        print(f"   Data integrity: {data_integrity['status']}")
        
        # Backup verification
        backup_status = verify_backup_integrity()
        print(f"   Backup integrity: {backup_status['status']}")
        
        # Configuration audit
        config_audit = perform_configuration_audit()
        print(f"   Configuration audit: {config_audit['status']}")
        
        # Generate monthly insights and strategic recommendations
        insights = generate_monthly_insights(clara, incidents)
        strategic_recommendations = generate_strategic_recommendations(clara)
        
        # Detailed reporting
        print("\n📋 Monthly Maintenance Report:")
        print("=" * 50)
        
        # Performance section
        print("\n🚀 Performance Analysis:")
        for detail in performance_report['details']:
            print(f"   • {detail}")
        
        # Capacity section
        print("\n📈 Capacity Planning:")
        for detail in capacity_analysis['details']:
            print(f"   • {detail}")
        
        # Security section
        print("\n🔒 Security Assessment:")
        for detail in security_report['details']:
            print(f"   • {detail}")
        
        # Optimization section
        print("\n⚡ Optimization Opportunities:")
        for detail in optimization_report['details']:
            print(f"   • {detail}")
        
        # Clara's monthly insights
        if insights:
            print("\n🧠 Clara's Monthly Insights:")
            for insight in insights:
                print(f"   • {insight}")
        
        # Strategic recommendations
        if strategic_recommendations:
            print("\n🎯 Strategic Recommendations:")
            for rec in strategic_recommendations:
                print(f"   • {rec}")
        
        # Incident summary
        print("\n📊 Monthly Incident Summary:")
        if incidents:
            critical = [i for i in incidents if i.severity == AlertSeverity.CRITICAL.value]
            warnings = [i for i in incidents if i.severity == AlertSeverity.WARNING.value]
            info = [i for i in incidents if i.severity == AlertSeverity.INFO.value]
            
            print(f"   Total incidents: {len(incidents)}")
            if critical:
                print(f"   🚨 Critical: {len(critical)}")
                for inc in critical[:3]:  # Show first 3
                    print(f"      - {inc.component}: {inc.description}")
            if warnings:
                print(f"   ⚠️  Warnings: {len(warnings)}")
            if info:
                print(f"   ℹ️  Info: {len(info)}")
        else:
            print("   ✅ No incidents this month. Exceptional system stability.")
        
        # Generate monthly report file
        report_path = generate_monthly_report_file(clara, {
            'performance': performance_report,
            'capacity': capacity_analysis,
            'security': security_report,
            'optimization': optimization_report,
            'incidents': incidents,
            'insights': insights,
            'recommendations': strategic_recommendations
        })
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        print("\n" + "=" * 80)
        print("Clara's Monthly Maintenance Complete")
        print(f"Next monthly maintenance: {get_next_month_date()}")
        
        # Exit with appropriate code
        critical_count = len([i for i in incidents if i.severity == AlertSeverity.CRITICAL.value])
        if critical_count > 0:
            sys.exit(2)  # Critical issues
        elif len(incidents) > 20:
            sys.exit(1)  # Many warnings
        else:
            sys.exit(0)  # All good
            
    except Exception as e:
        print(f"\n❌ Error during monthly maintenance: {e}")
        sys.exit(3)


def analyze_monthly_performance(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Analyze system performance trends over the past month"""
    try:
        trends = clara.maintenance_memory.get("performance_trends", [])
        
        if len(trends) < 10:
            return {
                'status': "📈 Insufficient data for monthly analysis",
                'details': ["Need at least 10 data points for trend analysis"]
            }
        
        # Analyze last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        monthly_trends = [
            trend for trend in trends
            if datetime.fromisoformat(trend["timestamp"]) > cutoff_date
        ]
        
        if not monthly_trends:
            return {
                'status': "📈 No recent performance data",
                'details': ["No performance data in the last 30 days"]
            }
        
        # Calculate statistics
        cpu_values = [t["cpu_percent"] for t in monthly_trends]
        memory_values = [t["memory_percent"] for t in monthly_trends]
        disk_values = [t["disk_percent"] for t in monthly_trends]
        
        cpu_avg = sum(cpu_values) / len(cpu_values)
        cpu_max = max(cpu_values)
        cpu_min = min(cpu_values)
        
        memory_avg = sum(memory_values) / len(memory_values)
        memory_max = max(memory_values)
        
        disk_avg = sum(disk_values) / len(disk_values)
        
        # Determine overall status
        if cpu_avg > 80 or memory_avg > 85:
            status = "⚠️  High resource utilization detected"
        elif cpu_max > 95 or memory_max > 95:
            status = "⚠️  Resource spikes detected"
        else:
            status = "✅ Performance within acceptable ranges"
        
        details = [
            f"CPU: avg {cpu_avg:.1f}%, max {cpu_max:.1f}%, min {cpu_min:.1f}%",
            f"Memory: avg {memory_avg:.1f}%, max {memory_max:.1f}%",
            f"Disk: avg {disk_avg:.1f}%",
            f"Data points analyzed: {len(monthly_trends)}",
            f"Variability: CPU ±{(cpu_max - cpu_min)/2:.1f}%, Memory ±{(memory_max - memory_avg):.1f}%"
        ]
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error analyzing performance: {e}",
            'details': ["Unable to complete performance analysis"]
        }


def perform_capacity_planning(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Perform capacity planning analysis"""
    try:
        trends = clara.maintenance_memory.get("performance_trends", [])
        
        if len(trends) < 30:
            return {
                'status': "📊 Insufficient data for capacity planning",
                'details': ["Need at least 30 data points for capacity analysis"]
            }
        
        # Analyze growth trends
        recent_30 = trends[-30:]
        older_30 = trends[-60:-30] if len(trends) >= 60 else trends[:-30]
        
        if not older_30:
            return {
                'status': "📊 Need more historical data",
                'details': ["Require 60+ data points for trend comparison"]
            }
        
        # Calculate averages for comparison
        recent_cpu_avg = sum(t["cpu_percent"] for t in recent_30) / len(recent_30)
        recent_mem_avg = sum(t["memory_percent"] for t in recent_30) / len(recent_30)
        
        older_cpu_avg = sum(t["cpu_percent"] for t in older_30) / len(older_30)
        older_mem_avg = sum(t["memory_percent"] for t in older_30) / len(older_30)
        
        # Calculate growth rates
        cpu_growth = ((recent_cpu_avg - older_cpu_avg) / older_cpu_avg) * 100 if older_cpu_avg > 0 else 0
        mem_growth = ((recent_mem_avg - older_mem_avg) / older_mem_avg) * 100 if older_mem_avg > 0 else 0
        
        # Project future capacity needs (3 months)
        projected_cpu = recent_cpu_avg + (cpu_growth * 3 / 100 * recent_cpu_avg)
        projected_mem = recent_mem_avg + (mem_growth * 3 / 100 * recent_mem_avg)
        
        # Determine status
        if projected_cpu > 90 or projected_mem > 90:
            status = "🚨 Capacity upgrade needed within 3 months"
        elif projected_cpu > 75 or projected_mem > 80:
            status = "⚠️  Monitor capacity - approaching limits"
        elif cpu_growth > 10 or mem_growth > 10:
            status = "📈 Significant growth trend detected"
        else:
            status = "✅ Capacity adequate for projected growth"
        
        details = [
            f"CPU growth rate: {cpu_growth:+.1f}% (recent: {recent_cpu_avg:.1f}%)",
            f"Memory growth rate: {mem_growth:+.1f}% (recent: {recent_mem_avg:.1f}%)",
            f"3-month projection: CPU {projected_cpu:.1f}%, Memory {projected_mem:.1f}%",
            f"Capacity headroom: CPU {100-projected_cpu:.1f}%, Memory {100-projected_mem:.1f}%"
        ]
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error in capacity planning: {e}",
            'details': ["Unable to complete capacity analysis"]
        }


def perform_comprehensive_security_audit() -> Dict[str, Any]:
    """Perform comprehensive security audit"""
    try:
        issues = []
        recommendations = []
        
        # Check file permissions
        sensitive_files = [
            ".env.dev",
            "config/app_config.json",
            "maintenance/config/maintenance_config.json",
            "maintenance/config/alert_thresholds.json"
        ]
        
        for file_path in sensitive_files:
            full_path = project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                if stat.st_mode & 0o044:  # Others can read
                    issues.append(f"Overly permissive: {file_path}")
                    recommendations.append(f"chmod 600 {file_path}")
        
        # Check for exposed secrets
        secret_patterns = ['.env', 'password', 'secret', 'key', 'token']
        for pattern in secret_patterns:
            for file_path in project_root.rglob(f"*{pattern}*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.json', '.txt']:
                    if file_path.name not in ['.env.example', 'requirements.txt']:
                        issues.append(f"Potential secret file: {file_path.relative_to(project_root)}")
        
        # Check Python dependencies for known vulnerabilities (basic)
        req_file = project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Check for unpinned versions
            unpinned = [dep for dep in deps if not any(op in dep for op in ['==', '>=', '<=', '~='])]
            if unpinned:
                issues.append(f"{len(unpinned)} unpinned dependencies")
                recommendations.append("Pin all dependency versions")
        
        # Check for .git directory exposure
        git_dir = project_root / ".git"
        if git_dir.exists():
            # This is normal for development, but note it
            recommendations.append("Ensure .git directory is not deployed to production")
        
        # Determine status
        if len(issues) > 5:
            status = "🚨 Multiple security issues detected"
        elif len(issues) > 0:
            status = f"⚠️  {len(issues)} security issues found"
        else:
            status = "✅ No major security issues detected"
        
        details = issues + recommendations
        if not details:
            details = ["Security posture appears good", "Continue regular security monitoring"]
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error in security audit: {e}",
            'details': ["Unable to complete security audit"]
        }


def identify_optimization_opportunities(clara: ClaraMaintenanceEngine) -> Dict[str, Any]:
    """Identify system optimization opportunities"""
    try:
        opportunities = []
        
        # Check log file sizes
        log_dir = project_root / "maintenance" / "logs"
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            total_size = sum(f.stat().st_size for f in log_files)
            if total_size > 50 * 1024 * 1024:  # 50MB
                opportunities.append(f"Log rotation needed - {total_size / 1024 / 1024:.1f}MB total")
        
        # Check for large data files
        data_dir = project_root / "data"
        if data_dir.exists():
            large_files = []
            for file_path in data_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    large_files.append(file_path.name)
            if large_files:
                opportunities.append(f"Large data files detected: {', '.join(large_files[:3])}")
        
        # Check memory usage patterns
        trends = clara.maintenance_memory.get("performance_trends", [])
        if trends:
            recent_memory = [t["memory_percent"] for t in trends[-20:]]
            if recent_memory and max(recent_memory) > 85:
                opportunities.append("Memory optimization recommended - peak usage > 85%")
        
        # Check for unused dependencies
        req_file = project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps = [line.strip().split('==')[0].split('>=')[0] for line in f 
                       if line.strip() and not line.startswith('#')]
            
            # Basic check for common unused packages
            python_files = list(project_root.rglob("*.py"))
            used_imports = set()
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        for dep in deps:
                            if f"import {dep}" in content or f"from {dep}" in content:
                                used_imports.add(dep)
                except:
                    continue
            
            unused = set(deps) - used_imports
            if len(unused) > 3:  # Only report if significant
                opportunities.append(f"Potentially unused dependencies: {len(unused)} packages")
        
        # Check for configuration optimization
        config_file = project_root / "maintenance" / "config" / "maintenance_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check if monitoring intervals could be optimized
            intervals = config.get("maintenance_schedule", {}).get("daily", {}).get("check_intervals", {})
            if intervals.get("system_health", 300) < 60:  # Less than 1 minute
                opportunities.append("Consider increasing system health check interval")
        
        # Determine status
        if len(opportunities) > 5:
            status = "⚡ Multiple optimization opportunities identified"
        elif len(opportunities) > 0:
            status = f"⚡ {len(opportunities)} optimization opportunities found"
        else:
            status = "✅ System appears well-optimized"
        
        details = opportunities if opportunities else ["No immediate optimization opportunities identified"]
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error identifying optimizations: {e}",
            'details': ["Unable to complete optimization analysis"]
        }


def verify_data_integrity() -> Dict[str, Any]:
    """Verify data integrity across the system"""
    try:
        issues = []
        checks = []
        
        # Check configuration files
        config_files = [
            "config/app_config.json",
            "maintenance/config/maintenance_config.json",
            "maintenance/config/alert_thresholds.json"
        ]
        
        for config_file in config_files:
            full_path = project_root / config_file
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        json.load(f)
                    checks.append(f"✓ {config_file} - valid JSON")
                except json.JSONDecodeError as e:
                    issues.append(f"✗ {config_file} - invalid JSON: {e}")
            else:
                issues.append(f"✗ {config_file} - missing")
        
        # Check memory file integrity
        memory_file = project_root / "memory" / "memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    memory_data = json.load(f)
                
                # Validate memory structure
                required_sections = ["maintenance_sessions", "maintenance_patterns", "system_knowledge"]
                for section in required_sections:
                    if section in memory_data:
                        checks.append(f"✓ Memory section '{section}' present")
                    else:
                        issues.append(f"✗ Memory section '{section}' missing")
                        
            except json.JSONDecodeError:
                issues.append("✗ memory.json - invalid JSON")
        else:
            issues.append("✗ memory.json - missing")
        
        # Check for data directory consistency
        data_dir = project_root / "data"
        if data_dir.exists():
            data_files = list(data_dir.glob("*"))
            checks.append(f"✓ Data directory contains {len(data_files)} files")
        
        # Determine status
        if issues:
            status = f"⚠️  {len(issues)} data integrity issues found"
        else:
            status = "✅ Data integrity verified"
        
        details = checks + issues
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error verifying data integrity: {e}",
            'details': ["Unable to complete data integrity check"]
        }


def verify_backup_integrity() -> Dict[str, Any]:
    """Verify backup integrity and coverage"""
    try:
        backup_status = []
        issues = []
        
        # Check if backup script exists
        backup_script = project_root / "tools" / "backup.sh"
        if backup_script.exists():
            backup_status.append("✓ Backup script present")
            
            # Check if script is executable
            if os.access(backup_script, os.X_OK):
                backup_status.append("✓ Backup script is executable")
            else:
                issues.append("✗ Backup script not executable")
        else:
            issues.append("✗ Backup script missing")
        
        # Check for recent backups (if backup directory exists)
        backup_dirs = [
            project_root / "backups",
            project_root / "backup",
            project_root.parent / "backups"
        ]
        
        recent_backup_found = False
        for backup_dir in backup_dirs:
            if backup_dir.exists():
                backup_files = list(backup_dir.glob("backup_*.tar.gz"))
                if backup_files:
                    # Check for recent backups (within last 7 days)
                    recent_backups = [
                        f for f in backup_files
                        if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days <= 7
                    ]
                    if recent_backups:
                        backup_status.append(f"✓ Recent backup found: {recent_backups[-1].name}")
                        recent_backup_found = True
                        break
        
        if not recent_backup_found:
            issues.append("✗ No recent backups found (within 7 days)")
        
        # Check critical files that should be backed up
        critical_files = [
            "config/app_config.json",
            "memory/memory.json",
            "maintenance/config/maintenance_config.json"
        ]
        
        for critical_file in critical_files:
            if (project_root / critical_file).exists():
                backup_status.append(f"✓ Critical file present: {critical_file}")
            else:
                issues.append(f"✗ Critical file missing: {critical_file}")
        
        # Determine status
        if issues:
            status = f"⚠️  {len(issues)} backup issues found"
        else:
            status = "✅ Backup integrity verified"
        
        details = backup_status + issues
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error verifying backups: {e}",
            'details': ["Unable to complete backup verification"]
        }


def perform_configuration_audit() -> Dict[str, Any]:
    """Perform comprehensive configuration audit"""
    try:
        audit_results = []
        issues = []
        
        # Audit maintenance configuration
        config_file = project_root / "maintenance" / "config" / "maintenance_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check critical configuration sections
            required_sections = ["clara_personality", "system_monitoring", "maintenance_schedule"]
            for section in required_sections:
                if section in config:
                    audit_results.append(f"✓ Configuration section '{section}' present")
                else:
                    issues.append(f"✗ Missing configuration section: {section}")
            
            # Check alert configuration
            if "alerting" in config:
                alerting = config["alerting"]
                if alerting.get("enabled", False):
                    audit_results.append("✓ Alerting enabled")
                    if "email" in alerting:
                        audit_results.append("✓ Email alerting configured")
                else:
                    issues.append("⚠️  Alerting disabled")
        
        # Audit alert thresholds
        thresholds_file = project_root / "maintenance" / "config" / "alert_thresholds.json"
        if thresholds_file.exists():
            with open(thresholds_file, 'r') as f:
                thresholds = json.load(f)
            
            # Check for reasonable threshold values
            system_thresholds = thresholds.get("system", {})
            cpu_threshold = system_thresholds.get("cpu_percent", {}).get("warning", 0)
            memory_threshold = system_thresholds.get("memory_percent", {}).get("warning", 0)
            
            if 70 <= cpu_threshold <= 90:
                audit_results.append(f"✓ CPU threshold reasonable: {cpu_threshold}%")
            else:
                issues.append(f"⚠️  CPU threshold may be too {('low' if cpu_threshold < 70 else 'high')}: {cpu_threshold}%")
            
            if 75 <= memory_threshold <= 95:
                audit_results.append(f"✓ Memory threshold reasonable: {memory_threshold}%")
            else:
                issues.append(f"⚠️  Memory threshold may be too {('low' if memory_threshold < 75 else 'high')}: {memory_threshold}%")
        
        # Check environment configuration
        env_file = project_root / ".env.dev"
        if env_file.exists():
            audit_results.append("✓ Development environment file present")
        else:
            issues.append("⚠️  No .env.dev file found")
        
        # Determine status
        if len(issues) > 3:
            status = f"⚠️  {len(issues)} configuration issues found"
        elif issues:
            status = f"⚠️  {len(issues)} minor configuration issues"
        else:
            status = "✅ Configuration audit passed"
        
        details = audit_results + issues
        
        return {'status': status, 'details': details}
        
    except Exception as e:
        return {
            'status': f"❌ Error in configuration audit: {e}",
            'details': ["Unable to complete configuration audit"]
        }


def generate_monthly_insights(clara: ClaraMaintenanceEngine, incidents: List) -> List[str]:
    """Generate Clara's monthly insights based on comprehensive analysis"""
    insights = []
    
    try:
        # Analyze incident patterns over the month
        if incidents:
            # Component analysis
            components = [i.component for i in incidents]
            component_counts = {}
            for comp in components:
                component_counts[comp] = component_counts.get(comp, 0) + 1
            
            if component_counts:
                most_problematic = max(component_counts.items(), key=lambda x: x[1])
                insights.append(f"Most incident-prone component: '{most_problematic[0]}' ({most_problematic[1]} incidents)")
            
            # Severity analysis
            critical_count = len([i for i in incidents if i.severity == AlertSeverity.CRITICAL.value])
            if critical_count > 0:
                insights.append(f"Critical incidents this month: {critical_count} - requires attention")
        
        # Performance trend insights
        trends = clara.maintenance_memory.get("performance_trends", [])
        if len(trends) > 50:
            recent_cpu = [t["cpu_percent"] for t in trends[-30:]]
            older_cpu = [t["cpu_percent"] for t in trends[-60:-30]] if len(trends) >= 60 else []
            
            if recent_cpu and older_cpu:
                recent_avg = sum(recent_cpu) / len(recent_cpu)
                older_avg = sum(older_cpu) / len(older_cpu)
                change = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
                
                if abs(change) > 10:
                    direction = "increased" if change > 0 else "decreased"
                    insights.append(f"CPU usage has {direction} by {abs(change):.1f}% compared to previous period")
        
        # Memory usage insights
        memory_history = clara.maintenance_memory.get("clara_maintenance_history", [])
        if len(memory_history) > 100:
            insights.append(f"Maintenance history contains {len(memory_history)} entries - rich pattern analysis available")
        
        # System stability insights
        if not incidents:
            insights.append("Exceptional month - zero incidents recorded, system stability is outstanding")
        elif len(incidents) < 5:
            insights.append(f"Low incident count ({len(incidents)}) indicates good system stability")
        
        # Seasonal or time-based insights
        current_month = datetime.now().strftime("%B")
        insights.append(f"Monthly analysis complete for {current_month} - patterns logged for future reference")
        
        # Default insight if none generated
        if len(insights) == 1:  # Only the month completion insight
            insights.append("System operating within expected parameters - no significant anomalies detected")
            
    except Exception as e:
        insights.append(f"Error generating insights: {e}")
    
    return insights


def generate_strategic_recommendations(clara: ClaraMaintenanceEngine) -> List[str]:
    """Generate Clara's strategic recommendations for long-term system health"""
    recommendations = []
    
    try:
        # Analyze system baselines for strategic planning
        baselines = clara.maintenance_memory.get("system_baselines", {})
        if baselines:
            cpu_baseline = baselines.get("cpu_baseline", 0)
            memory_baseline = baselines.get("memory_baseline", 0)
            
            if cpu_baseline > 60:
                recommendations.append("Strategic: Consider CPU capacity planning - baseline usage trending upward")
            if memory_baseline > 70:
                recommendations.append("Strategic: Memory optimization should be prioritized in next quarter")
        
        # Long-term maintenance strategy
        history = clara.maintenance_memory.get("clara_maintenance_history", [])
        if len(history) > 200:
            recommendations.append("Strategic: Rich maintenance history available - consider implementing predictive maintenance")
        
        # Infrastructure recommendations
        trends = clara.maintenance_memory.get("performance_trends", [])
        if len(trends) > 100:
            recent_variability = calculate_performance_variability(trends[-50:])
            if recent_variability > 20:  # High variability
                recommendations.append("Strategic: High performance variability detected - investigate workload patterns")
        
        # Security strategy
        recommendations.append("Strategic: Schedule quarterly security dependency audit")
        
        # Backup strategy
        recommendations.append("Strategic: Verify backup restoration procedures quarterly")
        
        # Monitoring strategy
        recommendations.append("Strategic: Consider implementing automated performance baseline updates")
        
        # Capacity planning
        recommendations.append("Strategic: Establish quarterly capacity planning reviews")
        
        # Documentation strategy
        recommendations.append("Strategic: Maintain runbook documentation for all automated remediation procedures")
        
        # Default recommendations
        if len(recommendations) < 3:
            recommendations.extend([
                "Strategic: Continue current maintenance schedule - system health is good",
                "Strategic: Focus on proactive monitoring and trend analysis"
            ])
            
    except Exception as e:
        recommendations.append(f"Error generating strategic recommendations: {e}")
    
    return recommendations


def calculate_performance_variability(trends: List[Dict]) -> float:
    """Calculate performance variability coefficient"""
    if not trends:
        return 0
    
    cpu_values = [t["cpu_percent"] for t in trends]
    if not cpu_values:
        return 0
    
    mean_cpu = sum(cpu_values) / len(cpu_values)
    if mean_cpu == 0:
        return 0
    
    variance = sum((x - mean_cpu) ** 2 for x in cpu_values) / len(cpu_values)
    std_dev = variance ** 0.5
    
    return (std_dev / mean_cpu) * 100  # Coefficient of variation as percentage


def generate_monthly_report_file(clara: ClaraMaintenanceEngine, report_data: Dict) -> str:
    """Generate detailed monthly report file"""
    try:
        reports_dir = project_root / "maintenance" / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m")
        report_file = reports_dir / f"monthly_report_{timestamp}.json"
        
        # Prepare comprehensive report
        full_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "monthly_maintenance",
                "clara_version": "1.0.0",
                "system": "Degiro-2025"
            },
            "executive_summary": {
                "total_incidents": len(report_data['incidents']),
                "critical_incidents": len([i for i in report_data['incidents'] if i.severity == AlertSeverity.CRITICAL.value]),
                "system_health": "Good" if len(report_data['incidents']) < 10 else "Needs Attention",
                "key_insights_count": len(report_data['insights']),
                "recommendations_count": len(report_data['recommendations'])
            },
            "detailed_analysis": {
                "performance": report_data['performance'],
                "capacity": report_data['capacity'],
                "security": report_data['security'],
                "optimization": report_data['optimization']
            },
            "incidents": [
                {
                    "timestamp": i.timestamp,
                    "severity": i.severity,
                    "component": i.component,
                    "message": i.description,
                    "auto_resolved": getattr(i, 'auto_resolved', False)
                } for i in report_data['incidents']
            ],
            "insights": report_data['insights'],
            "strategic_recommendations": report_data['recommendations'],
            "clara_notes": {
                "maintenance_philosophy": "Prevent, Preserve, Perfect",
                "memory_entries": len(clara.maintenance_memory.get("clara_maintenance_history", [])),
                "patterns_identified": len(clara.maintenance_memory.get("maintenance_patterns", {})),
                "next_monthly_maintenance": get_next_month_date()
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(full_report, f, indent=2, default=str)
        
        return str(report_file)
        
    except Exception as e:
        return f"Error generating report: {e}"


def get_next_month_date() -> str:
    """Get next month's maintenance date"""
    today = datetime.now()
    if today.month == 12:
        next_month = datetime(today.year + 1, 1, 1)
    else:
        next_month = datetime(today.year, today.month + 1, 1)
    
    return next_month.strftime("%Y-%m-01 10:00")


if __name__ == "__main__":
    main()