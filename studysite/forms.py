from django import forms
from studysite.models import Studysite, Comment, TagGroup

class SnippetForm(forms.ModelForm):
    tag_groups = forms.ModelMultipleChoiceField(
        queryset=TagGroup.objects.all(),  # 初期値として空のクエリセットを設定
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    LEVEL_CHOICES = [(i, str(i)) for i in range(1, 6)]
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.Select,
    )

    class Meta:
        model = Studysite
        fields = ('title', 'image', 'question', 'answer', 'level', 'tag_groups')
        

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Studysite
        fields = ('answer',)
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('username', 'text')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'コメントを入力してください'}),
        }