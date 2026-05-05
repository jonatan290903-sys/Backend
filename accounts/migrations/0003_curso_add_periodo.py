from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_rename_grado_curso'),
    ]

    operations = [
        migrations.AddField(
            model_name='curso',
            name='periodo',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
