from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_remove_matricula'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividad',
            name='trimestre',
            field=models.CharField(
                choices=[('T1', 'Trimestre 1'), ('T2', 'Trimestre 2'), ('T3', 'Trimestre 3')],
                default='T1',
                max_length=2,
            ),
        ),
    ]
