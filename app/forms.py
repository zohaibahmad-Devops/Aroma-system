from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import (Table, Item, ItemCategory, InventoryCategory, ExpenseCategory, Inventory, Expense, Employee,
                     EmployeeExpense, Recipe, User)


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('number', 'name', 'image')
        widgets = {
            'number': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Number of Counter in Store'}),
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Name of Counter'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'number': _('Counter Number'),
            'name': _('Counter Name (optional)'),
            'image': _('Image (Optional)'),
        }

        help_texts = {
            'name': _('Specify the number of Counter, which must be unique'),
            'name': _('Name of Counter if any'),
            'image': _('Image (Optional)'),
        }

        error_messages = {
            'number': {'required': _('The number of Counter is required')},
        }


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ('name', 'description', 'image')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Item Category Name'),
            'description': _('Item Category Description'),
            'image': _('Item Category Image'),
        }

        help_texts = {
            'name': _('The name for category and it will always be shown for Item to choose'),
            'description': _('Provide explanation or any extra information for your category'),
            'image': _('An image to make Category more clear'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'description': {'max-length': 'The description must be less then or equal to 300 character'},

        }

    def get_initial(self):
        initial = {'name': 'Test Pizza Name', 'description': 'Test description text'}
        return initial


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('name', 'price', 'category', 'description', 'image')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'category': forms.Select(attrs={'class': 'form-control', }),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Name'),
            'price': _('Price (Rs.)'),
            'category': _('Category'),
            'description': _('Description (Optional)'),
            'image': _('Image (Optional)'),
        }

        help_texts = {
            'name': _('Name'),
            'price': _('Price (Rs.)'),
            'category': _('Category'),
            'description': _('Description (Optional)'),
            'image': _('Image (Optional)'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'price': {'required': 'You must provide price for item'},
            'category': {'required': 'You must select category for item'},

        }


class InventoryCategoryForm(forms.ModelForm):
    class Meta:
        model = InventoryCategory
        fields = ('name', 'description', 'image')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Inventory Category Name'),
            'description': _('Inventory Category Description'),
            'image': _('Inventory Category Image'),
        }

        help_texts = {
            'name': _('The name for category and it will always be shown for Item to choose'),
            'description': _('Provide explanation or any extra information for your category'),
            'image': _('An image to make Category more clear'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'description': {'max-length': 'The description must be less then or equal to 300 character'},

        }

    def get_initial(self):
        initial = {'name': 'Test Inventory Name', 'description': 'Test description text'}
        return initial


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ('name', 'unit', 'price', 'category', 'description', 'quantity', 'image')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'unit': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'category': forms.Select(
                attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Inventory Item Name'),
            'unit': _('Inventory Item Unit'),
            'price': _('Inventory Item Price'),
            'category': _('Inventory Item Category'),
            'description': _('Inventory Item Description'),
            'quantity': _('Inventory Item Quantity'),
            'image': _('Inventory Item Image'),
        }

        help_texts = {
            'name': _('The name for category and it will always be shown for Item to choose'),
            'unit': _('The name for category and it will always be shown for Item to choose'),
            'price': _('Provide explanation or any extra information for your category'),
            'category': _('Provide explanation or any extra information for your category'),
            'description': _('Provide explanation or any extra information for your category'),
            'quantity': _('Provide explanation or any extra information for your category'),
            'image': _('An image to make Category more clear'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'unit': {'required': _('The name of category is required')},
            'price': {'required': _('The name of category is required')},
            'quantity': {'required': _('The name of category is required')},
        }

    def get_initial(self):
        initial = {'name': 'Test Inventory Name', 'description': 'Test description text'}
        return initial


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ('name', 'description', 'image')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Expense Category Name'),
            'description': _('Expense Category Description'),
            'image': _('Expense Category Image'),
        }

        help_texts = {
            'name': _('The name for category and it will always be shown for Item to choose'),
            'description': _('Provide explanation or any extra information for your category'),
            'image': _('An image to make Category more clear'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'description': {'max-length': 'The description must be less then or equal to 300 character'},

        }

    def get_initial(self):
        initial = {'name': 'Test Expense Name', 'description': 'Test description text'}
        return initial


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('name', 'price', 'category', 'description', 'quantity', 'image')
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'category': forms.Select(
                attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Expense Item Name'),
            'price': _('Expense Item Price'),
            'category': _('Expense Item Category'),
            'description': _('Expense Item Description'),
            'quantity': _('Expense Item Quantity'),
            'image': _('Expense Item Image'),
        }

        help_texts = {
            'name': _('The name for category and it will always be shown for Item to choose'),
            'price': _('Provide explanation or any extra information for your category'),
            'category': _('Provide explanation or any extra information for your category'),
            'description': _('Provide explanation or any extra information for your category'),
            'quantity': _('Provide explanation or any extra information for your category'),
            'image': _('An image to make Category more clear'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'price': {'required': _('The name of category is required')},
            'quantity': {'required': _('The name of category is required')},
        }

    def get_initial(self):
        initial = {'name': 'Test Inventory Name', 'description': 'Test description text'}
        return initial


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'name',
            'father_name',
            'contact',
            'email',
            'address',
            'joining_date',
            'leaving_date',
            'salary',
            'working_hours',
            'start_time',
            'off_time',
            'image',
        )
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'father_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'contact': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'joining_date': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'leaving_date': forms.DateInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'salary': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'working_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(
                attrs={'class': 'form-control', 'placeholder': 'Briefly explain this category'}),
            'off_time': forms.TimeInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'image': forms.FileInput(attrs={'class': 'form-control', }),
        }

        labels = {
            'name': _('Name'),
            'father_name': _('Father Name'),
            'contact': _('Contact (Mobile Number)'),
            'address': _('Address'),
            'joining_date': _('Joining Date'),
            'leaving_date': _('Leaving Date'),
            'salary': _('Salary (Rs.)'),
            'working_hours': _('Total Working Hours'),
            'start_time': _('Start Timings'),
            'off_time': _('Off Timings'),
            'image': _('Image'),
        }

        help_texts = {
            'name': _('The name for category and it will always be shown for Item to choose'),
            'father_name': _('Provide explanation or any extra information for your category'),
            'contact': _('Provide explanation or any extra information for your category'),
            'joining_date': _('Provide explanation or any extra information for your category'),
            'leaving_date': _('Provide explanation or any extra information for your category'),
            'salary': _('An image to make Category more clear'),
            'working_hours': _('An image to make Category more clear'),
            'start_time': _('An image to make Category more clear'),
            'off_time': _('An image to make Category more clear'),
            'image': _('An image to make Category more clear'),
        }

        error_messages = {
            'name': {'required': _('The name of category is required')},
            'father_name': {'required': _('The name of category is required')},
            'contact': {'required': _('The name of category is required')},
        }

    def get_initial(self):
        initial = {'name': 'Test Inventory Name', 'description': 'Test description text'}
        return initial


class EmployeeExpenseForm(forms.ModelForm):
    class Meta:
        model = EmployeeExpense
        fields = (
            'employee',
            'paid_salary',
            'bonus',
            'penalty',
            'penalty_reason',
            'paid_type',
        )
        widgets = {
            'employee': forms.Select(
                attrs={'class': 'form-control'}),
            'paid_salary': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'bonus': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'penalty': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'penalty_reason': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Self explanatory name for category'}),
            'paid_type': forms.HiddenInput(),
        }

        labels = {
            'employee': _('Select Employee'),
            'paid_salary': _('Salary (Rs.'),
            'bonus': _('Bonus (optional)'),
            'penalty': _('Penalty Amount'),
            'penalty_reason': _('Penalty Reason'),
        }

        help_texts = {
            'employee': _('Select Employee'),
            'paid_salary': _('Salary (Rs.'),
            'bonus': _('Bonus (optional)'),
            'penalty': _('Penalty Amount'),
            'penalty_reason': _('Penalty Reason'),
        }

        error_messages = {
            'employee': {'required': _('The name of category is required')},
            'paid_salary': {'required': _('The name of category is required')},
        }

    def get_initial(self):
        initial = {'name': 'Test Inventory Name', 'description': 'Test description text'}
        return initial


class AdminSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=254, required=True, help_text='Your valid email address',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self):
        user = super().save(commit=False)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save()
        return user


class ManagerSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=254, required=True, help_text='Your valid email address',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self):
        user = super().save(commit=False)
        user.is_manager = True
        user.is_staff = True
        user.save()
        return user


class InventoryManagerSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=254, required=True, help_text='Your valid email address',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self):
        user = super().save(commit=False)
        user.is_inventory_manager = True
        user.save()
        return user


class StaffSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=254, required=True, help_text='Your valid email address',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self):
        user = super().save(commit=False)
        user.is_staff = True
        user.save()
        return user
