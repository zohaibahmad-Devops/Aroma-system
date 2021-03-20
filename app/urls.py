from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.dates import ArchiveIndexView


urlpatterns = [
    path('', views.user_check, name='first-check'),
    path('dashboard/', views.index, name='index'),

    # Menu
    path('menu/', views.menu, name='menu'),

    # Table
    path('table/list', views.TableList.as_view(), name='table-list'),
    path('table/new', views.TableCreate.as_view(), name='table-new'),
    path('table/<int:pk>/new', views.TableUpdate.as_view(), name='table-edit'),
    path('table/<int:pk>/edit', views.TableDelete.as_view(), name='table-delete'),

    # Item
    path('item/list', views.ItemList.as_view(), name='item-list'),
    path('item/new', views.ItemCreate.as_view(), name='item-new'),
    path('item/<int:pk>/edit', views.ItemUpdate.as_view(), name='item-edit'),
    path('item/<int:pk>/delete', views.ItemDelete.as_view(), name='item-delete'),
    path('item/rating', views.item_rating, name='item-rating'),
    path('item/rating/<int:month>/<int:year>/', views.item_rating_month, name='item-rating-month'),

    # Item Category
    path('item/category/list', views.ItemCategoryList.as_view(), name='item-category-list'),
    path('item/category/new', views.ItemCategoryCreate.as_view(), name='item-category-new'),
    path('item/category/<int:pk>/edit', views.ItemCategoryUpdate.as_view(), name='item-category-edit'),
    path('item/category/<int:pk>/delete', views.ItemCategoryDelete.as_view(), name='item-category-delete'),

    # Order
    path('order/list', views.OrderList.as_view(), name='order-list'),
    path('order/new', views.order_new, name='order-new'),
    path('order/<int:pk>/new', views.order_edit, name='order-edit'),
    path('order/<int:pk>/edit', views.ItemCategoryCreate.as_view(), name='order-delete'),
    path('order/<int:pk>/ready', views.order_ready, name='order-ready'),
    path('order/<int:pk>/served', views.order_served, name='order-served'),
    path('order/<int:pk>/cancel', views.order_cancel, name='order-cancel'),
    path('order/<int:pk>/completed', views.order_completed, name='order-completed'),
    path('order/waiting', views.order_waiting, name='order-waiting-que'),
    path('order/ready', views.order_ready_que, name='order-ready-que'),
    path('order/served', views.order_served_que, name='order-served-que'),
    path('order/completed', views.order_completed_que, name='order-completed-que'),
    path('order/cancelled', views.order_cancelled_que, name='order-cancelled-que'),
    path('order/today', views.order_today, name='order-today-list'),
    path('order/report', views.OrderExportView.as_view(), name='order-report'),

    # Inventory
    path('inventory/list', views.InventoryList.as_view(), name='inventory-list'),
    path('inventory/new', views.InventoryCreate.as_view(), name='inventory-new'),
    path('inventory/<int:pk>/edit', views.InventoryUpdate.as_view(), name='inventory-edit'),
    path('inventory/<int:pk>/delete', views.InventoryDelete.as_view(), name='inventory-delete'),
    path('inventory/<int:pk>/add-to', views.add_to_inventory_item, name='inventory-add-to'),
    path('inventory/<int:pk>/issue', views.issue_inventory_to, name='inventory-issue'),
    path('inventory/<int:pk>/return', views.return_inventory_item, name='inventory-return'),
    path('inventory/history', views.inventory_history, name='inventory-history'),
    path('inventory/out-of-stock', views.inventory_out_of_stock, name='inventory-stock'),
    path('inventory/in', views.inventory_in, name='inventory-in'),
    path('inventory/out', views.inventory_out, name='inventory-out'),
    path('inventory/rating', views.inventory_ratings, name='inventory-rating'),

    # Inventory Category
    path('inventory/category/list', views.InventoryCategoryList.as_view(), name='inventory-category-list'),
    path('inventory/category/new', views.InventoryCategoryCreate.as_view(), name='inventory-category-new'),
    path('inventory/category/<int:pk>/edit', views.InventoryCategoryUpdate.as_view(), name='inventory-category-edit'),
    path('inventory/category/<int:pk>/delete', views.InventoryCategoryDelete.as_view(),
         name='inventory-category-delete'),


    # Expense
    path('expense/list', views.ExpenseList.as_view(), name='expense-list'),
    path('expense/new', views.ExpenseCreate.as_view(), name='expense-new'),
    path('expense/<int:pk>/edit', views.ExpenseUpdate.as_view(), name='expense-edit'),
    path('expense/<int:pk>/delete', views.ExpenseDelete.as_view(), name='expense-delete'),

    # Expense Category
    path('expense/category/list', views.ExpenseCategoryList.as_view(), name='expense-category-list'),
    path('expense/category/new', views.ExpenseCategoryCreate.as_view(), name='expense-category-new'),
    path('expense/category/<int:pk>/edit', views.ExpenseCategoryUpdate.as_view(), name='expense-category-edit'),
    path('expense/category/<int:pk>/delete', views.ExpenseCategoryDelete.as_view(),
         name='expense-category-delete'),

    # AJAX Calls
    path('ajax/item/add-to-order', views.add_to_order, name='item-add-to-order'),


    # Users
    #path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.login_user, name='login'),
    path('accounts/logout/', views.logout_user, name='logout'),
    path('accounts/signup/admin/', views.signup_admin, name='signup-admin'),
    path('accounts/signup/manager/', views.signup_manager, name='signup-manager'),
    path('accounts/signup/inventory-manager/', views.signup_inventory_manager, name='signup-inventory-manager'),
    path('accounts/signup/staff/', views.signup_staff, name='signup-staff'),
    path('users/list/', views.get_user_list, name='user-list'),
    path('users/<int:pk>/edit/', views.get_user_list, name='user-edit'),
    path('users/<int:pk>/activate/', views.activate_user, name='user-activate'),
    path('users/<int:pk>/deactivate/', views.deactivate_user, name='user-deactivate'),
    path('users/active/list', views.user_active_list, name='user-active-list'),
    path('users/blocked/list', views.user_blocked_list, name='user-deactive-list'),

    # Archives
    path('reports/daily/<str:day>/<str:month>/<str:year>/', views.report_daily, name='report-daily'),
    path('reports/monthly/<str:month>/<int:year>/', views.report_monthly, name='report-monthly'),
    path('reports/weekly/', views.report_weekly, name='report-weekly'),
    path('reports/yearly/<str:year>/', views.report_yearly, name='report-yearly'),
    path('reports/daily/index', views.report_daily_index, name='report-daily-index'),

]
