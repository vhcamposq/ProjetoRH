from django.db import models

class Employee(models.Model):
    nome = models.CharField(max_length=50)
    usuario = models.CharField(max_length=30, verbose_name='Usuário')
    cargo = models.CharField(max_length=50, default='', null=True, blank=True)
    departamento = models.CharField(max_length=50, default='', null=True, blank=True)
    empresa = models.CharField(max_length=50, default='', null=True, blank=True)
    lider = models.CharField(max_length=50, null=True, blank=True, default=None)
    lider_email = models.EmailField(max_length=254, null=True, blank=True, default=None)


    def __str__(self):
        return '{} - {} - {} - {} - {} - {} - {}'.format(self.nome, self.usuario, self.lider, self.lider_email, self.cargo, self.departamento, self.empresa)
