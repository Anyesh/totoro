import uuid
from io import BytesIO

from django.core.files import File
from django.core.files.base import ContentFile
from PIL import Image


def resize(image, size: tuple):
    im = Image.open(image)  # Catch original
    source_image = im.convert("RGB")
    source_image.thumbnail(size)  # Resize to size
    output = BytesIO()
    source_image.save(output, format="JPEG")  # Save resize image to bytes
    output.seek(0)

    content_file = ContentFile(
        output.read()
    )  # Read output and create ContentFile in memory
    file = File(content_file)

    random_name = f"{uuid.uuid4()}.jpeg"
    return random_name, file
