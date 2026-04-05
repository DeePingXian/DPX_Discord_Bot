import aioboto3
import logging
import hashlib
import os
import re
from botocore.exceptions import ClientError

class StorageService:
    """S3/MinIO Object Storage Management Service with Cloudflare Tunnel support"""
    
    def __init__(self, endpoint, access_key, secret_key, bucket_name):
        self.session = aioboto3.Session()
        self.internal_endpoint = f"http://{endpoint}"
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.public_url = None # Dynamically updated by DPX_Discord_Bot.py
        self.logger = logging.getLogger("Storage")

    async def _ensure_bucket_and_lifecycle(self, s3_client):
        """Ensure the target bucket exists and has a 30-day retention policy."""
        try:
            # 1. Check/Create Bucket
            try:
                await s3_client.head_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    self.logger.info(f"Bucket {self.bucket_name} not found. Creating...")
                    await s3_client.create_bucket(Bucket=self.bucket_name)
                else: raise

            # 2. Set Lifecycle Policy (Auto-delete after 30 days)
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'AutoDeleteOldMessages',
                        'Status': 'Enabled',
                        'Prefix': '', # Apply to all objects
                        'Expiration': {
                            'Days': 30
                        }
                    }
                ]
            }
            await s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            self.logger.info(f"S3 Lifecycle policy set: 30 days retention for {self.bucket_name}")

        except Exception as e:
            self.logger.error(f"Failed to configure S3 bucket/lifecycle: {e}")

    def refresh_public_url(self, log_path="/app/tunnel/cloudflared.log"):
        """Extract the trycloudflare.com URL from the tunnel log file."""
        if not os.path.exists(log_path):
            return None
        
        try:
            with open(log_path, "r") as f:
                content = f.read()
                urls = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                if urls:
                    new_url = urls[-1]
                    if new_url != self.public_url:
                        self.public_url = new_url
                        self.logger.info(f"Public S3 URL updated: {self.public_url}")
                    return self.public_url
        except Exception as e:
            self.logger.error(f"Failed to read tunnel log: {e}")
        return None

    async def exists(self, s3_key):
        """Check if an object exists in the bucket."""
        async with self.session.client(
            's3',
            endpoint_url=self.internal_endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1"
        ) as s3:
            try:
                await s3.head_object(Bucket=self.bucket_name, Key=s3_key)
                return True
            except ClientError:
                return False

    async def upload_file(self, file_data, original_name):
        """Upload file using INTERNAL endpoint"""
        file_hash = hashlib.sha256(file_data).hexdigest()
        file_ext = original_name.split('.')[-1] if '.' in original_name else ''
        s3_key = f"files/{file_hash[:2]}/{file_hash}.{file_ext}"

        async with self.session.client(
            's3',
            endpoint_url=self.internal_endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1"
        ) as s3:
            await self._ensure_bucket_and_lifecycle(s3)
            try:
                await s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            except ClientError:
                await s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=file_data)
                self.logger.info(f"File uploaded successfully: {s3_key}")

        return file_hash, s3_key

    async def get_download_url(self, s3_key, expires_in=3600):
        """Generate download URL using PUBLIC endpoint if available"""
        target_endpoint = self.public_url if self.public_url else self.internal_endpoint
        
        async with self.session.client(
            's3',
            endpoint_url=target_endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name="us-east-1"
        ) as s3:
            return await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
