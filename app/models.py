from django.db import models
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

USER = settings.AUTH_USER_MODEL


class Table(models.Model):
    """
    Table model to keep record of all available tables in Store
    """
    number = models.IntegerField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=30, unique=True, blank=True, null=True)
    is_favorite = models.BooleanField(default=False, blank=True, null=True)
    image = models.ImageField(upload_to="tables", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Table Number " + str(self.number)

    def get_absolute_url(self):
        return reverse('table-list')


class ItemCategory(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to="categories/items/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('item-category-list')


class Item(models.Model):
    """
    The model for Item to be stored
    """
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=300, null=True, blank=True)
    discount = models.IntegerField(default=0, null=True, blank=True)
    image = models.ImageField(upload_to="items/", null=True, blank=True)
    is_never_sold = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('item-list')


class MostSellingItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.item.name


class Order(models.Model):
    """
    The model for orders to keep all the record about an order
    """
    order_table = models.ForeignKey(Table, on_delete=models.PROTECT)
    is_served = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    is_waiting = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.CharField(max_length=300, null=True, blank=True)
    discount = models.IntegerField(default=0)
    service_charges = models.IntegerField(default=0)  # Added on 30 Sep
    placed_at = models.DateTimeField(blank=True, null=True)
    ready_at = models.DateTimeField(blank=True, null=True)
    served_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    total_bill = models.IntegerField()
    grand_total = models.IntegerField(blank=True, null=True)  # This needs to be must
    custom_amount = models.IntegerField(default=0)  # Added on 30 Sep
    complain = models.CharField(max_length=300, blank=True, null=True)
    suggestion = models.CharField(max_length=300, blank=True, null=True)
    waiter = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']

    def get_grand_total(self):
        if self.service_charges and self.service_charges != 0:
            return (self.total_bill + (self.total_bill * (self.service_charges / 100))) - (
                        self.total_bill * (self.discount / 100))
        return (self.total_bill - (self.total_bill * (self.discount / 100)))

    def __str__(self):
        return str(self.id) + ": Table " + str(self.order_table.number)

    def get_absolute_url(self):
        return reverse('order-list')

    def is_today(self):
        return self.created_at.day == timezone.now().day


class OrderItems(models.Model):
    """
    Add documents for orderItems
    """
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    item_extra = models.CharField(max_length=300)
    item_quantity = models.IntegerField()
    charges = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return "order ID: " + str(self.order.id)

    def get_grand_total(self):
        return self.item_quantity * self.item.price


class InventoryCategory(models.Model):
    """
    Add docs for InventoryCategory
    """
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to="categories/inventory/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('inventory-category-list')


class InventoryIn(models.Model):
    """
    Add docs for Inventory
    """
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=30, blank=True, null=True)  # undo nullify
    price = models.IntegerField()
    category = models.ForeignKey(InventoryCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=300, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to="inventory/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']

    def total_bill(self):
        return self.price * self.quantity

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('inventory-list')

    def get_grand_total(self):
        return self.price * self.quantity


class Inventory(models.Model):
    """
    Add docs for Inventory
    """
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=30, blank=True, null=True)  # undo nullify
    price = models.IntegerField()
    category = models.ForeignKey(InventoryCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=300, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to="inventory/", null=True, blank=True)
    is_out_of_stock = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def total_bill(self):
        return self.price * self.quantity

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('inventory-list')

    def get_grand_total(self):
        return self.price * self.quantity


class InventoryOut(models.Model):
    """
    Add docs for Inventory
    """
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=30, blank=True, null=True)  # undo nullify
    price = models.IntegerField()
    category = models.ForeignKey(InventoryCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=300, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to="inventory/", null=True, blank=True)
    issued_to = models.CharField(max_length=300, null=True, blank=True)
    reason = models.CharField(max_length=300, null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def total_bill(self):
        return self.price * self.quantity

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('inventory-list')

    def get_grand_total(self):
        return self.price * self.quantity


class Recipe(models.Model):
    """
    Add docs for Recipe
    """
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.item.name + ": " + self.inventory.name


class ExpenseCategory(models.Model):
    """
    Add docs for ExpenseCategory
    """
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300, null=True, blank=True)
    image = models.ImageField(upload_to="categories/expense/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('expense-category-list')


class Expense(models.Model):
    """
    Add docs for Expense
    """
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=300, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to="expenses/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def total_bill(self):
        return self.price * self.quantity

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('expense-list')


class Employee(models.Model):
    name = models.CharField(max_length=30)
    father_name = models.CharField(max_length=30)
    contact = models.CharField(max_length=30)
    email = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=30, blank=True, null=True)
    joining_date = models.DateField()
    leaving_date = models.DateField(blank=True, null=True)
    salary = models.IntegerField()
    working_hours = models.IntegerField()
    start_time = models.TimeField()
    off_time = models.TimeField()
    image = models.ImageField(upload_to="employees/", blank=True, null=True)
    is_fired = models.BooleanField(default=False)
    fire_reason = models.CharField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


class EmployeeExpense(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    paid_salary = models.IntegerField()
    bonus = models.IntegerField(blank=True, null=True)
    penalty = models.IntegerField(blank=True, null=True)
    penalty_reason = models.CharField(max_length=300, blank=True, null=True)
    paid_type = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


class User(AbstractUser):
    is_manager = models.BooleanField(default=False)
    is_inventory_manager = models.BooleanField(default=False)