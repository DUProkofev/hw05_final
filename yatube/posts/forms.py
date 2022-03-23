from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == "":
            raise forms.ValidationError(
                'Поле "Текст поста" должно быть заполнено'
            )
        return data