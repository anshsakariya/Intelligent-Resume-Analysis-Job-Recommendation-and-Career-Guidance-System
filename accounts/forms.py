from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import Profile

# Remove UnicodeUsernameValidator to allow flexible usernames (letters, spaces, special chars, etc.)
User._meta.get_field('username').validators = [
    v for v in User._meta.get_field('username').validators
    if not isinstance(v, UnicodeUsernameValidator)
]

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Username'})
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'name@example.com'}))
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Mobile number (e.g. 9876543210)',
            'maxlength': '15',
            'inputmode': 'numeric'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order fields: Username -> Email -> Mobile Number -> Password -> Confirm Password
        self.order_fields(['username', 'email', 'phone', 'password1', 'password2'])

        # Allow simple passwords without length or complex character requirements
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'placeholder': 'Password'
            })
            self.fields['password1'].widget.attrs.pop('minlength', None)
            self.fields['password1'].help_text = ''
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'placeholder': 'Confirm Password'
            })
            self.fields['password2'].widget.attrs.pop('minlength', None)
            self.fields['password2'].help_text = ''

        for field_name, field in self.fields.items():
            field.help_text = ''
            current_class = field.widget.attrs.get('class', 'form-control form-control-custom')
            if self.is_bound and self.errors.get(field_name):
                if 'is-invalid' not in current_class:
                    field.widget.attrs['class'] = f"{current_class} is-invalid"
            else:
                field.widget.attrs['class'] = current_class

        # Mobile number label
        self.fields['phone'].label = "Mobile Number"
        self.fields['phone'].help_text = ""

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return ''
        # Normalize: strip common country code or separators
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if phone.startswith('+91'):
            phone = phone[3:]
        elif phone.startswith('91') and len(phone) == 12:
            phone = phone[2:]
        elif phone.startswith('0') and len(phone) == 11:
            phone = phone[1:]

        if not phone.isdigit():
            raise forms.ValidationError("Mobile number must contain digits only.")

        # Check if mobile number is already registered by another account
        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This mobile number is already registered. Please use a different number or log in.")
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        username = self.cleaned_data.get('username', '').strip()
        user.username = username
        email = self.cleaned_data.get('email', '').strip().lower()
        user.email = email

        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = username
            if self.cleaned_data.get('phone'):
                profile.phone = self.cleaned_data.get('phone')
            profile.save()
            user.profile = profile
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control form-control-custom'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control form-control-custom'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'full_name', 'phone', 'location', 'bio',
            'linkedin_url', 'github_url', 'portfolio_url',
            'education', 'degree', 'university', 'graduation_year',
            'experience_level', 'current_role', 'target_role',
            'years_of_experience', 'key_skills', 'preferred_work_mode',
            'notice_period', 'expected_salary', 'career_goal',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'John Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '+1 555-0199'}),
            'location': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'New York, USA'}),
            'bio': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 2, 'placeholder': 'Brief professional summary / bio...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://linkedin.com/in/username'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://github.com/username'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://yourportfolio.com'}),
            'education': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'MCA / B.Tech / B.Sc CS'}),
            'degree': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Master of Computer Applications'}),
            'university': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'State University'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '2025'}),
            'experience_level': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'current_role': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Junior Developer / Student'}),
            'target_role': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '1'}),
            'key_skills': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Python, Django, REST API, React, SQL'}),
            'preferred_work_mode': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'notice_period': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'expected_salary': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '$80,000 / yr or ₹10 LPA'}),
            'career_goal': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3, 'placeholder': 'Describe your primary career objective...'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            if not phone.isdigit():
                raise forms.ValidationError("Mobile number must contain digits only (0-9).")
            if len(phone) != 10:
                raise forms.ValidationError(f"Mobile number must be exactly 10 digits (you entered {len(phone)} digits).")
            if len(set(phone)) == 1:
                raise forms.ValidationError("Invalid mobile number. All digits cannot be the same.")
            # Check if another user already has this phone number
            existing = Profile.objects.filter(phone=phone)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("This mobile number is already registered by another account.")
        return phone
