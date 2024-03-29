from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("product_name"))
    price = models.FloatField(verbose_name=_("product_price"))

    class Meta:
        verbose_name = _("product_model")
        verbose_name_plural = _("products_model")

    def __str__(self):
        return f"{self.name}, цена: {self.price}"


class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("client_name"))

    class Meta:
        verbose_name = _("client_model")
        verbose_name_plural = _("clients_model")

    def __str__(self):
        return f"{self.name}"


class Invoice(models.Model):
    number = models.IntegerField(verbose_name=_("invoice_number"))
    date = models.DateField(verbose_name=_("invoice_date"))
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name=_("invoice_client")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created_at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("updated_at")
    )

    @property
    def released(self):
        return Released.objects.filter(invoice_id=self.id)

    @property
    def summary(self):
        return sum([i.summary for i in self.released])

    @property
    def qty(self):
        return sum([i.qty for i in self.released])

    def __str__(self):
        return f"{self.number} от {self.date} для {self.client}"

    def get_absolute_url(self):
        return reverse("invoice:details", kwargs={"pk": self.pk})


class Released(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, verbose_name=_("released_invoice")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("released_product")
    )
    qty = models.IntegerField(verbose_name=_("released_qty"))
    discount = models.IntegerField(
        default=0, verbose_name=_("released_discount")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created_at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("updated_at")
    )

    @property
    def summary(self):
        summary = self.product.price * self.qty
        return summary - (summary * self.discount / 100)

    def get_absolute_url(self):
        return reverse("invoice:details", kwargs={"pk": self.invoice.pk})

    def __str__(self):
        return f"{self.product}  кол-во: {self.qty} скидка: {self.discount}%"


class Returned(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("released_product")
    )
    client = models.ForeignKey(
        Client,
        default=None,
        on_delete=models.CASCADE,
        verbose_name=_("invoice_client"),
    )
    qty = models.IntegerField(verbose_name=_("returned_qty"))
    discount = models.IntegerField(
        default=0, verbose_name=_("returned_discount")
    )
    date = models.DateField(verbose_name=_("returned_date"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created_at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("updated_at")
    )

    @property
    def summary(self):
        summary = self.product.price * self.qty
        return summary - (summary * self.discount / 100)

    def get_absolute_url(self):
        return reverse("invoice:index")

    def __str__(self):
        return (
            f"Возврат товара: {self.product} "
            f"кол-во: {self.qty} скидка: {self.discount}%"
        )
