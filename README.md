# AndroidWorld Challenge - Complete Evaluator Guide

## 🎯 **Challenge Overview**

Deploy AndroidWorld against cloud Android emulators (Genymotion), build an agent/evaluation harness using Google's agent-starter-pack, and demonstrate production-grade deployment, scaling, and observability using Vertex AI.

---

## 🚀 **Quick Start for Evaluators**

### **Prerequisites**

- Git installed
- Python 3.7+ installed
- Docker installed
- Genymotion Cloud account with valid subscription
- Google Cloud Project with Vertex AI enabled

### **Exact Challenge Steps**

```bash
# 1. Clone repo and read README
git clone <repository-url>
cd qualgent-challenge
cat README.md

# 2. Export Genymotion credentials (or follow runbook)
cp env.example .env
# Edit .env with your credentials

# 3. ./infra/create_devices.sh (or follow UI steps)
./infra/create_devices.sh

# 4. docker build -t candidate/android-world . && docker run --env-file .env candidate/android-world
docker build -t candidate/android-world .
docker run --env-file .env candidate/android-world

# 5. ./agents/evaluate.sh --episodes 50 → check results/* report.md
./agents/evaluate.sh --episodes 50
ls -la agents/results/
cat agents/reports/$(ls -t agents/reports/ | head -1)
```

---

## 📋 **Detailed Setup Instructions**

### **Step 1: Configure Environment**

```bash
# Copy example environment file
cp env.example .env

# Edit with your Genymotion credentials
nano .env
```

**Required Environment Variables:**

```bash
# Genymotion Cloud Credentials (Required)
GENYMOTION_USERNAME=your-genymotion-username@email.com
GENYMOTION_PASSWORD=your-genymotion-api-key

# Google Cloud Configuration (Optional - uses gcloud config if not set)
GOOGLE_CLOUD_PROJECT=your-project-id-here
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_CLOUD_ZONE=us-central1-a

# Agent System Defaults
DEFAULT_EPISODES=50
DEFAULT_AGENT_TYPE=orchestrator
DEFAULT_OUTPUT_FORMAT=json

# Docker Configuration
DOCKER_IMAGE_NAME=candidate/android-world
DOCKER_CONTAINER_NAME=androidworld-challenge
```

**Important:** This challenge requires actual Genymotion Cloud credentials for cloud Android emulators. You need:

1. **Genymotion Cloud account** with valid subscription
2. **Google Cloud Project** with Vertex AI enabled
3. **Billing enabled** for both services

### **Step 2: Create Cloud Devices**

```bash
# Run device creation script
./infra/create_devices.sh
```

This script will:

- Authenticate with Genymotion Cloud using your API key
- Create cloud Android emulator instances
- Set up ADB connections for automation

### **Step 3: Build and Run Docker Container**

```bash
# Build the Docker image
docker build -t candidate/android-world .

# Run with environment variables
docker run --env-file .env candidate/android-world
```

### **Step 4: Run Evaluation Pipeline**

```bash
# Run 50 episodes as specified in challenge
./agents/evaluate.sh --episodes 50

# Check generated results
ls -la agents/results/
ls -la agents/reports/

# View latest report
cat agents/reports/$(ls -t agents/reports/ | head -1)
```

---

## 🏗️ **Project Architecture**

### **Goal 1: Infrastructure & Deployment**

- **Docker Containerization**: `Dockerfile` for AndroidWorld execution
- **Cloud Emulators**: Genymotion Cloud integration via `infra/create_devices.sh`
- **Infrastructure Scripts**: Cloud deployment and local emulator setup
- **Main Runner**: `run.sh` for executing AndroidWorld tasks

### **Goal 2: Agent Integration & Evaluation**

- **Agent System**: Modular architecture using agent-starter-pack patterns
  - `BaseAgent`: Abstract base class for all agents
  - `TaskGenerator`: Generates AndroidWorld tasks from templates
  - `TaskExecutor`: Executes tasks using ADB and AndroidWorld
  - `AgentOrchestrator`: Coordinates task generation and execution
- **Evaluation Pipeline**: `agents/evaluate.sh` runs N episodes and aggregates metrics
- **Metrics Collection**: Success rate, average execution time, flakiness
- **Output Generation**: Machine-readable (JSON/CSV) and human-readable (Markdown) reports

### **Goal 3: Scaling, Observability & Reliability**

- **Kubernetes Deployment**: Production-ready deployment with autoscaling
  - Horizontal Pod Autoscaler (HPA) for automatic scaling
  - Resource-based scaling (CPU 70%, Memory 80%)
  - Staging and production environments
- **CI/CD Pipeline**: GitHub Actions with automated testing and deployment
  - Unit tests, smoke tests, and coverage reporting
  - Automated Docker builds and deployments
  - Post-deployment verification
- **Observability & Tracing**: Comprehensive monitoring and debugging
  - Google Cloud Logging, Trace, and Monitoring integration
  - OpenTelemetry for distributed tracing
  - Custom metrics for task performance
- **Load Testing**: Performance validation with k6
  - Multi-stage load testing (10 → 50 → 100 users)
  - Performance thresholds and reporting
  - Automated report generation

### **Production Features**

- **Vertex AI Integration**: Model monitoring, logging, custom metrics
- **Cloud Monitoring**: Custom metrics and alerting
- **Scalable Architecture**: Containerized deployment with environment configuration
- **Health Checks**: Kubernetes liveness and readiness probes
- **Web Server**: HTTP endpoints for monitoring and task execution

---

## 📊 **Expected Results**

### **Evaluation Output**

- **Success Rate**: > 0% (some tasks may fail without real emulator)
- **Execution Time**: < 60 seconds for 50 episodes
- **Task Types**: Multiple AndroidWorld task types generated
- **Report Quality**: Comprehensive metrics and episode details

### **Generated Files**

- **Results**: JSON files in `agents/results/` with detailed task execution data
- **Reports**: Markdown files in `agents/reports/` with human-readable summaries
- **Logs**: Detailed execution logs for debugging

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"ADB command not found"**

```bash
# Install Android platform tools
brew install android-platform-tools  # macOS
sudo apt-get install android-tools-adb  # Ubuntu
```

#### **"Genymotion credentials missing"**

- Check `.env` file exists and has credentials
- Verify `GENYMOTION_USERNAME` and `GENYMOTION_PASSWORD` are set

#### **"Docker build fails"**

- Ensure Docker daemon is running
- Check available disk space
- Verify Dockerfile syntax

#### **"Evaluation script not found"**

- Ensure you're in the correct directory
- Check if `./agents/evaluate.sh` exists and is executable

---

## ✅ **Verification Checklist**

### **Goal 1: Infrastructure & Deployment**

- [ ] **Docker container builds successfully** (`docker build -t candidate/android-world .`)
- [ ] **Device creation works** (`./infra/create_devices.sh`)
- [ ] **Docker container runs** (`docker run --env-file .env candidate/android-world`)

### **Goal 2: Agent Integration & Evaluation**

- [ ] **Agent system works** (evaluation script runs successfully)
- [ ] **Genymotion Cloud integration works** (authentication successful)
- [ ] **Evaluation pipeline runs** (`./agents/evaluate.sh --episodes 50`)
- [ ] **Results are generated** (JSON files in `agents/results/`)
- [ ] **Reports are generated** (Markdown files in `agents/reports/`)

### **Challenge Compliance**

- [ ] **agents/ directory structure** matches requirements
- [ ] **evaluate.sh script** runs N episodes and aggregates metrics
- [ ] **Machine-readable output** (JSON/CSV) is generated
- [ ] **Human-readable output** (Markdown) is generated
- [ ] **End-to-end workflow** functions from agent → emulator → results

### **Goal 3 Compliance**

- [ ] **Kubernetes manifests** with HPA for autoscaling
- [ ] **CI/CD pipeline** with GitHub Actions (tests, build, deploy, smoke tests)
- [ ] **Observability & tracing** with Google Cloud integration
- [ ] **Load testing** with k6 and performance reporting
- [ ] **Production deployment** with staging and production environments

---

## 🎉 **Success Criteria**

If all verification steps pass, the project has successfully met the challenge requirements:

- **Goal 1**: Infrastructure & Deployment ✅
- **Goal 2**: Agent Integration & Evaluation ✅
- **Goal 3**: Scaling, Observability & Reliability ✅
- **Challenge Compliance**: All deliverables met ✅

**The project is now production-ready with enterprise-grade scaling, observability, and reliability!** 🚀✨

---

## 📁 **Project Structure**

```
qualgent-challenge/
├── agents/                    # Agent system and evaluation
│   ├── __init__.py           # Package initialization
│   ├── base_agent.py         # Abstract base agent class
│   ├── task_generator.py     # Task generation logic
│   ├── task_executor.py      # Task execution logic
│   ├── orchestrator.py       # Agent coordination
│   ├── evaluate.sh           # Main evaluation script
│   ├── results/              # Generated evaluation results
│   └── reports/              # Generated evaluation reports
├── infra/                    # Infrastructure and deployment
│   ├── create_devices.sh     # Device creation script
│   ├── deploy-cloud.sh       # Cloud deployment script
│   ├── genymotion_cloud_working.py  # Genymotion Cloud integration
│   └── vertex_ai_integration.py     # Vertex AI integration
├── Dockerfile                # Container definition
├── run.sh                    # Main execution script
├── requirements.txt           # Python dependencies
├── .env                      # Environment configuration (create from env.example)
├── env.example               # Environment template
└── README.md                 # This comprehensive guide
```

---

## 🚀 **Next Steps for Evaluators**

1. **Follow the exact challenge steps** above
2. **Verify each component works** using the checklist
3. **Check generated results and reports** for quality
4. **Confirm end-to-end workflow** functions correctly
5. **Deploy Goal 3 features** using the deployment guide

**For questions or issues, refer to the troubleshooting section above.**

## 📚 **Additional Documentation**

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete Goal 3 deployment guide
- **[k8s/](k8s/)**: Kubernetes manifests for production deployment
- **[.github/workflows/](.github/workflows/)**: CI/CD pipeline configuration
- **[load-testing/](load-testing/)**: Load testing scripts and configuration
