from django.contrib import admin
from django.urls import path, include
from api.views import redirect_view 

# from testapi.views import TestApiView 

urlpatterns = [
    path('', redirect_view),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # path('', TestApiView.as_view(), name='test'),
]