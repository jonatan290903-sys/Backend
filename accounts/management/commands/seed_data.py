"""
python manage.py seed_data

Borra todos los datos existentes y carga un conjunto realista como si el sistema
hubiera estado funcionando desde el 1 de febrero de 2026.
Contraseña de todos los usuarios: 123456
"""
import random
import unicodedata
from datetime import date, timedelta

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

RNG = random.Random(42)

# ── Pools de nombres ──────────────────────────────────────────────────────────

NOMBRES_M = [
    'Juan', 'Carlos', 'Luis', 'Miguel', 'Andrés', 'Diego', 'Sebastián',
    'Fernando', 'Roberto', 'Alejandro', 'Eduardo', 'Pablo', 'Marcos',
    'David', 'Antonio', 'Manuel', 'Pedro', 'Ricardo', 'José', 'Rafael',
    'Ernesto', 'Rodrigo', 'Mateo', 'Bruno', 'Leonardo', 'Ángel',
    'Joaquín', 'Nicolás', 'Emilio', 'Víctor', 'Aarón', 'Iván',
]
NOMBRES_F = [
    'María', 'Ana', 'Carmen', 'Rosa', 'Sofía', 'Valentina', 'Isabella',
    'Camila', 'Daniela', 'Laura', 'Gabriela', 'Andrea', 'Patricia',
    'Fernanda', 'Lucía', 'Elena', 'Verónica', 'Natalia', 'Paula',
    'Sandra', 'Beatriz', 'Claudia', 'Silvia', 'Mónica', 'Gloria',
    'Martha', 'Pilar', 'Mercedes', 'Adriana', 'Rebeca', 'Valeria',
]
APELLIDOS = [
    'García', 'Martínez', 'López', 'González', 'Rodríguez', 'Pérez',
    'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Mendoza', 'Herrera',
    'Morales', 'Cruz', 'Vargas', 'Gutiérrez', 'Ortiz', 'Reyes',
    'Castillo', 'Ramos', 'Vega', 'Romero', 'Navarro', 'Jiménez',
    'Díaz', 'Campos', 'Ríos', 'Delgado', 'Fuentes', 'Molina',
    'Castro', 'Soto', 'Suárez', 'Chávez', 'Lima', 'Paredes',
    'Vera', 'Lara', 'Núñez', 'Prieto', 'Blanco', 'Alvarado',
    'Guzmán', 'Quispe', 'Huanca', 'Mamani', 'Condori', 'Apaza',
    'Tapia', 'Centeno', 'Solís', 'Bejarano', 'Inca', 'Cáceres',
    'Montes', 'Arce', 'Esquivel', 'Pinto', 'Salas', 'Bautista',
]

# ── Docentes predefinidos ─────────────────────────────────────────────────────
# (nombre, ap1, ap2, especialidad, nivel, grados_que_cubre, título)

TEACHERS = [
    # ── Primaria – Matemática (uno por grado) ─────────────────────────────────
    ('Raúl',       'Mendoza',   'Torres',   'Matemática',                    'primaria',   [1],       'Licenciado en Educación Primaria'),
    ('Gloria',     'Vásquez',   'Soto',     'Matemática',                    'primaria',   [2],       'Licenciada en Educación Primaria'),
    ('Ernesto',    'Paredes',   'Lima',     'Matemática',                    'primaria',   [3],       'Licenciado en Educación Primaria'),
    ('Miriam',     'Suárez',    'Chávez',   'Matemática',                    'primaria',   [4],       'Licenciada en Educación Primaria'),
    ('Óscar',      'Delgado',   'Ríos',     'Matemática',                    'primaria',   [5],       'Licenciado en Educación Primaria'),
    ('Isabel',     'Morales',   'Vargas',   'Matemática',                    'primaria',   [6],       'Licenciada en Educación Primaria'),
    # ── Primaria – Comunicación ───────────────────────────────────────────────
    ('Silvia',     'Romero',    'Castro',   'Comunicación',                  'primaria',   [1],       'Licenciada en Educación Primaria'),
    ('Héctor',     'Núñez',     'Prieto',   'Comunicación',                  'primaria',   [2],       'Licenciado en Educación Primaria'),
    ('Natividad',  'Blanco',    'Fuentes',  'Comunicación',                  'primaria',   [3],       'Licenciada en Educación Primaria'),
    ('Carmen',     'Alvarado',  'Bravo',    'Comunicación',                  'primaria',   [4],       'Licenciada en Educación Primaria'),
    ('Félix',      'Guzmán',    'Vera',     'Comunicación',                  'primaria',   [5],       'Licenciado en Educación Primaria'),
    ('Amparo',     'Castillo',  'Lara',     'Comunicación',                  'primaria',   [6],       'Licenciada en Educación Primaria'),
    # ── Primaria – Ciencias Naturales ─────────────────────────────────────────
    ('Virgilio',   'Prado',     'Espinoza', 'Ciencias Naturales',            'primaria',   [1],       'Licenciado en Educación Primaria'),
    ('Luisa',      'Pacheco',   'Mena',     'Ciencias Naturales',            'primaria',   [2],       'Licenciada en Educación Primaria'),
    ('Teodoro',    'Quispe',    'Huanca',   'Ciencias Naturales',            'primaria',   [3],       'Licenciado en Educación Primaria'),
    ('Milagros',   'Saavedra',  'Polo',     'Ciencias Naturales',            'primaria',   [4],       'Licenciada en Educación Primaria'),
    ('Armando',    'Vilela',    'Toro',     'Ciencias Naturales',            'primaria',   [5],       'Licenciado en Educación Primaria'),
    ('Rosa',       'Condori',   'Apaza',    'Ciencias Naturales',            'primaria',   [6],       'Licenciada en Educación Primaria'),
    # ── Primaria – Personal Social ────────────────────────────────────────────
    ('Cecilia',    'Herrera',   'Rojas',    'Personal Social',               'primaria',   [1, 2],    'Licenciada en Educación Primaria'),
    ('Javier',     'Solís',     'Mamani',   'Personal Social',               'primaria',   [3, 4],    'Licenciado en Educación Primaria'),
    ('Pilar',      'Tapia',     'Centeno',  'Personal Social',               'primaria',   [5, 6],    'Licenciada en Educación Primaria'),
    # ── Primaria – Inglés ─────────────────────────────────────────────────────
    ('Linda',      'Torres',    'Valdivia', 'Inglés',                        'primaria',   [1, 2],    'Licenciada en Idiomas Extranjeros'),
    ('César',      'Augusto',   'Flores',   'Inglés',                        'primaria',   [3, 4],    'Licenciado en Idiomas Extranjeros'),
    ('Wendy',      'Márquez',   'Leal',     'Inglés',                        'primaria',   [5, 6],    'Licenciada en Idiomas Extranjeros'),
    # ── Primaria – Arte, EF, Religión ─────────────────────────────────────────
    ('Arturo',     'Bazán',     'Medrano',  'Arte y Cultura',                'primaria',   [1,2,3],   'Licenciado en Arte'),
    ('Claudia',    'Segura',    'Peña',     'Arte y Cultura',                'primaria',   [4,5,6],   'Licenciada en Arte'),
    ('Jorge',      'Ramos',     'Bautista', 'Educación Física',              'primaria',   [1,2,3],   'Licenciado en Educación Física'),
    ('Patricia',   'Salas',     'Vega',     'Educación Física',              'primaria',   [4,5,6],   'Licenciada en Educación Física'),
    ('Ramón',      'Cárdenas',  'Montes',   'Religión',                      'primaria',   [1,2,3],   'Licenciado en Teología y Educación'),
    ('Teresa',     'Ugarte',    'Díaz',     'Religión',                      'primaria',   [4,5,6],   'Licenciada en Teología y Educación'),

    # ── Secundaria – Matemática ───────────────────────────────────────────────
    ('Alberto',    'Ríos',      'Paredes',  'Matemática',                    'secundaria', [1],       'Licenciado en Matemática'),
    ('Beatriz',    'Montoya',   'Lagos',    'Matemática',                    'secundaria', [2],       'Licenciada en Matemática'),
    ('Guillermo',  'Vela',      'Castro',   'Matemática',                    'secundaria', [3],       'Licenciado en Matemática'),
    ('Yolanda',    'Aguilar',   'Bravo',    'Matemática',                    'secundaria', [4],       'Licenciada en Matemática'),
    ('Rafael',     'Peña',      'Torres',   'Matemática',                    'secundaria', [5],       'Licenciado en Matemática'),
    ('Consuelo',   'Dueñas',    'Vargas',   'Matemática',                    'secundaria', [6],       'Licenciada en Matemática'),
    # ── Secundaria – Comunicación ─────────────────────────────────────────────
    ('Enrique',    'Salcedo',   'Mora',     'Comunicación',                  'secundaria', [1],       'Licenciado en Lengua y Literatura'),
    ('Angela',     'Portillo',  'Chávez',   'Comunicación',                  'secundaria', [2],       'Licenciada en Lengua y Literatura'),
    ('Francisco',  'Arenas',    'Díaz',     'Comunicación',                  'secundaria', [3],       'Licenciado en Lengua y Literatura'),
    ('Marisol',    'Zelada',    'Fuentes',  'Comunicación',                  'secundaria', [4],       'Licenciada en Lengua y Literatura'),
    ('Dante',      'Urbina',    'Pinto',    'Comunicación',                  'secundaria', [5],       'Licenciado en Lengua y Literatura'),
    ('Susana',     'Cóndor',    'Mamani',   'Comunicación',                  'secundaria', [6],       'Licenciada en Lengua y Literatura'),
    # ── Secundaria – Historia ─────────────────────────────────────────────────
    ('Rolando',    'Bejarano',  'Inca',     'Historia, Geografía y Economía','secundaria', [1,2],     'Licenciado en Ciencias Sociales'),
    ('Flor',       'Quispe',    'Huallpa',  'Historia, Geografía y Economía','secundaria', [3,4],     'Licenciada en Ciencias Sociales'),
    ('Germán',     'Cáceres',   'Montes',   'Historia, Geografía y Economía','secundaria', [5,6],     'Licenciado en Ciencias Sociales'),
    # ── Secundaria – Ciencias Naturales (Bio→1-3, Física→4-5, Química→6) ──────
    ('Violeta',    'Huanca',    'Apaza',    'Ciencias Naturales',            'secundaria', [1,2],     'Licenciada en Biología'),
    ('Óscar',      'Llanque',   'Vilca',    'Ciencias Naturales',            'secundaria', [3],       'Licenciado en Biología'),
    ('Marcelo',    'Arce',      'Pinto',    'Ciencias Naturales',            'secundaria', [4],       'Licenciado en Física'),
    ('Laura',      'Esquivel',  'Mamani',   'Ciencias Naturales',            'secundaria', [5],       'Licenciada en Física'),
    ('Diego',      'Chávez',    'Arévalo',  'Ciencias Naturales',            'secundaria', [6],       'Licenciado en Química'),
    # ── Secundaria – Inglés ───────────────────────────────────────────────────
    ('Michelle',   'Wagner',    'López',    'Inglés',                        'secundaria', [1,2],     'Licenciada en Idiomas Extranjeros'),
    ('Brian',      'Carpenter', 'Ríos',     'Inglés',                        'secundaria', [3,4],     'Licenciado en Idiomas Extranjeros'),
    ('Sandra',     'Williamson','Vera',     'Inglés',                        'secundaria', [5,6],     'Licenciada en Idiomas Extranjeros'),
    # ── Secundaria – Arte, EF, Religión, EPT, Cívica ─────────────────────────
    ('Fernando',   'Quispe',    'Arce',     'Arte y Cultura',                'secundaria', [1,2,3],   'Licenciado en Arte'),
    ('Lucero',     'Tapia',     'Molina',   'Arte y Cultura',                'secundaria', [4,5,6],   'Licenciada en Arte'),
    ('Santiago',   'Ramos',     'Vera',     'Educación Física',              'secundaria', [1,2,3],   'Licenciado en Educación Física'),
    ('Evelyn',     'Pumari',    'Ccoa',     'Educación Física',              'secundaria', [4,5,6],   'Licenciada en Educación Física'),
    ('Carlos',     'Mendoza',   'Ríos',     'Religión',                      'secundaria', [1,2,3],   'Licenciado en Teología y Educación'),
    ('Angélica',   'Roa',       'Sánchez',  'Religión',                      'secundaria', [4,5,6],   'Licenciada en Teología y Educación'),
    ('Mario',      'Gallegos',  'Soto',     'Educación para el Trabajo',     'secundaria', [1,2,3],   'Licenciado en Educación para el Trabajo'),
    ('Rebeca',     'Nieto',     'Palomino', 'Educación para el Trabajo',     'secundaria', [4,5,6],   'Licenciada en Educación para el Trabajo'),
    ('Zósimo',     'Huamán',    'Ccori',    'Formación Ciudadana y Cívica',  'secundaria', [1,2,3],   'Licenciado en Ciencias Sociales'),
    ('Lorena',     'Esquivel',  'Cruz',     'Formación Ciudadana y Cívica',  'secundaria', [4,5,6],   'Licenciada en Ciencias Sociales'),
]

# ── Materias por nivel ────────────────────────────────────────────────────────
# (nombre, código_base, horas_semana)

MATERIAS_PRIMARIA = [
    ('Matemática',       'MAT',  5),
    ('Comunicación',     'COM',  5),
    ('Ciencias Naturales','CNAT', 3),
    ('Personal Social',  'PSOC', 3),
    ('Inglés',           'ING',  2),
    ('Arte y Cultura',   'ART',  2),
    ('Educación Física', 'EDF',  2),
    ('Religión',         'REL',  2),
]

MATERIAS_SECUNDARIA = [
    ('Matemática',                    'MAT',  5),
    ('Comunicación',                  'COM',  5),
    ('Historia, Geografía y Economía','HGE',  3),
    ('Ciencias Naturales',            'CNAT', 4),
    ('Inglés',                        'ING',  3),
    ('Arte y Cultura',                'ART',  2),
    ('Educación Física',              'EDF',  2),
    ('Religión',                      'REL',  2),
    ('Educación para el Trabajo',     'EPT',  2),
    ('Formación Ciudadana y Cívica',  'FCA',  2),
]

# días de la semana según horas/semana
DIAS_POR_HORAS = {
    5: ['lunes', 'martes', 'miercoles', 'jueves', 'viernes'],
    4: ['lunes', 'martes', 'miercoles', 'jueves'],
    3: ['lunes', 'miercoles', 'viernes'],
    2: ['martes', 'jueves'],
}
DIA_TO_WD = {'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3, 'viernes': 4}

# ── Horario base ──────────────────────────────────────────────────────────────
# 6 periodos de 45 min

PERIODOS = [
    (1, '07:00', '07:45'),
    (2, '07:50', '08:35'),
    (3, '08:40', '09:25'),
    (4, '10:00', '10:45'),  # después del recreo
    (5, '10:50', '11:35'),
    (6, '11:40', '12:25'),
]

# Asignación de periodos por asignatura (primaria)
# (nombre_materia, dia, periodo_orden)
HORARIO_PRIMARIA_TEMPLATE = [
    ('Matemática',        'lunes',     1), ('Matemática',        'martes',    1),
    ('Matemática',        'miercoles', 1), ('Matemática',        'jueves',    1),
    ('Matemática',        'viernes',   1),
    ('Comunicación',      'lunes',     2), ('Comunicación',      'martes',    2),
    ('Comunicación',      'miercoles', 2), ('Comunicación',      'jueves',    2),
    ('Comunicación',      'viernes',   2),
    ('Ciencias Naturales','lunes',     3), ('Ciencias Naturales','miercoles', 3),
    ('Ciencias Naturales','viernes',   3),
    ('Personal Social',   'martes',    3), ('Personal Social',   'jueves',    3),
    ('Personal Social',   'lunes',     4),
    ('Inglés',            'martes',    4), ('Inglés',            'jueves',    4),
    ('Arte y Cultura',    'miercoles', 4), ('Arte y Cultura',    'viernes',   4),
    ('Educación Física',  'lunes',     5), ('Educación Física',  'miercoles', 5),
    ('Religión',          'martes',    5), ('Religión',          'jueves',    5),
]

HORARIO_SECUNDARIA_TEMPLATE = [
    ('Matemática',                    'lunes',     1), ('Matemática',                    'martes',    1),
    ('Matemática',                    'miercoles', 1), ('Matemática',                    'jueves',    1),
    ('Matemática',                    'viernes',   1),
    ('Comunicación',                  'lunes',     2), ('Comunicación',                  'martes',    2),
    ('Comunicación',                  'miercoles', 2), ('Comunicación',                  'jueves',    2),
    ('Comunicación',                  'viernes',   2),
    ('Historia, Geografía y Economía','lunes',     3), ('Historia, Geografía y Economía','miercoles', 3),
    ('Historia, Geografía y Economía','viernes',   3),
    ('Ciencias Naturales',            'martes',    3), ('Ciencias Naturales',            'jueves',    3),
    ('Ciencias Naturales',            'lunes',     4), ('Ciencias Naturales',            'martes',    4),
    ('Inglés',                        'miercoles', 4), ('Inglés',                        'jueves',    4),
    ('Inglés',                        'viernes',   4),
    ('Arte y Cultura',                'lunes',     5), ('Arte y Cultura',                'miercoles', 5),
    ('Educación Física',              'martes',    5), ('Educación Física',              'jueves',    5),
    ('Religión',                      'viernes',   5),
    ('Educación para el Trabajo',     'lunes',     6), ('Educación para el Trabajo',     'miercoles', 6),
    ('Formación Ciudadana y Cívica',  'martes',    6), ('Formación Ciudadana y Cívica',  'viernes',   6),
]

# ── Actividades por materia ───────────────────────────────────────────────────

ACTIVIDADES = [
    # (nombre, tipo, fecha, trimestre)
    ('Evaluación diagnóstica',   'examen',        '2026-02-14', 'T1'),
    ('Tarea 1',                  'tarea',         '2026-02-28', 'T1'),
    ('Examen parcial T1',        'examen',        '2026-03-20', 'T1'),
    ('Trabajo en equipo T1',     'proyecto',      '2026-04-04', 'T1'),
    ('Participación T1',         'participacion', None,         'T1'),
]


class Command(BaseCommand):
    help = 'Carga datos de demostración desde el 1 de febrero de 2026'

    def handle(self, *args, **options):
        self.pw_hash = make_password('123456')
        self._used_emails = set()
        self._used_usernames = set()
        self._used_docs = set()
        self._exp_counter = 1

        self.stdout.write('Borrando datos existentes...')
        self._clear()

        with transaction.atomic():
            self.stdout.write('Creando usuarios administrativos...')
            admin_user = self._create_staff()

            self.stdout.write('Creando 48 cursos...')
            cursos_map = self._create_cursos()

            self.stdout.write('Creando 61 docentes...')
            docentes_map = self._create_docentes()

            self.stdout.write('Creando materias (432 en total)...')
            materias_map = self._create_materias(cursos_map, docentes_map)

            self.stdout.write('Creando 480 estudiantes...')
            estudiantes_map = self._create_estudiantes(cursos_map, admin_user)

            self.stdout.write('Creando horarios...')
            self._create_horarios(cursos_map, materias_map)

            self.stdout.write('Creando registros de asistencia (Feb–Abr 2026)...')
            self._create_asistencia(materias_map, estudiantes_map)

            self.stdout.write('Creando actividades y calificaciones...')
            self._create_actividades_calificaciones(materias_map, estudiantes_map)

        self.stdout.write(self.style.SUCCESS(
            '\nDatos cargados correctamente.\n'
            '  Directivo:      pedro.alarcon@escuela.edu.bo / 123456\n'
            '  Administrativo: elena.fuentes@escuela.edu.bo / 123456\n'
            '  Docente ej.:    raul.mendoza@escuela.edu.bo  / 123456\n'
            '  Estudiantes:    <nombre>.<apellido>@escuela.edu.bo / 123456'
        ))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _slug(self, text):
        nfkd = unicodedata.normalize('NFKD', text)
        return nfkd.encode('ASCII', 'ignore').decode().lower().replace(' ', '').replace("'", '')

    def _make_email(self, first, last1):
        base = f"{self._slug(first)}.{self._slug(last1)}"
        email = f"{base}@escuela.edu.bo"
        n = 2
        while email in self._used_emails:
            email = f"{base}{n}@escuela.edu.bo"
            n += 1
        self._used_emails.add(email)
        return email

    def _make_username(self, first, last1):
        base = f"{self._slug(first)}.{self._slug(last1)}"
        u = base
        n = 2
        while u in self._used_usernames:
            u = f"{base}{n}"
            n += 1
        self._used_usernames.add(u)
        return u

    def _make_doc(self):
        doc = str(RNG.randint(10000000, 99999999))
        while doc in self._used_docs:
            doc = str(RNG.randint(10000000, 99999999))
        self._used_docs.add(doc)
        return doc

    def _rand_date(self, start, end):
        return start + timedelta(days=RNG.randint(0, (end - start).days))

    def _create_user(self, first, last1, last2, role, phone=''):
        from accounts.models import User
        email = self._make_email(first, last1)
        uname = self._make_username(first, last1)
        return User.objects.create(
            username=uname,
            email=email,
            password=self.pw_hash,
            first_name=first,
            last_name=f'{last1} {last2}',
            role=role,
            phone=phone,
            is_active=True,
        )

    # ── Clear ─────────────────────────────────────────────────────────────────

    def _clear(self):
        from courses.models import (Asistencia, Calificacion, Actividad,
                                     HorarioCurso, Inscripcion, Materia)
        from accounts.models import Estudiante, Docente, Curso
        Asistencia.objects.all().delete()
        Calificacion.objects.all().delete()
        Actividad.objects.all().delete()
        HorarioCurso.objects.all().delete()
        Inscripcion.objects.all().delete()
        Materia.objects.all().delete()
        Estudiante.objects.all().delete()
        Docente.objects.all().delete()
        Curso.objects.all().delete()
        from accounts.models import User
        User.objects.filter(is_superuser=False).delete()

    # ── Staff ─────────────────────────────────────────────────────────────────

    def _create_staff(self):
        u = self._create_user('Pedro', 'Alarcón', 'Saavedra', 'directivo', '999100001')
        self._create_user('Elena', 'Fuentes', 'Moreno', 'administrativo', '999100002')
        self._create_user('Marco', 'Quispe', 'Limache', 'administrativo', '999100003')
        from accounts.models import User
        return User.objects.filter(role='administrativo').first()

    # ── Cursos ────────────────────────────────────────────────────────────────

    def _create_cursos(self):
        from accounts.models import Curso
        nombres = {1: '1ro', 2: '2do', 3: '3ro', 4: '4to', 5: '5to', 6: '6to'}
        cursos_map = {}
        for nivel in ('primaria', 'secundaria'):
            for grado in range(1, 7):
                for sec in ('A', 'B', 'C', 'D'):
                    nombre = f"{nombres[grado]} {nivel.capitalize()} {sec}"
                    c = Curso.objects.create(
                        nombre=nombre, nivel=nivel,
                        cantidad_secciones=1, periodo='2026', estado=True,
                    )
                    cursos_map[(nivel, grado, sec)] = c
        return cursos_map

    # ── Docentes ──────────────────────────────────────────────────────────────

    def _create_docentes(self):
        from accounts.models import Docente
        docentes_map = {}
        cont_start = date(2015, 1, 1)
        cont_end   = date(2023, 12, 31)
        for (fn, ln1, ln2, esp, nivel, grados, titulo) in TEACHERS:
            user = self._create_user(fn, ln1, ln2, 'docente',
                                     f"9{RNG.randint(10000000,99999999)}")
            doc = Docente.objects.create(
                user=user,
                documento=self._make_doc(),
                especialidad=esp,
                titulo_profesional=titulo,
                fecha_contratacion=self._rand_date(cont_start, cont_end),
                estado='activo',
            )
            for g in grados:
                docentes_map[(esp, nivel, g)] = doc
        return docentes_map

    # ── Materias ──────────────────────────────────────────────────────────────

    def _create_materias(self, cursos_map, docentes_map):
        from courses.models import Materia
        materias_map = {}
        nivel_prefix = {'primaria': 'P', 'secundaria': 'S'}
        for (nivel, grado, sec), curso in cursos_map.items():
            lista = MATERIAS_PRIMARIA if nivel == 'primaria' else MATERIAS_SECUNDARIA
            mats = []
            for (nombre, cod, horas) in lista:
                codigo = f"{nivel_prefix[nivel]}{grado}{sec}-{cod}"
                docente = docentes_map.get((nombre, nivel, grado))
                m = Materia.objects.create(
                    nombre=nombre, codigo=codigo, curso=curso,
                    docente=docente, descripcion='',
                    numero_horas=horas, creditos=horas, estado=True,
                )
                mats.append(m)
            materias_map[curso.id] = mats
        return materias_map

    # ── Estudiantes ───────────────────────────────────────────────────────────

    def _create_estudiantes(self, cursos_map, admin_user):
        from accounts.models import Estudiante
        from courses.models import Inscripcion
        birth_ranges = {
            ('primaria',   1): (date(2018, 1, 1), date(2019, 6, 30)),
            ('primaria',   2): (date(2017, 1, 1), date(2018, 6, 30)),
            ('primaria',   3): (date(2016, 1, 1), date(2017, 6, 30)),
            ('primaria',   4): (date(2015, 1, 1), date(2016, 6, 30)),
            ('primaria',   5): (date(2014, 1, 1), date(2015, 6, 30)),
            ('primaria',   6): (date(2013, 1, 1), date(2014, 6, 30)),
            ('secundaria', 1): (date(2012, 1, 1), date(2013, 6, 30)),
            ('secundaria', 2): (date(2011, 1, 1), date(2012, 6, 30)),
            ('secundaria', 3): (date(2010, 1, 1), date(2011, 6, 30)),
            ('secundaria', 4): (date(2009, 1, 1), date(2010, 6, 30)),
            ('secundaria', 5): (date(2008, 1, 1), date(2009, 6, 30)),
            ('secundaria', 6): (date(2007, 1, 1), date(2008, 6, 30)),
        }
        estudiantes_map = {}
        for (nivel, grado, sec), curso in cursos_map.items():
            br_s, br_e = birth_ranges[(nivel, grado)]
            est_list = []
            for _ in range(10):
                fn = RNG.choice(NOMBRES_M if RNG.random() > 0.5 else NOMBRES_F)
                ln1, ln2 = RNG.sample(APELLIDOS, 2)
                user = self._create_user(fn, ln1, ln2, 'estudiante')
                est = Estudiante.objects.create(
                    user=user,
                    numero_expediente=f"2026-{self._exp_counter:04d}",
                    documento=self._make_doc(),
                    fecha_nacimiento=self._rand_date(br_s, br_e),
                    curso=curso,
                    estado='activo',
                )
                self._exp_counter += 1
                Inscripcion.objects.create(
                    estudiante=est, curso=curso,
                    estado='activo', registrada_por=admin_user,
                )
                est_list.append(est)
            estudiantes_map[curso.id] = est_list
        return estudiantes_map

    # ── Horarios ──────────────────────────────────────────────────────────────

    def _create_horarios(self, cursos_map, materias_map):
        from courses.models import HorarioCurso, PeriodoHorario, ClaseHorario
        for (nivel, grado, sec), curso in cursos_map.items():
            horario = HorarioCurso.objects.create(curso=curso)
            template = (HORARIO_PRIMARIA_TEMPLATE if nivel == 'primaria'
                        else HORARIO_SECUNDARIA_TEMPLATE)
            # Índice de materias del curso por nombre
            mat_by_name = {m.nombre: m for m in materias_map.get(curso.id, [])}
            # Crear los 6 periodos
            periodos_obj = {}
            for (orden, hi, hf) in PERIODOS:
                p = PeriodoHorario.objects.create(
                    horario=horario, orden=orden,
                    hora_inicio=hi, hora_fin=hf,
                )
                periodos_obj[orden] = p
            # Asignar materias a los slots
            for (mat_nombre, dia, periodo_orden) in template:
                materia = mat_by_name.get(mat_nombre)
                periodo = periodos_obj.get(periodo_orden)
                if not periodo:
                    continue
                ClaseHorario.objects.get_or_create(
                    periodo=periodo, dia=dia,
                    defaults={'materia': materia},
                )

    # ── Asistencia ────────────────────────────────────────────────────────────

    def _create_asistencia(self, materias_map, estudiantes_map):
        from courses.models import Asistencia
        # Días escolares Feb 3 (lunes) → Apr 30
        start, end = date(2026, 2, 3), date(2026, 4, 30)
        school_days = []
        d = start
        while d <= end:
            if d.weekday() < 5:
                school_days.append(d)
            d += timedelta(days=1)

        bulk = []
        BATCH = 5000

        for curso_id, mats in materias_map.items():
            ests = estudiantes_map.get(curso_id, [])
            if not ests:
                continue
            for mat in mats:
                dias_mat = set(
                    DIA_TO_WD[d] for d in DIAS_POR_HORAS.get(mat.numero_horas, ['lunes', 'miercoles', 'viernes'])
                )
                for day in school_days:
                    if day.weekday() not in dias_mat:
                        continue
                    for est in ests:
                        r = RNG.random()
                        estado = 'P' if r < 0.92 else ('F' if r < 0.97 else 'L')
                        motivo = 'Justificado' if estado == 'L' else ''
                        bulk.append(Asistencia(
                            estudiante=est, materia=mat, fecha=day,
                            estado=estado, motivo=motivo,
                        ))
                        if len(bulk) >= BATCH:
                            Asistencia.objects.bulk_create(bulk)
                            bulk = []
                            self.stdout.write('.', ending='')
        if bulk:
            Asistencia.objects.bulk_create(bulk)
        self.stdout.write('')

    # ── Actividades y Calificaciones ──────────────────────────────────────────

    def _create_actividades_calificaciones(self, materias_map, estudiantes_map):
        from courses.models import Actividad, Calificacion
        now = timezone.now()
        cal_bulk = []
        BATCH = 5000

        for curso_id, mats in materias_map.items():
            ests = estudiantes_map.get(curso_id, [])
            if not ests:
                continue
            for mat in mats:
                docente_user = mat.docente.user if mat.docente else None
                for (nombre, tipo, fecha, trimestre) in ACTIVIDADES:
                    act = Actividad.objects.create(
                        materia=mat, nombre=nombre, descripcion='',
                        tipo=tipo, fecha=fecha, trimestre=trimestre,
                        ponderacion=0, es_plantilla=False, creada_por=docente_user,
                    )
                    for est in ests:
                        if RNG.random() < 0.88:   # 88% de estudiantes tienen nota
                            nota = round(RNG.uniform(40.0, 100.0), 1)
                            c = Calificacion(
                                estudiante=est, actividad=act,
                                nota=nota, creada_por=docente_user,
                            )
                            c.fecha_modificacion = now  # requerido por auto_now en bulk_create
                            cal_bulk.append(c)
                            if len(cal_bulk) >= BATCH:
                                Calificacion.objects.bulk_create(cal_bulk)
                                cal_bulk = []
        if cal_bulk:
            Calificacion.objects.bulk_create(cal_bulk)
