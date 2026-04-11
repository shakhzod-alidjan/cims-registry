from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('cloud', '0001_initial')]
    operations = [
        migrations.AddField(
            model_name='cloudserver',
            name='currency',
            field=models.CharField(choices=[('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')],
                                   default='USD', max_length=3, verbose_name='Валюта'),
        ),
        migrations.AddField(
            model_name='cloudserver',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14,
                                      null=True, verbose_name='Стоимость / мес'),
        ),
    ]
