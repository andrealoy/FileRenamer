### Workflow quotidien
### Étape 1 – Se mettre à jour

Avant de commencer à travailler :

```
git checkout dev
git pull origin dev
```

### Étape 2 – Travailler sur ta partie

Andrea → dossiers core (logique, classes, exécution)

Colline → dossier ui (interface Streamlit, intégration des actions)

Fais tes modifications, puis sauvegarde :
```
git add .
git commit -m "update UI"   # ou "improve backend"
```

### Étape 3 – Synchroniser avec la branche commune

Avant de pousser :
```
git pull origin dev   # récupère les changements de l’autre
git push origin dev   # envoie tes changements
```

### Important : toujours pull avant push pour éviter les conflits.

### Étape 4 – Fusionner vers main

Quand tout fonctionne bien et qu’une version est prête :
```
git checkout main
git pull origin main
git merge dev
git push origin main
```

main devient alors la version “stable”.

### Utilisation de playground

Sert à tester du code, des fonctions ou des idées sans impacter dev

Tu peux y créer un fichier temporaire (test_playground.py, etc.)

Rien d’important ne doit y rester longtemps

Pour aller dessus: 
```
git checkout playground 
```

### Bonnes pratiques

Ne jamais travailler directement sur main

Toujours commenter clairement les commits

Avant un push, vérifie que ton code s’exécute sans erreur

Si tu modifies une fonction utilisée par l’autre personne → préviens-la !

Si tu crées un nouveau fichier, ajoute une docstring en haut avec ton nom et le but du script