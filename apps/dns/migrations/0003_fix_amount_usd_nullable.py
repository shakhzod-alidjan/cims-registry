from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('dns', '0002_domain_currency')]
    operations = [
        migrations.AlterField(
            model_name='domainpayment',
            name='amount_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Сумма (USD)'),
        ),
    ]
