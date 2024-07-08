from django.conf import settings
from django.db import models
# from users.models import User
import os
from uuid import uuid4

def rename_image(path):
   def wrapper(instance, filename):
       ext = filename.split('.')[-1]
       filename = '{}.{}'.format(uuid4().hex, ext)
       return os.path.join(path, filename)
   return wrapper

# Create your models here.
class Studysite(models.Model):
    title = models.CharField('タイトル', max_length=128)
    code = models.TextField('コード', blank=True)
    description = models.TextField('説明', blank=True)
    icon = models.ImageField('アイコン', upload_to='icons/', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name='投稿者',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.title