# -*- coding: utf-8 -*-
from django.db import models

class Estadio(models.Model):
    nome = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    capacidade = models.IntegerField(max_length=255)

    class Meta:
        verbose_name_plural= u'Estádios'

    def __unicode__(self):
        return self.nome

class Campeonato(models.Model):
    nome = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nome

class EdicaoCampeonato(models.Model):
    campeonato = models.ForeignKey(Campeonato)
    ano = models.IntegerField()

    class Meta:
        verbose_name_plural= u'Edições de Campeonato'

    def __unicode__(self):
        return self.campeonato.nome + " / " + str(self.ano)

class Equipe(models.Model):
    nome = models.CharField(max_length=255)
    nome_genero = models.CharField(max_length=1)
    apelido = models.CharField(max_length=255)
    sigla = models.CharField(max_length=3)
    gentilico = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nome

class Jogador(models.Model):
    nome = models.CharField(max_length=255)
    equipe = models.ForeignKey(Equipe, null=True, related_name='equipe')

    class Meta:
        verbose_name_plural= u'Jogadores'

    def __unicode__(self):
        return self.nome

class Gol(models.Model):
    equipe = models.ForeignKey(Equipe, null=True)
    jogador = models.ForeignKey(Jogador, null=True)
    momento = models.IntegerField()

    TIPOS_TEMPO = (
        ('1N', '1º tempo'),
        ('2N', '2º tempo'),
        ('1P', '1º tempo da prorrogação'),
        ('2P', '2º tempo da prorrogação'),
        ('PE', 'Pênaltis'),
    )
    tempo = models.CharField(max_length=2, choices=TIPOS_TEMPO)

    def __unicode__(self):
        return u"[%s] %s - %s' (%sº tempo)" % (self.equipe.sigla, self.jogador.nome, self.momento, self.tempo)

class Jogo(models.Model):
    mandante = models.ForeignKey(Equipe, null=True, related_name='mandante')
    visitante = models.ForeignKey(Equipe, null=True, related_name='visitante')
    estadio = models.ForeignKey(Estadio)
    edicaoCampeonato = models.ForeignKey(EdicaoCampeonato)
    data = models.DateField()
    gols = models.ManyToManyField(Gol, related_name='gols')
    hora = models.TimeField()
    video = models.CharField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return self.mandante.nome + " x " + self.visitante.nome + " | " + self.edicaoCampeonato.campeonato.nome  + " " + str(self.edicaoCampeonato.ano)