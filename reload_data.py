import os
import django
import json
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Curso, Estudiante, Docente
from courses.models import Materia, Inscripcion, Actividad, Calificacion, Asistencia

def reload():
    print("--- INICIANDO LIMPIEZA Y RECARGA TOTAL ---")
    
    with transaction.atomic():
        print("Borrando datos antiguos...")
        # Borrar en orden de dependencia
        Asistencia.objects.all().delete()
        Calificacion.objects.all().delete()
        Actividad.objects.all().delete()
        Inscripcion.objects.all().delete()
        Materia.objects.all().delete()
        Estudiante.objects.all().delete()
        Docente.objects.all().delete()
        Curso.objects.all().delete()
        # No borramos el superusuario admin
        User.objects.exclude(username='admin').delete()
        print("¡Limpieza completada!")

    print("Cargando datos desde data_backup_utf8.json...")
    with open('data_backup_utf8.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # El orden de carga es crítico
    with transaction.atomic():
        # 1. Cursos
        print("Cargando Cursos...")
        cursos = [Curso(**item['fields']) for item in data if item['model'] == 'accounts.curso']
        for c in cursos: c.id = next(item['pk'] for item in data if item['model'] == 'accounts.curso' and item['fields']['nombre'] == c.nombre) # Preservar PKs si es posible, pero el JSON de dumpdata ya tiene PKs
        
        # En dumpdata de Django, el formato es diferente. Vamos a usar un enfoque más directo.
        
        def get_items(model_name):
            return [item for item in data if item['model'] == model_name]

        # Mapeo de modelos
        model_map = {
            'accounts.curso': Curso,
            'accounts.user': User,
            'accounts.docente': Docente,
            'accounts.estudiante': Estudiante,
            'courses.materia': Materia,
            'courses.inscripcion': Inscripcion,
            'courses.actividad': Actividad,
            'courses.calificacion': Calificacion,
            'courses.asistencia': Asistencia,
        }

        for m_name, model in model_map.items():
            print(f"Insertando {m_name}...")
            items = get_items(m_name)
            objs = []
            for item in items:
                fields = item['fields'].copy()
                
                # Quitar campos M2M que dan error en bulk_create
                if m_name == 'accounts.user':
                    if fields['username'] == 'admin':
                        continue
                    fields.pop('groups', None)
                    fields.pop('user_permissions', None)
                
                # Convertir nombres de campos de FK a field_id
                processed_fields = {}
                for k, v in fields.items():
                    # Si el modelo tiene un campo con ese nombre y es una FK
                    try:
                        field_obj = model._meta.get_field(k)
                        if field_obj.is_relation and not field_obj.many_to_many:
                            processed_fields[f"{k}_id"] = v
                        else:
                            processed_fields[k] = v
                    except:
                        processed_fields[k] = v
                
                obj = model(pk=item['pk'], **processed_fields)
                objs.append(obj)
            
            if objs:
                model.objects.bulk_create(objs, batch_size=500, ignore_conflicts=True)
                print(f"  {len(objs)} registros insertados.")

    print("--- ¡RECARGA EXITOSA! ---")
    print("RECUERDA: Debes ejecutar 'python fix_sequences.py' después de esto.")

if __name__ == "__main__":
    reload()
