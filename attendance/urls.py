from django.urls import path
from attendance.views.leaves_views import *


urlpatterns = [

    path('test/', test_func, name='employee-leave-detail'),
]
