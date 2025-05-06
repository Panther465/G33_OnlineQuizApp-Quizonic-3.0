# Generated manually

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('QuizTemplateApp', '0004_question_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiquizattempt',
            name='attempt_data',
            field=models.JSONField(blank=True, default=dict),
        ),
    ] 