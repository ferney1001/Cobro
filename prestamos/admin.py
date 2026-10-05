from django.contrib import admin
from .models import Prestamo, Cuota, Pago


admin.site.register(Prestamo)
admin.site.register(Cuota)
admin.site.register(Pago)