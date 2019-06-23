# Generated by Django 2.2.2 on 2019-06-23 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("invoice", "0003_auto_20190623_1206")]

    operations = [
        migrations.AddField(
            model_name="returned",
            name="client",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="invoice.Client",
                verbose_name="invoice_client",
            ),
        )
    ]
