# Generated by Django 5.1.7 on 2025-04-15 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizTemplateApp', '0002_aiquizattempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='category',
            field=models.CharField(default='General', max_length=50),
        ),
        migrations.AddField(
            model_name='quiz',
            name='difficulty',
            field=models.CharField(default='Medium', max_length=20),
        ),
    ]
