from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Group, GroupMember
from .serializers import (
    GroupCreateSerializer,
    GroupMemberSerializer,
    GroupSerializer,
    InviteUserSerializer,
    JoinGroupSerializer,
)

User = get_user_model()


class IsGroupAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Group):
            group = obj
        elif isinstance(obj, GroupMember):
            group = obj.group
        else:
            return False
        return group.memberships.filter(
            user=request.user, role=GroupMember.Role.ADMIN
        ).exists()


class IsGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.memberships.filter(user=request.user).exists()


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Group.objects.filter(memberships__user=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return GroupCreateSerializer
        return GroupSerializer

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        GroupMember.objects.create(
            group=group,
            user=self.request.user,
            role=GroupMember.Role.ADMIN,
        )
        serializer.instance = group

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = GroupSerializer(serializer.instance, context={"request": request})
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["post"], url_path="join")
    def join(self, request):
        serializer = JoinGroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["invite_code"].upper()
        try:
            group = Group.objects.get(invite_code=code)
        except Group.DoesNotExist:
            raise ValidationError({"invite_code": "Invalid invitation code."})
        if group.memberships.filter(user=request.user).exists():
            raise ValidationError({"detail": "You are already a member of this group."})
        GroupMember.objects.create(group=group, user=request.user)
        return Response(
            GroupSerializer(group, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="invite",
        permission_classes=[permissions.IsAuthenticated, IsGroupAdmin],
    )
    def invite(self, request, pk=None):
        group = self.get_object()
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        invite_url = request.build_absolute_uri(group.invite_link)
        send_mail(
            subject=f"Invitation to join {group.name}",
            message=(
                f"You have been invited to join the group '{group.name}'.\n"
                f"Use invite code: {group.invite_code}\n"
                f"Or join via link: {invite_url}"
            ),
            from_email=None,
            recipient_list=[email],
        )
        return Response(
            {
                "detail": "Invitation sent.",
                "invite_code": group.invite_code,
                "invite_link": group.invite_link,
            }
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="members",
    )
    def members(self, request, pk=None):
        group = self.get_object()
        if not group.memberships.filter(user=request.user).exists():
            raise PermissionDenied("You are not a member of this group.")
        members = group.memberships.select_related("user")
        return Response(GroupMemberSerializer(members, many=True).data)

    @action(
        detail=True,
        methods=["delete"],
        url_path="members/(?P<member_id>[^/.]+)",
        permission_classes=[permissions.IsAuthenticated, IsGroupAdmin],
    )
    def remove_member(self, request, pk=None, member_id=None):
        group = self.get_object()
        try:
            membership = group.memberships.get(pk=member_id)
        except GroupMember.DoesNotExist:
            raise ValidationError({"detail": "Member not found."})
        if membership.user == group.created_by:
            raise ValidationError({"detail": "Cannot remove the group creator."})
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
