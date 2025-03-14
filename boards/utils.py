from django.db.models import Max

def get_next_order(queryset):
    """Get the next order number for a new item"""
    max_order = queryset.aggregate(Max('order'))['order__max']
    return (max_order or 0) + 1

def reorder_items(queryset, item_id, new_order):
    """Reorder items when an item is moved"""
    items = list(queryset.order_by('order'))
    item_to_move = next(item for item in items if item.id == item_id)
    old_order = item_to_move.order
    
    if old_order < new_order:
        # Moving down
        for item in items:
            if old_order < item.order <= new_order:
                item.order -= 1
                item.save()
    else:
        # Moving up
        for item in items:
            if new_order <= item.order < old_order:
                item.order += 1
                item.save()
    
    item_to_move.order = new_order
    item_to_move.save() 