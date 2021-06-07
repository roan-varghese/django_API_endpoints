from django.contrib import admin
from django.urls import path, include

# from testapi.views import TestApiView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # path('', TestApiView.as_view(), name='test'),
]