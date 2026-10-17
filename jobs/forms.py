from django import forms
from .models import JobApplication
from resumes.models import Resume
from resumes.validators import validate_pdf_upload

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'experience_years', 'resume', 'custom_resume_file', 'cover_letter']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '+91 9876543210'}),
            'experience_years': forms.Select(
                choices=[
                    ('0-1 years', '0 - 1 years'),
                    ('1-3 years', '1 - 3 years'),
                    ('3-5 years', '3 - 5 years'),
                    ('5+ years', '5+ years'),
                ],
                attrs={'class': 'form-select form-select-custom'}
            ),
            'resume': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'custom_resume_file': forms.FileInput(attrs={'class': 'form-control form-control-custom'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 4, 'placeholder': 'Briefly describe your relevant experience, key skills, and why you are excited about this position...'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['resume'].queryset = Resume.objects.filter(user=user).order_by('-uploaded_at')
            self.fields['resume'].empty_label = "Select an existing uploaded resume (optional)"
            self.fields['resume'].required = False
            self.fields['custom_resume_file'].required = False

    def clean_custom_resume_file(self):
        upload = self.cleaned_data.get('custom_resume_file')
        if upload:
            validate_pdf_upload(upload)
        return upload
