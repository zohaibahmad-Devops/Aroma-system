from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import (Table, Item, ItemCategory, InventoryCategory, ExpenseCategory, Order, OrderItems, Expense,
                     Inventory, Employee, EmployeeExpense, MostSellingItem, InventoryIn, InventoryOut, User)
from .forms import (ItemCategoryForm, InventoryCategoryForm, ExpenseCategoryForm, ItemForm, TableForm, ExpenseForm,
                    InventoryForm, EmployeeForm, EmployeeExpenseForm, AdminSignupForm, ManagerSignupForm,
                    InventoryManagerSignupForm, StaffSignupForm)

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from .decorators import admin_required, manager_required, staff_required, inventory_manager_required

from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from excel_response import ExcelResponse, ExcelView
from django.views.generic.dates import DayArchiveView, WeekArchiveView, MonthArchiveView, YearArchiveView, \
    ArchiveIndexView


# Create your views here.
def user_check(request):
    u = get_user_model()
    if u.objects.count() > 0:
        if request.user.is_authenticated:
            return redirect('index')
        return redirect('login')
    else:
        if request.method == "POST":
            form = AdminSignupForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('index')
        else:
            form = AdminSignupForm()
        return render(request, 'registration/first_time_signup.html', {'form': form})


def login_user(request):
    logout(request)
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = get_user_model().objects.filter(username=username).get()
            if not user.is_active:
                return render(request, 'app/blocked.html', {'user': user})
        except User.DoesNotExist:
            pass

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('index')
        else:
            context['error'] = "Invalid user name or password"
    return render(request, 'registration/login.html')


@login_required
def logout_user(request):
    logout(request)
    return redirect('/')


@login_required
def index(request):
    context = {}
    template = 'app/dashboard.html'

    earning = 0
    spent = 0
    inventory = 0

    if Order.objects.count() > 0:
        today_orders = Order.objects.filter(created_at__date=timezone.now(), is_completed=True)
        context['today_orders'] = len(today_orders)

        for order in today_orders:
            earning += order.get_grand_total()
        context['today_earning'] = earning

    if Expense.objects.count() > 0:
        today_spent = Expense.objects.filter(created_at__date=timezone.now())
        for expense in today_spent:
            spent += expense.total_bill()
        context['today_spent'] = spent

    if InventoryIn.objects.count() > 0:
        today_inventory = InventoryIn.objects.filter(created_at__date=timezone.now())
        for i in today_inventory:
            inventory += i.total_bill()
        context['today_inventory'] = inventory

    if OrderItems.objects.count() > 0:
        most_selling_item_list = OrderItems.objects.values('item').annotate(item_count=Count('item')).order_by(
            '-item_count')

        most_popular_item_list = OrderItems.objects.values('item').annotate(s=Sum('item_quantity')).order_by('-s')

        if len(most_selling_item_list) > 0:
            most_selling_item_id = most_selling_item_list[0]['item']
            most_selling_item = Item.objects.filter(pk=most_selling_item_id).get()
            context['most_selling_item'] = most_selling_item

            most_selling_item_is(most_selling_item)

        if len(most_popular_item_list) > 0:
            most_popular_item_id = most_popular_item_list[0]['item']
            most_popular_item = Item.objects.filter(pk=most_popular_item_id).get()
            context['most_popular_item'] = most_popular_item

            most_selling_item_is(most_popular_item)

    if Order.objects.count() > 0:
        if Table.objects.count() > 0:
            most_favorite_table_id = \
                Order.objects.values_list('order_table').annotate(c=Count('order_table')).order_by('-c')[0][0]
            most_favorite_table = Table.objects.filter(pk=most_favorite_table_id).get()
            context['most_favorite_table'] = most_favorite_table

    if earning != 0 and spent != 0:
        result = earning - spent
        if result > 0:
            profit = result
            context['today_profit'] = profit
        else:
            loss = -(result)
            context['today_loss'] = loss

    return render(request, template, context)


@login_required
def menu(request):
    template = 'app/menu.html'
    context = {}

    categories = ItemCategory.objects.all()
    tables = Table.objects.all()

    context['category_list'] = categories
    context['table_list'] = tables
    return render(request, template, context)


# ---------------------------------------------------
#
#                   ORDERs
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class OrderList(ListView):
    model = Order


@login_required
def order_new(request):
    if request.method == 'POST':
        print("------------------------------------")
        print(request.POST)
        table_pk = request.POST.get('menu-table')
        # discount = int(request.POST.get('discount'))
        menu_items = request.POST.getlist('menu-item')
        menu_item_quantity = request.POST.getlist('menu-item-quantity')
        menu_extra = request.POST.getlist('menu-extra')
        waiter = request.POST.get('waiter')

        print(menu_extra)

        table = Table.objects.filter(pk=table_pk).get()
        order = Order()
        order.order_table = table;
        order.waiter = waiter
        # order.discount = discount;

        order_items = []
        total_bill = 0

        for i, item_id in enumerate(menu_items):
            pk = int(item_id)
            item = Item.objects.filter(pk=pk).get()
            if item.is_never_sold:
                item.is_never_sold = False
                item.save()

            total_bill += (item.price * int(menu_item_quantity[i]))

            order_item = OrderItems()
            order_item.item = item
            order_item.item_quantity = int(menu_item_quantity[i])
            order_item.item_extra = menu_extra[i]
            order_item.charges = item.price

            order_items.append(order_item)

        # total_bill = total_bill - (total_bill * (discount / 100))
        order.total_bill = total_bill
        order.placed_at = timezone.now()
        order.save()

        for order_item in order_items:
            order_item.order = order
            order_item.save()

        return redirect('order-waiting-que')


def order_edit(request, pk):
    context = {}
    order = Order.objects.filter(pk=pk).get()
    context['order'] = order

    if request.method == "POST":
        print('------------------changing order')
        table_pk = request.POST.get('menu-table')
        menu_items = request.POST.getlist('menu-item')
        menu_item_quantity = request.POST.getlist('menu-item-quantity')
        menu_extra = request.POST.getlist('menu-extra')
        waiter = request.POST.get('waiter')

        table = Table.objects.filter(pk=table_pk).get()
        order = Order.objects.filter(pk=pk).get()
        order.order_table = table;
        order.waiter = waiter
        # order.discount = discount;

        order_items = []
        total_bill = 0

        for i, item_id in enumerate(menu_items):
            pk = int(item_id)
            item = Item.objects.filter(pk=pk).get()
            if item.is_never_sold:
                item.is_never_sold = False
                item.save()

            total_bill += (item.price * int(menu_item_quantity[i]))

            order_item = OrderItems()
            order_item.item = item
            order_item.item_quantity = int(menu_item_quantity[i])
            order_item.item_extra = menu_extra[i]
            order_item.charges = item.price

            order_items.append(order_item)

        # total_bill = total_bill - (total_bill * (discount / 100))
        order.total_bill = total_bill
        order.orderitems_set.all().delete()
        order.save()

        for order_item in order_items:
            order_item.order = order
            order_item.save()

        if order.is_ready:
            return redirect('order-ready-que')
        elif order.is_served:
            return redirect('order-served-que')
        elif order.is_waiting:
            return redirect('order-waiting-que')

    categories = ItemCategory.objects.all()
    tables = Table.objects.all()

    context['category_list'] = categories
    context['table_list'] = tables
    return render(request, 'app/menu_edit.html', context)


@login_required
def order_ready(request, pk):
    order = Order.objects.filter(pk=pk).get()
    order.is_ready = True
    order.ready_at = timezone.now()
    order.is_cancelled = False
    order.is_completed = False
    order.is_served = False
    order.is_waiting = False
    order.save()

    return redirect('order-ready-que')


@login_required
def order_served(request, pk):
    order = Order.objects.filter(pk=pk).get()
    order.is_ready = False
    order.is_cancelled = False
    order.is_completed = False
    order.is_served = True
    order.served_at = timezone.now()
    order.is_waiting = False
    order.save()

    return redirect('order-served-que')


QUOTES = [
    "Be good to people for no reason",
    "People who love to EAT are always the best people",
    "Each day has a color, an Aroma",
    "All you need is love. But a little chocolate now and then doesn't hurt",
]

NIGHT_QUOTES = [
    "After a good dinner one can forgive anybody, even one's own relations"
]


@login_required
def order_completed(request, pk):
    if request.method == "POST":
        order = Order.objects.filter(pk=pk).get()

        if not order.is_completed:
            discount = request.POST.get('discount')
            service_charges = request.POST.get('service_charges')
            custom_amount = request.POST.get('custom_amount')
            is_print = request.POST.get('print')

            order.discount = int(discount)
            order.service_charges = int(service_charges)
            order.custom_amount = int(custom_amount)

            total_bill = order.total_bill
            #grand_total = total_bill - (total_bill * (int(discount) / 100))
            grand_total = order.get_grand_total()

            order.grand_total = grand_total


            order.is_ready = False
            order.is_cancelled = False
            order.is_completed = True
            order.is_served = False
            order.is_waiting = False

            order.is_active = False
            order.completed_at = timezone.now()
            order.save()

            if is_print:
                return render(request, 'app/print.html', {'order': order})
        else:
            return render(request, 'app/print.html', {'order': order})

    # print bill
    return redirect('order-completed-que')


@login_required
def order_cancel(request, pk):
    order = Order.objects.filter(pk=pk).get()

    if request.method == "POST":
        reason = request.POST.get('reason')

        order_items = order.orderitems_set.all()
        for oi in order_items:
            item = oi.item
            if item.orderitems_set.all().count() == 1:
                item.is_never_sold = True
                item.save()

        order.cancel_reason = reason
        order.is_ready = False
        order.is_cancelled = True
        order.is_completed = False
        order.is_served = False
        order.is_waiting = False
        order.is_active = False
        order.save()

        return redirect('order-waiting-que')

    return render(request, 'app/order_cancel.html', {'order': order})


@login_required
def order_waiting(request):
    orders = Order.objects.filter(is_waiting=True)
    context = {}
    context['page'] = 'w'
    context['object_list'] = orders
    return render(request, 'app/order_list.html', context)


@login_required
def order_ready_que(request):
    orders = Order.objects.filter(is_ready=True)
    context = {}
    context['page'] = 'r'
    context['object_list'] = orders
    return render(request, 'app/order_list.html', context)


@login_required
def order_served_que(request):
    orders = Order.objects.filter(is_served=True)
    context = {}
    context['page'] = 's'
    context['object_list'] = orders
    return render(request, 'app/order_list.html', context)


@login_required
def order_cancelled_que(request):
    orders = Order.objects.filter(is_cancelled=True)
    context = {}
    context['page'] = 'c'
    context['object_list'] = orders
    return render(request, 'app/order_list.html', context)


@login_required
def order_completed_que(request):
    orders = Order.objects.filter(is_completed=True)
    context = {}
    context['page'] = 'cd'
    context['object_list'] = orders
    return render(request, 'app/order_list.html', context)


@login_required
def order_today(request):
    orders = Order.objects.filter(created_at__date=timezone.now())
    context = {}
    context['page'] = 'ot'
    context['object_list'] = orders
    return render(request, 'app/order_list.html', context)


class OrderExportView(ExcelView):
    model = Order


# ---------------------------------------------------
#
#                   TABLEs
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class TableList(ListView):
    model = Table


@method_decorator([login_required], name='dispatch')
class TableCreate(SuccessMessageMixin, CreateView):
    model = Table
    form_class = TableForm
    success_message = "New Table was created successfully"


@method_decorator([login_required], name='dispatch')
class TableUpdate(UpdateView):
    model = Table
    form_class = TableForm


@method_decorator([login_required], name='dispatch')
class TableDelete(DeleteView):
    model = Table
    success_url = reverse_lazy('table-list')


# ---------------------------------------------------
#
#                   ITEMS
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class ItemList(ListView):
    model = Item

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        try:
            context['categories'] = ItemCategory.objects.all()
            context['most_selling'] = MostSellingItem.objects.filter(pk=1).get().item.id
        except MostSellingItem.DoesNotExist:
            context['most_selling'] = -1

        return context


@method_decorator([login_required], name='dispatch')
class ItemCreate(SuccessMessageMixin, CreateView):
    model = Item
    form_class = ItemForm
    success_message = "New Item was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ic = ItemCategory.objects.all()
        context['item_categories'] = ic if ic.count() > 0 else None
        return context


@method_decorator([login_required], name='dispatch')
class ItemUpdate(UpdateView):
    model = Item
    form_class = ItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ic = ItemCategory.objects.all()
        context['item_categories'] = ic if ic.count() > 0 else None
        return context


from django.db.models import ProtectedError


@method_decorator([login_required], name='dispatch')
class ItemDelete(DeleteView):
    model = Item
    success_url = reverse_lazy('item-list')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError:
            return render(request, 'app/cant_delete.html', {'item': self.model})


@login_required
def add_to_order(request):
    pk = request.GET.get('id')
    item = Item.objects.filter(pk=pk).get()
    return render(request, 'app/item_add_to_order.html', {'item': item})


def most_selling_item_is(item):
    already_exists = MostSellingItem.objects.filter(item=item).exists()
    if not already_exists:
        try:
            # save each item for day wise reporting
            most_selling_db = MostSellingItem.objects.filter(pk=1).get()
            most_selling_db.item = item
            most_selling_db.save()
        except MostSellingItem.DoesNotExist:
            most_selling_db = MostSellingItem()
            most_selling_db.item = item
            most_selling_db.save()


@login_required
def item_rating(request):
    order_rating = OrderItems.objects.values_list('item').annotate(c=Count('item')).order_by('-c')
    item_list = []
    for rating in order_rating:
        item = Item.objects.filter(pk=rating[0]).get()
        t = (item, rating[1])
        item_list.append(t)

    return render(request, 'app/item_rating_list.html', {'object_list': item_list})

@login_required
def item_rating_month(request, month, year):
    items = OrderItems.objects.filter(created_at__month=month, created_at__year=year)
    order_rating = items.values_list('item').annotate(c=Count('item')).order_by('-c')
    item_list = []
    for rating in order_rating:
        item = Item.objects.filter(pk=rating[0]).get()
        t = (item, rating[1])
        item_list.append(t)

    return render(request, 'app/item_rating_list.html', {'object_list': item_list})


# ---------------------------------------------------
#
#                   ITEM CATEGORY
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class ItemCategoryList(ListView):
    model = ItemCategory


@method_decorator([login_required], name='dispatch')
class ItemCategoryCreate(SuccessMessageMixin, CreateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    success_message = "New Item Category was created successfully"


@method_decorator([login_required], name='dispatch')
class ItemCategoryUpdate(UpdateView):
    model = ItemCategory
    form_class = ItemCategoryForm


@method_decorator([login_required], name='dispatch')
class ItemCategoryDelete(DeleteView):
    model = ItemCategory
    success_url = reverse_lazy('item-category-list')


# ---------------------------------------------------
#
#                   INVENTORY CATEGORY
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class InventoryCategoryList(ListView):
    model = InventoryCategory


@method_decorator([login_required], name='dispatch')
class InventoryCategoryCreate(SuccessMessageMixin, CreateView):
    model = InventoryCategory
    form_class = InventoryCategoryForm
    success_message = "New inventory Category was created successfully"


@method_decorator([login_required], name='dispatch')
class InventoryCategoryUpdate(UpdateView):
    model = InventoryCategory
    form_class = InventoryCategoryForm


@method_decorator([login_required], name='dispatch')
class InventoryCategoryDelete(DeleteView):
    model = InventoryCategory
    success_url = reverse_lazy('inventory-category-list')


# ---------------------------------------------------
#
#                   INVENTORY
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class InventoryList(ListView):
    model = Inventory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ic = InventoryCategory.objects.all()
        context['inventory_categories'] = ic
        return context


@method_decorator([login_required], name='dispatch')
class InventoryCreate(SuccessMessageMixin, CreateView):
    model = Inventory
    form_class = InventoryForm
    success_message = "New inventory was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ic = InventoryCategory.objects.all()
        context['inventory_categories'] = ic if ic.count() > 0 else None
        return context


@method_decorator([login_required], name='dispatch')
class InventoryUpdate(UpdateView):
    model = Inventory
    form_class = InventoryForm

    # changes were created on 30 Sep, 2018, at 11:12 Am
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ic = InventoryCategory.objects.all()
        context['inventory_categories'] = ic if ic.count() > 0 else None
        return context


@method_decorator([login_required], name='dispatch')
class InventoryDelete(DeleteView):
    model = Inventory
    success_url = reverse_lazy('inventory-list')


@login_required
def add_to_inventory_item(request, pk):
    inventory = Inventory.objects.filter(pk=pk).get()
    context = {}
    context['inventory'] = inventory
    context['page'] = "add"

    if request.method == "POST":
        quantity = request.POST.get('quantity')
        if quantity != "":
            inventory.quantity += int(quantity)
            inventory.save()

            inventory_in = InventoryIn()
            inventory_in.name = inventory.name
            inventory_in.unit = inventory.unit
            inventory_in.category = inventory.category
            inventory_in.description = inventory.description
            inventory_in.image = inventory.image
            inventory_in.quantity = quantity
            inventory_in.price = inventory.price
            inventory_in.save()

            return redirect('inventory-list')

    return render(request, 'app/inventory_add_to.html', context)


@login_required
def issue_inventory_to(request, pk):
    inventory = Inventory.objects.filter(pk=pk).get()
    context = {}
    context['inventory'] = inventory
    context['page'] = "issue"

    if request.method == "POST":
        quantity = request.POST.get('quantity')
        issued_to = request.POST.get('issued_to')
        if quantity != "":
            inventory.quantity -= int(quantity)

            if inventory.quantity < 0:
                inventory.quantity = 0;

            inventory.save()

            inventory_out = InventoryOut()
            inventory_out.name = inventory.name
            inventory_out.unit = inventory.unit
            inventory_out.category = inventory.category
            inventory_out.description = inventory.description
            inventory_out.image = inventory.image
            inventory_out.issued_to = issued_to
            inventory_out.quantity = quantity
            inventory_out.price = inventory.price
            inventory_out.save()

            return redirect('inventory-list')

    return render(request, 'app/inventory_issue_to.html', context)


@login_required
def return_inventory_item(request, pk):
    inventory = Inventory.objects.filter(pk=pk).get()
    context = {}
    context['inventory'] = inventory
    context['page'] = "return"

    if request.method == "POST":
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')
        print("------------------------- Returning")
        if quantity != "":
            inventory.quantity -= int(quantity)

            if inventory.quantity < 0:
                inventory.quantity = 0;

            inventory.save()

            inventory_out = InventoryOut()
            inventory_out.name = inventory.name
            inventory_out.unit = inventory.unit
            inventory_out.category = inventory.category
            inventory_out.description = inventory.description
            inventory_out.image = inventory.image
            inventory_out.is_returned = True
            inventory_out.reason = reason
            inventory_out.quantity = quantity
            inventory_out.price = inventory.price
            inventory_out.save()

            return redirect('inventory-list')

    return render(request, 'app/inventory_return_to.html', context)


@login_required
def inventory_out_of_stock(request):
    template = 'app/inventory_out_of_stock.html'
    context = {}

    inventory = Inventory.objects.filter(quantity=0).all()
    context['object_list'] = inventory

    return render(request, template, context)


@login_required
def inventory_in(request):
    inventory = InventoryIn.objects.all().order_by('-created_at')
    return render(request, 'app/inventory_in_list.html', {'object_list': inventory})


@login_required
def inventory_out(request):
    inventory = InventoryOut.objects.all().order_by('-created_at')
    return render(request, 'app/inventory_out_list.html', {'object_list': inventory})


@login_required
def inventory_ratings(request):
    inventory_rating = InventoryOut.objects.values_list('name').annotate(c=Count('name')).order_by('-c')
    inventory_list = []
    for rating in inventory_rating:
        item = InventoryOut.objects.filter(name=rating[0]).first()
        t = (item, rating[1])
        inventory_list.append(t)

    return render(request, 'app/inventory_rating_list.html', {'object_list': inventory_list})


@login_required
def inventory_history(request):
    history = Inventory.history.all()
    context = {}
    context['object_list'] = history
    context['page'] = 'history'
    return render(request, 'app/inventory_list.html', context)


# ---------------------------------------------------
#
#                   EXPENSE CATEGORY
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class ExpenseCategoryList(ListView):
    model = ExpenseCategory


@method_decorator([login_required], name='dispatch')
class ExpenseCategoryCreate(SuccessMessageMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    success_message = "New expense Category was created successfully"


@method_decorator([login_required], name='dispatch')
class ExpenseCategoryUpdate(UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm


@method_decorator([login_required], name='dispatch')
class ExpenseCategoryDelete(DeleteView):
    model = ExpenseCategory
    success_url = reverse_lazy('expense-category-list')


# ---------------------------------------------------
#
#                   EXPENSEs
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class ExpenseList(ListView):
    model = Expense


@method_decorator([login_required], name='dispatch')
class ExpenseCreate(SuccessMessageMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    success_message = "New expense was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ex = ExpenseCategory.objects.all()
        context['ex_categories'] = ex if ex.count() > 0 else None
        return context


@method_decorator([login_required], name='dispatch')
class ExpenseUpdate(UpdateView):
    model = Expense
    form_class = ExpenseForm


@method_decorator([login_required], name='dispatch')
class ExpenseDelete(DeleteView):
    model = Expense
    success_url = reverse_lazy('expense-list')


# ---------------------------------------------------
#
#                   EMPLOYEEs
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class EmployeeList(ListView):
    model = Employee


@method_decorator([login_required], name='dispatch')
class EmployeeCreate(SuccessMessageMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    success_message = "New Table was created successfully"


@method_decorator([login_required], name='dispatch')
class EmployeeUpdate(UpdateView):
    model = Employee
    form_class = EmployeeForm


@method_decorator([login_required], name='dispatch')
class EmployeeDelete(DeleteView):
    model = Employee
    success_url = reverse_lazy('employee-list')


# ---------------------------------------------------
#
#                   EMPLOYEE EXPENSEs
#
# ---------------------------------------------------
@method_decorator([login_required], name='dispatch')
class EmployeeExpenseList(ListView):
    model = EmployeeExpense


@method_decorator([login_required], name='dispatch')
class EmployeeExpenseCreate(SuccessMessageMixin, CreateView):
    model = EmployeeExpense
    form_class = EmployeeExpenseForm
    success_message = "New Table was created successfully"


@method_decorator([login_required], name='dispatch')
class EmployeeExpenseUpdate(UpdateView):
    model = EmployeeExpense
    form_class = EmployeeExpenseForm


@method_decorator([login_required], name='dispatch')
class EmployeeExpenseDelete(DeleteView):
    model = EmployeeExpense
    success_url = reverse_lazy('employee-expense-list')


# ---------------------------------------------------
#
#                   USERs
#
# ---------------------------------------------------
@login_required
@admin_required
def signup_admin(request):
    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-list')

    else:
        form = AdminSignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
@admin_required
def signup_manager(request):
    if request.method == "POST":
        form = ManagerSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-list')

    else:
        form = ManagerSignupForm()
    return render(request, 'registration/manager_signup.html', {'form': form})


@login_required
@admin_required
def signup_inventory_manager(request):
    if request.method == "POST":
        form = InventoryManagerSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-list')

    else:
        form = InventoryManagerSignupForm()
    return render(request, 'registration/inventory_manager_signup.html', {'form': form})


@login_required
@admin_required
def signup_staff(request):
    if request.method == "POST":
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-list')

    else:
        form = StaffSignupForm()
    return render(request, 'registration/staff_signup.html', {'form': form})


class AdminSignUpView(CreateView):
    model = User
    form_class = AdminSignupForm
    template_name = 'registration/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'admin'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('dashboard')


@method_decorator([login_required, admin_required], name='dispatch')
class ManagerSignUpView(CreateView):
    model = User
    form_class = AdminSignupForm
    template_name = ''

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'manager'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('dashboard')


@method_decorator([login_required, admin_required], name='dispatch')
class InventoryManagerSignUpView(CreateView):
    model = User
    form_class = AdminSignupForm
    template_name = ''

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'inventory_manager'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('dashboard')


@method_decorator([login_required, admin_required], name='dispatch')
class StaffSignUpView(CreateView):
    model = User
    form_class = AdminSignupForm
    template_name = ''

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'staff'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('dashboard')


@login_required
@admin_required
def get_user_list(request):
    u = get_user_model()
    users = u.objects.all()
    return render(request, 'app/users_list.html', context={'object_list': users})


@login_required
@admin_required
def activate_user(request, pk):
    u = get_user_model()
    user = u.objects.filter(pk=pk).get()
    user.is_active = True
    user.save()
    return redirect('user-list')


@login_required
@admin_required
def deactivate_user(request, pk):
    u = get_user_model()
    user = u.objects.filter(pk=pk).get()
    user.is_active = False
    user.save()
    return redirect('user-list')


@login_required
@admin_required
def user_active_list(request):
    u = get_user_model()
    users = u.objects.filter(is_active=True)
    return render(request, 'app/users_list.html', context={'object_list': users})


@login_required
@admin_required
def user_blocked_list(request):
    u = get_user_model()
    users = u.objects.filter(is_active=False)
    return render(request, 'app/users_list.html', context={'object_list': users})


# ---------------------------------------------------
#
#                   REPORTs
#
# ---------------------------------------------------
from django.db.models import Avg, Max, Min, F
from time import strftime


def report_daily_index(request):
    return render(request, 'app/archive/archive_index_daily.html')


# ---------------------------------------------------
#
#                   DAILY REPORT
#
# ---------------------------------------------------
def report_daily(request, day, month, year):
    # day = int(day)
    context = {}
    context['orders'] = orders = Order.objects.filter(created_at__day=day,
            created_at__month=month,
            created_at__year=year)

    if orders.count() > 0:
        # Today Peak Hour
        pre_count = 0
        peak_hour = 0
        for x in range(24):
            hour = orders.filter(created_at__hour=x)
            if hour.count() > 0:
                if pre_count < len(hour):
                    pre_count = len(hour)
                    peak_hour = x

        context['peak_hour'] = orders.filter(created_at__hour=peak_hour).values('created_at').all()[0][
            'created_at'].time().strftime("%I:00 %p")

        # Today Top Order
        top_order = orders.values('id').annotate(m=Max('total_bill')).order_by('-m')[0]['id']
        context['top_order'] = Order.objects.filter(pk=top_order).get()

        # Today Lowest Order
        min_order = orders.filter(is_completed=True).values('id').annotate(m=Min('total_bill')).order_by('m')[0]['id']
        context['min_order'] = Order.objects.filter(pk=min_order).get()

        # Avg sale
        context['avg_sales'] = orders.aggregate(Avg('grand_total'))['grand_total__avg']

        # Total Sale
        context['total_sale'] = orders.aggregate(Sum('grand_total'))['grand_total__sum']

    if OrderItems.objects.count() > 0:
        # Today Most Demanding Item
        most_popular_item_list = OrderItems.objects.filter(created_at__day=day).values('item').annotate(
            s=Sum('item_quantity')).order_by('-s')

        if len(most_popular_item_list) > 0:
            most_popular_item_id = most_popular_item_list[0]['item']
            most_popular_item = Item.objects.filter(pk=most_popular_item_id).get()
            context['most_popular_item'] = most_popular_item

    if InventoryOut.objects.count() > 0:
        # Inventory Out
        inventory_out = InventoryOut.objects.filter(created_at__day=day, created_at__month=month, created_at__year=year)
        context['inventory_out'] = inventory_out
        if inventory_out.count() > 0:
            context['inventory_used'] = inventory_out.count()
            context['inventory_expended'] = inventory_out.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if InventoryIn.objects.count() > 0:
        # Inventory In
        inventory_in = InventoryIn.objects.filter(created_at__day=day)
        context['inventory_in'] = inventory_in
        if inventory_in.count() > 0:
            context['inventory_added'] = inventory_in.count()

    if Inventory.objects.count() > 0:
        # Inventory Worth
        inventory = Inventory.objects.filter(created_at__day=day)
        context['inventory'] = inventory
        context['inventory_worth'] = inventory.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if Expense.objects.count() > 0:
        # Expenses
        expenes = Expense.objects.filter(created_at__day=day)
        context['expenses'] = expenes
        context['expense_worth'] = expenes.aggregate(t=Sum(F('price')*F('quantity')))['t']

    return render(request, 'app/archive/report_daily.html', context)


# ---------------------------------------------------
#
#                   Monthly REPORT
#
# ---------------------------------------------------
def report_monthly(request, month, year):
    context = {}
    context['orders'] = orders = Order.objects.filter(created_at__month=month, created_at__year=year)


    if orders.count() > 0:
        # Today Peak Hour
        pre_count = 0
        peak_hour = 0
        for x in range(24):
            hour = orders.filter(created_at__hour=x)
            if hour.count() > 0:
                if pre_count < len(hour):
                    pre_count = len(hour)
                    peak_hour = x

        context['peak_hour'] = orders.filter(created_at__hour=peak_hour).values('created_at').all()[0][
            'created_at'].time().strftime("%I:00 %p")

        # Today Top Order
        top_order = orders.values('id').annotate(m=Max('total_bill')).order_by('-m')[0]['id']
        context['top_order'] = Order.objects.filter(pk=top_order).get()

        # Today Lowest Order
        min_order = orders.filter(is_completed=True).values('id').annotate(m=Min('total_bill')).order_by('m')[0]['id']
        context['min_order'] = Order.objects.filter(pk=min_order).get()

        # Avg sale
        context['avg_sales'] = orders.aggregate(Avg('total_bill'))['total_bill__avg']

        # Total Sale
        context['total_sale'] = orders.aggregate(Sum('grand_total'))['grand_total__sum']

    if OrderItems.objects.count() > 0:
        # Today Most Demanding Item
        most_popular_item_list = OrderItems.objects.filter(created_at__month=month).values('item').annotate(
            s=Sum('item_quantity')).order_by('-s')

        if len(most_popular_item_list) > 0:
            most_popular_item_id = most_popular_item_list[0]['item']
            most_popular_item = Item.objects.filter(pk=most_popular_item_id).get()
            context['most_popular_item'] = most_popular_item

    if InventoryOut.objects.count() > 0:
        # Inventory Out
        inventory_out = InventoryOut.objects.filter(created_at__month=month)
        context['inventory_out'] = inventory_out
        if inventory_out.count() > 0:
            context['inventory_used'] = inventory_out.count()
            context['inventory_expended'] = inventory_out.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if InventoryIn.objects.count() > 0:
        # Inventory In
        inventory_in = InventoryIn.objects.filter(created_at__month=month)
        context['inventory_in'] = inventory_in
        if inventory_in.count() > 0:
            context['inventory_added'] = inventory_in.count()

    if Inventory.objects.count() > 0:
        # Inventory Worth
        inventory = Inventory.objects.filter(created_at__month=month)
        context['inventory'] = inventory
        context['inventory_worth'] = inventory.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if Expense.objects.count() > 0:
        # Expenses
        expenes = Expense.objects.filter(created_at__month=month)
        context['expenses'] = expenes
        context['expense_worth'] = expenes.aggregate(t=Sum(F('price')*F('quantity')))['t']

    return render(request, 'app/archive/report_monthly.html', context)


# ---------------------------------------------------
#
#                   Weekly REPORT
#
# ---------------------------------------------------
def report_weekly(request):
    week = timezone.now().isocalendar()[1]
    context = {}
    context['orders'] = orders = Order.objects.filter(created_at__week=week)

    if orders.count() > 0:
        # Today Peak Hour
        pre_count = 0
        peak_hour = 0
        for x in range(24):
            hour = orders.filter(created_at__hour=x)
            if hour.count() > 0:
                if pre_count < len(hour):
                    pre_count = len(hour)
                    peak_hour = x

        context['peak_hour'] = orders.filter(created_at__hour=peak_hour).values('created_at').all()[0][
            'created_at'].time().strftime("%I:00 %p")

        # Today Top Order
        top_order = orders.values('id').annotate(m=Max('total_bill')).order_by('-m')[0]['id']
        context['top_order'] = Order.objects.filter(pk=top_order).get()

        # Today Lowest Order
        min_order = orders.filter(is_completed=True).values('id').annotate(m=Min('total_bill')).order_by('m')[0]['id']
        context['min_order'] = Order.objects.filter(pk=min_order).get()

        # Avg sale
        context['avg_sales'] = orders.aggregate(Avg('total_bill'))['total_bill__avg']

        # Total Sale
        context['total_sale'] = orders.aggregate(Sum('grand_total'))['grand_total__sum']

    if OrderItems.objects.count() > 0:
        # Today Most Demanding Item
        most_popular_item_list = OrderItems.objects.filter(created_at__week=week).values('item').annotate(
            s=Sum('item_quantity')).order_by('-s')

        if len(most_popular_item_list) > 0:
            most_popular_item_id = most_popular_item_list[0]['item']
            most_popular_item = Item.objects.filter(pk=most_popular_item_id).get()
            context['most_popular_item'] = most_popular_item

    if InventoryOut.objects.count() > 0:
        # Inventory Out
        inventory_out = InventoryOut.objects.filter(created_at__week=week)
        context['inventory_out'] = inventory_out
        if inventory_out.count() > 0:
            context['inventory_used'] = inventory_out.count()
            context['inventory_expended'] = inventory_out.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if InventoryIn.objects.count() > 0:
        # Inventory In
        inventory_in = InventoryIn.objects.filter(created_at__week=week)
        context['inventory_in'] = inventory_in
        if inventory_in.count() > 0:
            context['inventory_added'] = inventory_in.count()

    if Inventory.objects.count() > 0:
        # Inventory Worth
        inventory = Inventory.objects.filter(created_at__week=week)
        context['inventory'] = inventory
        context['inventory_worth'] = inventory.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if Expense.objects.count() > 0:
        # Expenses
        expenes = Expense.objects.filter(created_at__week=week)
        context['expenses'] = expenes
        context['expense_worth'] = expenes.aggregate(t=Sum(F('price')*F('quantity')))['t']

    return render(request, 'app/archive/report_weekly.html', context)


# ---------------------------------------------------
#
#                   Yearly REPORT
#
# ---------------------------------------------------
def report_yearly(request, year):
    context = {}
    context['orders'] = orders = Order.objects.filter(created_at__year=year)

    if orders.count() > 0:
        # Today Peak Hour
        pre_count = 0
        peak_hour = 0
        for x in range(24):
            hour = orders.filter(created_at__hour=x)
            if hour.count() > 0:
                if pre_count < len(hour):
                    pre_count = len(hour)
                    peak_hour = x

        context['peak_hour'] = orders.filter(created_at__hour=peak_hour).values('created_at').all()[0][
            'created_at'].time().strftime("%I:00 %p")

        # Today Top Order
        top_order = orders.values('id').annotate(m=Max('total_bill')).order_by('-m')[0]['id']
        context['top_order'] = Order.objects.filter(pk=top_order).get()

        # Today Lowest Order
        min_order = orders.filter(is_completed=True).values('id').annotate(m=Min('total_bill')).order_by('m')[0]['id']
        context['min_order'] = Order.objects.filter(pk=min_order).get()

        # Avg sale
        context['avg_sales'] = orders.aggregate(Avg('total_bill'))['total_bill__avg']

        # Total Sale
        context['total_sale'] = orders.aggregate(Sum('grand_total'))['grand_total__sum']

    if OrderItems.objects.count() > 0:
        # Today Most Demanding Item
        most_popular_item_list = OrderItems.objects.filter(created_at__year=year).values('item').annotate(
            s=Sum('item_quantity')).order_by('-s')

        if len(most_popular_item_list) > 0:
            most_popular_item_id = most_popular_item_list[0]['item']
            most_popular_item = Item.objects.filter(pk=most_popular_item_id).get()
            context['most_popular_item'] = most_popular_item

    if InventoryOut.objects.count() > 0:
        # Inventory Out
        inventory_out = InventoryOut.objects.filter(created_at__year=year)
        context['inventory_out'] = inventory_out
        if inventory_out.count() > 0:
            context['inventory_used'] = inventory_out.count()
            context['inventory_expended'] = inventory_out.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if InventoryIn.objects.count() > 0:
        # Inventory In
        inventory_in = InventoryIn.objects.filter(created_at__year=year)
        context['inventory_in'] = inventory_in
        if inventory_in.count() > 0:
            context['inventory_added'] = inventory_in.count()

    if Inventory.objects.count() > 0:
        # Inventory Worth
        inventory = Inventory.objects.filter(created_at__year=year)
        context['inventory'] = inventory
        context['inventory_worth'] = inventory.aggregate(t=Sum(F('price')*F('quantity')))['t']

    if Expense.objects.count() > 0:
        # Expenses
        expenes = Expense.objects.filter(created_at__year=year)
        context['expenses'] = expenes
        context['expense_worth'] = expenes.aggregate(t=Sum(F('price')*F('quantity')))['t']

    return render(request, 'app/archive/report_yearly.html', context)





