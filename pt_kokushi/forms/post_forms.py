from django import forms
from django.core.exceptions import ValidationError
from pt_kokushi.models.post_models import Post, Comment
import os

#掲示板用
def load_banned_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]

# ここでファイルパスを指定
BANNED_WORDS = load_banned_words(os.path.join(os.path.dirname(__file__), 'banned_words.txt'))

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['nickname','title', 'content',]
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if not nickname:
            # nicknameが未入力の場合、デフォルト値を設定します
            nickname = "Anonymous"  # ここでデフォルトの値を設定
        return nickname
    
    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname', '').lower()
        for banned_word in BANNED_WORDS:
            if banned_word.lower() in nickname:
                raise ValidationError("ニックネームには不適切な内容が含まれています。")
        return nickname

    def clean_title(self):
        title = self.cleaned_data.get('title', '').lower()
        for banned_word in BANNED_WORDS:
            if banned_word.lower() in title:
                raise ValidationError("タイトルには不適切な内容が含まれています。")
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '').lower()
        for banned_word in BANNED_WORDS:
            if banned_word.lower() in content:
                raise ValidationError("投稿には不適切な内容が含まれています。")
        return content

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content','nickname']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if not nickname:
            # nicknameが未入力の場合、デフォルト値を設定します
            nickname = "Anonymous"  # ここでデフォルトの値を設定
        return nickname
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '').lower()
        for banned_word in BANNED_WORDS:
            if banned_word in content:
                raise ValidationError("コメントには不適切な内容が含まれています。")
        return content
    