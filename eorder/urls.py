from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin bawaan
    path('admin/', admin.site.urls),

    # Halaman pelanggan (root URL)
    path('', include('pelanggan.urls')),

    # Dashboard kasir
    path('kasir/', include('kasir.urls')),

    # Data menu (API internal)
    path('menu-data/', include('menu.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)