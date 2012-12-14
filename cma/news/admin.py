from news.models import News
from django.contrib import admin

class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo')

admin.site.register(News, NewsAdmin)

