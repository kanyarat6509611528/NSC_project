from django.contrib import admin
from app_general.models import Phobias
from app_general.models import Add_pb

# Register your models here.

class PhobiasAdmin(admin.ModelAdmin):
    list_display = ['name_TH','name_ENG','color','count']

class Add_pb_Admin(admin.ModelAdmin):
    list_display = ['pb_data','pb_status','pb_time']
    search_fields = ['pb_data']
    list_filter = ['pb_status']
    
admin.site.register(Phobias,PhobiasAdmin)
admin.site.register(Add_pb,Add_pb_Admin)
