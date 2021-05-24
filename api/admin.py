from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    ordering = ['name']


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'review_id', 'author', 'pub_date', 'text')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    ordering = ['name']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title_id', 'pub_date', 'author', 'text', 'score')


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'description', 'category')
    ordering = ['-year']


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'role', 'bio')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(User, UserAdmin)
