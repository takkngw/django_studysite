from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
# from users.models import User
import os
from uuid import uuid4
from django.utils import timezone


def rename_image(path):
   def wrapper(instance, filename):
       ext = filename.split('.')[-1]
       filename = '{}.{}'.format(uuid4().hex, ext)
       return os.path.join(path, filename)
   return wrapper
    
class TagGroup(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)  # 並び順を指定するためのフィールド


    def __str__(self):
        return self.name

    def get_hierarchy(self):
        """
        親グループから順に階層を取得するメソッド
        """
        hierarchy = [self.name]
        parent = self.parent
        while parent:
            hierarchy.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(hierarchy)


class VisitorCounter(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Visitor count: {self.count}"


# Create your models here.
class Studysite(models.Model):
    title = models.CharField('タイトル', max_length=128)
    image = models.FileField('問題画像', upload_to='image/', blank=True)
    question = models.TextField('問題', blank=True)
    answer = models.TextField('解説', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name='投稿者',
                                   on_delete=models.CASCADE)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    tag_groups = models.ManyToManyField(TagGroup, blank=True)
    likes = models.PositiveIntegerField(default=0)
    level = models.IntegerField(default=0)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_posts', blank=True)

    def __str__(self):
        return self.title



class Comment(models.Model):
    snippet = models.ForeignKey(Studysite, on_delete=models.CASCADE, related_name='comments')
    username = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text[:20]