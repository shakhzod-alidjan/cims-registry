from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='ISPOperator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('contact_name', models.CharField(blank=True, max_length=200)),
                ('contact_email', models.EmailField(blank=True)),
                ('contact_phone', models.CharField(blank=True, max_length=50)),
                ('country', models.CharField(blank=True, max_length=100)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='ISPContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('service_type', models.CharField(max_length=20)),
                ('service_name', models.CharField(max_length=200)),
                ('tariff', models.CharField(blank=True, max_length=200)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('speed', models.CharField(blank=True, max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('contract_number', models.CharField(blank=True, max_length=100)),
                ('contract_file', models.FileField(blank=True, upload_to='contracts/isp/')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('auto_renewal', models.BooleanField(default=False)),
                ('cost_uzs', models.DecimalField(blank=True, decimal_places=0, max_digits=14, null=True)),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_method', models.CharField(blank=True, max_length=100)),
                ('next_payment', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts', to='internet.ispoperator')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='isp_contracts', to='core.site')),
            ],
            options={'ordering': ['site__name']},
        ),
    ]
