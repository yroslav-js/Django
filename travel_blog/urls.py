from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='travel_posts')),
]

handler404 = 'core.views.page_not_found' # noqa
handler500 = 'core.views.server_error'  # noqa
handler403 = 'core.views.permission_denied' # noqa

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
