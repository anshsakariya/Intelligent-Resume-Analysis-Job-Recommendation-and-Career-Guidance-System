from django import forms
from .models import Resume
from .validators import validate_pdf_upload

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control form-control-custom', 'accept': '.pdf'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        validate_pdf_upload(file)
        return file
