import os
import uuid

from django.utils.deconstruct import deconstructible


@deconstructible
class SecureUploadTo:
    """
    Generate randomized, UUID-based filenames to prevent collisions and Path Traversal attacks.
    """

    def __init__(self, sub_dir: str):
        self.sub_dir = sub_dir

    def __call__(self, instance, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return os.path.join(self.sub_dir, unique_name)
