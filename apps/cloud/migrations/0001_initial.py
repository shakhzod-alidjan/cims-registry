from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloudProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Провайдер')),
                ('contact_email', models.EmailField(blank=True, verbose_name='Email')),
                ('billing_url', models.URLField(blank=True, verbose_name='Биллинг URL')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
            ],
            options={
                'verbose_name': 'Cloud-провайдер',
                'verbose_name_plural': 'Cloud-провайдеры',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CloudServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_type', models.CharField(choices=[('vps', 'VPS'), ('dedicated', 'Dedicated'), ('managed_db', 'Managed Database'), ('s3', 'Object Storage (S3)'), ('function', 'Serverless / Function'), ('other', 'Другое')], default='vps', max_length=20, verbose_name='Тип')),
                ('name', models.CharField(max_length=200, verbose_name='Имя сервера')),
                ('cpu', models.CharField(blank=True, max_length=50, verbose_name='CPU')),
                ('ram_gb', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='RAM (GB)')),
                ('disk_gb', models.PositiveIntegerField(blank=True, null=True, verbose_name='Диск (GB)')),
                ('disk_type', models.CharField(choices=[('ssd', 'SSD'), ('hdd', 'HDD'), ('nvme', 'NVMe')], default='ssd', max_length=10, verbose_name='Тип диска')),
                ('os', models.CharField(blank=True, max_length=100, verbose_name='ОС')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP адрес')),
                ('purpose', models.CharField(blank=True, max_length=300, verbose_name='Назначение')),
                ('status', models.CharField(choices=[('active', 'Активен'), ('stopped', 'Остановлен')], default='active', max_length=20, verbose_name='Статус')),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Стоимость / мес (USD)')),
                ('billing_period', models.CharField(choices=[('monthly', 'Ежемесячно'), ('yearly', 'Ежегодно')], default='monthly', max_length=20, verbose_name='Период оплаты')),
                ('next_payment', models.DateField(blank=True, null=True, verbose_name='Следующий платёж')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servers', to='cloud.cloudprovider', verbose_name='Провайдер')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cloud_servers', to='core.site', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Cloud-сервер',
                'verbose_name_plural': 'Cloud-серверы',
                'ordering': ['provider__name', 'name'],
            },
        ),
    ]
