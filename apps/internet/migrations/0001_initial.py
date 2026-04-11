from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ISPOperator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Оператор')),
                ('contact_name', models.CharField(blank=True, max_length=200, verbose_name='Контакт')),
                ('contact_email', models.EmailField(blank=True, verbose_name='Email')),
                ('contact_phone', models.CharField(blank=True, max_length=50, verbose_name='Телефон')),
                ('country', models.CharField(blank=True, max_length=100, verbose_name='Страна')),
            ],
            options={
                'verbose_name': 'Оператор связи',
                'verbose_name_plural': 'Операторы связи',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ISPContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', models.CharField(choices=[('internet', 'Интернет (основной)'), ('reserve', 'Резерв интернет'), ('apn', 'APN услуги'), ('mpls', 'MPLS VPN'), ('mobile', 'Мобильная связь'), ('phone', 'Городская телефония')], max_length=20, verbose_name='Тип услуги')),
                ('service_name', models.CharField(max_length=200, verbose_name='Название услуги')),
                ('tariff', models.CharField(blank=True, max_length=200, verbose_name='Тариф / описание')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Локация / объект')),
                ('speed', models.CharField(blank=True, max_length=100, verbose_name='Скорость / объём')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP адрес')),
                ('contract_number', models.CharField(blank=True, max_length=100, verbose_name='№ договора')),
                ('contract_file', models.FileField(blank=True, upload_to='contracts/isp/', verbose_name='Файл договора')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
                ('auto_renewal', models.BooleanField(default=False, verbose_name='Авто-продление')),
                ('cost_uzs', models.DecimalField(blank=True, decimal_places=0, max_digits=14, null=True, verbose_name='Стоимость / мес (UZS)')),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Стоимость / мес (USD)')),
                ('payment_method', models.CharField(blank=True, max_length=100, verbose_name='Способ оплаты')),
                ('next_payment', models.DateField(blank=True, null=True, verbose_name='Дата след. оплаты')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts', to='internet.ispoperator', verbose_name='Оператор')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='isp_contracts', to='core.site', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Договор ISP',
                'verbose_name_plural': 'Договоры ISP',
                'ordering': ['site__name', 'operator__name'],
            },
        ),
    ]
