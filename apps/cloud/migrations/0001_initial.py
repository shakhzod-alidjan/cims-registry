from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='CloudProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('contact_email', models.EmailField(blank=True)),
                ('billing_url', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='CloudServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('server_type', models.CharField(default='vps', max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('cpu', models.CharField(blank=True, max_length=50)),
                ('ram_gb', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('disk_gb', models.PositiveIntegerField(blank=True, null=True)),
                ('disk_type', models.CharField(default='ssd', max_length=10)),
                ('os', models.CharField(blank=True, max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('purpose', models.CharField(blank=True, max_length=300)),
                ('status', models.CharField(default='active', max_length=20)),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('billing_period', models.CharField(default='monthly', max_length=20)),
                ('next_payment', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servers', to='cloud.cloudprovider')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cloud_servers', to='core.site')),
            ],
            options={'ordering': ['provider__name', 'name']},
        ),
    ]
