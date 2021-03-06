# Generated by Django 3.0.4 on 2020-03-21 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="twilio_worker_sid",
            field=models.CharField(
                blank=True,
                max_length=34,
                null=True,
                unique=True,
                verbose_name="Twilio Worker SID",
            ),
        ),
    ]
