"""
Base Agent Class for AndroidWorld

This class provides common functionality for all agents that interact with AndroidWorld.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskResult:
    """Result of a task execution"""

    task_id: str
    task_name: str
    success: bool
    execution_time: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all AndroidWorld agents"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = self._setup_logging()
        self.results: List[TaskResult] = []

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the agent"""
        logger = logging.getLogger(f"agent.{self.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    def generate_task(self) -> Dict[str, Any]:
        """Generate a new task to execute"""
        pass

    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """Execute a given task"""
        pass

    def run_episode(self) -> TaskResult:
        """Run a complete episode: generate and execute a task"""
        self.logger.info(f"Starting episode for agent {self.name}")

        # Generate task
        task = self.generate_task()
        self.logger.info(f"Generated task: {task.get('name', 'Unknown')}")

        # Execute task
        start_time = time.time()
        result = self.execute_task(task)
        end_time = time.time()

        # Update result with timing
        result.execution_time = end_time - start_time
        result.start_time = datetime.fromtimestamp(start_time)
        result.end_time = datetime.fromtimestamp(end_time)

        # Store result
        self.results.append(result)

        self.logger.info(
            f"Episode completed: {result.success}, "
            f"Time: {result.execution_time:.2f}s"
        )

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics from all results"""
        if not self.results:
            return {}

        total_tasks = len(self.results)
        successful_tasks = sum(1 for r in self.results if r.success)
        failed_tasks = total_tasks - successful_tasks

        execution_times = [r.execution_time for r in self.results]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Calculate flakiness (tasks that succeed sometimes but fail others)
        task_names = set(r.task_name for r in self.results)
        flaky_tasks = 0

        for task_name in task_names:
            task_results = [r for r in self.results if r.task_name == task_name]
            if len(task_results) > 1:
                successes = sum(1 for r in task_results if r.success)
                if 0 < successes < len(task_results):
                    flaky_tasks += 1

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "avg_time": avg_time,
            "flaky_tasks": flaky_tasks,
            "flakiness_rate": flaky_tasks / len(task_names) if task_names else 0,
        }

    def reset(self):
        """Reset agent state and clear results"""
        self.results.clear()
        self.logger.info(f"Agent {self.name} reset")
