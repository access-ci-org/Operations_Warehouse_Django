from django.contrib import admin
from news.models import *

# Register your models here.

class News_Admin(admin.ModelAdmin):
    list_display = ('URN', 'NewsStart', 'NewsType', 'Subject')
    list_display_links = ['URN']
    ordering = ['NewsStart']
    search_fields = ['URN__iexact', 'Subject']
admin.site.register(News, News_Admin)

class News_Associations_Admin(admin.ModelAdmin):
    list_display = ('NewsItem', 'AssociatedType', 'AssociatedID')
    list_display_links = ['NewsItem']
    ordering = ['NewsItem']
    search_fields = ['NewsItem__iexact', 'AssociatedID__iexact']
admin.site.register(News_Associations, News_Associations_Admin)

class News_Publisher_Admin(admin.ModelAdmin):
    list_display = ('OrganizationID', 'OrganizationName')
    list_display_links = ['OrganizationID']
    ordering = ['OrganizationName']
    search_fields = ['OrganizationID__iexact', 'OrganizationName']
admin.site.register(News_Publisher, News_Publisher_Admin)
