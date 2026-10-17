from django.core.exceptions import ValidationError

MAX_PDF_UPLOAD_SIZE = 4 * 1024 * 1024


def validate_pdf_upload(upload):
    if not upload:
        raise ValidationError('Please select a PDF file to upload.')
    if not upload.name.lower().endswith('.pdf'):
        raise ValidationError('Only PDF files are accepted.')
    if upload.size > MAX_PDF_UPLOAD_SIZE:
        raise ValidationError('File size exceeds 4MB. Please upload a smaller PDF.')

    header = upload.read(1024)
    upload.seek(0)
    if b'%PDF-' not in header:
        raise ValidationError('The selected file is not a valid PDF document.')
