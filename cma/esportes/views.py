# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import simplejson
from django.db.models import Count
from esportes.models import Estadio, Campeonato, EdicaoCampeonato, Equipe, Jogo, Jogador, Gol
from random import randint
import urllib

TEMPO_NORMAL = "N"
TEMPO_PRORROGACAO = "P"
TEMPO_PENALTI = "PE"

def get_game_text(request, jogo_id=None):

    jogo = Jogo.objects.get(id=jogo_id)
    edicao = EdicaoCampeonato.objects.get(id=jogo.edicaoCampeonato_id)
    campeonato = Campeonato.objects.get(id=edicao.campeonato_id)
    mandante = Equipe.objects.get(id=jogo.mandante_id)
    visitante = Equipe.objects.get(id=jogo.visitante_id)
    estadio = Estadio.objects.get(id=jogo.estadio_id)

    to_json = {
        "id": jogo_id,
        "mandante": mandante.nome,
        "visitante": visitante.nome,
        "placar_mandante_normal": get_total_gols_equipe_partida(jogo.id, mandante.id, TEMPO_NORMAL),
        "placar_visitante_normal": get_total_gols_equipe_partida(jogo.id, visitante.id, TEMPO_NORMAL),
        "campeonato": campeonato.nome,
        "video": jogo.video,
        "maps": urllib.quote("https://maps.google.com.br/maps?q=" + estadio.nome + "+" + estadio.cidade + "&radius=15000&z=14&t=m", safe="%/:=&?~#+!$,;'@()*[]"),
        "review": get_review(jogo)
    }

    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')# Create your views here.

def get_total_gols_equipe_partida(jogo, equipe, tempo):

    if(tempo != TEMPO_PENALTI):
        return Jogo.objects.filter(gols__tempo=("1"+tempo), gols__equipe_id=equipe, id=jogo).count() + Jogo.objects.filter(gols__tempo=("2"+tempo), gols__equipe_id=equipe, id=jogo).count()
    else:
        return Jogo.objects.filter(gols__tempo=(tempo), gols__equipe_id=equipe, id=jogo).count()

def get_review(jogo):

    contextos = {
        "historico": {
            "local": get_frase_local(jogo)
        },
        "factual": {
            "resultado_tempo_normal": get_frase_resultado(jogo),
            "campeonato": get_frase_campeonato(jogo),
            "gols": get_gols_partida(jogo),
            "penaltis": get_penaltis(jogo),
        }
    }

    f = contextos["factual"]["resultado_tempo_normal"].capitalize() + ", " + contextos["factual"]["campeonato"]
    h = contextos["historico"]["local"]
    g = (contextos["factual"]["gols"] + ".") if( contextos["factual"]["gols"] != "" ) else ""
    k = (contextos["factual"]["penaltis"] + ".") if( contextos["factual"]["penaltis"] != "" ) else ""

    return "%s, %s. %s %s" % (f, h, g, k)

#######################################################################################################################
# contexto factual > resultado
#######################################################################################################################
def get_frase_resultado(jogo):

    mandante = Equipe.objects.get(id=jogo.mandante_id)
    visitante = Equipe.objects.get(id=jogo.visitante_id)

    placar_mandante = get_total_gols_equipe_partida(jogo.id, mandante.id, TEMPO_NORMAL)
    placar_visitante = get_total_gols_equipe_partida(jogo.id, visitante.id, TEMPO_NORMAL)

    frase_tempo_normal = get_frase_vencedor_ou_empate(mandante, visitante, placar_mandante, placar_visitante)

    # caso tenha ido para prorrogacao
    placar_mandante_na_prorrogacao = get_total_gols_equipe_partida(jogo.id, mandante.id, TEMPO_PRORROGACAO)
    placar_visitante_na_prorrogacao = get_total_gols_equipe_partida(jogo.id, visitante.id, TEMPO_PRORROGACAO)

    # caso tenha ido aos penaltis
    placar_mandante_nos_penaltis = get_total_gols_equipe_partida(jogo.id, mandante.id, TEMPO_PENALTI)
    placar_visitante_nos_penaltis = get_total_gols_equipe_partida(jogo.id, visitante.id, TEMPO_PENALTI)

    frase_tempo_prorrogacao = ""
    frase_tempo_penaltis = ""

    if(placar_mandante_nos_penaltis != 0 or placar_visitante_nos_penaltis != 0):
        frase_tempo_penaltis = get_frase_penaltis_inicio() + " " + get_frase_vencedor_ou_empate(mandante, visitante, placar_mandante_nos_penaltis, placar_visitante_nos_penaltis) + ", "

        placar_normal = get_frase_placar(placar_mandante, placar_visitante, False)
        placar_prorrogacao = get_frase_placar(placar_mandante_na_prorrogacao, placar_visitante_na_prorrogacao, False)

        if(placar_normal == placar_prorrogacao):
            frase_tempo_normal = ""
            frase_tempo_prorrogacao = u" após 120 minutos o resultado ainda era " + placar_normal
        else:
            frase_tempo_prorrogacao = u" na prorrogação o resultado foi de " + placar_prorrogacao
            frase_tempo_normal = u" e " + placar_normal + ", no tempo normal"

    elif(placar_mandante_na_prorrogacao != 0 or placar_visitante_na_prorrogacao != 0):
        frase_tempo_prorrogacao = "Na prorrogacao" + ", " + get_frase_vencedor_ou_empate(mandante, visitante, placar_mandante_na_prorrogacao, placar_visitante_na_prorrogacao) + ", "
        frase_tempo_normal = u" no tempo normal o resultado foi de " + get_frase_placar(placar_mandante, placar_visitante, False)


    return frase_tempo_penaltis + frase_tempo_prorrogacao + frase_tempo_normal

def get_frase_vencedor_ou_empate(mandante, visitante, placar_mandante, placar_visitante):

    frase_temporaria = ""

    if (placar_mandante == placar_visitante):

        frase_temporaria = get_frase_empate(mandante, visitante, placar_mandante) + " " + get_frase_placar(placar_mandante, placar_mandante)

    else:
        if ( placar_mandante > placar_visitante ):

            vencedor = mandante
            derrotado = visitante

            frase_vencedor = get_frase_vencedor_goleada(vencedor, derrotado) if( (placar_mandante - placar_visitante) >= 3 ) else get_frase_vencedor(vencedor, derrotado)

            frase_temporaria = frase_vencedor + " " + get_frase_placar(placar_mandante, placar_visitante)
        else:

            vencedor = visitante
            derrotado = mandante

            frase_temporaria = get_frase_vencedor(vencedor, derrotado) + " " + get_frase_placar(placar_visitante, placar_mandante)

    return frase_temporaria

def get_frase_penaltis_inicio():

    frases = [u"Em um jogo decidido nos pênaltis, ",
              u"Em uma partida decidida nos pênaltis, ",
              u"A partida foi para os pênaltis, neles ",
              u"A decisão foi para os pênaltis, neles ",
              u"O resultado só veio após os pênaltis, onde",
              u"O resultado só saiu após os pênaltis, onde",
            ]

    return sorteia_frase(frases)

def get_frase_vencedor(vencedor, derrotado):

    frases = [u"%s venceu %s",
              u"%s levou a melhor sobre %s",
              u"%s venceu a disputa contra %s",
              u"%s venceu o duelo contra %s",
              u"%s venceu a batalha contra %s",
              u"%s terminou o jogo em vantagem sobre %s",
            ]

    return sorteia_frase(frases) % (get_time_gentilico(vencedor), get_time_gentilico(derrotado))

def get_time_gentilico(equipe):
    if( randint(0, 1) ):
      trecho_vencedor = u"%s %s" % (get_equipe_genero(equipe), equipe.nome)
    else:
      trecho_vencedor = u"o time %s" % equipe.gentilico
    return trecho_vencedor

def get_frase_vencedor_goleada(vencedor, derrotado):

    frases = [u"%s goleou %s",
              u"%s sapecou %s",
              u"%s levou a melhor sobre %s",
              u"%s venceu, com folga, a disputa contra %s",
              u"%s venceu, com folga, o duelo contra %s",
              u"%s venceu, com folga, a batalha contra %s",
            ]

    return sorteia_frase(frases) % (get_time_gentilico(vencedor), get_time_gentilico(derrotado))

def get_frase_placar(placar_a, placar_b, conector=True):

    if(conector):
        frases = [u"com o placar de %s a %s",
                  u"em %s a %s",
                  u"por %s a %s",
                ]
    else:
        frases = [u"%s a %s"]

    return sorteia_frase(frases) % (placar_a, placar_b)

def get_frase_empate(mandante, visitante, placar):

    frases = [u"%s e %s empataram",
              u"%s e %s ficaram no empate",
            ]

    return sorteia_frase(frases) % (mandante.nome, visitante.nome)

#######################################################################################################################
# contexto gols
#######################################################################################################################
def get_gols_partida(jogo):

    gols_mandante = Jogo.objects.filter(id=jogo.id)[0].gols.filter(equipe_id=jogo.mandante_id).exclude(tempo="PE")
    gols_visitante = Jogo.objects.filter(id=jogo.id)[0].gols.filter(equipe_id=jogo.visitante_id).exclude(tempo="PE")
    mandante = Equipe.objects.get(id=jogo.mandante_id)
    visitante = Equipe.objects.get(id=jogo.visitante_id)

    if( len(gols_mandante) or len(gols_mandante) ):

        gols_mandante_texto = ""

        for i in range(len(gols_mandante)):
            if( i > 0 and i != (len(gols_mandante) - 1) ):
                gols_mandante_texto += ", "
            if( i > 0 and i == (len(gols_mandante) - 1) ):
                gols_mandante_texto += " e "
            gols_mandante_texto += gols_mandante[i].jogador.nome + " ("+ str(gols_mandante[i].momento) +"')"

        if (len(gols_mandante)):
            gols_mandante_texto = "%s pel%s %s" % (gols_mandante_texto, mandante.nome_genero, mandante.nome)

        gols_visitante_texto = ""

        for i in range(len(gols_visitante)):

            if( i > 0 and i != (len(gols_visitante) - 1) ):
                gols_visitante_texto += ", "
            if( i > 0 and i == (len(gols_visitante) - 1) ):
                gols_visitante_texto += " e "
            gols_visitante_texto += gols_visitante[i].jogador.nome + " ("+ str(gols_visitante[i].momento) +"')"

        if (len(gols_visitante)):
            gols_visitante_texto = "%s pel%s %s" % (gols_visitante_texto, visitante.nome_genero, visitante.nome)


        if (len(gols_mandante) and len(gols_visitante)):
            todos_gols_texto = gols_mandante_texto + " e " + gols_visitante_texto
            return get_gol_plural(todos_gols_texto)
        elif ( (len(gols_mandante) + len(gols_visitante)) > 1 ):
            todos_gols_texto = gols_mandante_texto + "" + gols_visitante_texto
            return get_gol_plural(todos_gols_texto)
        else:
            todos_gols_texto = gols_mandante_texto + gols_visitante_texto
            return get_gol_unico(todos_gols_texto)

    return ""

def get_gol_unico(todos_gols_texto):
    frases = [u"O autor do gol da partida foi %s",
              u"O único gol da partida foi de %s",
              u"O único gol do jogo foi de %s",
              u'O gol marcado por %s foi o único da partida',
              u'%s marcou o gol da vitória',
              u'%s fez o único gol da partida',
              u'O gol da vitória foi marcado por %s',
              u'A vitória veio de um gol de %s',
              u'%s foi o nome da partida, marcando o único gol',
              u'%s garantiu a vitória, marcando o gol da partida',
              ]

    return sorteia_frase(frases) % (todos_gols_texto)

def get_gol_plural(todos_gols_texto):
    frases = [u"Fizeram os gols da partida: %s",
              u"Marcaram os gols da partida: %s",
              u"Os gols foram feitos por %s",
              u"Os gols foram marcados por %s",
              u"Os gols do jogo foram marcados por %s",
              u"Os gols da partida foram marcados por %s",
              u"Os gols foram de %s",
              u"O placar foi construído por %s",
              u"Construíram o placar %s",
              u"Balançaram as redes: %s",
              ]

    return sorteia_frase(frases) % (todos_gols_texto)

def get_penaltis(jogo):

    gols_mandante = Jogo.objects.filter(id=jogo.id)[0].gols.filter(equipe_id=jogo.mandante_id, tempo="PE")
    gols_visitante = Jogo.objects.filter(id=jogo.id)[0].gols.filter(equipe_id=jogo.visitante_id, tempo="PE")
    mandante = Equipe.objects.get(id=jogo.mandante_id)
    visitante = Equipe.objects.get(id=jogo.visitante_id)

    if( len(gols_mandante) or len(gols_mandante) ):

        gols_mandante_texto = ""

        for i in range(len(gols_mandante)):
            if( i > 0 and i != (len(gols_mandante) - 1) ):
                gols_mandante_texto += ", "
            if( i > 0 and i == (len(gols_mandante) - 1) ):
                gols_mandante_texto += " e "

            gols_mandante_texto += gols_mandante[i].jogador.nome

        if (len(gols_mandante)):
            gols_mandante_texto = "%s pel%s %s" % (gols_mandante_texto, mandante.nome_genero, mandante.nome)

        gols_visitante_texto = ""

        for i in range(len(gols_visitante)):
            if( i > 0 and i != (len(gols_visitante) - 1) ):
                gols_visitante_texto += ", "
            if( i > 0 and i == (len(gols_visitante) - 1) ):
                gols_visitante_texto += " e "
            gols_visitante_texto += gols_visitante[i].jogador.nome

        if (len(gols_visitante)):
            gols_visitante_texto = "%s pel%s %s" % (gols_visitante_texto, visitante.nome_genero, visitante.nome)

        if (len(gols_mandante) and len(gols_visitante)):
            todos_gols_texto = gols_mandante_texto + ", " + gols_visitante_texto
        else:
            todos_gols_texto = gols_mandante_texto + gols_visitante_texto

        return get_frase_penaltis(todos_gols_texto)

    return ""

def get_frase_penaltis(todos_gols_texto):
    frases = [u"Na disputa dos pênaltis fizeram os gols: %s",
             ]

    return sorteia_frase(frases) % (todos_gols_texto)

#######################################################################################################################
# contexto factual > campeonato
#######################################################################################################################
def get_frase_campeonato(jogo):

    edicao = EdicaoCampeonato.objects.get(id=jogo.edicaoCampeonato_id)
    campeonato = Campeonato.objects.get(id=edicao.campeonato_id)

    frases = [u"em disputa válida pela %s de %d",
              u"em desafio válido pela %s de %d",
              u"em partida válida pela %s de %d",
             ]

    return sorteia_frase(frases) % (campeonato.nome, edicao.ano)

#######################################################################################################################
# contexto factual > local
#######################################################################################################################
def get_frase_local(jogo):

    frases = [u"que teve como palco o estádio do %s",
              u"que aconteceu no estádio do %s",
              u"que rolou no estádio do %s",
              u"que teve como palco o estádio do %s",
              u"que aconteceu no estádio do %s",
              u"que rolou no estádio do %s",
            ]

    estadio = Estadio.objects.get(id=jogo.estadio_id)

    return (sorteia_frase(frases) % (estadio.nome)) + get_frase_local_cidade(estadio.cidade)

def get_frase_local_cidade(cidade):

    frases = [u" (%s)",
              u", em %s",
              u", localizado em %s",
            ]

    return sorteia_frase(frases) % (cidade)

#######################################################################################################################
# utils
#######################################################################################################################
# obtem uma das frases
def sorteia_frase(frases):
    return frases[ randint(0, len(frases) - 1) ]

# tratamento de genero
def get_equipe_genero(equipe):
    return equipe.nome_genero