# -*- coding: utf-8 -*-
import datetime
from django.utils import timezone
from django.db import models
from esportes.models import Estadio, Campeonato, EdicaoCampeonato, Equipe, Jogo

class News(models.Model):
    titulo = models.CharField(max_length=255)

    jogo = models.ForeignKey(Jogo)
    content = models.TextField()

    class Meta:
        verbose_name = "resenha esportiva"
        verbose_name_plural= u'Resenha esportiva'
