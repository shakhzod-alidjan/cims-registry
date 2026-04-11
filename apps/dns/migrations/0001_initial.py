from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registrar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Регистратор')),
                ('url', models.URLField(blank=True, verbose_name='Сайт')),
                ('contact_name', models.CharField(blank=True, max_length=200, verbose_name='Контакт')),
                ('contact_email', models.EmailField(blank=True, verbose_name='Email')),
            ],
            options={
                'verbose_name': 'Регистратор',
                'verbose_name_plural': 'Регистраторы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Домен')),
                ('registration_date', models.DateField(blank=True, null=True, verbose_name='Дата регистрации')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='Дата истечения')),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Стоимость / год (USD)')),
                ('auto_renewal', models.BooleanField(default=False, verbose_name='Авто-продление')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('registrar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='domains', to='dns.registrar', verbose_name='Регистратор')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='core.site', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Домен',
                'verbose_name_plural': 'Домены',
                'ordering': ['site__name', 'name'],
            },
        ),
        migrations.CreateModel(
            name='DomainPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid_date', models.DateField(verbose_name='Дата оплаты')),
                ('amount_usd', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Сумма (USD)')),
                ('paid_by', models.CharField(blank=True, max_length=200, verbose_name='Кто оплатил')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='dns.domain', verbose_name='Домен')),
            ],
            options={
                'verbose_name': 'Платёж за домен',
                'verbose_name_plural': 'Платежи за домены',
                'ordering': ['-paid_date'],
            },
        ),
    ]
