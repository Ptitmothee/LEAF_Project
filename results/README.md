Results from the experiments after observation

2.2. Ce que je mettrais dans results/

Ici, je stockerais ce que le benchmark produit pendant ses expériences :

les réponses brutes des modèles ;
les solutions générées ;
les journaux des appels aux API ;
les temps de réponse et les nombres de tokens ;
les résultats de compilation et d'exécution ;
les mesures énergétiques ;
les résultats des tests ;
les erreurs rencontrées ;
les agrégations et les statistiques ;
les graphiques et les tableaux produits pour l'analyse.

Par exemple :

results/
├── experiments/
│   └── experiment_2026_001/
│       ├── manifest.json
│       ├── generations.jsonl
│       ├── execution_metrics.jsonl
│       └── energy_metrics.jsonl
│
├── analysis/
│   ├── success_rates.csv
│   └── energy_comparison.csv
│
└── figures/
    ├── energy_by_model.png
    └── success_rate_by_strategy.png