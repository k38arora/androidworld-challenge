#!/bin/bash

# AndroidWorld Agent Evaluation Script
# This script runs N episodes, aggregates metrics, and produces evaluation artifacts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
REPORTS_DIR="$SCRIPT_DIR/reports"
LOG_DIR="$SCRIPT_DIR/logs"
OUTPUT_DIR="$SCRIPT_DIR/outputs"

# Default values
NUM_EPISODES=10
AGENT_TYPE="orchestrator"
EMULATOR_IP="localhost"
EMULATOR_PORT="5555"
VERBOSE=false
OUTPUT_FORMAT="json"
GENERATE_REPORT=true

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -n, --episodes N        Number of episodes to run (default: 10)
    -a, --agent TYPE        Agent type: orchestrator, generator, executor (default: orchestrator)
    -i, --ip IP             Emulator IP address (default: localhost)
    -p, --port PORT         Emulator ADB port (default: 5555)
    -f, --format FORMAT     Output format: json, csv (default: json)
    -r, --no-report         Skip generating human-readable report
    -v, --verbose           Enable verbose output

Examples:
    # Run 20 episodes with orchestrator agent
    $0 --episodes 20 --agent orchestrator
    
    # Run 5 episodes with custom emulator IP
    $0 -n 5 -i 192.168.1.100
    
    # Run evaluation in CSV format
    $0 --format csv --episodes 15

EOF
}

# Function to log messages
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[$timestamp] INFO: $message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] WARN: $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] ERROR: $message${NC}"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${BLUE}[$timestamp] DEBUG: $message${NC}"
            fi
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python 3 not found. Please install Python 3 first."
        exit 1
    fi
    
    # Check if required Python packages are available
    if ! python3 -c "import json, time, logging" 2>/dev/null; then
        log "ERROR" "Required Python packages not found. Please install them first."
        exit 1
    fi
    
    # Check if agents directory exists (we're already in it)
    if [ ! -d "$SCRIPT_DIR" ]; then
        log "ERROR" "Current directory not found. Please ensure script is properly set up."
        exit 1
    fi
    
    log "INFO" "Prerequisites check passed"
}

# Function to create directories
create_directories() {
    log "DEBUG" "Creating necessary directories..."
    
    mkdir -p "$RESULTS_DIR"
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    log "DEBUG" "Directories created: $RESULTS_DIR, $REPORTS_DIR, $LOG_DIR, $OUTPUT_DIR"
}

# Function to run evaluation
run_evaluation() {
    log "INFO" "Starting AndroidWorld agent evaluation..."
    log "INFO" "Episodes: $NUM_EPISODES, Agent: $AGENT_TYPE, Emulator: $EMULATOR_IP:$EMULATOR_PORT"
    
    # Create evaluation script
    local eval_script="$SCRIPT_DIR/evaluation_runner.py"
    
    cat > "$eval_script" << 'EOF'
#!/usr/bin/env python3
"""
AndroidWorld Agent Evaluation Runner

This script runs multiple episodes using the specified agent and generates
evaluation artifacts.
"""

import sys
import os
import json
import csv
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path (we're already in agents directory)
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import AgentOrchestrator
from task_generator import TaskGenerator
from task_executor import TaskExecutor

def run_evaluation(num_episodes, agent_type, emulator_ip, emulator_port, output_format, results_dir, reports_dir):
    """Run the evaluation and generate results"""
    
    print(f"Starting evaluation with {agent_type} agent for {num_episodes} episodes...")
    
    # Configure agent based on type
    if agent_type == "orchestrator":
        config = {
            'executor_config': {
                'emulator_ip': emulator_ip,
                'emulator_port': emulator_port,
                'working_directory': '.'
            }
        }
        agent = AgentOrchestrator(name="EvaluationOrchestrator", config=config)
    elif agent_type == "generator":
        agent = TaskGenerator(name="EvaluationGenerator")
    elif agent_type == "executor":
        config = {
            'emulator_ip': emulator_ip,
            'emulator_port': emulator_port,
            'working_directory': '.'
        }
        agent = TaskExecutor(name="EvaluationExecutor", config=config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    # Run episodes
    start_time = time.time()
    
    if agent_type == "orchestrator":
        results = agent.run_multiple_episodes(num_episodes)
    else:
        # For single agents, run episodes manually
        results = []
        for episode in range(1, num_episodes + 1):
            print(f"Episode {episode}/{num_episodes}")
            try:
                if agent_type == "generator":
                    task = agent.generate_task()
                    # Create a mock result for generator
                    from agents.base_agent import TaskResult
                    from datetime import datetime
                    result = TaskResult(
                        task_id=task['id'],
                        task_name=task['name'],
                        success=True,
                        execution_time=0.1,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        metrics={'task_type': 'generation'}
                    )
                else:  # executor
                    # Generate a simple task for executor
                    task = {
                        'id': f'episode_{episode}',
                        'name': f'Test Task {episode}',
                        'type': 'information_gathering',
                        'parameters': {'check_type': 'general'}
                    }
                    result = agent.execute_task(task)
                
                results.append(result)
                time.sleep(1)  # Small delay between episodes
                
            except Exception as e:
                print(f"Episode {episode} failed: {str(e)}")
                # Create failed result
                from agents.base_agent import TaskResult
                from datetime import datetime
                failed_result = TaskResult(
                    task_id=f'episode_{episode}_failed',
                    task_name=f'Episode {episode}',
                    success=False,
                    execution_time=0.0,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error_message=str(e)
                )
                results.append(failed_result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Generate results
    generate_results(results, agent, output_format, results_dir, reports_dir, total_time)
    
    print(f"Evaluation completed in {total_time:.2f} seconds")
    return results

def generate_results(results, agent, output_format, results_dir, reports_dir, total_time):
    """Generate evaluation results and reports"""
    
    # Get agent statistics
    if hasattr(agent, 'get_comprehensive_statistics'):
        stats = agent.get_comprehensive_statistics()
    else:
        stats = agent.get_statistics()
    
    # Add evaluation metadata
    evaluation_data = {
        'evaluation': {
            'timestamp': datetime.now().isoformat(),
            'total_episodes': len(results),
            'total_time': total_time,
            'agent_type': agent.__class__.__name__,
            'agent_name': agent.name
        },
        'results': [
            {
                'task_id': r.task_id,
                'task_name': r.task_name,
                'success': r.success,
                'execution_time': r.execution_time,
                'start_time': r.start_time.isoformat() if hasattr(r.start_time, 'isoformat') else str(r.start_time),
                'end_time': r.end_time.isoformat() if hasattr(r.end_time, 'isoformat') else str(r.end_time),
                'error_message': r.error_message,
                'metrics': r.metrics
            }
            for r in results
        ],
        'statistics': stats
    }
    
    # Save results in specified format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format.lower() == 'json':
        results_file = os.path.join(results_dir, f'evaluation_results_{timestamp}.json')
        with open(results_file, 'w') as f:
            json.dump(evaluation_data, f, indent=2, default=str)
        print(f"Results saved to: {results_file}")
        
    elif output_format.lower() == 'csv':
        results_file = os.path.join(results_dir, f'evaluation_results_{timestamp}.csv')
        with open(results_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['task_id', 'task_name', 'success', 'execution_time', 'start_time', 'end_time', 'error_message'])
            # Write data
            for r in results:
                writer.writerow([
                    r.task_id,
                    r.task_name,
                    r.success,
                    r.execution_time,
                    r.start_time.isoformat() if hasattr(r.start_time, 'isoformat') else str(r.start_time),
                    r.end_time.isoformat() if hasattr(r.end_time, 'isoformat') else str(r.end_time),
                    r.error_message or ''
                ])
        print(f"Results saved to: {results_file}")
    
    # Generate human-readable report
    generate_human_report(evaluation_data, reports_dir, timestamp)

def generate_human_report(evaluation_data, reports_dir, timestamp):
    """Generate a human-readable evaluation report"""
    
    report_file = os.path.join(reports_dir, f'evaluation_report_{timestamp}.md')
    
    with open(report_file, 'w') as f:
        f.write("# AndroidWorld Agent Evaluation Report\n\n")
        
        # Evaluation Summary
        eval_info = evaluation_data['evaluation']
        f.write(f"## Evaluation Summary\n\n")
        f.write(f"- **Timestamp**: {eval_info['timestamp']}\n")
        f.write(f"- **Total Episodes**: {eval_info['total_episodes']}\n")
        f.write(f"- **Total Time**: {eval_info['total_time']:.2f} seconds\n")
        f.write(f"- **Agent Type**: {eval_info['agent_type']}\n")
        f.write(f"- **Agent Name**: {eval_info['agent_name']}\n\n")
        
        # Statistics
        stats = evaluation_data['statistics']
        if 'summary' in stats:
            summary = stats['summary']
            f.write(f"## Performance Metrics\n\n")
            f.write(f"- **Overall Success Rate**: {summary.get('overall_success_rate', 0):.2%}\n")
            f.write(f"- **Average Execution Time**: {summary.get('average_execution_time', 0):.2f} seconds\n")
            f.write(f"- **Flakiness Rate**: {summary.get('flakiness_rate', 0):.2%}\n\n")
        elif 'success_rate' in stats:
            f.write(f"## Performance Metrics\n\n")
            f.write(f"- **Success Rate**: {stats.get('success_rate', 0):.2%}\n")
            f.write(f"- **Average Execution Time**: {stats.get('avg_time', 0):.2f} seconds\n")
            f.write(f"- **Total Tasks**: {stats.get('total_tasks', 0)}\n\n")
        
        # Episode Results
        f.write(f"## Episode Results\n\n")
        f.write(f"| Episode | Task | Success | Time (s) | Error |\n")
        f.write(f"|---------|------|---------|----------|-------|\n")
        
        for i, result in enumerate(evaluation_data['results'], 1):
            task_name = result['task_name'][:30] + '...' if len(result['task_name']) > 30 else result['task_name']
            success = "✅" if result['success'] else "❌"
            error = result['error_message'][:50] + '...' if result['error_message'] and len(result['error_message']) > 50 else (result['error_message'] or '')
            
            f.write(f"| {i} | {task_name} | {success} | {result['execution_time']:.2f} | {error} |\n")
        
        f.write(f"\n")
        
        # Detailed Statistics
        if 'orchestrator' in stats:
            f.write(f"## Detailed Statistics\n\n")
            f.write(f"### Orchestrator\n")
            f.write(f"- Total Episodes: {stats['orchestrator'].get('total_tasks', 0)}\n")
            f.write(f"- Success Rate: {stats['orchestrator'].get('success_rate', 0):.2%}\n")
            f.write(f"- Average Time: {stats['orchestrator'].get('avg_time', 0):.2f}s\n\n")
            
            f.write(f"### Task Generator\n")
            f.write(f"- Tasks Generated: {stats['task_generator'].get('total_generated', 0)}\n")
            f.write(f"- Unique Tasks: {stats['task_generator'].get('unique_tasks', 0)}\n")
            f.write(f"- Task Types: {', '.join([f'{k}: {v}' for k, v in stats['task_generator'].get('task_types', {}).items()])}\n\n")
            
            f.write(f"### Task Executor\n")
            f.write(f"- Tasks Executed: {stats['task_executor'].get('total_tasks', 0)}\n")
            f.write(f"- Success Rate: {stats['task_executor'].get('success_rate', 0):.2%}\n")
            f.write(f"- Average Time: {stats['task_executor'].get('avg_time', 0):.2f}s\n\n")
    
    print(f"Report generated: {report_file}")

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python3 evaluation_runner.py <episodes> <agent_type> <emulator_ip> <emulator_port> <output_format> <results_dir>")
        sys.exit(1)
    
    num_episodes = int(sys.argv[1])
    agent_type = sys.argv[2]
    emulator_ip = sys.argv[3]
    emulator_port = sys.argv[4]
    output_format = sys.argv[5]
    results_dir = sys.argv[6]
    reports_dir = os.path.join(os.path.dirname(results_dir), 'reports')
    
    run_evaluation(num_episodes, agent_type, emulator_ip, emulator_port, output_format, results_dir, reports_dir)
EOF
    
    # Make script executable
    chmod +x "$eval_script"
    
    # Run evaluation
    log "INFO" "Executing evaluation..."
    
    if python3 "$eval_script" "$NUM_EPISODES" "$AGENT_TYPE" "$EMULATOR_IP" "$EMULATOR_PORT" "$OUTPUT_FORMAT" "$RESULTS_DIR"; then
        log "INFO" "Evaluation completed successfully"
    else
        log "ERROR" "Evaluation failed"
        exit 1
    fi
    
    # Clean up temporary script
    rm -f "$eval_script"
}

# Function to display results summary
display_summary() {
    log "INFO" "Evaluation completed!"
    log "INFO" "Results directory: $RESULTS_DIR"
    log "INFO" "Reports directory: $REPORTS_DIR"
    
    # Show latest results
    if [ -d "$RESULTS_DIR" ]; then
        latest_result=$(ls -t "$RESULTS_DIR"/*.json 2>/dev/null | head -1)
        if [ -n "$latest_result" ]; then
            log "INFO" "Latest results file: $(basename "$latest_result")"
        fi
    fi
    
    if [ -d "$REPORTS_DIR" ]; then
        latest_report=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -1)
        if [ -n "$latest_report" ]; then
            log "INFO" "Latest report: $(basename "$latest_report")"
        fi
    fi
}

# Main execution
main() {
    log "INFO" "AndroidWorld Agent Evaluation Script"
    log "INFO" "=================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -n|--episodes)
                NUM_EPISODES="$2"
                shift 2
                ;;
            -a|--agent)
                AGENT_TYPE="$2"
                shift 2
                ;;
            -i|--ip)
                EMULATOR_IP="$2"
                shift 2
                ;;
            -p|--port)
                EMULATOR_PORT="$2"
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -r|--no-report)
                GENERATE_REPORT=false
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Validate arguments
    if [[ ! "$NUM_EPISODES" =~ ^[0-9]+$ ]] || [ "$NUM_EPISODES" -lt 1 ]; then
        log "ERROR" "Number of episodes must be a positive integer"
        exit 1
    fi
    
    if [[ ! "$AGENT_TYPE" =~ ^(orchestrator|generator|executor)$ ]]; then
        log "ERROR" "Agent type must be one of: orchestrator, generator, executor"
        exit 1
    fi
    
    if [[ ! "$OUTPUT_FORMAT" =~ ^(json|csv)$ ]]; then
        log "ERROR" "Output format must be one of: json, csv"
        exit 1
    fi
    
    # Execute evaluation
    check_prerequisites
    create_directories
    run_evaluation
    display_summary
    
    log "INFO" "Evaluation script completed successfully"
}

# Run main function
main "$@"
