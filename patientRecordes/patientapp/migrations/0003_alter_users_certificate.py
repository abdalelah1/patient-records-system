# Generated by Django 4.0.4 on 2024-01-29 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientapp', '0002_basicanalyses_categoriesanalysis_result_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='certificate',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
