import os
from io import BytesIO

import aiofiles
import aiofiles.os
from PIL import Image


class DiskManager:

    DISK_BASE_FOLDERS = [
        "media",
        "media/images",
        "media/videos",
        "media/images/collections",
        "media/images/sub-collections",
        "media/images/products",
    ]

    COLLECTIONS_SAVE_PATH = "media/images/collections/"
    SUB_COLLECTIONS_SAVE_PATH = "media/images/sub-collections/"
    PRODUCTS_SAVE_PATH = "media/images/products/"

    @classmethod
    async def create_folder(cls, folder_path: str) -> None:
        await aiofiles.os.makedirs(folder_path, exist_ok=True)
        print(f"Created/Verified folder {folder_path}")

    @classmethod
    async def create_application_folders(cls):
        for item in cls.DISK_BASE_FOLDERS:
            await cls.create_folder(item)

    @staticmethod
    def image_title_webp_convertor_for_route(image_path: str):
        formatted_name = os.path.splitext(image_path.split("/")[-1])
        formatted_path = image_path.split("/")[0:-1]
        filename = f"{formatted_name[0]}.webp"
        formatted_path.append(filename)

        formatted_image = "/".join(formatted_path)
        print(formatted_image)
        return formatted_image

    @staticmethod
    def image_processor_for_route(
        image_file: bytes,
        width: int = 1024,
        height: int = 1024,
        quality: int = 90,
    ):
        original_image = Image.open(BytesIO(image_file))

        if original_image.width > width or original_image.height > height:
            original_image.thumbnail((width, height))

        if original_image.mode in ("RGBA", "LA", "P"):
            original_image.convert("RGBA")

        buffer = BytesIO()
        original_image.save(buffer, format="WEBP", quality=quality, optimized=True)
        buffer.seek(0)

        return buffer.getvalue()

    @staticmethod
    def upload_image_for_route(image_file, image_path: str):
        with open(image_path, "wb") as f:
            f.write(image_file)
