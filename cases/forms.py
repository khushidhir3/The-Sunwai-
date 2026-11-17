from django import forms
from .models import Case, Party


class CaseFilingForm(forms.ModelForm):
    petitioner_name = forms.CharField(
        max_length=200,
        label="Petitioner / Plaintiff Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Ramesh Chandra Sharma',
            'class': 'form-input',
        })
    )
    respondent_name = forms.CharField(
        max_length=200,
        label="Respondent / Defendant Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Municipal Corporation of Delhi',
            'class': 'form-input',
        })
    )

    class Meta:
        model = Case
        fields = ['case_no', 'title', 'case_type', 'description']
        widgets = {
            'case_no': forms.TextInput(attrs={
                'placeholder': 'e.g. CS(COMM) 105/2026',
                'class': 'form-input',
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Sharma v. Municipal Corporation of Delhi',
                'class': 'form-input',
            }),
            'case_type': forms.Select(attrs={
                'class': 'form-input',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Brief statement of claim, controversy, and relief sought...',
                'class': 'form-input',
            }),
        }
