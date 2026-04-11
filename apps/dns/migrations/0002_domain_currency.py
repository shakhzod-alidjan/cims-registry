from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('dns', '0001_initial')]
    operations = [
        migrations.AddField(
            model_name='domain',
            name='currency',
            field=models.CharField(choices=[('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')],
                                   default='USD', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='domain',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14,
                                      null=True, verbose_name='Стоимость / год'),
        ),
        migrations.AddField(
            model_name='domainpayment',
            name='currency',
            field=models.CharField(choices=[('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')],
                                   default='USD', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='domainpayment',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14,
                                      null=True, verbose_name='Сумма'),
        ),
    ]
