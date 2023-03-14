from django.shortcuts import render
from .models import *
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants

def nova_empresa(request):

    if request.method == "GET":

        techs = Tecnologias.objects.all()

        context = {
            'techs': techs
        }
        return render(request, "nova_empresa.html",context)

    elif request.method == "POST":
        
        #RECEBENDO DADOS DO FORMULÁRIO
        
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cidade = request.POST.get('cidade')
        endereco = request.POST.get('endereco')
        nicho = request.POST.get('nicho')
        caracteristicas = request.POST.get('caracteristicas')
        tecnologias = request.POST.getlist('tecnologias')
        logo = request.FILES.get('logo')

        #VALIDAÇÕES

        #O "strip()" tira oas espaços em branco do formulário, se o nome nao tiver nada e com espaços em branco, ele será igual a zero, e isso vai ser dado como inválido pelo IF. 
        if (len(nome.strip()) == 0 or len(email.strip()) == 0 or len(cidade.strip()) == 0 or len(endereco.strip()) == 0 or len(nicho.strip()) == 0 or len(caracteristicas.strip()) == 0 or (not logo)):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos') 
            return redirect('/home/nova_empresa')

        #VALIDANDO O TAMANHO DO ARQUIVO. O ARQUIVO NÃO PODE PASSAR DE 10MB.
        if logo.size > 100_000_000:
            messages.add_message(request, constants.ERROR, 'A logo da empresa deve ter menos de 10MB')
            return redirect('/home/nova_empresa')

        # 1-Se o "nicho" que o usuáio escolheu não estiver dentro da lista(opções dentro da Model) ele será invalidado.
        # 2-Isso servirá caso o usuário altere pelo comando "F12" os "values"  dos "options" do Formulário no HTML.
        # 3-EX: O value do Desing é "D", se o usuário alterar o options, e pôr qualquer outra coisa diferente do "D", "N" e "M" ele será invalidado.
        if nicho not in [i[0] for i in Empresa.choices_nicho_mercado]:
            messages.add_message(request, constants.ERROR, 'Nicho de mercado inválido')
            return redirect('/home/nova_empresa')
        
        #SALVANDO NO BANCO DE DADOS

        empresa = Empresa(logo=logo,
                        nome=nome,
                        email=email,
                        cidade=cidade,
                        endereco=endereco,
                        nicho_mercado=nicho,
                        caracteristica_empresa=caracteristicas)

        empresa.save()
        empresa.tecnologias.add(*tecnologias)
        empresa.save()
        messages.add_message(request, constants.SUCCESS, 'Empresa cadastrada com sucesso')

        return redirect('/home/nova_empresa')


def empresas(request):

    tecnologias_filter = request.GET.get('tecnologias')
    nome_filter = request.GET.get('nome')
    empresas = Empresa.objects.all()

    # FILTROS
    if tecnologias_filter:
        empresas = empresas.filter(tecnologias = tecnologias_filter)

    if nome_filter:
        empresas = empresas.filter(nome__icontains = nome_filter)
    
    tecnologias = Tecnologias.objects.all()
    return render(request, 'empresas.html', {'empresas': empresas, 'tecnologias': tecnologias}) 

def excluir_empresa(request, id):
    empresa = Empresa.objects.get(id=id)
    empresa.delete()
    messages.add_message(request, constants.SUCCESS, 'Empresa excluída com sucesso')
    return redirect('/home/empresas')

def empresa_unica(request, id):
    empresa_unica = get_object_or_404(Empresa, id=id)
    empresas = Empresa.objects.all()
    tecnologias = Tecnologias.objects.all()

    vagas = Vagas.objects.filter(empresa_id=id)

    context ={
        'empresa': empresa_unica,
        'tecnologias':tecnologias,
        'empresas': empresas,
        'vagas':vagas
    }

    return render(request, 'empresa_unica.html', context)    