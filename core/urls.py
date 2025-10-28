from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('sales.urls')),
    # path('', include('employee.urls')),
    # path('', include('rsvp.urls')),
    path('', include('attendance.urls'))
    
]
