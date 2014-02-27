from django.contrib import admin
from rango.models import Category, Page, UserProfile
#import admin.ModelAdmin

# Admin Page : Page Configuration
class PageAdmin(admin.ModelAdmin):
    list_display = ('title','category','url')   


# Admin Page : Category Configuration
admin.site.register(Category)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)