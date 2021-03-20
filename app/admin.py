from django.contrib import admin
from .models import (Table, ItemCategory, Item, InventoryCategory, Inventory, Order,
                     OrderItems, Recipe, Expense, ExpenseCategory, MostSellingItem, InventoryIn,
                     InventoryOut, User)
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.admin import UserAdmin



class InventoryHistoryAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'unit', 'price', 'category', 'description', 'quantity', 'image']
    history_list_display = ['name', 'unit', 'price', 'category', 'description', 'quantity', 'image']
    search_fields = ['name']


# Register your models here.
admin.site.register(Table, SimpleHistoryAdmin)
admin.site.register(ItemCategory, SimpleHistoryAdmin)
admin.site.register(Item, SimpleHistoryAdmin)
admin.site.register(MostSellingItem, SimpleHistoryAdmin)
admin.site.register(Inventory, InventoryHistoryAdmin)
admin.site.register(InventoryCategory, SimpleHistoryAdmin)
admin.site.register(InventoryIn, InventoryHistoryAdmin)
admin.site.register(InventoryOut, InventoryHistoryAdmin)
admin.site.register(Order, SimpleHistoryAdmin)
admin.site.register(OrderItems, SimpleHistoryAdmin)
admin.site.register(Recipe, SimpleHistoryAdmin)
admin.site.register(Expense, SimpleHistoryAdmin)
admin.site.register(ExpenseCategory, SimpleHistoryAdmin)
admin.site.register(User, UserAdmin)
# admin.site.register(Role, SimpleHistoryAdmin)
# admin.site.register(UserRole, SimpleHistoryAdmin)

