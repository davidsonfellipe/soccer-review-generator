# -*- coding: utf-8 -*-
from esportes.models import Estadio, Campeonato, EdicaoCampeonato, Equipe, Jogo, Jogador, Gol
from django.contrib import admin
from django import forms

class EstadioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade')

    fieldsets = [
        (None, {'fields': ['nome']}),
        (None, {'fields': ['capacidade']}),
        (None, {'fields': ['cidade']}),
    ]

class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id')

class EdicaoCampeonatoAdmin(admin.ModelAdmin):
    list_display = ('campeonato', 'ano')

class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'apelido', 'sigla', 'gentilico')

class GolInline(admin.TabularInline):
    model = Jogo.gols.through

class GolAdmin(admin.ModelAdmin):
    inlines = [
        GolInline,
    ]
    # exclude = ('jogos',)

class JogoAdmin(admin.ModelAdmin):
    list_display = ('mandante', 'visitante')

    video = forms.CharField(required=True)

    inlines = [
        GolInline,
    ]

    exclude = ('gols', )

class JogadorAdmin(admin.ModelAdmin):
    list_display = ('nome', "equipe")

    fieldsets = [
        (None, {'fields': ['nome']}),
        (None, {'fields': ['equipe']}),
    ]

admin.site.register(Estadio, EstadioAdmin)
admin.site.register(Campeonato, CampeonatoAdmin)
admin.site.register(EdicaoCampeonato, EdicaoCampeonatoAdmin)
admin.site.register(Equipe, EquipeAdmin)
admin.site.register(Jogo, JogoAdmin)
admin.site.register(Gol, GolAdmin)
admin.site.register(Jogador, JogadorAdmin)