from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from .models import Employee
from django.shortcuts import render, redirect
from django.contrib import messages
from .ldap_utils import get_user_info, get_ldap_connection
from django.shortcuts import get_object_or_404
from .ldap_utils import demitir_funcionario,is_user_disabled
from django.contrib.auth.mixins import LoginRequiredMixin

class EmployeeCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Employee
    fields = ['usuario']
    template_name = 'records/form.html'
    success_url = reverse_lazy('listar-employee')

    def form_valid(self, form):
        sAMAccountName = form.cleaned_data['usuario']
        
        # Verificar se o usuário já está cadastrado
        if Employee.objects.filter(usuario=sAMAccountName).exists():
            messages.error(self.request, 'Usuário já cadastrado.')
            return self.form_invalid(form)

        # Verificar a conexão com o servidor LDAP
        conn = get_ldap_connection()
        if not conn:
            messages.error(self.request, 'Servidor indisponível, entre em contato com o administrador.')
            return self.form_invalid(form)

        # Verificar se a conta do usuário está desativada
        if is_user_disabled(sAMAccountName):
            messages.error(self.request, 'Esse usuário já foi demitido.')
            return self.form_invalid(form)

        user_info = get_user_info(sAMAccountName)

        if user_info:
            employee = form.save(commit=False)
            employee.nome = user_info.get('displayName', '')
            employee.lider = user_info.get('manager', '')
            employee.cargo = user_info.get('title', '')
            employee.departamento = user_info.get('department', '')
            employee.empresa = user_info.get('company', '')
            employee.lider_email = user_info.get('manager_email', '')  # Usando .get() para tratar a ausência da chave
            employee.save()

            return super().form_valid(form)
        else:
            messages.error(self.request, 'Usuário não encontrado. Por favor, tente novamente.')
            return super().form_invalid(form)



class EmployeeDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Employee
    template_name = 'records/form-excluir.html'
    success_url = reverse_lazy('listar-employee')

class EmployeeList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Employee
    template_name = 'records/list/employee.html'


def demitir_employee(request, pk):
    demitir_funcionario(request, pk)
    return redirect('listar-employee')
