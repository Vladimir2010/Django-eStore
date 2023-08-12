from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500, handler400, handler403
from core.views import page_not_found_view, forrbiden, bad_request, internal_server_error
from django.urls import re_path
from django.views.static import serve


handler404 = page_not_found_view
handler500 = internal_server_error
handler400 = bad_request
handler403 = forrbiden


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('allauth.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('staff/', include('staff.urls', namespace='staff')),
    path('page_not_found_view/', page_not_found_view, name="page_not_found"),
    path('bad_request/', bad_request, name="bad_request"),
    path('internal_server_error/', internal_server_error, name="internal_server_error"),
    path('forrbiden/', forrbiden, name="forrbiden"),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                            document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                            document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL,
                            document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                            document_root=settings.MEDIA_ROOT)

