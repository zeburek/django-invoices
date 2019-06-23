from django.test import TestCase

from .models import Client, Invoice, Product, Released


class ProductTestCase(TestCase):
    def setUp(self) -> None:
        Product.objects.create(name="Test name 1", price=160)

    def test_product_string_representation(self):
        product = Product.objects.get(name="Test name 1")
        self.assertEquals(
            str(product), f"{product.name}, цена: {product.price}"
        )


class ClientTestCase(TestCase):
    def setUp(self) -> None:
        Client.objects.create(name="Test name 1")

    def test_client_string_representation(self):
        client = Client.objects.get(name="Test name 1")
        self.assertEquals(
            str(client), f"{client.name}"
        )


class ReleasedTestCase(TestCase):
    def setUp(self) -> None:
        client = Client.objects.create(name="Test")
        product = Product.objects.create(name="Test", price=160)
        invoice = Invoice.objects.create(client_id=client.id, date="2019-06-21", number=10)
        Released.objects.create(invoice_id=invoice.id, product_id=product.id, qty=10, discount=15)

    def test_client_string_representation(self):
        invoice = Invoice.objects.get(number=10)
        released = Released.objects.get(invoice_id=invoice.id)
        self.assertEquals(released.summary, 160 * 10 - (160 * 10 * 15 / 100))
