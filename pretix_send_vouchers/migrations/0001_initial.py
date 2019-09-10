# Generated by Django 2.2.5 on 2019-09-09 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pretixbase', '0134_auto_20190905_1559'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoucherMarking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('shared', models.CharField(max_length=255)),
                ('voucher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='marking', to='pretixbase.Voucher')),
            ],
        ),
    ]