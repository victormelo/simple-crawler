#encoding: utf-8

import urllib
from bs4 import BeautifulSoup
from soupselect import select
import csv
from collections import OrderedDict

# response = urllib.request.urlopen('http://www.wimoveis.com.br/df/brasilia/apartamento/aluguel')
response = urllib.request.urlopen('http://www.wimoveis.com.br/df/brasilia/apartamento/aluguel/?busca=galeria&r=0&s=0&o=F&pg=0')
source = response.read()
response.close()
soup = BeautifulSoup(source)

try:
    last_page = int(select(soup, '#ctl00_Resultado_ResultadoGaleriaUC1_NavegacaoUC1_labelPaginas')[0].text.strip())
except:
    last_page = 1

responseSoups = list()
pegarTelefone = False
pegarDadosEspecificos = False

casas = []
for pg in range(last_page):
    response = urllib.request.urlopen('http://www.wimoveis.com.br/df/brasilia/apartamento/aluguel/?busca=galeria&r=0&s=0&o=F&pg=%s' % pg)
    source = response.read()
    response.close()
    soup = BeautifulSoup(source)
    # nome = div.findAll('div', {'class' : 'anunciante'})[0].find('p').find('a').text
    for index, listagem in enumerate(select(soup, 'div.listagem_foto')):

        # valor
        valor = select(listagem, 'div.info_galeria div.borda_galeria h4')[0].text.strip()

        # necessário find pois pega-se o primeiro elemento <p>
        imob = listagem.find('p').find('a').text.strip()

        # quartos, suites e garagens
        numQuartos = select(listagem, 'div.borda_galeria span')[0].text.strip()
        numSuites = select(listagem, 'div.borda_galeria span')[1].text.strip()
        numGaragens = select(listagem, 'div.borda_galeria span')[2].text.strip()

        # url
        url = select(listagem, 'div.info_galeria div.borda_galeria a')[0].attrs['href']

        localizacao = select(listagem, 'div.info_galeria div.borda_galeria a h3')[0].text.strip()

        area = select(listagem, 'div.info_galeria div.borda_galeria span')[5].text.strip()

        if(pegarTelefone):
            # telefone
            # uri - necessário para pegar telefone
            uri = url.replace('/imovel/', '')
            responseTelefone = urllib.request.urlopen('http://www.wimoveis.com.br/telefone/'+uri)
            sourceTelefone = responseTelefone.read()
            responseTelefone.close()
            soupTelefone = BeautifulSoup(sourceTelefone)
            telefones = [x.text.strip() for x in select(soupTelefone, 'tbody tr')]

        if(pegarDadosEspecificos):
            responseEspecifico = urllib.request.urlopen('http://www.wimoveis.com.br'+url)
            sourceEspecifico = responseEspecifico.read()
            responseEspecifico.close()
            soupEspecifico = BeautifulSoup(sourceEspecifico)
            codigo = select(soupEspecifico, 'div.conteudo div.dados_do_imovel div.dados_principais p b')[1].text.strip()
            descricao = select(soupEspecifico, '#divDescricao p')[0].text

        dic = OrderedDict()
        dic['valor'] = valor
        dic['numero_quartos'] = numQuartos
        dic['numero_suites'] = numSuites
        dic['numero_garagens'] = numGaragens
        dic['URL'] = 'http://www.wimoveis.com.br' + url
        dic['imobiliaria'] = imob

        if(pegarTelefone):
            for idx, val in enumerate(telefones):
                dic['telefone_'+ str(idx+1)] = val



        dic['localizacao'] = localizacao
        if(pegarDadosEspecificos):
            dic['codigo'] = codigo
            dic['descricao'] = descricao

        dic['area'] = area

        casas.append(dic)

        print('Finished imovel ' + str(index) + ' from page %s' % pg)

with open('mycsvfile.csv', 'w') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, dic.keys())
    w.writeheader()
    for dicBody in casas:
        w.writerow(dicBody)
