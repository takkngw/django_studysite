from django import forms
from studysite.models import Studysite, Tag

class SnippetForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Studysite
        fields = ('title', 'image', 'question', 'answer', 'tags')


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Studysite
        fields = ('answer',)
        
