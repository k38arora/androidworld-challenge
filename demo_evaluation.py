#!/usr/bin/env python3
"""
Demo script for AndroidWorld Agent Evaluation

This script demonstrates how to use the evaluation system programmatically.
"""

import sys
import os
import json
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))


def demo_basic_evaluation():
    """Demonstrate basic evaluation functionality"""
    print("=== Basic Evaluation Demo ===")

    try:
        from agents.orchestrator import AgentOrchestrator

        # Configure the orchestrator
        config = {
            "executor_config": {
                "emulator_ip": "localhost",
                "emulator_port": "5555",
                "working_directory": ".",
            }
        }

        # Create orchestrator
        orchestrator = AgentOrchestrator(name="DemoOrchestrator", config=config)

        print(f"Created orchestrator: {orchestrator.name}")

        # Run a few episodes
        print("\nRunning 3 episodes...")
        results = orchestrator.run_multiple_episodes(3)

        # Display results
        print(f"\nCompleted {len(results)} episodes:")
        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            print(
                f"  Episode {i}: {status} {result.task_name} ({result.execution_time:.2f}s)"
            )

        # Get statistics
        stats = orchestrator.get_comprehensive_statistics()
        print(f"\nFinal Statistics:")
        print(f"  Overall Success Rate: {stats['summary']['overall_success_rate']:.2%}")
        print(
            f"  Average Execution Time: {stats['summary']['average_execution_time']:.2f}s"
        )
        print(f"  Flakiness Rate: {stats['summary']['flakiness_rate']:.2%}")

        return True

    except Exception as e:
        print(f"Demo failed: {str(e)}")
        return False


def demo_task_generation():
    """Demonstrate task generation capabilities"""
    print("\n=== Task Generation Demo ===")

    try:
        from agents.task_generator import TaskGenerator

        generator = TaskGenerator(name="DemoGenerator")

        print("Generated tasks:")
        for i in range(5):
            task = generator.generate_task()
            print(f"  {i+1}. {task['name']} ({task['type']})")
            print(f"     Description: {task['description']}")
            print(f"     Parameters: {task['parameters']}")
            print()

        # Get generation statistics
        stats = generator.get_task_statistics()
        print(f"Generation Statistics:")
        print(f"  Total Generated: {stats['total_generated']}")
        print(f"  Unique Tasks: {stats['unique_tasks']}")
        print(
            f"  Task Types: {', '.join([f'{k}: {v}' for k, v in stats['task_types'].items()])}"
        )

        return True

    except Exception as e:
        print(f"Task generation demo failed: {str(e)}")
        return False


def demo_custom_evaluation():
    """Demonstrate custom evaluation setup"""
    print("\n=== Custom Evaluation Demo ===")

    try:
        from agents.orchestrator import AgentOrchestrator
        from agents.base_agent import TaskResult
        from datetime import datetime

        # Create orchestrator with custom configuration
        config = {
            "executor_config": {
                "emulator_ip": "192.168.1.100",  # Custom IP
                "emulator_port": "5555",
                "working_directory": "/custom/path",
            }
        }

        orchestrator = AgentOrchestrator(name="CustomOrchestrator", config=config)

        print(f"Created custom orchestrator: {orchestrator.name}")

        # Run episodes and collect detailed metrics
        print("\nRunning evaluation with custom metrics...")

        episode_results = []
        for episode in range(1, 4):
            print(f"  Episode {episode}...")

            # Run episode
            result = orchestrator.run_episode()

            # Add custom metrics
            if result.metrics is None:
                result.metrics = {}

            result.metrics.update(
                {
                    "episode_number": episode,
                    "custom_metric": f"value_{episode}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            episode_results.append(result)

        # Display custom results
        print(f"\nCustom Evaluation Results:")
        for result in episode_results:
            print(f"  Episode {result.metrics['episode_number']}: {result.task_name}")
            print(f"    Success: {result.success}")
            print(f"    Custom Metric: {result.metrics['custom_metric']}")
            print(f"    Timestamp: {result.metrics['timestamp']}")

        return True

    except Exception as e:
        print(f"Custom evaluation demo failed: {str(e)}")
        return False


def demo_results_export():
    """Demonstrate results export functionality"""
    print("\n=== Results Export Demo ===")

    try:
        from agents.orchestrator import AgentOrchestrator

        # Create orchestrator and run episodes
        config = {
            "executor_config": {
                "emulator_ip": "localhost",
                "emulator_port": "5555",
                "working_directory": ".",
            }
        }

        orchestrator = AgentOrchestrator(name="ExportOrchestrator", config=config)

        # Run episodes
        results = orchestrator.run_multiple_episodes(2)

        # Export results in different formats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON export
        json_data = {
            "evaluation": {
                "timestamp": datetime.now().isoformat(),
                "total_episodes": len(results),
                "agent_name": orchestrator.name,
            },
            "results": [
                {
                    "task_id": r.task_id,
                    "task_name": r.task_name,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message,
                    "metrics": r.metrics,
                }
                for r in results
            ],
            "statistics": orchestrator.get_comprehensive_statistics(),
        }

        # Save JSON
        json_file = f"demo_results_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(json_data, f, indent=2, default=str)

        print(f"Results exported to: {json_file}")

        # CSV export
        import csv

        csv_file = f"demo_results_{timestamp}.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["episode", "task_name", "success", "execution_time", "error"]
            )

            for i, result in enumerate(results, 1):
                writer.writerow(
                    [
                        i,
                        result.task_name,
                        result.success,
                        f"{result.execution_time:.2f}",
                        result.error_message or "",
                    ]
                )

        print(f"Results exported to: {csv_file}")

        # Clean up demo files
        os.remove(json_file)
        os.remove(csv_file)
        print("Demo files cleaned up")

        return True

    except Exception as e:
        print(f"Results export demo failed: {str(e)}")
        return False


def main():
    """Run all demos"""
    print("AndroidWorld Agent Evaluation Demo")
    print("=================================")
    print()

    demos = [
        demo_basic_evaluation,
        demo_task_generation,
        demo_custom_evaluation,
        demo_results_export,
    ]

    successful_demos = 0
    total_demos = len(demos)

    for demo in demos:
        try:
            if demo():
                successful_demos += 1
        except Exception as e:
            print(f"Demo {demo.__name__} crashed: {str(e)}")
        print()

    print(
        f"Demo Results: {successful_demos}/{total_demos} demos completed successfully"
    )

    if successful_demos == total_demos:
        print("🎉 All demos completed successfully!")
        print("\nYou can now use the evaluation system:")
        print("1. Run: ./evaluate.sh --episodes 10")
        print("2. Or use the agents programmatically as shown in the demos")
        return 0
    else:
        print("⚠️  Some demos failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
