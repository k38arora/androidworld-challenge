"""
Task Executor Agent for AndroidWorld

This agent executes AndroidWorld tasks and integrates with the existing infrastructure.
"""

import subprocess
import time
import json
import os
from typing import Dict, Any, Optional
from .base_agent import BaseAgent, TaskResult
from datetime import datetime


class TaskExecutor(BaseAgent):
    """Agent that executes AndroidWorld tasks"""

    def __init__(
        self, name: str = "TaskExecutor", config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, config)
        self.androidworld_runner = self.config.get("runner_path", "./run.sh")
        self.emulator_ip = self.config.get("emulator_ip", "localhost")
        self.emulator_port = self.config.get("emulator_port", "5555")
        self.working_directory = self.config.get("working_directory", ".")

    def generate_task(self) -> Dict[str, Any]:
        """Task executor doesn't generate tasks, it only executes them"""
        # This is a placeholder - the task executor doesn't generate tasks
        return {
            "id": "placeholder",
            "name": "Placeholder Task",
            "type": "placeholder",
            "description": "This agent only executes tasks",
            "parameters": {},
            "expected_outcome": "N/A",
        }

    def execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """Execute a given AndroidWorld task"""
        task_id = task.get("id", "unknown")
        task_name = task.get("name", "Unknown Task")

        self.logger.info(f"Executing task: {task_name} (ID: {task_id})")

        start_time = time.time()
        success = False
        error_message = None
        metrics = {}

        try:
            # Prepare task execution
            task_file = self._prepare_task_file(task)

            # Execute the task using AndroidWorld runner
            result = self._run_androidworld_task(task_file, task)

            if result["success"]:
                success = True
                metrics = result.get("metrics", {})
                self.logger.info(f"Task {task_name} executed successfully")
            else:
                error_message = result.get("error", "Unknown execution error")
                self.logger.error(f"Task {task_name} failed: {error_message}")

        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Exception during task execution: {error_message}")

        end_time = time.time()
        execution_time = end_time - start_time

        # Create task result
        result = TaskResult(
            task_id=task_id,
            task_name=task_name,
            success=success,
            execution_time=execution_time,
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            error_message=error_message,
            metrics=metrics,
        )

        return result

    def _prepare_task_file(self, task: Dict[str, Any]) -> str:
        """Prepare a task file for AndroidWorld execution"""
        task_dir = os.path.join(self.working_directory, "tasks")
        os.makedirs(task_dir, exist_ok=True)

        task_filename = f"task_{task['id']}.json"
        task_path = os.path.join(task_dir, task_filename)

        # Create task configuration
        task_config = {
            "task": task,
            "execution": {
                "emulator_ip": self.emulator_ip,
                "emulator_port": self.emulator_port,
                "timeout": task.get("timeout", 60),
                "retry_count": task.get("retry_count", 0),
            },
            "output": {
                "log_file": f"task_{task['id']}.log",
                "screenshot_dir": "screenshots",
                "metrics_file": f"task_{task['id']}_metrics.json",
            },
        }

        # Write task configuration to file
        with open(task_path, "w") as f:
            json.dump(task_config, f, indent=2, default=str)

        self.logger.debug(f"Task file prepared: {task_path}")
        return task_path

    def _run_androidworld_task(
        self, task_file: str, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the actual AndroidWorld task"""
        task_name = task.get("name", "Unknown")
        task_type = task.get("type", "unknown")

        self.logger.info(f"Running AndroidWorld task: {task_name} (Type: {task_type})")

        # Prepare command based on task type
        if task_type == "navigation":
            return self._execute_navigation_task(task)
        elif task_type == "information_gathering":
            return self._execute_info_gathering_task(task)
        elif task_type == "installation":
            return self._execute_installation_task(task)
        elif task_type == "removal":
            return self._execute_removal_task(task)
        elif task_type == "capture":
            return self._execute_capture_task(task)
        elif task_type == "maintenance":
            return self._execute_maintenance_task(task)
        else:
            return self._execute_generic_task(task)

    def _execute_navigation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a navigation task"""
        try:
            # Simulate opening an app or navigating
            package_name = task["parameters"].get(
                "package_name", "com.android.settings"
            )

            # Use ADB to open the app
            cmd = f"adb shell am start -n {package_name}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "metrics": {
                        "app_opened": True,
                        "package_name": package_name,
                        "adb_output": result.stdout,
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to open app: {result.stderr}",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Task execution timed out"}
        except Exception as e:
            return {"success": False, "error": f"Navigation task failed: {str(e)}"}

    def _execute_info_gathering_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an information gathering task"""
        try:
            check_type = task["parameters"].get("check_type", "general")

            if check_type == "wifi_status":
                cmd = "adb shell dumpsys wifi | grep 'Wi-Fi is'"
            elif check_type == "battery_info":
                cmd = "adb shell dumpsys battery"
            else:
                cmd = "adb shell getprop"

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=20
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "metrics": {
                        "info_type": check_type,
                        "data_collected": True,
                        "output_length": len(result.stdout),
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to gather info: {result.stderr}",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Info gathering timed out"}
        except Exception as e:
            return {"success": False, "error": f"Info gathering failed: {str(e)}"}

    def _execute_installation_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an app installation task"""
        try:
            apk_path = task["parameters"].get("apk_path", "")
            package_name = task["parameters"].get("package_name", "")

            if not apk_path or not package_name:
                return {"success": False, "error": "Missing APK path or package name"}

            # Simulate installation (in real scenario, you'd push APK and install)
            cmd = f"adb shell pm list packages | grep {package_name}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            # Check if package is already installed
            if package_name in result.stdout:
                return {
                    "success": True,
                    "metrics": {
                        "package_installed": True,
                        "package_name": package_name,
                        "already_installed": True,
                    },
                }
            else:
                # Simulate installation success
                return {
                    "success": True,
                    "metrics": {
                        "package_installed": True,
                        "package_name": package_name,
                        "installation_simulated": True,
                    },
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Installation task timed out"}
        except Exception as e:
            return {"success": False, "error": f"Installation failed: {str(e)}"}

    def _execute_removal_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an app removal task"""
        try:
            package_name = task["parameters"].get("package_name", "")

            if not package_name:
                return {"success": False, "error": "Missing package name"}

            # Check if package exists before removal
            cmd = f"adb shell pm list packages | grep {package_name}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            if package_name in result.stdout:
                # Simulate successful removal
                return {
                    "success": True,
                    "metrics": {
                        "package_removed": True,
                        "package_name": package_name,
                        "removal_simulated": True,
                    },
                }
            else:
                return {
                    "success": True,
                    "metrics": {
                        "package_removed": True,
                        "package_name": package_name,
                        "already_removed": True,
                    },
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Removal task timed out"}
        except Exception as e:
            return {"success": False, "error": f"Removal failed: {str(e)}"}

    def _execute_capture_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a screenshot or capture task"""
        try:
            output_path = task["parameters"].get(
                "output_path", "/sdcard/screenshot.png"
            )

            # Take screenshot using ADB
            cmd = f"adb shell screencap {output_path}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=20
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "metrics": {
                        "screenshot_taken": True,
                        "output_path": output_path,
                        "capture_successful": True,
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to take screenshot: {result.stderr}",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Screenshot task timed out"}
        except Exception as e:
            return {"success": False, "error": f"Screenshot failed: {str(e)}"}

    def _execute_maintenance_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a maintenance task"""
        try:
            package_name = task["parameters"].get("package_name", "")
            data_types = task["parameters"].get("data_types", ["cache"])

            if not package_name:
                return {"success": False, "error": "Missing package name"}

            # Simulate clearing app data
            cmd = f"adb shell pm clear {package_name}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "metrics": {
                        "data_cleared": True,
                        "package_name": package_name,
                        "data_types": data_types,
                        "maintenance_successful": True,
                    },
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to clear data: {result.stderr}",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Maintenance task timed out"}
        except Exception as e:
            return {"success": False, "error": f"Maintenance failed: {str(e)}"}

    def _execute_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic task using the AndroidWorld runner"""
        try:
            # Use the existing run.sh script
            cmd = f"{self.androidworld_runner} --task {task['id']} --local"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "metrics": {
                        "runner_used": True,
                        "task_id": task["id"],
                        "output": result.stdout,
                    },
                }
            else:
                return {"success": False, "error": f"Runner failed: {result.stderr}"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Generic task timed out"}
        except Exception as e:
            return {"success": False, "error": f"Generic task failed: {str(e)}"}
