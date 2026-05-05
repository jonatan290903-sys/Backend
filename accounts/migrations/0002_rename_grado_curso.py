from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Grado',
            new_name='Curso',
        ),
        migrations.RenameField(
            model_name='estudiante',
            old_name='grado',
            new_name='curso',
        ),
        migrations.AlterModelOptions(
            name='curso',
            options={},
        ),
    ]
