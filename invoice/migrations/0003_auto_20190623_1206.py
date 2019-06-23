# Generated by Django 2.2.2 on 2019-06-23 09:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20190621_2302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'client_model', 'verbose_name_plural': 'clients_model'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'product_model', 'verbose_name_plural': 'products_model'},
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.CharField(max_length=200, verbose_name='client_name'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoice.Client', verbose_name='invoice_client'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created_at'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date',
            field=models.DateField(verbose_name='invoice_date'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='number',
            field=models.IntegerField(verbose_name='invoice_number'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='updated_at'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200, verbose_name='product_name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(verbose_name='product_price'),
        ),
        migrations.AlterField(
            model_name='released',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created_at'),
        ),
        migrations.AlterField(
            model_name='released',
            name='discount',
            field=models.IntegerField(default=0, verbose_name='released_discount'),
        ),
        migrations.AlterField(
            model_name='released',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoice.Invoice', verbose_name='released_invoice'),
        ),
        migrations.AlterField(
            model_name='released',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoice.Product', verbose_name='released_product'),
        ),
        migrations.AlterField(
            model_name='released',
            name='qty',
            field=models.IntegerField(verbose_name='released_qty'),
        ),
        migrations.AlterField(
            model_name='released',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='updated_at'),
        ),
        migrations.CreateModel(
            name='Returned',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(verbose_name='returned_qty')),
                ('discount', models.IntegerField(default=0, verbose_name='returned_discount')),
                ('date', models.DateField(verbose_name='returned_date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invoice.Product', verbose_name='released_product')),
            ],
        ),
    ]
