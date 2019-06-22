from django.contrib import admin

# Register your models here.
from .models import Client, Product

admin.site.register(Product)
admin.site.register(Client)
