#!/usr/bin/env python3
"""
Test script for AndroidWorld agents

This script tests the basic functionality of our agent system.
"""

import sys
import os
import json
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))


def test_task_generator():
    """Test the task generator agent"""
    print("Testing Task Generator...")

    try:
        from agents.task_generator import TaskGenerator

        generator = TaskGenerator(name="TestGenerator")

        # Generate a few tasks
        tasks = []
        for i in range(3):
            task = generator.generate_task()
            tasks.append(task)
            print(f"  Generated task {i+1}: {task['name']} ({task['type']})")

        # Get statistics
        stats = generator.get_task_statistics()
        print(f"  Statistics: {stats}")

        print("✅ Task Generator test passed")
        return True

    except Exception as e:
        print(f"❌ Task Generator test failed: {str(e)}")
        return False


def test_task_executor():
    """Test the task executor agent"""
    print("Testing Task Executor...")

    try:
        from agents.task_executor import TaskExecutor

        config = {
            "emulator_ip": "localhost",
            "emulator_port": "5555",
            "working_directory": ".",
        }

        executor = TaskExecutor(name="TestExecutor", config=config)

        # Test with a simple task
        test_task = {
            "id": "test_task_001",
            "name": "Test Information Gathering",
            "type": "information_gathering",
            "parameters": {"check_type": "general"},
        }

        result = executor.execute_task(test_task)
        print(f"  Executed task: {result.task_name}")
        print(f"  Success: {result.success}")
        print(f"  Execution time: {result.execution_time:.2f}s")

        print("✅ Task Executor test passed")
        return True

    except Exception as e:
        print(f"❌ Task Executor test failed: {str(e)}")
        return False


def test_orchestrator():
    """Test the orchestrator agent"""
    print("Testing Agent Orchestrator...")

    try:
        from agents.orchestrator import AgentOrchestrator

        config = {
            "executor_config": {
                "emulator_ip": "localhost",
                "emulator_port": "5555",
                "working_directory": ".",
            }
        }

        orchestrator = AgentOrchestrator(name="TestOrchestrator", config=config)

        # Run a single episode
        result = orchestrator.run_episode()
        print(f"  Episode completed: {result.success}")
        print(f"  Task: {result.task_name}")
        print(f"  Execution time: {result.execution_time:.2f}s")

        # Get comprehensive statistics
        stats = orchestrator.get_comprehensive_statistics()
        print(f"  Statistics: {json.dumps(stats['summary'], indent=2)}")

        print("✅ Agent Orchestrator test passed")
        return True

    except Exception as e:
        print(f"❌ Agent Orchestrator test failed: {str(e)}")
        return False


def test_episode_runner():
    """Test running multiple episodes"""
    print("Testing Episode Runner...")

    try:
        from agents.orchestrator import AgentOrchestrator

        config = {
            "executor_config": {
                "emulator_ip": "localhost",
                "emulator_port": "5555",
                "working_directory": ".",
            }
        }

        orchestrator = AgentOrchestrator(name="TestOrchestrator", config=config)

        # Run 3 episodes
        results = orchestrator.run_multiple_episodes(3)

        print(f"  Completed {len(results)} episodes")
        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            print(
                f"    Episode {i}: {status} {result.task_name} ({result.execution_time:.2f}s)"
            )

        # Get final statistics
        stats = orchestrator.get_comprehensive_statistics()
        print(f"  Final success rate: {stats['summary']['overall_success_rate']:.2%}")

        print("✅ Episode Runner test passed")
        return True

    except Exception as e:
        print(f"❌ Episode Runner test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("AndroidWorld Agent System Test")
    print("==============================")
    print()

    tests = [
        test_task_generator,
        test_task_executor,
        test_orchestrator,
        test_episode_runner,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}")
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The agent system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
