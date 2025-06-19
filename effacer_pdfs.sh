#!/bin/bash

# Supprimer tous les fichiers .pdf modifiés il y a plus de 30 jours
find "/srv/HOSPITALIX/static" -name "*.pdf" -type f -mtime +30 -exec rm {} \;
