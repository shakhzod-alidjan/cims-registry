from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('contact_name', models.CharField(blank=True, max_length=200)),
                ('contact_email', models.EmailField(blank=True)),
                ('contact_phone', models.CharField(blank=True, max_length=50)),
                ('telegram', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('support_terms', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='BusinessApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(default='other', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='apps', to='licenses.vendor')),
                ('sites', models.ManyToManyField(blank=True, to='core.site')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('license_type', models.CharField(max_length=20)),
                ('license_type_custom', models.CharField(blank=True, max_length=100)),
                ('quantity_total', models.PositiveIntegerField(blank=True, null=True)),
                ('quantity_used', models.PositiveIntegerField(blank=True, null=True)),
                ('price_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('contract_number', models.CharField(blank=True, max_length=100)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('contract_file', models.FileField(blank=True, upload_to='contracts/licenses/')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='licenses.businessapp')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to='core.site')),
            ],
            options={'ordering': ['app__name']},
        ),
    ]
