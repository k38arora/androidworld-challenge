#!/bin/bash

# Cloud Deployment Script for Genymotion Android Emulators
# This script provisions infrastructure on Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
ZONE=${GOOGLE_CLOUD_ZONE:-"us-central1-a"}
INSTANCE_NAME="genymotion-emulator"
MACHINE_TYPE="n1-standard-4"
DISK_SIZE="50GB"

echo -e "${GREEN}🚀 Starting Cloud Deployment for Genymotion Emulators${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ Google Cloud CLI not found. Please install it first.${NC}"
        exit 1
    fi
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${RED}❌ Not authenticated with Google Cloud. Please run 'gcloud auth login' first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Enabling required Google Cloud APIs...${NC}"
    
    gcloud services enable compute.googleapis.com
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable container.googleapis.com
    
    echo -e "${GREEN}✅ APIs enabled successfully${NC}"
}

# Create compute instance for Genymotion
create_compute_instance() {
    echo -e "${YELLOW}🖥️  Creating compute instance for Genymotion...${NC}"
    
    # Check if instance already exists
    if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null; then
        echo -e "${YELLOW}⚠️  Instance $INSTANCE_NAME already exists. Skipping creation.${NC}"
        return
    fi
    
    gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=$DISK_SIZE \
        --boot-disk-type=pd-ssd \
        --tags=genymotion \
        --metadata=startup-script='#!/bin/bash
            # Update system
            apt-get update
            apt-get install -y wget curl unzip
            
            # Install Docker
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            usermod -aG docker $USER
            
            # Install Genymotion
            wget -O genymotion.bin https://dl.genymotion.com/releases/genymotion-3.5.0/genymotion-3.5.0-linux_x64.bin
            chmod +x genymotion.bin
            ./genymotion.bin --yes
            
            # Install Android SDK and ADB
            apt-get install -y android-tools-adb
            
            # Create startup script
            cat > /usr/local/bin/start-genymotion.sh << "EOF"
            #!/bin/bash
            export DISPLAY=:0
            /opt/genymotion/genymotion &
            sleep 10
            adb start-server
            EOF
            
            chmod +x /usr/local/bin/start-genymotion.sh'
    
    echo -e "${GREEN}✅ Compute instance created successfully${NC}"
}

# Configure firewall rules
configure_firewall() {
    echo -e "${YELLOW}🔥 Configuring firewall rules...${NC}"
    
    # Create firewall rule for ADB (port 5555)
    gcloud compute firewall-rules create genymotion-adb \
        --allow tcp:5555 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=genymotion \
        --description="Allow ADB connections to Genymotion emulators"
    
    # Create firewall rule for VNC (port 5900)
    gcloud compute firewall-rules create genymotion-vnc \
        --allow tcp:5900 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=genymotion \
        --description="Allow VNC connections to Genymotion emulators"
    
    echo -e "${GREEN}✅ Firewall rules configured${NC}"
}

# Get instance details
get_instance_info() {
    echo -e "${YELLOW}📊 Getting instance information...${NC}"
    
    INSTANCE_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format="value(networkInterfaces[0].accessConfigs[0].natIP)")
    
    echo -e "${GREEN}✅ Instance created successfully!${NC}"
    echo -e "${GREEN}🌐 Instance IP: $INSTANCE_IP${NC}"
    echo -e "${GREEN}🔗 SSH Command: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE${NC}"
    echo -e "${GREEN}📱 ADB Connect: adb connect $INSTANCE_IP:5555${NC}"
}

# Main deployment function
main() {
    check_prerequisites
    enable_apis
    create_compute_instance
    configure_firewall
    get_instance_info
    
    echo -e "${GREEN}🎉 Cloud deployment completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Wait a few minutes for the instance to fully initialize"
    echo "2. SSH into the instance: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
    echo "3. Start Genymotion: sudo /usr/local/bin/start-genymotion.sh"
    echo "4. Connect from your local machine: adb connect $INSTANCE_IP:5555"
}

# Run main function
main "$@"
