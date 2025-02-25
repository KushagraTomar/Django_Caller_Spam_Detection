# Generated by Django 5.1.4 on 2025-01-08 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_reporteduserspam_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.RemoveIndex(
            model_name='registeredusercontact',
            name='registered__phone_n_3c9ca9_idx',
        ),
        migrations.RemoveIndex(
            model_name='reporteduserspam',
            name='reported_us_phone_n_e9e91d_idx',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='registeredusercontact',
            name='phone_number',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='reporteduserspam',
            name='phone_number',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterModelTable(
            name='customuser',
            table=None,
        ),
        migrations.AlterModelTable(
            name='registeredusercontact',
            table=None,
        ),
        migrations.AlterModelTable(
            name='reporteduserspam',
            table=None,
        ),
    ]
