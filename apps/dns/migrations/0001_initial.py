from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Registrar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField(blank=True)),
                ('contact_name', models.CharField(blank=True, max_length=200)),
                ('contact_email', models.EmailField(blank=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('registration_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('cost_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('auto_renewal', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('registrar', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='domains', to='dns.registrar')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='core.site')),
            ],
            options={'ordering': ['site__name', 'name']},
        ),
        migrations.CreateModel(
            name='DomainPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('paid_date', models.DateField()),
                ('amount_usd', models.DecimalField(decimal_places=2, max_digits=8)),
                ('paid_by', models.CharField(blank=True, max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='dns.domain')),
            ],
            options={'ordering': ['-paid_date']},
        ),
    ]
