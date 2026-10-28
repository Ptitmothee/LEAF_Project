Initial data and resources to conduct the experiences

2.1. Ce que je mettrais dans data/

Dans ton projet, les données d'entrée pourraient inclure :

les problèmes de programmation récupérés depuis les datasets ;
les énoncés et les métadonnées des problèmes ;
les solutions de référence ;
les jeux de tests publics autorisés ;
les informations sur les langues et les contraintes d'exécution ;
les métadonnées des sources d'origine.

Par exemple :

data/
├── datasets/
│   ├── code_contest/
│   └── lcb/
│
├── problems/
│   ├── problem_0001.json
│   └── problem_0002.json
│
└── metadata/
    └── dataset_manifest.json