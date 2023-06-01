from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('recipes.urls', namespace='recipes')),
    path('admin/', admin.site.urls),
    # path('auth/', include('users.urls')),
    # path('auth/', include('django.contrib.auth.urls')),
]

# handler404 = 'core.views.page_not_found'
# handler403 = 'core.views.permission_denied'
# handler500 = 'core.views.server_error'
