#!/usr/bin/env python3
"""
Clara Maintenance Engine - Autonomous System Maintenance for Degiro-2025

Clara embodies vigilant, proactive maintenance with institutional memory.
She prevents issues before they escalate and learns from every incident.

Author: Clara Maintenance Agent
Version: 1.0.0
Status: Core Implementation
"""

import os
import sys
import json
import logging
import psutil
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import setup_logging
from core.config import config_manager, settings


class MaintenanceLevel(Enum):
    """Maintenance operation levels"""
    EMERGENCY = "emergency"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MaintenanceIncident:
    """Represents a maintenance incident for Clara's memory"""
    incident_id: str
    timestamp: str
    severity: str
    component: str
    description: str
    resolution: Optional[str] = None
    auto_resolved: bool = False
    pattern_match: Optional[str] = None


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int
    load_average: Optional[float] = None


class ClaraMaintenanceEngine:
    """
    Clara's Autonomous Maintenance Engine
    
    Clara isn't just a set of protocols; she's the vigilant guardian of Degiro-2025.
    She embodies meticulousness, calm preparedness, and an uncanny ability to
    anticipate issues before they escalate.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Clara's maintenance engine"""
        self.project_root = Path(__file__).parent.parent
        self.maintenance_dir = self.project_root / "maintenance"
        self.memory_file = self.project_root / "memory" / "memory.json"
        self.maintenance_memory_file = self.maintenance_dir / "config" / "clara_maintenance_memory.json"
        
        # Setup logging
        self.logger = self._setup_maintenance_logging()
        
        # Load configuration
        self.config = self._load_maintenance_config(config_path)
        
        # Initialize memory system
        self.memory = self._load_memory()
        self.maintenance_memory = self._load_maintenance_memory()
        
        # System monitoring thresholds
        self.thresholds = {
            'cpu_warning': self.config.get('cpu_warning_threshold', 80),
            'cpu_critical': self.config.get('cpu_critical_threshold', 95),
            'memory_warning': self.config.get('memory_warning_threshold', 80),
            'memory_critical': self.config.get('memory_critical_threshold', 95),
            'disk_warning': self.config.get('disk_warning_threshold', 85),
            'disk_critical': self.config.get('disk_critical_threshold', 90)
        }
        
        self.logger.info("Clara Maintenance Engine initialized. Ready for vigilant operation.")
    
    def _setup_maintenance_logging(self) -> logging.Logger:
        """Setup Clara's maintenance-specific logging"""
        log_file = self.maintenance_dir / "logs" / "maintenance.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create maintenance logger
        logger = logging.getLogger('clara_maintenance')
        logger.setLevel(logging.INFO)
        
        # File handler for maintenance logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - Clara - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_maintenance_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load maintenance configuration"""
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self.maintenance_dir / "config" / "maintenance_config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "enabled": True,
                "cpu_warning_threshold": 80,
                "cpu_critical_threshold": 95,
                "memory_warning_threshold": 80,
                "memory_critical_threshold": 95,
                "disk_warning_threshold": 85,
                "disk_critical_threshold": 90,
                "log_retention_days": 30,
                "backup_retention_days": 7,
                "auto_remediation_enabled": True,
                "notification_email": None
            }
            
            # Save default config
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load Clara's institutional memory from main memory.json"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_maintenance_memory(self) -> Dict[str, Any]:
        """Load Clara's maintenance-specific memory"""
        if self.maintenance_memory_file.exists():
            with open(self.maintenance_memory_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize maintenance memory structure
            initial_memory = {
                "clara_maintenance_history": [],
                "system_baselines": {},
                "incident_patterns": {},
                "performance_trends": [],
                "auto_remediation_history": [],
                "last_maintenance_runs": {
                    "daily": None,
                    "weekly": None,
                    "monthly": None,
                    "emergency": None
                },
                "clara_notes": [
                    "Clara's maintenance memory initialized.",
                    "Ready to learn and adapt to Degiro-2025's operational patterns."
                ]
            }
            
            self.maintenance_memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.maintenance_memory_file, 'w') as f:
                json.dump(initial_memory, f, indent=2)
            
            return initial_memory
    
    def _save_maintenance_memory(self):
        """Save Clara's maintenance memory"""
        with open(self.maintenance_memory_file, 'w') as f:
            json.dump(self.maintenance_memory, f, indent=2)
    
    def _record_incident(self, incident: MaintenanceIncident):
        """Record an incident in Clara's memory"""
        self.maintenance_memory["clara_maintenance_history"].append(asdict(incident))
        self._save_maintenance_memory()
        self.logger.info(f"Incident recorded: {incident.incident_id} - {incident.description}")
    
    def get_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get load average (Unix-like systems)
        load_avg = None
        try:
            load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else None
        except (OSError, AttributeError):
            pass
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=(disk.used / disk.total) * 100,
            process_count=len(psutil.pids()),
            load_average=load_avg
        )
    
    def check_system_health(self) -> List[MaintenanceIncident]:
        """Check system health and identify issues"""
        incidents = []
        metrics = self.get_system_metrics()
        
        # CPU checks
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            incident = MaintenanceIncident(
                incident_id=f"cpu_critical_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity=AlertSeverity.CRITICAL.value,
                component="system_cpu",
                description=f"CPU usage critical: {metrics.cpu_percent:.1f}%"
            )
            incidents.append(incident)
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            incident = MaintenanceIncident(
                incident_id=f"cpu_warning_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity=AlertSeverity.WARNING.value,
                component="system_cpu",
                description=f"CPU usage elevated: {metrics.cpu_percent:.1f}%"
            )
            incidents.append(incident)
        
        # Memory checks
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            incident = MaintenanceIncident(
                incident_id=f"memory_critical_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity=AlertSeverity.CRITICAL.value,
                component="system_memory",
                description=f"Memory usage critical: {metrics.memory_percent:.1f}%"
            )
            incidents.append(incident)
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            incident = MaintenanceIncident(
                incident_id=f"memory_warning_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity=AlertSeverity.WARNING.value,
                component="system_memory",
                description=f"Memory usage elevated: {metrics.memory_percent:.1f}%"
            )
            incidents.append(incident)
        
        # Disk checks
        if metrics.disk_percent >= self.thresholds['disk_critical']:
            incident = MaintenanceIncident(
                incident_id=f"disk_critical_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity=AlertSeverity.CRITICAL.value,
                component="system_disk",
                description=f"Disk usage critical: {metrics.disk_percent:.1f}%"
            )
            incidents.append(incident)
        elif metrics.disk_percent >= self.thresholds['disk_warning']:
            incident = MaintenanceIncident(
                incident_id=f"disk_warning_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity=AlertSeverity.WARNING.value,
                component="system_disk",
                description=f"Disk usage elevated: {metrics.disk_percent:.1f}%"
            )
            incidents.append(incident)
        
        return incidents
    
    def check_application_health(self) -> List[MaintenanceIncident]:
        """Check Degiro-2025 application health"""
        incidents = []
        
        # Check log files for errors
        log_dir = self.project_root / "logs"
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                incidents.extend(self._analyze_log_file(log_file))
        
        # Check core components
        core_files = [
            "core/degiro_api.py",
            "core/database.py",
            "core/portfolio_service.py"
        ]
        
        for core_file in core_files:
            file_path = self.project_root / core_file
            if not file_path.exists():
                incident = MaintenanceIncident(
                    incident_id=f"missing_core_file_{int(time.time())}",
                    timestamp=datetime.now().isoformat(),
                    severity=AlertSeverity.CRITICAL.value,
                    component="core_files",
                    description=f"Critical file missing: {core_file}"
                )
                incidents.append(incident)
        
        return incidents
    
    def _analyze_log_file(self, log_file: Path) -> List[MaintenanceIncident]:
        """Analyze log file for error patterns"""
        incidents = []
        
        try:
            # Read recent log entries (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            with open(log_file, 'r') as f:
                lines = f.readlines()[-1000:]  # Last 1000 lines
            
            error_patterns = [
                ("ERROR", AlertSeverity.CRITICAL),
                ("CRITICAL", AlertSeverity.CRITICAL),
                ("WARNING", AlertSeverity.WARNING),
                ("Exception", AlertSeverity.WARNING),
                ("Failed", AlertSeverity.WARNING)
            ]
            
            for line in lines:
                for pattern, severity in error_patterns:
                    if pattern in line:
                        incident = MaintenanceIncident(
                            incident_id=f"log_error_{int(time.time())}",
                            timestamp=datetime.now().isoformat(),
                            severity=severity.value,
                            component="application_logs",
                            description=f"Log pattern detected in {log_file.name}: {line.strip()[:100]}"
                        )
                        incidents.append(incident)
                        break
        
        except Exception as e:
            self.logger.warning(f"Could not analyze log file {log_file}: {e}")
        
        return incidents
    
    def run_daily_maintenance(self):
        """Run daily maintenance checks"""
        self.logger.info("Starting daily maintenance routine...")
        
        # Update last run time
        self.maintenance_memory["last_maintenance_runs"]["daily"] = datetime.now().isoformat()
        
        # System health check
        system_incidents = self.check_system_health()
        app_incidents = self.check_application_health()
        
        all_incidents = system_incidents + app_incidents
        
        # Record incidents
        for incident in all_incidents:
            self._record_incident(incident)
        
        # Log cleanup
        self._cleanup_old_logs()
        
        # Save memory
        self._save_maintenance_memory()
        
        self.logger.info(f"Daily maintenance completed. Found {len(all_incidents)} incidents.")
        
        return all_incidents
    
    def run_weekly_maintenance(self):
        """Run weekly maintenance checks"""
        self.logger.info("Starting weekly maintenance routine...")
        
        # Update last run time
        self.maintenance_memory["last_maintenance_runs"]["weekly"] = datetime.now().isoformat()
        
        # Run daily checks first
        incidents = self.run_daily_maintenance()
        
        # Additional weekly tasks
        self._analyze_performance_trends()
        self._update_system_baselines()
        
        self.logger.info("Weekly maintenance completed.")
        
        return incidents
    
    def run_monthly_maintenance(self):
        """Run monthly maintenance checks"""
        self.logger.info("Starting monthly maintenance routine...")
        
        # Update last run time
        self.maintenance_memory["last_maintenance_runs"]["monthly"] = datetime.now().isoformat()
        
        # Run weekly checks first
        incidents = self.run_weekly_maintenance()
        
        # Additional monthly tasks
        self._cleanup_old_backups()
        self._generate_monthly_report()
        
        self.logger.info("Monthly maintenance completed.")
        
        return incidents
    
    def run_emergency_check(self):
        """Run emergency system check"""
        self.logger.info("Running emergency system check...")
        
        # Update last run time
        self.maintenance_memory["last_maintenance_runs"]["emergency"] = datetime.now().isoformat()
        
        # Quick system health check
        incidents = self.check_system_health()
        
        # Record critical incidents immediately
        critical_incidents = [i for i in incidents if i.severity == AlertSeverity.CRITICAL.value]
        for incident in critical_incidents:
            self._record_incident(incident)
            self.logger.critical(f"EMERGENCY: {incident.description}")
        
        self._save_maintenance_memory()
        
        return incidents
    
    def _cleanup_old_logs(self):
        """Clean up old log files"""
        retention_days = self.config.get('log_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        log_dirs = [self.maintenance_dir / "logs", self.project_root / "logs"]
        
        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.glob("*.log*"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        try:
                            log_file.unlink()
                            self.logger.info(f"Cleaned up old log file: {log_file}")
                        except Exception as e:
                            self.logger.warning(f"Could not remove log file {log_file}: {e}")
    
    def _cleanup_old_backups(self):
        """Clean up old backup files"""
        retention_days = self.config.get('backup_retention_days', 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        backup_dirs = [self.project_root / "backups", self.project_root / "data" / "exports"]
        
        for backup_dir in backup_dirs:
            if backup_dir.exists():
                for backup_file in backup_dir.glob("*"):
                    if backup_file.stat().st_mtime < cutoff_date.timestamp():
                        try:
                            if backup_file.is_file():
                                backup_file.unlink()
                            elif backup_file.is_dir():
                                import shutil
                                shutil.rmtree(backup_file)
                            self.logger.info(f"Cleaned up old backup: {backup_file}")
                        except Exception as e:
                            self.logger.warning(f"Could not remove backup {backup_file}: {e}")
    
    def _analyze_performance_trends(self):
        """Analyze system performance trends"""
        # This would analyze historical metrics to identify trends
        # For now, just log that analysis is happening
        self.logger.info("Analyzing performance trends...")
        
        # Add current metrics to trends
        current_metrics = self.get_system_metrics()
        
        if "performance_trends" not in self.maintenance_memory:
            self.maintenance_memory["performance_trends"] = []
        
        self.maintenance_memory["performance_trends"].append(asdict(current_metrics))
        
        # Keep only last 30 days of metrics
        cutoff_date = datetime.now() - timedelta(days=30)
        self.maintenance_memory["performance_trends"] = [
            metric for metric in self.maintenance_memory["performance_trends"]
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_date
        ]
    
    def _update_system_baselines(self):
        """Update system performance baselines"""
        current_metrics = self.get_system_metrics()
        
        self.maintenance_memory["system_baselines"] = {
            "last_updated": current_metrics.timestamp,
            "cpu_baseline": current_metrics.cpu_percent,
            "memory_baseline": current_metrics.memory_percent,
            "disk_baseline": current_metrics.disk_percent,
            "process_count_baseline": current_metrics.process_count
        }
        
        self.logger.info("System baselines updated.")
    
    def _generate_monthly_report(self):
        """Generate monthly maintenance report"""
        report_file = self.maintenance_dir / "logs" / f"monthly_report_{datetime.now().strftime('%Y%m')}.json"
        
        report = {
            "report_date": datetime.now().isoformat(),
            "period": "monthly",
            "incidents_summary": self._summarize_incidents(),
            "performance_summary": self._summarize_performance(),
            "maintenance_actions": len(self.maintenance_memory.get("auto_remediation_history", [])),
            "system_health": "stable"  # This would be calculated based on incidents
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Monthly report generated: {report_file}")
    
    def _summarize_incidents(self) -> Dict[str, int]:
        """Summarize incidents by severity"""
        incidents = self.maintenance_memory.get("clara_maintenance_history", [])
        
        # Count incidents from last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_incidents = [
            incident for incident in incidents
            if datetime.fromisoformat(incident["timestamp"]) > cutoff_date
        ]
        
        summary = {
            "total": len(recent_incidents),
            "critical": len([i for i in recent_incidents if i["severity"] == "critical"]),
            "warning": len([i for i in recent_incidents if i["severity"] == "warning"]),
            "info": len([i for i in recent_incidents if i["severity"] == "info"])
        }
        
        return summary
    
    def _summarize_performance(self) -> Dict[str, float]:
        """Summarize performance metrics"""
        trends = self.maintenance_memory.get("performance_trends", [])
        
        if not trends:
            return {}
        
        # Calculate averages for last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_metrics = [
            metric for metric in trends
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_date
        ]
        
        if not recent_metrics:
            return {}
        
        avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["memory_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m["disk_percent"] for m in recent_metrics) / len(recent_metrics)
        
        return {
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_percent": round(avg_memory, 2),
            "avg_disk_percent": round(avg_disk, 2)
        }


def main():
    """Main entry point for Clara Maintenance Engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clara Maintenance Engine")
    parser.add_argument(
        "mode",
        choices=["daily", "weekly", "monthly", "emergency", "daemon"],
        help="Maintenance mode to run"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Initialize Clara
    clara = ClaraMaintenanceEngine(config_path=args.config)
    
    if args.mode == "daily":
        incidents = clara.run_daily_maintenance()
    elif args.mode == "weekly":
        incidents = clara.run_weekly_maintenance()
    elif args.mode == "monthly":
        incidents = clara.run_monthly_maintenance()
    elif args.mode == "emergency":
        incidents = clara.run_emergency_check()
    elif args.mode == "daemon":
        # Run as daemon with scheduled tasks
        clara.logger.info("Starting Clara in daemon mode...")
        
        # Schedule maintenance tasks
        schedule.every().day.at("09:00").do(clara.run_daily_maintenance)
        schedule.every().monday.at("10:00").do(clara.run_weekly_maintenance)
        schedule.every().month.at("11:00").do(clara.run_monthly_maintenance)
        schedule.every().hour.do(clara.run_emergency_check)
        
        clara.logger.info("Clara daemon started. Maintenance scheduled.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            clara.logger.info("Clara daemon stopped by user.")
    
    # Print summary
    if args.mode != "daemon":
        if incidents:
            print(f"\nMaintenance completed. Found {len(incidents)} incidents:")
            for incident in incidents:
                print(f"  - {incident.severity.upper()}: {incident.description}")
        else:
            print("\nMaintenance completed. No incidents found. System healthy.")


if __name__ == "__main__":
    main()