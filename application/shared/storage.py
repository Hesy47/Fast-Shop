import aiofiles
import aiofiles.os
from fastapi import UploadFile


class DiskManager:

    DISK_BASE_FOLDERS = ["media", "media/images", "media/videos"]

    @classmethod
    async def create_folder(cls, folder_path: str) -> None:
        await aiofiles.os.makedirs(folder_path, exist_ok=True)
        print(f"Created/Verified folder {folder_path}")

    @classmethod
    async def create_application_folders(cls):
        for item in cls.DISK_BASE_FOLDERS:
            await cls.create_folder(item)

    @classmethod
    async def upload_image(image_file: UploadFile):
        pass
