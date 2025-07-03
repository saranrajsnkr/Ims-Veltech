from django import forms
from .models import Student

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