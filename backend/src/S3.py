import aioboto3
from botocore.exceptions import ClientError
from botocore.config import Config

from src.core.config import settings
from src.logger import logger



class MyAsyncS3Client:
    def __init__(self, endpoint_url: str, access_key_id: str, access_secret: str, bucket_name: str, save_file_url : str):
        self.endpoint_url = endpoint_url
        self.save_file_url = save_file_url
        self.access_key_id = access_key_id
        self.access_secret = access_secret
        self.bucket_name = bucket_name
        self.session = aioboto3.Session()
        self.s3_client = None

    async def connect(self):
        # Создаем асинхронный клиент
        self.s3_client = await self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.access_secret,
            config=Config(signature_version='s3')
        ).__aenter__()

    async def close(self):
        if self.s3_client:
            await self.s3_client.__aexit__(None, None, None)

    async def download_file(self, s3_path: str, local_path: str)  -> dict:
        if not local_path.exists():
            logger.exception("Local file does not exist. Path: %s" % local_path)
            return {
                "ok": False,
                "message": "Local file does not exist"
            }
        try:
            await self.s3_client.download_file(self.bucket_name, s3_path, str(local_path))
        except ClientError:
            logger.exception("Error in download file on S3. bucket_path: %s , local_path: %s" % (s3_path, local_path))
            return {
                "ok": False,
                "message": "File not found"
            }
        else:
            logger.info("Success download file bucket_path: %s , local_path: %s" % (s3_path, local_path))
            return {
                "ok": True,
                "message": None
            }
        
    async def upload_file(self, local_path: str, s3_path: str)  -> dict:
        try:
            await self.s3_client.upload_file(str(local_path), self.bucket_name, s3_path)
        except ClientError:
            logger.exception("Error uploading file to S3. Local path: %s , s3 path: %s" % (local_path, s3_path))
            return {
                "ok": False,
                "message": "Failed to upload file",
                "url" : None
            }
        else:
            file_url = f"{self.save_file_url}/{s3_path}"
            logger.info("Successfully uploaded file to s3. Local path: %s , s3 path: %s" % (local_path, s3_path))
            return {
                "ok": True,
                "message": None,
                "url" : file_url
            }
    

    async def delete_file(self, s3_path: str) -> dict:
        try:
            await self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_path)
        except ClientError:
            logger.exception("Error deleting file from S3. Path in bucket: %s" % s3_path)
            return {
                "ok": False,
                "message": "Failed to delete file"
            }
        else:
            logger.info("Successfully deleted file from S3. Path in bucket: %s" % s3_path)
            return {
                "ok": True,
                "message": None
            }
        
    
    async def file_exists(self, s3_path: str) -> bool:
        try:
            await self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise
    
    

s3_client = MyAsyncS3Client(
        settings.S3.url,
        settings.S3.access_id,
        settings.S3.secret_key,
        settings.S3.bucket_name,
        settings.S3.save_file_url
    )