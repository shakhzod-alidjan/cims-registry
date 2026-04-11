from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Вендор')),
                ('contact_name', models.CharField(blank=True, max_length=200, verbose_name='Контактное лицо')),
                ('contact_email', models.EmailField(blank=True, verbose_name='Email')),
                ('contact_phone', models.CharField(blank=True, max_length=50, verbose_name='Телефон')),
                ('telegram', models.CharField(blank=True, max_length=100, verbose_name='Telegram')),
                ('country', models.CharField(blank=True, max_length=100, verbose_name='Страна')),
                ('support_terms', models.CharField(blank=True, max_length=200, verbose_name='Условия поддержки')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
            ],
            options={
                'verbose_name': 'Вендор',
                'verbose_name_plural': 'Вендоры',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BusinessApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название БП')),
                ('category', models.CharField(choices=[('erp', 'ERP / Бухгалтерия'), ('hr', 'HR / Зарплата'), ('bi', 'BI / Аналитика'), ('mining', 'Горное ПО'), ('cad', 'САПР'), ('office', 'Офисный пакет'), ('security', 'Безопасность'), ('legal', 'Правовая база'), ('other', 'Другое')], default='other', max_length=20, verbose_name='Категория')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='apps', to='licenses.vendor', verbose_name='Вендор')),
                ('sites', models.ManyToManyField(blank=True, to='core.site', verbose_name='Объекты')),
            ],
            options={
                'verbose_name': 'Бизнес-приложение',
                'verbose_name_plural': 'Бизнес-приложения',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_type', models.CharField(choices=[('named', 'Именная'), ('concurrent', 'Конкурентная'), ('subscription', 'Подписка'), ('corporate', 'Корпоративная'), ('oem', 'OEM')], max_length=20, verbose_name='Тип лицензии')),
                ('license_type_custom', models.CharField(blank=True, max_length=100, verbose_name='Тип (свой)')),
                ('quantity_total', models.PositiveIntegerField(blank=True, null=True, verbose_name='Куплено (шт.)')),
                ('quantity_used', models.PositiveIntegerField(blank=True, null=True, verbose_name='Используется (шт.)')),
                ('price_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Цена / лиц. (USD)')),
                ('contract_number', models.CharField(blank=True, max_length=100, verbose_name='№ договора')),
                ('purchase_date', models.DateField(blank=True, null=True, verbose_name='Дата покупки')),
                ('expiry_date', models.DateField(blank=True, null=True, verbose_name='Дата истечения')),
                ('contract_file', models.FileField(blank=True, upload_to='contracts/licenses/', verbose_name='Файл договора')),
                ('notes', models.TextField(blank=True, verbose_name='Примечания')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='licenses.businessapp', verbose_name='Приложение')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='core.site', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Лицензия',
                'verbose_name_plural': 'Лицензии',
                'ordering': ['app__name', 'license_type'],
            },
        ),
    ]
