from django import forms
from .models import Student , UserReport , InternshipApplication , StudentReport

class StudentApplicationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'mobile_number', 'department']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Full Name',
                'class': 'form-control'
            }),
            'roll_number': forms.TextInput(attrs={
                'placeholder': 'Roll Number',
                'class': 'form-control'
            }),

            'mobile_number': forms.TextInput(attrs={
                'placeholder': 'Mobile Number',
                'class': 'form-control'
            }),
            'department': forms.TextInput(attrs={
                'placeholder': 'Department',
                'class': 'form-control'
            }),
        }

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if Student.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError("You have already applied to a company.")
        return roll_number
    
    
    
class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ['name', 'roll_number', 'email', 'problem']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Full Name',
                'class': 'form-control'
            }),
            'roll_number': forms.TextInput(attrs={
                'placeholder': 'VTU Number (e.g., 24875)',
                'class': 'form-control',
                'pattern': '\\d{5}',
                'inputmode': 'numeric',
                'title': 'Enter a valid 5-digit roll number',
                'readonly': 'readonly',  # <-- lock the field
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'VTU Email',
                'class': 'form-control',
                'pattern': '^vtu\\d{5}@veltech\\.edu\\.in$',
                'title': 'Enter a valid Veltech email @veltech.edu.in',
                'readonly': 'readonly',  # Makes it non-editable
            })
            ,
            'problem': forms.Textarea(attrs={
                'placeholder': 'Describe your problem here',
                'class': 'form-control',
                'rows': 4,
            }),
        }
        
        
from django import forms
from .models import InternshipApplication

class InternshipApplicationForm(forms.ModelForm):
    class Meta:
        model = InternshipApplication
        fields = [
            'email', 'student_name', 'vtu_number', 'department', 'contact_number',
            'industry_name', 'industry_location', 'domain_of_work',
            'industry_category', 'industry_website', 'industry_email',
            'industry_phone_number', 'referal_person_name',
            'referal_person_designation', 'referal_person_email',
            'referal_person_phone_number', 'stipend_provided',
            'stipend_amount', 'fees_required', 'fees_amount'
        ]

        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'VTU Email',
                'class': 'form-control',
                'pattern': '^vtu\\d{5}@veltech\\.edu\\.in$',
                'title': 'Enter a valid Veltech email (e.g., vtu12345@veltech.edu.in)',
                'readonly': 'readonly',
            }),
            'student_name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'class': 'form-control',
            }),
            'vtu_number': forms.TextInput(attrs={
                'placeholder': 'VTU Number (e.g., 24875)',
                'class': 'form-control',
                'pattern': '\\d{5}',
                'inputmode': 'numeric',
                'title': 'Enter a valid 5-digit VTU number',
                'readonly': 'readonly',
            }),
            'department': forms.Select(attrs={
                'placeholder': 'Department',
                'class': '',
                'required': True,
                'choices': InternshipApplication.DEPARTMENT_CHOICES,
            }),
            'contact_number': forms.TextInput(attrs={
                'placeholder': 'Student Contact Number (e.g., 9789XXXXXX)',
                'class': 'form-control',
                'pattern': '[0-9]{10}',
                'title': 'Enter a valid 10-digit mobile number',
                'inputmode': 'numeric',
            }),
            'industry_name': forms.TextInput(attrs={
                'placeholder': 'Company/Industry Name',
                'class': 'form-control',
            }),
            'industry_location': forms.TextInput(attrs={
                'placeholder': 'Location of the Industry',
                'class': 'form-control',
            }),
            'domain_of_work': forms.TextInput(attrs={
                'placeholder': 'e.g., AI/ML, Web Dev, IoT',
                'class': 'form-control',
            }),
            'industry_category': forms.TextInput(attrs={
                'placeholder': 'Startup / MNC / MSME / etc.',
                'class': 'form-control',
            }),
            'industry_website': forms.TextInput(attrs={
                'placeholder': 'https://example.com',
                'class': 'form-control',
                'required': True,
            }),
            'industry_email': forms.EmailInput(attrs={
                'placeholder': 'Industry Email (e.g., hr@company.com)',
                'class': 'form-control',
                'required': True,
            }),
            'industry_phone_number': forms.TextInput(attrs={
                'placeholder': 'Industry Phone Number',
                'class': 'form-control',
                'pattern': '[0-9]{10,15}',
                'title': 'Enter a valid phone number',
                'inputmode': 'numeric',
                'required': True,
            }),
            'referal_person_name': forms.TextInput(attrs={
                'placeholder': 'Name of the Referral Person',
                'class': 'form-control',
                'required': True,

                
            }),
            'referal_person_designation': forms.TextInput(attrs={
                'placeholder': 'Designation of the Referral Person',
                'class': 'form-control',
                'required': True,
            }),
            'referal_person_email': forms.EmailInput(attrs={
                'placeholder': 'Email of the Referral Person',
                'class': 'form-control',
                'required': True,
            }),
            'referal_person_phone_number': forms.TextInput(attrs={
                'placeholder': 'Mobile Number of the Referral Person',
                'class': 'form-control',
                'pattern': '[0-9]{10}',
                'title': 'Enter a valid 10-digit mobile number',
                'inputmode': 'numeric',
                'required': True,
            }),
            'stipend_provided': forms.TextInput(attrs={
                'placeholder': 'Is stipend provided? (YES/NO)',
                'class': 'form-control',
            }),
            'stipend_amount': forms.TextInput(attrs={
                'placeholder': 'Enter stipend amount if applicable or "N/A"',
                'class': 'form-control',
            }),
            'fees_required': forms.TextInput(attrs={
                'placeholder': 'Is fees required? (YES/NO)',
                'class': 'form-control',
            }),
            'fees_amount': forms.TextInput(attrs={
                'placeholder': 'Enter fee amount if applicable or "N/A"',
                'class': 'form-control',
            }),
        }




class StudentReportForm(forms.ModelForm):
    class Meta:
        model = StudentReport
        fields = ['roll_number', 'report_status']
        widgets = {
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Roll Number',
                'readonly': 'readonly',  # UI-only; backend still needs protection

            }),
            'report_status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
        
        
from django import forms
from .models import Company

class CompanyLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        try:
            company = Company.objects.get(username=username, password=password)
            cleaned_data["company"] = company
        except Company.DoesNotExist:
            raise forms.ValidationError("Invalid username or password")

        return cleaned_data
