from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    search_fields = ("title",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Group, GroupAdmin)
