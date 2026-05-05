from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_curso_add_periodo'),
        ('courses', '0003_remove_periodo'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorarioCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('curso', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='horario',
                    to='accounts.curso',
                )),
            ],
        ),
        migrations.CreateModel(
            name='PeriodoHorario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveIntegerField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('horario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='periodos',
                    to='courses.horariocurso',
                )),
            ],
            options={'ordering': ['orden']},
        ),
        migrations.AlterUniqueTogether(
            name='periodohorario',
            unique_together={('horario', 'orden')},
        ),
        migrations.CreateModel(
            name='ClaseHorario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(
                    choices=[
                        ('lunes', 'Lunes'),
                        ('martes', 'Martes'),
                        ('miercoles', 'Miércoles'),
                        ('jueves', 'Jueves'),
                        ('viernes', 'Viernes'),
                    ],
                    max_length=10,
                )),
                ('materia', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='clases_horario',
                    to='courses.materia',
                )),
                ('periodo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='clases',
                    to='courses.periodohorario',
                )),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='clasehorario',
            unique_together={('periodo', 'dia')},
        ),
    ]
