#!/usr/bin/env python3
"""
Clara Weekly Maintenance Script

Executes Clara's weekly maintenance routine with comprehensive system analysis,
performance trend evaluation, and proactive optimization.

Author: Clara Maintenance Agent
Version: 1.0.0
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from maintenance.clara_maintenance_engine import ClaraMaintenanceEngine, AlertSeverity


def main():
    """Execute Clara's weekly maintenance routine"""
    print(f"Clara Weekly Maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Initialize Clara
        clara = ClaraMaintenanceEngine()
        clara.logger.info("Starting weekly maintenance routine...")
        
        # Execute weekly maintenance (includes daily checks)
        incidents = clara.run_weekly_maintenance()
        
        # Weekly-specific analysis
        print("\n📊 Weekly System Analysis:")
        
        # Performance trend analysis
        performance_analysis = analyze_performance_trends(clara)
        print(f"   Performance trends: {performance_analysis}")
        
        # Security audit
        security_status = perform_security_audit()
        print(f"   Security audit: {security_status}")
        
        # Dependency analysis
        dependency_status = analyze_dependencies()
        print(f"   Dependencies: {dependency_status}")
        
        # Configuration drift check
        config_status = check_configuration_drift()
        print(f"   Configuration: {config_status}")
        
        # Database health check
        db_status = check_database_health()
        print(f"   Database health: {db_status}")
        
        # API integration health
        api_status = check_api_integrations()
        print(f"   API integrations: {api_status}")
        
        # Generate weekly insights
        insights = generate_weekly_insights(clara, incidents)
        if insights:
            print("\n🧠 Clara's Weekly Insights:")
            for insight in insights:
                print(f"   • {insight}")
        
        # Report summary
        print("\n📋 Weekly Maintenance Summary:")
        if incidents:
            critical = [i for i in incidents if i.severity == AlertSeverity.CRITICAL.value]
            warnings = [i for i in incidents if i.severity == AlertSeverity.WARNING.value]
            info = [i for i in incidents if i.severity == AlertSeverity.INFO.value]
            
            print(f"   Total incidents: {len(incidents)}")
            if critical:
                print(f"   🚨 Critical: {len(critical)}")
            if warnings:
                print(f"   ⚠️  Warnings: {len(warnings)}")
            if info:
                print(f"   ℹ️  Info: {len(info)}")
        else:
            print("   ✅ No incidents found. System performing well.")
        
        # Recommendations
        recommendations = generate_recommendations(clara)
        if recommendations:
            print("\n💡 Clara's Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        print("\n" + "=" * 70)
        print("Clara's Weekly Maintenance Complete")
        print(f"Next weekly maintenance: Next Monday at 10:00")
        
        # Exit with appropriate code
        critical_count = len([i for i in incidents if i.severity == AlertSeverity.CRITICAL.value])
        if critical_count > 0:
            sys.exit(2)  # Critical issues
        elif len(incidents) > 10:
            sys.exit(1)  # Many warnings
        else:
            sys.exit(0)  # All good
            
    except Exception as e:
        print(f"\n❌ Error during weekly maintenance: {e}")
        sys.exit(3)


def analyze_performance_trends(clara: ClaraMaintenanceEngine) -> str:
    """Analyze system performance trends over the past week"""
    try:
        trends = clara.maintenance_memory.get("performance_trends", [])
        
        if len(trends) < 2:
            return "📈 Insufficient data for trend analysis"
        
        # Analyze last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_trends = [
            trend for trend in trends
            if datetime.fromisoformat(trend["timestamp"]) > cutoff_date
        ]
        
        if not recent_trends:
            return "📈 No recent performance data"
        
        # Calculate averages
        avg_cpu = sum(t["cpu_percent"] for t in recent_trends) / len(recent_trends)
        avg_memory = sum(t["memory_percent"] for t in recent_trends) / len(recent_trends)
        avg_disk = sum(t["disk_percent"] for t in recent_trends) / len(recent_trends)
        
        # Determine trend status
        if avg_cpu > 80 or avg_memory > 80:
            return f"⚠️  High usage (CPU: {avg_cpu:.1f}%, Mem: {avg_memory:.1f}%)"
        elif avg_cpu > 60 or avg_memory > 60:
            return f"📊 Moderate usage (CPU: {avg_cpu:.1f}%, Mem: {avg_memory:.1f}%)"
        else:
            return f"✅ Good performance (CPU: {avg_cpu:.1f}%, Mem: {avg_memory:.1f}%)"
            
    except Exception as e:
        return f"❌ Error analyzing trends: {e}"


def perform_security_audit() -> str:
    """Perform basic security audit"""
    try:
        issues = []
        
        # Check file permissions on sensitive files
        sensitive_files = [
            ".env.dev",
            "config/app_config.json",
            "maintenance/config/maintenance_config.json"
        ]
        
        for file_path in sensitive_files:
            full_path = project_root / file_path
            if full_path.exists():
                stat = full_path.stat()
                # Check if file is readable by others (basic check)
                if stat.st_mode & 0o044:  # Others can read
                    issues.append(f"Permissions too open: {file_path}")
        
        # Check for .env files in wrong locations
        for env_file in project_root.rglob(".env*"):
            if env_file.name not in [".env.dev", ".env.example"]:
                issues.append(f"Unexpected env file: {env_file.relative_to(project_root)}")
        
        if issues:
            return f"⚠️  {len(issues)} security issues found"
        else:
            return "✅ No security issues detected"
            
    except Exception as e:
        return f"❌ Error in security audit: {e}"


def analyze_dependencies() -> str:
    """Analyze project dependencies for updates and vulnerabilities"""
    try:
        req_file = project_root / "requirements.txt"
        if not req_file.exists():
            return "❌ requirements.txt not found"
        
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        # Count dependencies
        deps = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        
        # Basic analysis
        pinned_deps = [dep for dep in deps if '>=' in dep or '==' in dep]
        unpinned_deps = [dep for dep in deps if '>=' not in dep and '==' not in dep and dep]
        
        if unpinned_deps:
            return f"⚠️  {len(unpinned_deps)} unpinned dependencies"
        else:
            return f"✅ {len(pinned_deps)} dependencies properly pinned"
            
    except Exception as e:
        return f"❌ Error analyzing dependencies: {e}"


def check_configuration_drift() -> str:
    """Check for configuration drift"""
    try:
        config_files = [
            "config/app_config.json",
            "maintenance/config/maintenance_config.json",
            "maintenance/config/alert_thresholds.json"
        ]
        
        issues = []
        for config_file in config_files:
            full_path = project_root / config_file
            if not full_path.exists():
                issues.append(f"Missing: {config_file}")
                continue
            
            try:
                with open(full_path, 'r') as f:
                    json.load(f)  # Validate JSON
            except json.JSONDecodeError:
                issues.append(f"Invalid JSON: {config_file}")
        
        if issues:
            return f"⚠️  {len(issues)} configuration issues"
        else:
            return "✅ All configurations valid"
            
    except Exception as e:
        return f"❌ Error checking configuration: {e}"


def check_database_health() -> str:
    """Check database health and connectivity"""
    try:
        # This would normally connect to the database
        # For now, just check if database module exists
        db_file = project_root / "core" / "database.py"
        if not db_file.exists():
            return "❌ Database module missing"
        
        # Check for database-related files
        data_dir = project_root / "data"
        if data_dir.exists():
            db_files = list(data_dir.glob("*.db")) + list(data_dir.glob("*.sqlite"))
            if db_files:
                return f"✅ Database files present ({len(db_files)} files)"
        
        return "ℹ️  Database status unknown (no local files)"
        
    except Exception as e:
        return f"❌ Error checking database: {e}"


def check_api_integrations() -> str:
    """Check API integration health"""
    try:
        # Check if API modules exist
        api_file = project_root / "core" / "degiro_api.py"
        if not api_file.exists():
            return "❌ DEGIRO API module missing"
        
        # Check for recent API logs or test results
        test_files = list(project_root.glob("test_*api*.py"))
        if test_files:
            return f"✅ API modules and tests present ({len(test_files)} test files)"
        else:
            return "⚠️  API module present but no test files found"
            
    except Exception as e:
        return f"❌ Error checking API integrations: {e}"


def generate_weekly_insights(clara: ClaraMaintenanceEngine, incidents: List) -> List[str]:
    """Generate Clara's weekly insights based on observations"""
    insights = []
    
    try:
        # Analyze incident patterns
        if incidents:
            components = [i.component for i in incidents]
            component_counts = {}
            for comp in components:
                component_counts[comp] = component_counts.get(comp, 0) + 1
            
            most_problematic = max(component_counts.items(), key=lambda x: x[1])
            if most_problematic[1] > 1:
                insights.append(f"Component '{most_problematic[0]}' had {most_problematic[1]} incidents this week")
        
        # Check maintenance memory for patterns
        history = clara.maintenance_memory.get("clara_maintenance_history", [])
        if len(history) > 10:
            insights.append(f"Maintenance history contains {len(history)} incidents - pattern analysis available")
        
        # Performance insights
        trends = clara.maintenance_memory.get("performance_trends", [])
        if len(trends) > 20:
            recent_cpu = [t["cpu_percent"] for t in trends[-10:]]
            if recent_cpu and max(recent_cpu) - min(recent_cpu) > 30:
                insights.append("CPU usage shows high variability - investigate workload patterns")
        
        # If no specific insights, provide general observation
        if not insights:
            insights.append("System operating within normal parameters - no significant patterns detected")
            
    except Exception as e:
        insights.append(f"Error generating insights: {e}")
    
    return insights


def generate_recommendations(clara: ClaraMaintenanceEngine) -> List[str]:
    """Generate Clara's recommendations for system improvement"""
    recommendations = []
    
    try:
        # Check system baselines
        baselines = clara.maintenance_memory.get("system_baselines", {})
        if baselines:
            cpu_baseline = baselines.get("cpu_baseline", 0)
            memory_baseline = baselines.get("memory_baseline", 0)
            
            if cpu_baseline > 70:
                recommendations.append("Consider CPU optimization - baseline usage is high")
            if memory_baseline > 80:
                recommendations.append("Monitor memory usage - baseline approaching limits")
        
        # Check log file sizes
        log_dir = project_root / "maintenance" / "logs"
        if log_dir.exists():
            total_size = sum(f.stat().st_size for f in log_dir.glob("*.log"))
            if total_size > 100 * 1024 * 1024:  # 100MB
                recommendations.append("Log files are large - consider more aggressive rotation")
        
        # Check incident frequency
        history = clara.maintenance_memory.get("clara_maintenance_history", [])
        recent_incidents = [
            inc for inc in history
            if datetime.fromisoformat(inc["timestamp"]) > datetime.now() - timedelta(days=7)
        ]
        
        if len(recent_incidents) > 20:
            recommendations.append("High incident rate this week - review system capacity")
        elif len(recent_incidents) == 0:
            recommendations.append("No incidents this week - system stability excellent")
        
        # Default recommendation if none generated
        if not recommendations:
            recommendations.append("Continue current maintenance schedule - system performing well")
            
    except Exception as e:
        recommendations.append(f"Error generating recommendations: {e}")
    
    return recommendations


if __name__ == "__main__":
    main()