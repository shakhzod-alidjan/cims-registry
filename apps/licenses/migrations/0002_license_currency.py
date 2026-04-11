from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('licenses', '0001_initial')]
    operations = [
        migrations.AddField(
            model_name='license',
            name='currency',
            field=models.CharField(choices=[('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')],
                                   default='USD', max_length=3, verbose_name='Валюта'),
        ),
    ]
