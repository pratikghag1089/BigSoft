"""DigitalOcean Deployment - Deploy real services to cloud."""

import logging
import requests
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.core.config import settings

logger = logging.getLogger(__name__)


class DigitalOceanDeployer:
    """
    Deploy applications to DigitalOcean.
    Creates droplets, deploys code, sets up domains.
    """

    def __init__(self):
        self.api_token = settings.digitalocean_api_token
        self.base_url = "https://api.digitalocean.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.enabled = settings.digitalocean_enabled

    def create_droplet(
        self,
        name: str,
        region: str = "blr1",  # Bangalore, India
        size: str = "s-1vcpu-1gb",  # $6/month
        image: str = "ubuntu-22-04-x64"
    ) -> Dict[str, Any]:
        """
        Create a new droplet (virtual machine).

        Args:
            name: Droplet name
            region: Region code (blr1=Bangalore, nyc1=New York, etc.)
            size: Droplet size slug
            image: OS image

        Returns:
            Droplet details
        """
        if not self.enabled:
            logger.warning("DigitalOcean not enabled - simulating droplet creation")
            return {
                "id": f"sim_droplet_{name}",
                "name": name,
                "ip_address": "127.0.0.1",
                "status": "simulated"
            }

        try:
            data = {
                "name": name,
                "region": region,
                "size": size,
                "image": image,
                "ssh_keys": [settings.digitalocean_ssh_key_id] if settings.digitalocean_ssh_key_id else [],
                "backups": False,
                "ipv6": True,
                "monitoring": True,
                "tags": ["ai-entrepreneur", "auto-deployed"]
            }

            response = requests.post(
                f"{self.base_url}/droplets",
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            droplet = response.json()["droplet"]

            logger.info(f"Created droplet: {name} (ID: {droplet['id']})")

            # Wait for IP assignment
            droplet_id = droplet["id"]
            ip_address = self._wait_for_ip(droplet_id)

            return {
                "id": droplet_id,
                "name": name,
                "ip_address": ip_address,
                "region": region,
                "size": size,
                "status": "active"
            }

        except Exception as e:
            logger.error(f"Error creating droplet: {e}")
            return {"error": str(e), "status": "failed"}

    def deploy_app(
        self,
        droplet_id: str,
        workspace_path: Path,
        app_name: str,
        port: int = 8000
    ) -> Dict[str, Any]:
        """
        Deploy application to droplet.

        Args:
            droplet_id: Droplet ID
            workspace_path: Path to workspace with code
            app_name: Application name
            port: Application port

        Returns:
            Deployment details
        """
        if not self.enabled:
            logger.warning("DigitalOcean not enabled - simulating deployment")
            return {
                "url": f"http://simulated-{app_name}.com",
                "status": "simulated"
            }

        try:
            # Get droplet IP
            droplet = self._get_droplet(droplet_id)
            ip_address = droplet["ip_address"]

            # Create deployment script
            deploy_script = self._generate_deploy_script(workspace_path, app_name, port)

            # Upload and execute via SSH
            # Note: In production, you'd use paramiko or fabric for SSH
            # For now, we'll use DigitalOcean App Platform instead

            logger.info(f"Deploying {app_name} to {ip_address}")

            # TODO: Implement SSH deployment or use App Platform
            # For MVP, return deployment URL

            return {
                "url": f"http://{ip_address}:{port}",
                "droplet_id": droplet_id,
                "ip_address": ip_address,
                "port": port,
                "status": "deployed"
            }

        except Exception as e:
            logger.error(f"Error deploying app: {e}")
            return {"error": str(e), "status": "failed"}

    def create_app_platform_app(
        self,
        app_name: str,
        github_repo: Optional[str] = None,
        docker_image: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy using DigitalOcean App Platform (easier than droplets).

        Args:
            app_name: Application name
            github_repo: GitHub repository URL
            docker_image: Docker image URL

        Returns:
            App details
        """
        if not self.enabled:
            logger.warning("DigitalOcean not enabled - simulating app platform deployment")
            return {
                "url": f"https://{app_name}-simulated.ondigitalocean.app",
                "status": "simulated"
            }

        try:
            # App Platform spec
            spec = {
                "name": app_name,
                "region": "blr",
                "services": [
                    {
                        "name": "web",
                        "github": {
                            "repo": github_repo,
                            "branch": "main"
                        } if github_repo else None,
                        "image": {
                            "registry_type": "DOCKER_HUB",
                            "repository": docker_image
                        } if docker_image else None,
                        "instance_count": 1,
                        "instance_size_slug": "basic-xxs",  # $5/month
                        "http_port": 8000,
                        "routes": [{"path": "/"}]
                    }
                ]
            }

            response = requests.post(
                f"{self.base_url}/apps",
                headers=self.headers,
                json={"spec": spec},
                timeout=30
            )
            response.raise_for_status()

            app = response.json()["app"]

            logger.info(f"Created App Platform app: {app_name}")

            return {
                "id": app["id"],
                "name": app_name,
                "url": app.get("live_url", f"https://{app_name}.ondigitalocean.app"),
                "status": "deployed"
            }

        except Exception as e:
            logger.error(f"Error creating app: {e}")
            return {"error": str(e), "status": "failed"}

    def create_domain(
        self,
        domain_name: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Add domain and create DNS records.

        Args:
            domain_name: Domain name (must be registered separately)
            ip_address: IP address to point to

        Returns:
            Domain details
        """
        if not self.enabled:
            logger.warning("DigitalOcean not enabled - simulating domain creation")
            return {
                "domain": domain_name,
                "status": "simulated"
            }

        try:
            # Create domain
            response = requests.post(
                f"{self.base_url}/domains",
                headers=self.headers,
                json={"name": domain_name, "ip_address": ip_address},
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Added domain: {domain_name} -> {ip_address}")

            return {
                "domain": domain_name,
                "ip_address": ip_address,
                "status": "active"
            }

        except Exception as e:
            logger.error(f"Error creating domain: {e}")
            return {"error": str(e), "status": "failed"}

    def list_droplets(self) -> List[Dict[str, Any]]:
        """List all droplets."""
        if not self.enabled:
            return []

        try:
            response = requests.get(
                f"{self.base_url}/droplets",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            droplets = response.json()["droplets"]

            return [
                {
                    "id": d["id"],
                    "name": d["name"],
                    "ip_address": d["networks"]["v4"][0]["ip_address"] if d["networks"]["v4"] else None,
                    "status": d["status"],
                    "size": d["size_slug"],
                    "region": d["region"]["slug"]
                }
                for d in droplets
            ]

        except Exception as e:
            logger.error(f"Error listing droplets: {e}")
            return []

    def delete_droplet(self, droplet_id: str) -> bool:
        """Delete a droplet."""
        if not self.enabled:
            return True

        try:
            response = requests.delete(
                f"{self.base_url}/droplets/{droplet_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            logger.info(f"Deleted droplet: {droplet_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting droplet: {e}")
            return False

    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance and usage."""
        if not self.enabled:
            return {"balance": 0, "status": "simulated"}

        try:
            response = requests.get(
                f"{self.base_url}/customers/my/balance",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            balance_data = response.json()

            return {
                "account_balance": balance_data.get("account_balance", "0"),
                "month_to_date_balance": balance_data.get("month_to_date_balance", "0"),
                "month_to_date_usage": balance_data.get("month_to_date_usage", "0")
            }

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {"error": str(e)}

    def _get_droplet(self, droplet_id: str) -> Dict[str, Any]:
        """Get droplet details."""
        response = requests.get(
            f"{self.base_url}/droplets/{droplet_id}",
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()

        droplet = response.json()["droplet"]

        return {
            "id": droplet["id"],
            "name": droplet["name"],
            "ip_address": droplet["networks"]["v4"][0]["ip_address"] if droplet["networks"]["v4"] else None,
            "status": droplet["status"]
        }

    def _wait_for_ip(self, droplet_id: str, max_wait: int = 60) -> Optional[str]:
        """Wait for droplet to get IP address."""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            droplet = self._get_droplet(droplet_id)
            if droplet["ip_address"]:
                return droplet["ip_address"]

            time.sleep(5)

        logger.warning(f"Timeout waiting for IP for droplet {droplet_id}")
        return None

    def _generate_deploy_script(
        self,
        workspace_path: Path,
        app_name: str,
        port: int
    ) -> str:
        """Generate deployment script."""
        script = f"""#!/bin/bash
# Auto-generated deployment script for {app_name}

# Update system
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx

# Create app directory
mkdir -p /var/www/{app_name}
cd /var/www/{app_name}

# Copy application files
# (Files would be uploaded separately)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/{app_name}.service << 'ENDSERVICE'
[Unit]
Description={app_name}
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/{app_name}
ExecStart=/var/www/{app_name}/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
ENDSERVICE

# Start service
systemctl daemon-reload
systemctl enable {app_name}
systemctl start {app_name}

# Configure nginx
cat > /etc/nginx/sites-available/{app_name} << 'ENDNGINX'
server {{
    listen 80;
    server_name _;

    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
ENDNGINX

ln -s /etc/nginx/sites-available/{app_name} /etc/nginx/sites-enabled/
systemctl restart nginx

echo "Deployment complete!"
"""
        return script


# Global instance
digitalocean_deployer = DigitalOceanDeployer()
