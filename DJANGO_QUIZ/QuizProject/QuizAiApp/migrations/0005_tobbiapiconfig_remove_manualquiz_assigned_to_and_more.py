# Generated by Django 5.0.2 on 2025-04-16 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuizAiApp', '0004_remove_manualquestion_quiz_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TobbiAPIConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(help_text='API key for TOBBI API access', max_length=255)),
                ('base_url', models.URLField(default='https://openrouter.ai/api/v1', help_text='Base URL for the API')),
                ('model', models.CharField(default='deepseek/deepseek-r1:free', help_text='AI model to use', max_length=100)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this configuration is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'TOBBI API Configuration',
                'verbose_name_plural': 'TOBBI API Configurations',
            },
        ),
        migrations.RemoveField(
            model_name='manualquiz',
            name='assigned_to',
        ),
        migrations.RemoveField(
            model_name='quizattempt',
            name='quiz',
        ),
        migrations.RemoveField(
            model_name='quizattempt',
            name='user',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='ManualQuiz',
        ),
        migrations.DeleteModel(
            name='QuizAttempt',
        ),
    ]
