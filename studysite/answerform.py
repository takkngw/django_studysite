from django import forms
from studysite.models import Studysite

class SnippetForm(forms.ModelForm):
    class Meta:
        model = Studysite
        fields = ('answer')
