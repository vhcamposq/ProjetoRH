from django.urls import path
from .views import EmployeeCreate, EmployeeDelete
from .views import EmployeeList
from .views import demitir_employee

urlpatterns = [
    #create
    path('records/employee', EmployeeCreate.as_view(), name="records-employee"),
    
    
    #delete
    path('delete/employee/<int:pk>/',EmployeeDelete.as_view(), name='delete-employee'),

    
    #list
    path('listar/employee/', EmployeeList.as_view(), name='listar-employee'),

    #demitir
    
    path('demitir/employee/<int:pk>/', demitir_employee, name='demitir-employee'),
]
