import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.storage import SecureUploadTo
from apps.core.validators import validate_image_file, validate_resume_file


def test_valid_pdf_file_passes_validation():
    valid_pdf_content = b"%PDF-1.5 \x00\x01\x02 test resume body"
    file_obj = SimpleUploadedFile("cv.pdf", valid_pdf_content, content_type="application/pdf")

    # Should not raise any validation errors
    validate_resume_file(file_obj)


def test_fake_pdf_with_invalid_header_raises_validation_error():
    # File with .pdf extension but malicious HTML content (MIME spoofing)
    fake_pdf_content = b"<html><script>alert(1)</script></html>"
    file_obj = SimpleUploadedFile("malicious.pdf", fake_pdf_content, content_type="application/pdf")

    with pytest.raises(ValidationError) as exc:
        validate_resume_file(file_obj)
    assert "Invalid PDF file header" in str(exc.value)


def test_resume_invalid_extension_raises_validation_error():
    file_obj = SimpleUploadedFile(
        "doc.docx", b"%PDF-1.4 valid header", content_type="application/pdf"
    )
    with pytest.raises(ValidationError) as exc:
        validate_resume_file(file_obj)
    assert "Only PDF files are allowed" in str(exc.value)


def test_resume_oversize_raises_validation_error():
    oversized_content = b"%PDF-" + b"0" * (6 * 1024 * 1024)  # 6 MB
    file_obj = SimpleUploadedFile("heavy.pdf", oversized_content, content_type="application/pdf")

    with pytest.raises(ValidationError) as exc:
        validate_resume_file(file_obj)
    assert "cannot exceed 5 MB" in str(exc.value)


def test_valid_png_image_passes_validation():
    png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    file_obj = SimpleUploadedFile("shot.png", png_content, content_type="image/png")

    validate_image_file(file_obj)


def test_valid_jpeg_and_webp_image_passes_validation():
    jpeg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    jpeg_file = SimpleUploadedFile("shot.jpg", jpeg_content, content_type="image/jpeg")
    validate_image_file(jpeg_file)

    webp_content = b"RIFF\x00\x00\x00\x00WEBPVP8 "
    webp_file = SimpleUploadedFile("shot.webp", webp_content, content_type="image/webp")
    validate_image_file(webp_file)


def test_image_invalid_extension_raises_validation_error():
    file_obj = SimpleUploadedFile("script.exe", b"\x89PNG\r\n\x1a\n", content_type="image/png")
    with pytest.raises(ValidationError) as exc:
        validate_image_file(file_obj)
    assert "Unsupported image format" in str(exc.value)


def test_image_oversize_raises_validation_error():
    oversized_png = b"\x89PNG\r\n\x1a\n" + b"0" * (4 * 1024 * 1024)
    file_obj = SimpleUploadedFile("large.png", oversized_png, content_type="image/png")
    with pytest.raises(ValidationError) as exc:
        validate_image_file(file_obj)
    assert "cannot exceed 3 MB" in str(exc.value)


def test_fake_image_raises_validation_error():
    fake_image_content = b"<?php echo 'malware'; ?>"
    file_obj = SimpleUploadedFile("backdoor.png", fake_image_content, content_type="image/png")

    with pytest.raises(ValidationError) as exc:
        validate_image_file(file_obj)
    assert "Invalid or corrupted image binary" in str(exc.value)


def test_secure_upload_to_generates_uuid_filename():
    uploader = SecureUploadTo("resumes/")
    path = uploader(None, "my resume original.pdf")
    assert path.startswith("resumes")
    assert path.endswith(".pdf")
    assert "my resume original" not in path
