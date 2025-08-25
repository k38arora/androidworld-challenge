"""
Task Generator Agent for AndroidWorld

This agent generates various types of AndroidWorld tasks based on different strategies.
"""

import random
import uuid
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, TaskResult
from datetime import datetime


class TaskGenerator(BaseAgent):
    """Agent that generates AndroidWorld tasks"""

    def __init__(
        self, name: str = "TaskGenerator", config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, config)
        self.task_templates = self._load_task_templates()
        self.task_history = []

    def _load_task_templates(self) -> List[Dict[str, Any]]:
        """Load predefined task templates"""
        return [
            {
                "name": "Open App",
                "type": "navigation",
                "description": "Open a specific application on the device",
                "parameters": {
                    "package_name": "com.android.settings",
                    "activity_name": "com.android.settings.Settings",
                },
                "expected_outcome": "Settings app should open successfully",
            },
            {
                "name": "Navigate to Settings",
                "type": "navigation",
                "description": "Navigate to device settings menu",
                "parameters": {"target_menu": "Settings", "submenu": "System"},
                "expected_outcome": "Should reach System settings menu",
            },
            {
                "name": "Check WiFi Status",
                "type": "information_gathering",
                "description": "Check the current WiFi connection status",
                "parameters": {"check_type": "connection_status", "timeout": 10},
                "expected_outcome": "Should return WiFi connection information",
            },
            {
                "name": "Install App",
                "type": "installation",
                "description": "Install an application from APK file",
                "parameters": {
                    "apk_path": "/sdcard/test_app.apk",
                    "package_name": "com.example.testapp",
                },
                "expected_outcome": "App should install successfully",
            },
            {
                "name": "Uninstall App",
                "type": "removal",
                "description": "Uninstall a specific application",
                "parameters": {"package_name": "com.example.testapp"},
                "expected_outcome": "App should be removed from device",
            },
            {
                "name": "Take Screenshot",
                "type": "capture",
                "description": "Capture a screenshot of the current screen",
                "parameters": {
                    "output_path": "/sdcard/screenshot.png",
                    "format": "PNG",
                },
                "expected_outcome": "Screenshot should be saved successfully",
            },
            {
                "name": "Check Battery Level",
                "type": "information_gathering",
                "description": "Get current battery level and status",
                "parameters": {"check_type": "battery_info", "include_charging": True},
                "expected_outcome": "Should return battery percentage and charging status",
            },
            {
                "name": "Clear App Data",
                "type": "maintenance",
                "description": "Clear data for a specific application",
                "parameters": {
                    "package_name": "com.android.settings",
                    "data_types": ["cache", "user_data"],
                },
                "expected_outcome": "App data should be cleared successfully",
            },
        ]

    def generate_task(self) -> Dict[str, Any]:
        """Generate a new task based on available templates"""
        # Select a random task template
        template = random.choice(self.task_templates)

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Create task with some randomization
        task = {
            "id": task_id,
            "name": template["name"],
            "type": template["type"],
            "description": template["description"],
            "parameters": template["parameters"].copy(),
            "expected_outcome": template["expected_outcome"],
            "priority": random.randint(1, 5),
            "timeout": random.randint(30, 120),
            "retry_count": random.randint(0, 2),
        }

        # Add some randomization to parameters
        if task["type"] == "navigation":
            # Randomize package names for variety
            packages = [
                "com.android.settings",
                "com.android.vending",
                "com.google.android.apps.maps",
                "com.whatsapp",
                "com.instagram.android",
            ]
            if "package_name" in task["parameters"]:
                task["parameters"]["package_name"] = random.choice(packages)

        self.logger.info(f"Generated task: {task['name']} (ID: {task_id})")
        self.task_history.append(task)

        return task

    def execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """Task generator doesn't execute tasks, it only generates them"""
        # This is a placeholder - the task generator doesn't execute tasks
        return TaskResult(
            task_id=task["id"],
            task_name=task["name"],
            success=True,
            execution_time=0.0,
            start_time=datetime.now(),
            end_time=datetime.now(),
            metrics={"task_type": "generation"},
        )

    def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated tasks"""
        if not self.task_history:
            return {}

        task_types = {}
        for task in self.task_history:
            task_type = task["type"]
            if task_type not in task_types:
                task_types[task_type] = 0
            task_types[task_type] += 1

        return {
            "total_generated": len(self.task_history),
            "task_types": task_types,
            "unique_tasks": len(set(task["name"] for task in self.task_history)),
        }

    def generate_custom_task(
        self, task_type: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a custom task with specific parameters"""
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "name": f"Custom_{task_type}",
            "type": task_type,
            "description": f"Custom {task_type} task",
            "parameters": parameters,
            "expected_outcome": "Task should complete successfully",
            "priority": 3,
            "timeout": 60,
            "retry_count": 1,
        }

        self.logger.info(f"Generated custom task: {task['name']} (ID: {task_id})")
        self.task_history.append(task)

        return task
