from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content','is_anonymous']
        labels = {
            'content': '内容',
            'is_anonymous': '匿名で投稿する',
        }
        # ユーザーに入力してほしいフィールドを指定