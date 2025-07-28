from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from .models import SessionData, SensorData
from datetime import datetime, timedelta
from django.utils.html import format_html


@admin.register(SessionData)
class SessionDataAdmin(admin.ModelAdmin):
    list_display = (
        'view_details_link', 'id', 'user_email', 'user_id', 'start_time', 'end_time', 'session_duration',
        'steps_taken', 'wheelchair_id',
        'start_quality_1', 'start_quality_2', 'start_quality_3',
        'end_quality_1', 'end_quality_2', 'version',
         )
    search_fields = ('user_id',)
    ordering = ('-duration_ms',)
    change_form_template = "admin/device/session_change_form.html"

    def user_email(self, obj):
        from account.models import User
        try:
            return User.objects.get(id=obj.user_id).email
        except User.DoesNotExist:
            return "Unknown"
    user_email.short_description = "User Email"

    def start_time(self, obj):
        try:
            return datetime.fromtimestamp(obj.start_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return "Invalid start"
    start_time.short_description = "Start Time"

    def end_time(self, obj):
        try:
            return datetime.fromtimestamp(obj.end_timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return "Invalid end"
    end_time.short_description = "End Time"

    def session_duration(self, obj):
        try:
            duration = timedelta(milliseconds=obj.duration_ms)
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            parts = []
            if hours:
                parts.append(f"{hours} hr")
            if minutes:
                parts.append(f"{minutes} min")
            if seconds or not parts:
                parts.append(f"{seconds} sec")
            return ' '.join(parts)
        except Exception:
            return "Invalid duration"
    session_duration.short_description = "Duration"

    def view_details_link(self, obj):
        url = reverse("admin:device_sessiondata_details", args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" class="btn btn-primary" style="'
            'font-weight: 600; padding: 6px 12px; border-radius: 6px; '
            'color: white; background-color: #0d6efd; border: none; text-decoration: none;">'
            '🔍 View</a>', url
        )
    view_details_link.short_description = "Details"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:session_id>/details/', self.admin_site.admin_view(self.session_detail_view), name='device_sessiondata_details'),
        ]
        return custom_urls + urls

    def session_detail_view(self, request, session_id):
        session = get_object_or_404(SessionData, id=session_id)
        sensor_data = SensorData.objects.filter(session_id=session_id).order_by('timestamp')
        return render(request, "admin/device/session_detail.html", {
            "session": session,
            "sensor_data": sensor_data,
            "title": f"Session Details – #{session_id}"
        })

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False
