from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_horario'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Matricula',
        ),
    ]
