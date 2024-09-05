from django.contrib import admin
from studysite.models import Studysite
from .models import Studysite, TagGroup


# Register your models here.
# admin.site.register(Studysite)

@admin.register(Studysite)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'level')
    list_filter = ('created_at', 'tag_groups')
    search_fields = ('title', 'description', 'code')

@admin.register(TagGroup)
class TagGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')
    list_editable = ('order',)
    ordering = ('order', 'name')

