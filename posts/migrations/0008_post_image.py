# Generated by Django 4.0.4 on 2022-06-28 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_alter_country_id_alter_post_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='posts/', verbose_name='Picture'),
        ),
    ]
