# Generated by Django 3.0.5 on 2020-06-01 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(max_length=100, verbose_name='Calle')),
                ('suburb', models.CharField(max_length=100, verbose_name='Colonia')),
                ('phone_number', models.CharField(max_length=10, verbose_name='Telefono')),
                ('state', models.CharField(max_length=30, verbose_name='estado')),
                ('zip', models.CharField(max_length=6, verbose_name='Codigo Postal')),
                ('default', models.BooleanField(default=False)),
                ('point', models.CharField(max_length=200, verbose_name='Punto medio')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Cliente')),
            ],
            options={
                'verbose_name_plural': 'Direcciones',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
            ],
            options={
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Nombre del articulo')),
                ('price', models.FloatField(verbose_name='Precio')),
                ('discount_price', models.FloatField(blank=True, null=True, verbose_name='Precio de descuento')),
                ('label', models.CharField(choices=[('N', 'Nuevo'), ('O', 'En oferta')], max_length=2, verbose_name='Nuevo o en oferta?')),
                ('slug', models.SlugField(verbose_name='Link')),
                ('description', models.TextField(verbose_name='Descripcion')),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('image2', models.ImageField(blank=True, null=True, upload_to='')),
                ('image3', models.ImageField(blank=True, null=True, upload_to='')),
                ('stock', models.IntegerField(default=1, verbose_name='Stock')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent', models.BooleanField(default=False, verbose_name='¿Ha sido enviado?')),
                ('ref_code', models.CharField(max_length=30, verbose_name='Número de rastreo')),
                ('ordered', models.BooleanField(default=False, verbose_name='¿Ordenado?')),
                ('start_date', models.DateTimeField(auto_now=True)),
                ('ordered_date', models.DateTimeField(verbose_name='Fecha de orden')),
                ('sent_price', models.IntegerField(blank=True, null=True, verbose_name='Precio de envío')),
            ],
            options={
                'verbose_name': 'Orden',
                'verbose_name_plural': 'Ordenes',
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('accepted', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_charge_id', models.CharField(max_length=50, verbose_name='ID de pago')),
                ('amount', models.FloatField(verbose_name='Cantidad (MXN)')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Fecha')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Cantidad')),
                ('ordered', models.BooleanField(default=False, verbose_name='¿Ordenado?')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Item', verbose_name='Producto')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Producto de orden',
                'verbose_name_plural': 'Productos de orden',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='core.OrderItem', verbose_name='Productos'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Payment', verbose_name='Pago'),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipping_address', to='core.Address', verbose_name='Dirección'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
    ]