#!/usr/bin/env python3
"""
Test Genymotion Cloud Integration (Demo Mode)

This script demonstrates how Genymotion Cloud integration works
without requiring actual credentials.
"""

import os
import json
from typing import Dict, Any, Optional, List


class MockGenymotionCloudManager:
    """Mock Genymotion Cloud Manager for demonstration"""

    def __init__(self):
        self.api_url = "https://cloud.geny.io/api/v1"
        print("🔧 Mock Genymotion Cloud Manager initialized")
        print("   (This is a demo - replace with real credentials)")

    def authenticate(self) -> bool:
        """Mock authentication"""
        print("✅ Mock authentication successful")
        print("   In real usage, this would authenticate with Genymotion Cloud")
        return True

    def list_device_templates(self) -> List[Dict[str, Any]]:
        """Mock device templates"""
        templates = [
            {
                "uuid": "mock-uuid-1",
                "name": "Google Pixel 4",
                "android_version": "11.0",
                "description": "High-performance Android device",
            },
            {
                "uuid": "mock-uuid-2",
                "name": "Samsung Galaxy S21",
                "android_version": "12.0",
                "description": "Premium Samsung device",
            },
            {
                "uuid": "mock-uuid-3",
                "name": "OnePlus 9",
                "android_version": "11.0",
                "description": "Fast and smooth performance",
            },
        ]

        print(f"📱 Found {len(templates)} device templates:")
        for template in templates:
            print(f"   - {template['name']} (Android {template['android_version']})")

        return templates

    def create_instance(
        self, template_name: str, instance_name: str
    ) -> Optional[Dict[str, Any]]:
        """Mock instance creation"""
        print(f"✅ Mock instance '{instance_name}' created successfully")
        print(f"   Using template: {template_name}")

        instance = {
            "uuid": "mock-instance-uuid",
            "name": instance_name,
            "state": "creating",
            "adb_tunnel_public_host": "mock-host.geny.io",
            "adb_tunnel_public_port": 5555,
        }

        return instance

    def wait_for_instance(
        self, instance_uuid: str, timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Mock instance waiting"""
        print(f"⏳ Mock instance {instance_uuid} is starting...")
        print("   In real usage, this would wait for the instance to be online")

        instance = {
            "uuid": instance_uuid,
            "state": "online",
            "adb_tunnel_public_host": "mock-host.geny.io",
            "adb_tunnel_public_port": 5555,
        }

        print("✅ Mock instance is now online!")
        return instance

    def get_adb_connection_info(self, instance_uuid: str) -> Optional[Dict[str, str]]:
        """Mock ADB connection info"""
        adb_info = {
            "host": "mock-host.geny.io",
            "port": "5555",
            "internal_host": "10.0.0.1",
            "internal_port": "5555",
        }

        print(f"🔗 Mock ADB connection: {adb_info['host']}:{adb_info['port']}")
        print("   In real usage, you would connect using:")
        print(f"   adb connect {adb_info['host']}:{adb_info['port']}")

        return adb_info

    def list_instances(self) -> List[Dict[str, Any]]:
        """Mock instances list"""
        instances = [
            {"uuid": "mock-uuid-1", "name": "AndroidWorld-Test-1", "state": "online"},
            {"uuid": "mock-uuid-2", "name": "AndroidWorld-Test-2", "state": "creating"},
        ]

        print(f"📱 Found {len(instances)} mock instances:")
        for instance in instances:
            print(f"   - {instance['name']} ({instance['uuid']}): {instance['state']}")

        return instances


def demonstrate_integration():
    """Demonstrate the complete Genymotion Cloud integration flow"""

    print("🚀 Genymotion Cloud Integration Demo")
    print("=" * 50)

    # Initialize manager
    manager = MockGenymotionCloudManager()

    # Step 1: Authenticate
    print("\n🔐 Step 1: Authentication")
    if not manager.authenticate():
        print("❌ Authentication failed")
        return

    # Step 2: List available templates
    print("\n📱 Step 2: Device Templates")
    templates = manager.list_device_templates()

    # Step 3: Create an instance
    print("\n🔧 Step 3: Create Instance")
    instance = manager.create_instance("Google Pixel 4", "AndroidWorld-Test-Device")

    if instance:
        # Step 4: Wait for instance to be ready
        print("\n⏳ Step 4: Wait for Instance")
        ready_instance = manager.wait_for_instance(instance["uuid"])

        if ready_instance:
            # Step 5: Get ADB connection info
            print("\n🔗 Step 5: ADB Connection")
            adb_info = manager.get_adb_connection_info(ready_instance["uuid"])

            # Step 6: List all instances
            print("\n📋 Step 6: Instance Management")
            manager.list_instances()

            print("\n🎯 Integration Demo Complete!")
            print("=" * 50)
            print("To use real Genymotion Cloud:")
            print("1. Set GENYMOTION_USERNAME, GENYMOTION_PASSWORD in .env")
            print("2. Replace MockGenymotionCloudManager with GenymotionCloudManager")
            print("3. Run: ./infra/create_devices.sh")
        else:
            print("❌ Instance failed to start")
    else:
        print("❌ Failed to create instance")


if __name__ == "__main__":
    demonstrate_integration()
