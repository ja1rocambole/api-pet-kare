# Generated by Django 4.2.2 on 2023-06-12 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0001_initial'),
        ('traits', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trait',
            name='pets',
            field=models.ManyToManyField(related_name='traits', to='pets.pet'),
        ),
    ]
