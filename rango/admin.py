from django.contrib import admin
from rango.models import Category, Page
#import admin.ModelAdmin

# Admin Page : Category Configuration
admin.site.register(Category)


# Admin Page : Page Configuration
class PageAdmin(admin.ModelAdmin):
    list_display = ('title','category','url')   

admin.site.register(Page, PageAdmin)