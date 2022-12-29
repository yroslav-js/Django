from django.contrib import admin
from .models import Post, Country


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'pub_date', 'author', 'country', 'text')
    search_fields = ('text',)
    list_filter = ('pub_date', 'author')
    list_editable = ('country',)
    empty_value_display = '--empty--'


class CountryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '--empty--'


admin.site.register(Post, PostAdmin)
admin.site.register(Country, CountryAdmin)
