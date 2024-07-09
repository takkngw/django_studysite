from django.contrib import admin
from studysite.models import Studysite
from .models import Studysite, Tag


# Register your models here.
# admin.site.register(Studysite)


@admin.register(Studysite)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'description', 'code')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


