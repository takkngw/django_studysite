from django.conf import settings
from django.db import models
from markdown import markdown
# from users.models import User
import os
from uuid import uuid4

def rename_image(path):
   def wrapper(instance, filename):
       ext = filename.split('.')[-1]
       filename = '{}.{}'.format(uuid4().hex, ext)
       return os.path.join(path, filename)
   return wrapper

def get_markdown_text_as_html(self):
    """MarkDown記法で書かれたtextをHTML形式に変換して返す"""
    return markdown(self.text)

# Create your models here.
class Studysite(models.Model):
    title = models.CharField('タイトル', max_length=128)
    image = models.ImageField('問題画像', upload_to='image/', blank=True)
    question = models.TextField('問題', blank=True)
    answer = models.TextField('解答', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name='投稿者',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.title