from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('accounts', '0002_rename_grado_curso'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Renombrar modelo Curso → Materia
        migrations.RenameModel(
            old_name='Curso',
            new_name='Materia',
        ),

        # 2. Renombrar campo Materia.grado → Materia.curso (FK a accounts.Curso)
        migrations.RenameField(
            model_name='materia',
            old_name='grado',
            new_name='curso',
        ),

        # 3. Actualizar related_name en Materia.curso y Materia.docente
        migrations.AlterField(
            model_name='materia',
            name='curso',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='materias',
                to='accounts.curso',
            ),
        ),
        migrations.AlterField(
            model_name='materia',
            name='docente',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='materias',
                to='accounts.docente',
            ),
        ),

        # 4. Actualizar unique_together de Materia
        migrations.AlterUniqueTogether(
            name='materia',
            unique_together={('nombre', 'curso')},
        ),

        # 5. Renombrar campo Matricula.curso → Matricula.materia
        migrations.RenameField(
            model_name='matricula',
            old_name='curso',
            new_name='materia',
        ),

        # 6. Actualizar unique_together de Matricula
        migrations.AlterUniqueTogether(
            name='matricula',
            unique_together={('estudiante', 'materia', 'periodo')},
        ),

        # 7. Renombrar campo Actividad.curso → Actividad.materia
        migrations.RenameField(
            model_name='actividad',
            old_name='curso',
            new_name='materia',
        ),

        # 8. Renombrar campo Asistencia.curso → Asistencia.materia
        migrations.RenameField(
            model_name='asistencia',
            old_name='curso',
            new_name='materia',
        ),

        # 9. Actualizar unique_together de Asistencia
        migrations.AlterUniqueTogether(
            name='asistencia',
            unique_together={('estudiante', 'materia', 'fecha')},
        ),

        # 10. Crear modelo Inscripcion
        migrations.CreateModel(
            name='Inscripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(max_length=10)),
                ('fecha_inscripcion', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(
                    choices=[('activo', 'Activo'), ('retirado', 'Retirado'), ('culminado', 'Culminado')],
                    default='activo',
                    max_length=20,
                )),
                ('curso', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='inscripciones',
                    to='accounts.curso',
                )),
                ('estudiante', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='inscripciones',
                    to='accounts.estudiante',
                )),
                ('registrada_por', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='inscripciones_registradas',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'unique_together': {('estudiante', 'curso', 'periodo')},
            },
        ),
    ]
