from django.contrib import admin

from .models import Group, GroupMember


class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 0


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "invite_code", "created_at")
    search_fields = ("name", "invite_code")
    inlines = [GroupMemberInline]


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "role", "joined_at")
    list_filter = ("role",)
