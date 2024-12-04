from django.urls import include, path
from .views import LoginAPIView


from . import views

urlpatterns = [
    path('', views.horario, name='horario'),
    path('administracion/', views.Administracion, name='administracion'),
     path('registro/', views.registro_entrada_salida, name='registro_entrada_salida'),
     path('login/', LoginAPIView.as_view(), name='login'),
     path('loginu/', views.login, name='loginu'),
     path('sucursal_list', views.sucursal_list, name='sucursal_list'),  # Listar sucursales
    path('crear/', views.sucursal_create, name='sucursal_create'),  # Crear sucursal
    path('editar/<int:id>/', views.sucursal_edit, name='sucursal_edit'),  # Editar sucursal
    path('eliminar/<int:id>/', views.eliminar_sucursal, name='eliminar_sucursal'),
    path('departamento_list', views.listar_departamentos, name='departamento_list'),
    path('crear_departamento/', views.crear_departamento, name='crear_departamento'),
    path('editar_departamento/<int:id>/', views.editar_departamento, name='editar_departamento'),
    path('eliminar_departamento/<int:id>/', views.eliminar_departamento, name='eliminar_departamento'),
    path('puesto_list/', views.lista_puestos, name='puesto_list'),
    path('crear_puesto/', views.crear_puesto, name='crear_puesto'),
    path('editar_puesto/<int:puesto_id>/', views.editar_puesto, name='editar_puesto'),
    path('eliminar_puesto/<int:puesto_id>/', views.eliminar_puesto, name='eliminar_puesto'),
    path('empleado_list/', views.listar_empleados, name='empleado_list'),
    path('get_departamentos/', views.get_departamentos, name='get_departamentos'),
    path('get_puestos/', views.get_puestos, name='get_puestos'),
    path('agregar_empleado/', views.agregar_empleado, name='agregar_empleado'),
    path('editar_empleado/<int:id>/', views.editar_empleado, name='editar_empleado'),
    path('eliminar_empleado/<int:id>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('nomina_list/', views.lista_nominas, name='nomina_list'),
    path('crear_nomina/', views.guardar_nomina, name='crear_nomina'),
    path('imprimir_nomina/<int:codigo>/', views.imprimir_nomina, name='imprimir_nomina'),

]