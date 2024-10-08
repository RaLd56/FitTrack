# Generated by Django 5.1 on 2024-09-10 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_goal_end_point_goal_start_point_alter_goal_progress_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='progress',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userstats',
            name='bodyfat',
            field=models.FloatField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='userstats',
            name='height',
            field=models.FloatField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='userstats',
            name='waist',
            field=models.FloatField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='userstats',
            name='weight',
            field=models.FloatField(blank=True, default=False, null=True),
        ),
    ]
