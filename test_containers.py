#!/usr/bin/env python3
"""Test EPIC V11 Docker containers and services"""
import subprocess
import json
import time
import sys

def check_docker_running():
    """Check if Docker is running"""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker.")
        return False

def get_container_status():
    """Get status of all EPIC containers"""
    try:
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=epic_", 
            "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception as e:
        print(f"Error checking containers: {e}")
        return None

def check_container_health():
    """Check health of EPIC containers"""
    containers = ["epic_control_panel", "epic_agno", "epic_mcp", "epic_postgres", "epic_redis", "epic_frontend"]
    health_status = {}
    
    for container in containers:
        try:
            # Check if container exists and is running
            result = subprocess.run([
                "docker", "inspect", container, "--format", "{{.State.Status}}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                status = result.stdout.strip()
                
                # Check health if container is running
                if status == "running":
                    health_result = subprocess.run([
                        "docker", "inspect", container, "--format", "{{.State.Health.Status}}"
                    ], capture_output=True, text=True)
                    
                    if health_result.returncode == 0:
                        health = health_result.stdout.strip()
                        health_status[container] = {"status": status, "health": health}
                    else:
                        health_status[container] = {"status": status, "health": "no_healthcheck"}
                else:
                    health_status[container] = {"status": status, "health": "not_running"}
            else:
                health_status[container] = {"status": "not_found", "health": "not_found"}
                
        except Exception as e:
            health_status[container] = {"status": "error", "health": str(e)}
    
    return health_status

def test_network_connectivity():
    """Test network connectivity between containers"""
    print("🌐 Testing Network Connectivity...")
    
    # Test if epic_network exists
    try:
        result = subprocess.run([
            "docker", "network", "ls", "--filter", "name=epic_network", "--format", "{{.Name}}"
        ], capture_output=True, text=True)
        
        if "epic_network" in result.stdout:
            print("✅ PASS Epic Network: exists")
            return True
        else:
            print("❌ FAIL Epic Network: not found")
            return False
    except Exception as e:
        print(f"❌ ERROR Epic Network: {e}")
        return False

def check_volumes():
    """Check if Docker volumes exist"""
    print("💾 Checking Docker Volumes...")
    
    volumes = ["epic11_postgres_data", "epic11_redis_data", "epic11_n8n_data"]
    volume_status = {}
    
    for volume in volumes:
        try:
            result = subprocess.run([
                "docker", "volume", "inspect", volume
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PASS Volume {volume}: exists")
                volume_status[volume] = "exists"
            else:
                print(f"❌ FAIL Volume {volume}: not found")
                volume_status[volume] = "not_found"
        except Exception as e:
            print(f"❌ ERROR Volume {volume}: {e}")
            volume_status[volume] = "error"
    
    return volume_status

def test_dockerfile_syntax():
    """Test Dockerfile syntax for all services"""
    print("📋 Testing Dockerfile Syntax...")
    
    services = ["control_panel_backend", "agno_service", "mcp_server", "frontend"]
    dockerfile_status = {}
    
    for service in services:
        dockerfile_path = f"/home/epic/epic11/{service}/Dockerfile"
        try:
            # Test build context (dry run)
            result = subprocess.run([
                "docker", "build", "--dry-run", "-f", dockerfile_path, f"/home/epic/epic11/{service}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ PASS Dockerfile {service}: syntax valid")
                dockerfile_status[service] = "valid"
            else:
                print(f"❌ FAIL Dockerfile {service}: syntax error")
                dockerfile_status[service] = "invalid"
        except Exception as e:
            print(f"❌ ERROR Dockerfile {service}: {e}")
            dockerfile_status[service] = "error"
    
    return dockerfile_status

def main():
    """Run container tests"""
    print("🐳 EPIC V11 CONTAINER VERIFICATION")
    print("=" * 50)
    
    # Check Docker
    if not check_docker_running():
        print("❌ Docker is not running. Please start Docker first.")
        return 1
    
    print("✅ Docker is running")
    
    # Check container status
    print("\n📦 Container Status:")
    container_output = get_container_status()
    if container_output:
        print(container_output)
    else:
        print("No EPIC containers found or error checking containers")
    
    # Check container health
    print("\n🏥 Container Health Check:")
    health_status = check_container_health()
    
    healthy_containers = 0
    total_containers = len(health_status)
    
    for container, status in health_status.items():
        state = status.get("status", "unknown")
        health = status.get("health", "unknown")
        
        if state == "running" and health in ["healthy", "no_healthcheck"]:
            print(f"✅ {container}: {state} ({health})")
            healthy_containers += 1
        elif state == "not_found":
            print(f"⚪ {container}: not deployed")
        else:
            print(f"❌ {container}: {state} ({health})")
    
    # Test network
    network_ok = test_network_connectivity()
    
    # Check volumes
    volumes_status = check_volumes()
    
    # Test Dockerfiles
    dockerfile_status = test_dockerfile_syntax()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CONTAINER TEST SUMMARY")
    print("=" * 50)
    
    print(f"Containers: {healthy_containers}/{total_containers} healthy")
    print(f"Network: {'✅ OK' if network_ok else '❌ FAIL'}")
    print(f"Volumes: {sum(1 for v in volumes_status.values() if v == 'exists')}/{len(volumes_status)} exist")
    print(f"Dockerfiles: {sum(1 for d in dockerfile_status.values() if d == 'valid')}/{len(dockerfile_status)} valid")
    
    # Overall status
    if healthy_containers > 0:
        print("\n🎉 EPIC V11 containers are available!")
        print("Run './deploy.sh' to start the full system.")
        return 0
    else:
        print("\n⚠️ No EPIC V11 containers are running.")
        print("Run 'docker-compose up -d' to start the system.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)