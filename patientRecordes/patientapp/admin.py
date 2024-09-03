from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django.utils.html import format_html

admin.site.site_header="Patient Recordes Panel"
class RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_status', 'get_user_full_name', 'view_user_certificate')
    list_filter = ('request_status',)  # تصفية حسب حالة الطلب
    search_fields = ('user__username', 'user__first_name', 'user__last_name')  # البحث حسب اسم المستخدم

    ordering = ('request_status',)  # ترتيب العرض - المعلق أولًا
    readonly_fields = ('user', 'get_user_full_name', 'view_user_certificate')  # اجعل user كحقل للقراءة فقط

    def get_user_full_name(self, obj):
        if obj.user.is_superuser:
            return "Admin"
        elif hasattr(obj.user, 'patient'):
            return obj.user.patient.full_name
        elif hasattr (obj.user, 'users'):
            return obj.user.users.full_name
        return "Unknown"
    def has_add_permission(self, request):
        return False

    def view_user_certificate(self, obj):
        if obj.user.is_superuser:
            return "N/A"
        elif hasattr(obj.user, 'users'):
            # عند النقر على اسم الصورة، سيتم عرضها في نافذة منفصلة
            return format_html('<a href="{}" target="_blank">View Certificate</a>', obj.user.users.certificate.url)
        return "N/A"
    def save_model(self, request, obj, form, change):
        # تحديث حالة الطلب
        super().save_model(request, obj, form, change)

        # تحقق من تغيير حالة الطلب إلى True
        if obj.request_status and hasattr(obj.user, 'users'):
            # إذا كان المستخدم مرتبطًا بـ Users وتغيير الحالة إلى True، ثم قم بتعيين active للمستخدم على True
            obj.user.users.active = True
            obj.user.users.save()    

    get_user_full_name.short_description = 'User Full Name'
    view_user_certificate.short_description = 'User Certificate'

admin.site.register(Request, RequestAdmin)
admin.site.register(Patient)
admin.site.register(Major)
admin.site.register(Xray)
admin.site.register(Users)
admin.site.unregister(Group)
admin.site.register(CategoriesAnalysis)
admin.site.register(BasicAnalyses)
admin.site.register(Result)
admin.site.register(Result_details)

