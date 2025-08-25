"""
Agent Orchestrator for AndroidWorld

This agent coordinates between task generation and execution, providing
a unified interface for running complete episodes.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, TaskResult
from .task_generator import TaskGenerator
from .task_executor import TaskExecutor


class AgentOrchestrator(BaseAgent):
    """Orchestrates task generation and execution"""

    def __init__(
        self, name: str = "Orchestrator", config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, config)

        # Initialize sub-agents
        self.task_generator = TaskGenerator(
            name="TaskGenerator", config=config.get("generator_config", {})
        )

        self.task_executor = TaskExecutor(
            name="TaskExecutor", config=config.get("executor_config", {})
        )

        self.logger.info(f"Orchestrator initialized with {self.name}")

    def generate_task(self) -> Dict[str, Any]:
        """Generate a task using the task generator"""
        return self.task_generator.generate_task()

    def execute_task(self, task: Dict[str, Any]) -> TaskResult:
        """Execute a task using the task executor"""
        return self.task_executor.execute_task(task)

    def run_episode(self) -> TaskResult:
        """Run a complete episode: generate and execute a task"""
        self.logger.info(f"Starting episode for orchestrator {self.name}")

        # Generate task
        task = self.generate_task()
        self.logger.info(f"Generated task: {task.get('name', 'Unknown')}")

        # Execute task
        start_time = time.time()
        result = self.execute_task(task)
        end_time = time.time()

        # Update result with timing
        result.execution_time = end_time - start_time

        # Store result
        self.results.append(result)

        self.logger.info(
            f"Episode completed: {result.success}, "
            f"Time: {result.execution_time:.2f}s"
        )

        return result

    def run_multiple_episodes(self, num_episodes: int) -> List[TaskResult]:
        """Run multiple episodes and return all results"""
        self.logger.info(f"Running {num_episodes} episodes...")

        results = []
        for episode in range(1, num_episodes + 1):
            self.logger.info(f"Episode {episode}/{num_episodes}")

            try:
                result = self.run_episode()
                results.append(result)

                # Small delay between episodes
                if episode < num_episodes:
                    time.sleep(2)

            except Exception as e:
                self.logger.error(f"Episode {episode} failed: {str(e)}")
                # Create a failed result
                failed_result = TaskResult(
                    task_id=f"episode_{episode}_failed",
                    task_name=f"Episode {episode}",
                    success=False,
                    execution_time=0.0,
                    start_time=time.time(),
                    end_time=time.time(),
                    error_message=str(e),
                )
                results.append(failed_result)

        self.logger.info(f"Completed {num_episodes} episodes")
        return results

    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all agents"""
        orchestrator_stats = self.get_statistics()
        generator_stats = self.task_generator.get_task_statistics()
        executor_stats = self.task_executor.get_statistics()

        # Combine statistics
        comprehensive_stats = {
            "orchestrator": orchestrator_stats,
            "task_generator": generator_stats,
            "task_executor": executor_stats,
            "summary": {
                "total_episodes": orchestrator_stats.get("total_tasks", 0),
                "overall_success_rate": orchestrator_stats.get("success_rate", 0),
                "average_execution_time": orchestrator_stats.get("avg_time", 0),
                "flakiness_rate": orchestrator_stats.get("flakiness_rate", 0),
            },
        }

        return comprehensive_stats

    def reset_all_agents(self):
        """Reset all agents to initial state"""
        self.reset()
        self.task_generator.reset()
        self.task_executor.reset()
        self.logger.info("All agents reset")

    def configure_agents(
        self, generator_config: Dict[str, Any], executor_config: Dict[str, Any]
    ):
        """Configure the sub-agents with new settings"""
        self.task_generator.config.update(generator_config)
        self.task_executor.config.update(executor_config)
        self.logger.info("Agent configurations updated")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "orchestrator": {
                "name": self.name,
                "status": "active",
                "episodes_run": len(self.results),
            },
            "task_generator": {
                "name": self.task_generator.name,
                "status": "active",
                "tasks_generated": len(self.task_generator.task_history),
            },
            "task_executor": {
                "name": self.task_executor.name,
                "status": "active",
                "tasks_executed": len(self.task_executor.results),
            },
        }
