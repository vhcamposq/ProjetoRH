from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter os valores das variáveis de ambiente
ldap_user = os.getenv('LDAP_USER')
ldap_password = os.getenv('LDAP_PASSWORD')


def get_ldap_connection():
    try:
        server = Server('192.168.1.9', port=389)
        conn = Connection(server, user=ldap_user, password=ldap_password)
        conn.bind()
        return conn
    except Exception as e:
        print("Não foi possível conectar com o servidor LDAP:", e)
        return None

def get_user_info(sAMAccountName):
    
    conn = None
    try:
        conn = get_ldap_connection()

        # Fazer a consulta no Active Directory
        conn.search(
            search_base='ou=Vsoft,dc=vserver,dc=ad',
            search_filter=f'(sAMAccountName={sAMAccountName})',
            search_scope=SUBTREE,
            attributes=['cn', 'givenName', 'displayName', 'title', 'department', 'company', 'manager']
        )

        # Obter as informações do usuário
        if len(conn.entries) > 0:
            user_entry = conn.entries[0]
            user_info = {
                'cn': user_entry.cn.value,
                'givenName': user_entry.givenName.value,
                'displayName': user_entry.displayName.value,
                'title': user_entry.title.value if 'title' in user_entry else None,
                'department': user_entry.department.value if 'department' in user_entry else None,
                'company': user_entry.company.value if 'company' in user_entry else None,
                'manager': None
            }

            if 'manager' in user_entry and user_entry.manager.value is not None:
                user_info['manager'] = get_manager_name(user_entry.manager.value)
                user_info['manager_email'] = get_manager_email(user_entry.manager.value)


            return user_info
        else:
            return None
        
    except Exception as e:
        print("Não foi possível obter informações do usuário do servidor LDAP:", e)
        return None
    finally:
        if conn:
            conn.unbind()  # Verifica se a variável conn está definida antes de realizar o unbind


def is_user_disabled(sAMAccountName):
    conn = None
    try:
        conn = get_ldap_connection()

        # Fazer a consulta no Active Directory
        conn.search(
            search_base='ou=Vsoft,dc=vserver,dc=ad',
            search_filter=f'(sAMAccountName={sAMAccountName})',
            search_scope=SUBTREE,
            attributes=['userAccountControl']
        )

        # Verificar se a conta do usuário está desativada
        if len(conn.entries) > 0:
            user_entry = conn.entries[0]
            user_account_control = int(user_entry.userAccountControl.value)
            # O valor 514 representa uma conta desativada no Active Directory
            if user_account_control == 514:
                return True
            else:
                return False
        else:
            return False

    except Exception as e:
        print("Não foi possível verificar o status da conta do usuário no servidor LDAP:", e)
        return False
    finally:
        if conn:
            conn.unbind()



def get_manager_name(manager_dn):
    try:
        conn = get_ldap_connection()

        # Fazer a consulta do gerente no Active Directory
        conn.search(
            search_base=manager_dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['displayName']
        )

        # Obter o nome do gerente
        if len(conn.entries) > 0:
            manager_entry = conn.entries[0]
            manager_name = manager_entry.displayName.value
            return manager_name
        else:
            return None
        
    except Exception as e:
        print("Não foi possível obter o nome do gerente do servidor LDAP:", e)
        return None
    finally:
        conn.unbind()
        
def get_manager_email(manager_dn):
    conn = None  # Inicializar a variável de conexão fora do bloco try

    try:
        conn = get_ldap_connection()

        # Fazer a consulta do gerente no Active Directory
        conn.search(
            search_base=manager_dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['mail']
        )

        # Obter o e-mail do gerente
        if len(conn.entries) > 0:
            manager_entry = conn.entries[0]
            manager_email = manager_entry.mail.value
            return manager_email
        else:
            return None

    except Exception as e:
        print("Não foi possível obter o e-mail do gerente do servidor LDAP:", e)
        return None

    finally:
        if conn:
            conn.unbind()



def disable_user_account(sAMAccountName, user_info):
    try:
        conn = get_ldap_connection()

        # Fazer a consulta no Active Directory
        conn.search(
            search_base='ou=Vsoft,dc=vserver,dc=ad',
            search_filter=f'(sAMAccountName={sAMAccountName})',
            search_scope=SUBTREE,
            attributes=['distinguishedName', 'description']
        )

        # Obter o distinguishedName e a descrição do usuário
        if len(conn.entries) > 0:
            user_entry = conn.entries[0]
            user_dn = user_entry.distinguishedName.value
            description = user_entry.description.value if 'description' in user_entry else ''

            # Atualizar a descrição do usuário com a mensagem de desligamento e a data atual
            today = date.today().strftime("%d/%m/%Y")
            new_description = f"Usuário desligado em {today}."
            if description:
                new_description = f"{new_description} {description}"
            conn.modify(user_dn, {'description': [(MODIFY_REPLACE, [new_description])]})

            # Desativar a conta do usuário
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [514])]})

            # Mover o usuário para o grupo de usuários demitidos
            demitidos_dn = 'ou=Demitidos,ou=Vsoft,dc=vserver,dc=ad'
            conn.modify_dn(user_dn, f'CN={user_info["cn"]}', new_superior=demitidos_dn)

            return True
        else:
            return False

    except Exception as e:
        print("Não foi possível desativar a conta do usuário no servidor LDAP:", e)
        return False
    finally:
        conn.unbind()

def demitir_funcionario(request, pk):
    from .models import Employee
    employee = Employee.objects.get(pk=pk)
    sAMAccountName = employee.usuario

    # Obter as informações do usuário
    user_info = get_user_info(sAMAccountName)

    if user_info:
        try:
            # Desativar a conta do usuário e movê-la para o grupo de usuários demitidos
            if disable_user_account(sAMAccountName, user_info):
                # Enviar e-mail para o líder
                enviar_email_lider(user_info['manager_email'], user_info['manager'], user_info['displayName'])

                # Excluir o objeto Employee
                employee.delete()

                # Retornar mensagem de sucesso com o nome do usuário em negrito
                user_name = user_info['displayName']
                messages.success(request, format_html("<strong>{}</strong> não faz mais parte da Empresa!", user_name))
            else:
                # Retornar mensagem de erro com o nome do usuário em negrito
                user_name = user_info['displayName']
                messages.error(request, format_html("Usuário <strong>{}</strong> não encontrado no Active Directory!", user_name))
        except Exception as e:
            # Tratamento de exceção quando ocorre um erro ao desativar a conta do usuário
            print("Erro ao desativar a conta do usuário:", e)
            messages.error(request, "Ocorreu um erro ao desativar a conta do usuário. Por favor, tente novamente mais tarde.")
    else:
        # Retornar mensagem de erro caso o usuário não seja encontrado no LDAP
        messages.error(request, "Ops! O servidor caiu, favor entre em contado com o administrador.")

    # Redirecionar para a página de listagem após a demissão
    return redirect('listar-employee')

def enviar_email_lider(lider_email, lider_nome, funcionario_nome):
    # Configurações do servidor SMTP do Outlook
    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    smtp_username = 'no-reply.vserver@outlook.com'
    smtp_password = 'vserver@ad'

    # Criação da mensagem de e-mail
    mensagem = MIMEMultipart()
    mensagem['From'] = smtp_username
    mensagem['To'] = lider_email
    mensagem['Subject'] = f'Processo de demissão iniciado para o funcionário {funcionario_nome}'

    corpo_mensagem = f'''
    <html>
        <body>
            <p>Prezado(a) {lider_nome},</p>

            <p>Gostaríamos de informar que o processo de demissão foi iniciado para o funcionário {funcionario_nome}.</p>

            <p>Por favor, tome as medidas necessárias em relação a essa situação.</p>

            <p>Atenciosamente,</p>

            <p>Gente & Cultura</p>
            <br/>
            <p>--</p>
            <p>Sua assinatura de email aqui</p>
        </body>
    </html>
    '''

    mensagem.attach(MIMEText(corpo_mensagem, 'html'))

    # Conexão com o servidor SMTP do Outlook
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        # Envio do e-mail
        server.sendmail(smtp_username, lider_email, mensagem.as_string())
        server.quit()

        print('E-mail enviado com sucesso para o líder!')
    except Exception as e:
        print('Erro ao enviar o e-mail para o líder:', e)
