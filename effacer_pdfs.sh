#!/bin/bash

# Supprimer tous les fichiers .pdf modifiés il y a plus de 30 jours
find "/data/copie_windows/version Windows alix02/Desktop/ALIX_APP_DEV/static" -name "*.pdf" -type f -mtime +30 -exec rm {} \;
