from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_rename_curso_materia_inscripcion'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='matricula',
            unique_together={('estudiante', 'materia')},
        ),
        migrations.RemoveField(
            model_name='matricula',
            name='periodo',
        ),
        migrations.AlterUniqueTogether(
            name='inscripcion',
            unique_together={('estudiante', 'curso')},
        ),
        migrations.RemoveField(
            model_name='inscripcion',
            name='periodo',
        ),
    ]
