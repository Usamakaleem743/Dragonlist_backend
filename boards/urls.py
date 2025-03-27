from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    ListViewSet, CardViewSet, 
    LabelViewSet, ChecklistViewSet,
    UserViewSet, remove_card_dates,
    add_card_member, remove_card_member, add_card_dates,
    ChecklistItemViewSet, AttachmentViewSet, CardLocationViewSet, CommentViewSet,
    BoardViewSet
)

router = DefaultRouter()
router.register(r'cards', CardViewSet, basename='card')
router.register(r'labels', LabelViewSet, basename='label')
router.register(r'lists', ListViewSet, basename='list')
router.register(r'checklists', ChecklistViewSet, basename='checklist')
router.register(r'checklist-items', ChecklistItemViewSet, basename='checklist-item')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'card-locations', CardLocationViewSet, basename='card-location')
router.register(r'users', UserViewSet, basename='user')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'boards', BoardViewSet, basename='board')
urlpatterns = [
    path('', include(router.urls)),
    path('cards/<int:card_pk>/members/add_member/', add_card_member, name='add-card-member'),
    path('cards/<int:card_pk>/members/remove_member/', remove_card_member, name='remove-card-member'),
    path('cards/<int:card_pk>/dates/remove/', remove_card_dates, name='remove-card-dates'),
    path('cards/<int:card_pk>/dates/add_date/', add_card_dates, name='add-card-dates'),
    path('cards/<int:card_pk>/checklists/', ChecklistViewSet.as_view({'get': 'list' ,'post': 'create'}), name='get-checklists'),
    path('cards/<int:card_pk>/checklists/<int:checklist_pk>/', ChecklistViewSet.as_view({'delete'}), name='delete-checklist'),
    path('cards/<int:card_pk>/checklists/<int:checklist_pk>/items/', ChecklistItemViewSet.as_view({'get': 'list' ,'post': 'create'}), name='get-checklist-items'),
    path('checklist-items/<int:item_pk>/toggle/', ChecklistItemViewSet.as_view({'post': 'toggle'}), name='toggle-checklist-item'),
    path('checklist-items/<int:item_pk>/delete/', ChecklistItemViewSet.as_view({'delete': 'delete'}), name='delete-checklist-item'),
    path('checklist-items/', ChecklistItemViewSet.as_view({'get': 'list'}), name='get-checklist-items'),
    path('cards/<int:card_pk>/comments/', CommentViewSet.as_view({'get': 'list' ,'post': 'create'}), name='get-comments'),
    path('cards/<int:card_pk>/labels/<int:label_pk>/', CardViewSet.as_view({'delete': 'remove_label'}), name='remove-card-label'),
    path('cards/<int:pk>/optimize-description/', CardViewSet.as_view({'post': 'optimize_description'}), 
         name='card-optimize-description'),
]   