from django.contrib import admin

from .models import User, Profile, ProfileSearch, ProfileLikes

admin.site.register(ProfileSearch)
admin.site.register(ProfileLikes)


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'first_name', 'username')


@admin.register(Profile)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_registered')