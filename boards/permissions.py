from rest_framework import permissions

class IsBoardMember(permissions.BasePermission):
    """
    Custom permission to only allow board members to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a member of the board
        return request.user in obj.members.all()

class IsListBoardMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a list's board to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a member of the list's board
        return request.user in obj.board.members.all()

class IsCardBoardMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a card's board to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a member of the card's board
        return request.user in obj.list.board.members.all() 