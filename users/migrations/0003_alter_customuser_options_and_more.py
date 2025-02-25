# Generated by Django 5.1.4 on 2025-01-08 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_registeredusercontact_reporteduserspam'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(db_index=True, max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='registeredusercontact',
            name='phone_number',
            field=models.CharField(db_index=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='reporteduserspam',
            name='phone_number',
            field=models.CharField(db_index=True, max_length=15, unique=True),
        ),
        migrations.AddIndex(
            model_name='registeredusercontact',
            index=models.Index(fields=['phone_number', 'contact_of'], name='registered__phone_n_3c9ca9_idx'),
        ),
        migrations.AddIndex(
            model_name='reporteduserspam',
            index=models.Index(fields=['phone_number', 'marked_by'], name='reported_us_phone_n_e9e91d_idx'),
        ),
        migrations.AlterModelTable(
            name='customuser',
            table='custom_user_table',
        ),
        migrations.AlterModelTable(
            name='registeredusercontact',
            table='registered_user_contact_table',
        ),
        migrations.AlterModelTable(
            name='reporteduserspam',
            table='reported_user_spam_table',
        ),
    ]
