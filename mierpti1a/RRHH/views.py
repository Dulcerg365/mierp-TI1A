from pyexpat.errors import messages
from unittest import loader
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from .models import Nomina

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Empleado, Salida_Entrada
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
import json 


def horario(request):
    return render(request, 'RRHH/horario.html')
def login(request):
    return render(request, 'RRHH/login.html')
def Administracion(request):
    return render(request, 'RRHH/Administracion.html')
def registro_entrada_salida(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            folio = data.get('folio')
            action = data.get('action')
            password = data.get('password')

            if not folio or not action or not password:
                return JsonResponse({'success': False, 'error': 'Faltan campos requeridos'}, status=400)

            # Autenticación del usuario
            user = authenticate(username=folio, password=password)
            if user is None:
                return JsonResponse({'success': False, 'error': 'Credenciales incorrectas'}, status=400)

            # Obtener el empleado relacionado con el usuario autenticado
            try:
                empleado = Empleado.objects.get(Username=user)
            except Empleado.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=400)

            # Registro de entrada o salida
            nuevo_registro = Salida_Entrada(codigo_empleado=empleado, hora=timezone.now(), opcion=action)
            nuevo_registro.save()

            return JsonResponse({
                'success': True,
                'empleado': {
                    'nombre': empleado.nombre,
                    'foto': empleado.foto.url if empleado.foto else None
                },
                'action': action
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Error en el cuerpo de la solicitud'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        folio = data.get('folio')
        password = data.get('password')

        if not folio or not password:
            return Response({'success': False, 'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        # Autenticación del usuario
        user = authenticate(username=folio, password=password)
        if user is None:
            return Response({'success': False, 'error': 'Credenciales incorrectas'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el empleado relacionado con el usuario autenticado
        try:
            empleado = Empleado.objects.get(Username=user)
        except Empleado.DoesNotExist:
            return Response({'success': False, 'error': 'Empleado no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        print(empleado.sucursal_id)

        return Response({
            'success': True,
            'empleado': {
                'id': str(empleado.id),
                'nombre': str(empleado.nombre),
                'apellidos': str(empleado.apellidos),
                'sucursal': str(empleado.sucursal_id),
                'nombre_sucursal': str(empleado.sucursal),
                'puesto': str(empleado.puesto),
            },
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        return Response({'success': False, 'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
def get_sucursales(request):
    sucursales = list(Sucursal.objects.values())

    if len(sucursales) > 0:
        data = {'message': "Success", 'sucursales': sucursales}
    else:
        data = {'message': "Not Found"}
    
    return JsonResponse(data)

def get_empleados(request):
    empleados = list(Empleado.objects.values())

    if len(empleados) > 0:
        data= {'message': "Success", 'empleados':empleados}
    else:
        data = {'message': "Not found"}
    return JsonResponse(data)

# Listar sucursales
def sucursal_list(request):
    sucursales = Sucursal.objects.all()
    return render(request, 'RRHH/Sucursal.html', {'sucursales': sucursales})

def sucursal_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        Sucursal.objects.create(nombre=nombre, direccion=direccion)
        return JsonResponse({'message': 'Sucursal creada exitosamente!'})
    return JsonResponse({'error': 'Método no permitido'}, status=400)

# Editar sucursal
def sucursal_edit(request, id):
    sucursal = get_object_or_404(Sucursal, id=id)
    if request.method == 'POST':
        sucursal.nombre = request.POST.get('nombre')
        sucursal.direccion = request.POST.get('direccion')
        sucursal.save()
        return JsonResponse({'message': 'Sucursal actualizada exitosamente!'})
    return JsonResponse({'error': 'Método no permitido'}, status=400)

def eliminar_sucursal(request, id):
    if request.method == 'POST':
        try:
            sucursal = Sucursal.objects.get(pk=id)
            sucursal.delete()
            return JsonResponse({'message': 'Sucursal eliminada correctamente'})
        except Sucursal.DoesNotExist:
            return JsonResponse({'error': 'Sucursal no encontrada'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Listar departamentos
def listar_departamentos(request):
    departamentos = Departamento.objects.all()
    sucursales = Sucursal.objects.all()
    return render(request, 'RRHH/Departamento.html', {
        'departamentos': departamentos,
        'sucursales': sucursales
    })

# Crear departamento
def crear_departamento(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        sucursal_id = request.POST.get('sucursal')
        sucursal = get_object_or_404(Sucursal, id=sucursal_id)

        Departamento.objects.create(nombre=nombre, sucursal=sucursal)
        return JsonResponse({'message': 'Departamento creado exitosamente!'})

    return JsonResponse({'error': 'Método no permitido'}, status=400)

# Editar departamento
def editar_departamento(request, id):
    departamento = get_object_or_404(Departamento, id=id)
    if request.method == 'POST':
        departamento.nombre = request.POST.get('nombre')
        sucursal_id = request.POST.get('sucursal')
        departamento.sucursal = get_object_or_404(Sucursal, id=sucursal_id)
        departamento.save()
        return JsonResponse({'message': 'Departamento actualizado exitosamente!'})

    return JsonResponse({'error': 'Método no permitido'}, status=400)

# Eliminar departamento
def eliminar_departamento(request, id):
    if request.method == 'POST':
        departamento = get_object_or_404(Departamento, id=id)
        departamento.delete()
        return JsonResponse({'message': 'Departamento eliminado correctamente'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para listar los puestos
def lista_puestos(request):
    puestos = Puesto.objects.all()
    departamentos = Departamento.objects.all()
    return render(request, 'RRHH/Puesto.html', {
        'puestos': puestos,
        'departamentos': departamentos
    })

# Vista para crear un nuevo puesto
def crear_puesto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        departamento_id = request.POST.get('departamento')
        
        # Validar los datos recibidos
        if not nombre or not departamento_id:
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)
        
        # Obtener el departamento relacionado
        departamento = get_object_or_404(Departamento, id=departamento_id)

        # Crear el puesto
        puesto = Puesto.objects.create(nombre=nombre, departamento=departamento)
        return JsonResponse({'message': 'Puesto creado exitosamente'}, status=200)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para editar un puesto existente
def editar_puesto(request, puesto_id):
    puesto = get_object_or_404(Puesto, id=puesto_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        departamento_id = request.POST.get('departamento')

        if not nombre or not departamento_id:
            return JsonResponse({'error': 'Todos los campos son requeridos'}, status=400)

        departamento = get_object_or_404(Departamento, id=departamento_id)

        puesto.nombre = nombre
        puesto.departamento = departamento
        puesto.save()

        return JsonResponse({'message': 'Puesto actualizado exitosamente'}, status=200)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para eliminar un puesto
def eliminar_puesto(request, puesto_id):
    if request.method == 'POST':
        puesto = get_object_or_404(Puesto, id=puesto_id)
        puesto.delete()
        return JsonResponse({'message': 'Puesto eliminado exitosamente'}, status=200)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def listar_empleados(request):
    departamentos = Departamento.objects.all()
    sucursales = Sucursal.objects.all()
    puestos = Puesto.objects.all()
    empleados = Empleado.objects.all()
    return render(request, 'RRHH/Empleados.html', {
        'empleados':empleados,
        'puestos':puestos,
        'departamentos': departamentos,
        'sucursales': sucursales
    })

# Vista para obtener departamentos basados en la sucursal
def get_departamentos(request):
    sucursal_id = request.GET.get('sucursal_id')
    departamentos = Departamento.objects.filter(sucursal_id=sucursal_id).values('id', 'nombre')
    return JsonResponse({'departamentos': list(departamentos)})

# Vista para obtener puestos basados en el departamento
def get_puestos(request):
    departamento_id = request.GET.get('departamento_id')
    puestos = Puesto.objects.filter(departamento_id=departamento_id).values('id', 'nombre')
    return JsonResponse({'puestos': list(puestos)})

def agregar_empleado(request):
    if request.method == 'POST':
        # Recibe los datos del formulario
        data = request.POST
        # Crea un nuevo empleado
        try:
            Empleado.objects.create(
                nombre=data['name'],
                apellidos=data['apellidos'],
                correo=data['correo'],
                numero=data['numero'],
                fecha_nac=data['fecha_nac'],
                estado_civil=data['estado_civil'],
                edad=data['edad'],
                sexo=data['sexo'],
                rfc=data['rfc'],
                curp=data['curp'],
                sucursal_id=data['sucursal'],
                departamento_id=data['depa'],
                puesto_id=data['puesto'],
                foto=request.FILES.get('foto')  # Maneja la foto
            )
            return JsonResponse({'message': 'Empleado agregado correctamente', 'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False}, status=500)
    return JsonResponse({'success': False}, status=400)

def editar_empleado(request, id):
    if request.method == 'POST':  # Usamos POST, con un 'method_override' desde el frontend
        empleado = get_object_or_404(Empleado, id=id)
        data = request.POST
        try:
            empleado.nombre = data['name']
            empleado.apellidos = data['apellidos']
            empleado.correo = data['correo']
            empleado.numero = data['numero']
            empleado.fecha_nac = data['fecha_nac']
            empleado.estado_civil = data['estado_civil']
            empleado.edad = data['edad']
            empleado.sexo = data['sexo']
            empleado.rfc = data['rfc']
            empleado.curp = data['curp']
            empleado.sucursal_id = data['sucursal']
            empleado.departamento_id = data['depa']
            empleado.puesto_id = data['puesto']
            if 'foto' in request.FILES:
                empleado.foto = request.FILES['foto']  # Actualiza la foto si se sube una nueva
            empleado.save()
            return JsonResponse({'message': 'Empleado actualizado correctamente', 'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False}, status=500)
    return JsonResponse({'success': False}, status=400)
def eliminar_empleado(request, id):
    if request.method == 'DELETE':
        try:
            empleado = get_object_or_404(Empleado, id=id)
            empleado.delete()
            return JsonResponse({'message': 'Empleado eliminado correctamente', 'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False}, status=500)
    return JsonResponse({'success': False}, status=400)

def lista_nominas(request):
    nominas = Nomina.objects.all()
    puestos = Puesto.objects.all()
    empleados = Empleado.objects.all()
    departamentos = Departamento.objects.all()
    return render(request, 'RRHH/Nomina.html', {
        'nominas': nominas,
        'puestos':puestos,
        'empleados':empleados,
        'departamentos': departamentos
    })
def guardar_nomina(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        codigo = request.POST.get('codigo')
        nombre_empleado_id = request.POST.get('nombre')
        departamento_id = request.POST.get('departamento')
        puesto_id = request.POST.get('puesto')
        tipo_nomina = request.POST.get('tiponomina')
        salario_diario = request.POST.get('salario_diario')
        dias_trabajados = request.POST.get('dias_trabajados')
        monto_DA = request.POST.get('monto_DA', 0)  # Default 0 si no se proporciona
        monto_DP = request.POST.get('monto_DP', 0)  # Default 0 si no se proporciona
        
        # Convertir los valores numéricos a float
        salario_diario = float(salario_diario)
        dias_trabajados = int(dias_trabajados)
        monto_DA = float(monto_DA)
        monto_DP = float(monto_DP)

        # Calcular percepciones, deducciones y salario final
        percepciones = salario_diario * dias_trabajados
        deducciones = monto_DA + monto_DP
        salario_final = percepciones - deducciones
        
        # Obtener los objetos de empleado, departamento y puesto
        empleado = Empleado.objects.get(id=nombre_empleado_id)
        departamento = Departamento.objects.get(id=departamento_id)
        puesto = Puesto.objects.get(id=puesto_id)

        # Crear la nómina
        nueva_nomina = Nomina(
            codigo=codigo,
            nombre=empleado,
            departamento=departamento,
            puesto=puesto,
            tiponomina=tipo_nomina,
            salario_diario=salario_diario,
            dias_trabajados=dias_trabajados,
            monto_DA=monto_DA,
            monto_DP=monto_DP,
            total_percepciones=percepciones,
            deducciones=deducciones,
            salario_final=salario_final
        )
        nueva_nomina.save()

        # Devolver una respuesta JSON
        return JsonResponse({"success": True, "message": "Nómina agregada correctamente."})
    else:
        return JsonResponse({"success": False, "message": "Método no permitido."})


def imprimir_nomina(request, codigo):
    try:
        # Obtén la nómina a partir del ID
        nomina = Nomina.objects.get(codigo=codigo)

        # Crea la respuesta HTTP con el tipo de contenido 'application/pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="nomina_{id}.pdf"'

        # Crea un objeto Canvas para el PDF
        p = canvas.Canvas(response, pagesize=letter)
        
        # Agrega contenido al PDF
        p.drawString(100, 750, f"Nomina para: {nomina.nombre.nombre}")
        p.drawString(100, 735, f"Departamento: {nomina.departamento.nombre}")
        p.drawString(100, 720, f"Puesto: {nomina.puesto.nombre}")
        p.drawString(100, 705, f"Fecha de pago: {nomina.fecha_pago}")
        p.drawString(100, 690, f"Salario diario: ${nomina.salario_diario}")
        p.drawString(100, 675, f"Deducciones: ${nomina.deducciones}")
        p.drawString(100, 660, f"Total: ${nomina.salario_final}")

        # Finaliza la creación del PDF
        p.showPage()
        p.save()

        return response
    except Nomina.DoesNotExist:
        return HttpResponse("Nómina no encontrada", status=404)