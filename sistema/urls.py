from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Público
    path("", views.home, name="home"),
    path("evento/<int:pk>/", views.detalle_evento, name="detalle_evento"),
    path("tesis/", views.tesis_lista, name="tesis_lista"),
    # Auth
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    # Estudiante
    path("evento/<int:pk>/inscribir/", views.inscribir_evento, name="inscribir_evento"),
    path("evento/<int:pk>/cancelar/", views.cancelar_inscripcion, name="cancelar_inscripcion"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/notificaciones/", views.configuracion_notificaciones, name="configuracion_notificaciones"),
    # Admin
    path("gestion/", views.admin_panel, name="admin_panel"),
    path("gestion/evento/nuevo/", views.admin_evento_crear, name="admin_evento_crear"),
    path("gestion/evento/<int:pk>/editar/", views.admin_evento_editar, name="admin_evento_editar"),
    path("gestion/evento/<int:pk>/eliminar/", views.admin_evento_eliminar, name="admin_evento_eliminar"),
]
