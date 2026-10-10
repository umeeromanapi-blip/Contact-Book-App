from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Form for validating, creating, and updating Contact entries in Epic 1, 2 & 3.
    Implements validation rules:
    - Name: trimmed, not empty, max 100 characters
    - Phone: trimmed, not empty, max 20 characters
    - Email: trimmed, optional, valid email format
    - Category: choices in CATEGORY_CHOICES
    - Notes: trimmed, optional
    - is_favorite: optional boolean
    """
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'category', 'notes', 'is_favorite']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Eleanor Vance',
                'id': 'id_name',
                'autocomplete': 'name',
                'required': True,
                'maxlength': '100',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. +1 555-019-2834 or 0300-1234567',
                'id': 'id_phone',
                'autocomplete': 'tel',
                'required': True,
                'maxlength': '20',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. eleanor@example.com (optional)',
                'id': 'id_email',
                'autocomplete': 'email',
                'maxlength': '100',
            }),
            'category': forms.Select(attrs={
                'class': 'form-input form-select',
                'id': 'id_category',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'e.g. Office extension 402, met at tech summit...',
                'id': 'id_notes',
                'rows': 3,
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
                'id': 'id_is_favorite',
            }),
        }
        labels = {
            'name': 'Full Name',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'category': 'Group / Category',
            'notes': 'Notes & Details',
            'is_favorite': 'Mark as Favorite',
        }
        error_messages = {
            'name': {
                'required': 'Please enter a contact name.',
                'max_length': 'Name cannot exceed 100 characters.',
            },
            'phone': {
                'required': 'Please enter a phone number.',
                'max_length': 'Phone number cannot exceed 20 characters.',
            },
            'email': {
                'invalid': 'Please enter a valid email address.',
            },
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        trimmed = name.strip()
        if not trimmed:
            raise forms.ValidationError('Contact name cannot be empty or contain only whitespace.')
        return trimmed

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        trimmed = phone.strip()
        if not trimmed:
            raise forms.ValidationError('Phone number cannot be empty or contain only whitespace.')
        return trimmed

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        return email.strip() if email else ''

    def clean_category(self):
        category = self.cleaned_data.get('category')
        return category if category else 'personal'

    def clean_notes(self):
        notes = self.cleaned_data.get('notes', '')
        return notes.strip() if notes else ''


class CSVImportForm(forms.Form):
    """
    Epic 3 Form: Handles validation of uploaded CSV contact files.
    """
    csv_file = forms.FileField(
        required=True,
        label="Select CSV File",
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.csv,text/csv',
            'id': 'id_csv_file'
        })
    )

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')
        if file:
            if not file.name.lower().endswith('.csv'):
                raise forms.ValidationError('Only valid .csv files are supported.')
            if file.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError('CSV file size cannot exceed 2MB.')
        return file


from django.contrib.auth.models import User


class UserRegistrationForm(forms.ModelForm):
    """
    Epic 4 Form: User registration with password confirmation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a secure password',
            'id': 'id_reg_password'
        }),
        min_length=6,
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'id': 'id_reg_password_confirm'
        }),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. johndoe',
                'id': 'id_reg_username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. john@example.com (optional)',
                'id': 'id_reg_email'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned_data


class UserLoginForm(forms.Form):
    """
    Epic 4 Form: User login form.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your username',
            'id': 'id_login_username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your password',
            'id': 'id_login_password',
            'autocomplete': 'current-password'
        })
    )

