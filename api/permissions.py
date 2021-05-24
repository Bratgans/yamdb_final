from rest_framework import permissions

from api.models import User


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_superuser or request.user.is_admin))

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and (request.user.is_superuser or request.user.is_admin))


class IsAuthor(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.is_superuser or request.user.is_moderator))

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and (request.user.is_superuser or request.user.is_moderator))


class IsUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        return bool(user and User.objects.filter(email=user))


class IsReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
