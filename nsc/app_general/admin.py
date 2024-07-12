from django.contrib import admin
from app_general.models import Phobias
from app_general.models import Add_pb
from django.utils.html import format_html

# Register your models here.

class PhobiasAdmin(admin.ModelAdmin):
    def image1_tag(self, obj):
        if obj.image1:
            return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image1.url))
        return "No Image"

    def image2_tag(self, obj):
        if obj.image2:
            return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image2.url))
        return "No Image"

    image1_tag.short_description = 'Image 1'
    image2_tag.short_description = 'Image 2'
    list_display = ['name_TH', 'name_ENG', 'color', 'count', 'image1_tag', 'image2_tag']


class Add_pb_Admin(admin.ModelAdmin):
    list_display = ['pb_data', 'pb_status', 'pb_time']
    search_fields = ['pb_data']
    list_filter = ['pb_status']
    
admin.site.register(Phobias, PhobiasAdmin)
admin.site.register(Add_pb, Add_pb_Admin)
