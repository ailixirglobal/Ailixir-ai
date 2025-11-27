from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import redirect, render
from .models import AISetting, AuthToken, QuickPrompt
from .forms import AISettingForm

admin.site.register(QuickPrompt)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "key_preview", "created_at", "regenerate_button")
    readonly_fields = ("key", "created_at")

    def key_preview(self, obj):
        return obj.key[:10] + "..." if obj.key else ""
    key_preview.short_description = "Token"

    def regenerate_button(self, obj):
        return format_html(
            f"<a class='button' href='/admin/regenerate-token/{obj.id}/'>Regenerate</a>"
        )
    regenerate_button.short_description = "Actions"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()

        custom_urls = [
            path(
                'regenerate-token/<int:pk>/',
                self.admin_site.admin_view(self.regenerate_token_view),
                name='regenerate_token',
            ),
        ]
        return custom_urls + urls

    def regenerate_token_view(self, request, pk):
        token = AuthToken.objects.get(pk=pk)
        token.regenerate()
        self.message_user(request, "Token regenerated successfully.")
        return redirect(request.META.get("HTTP_REFERER"))


@admin.register(AISetting)
class AISettingAdmin(admin.ModelAdmin):
    # Hide default add/change/delete
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Custom admin page
    def changelist_view(self, request, extra_context=None):
        # Ensure one instance exists
        obj, created = AISetting.objects.get_or_create(id=1)

        if request.method == "POST":
            form = AISettingForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                self.message_user(request, "Settings updated successfully.")
                return redirect("admin:core_aisetting_changelist")
        else:
            form = AISettingForm(instance=obj)

        context = {
            "form": form,
            "title": "AI System Settings",
        }
        return render(request, "admin/settings_page.html", context)