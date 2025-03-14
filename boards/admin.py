from django.contrib import admin
from .models import List, Card, Label, ChecklistItem, CardDate

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'order')
    list_filter = ('list',)
    search_fields = ('title', 'description')
    filter_horizontal = ('members',)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('title', 'color', 'card')
    search_fields = ('title',)
    list_filter = ('card',)
@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'checklist', 'is_completed', 'order')
    list_filter = ('is_completed', 'checklist')
    search_fields = ('title',)
    ordering = ('order',)

@admin.register(CardDate)
class DateAdmin(admin.ModelAdmin):
    list_display = ('card', 'start_date', 'due_date', 'is_complete')
    list_filter = ('is_complete',)
    search_fields = ('card', 'start_date', 'due_date')
