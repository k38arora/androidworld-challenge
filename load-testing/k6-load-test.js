import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const taskSuccessRate = new Rate('task_success_rate');
const taskDuration = new Trend('task_duration');
const taskErrors = new Counter('task_errors');
const concurrentUsers = new Counter('concurrent_users');

// Test configuration
export const options = {
  stages: [
    // Ramp up to 10 users over 2 minutes
    { duration: '2m', target: 10 },
    // Stay at 10 users for 3 minutes
    { duration: '3m', target: 10 },
    // Ramp up to 50 users over 3 minutes
    { duration: '3m', target: 50 },
    // Stay at 50 users for 5 minutes
    { duration: '5m', target: 50 },
    // Ramp up to 100 users over 3 minutes
    { duration: '3m', target: 100 },
    // Stay at 100 users for 5 minutes
    { duration: '5m', target: 100 },
    // Ramp down to 0 users over 2 minutes
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    // 95% of requests must complete within 5 seconds
    'http_req_duration': ['p(95)<5000'],
    // 99% of requests must complete within 10 seconds
    'http_req_duration': ['p(99)<10000'],
    // Error rate must be less than 5%
    'http_req_failed': ['rate<0.05'],
    // Task success rate must be above 90%
    'task_success_rate': ['rate>0.90'],
  },
};

// Test data
const taskTypes = [
  'click_button',
  'scroll_list',
  'input_text',
  'navigate_menu',
  'check_element',
  'wait_for_element',
  'take_screenshot',
  'verify_text'
];

const taskData = {
  click_button: {
    task_type: 'click_button',
    target: 'submit_button',
    coordinates: { x: 100, y: 200 }
  },
  scroll_list: {
    task_type: 'scroll_list',
    direction: 'down',
    distance: 500
  },
  input_text: {
    task_type: 'input_text',
    target: 'search_field',
    text: 'Android automation test'
  },
  navigate_menu: {
    task_type: 'navigate_menu',
    menu_path: ['Settings', 'Display', 'Brightness']
  },
  check_element: {
    task_type: 'check_element',
    target: 'status_indicator',
    expected_state: 'visible'
  },
  wait_for_element: {
    task_type: 'wait_for_element',
    target: 'loading_spinner',
    timeout: 5000
  },
  take_screenshot: {
    task_type: 'take_screenshot',
    filename: 'test_screenshot.png'
  },
  verify_text: {
    task_type: 'verify_text',
    target: 'result_message',
    expected_text: 'Operation completed successfully'
  }
};

// Main test function
export default function() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8080';
  const userId = __VU;
  const iteration = __ITER;
  
  // Track concurrent users
  concurrentUsers.add(1);
  
  // Health check
  const healthCheck = http.get(`${baseUrl}/health`);
  check(healthCheck, {
    'health check passed': (r) => r.status === 200,
    'health check response time < 100ms': (r) => r.timings.duration < 100,
  });
  
  // Readiness check
  const readyCheck = http.get(`${baseUrl}/ready`);
  check(readyCheck, {
    'readiness check passed': (r) => r.status === 200,
    'readiness check response time < 100ms': (r) => r.timings.duration < 100,
  });
  
  // Random task selection
  const taskType = taskTypes[Math.floor(Math.random() * taskTypes.length)];
  const taskPayload = {
    task_id: `load_test_${userId}_${iteration}_${Date.now()}`,
    user_id: userId,
    iteration: iteration,
    ...taskData[taskType]
  };
  
  // Execute task
  const startTime = Date.now();
  const taskResponse = http.post(`${baseUrl}/task`, JSON.stringify(taskPayload), {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'k6-load-test',
    },
  });
  const endTime = Date.now();
  const duration = endTime - startTime;
  
  // Record metrics
  taskDuration.add(duration);
  
  // Check response
  const success = check(taskResponse, {
    'task request successful': (r) => r.status === 200,
    'task response time < 5s': (r) => r.timings.duration < 5000,
    'task response has task_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.task_id === taskPayload.task_id;
      } catch (e) {
        return false;
      }
    },
    'task response has success field': (r) => {
      try {
        const body = JSON.parse(r.body);
        return 'success' in body;
      } catch (e) {
        return false;
      }
    },
  });
  
  // Record success/failure
  taskSuccessRate.add(success);
  
  if (!success) {
    taskErrors.add(1);
    console.error(`Task failed for user ${userId}, iteration ${iteration}:`, taskResponse.status, taskResponse.body);
  }
  
  // Metrics endpoint check
  const metricsResponse = http.get(`${baseUrl}/metrics`);
  check(metricsResponse, {
    'metrics endpoint accessible': (r) => r.status === 200,
    'metrics response contains Prometheus format': (r) => r.body.includes('# HELP'),
  });
  
  // Status endpoint check
  const statusResponse = http.get(`${baseUrl}/status`);
  check(statusResponse, {
    'status endpoint accessible': (r) => r.status === 200,
    'status response has service name': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.service === 'androidworld-worker';
      } catch (e) {
        return false;
      }
    },
  });
  
  // Trace endpoint check
  const traceResponse = http.get(`${baseUrl}/trace`);
  check(traceResponse, {
    'trace endpoint accessible': (r) => r.status === 200,
    'trace response has service name': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.service === 'androidworld-worker';
      } catch (e) {
        return false;
      }
    },
  });
  
  // Random sleep between requests (1-3 seconds)
  sleep(Math.random() * 2 + 1);
}

// Setup function (runs once before the test)
export function setup() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8080';
  
  console.log('Starting AndroidWorld Load Test');
  console.log(`Target URL: ${baseUrl}`);
  console.log('Test stages:');
  console.log('- 0-2m: Ramp up to 10 users');
  console.log('- 2-5m: Stay at 10 users');
  console.log('- 5-8m: Ramp up to 50 users');
  console.log('- 8-13m: Stay at 50 users');
  console.log('- 13-16m: Ramp up to 100 users');
  console.log('- 16-21m: Stay at 100 users');
  console.log('- 21-23m: Ramp down to 0 users');
  
  // Verify service is accessible
  const healthCheck = http.get(`${baseUrl}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`Service not accessible at ${baseUrl}/health`);
  }
  
  console.log('Service is accessible, starting load test...');
}

// Teardown function (runs once after the test)
export function teardown(data) {
  console.log('Load test completed');
  console.log('Final metrics:');
  console.log(`- Total requests: ${data.metrics.http_reqs.values.count}`);
  console.log(`- Average response time: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms`);
  console.log(`- 95th percentile: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms`);
  console.log(`- Error rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%`);
}
