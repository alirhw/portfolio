import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Maximum allowed file sizes
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_SIZE = 3 * 1024 * 1024  # 3 MB

# Standard binary signatures (Magic Numbers)
PDF_MAGIC_BYTES = b"%PDF-"
PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC_BYTES = b"\xff\xd8\xff"
WEBP_MAGIC_PREFIX = b"RIFF"


def validate_resume_file(file_obj) -> None:
    """
    Validate resume file upload:
    1. Allowed extension (.pdf)
    2. File size ceiling (5 MB)
    3. Binary magic byte signature (%PDF-)
    """
    # 1. Check extension
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext != ".pdf":
        raise ValidationError(_("Only PDF files are allowed for resume uploads."))

    # 2. Check file size
    if file_obj.size > MAX_RESUME_SIZE:
        raise ValidationError(
            _("Resume file size cannot exceed %(max_size)s MB.") % {"max_size": 5}
        )

    # 3. Check binary magic signature
    if hasattr(file_obj, "seek") and hasattr(file_obj, "read"):
        file_obj.seek(0)
        header = file_obj.read(10)
        file_obj.seek(0)

        if not header.startswith(PDF_MAGIC_BYTES):
            raise ValidationError(_("Invalid PDF file header/content detected."))


def validate_image_file(file_obj) -> None:
    """
    Validate project image upload:
    1. Allowed extensions (.jpg, .jpeg, .png, .webp)
    2. File size ceiling (3 MB)
    3. Binary magic byte signature
    """
    allowed_exts = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext not in allowed_exts:
        raise ValidationError(_("Unsupported image format. Allowed formats: JPG, PNG, WEBP."))

    if file_obj.size > MAX_IMAGE_SIZE:
        raise ValidationError(_("Image size cannot exceed %(max_size)s MB.") % {"max_size": 3})

    if hasattr(file_obj, "seek") and hasattr(file_obj, "read"):
        file_obj.seek(0)
        header = file_obj.read(16)
        file_obj.seek(0)

        is_valid_image = (
            header.startswith(JPEG_MAGIC_BYTES)
            or header.startswith(PNG_MAGIC_BYTES)
            or (header.startswith(WEBP_MAGIC_PREFIX) and b"WEBP" in header)
        )

        if not is_valid_image:
            raise ValidationError(_("Invalid or corrupted image binary signature."))
