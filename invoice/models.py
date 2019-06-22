from django.db import models
from django.urls import reverse


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name}, цена: {self.price}"


class Client(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"


class Invoice(models.Model):
    number = models.IntegerField()
    date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number} от {self.date} для {self.client}"

    def get_absolute_url(self):
        return reverse("invoice:details", kwargs={"pk": self.pk})


class Released(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    discount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def summary(self):
        summary = self.product.price * self.qty
        return summary - (summary * self.discount / 100)

    def get_absolute_url(self):
        return reverse("invoice:details", kwargs={"pk": self.invoice.pk})

    def __str__(self):
        return f"{self.product}  кол-во: {self.qty} скидка: {self.discount}%"
