from . import education_bp
from flask import jsonify, request, render_template, session
from flask_login import login_required, current_user
from ...models import ContentItem
from ...security import premium_required


def _t(fr_text, en_text):
    return en_text if session.get('lang') == 'en' else fr_text


# ═══════════════════════════════════════════════════════════════
# DATA ANALYSE - COURS COMPLET
# ═══════════════════════════════════════════════════════════════

DATA_ANALYSE_LESSONS = [
    {
        'id': 1,
        'title': "Introduction à l'Analyse de Données",
        'title_en': "Introduction to Data Analysis",
        'duration': '45 min',
        'level': 'Débutant',
        'content': """
        <h3>Qu'est-ce que l'analyse de données ?</h3>
        <p>L'<strong>analyse de données</strong> est le processus d'inspection, de nettoyage, de transformation et de modélisation des données dans le but de découvrir des informations utiles, de tirer des conclusions et de soutenir la prise de décision.</p>
        
        <h4>Les 4 types d'analyse de données :</h4>
        <ol>
            <li><strong>Analyse descriptive</strong> : Que s'est-il passé ? (ex: rapports de ventes mensuels)</li>
            <li><strong>Analyse diagnostique</strong> : Pourquoi cela s'est-il passé ? (ex: chute des ventes en été)</li>
            <li><strong>Analyse prédictive</strong> : Que va-t-il se passer ? (ex: prévision des tendances)</li>
            <li><strong>Analyse prescriptive</strong> : Que devons-nous faire ? (ex: optimisation des stocks)</li>
        </ol>
        
        <h4>Le cycle de vie des données :</h4>
        <p>Tout projet data suit ces étapes :</p>
        <ul>
            <li>📥 <strong>Collecte</strong> : Acquisition des données brutes</li>
            <li>🧹 <strong>Nettoyage</strong> : Correction des erreurs, valeurs manquantes</li>
            <li>🔄 <strong>Transformation</strong> : Mise en forme pour l'analyse</li>
            <li>📊 <strong>Analyse</strong> : Application de méthodes statistiques</li>
            <li>📈 <strong>Visualisation</strong> : Création de graphiques compréhensibles</li>
            <li>💡 <strong>Interprétation</strong> : Conclusions et recommandations</li>
        </ul>
        
        <h4>Outils essentiels du Data Analyst :</h4>
        <table>
            <tr><th>Catégorie</th><th>Outils</th></tr>
            <tr><td>Tableurs</td><td>Excel, Google Sheets</td></tr>
            <tr><td>Langages</td><td>Python (Pandas, NumPy), R, SQL</td></tr>
            <tr><td>Visualisation</td><td>Tableau, Power BI, Matplotlib</td></tr>
            <tr><td>Bases de données</td><td>MySQL, PostgreSQL, MongoDB</td></tr>
        </table>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Un bon Data Analyst ne se contente pas de manipuler des chiffres – il raconte une histoire avec les données pour aider à la prise de décision.
        </div>
        """,
        'quiz': [
            {'q': "Quel type d'analyse répond à la question 'Que va-t-il se passer ?'", 'choices': ['Descriptive', 'Diagnostique', 'Prédictive', 'Prescriptive'], 'answer': 2},
            {'q': "Quelle est la première étape du cycle de vie des données ?", 'choices': ['Nettoyage', 'Collecte', 'Analyse', 'Visualisation'], 'answer': 1},
            {'q': "Quel outil est utilisé pour la visualisation de données ?", 'choices': ['SQL', 'Tableau', 'Python', 'MongoDB'], 'answer': 1},
        ]
    },
    {
        'id': 2,
        'title': "Nettoyage et Préparation des Données",
        'title_en': "Data Cleaning and Preparation",
        'duration': '60 min',
        'level': 'Intermédiaire',
        'content': """
        <h3>Pourquoi le nettoyage est crucial ?</h3>
        <p>On estime que <strong>80% du temps</strong> d'un Data Analyst est consacré au nettoyage des données. Des données sales mènent à des analyses erronées.</p>
        
        <h4>Les problèmes courants des données :</h4>
        <ul>
            <li>❌ <strong>Valeurs manquantes</strong> : Cellules vides ou NULL</li>
            <li>❌ <strong>Doublons</strong> : Enregistrements répétés</li>
            <li>❌ <strong>Incohérences</strong> : "France", "FRANCE", "Fr" pour le même pays</li>
            <li>❌ <strong>Outliers</strong> : Valeurs aberrantes (âge = 250 ans)</li>
            <li>❌ <strong>Types incorrects</strong> : Date stockée comme texte</li>
        </ul>
        
        <h4>Techniques de nettoyage :</h4>
        
        <h5>1. Gestion des valeurs manquantes</h5>
        <ul>
            <li><strong>Suppression</strong> : Si < 5% des données</li>
            <li><strong>Imputation par moyenne/médiane</strong> : Pour les variables numériques</li>
            <li><strong>Imputation par mode</strong> : Pour les catégories</li>
            <li><strong>Imputation avancée</strong> : KNN, régression</li>
        </ul>
        
        <h5>2. Détection des outliers</h5>
        <p>Méthodes statistiques :</p>
        <ul>
            <li><strong>Méthode IQR</strong> : Valeur < Q1 - 1.5×IQR ou > Q3 + 1.5×IQR</li>
            <li><strong>Z-Score</strong> : |z| > 3 indique un outlier</li>
        </ul>
        
        <h5>3. Standardisation des formats</h5>
        <pre><code># Exemple Python avec Pandas
df['date'] = pd.to_datetime(df['date'])
df['pays'] = df['pays'].str.upper().str.strip()
df['email'] = df['email'].str.lower()</code></pre>
        
        <h4>Bonnes pratiques :</h4>
        <ol>
            <li>✅ Toujours garder une copie des données originales</li>
            <li>✅ Documenter chaque transformation</li>
            <li>✅ Valider avec des statistiques descriptives</li>
            <li>✅ Créer des scripts reproductibles</li>
        </ol>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> "Garbage In, Garbage Out" – la qualité de votre analyse dépend directement de la qualité de vos données nettoyées.
        </div>
        """,
        'quiz': [
            {'q': "Quel pourcentage du temps d'un Data Analyst est consacré au nettoyage ?", 'choices': ['20%', '50%', '80%', '95%'], 'answer': 2},
            {'q': "Quelle technique utilise-t-on pour les valeurs manquantes numériques ?", 'choices': ['Suppression uniquement', 'Imputation par mode', 'Imputation par moyenne/médiane', 'Ignorer'], 'answer': 2},
            {'q': "Que signifie 'Garbage In, Garbage Out' ?", 'choices': ['Il faut recycler les données', 'Les données sales donnent des analyses erronées', 'Les outliers sont inutiles', 'Il faut supprimer toutes les données'], 'answer': 1},
        ]
    },
    {
        'id': 3,
        'title': "Statistiques Descriptives Essentielles",
        'title_en': "Essential Descriptive Statistics",
        'duration': '50 min',
        'level': 'Intermédiaire',
        'content': """
        <h3>Comprendre vos données avec les statistiques</h3>
        <p>Les statistiques descriptives résument et décrivent les caractéristiques principales d'un jeu de données.</p>
        
        <h4>Mesures de tendance centrale :</h4>
        <table>
            <tr><th>Mesure</th><th>Définition</th><th>Quand l'utiliser</th></tr>
            <tr><td><strong>Moyenne</strong></td><td>Somme / Nombre d'éléments</td><td>Données sans outliers</td></tr>
            <tr><td><strong>Médiane</strong></td><td>Valeur du milieu</td><td>Données avec outliers</td></tr>
            <tr><td><strong>Mode</strong></td><td>Valeur la plus fréquente</td><td>Données catégorielles</td></tr>
        </table>
        
        <h4>Mesures de dispersion :</h4>
        <ul>
            <li><strong>Étendue</strong> : Max - Min (sensible aux outliers)</li>
            <li><strong>Variance (σ²)</strong> : Moyenne des carrés des écarts à la moyenne</li>
            <li><strong>Écart-type (σ)</strong> : Racine carrée de la variance</li>
            <li><strong>IQR</strong> : Q3 - Q1 (robuste aux outliers)</li>
        </ul>
        
        <h4>Les quartiles expliqués :</h4>
        <p>Les quartiles divisent les données en 4 parties égales :</p>
        <ul>
            <li><strong>Q1 (25%)</strong> : 25% des données sont inférieures</li>
            <li><strong>Q2 (50%)</strong> : La médiane</li>
            <li><strong>Q3 (75%)</strong> : 75% des données sont inférieures</li>
        </ul>
        
        <h4>Exemple pratique :</h4>
        <pre><code>Salaires (en k€) : 25, 30, 32, 35, 38, 40, 42, 45, 120

Moyenne = 45.2 k€ (biaisée par 120k)
Médiane = 38 k€ (plus représentative)
Mode = Aucun (pas de répétition)
Écart-type = 28.4 k€</code></pre>
        
        <h4>Visualisations recommandées :</h4>
        <ul>
            <li>📊 <strong>Histogramme</strong> : Distribution des données</li>
            <li>📦 <strong>Boxplot</strong> : Quartiles et outliers</li>
            <li>📈 <strong>Courbe de densité</strong> : Forme de la distribution</li>
        </ul>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Toujours comparer moyenne et médiane. Si elles sont très différentes, vous avez probablement des outliers ou une distribution asymétrique.
        </div>
        """,
        'quiz': [
            {'q': "Quelle mesure est robuste aux outliers ?", 'choices': ['Moyenne', 'Médiane', 'Étendue', 'Variance'], 'answer': 1},
            {'q': "Que représente Q3 ?", 'choices': ['25% des données', '50% des données', '75% des données', '100% des données'], 'answer': 2},
            {'q': "Quel graphique montre les quartiles et outliers ?", 'choices': ['Histogramme', 'Camembert', 'Boxplot', 'Nuage de points'], 'answer': 2},
        ]
    },
    {
        'id': 4,
        'title': "Visualisation de Données avec Python",
        'title_en': "Data Visualization with Python",
        'duration': '75 min',
        'level': 'Avancé',
        'content': """
        <h3>L'art de raconter une histoire avec les données</h3>
        <p>Une bonne visualisation transforme des chiffres complexes en insights compréhensibles.</p>
        
        <h4>Les bibliothèques Python essentielles :</h4>
        <table>
            <tr><th>Bibliothèque</th><th>Usage</th><th>Points forts</th></tr>
            <tr><td><strong>Matplotlib</strong></td><td>Graphiques basiques</td><td>Contrôle total, personnalisation</td></tr>
            <tr><td><strong>Seaborn</strong></td><td>Statistiques</td><td>Esthétique, facile</td></tr>
            <tr><td><strong>Plotly</strong></td><td>Interactif</td><td>Zoom, survol, export</td></tr>
            <tr><td><strong>Altair</strong></td><td>Déclaratif</td><td>Syntaxe simple</td></tr>
        </table>
        
        <h4>Choisir le bon graphique :</h4>
        <ul>
            <li>📊 <strong>Barres</strong> : Comparaison de catégories</li>
            <li>📈 <strong>Ligne</strong> : Évolution temporelle</li>
            <li>🔵 <strong>Scatter plot</strong> : Corrélation entre 2 variables</li>
            <li>🥧 <strong>Camembert</strong> : Proportions (max 5-6 catégories)</li>
            <li>🔥 <strong>Heatmap</strong> : Corrélations multiples</li>
        </ul>
        
        <h4>Exemple de code :</h4>
        <pre><code>import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Charger les données
df = pd.read_csv('ventes.csv')

# Graphique en barres
plt.figure(figsize=(10, 6))
sns.barplot(x='mois', y='ventes', data=df, palette='viridis')
plt.title('Ventes Mensuelles 2025')
plt.xlabel('Mois')
plt.ylabel('Ventes (€)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('ventes_mensuelles.png', dpi=300)
plt.show()</code></pre>
        
        <h4>Les 5 règles d'or de la visualisation :</h4>
        <ol>
            <li>✅ <strong>Simplicité</strong> : Un message par graphique</li>
            <li>✅ <strong>Titre clair</strong> : Décrit le insight principal</li>
            <li>✅ <strong>Axes lisibles</strong> : Labels et unités visibles</li>
            <li>✅ <strong>Couleurs cohérentes</strong> : Palette harmonieuse</li>
            <li>✅ <strong>Pas de distorsion</strong> : Axes commençant à 0 (sauf exception)</li>
        </ol>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> "La meilleure visualisation est celle que votre audience comprend en moins de 5 secondes."
        </div>
        """,
        'quiz': [
            {'q': "Quelle bibliothèque Python est la plus adaptée aux graphiques interactifs ?", 'choices': ['Matplotlib', 'Seaborn', 'Plotly', 'NumPy'], 'answer': 2},
            {'q': "Quel graphique utiliser pour montrer une corrélation entre 2 variables ?", 'choices': ['Barres', 'Camembert', 'Scatter plot', 'Histogramme'], 'answer': 2},
            {'q': "Combien de temps votre audience devrait-elle mettre pour comprendre un bon graphique ?", 'choices': ['30 secondes', '5 secondes', '1 minute', '10 secondes'], 'answer': 1},
        ]
    }
]


MARKETING_DIGITAL_LESSONS = [
    {
        'id': 1,
        'title': "Fondamentaux du Marketing Digital",
        'title_en': "Digital Marketing Fundamentals",
        'duration': '50 min',
        'level': 'Débutant',
        'content': """
        <h3>Qu'est-ce que le Marketing Digital ?</h3>
        <p>Le marketing digital englobe toutes les actions marketing utilisant les canaux numériques pour promouvoir des produits, services ou marques.</p>
        
        <h4>Les piliers du marketing digital :</h4>
        <table>
            <tr><th>Pilier</th><th>Description</th><th>Exemples</th></tr>
            <tr><td><strong>SEO</strong></td><td>Optimisation pour les moteurs de recherche</td><td>Google, Bing</td></tr>
            <tr><td><strong>SEA</strong></td><td>Publicité payante sur moteurs</td><td>Google Ads</td></tr>
            <tr><td><strong>SMM</strong></td><td>Marketing sur réseaux sociaux</td><td>Facebook, Instagram, LinkedIn</td></tr>
            <tr><td><strong>Email Marketing</strong></td><td>Communication par email</td><td>Newsletters, automation</td></tr>
            <tr><td><strong>Content Marketing</strong></td><td>Création de contenu de valeur</td><td>Blog, vidéos, podcasts</td></tr>
        </table>
        
        <h4>Le funnel marketing (AIDA) :</h4>
        <ol>
            <li><strong>Attention</strong> : Capter l'intérêt (publicités, SEO)</li>
            <li><strong>Intérêt</strong> : Informer et engager (contenu)</li>
            <li><strong>Désir</strong> : Créer le besoin (témoignages, démos)</li>
            <li><strong>Action</strong> : Convertir (achat, inscription)</li>
        </ol>
        
        <h4>KPIs essentiels à suivre :</h4>
        <ul>
            <li>📈 <strong>Trafic</strong> : Nombre de visiteurs</li>
            <li>💰 <strong>Taux de conversion</strong> : Visiteurs → Clients</li>
            <li>📊 <strong>CTR (Click-Through Rate)</strong> : Clics / Impressions</li>
            <li>💵 <strong>CAC</strong> : Coût d'Acquisition Client</li>
            <li>🔄 <strong>LTV</strong> : Lifetime Value (valeur client)</li>
            <li>📉 <strong>Taux de rebond</strong> : % de visiteurs qui quittent immédiatement</li>
        </ul>
        
        <h4>Différence B2B vs B2C :</h4>
        <table>
            <tr><th>Critère</th><th>B2B</th><th>B2C</th></tr>
            <tr><td>Cycle de vente</td><td>Long (semaines/mois)</td><td>Court (minutes/jours)</td></tr>
            <tr><td>Décision</td><td>Rationnelle, ROI</td><td>Émotionnelle, impulsive</td></tr>
            <tr><td>Canaux clés</td><td>LinkedIn, Email</td><td>Instagram, TikTok</td></tr>
            <tr><td>Contenu</td><td>Éducatif, technique</td><td>Divertissant, inspirant</td></tr>
        </table>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Le marketing digital n'est pas de la magie – c'est de la data. Chaque action doit être mesurée et optimisée.
        </div>
        """,
        'quiz': [
            {'q': "Que signifie SEO ?", 'choices': ['Social Engine Optimization', 'Search Engine Optimization', 'Sales Email Outreach', 'Simple E-commerce Operation'], 'answer': 1},
            {'q': "Quelle est la première étape du funnel AIDA ?", 'choices': ['Action', 'Intérêt', 'Attention', 'Désir'], 'answer': 2},
            {'q': "Quel KPI mesure le coût pour acquérir un client ?", 'choices': ['LTV', 'CTR', 'CAC', 'ROI'], 'answer': 2},
        ]
    },
    {
        'id': 2,
        'title': "SEO : Référencement Naturel",
        'title_en': "SEO: Search Engine Optimization",
        'duration': '70 min',
        'level': 'Intermédiaire',
        'content': """
        <h3>Dominer les résultats Google gratuitement</h3>
        <p>Le <strong>SEO (Search Engine Optimization)</strong> est l'art d'optimiser un site web pour apparaître en haut des résultats de recherche organiques.</p>
        
        <h4>Les 3 piliers du SEO :</h4>
        
        <h5>1. SEO Technique</h5>
        <ul>
            <li>⚡ <strong>Vitesse de chargement</strong> : < 3 secondes</li>
            <li>📱 <strong>Mobile-first</strong> : Site responsive</li>
            <li>🔒 <strong>HTTPS</strong> : Certificat SSL obligatoire</li>
            <li>🗺️ <strong>Sitemap XML</strong> : Plan du site pour Google</li>
            <li>🤖 <strong>Robots.txt</strong> : Instructions pour les crawlers</li>
        </ul>
        
        <h5>2. SEO On-Page</h5>
        <ul>
            <li><strong>Balise Title</strong> : 50-60 caractères, mot-clé au début</li>
            <li><strong>Meta Description</strong> : 150-160 caractères, incitation au clic</li>
            <li><strong>URL</strong> : Courte, lisible, avec mot-clé</li>
            <li><strong>H1, H2, H3</strong> : Structure hiérarchique</li>
            <li><strong>Contenu</strong> : 1500+ mots, original, utile</li>
            <li><strong>Images</strong> : Alt text descriptif, compression</li>
        </ul>
        
        <h5>3. SEO Off-Page</h5>
        <ul>
            <li>🔗 <strong>Backlinks</strong> : Liens depuis d'autres sites (qualité > quantité)</li>
            <li>🏆 <strong>Domain Authority</strong> : Réputation du domaine</li>
            <li>📣 <strong>Mentions sociales</strong> : Partages et engagement</li>
        </ul>
        
        <h4>Comment trouver les bons mots-clés :</h4>
        <ol>
            <li><strong>Recherche de base</strong> : Google Suggest, "People Also Ask"</li>
            <li><strong>Outils gratuits</strong> : Ubersuggest, Answer The Public</li>
            <li><strong>Outils payants</strong> : SEMrush, Ahrefs, Moz</li>
            <li><strong>Critères de sélection</strong> : Volume de recherche, difficulté, intention</li>
        </ol>
        
        <h4>Types d'intention de recherche :</h4>
        <table>
            <tr><th>Type</th><th>Exemple</th><th>Contenu adapté</th></tr>
            <tr><td>Informationnelle</td><td>"Comment faire un gâteau"</td><td>Article de blog, tutoriel</td></tr>
            <tr><td>Navigationnelle</td><td>"Facebook login"</td><td>Page d'accueil</td></tr>
            <tr><td>Commerciale</td><td>"Meilleur smartphone 2026"</td><td>Comparatif, avis</td></tr>
            <tr><td>Transactionnelle</td><td>"Acheter iPhone 15"</td><td>Page produit</td></tr>
        </table>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Le SEO est un marathon, pas un sprint. Les résultats prennent 3-6 mois, mais le trafic est ensuite gratuit et durable.
        </div>
        """,
        'quiz': [
            {'q': "Quel est le temps de chargement maximum recommandé pour le SEO ?", 'choices': ['1 seconde', '3 secondes', '5 secondes', '10 secondes'], 'answer': 1},
            {'q': "Quelle longueur recommandée pour une balise Title ?", 'choices': ['20-30 caractères', '50-60 caractères', '100-120 caractères', '200 caractères'], 'answer': 1},
            {'q': "Qu'est-ce qu'un backlink ?", 'choices': ['Un lien interne', 'Un lien depuis un autre site', 'Un bouton retour', 'Une erreur 404'], 'answer': 1},
        ]
    },
    {
        'id': 3,
        'title': "Google Ads & Publicité Payante",
        'title_en': "Google Ads & Paid Advertising",
        'duration': '65 min',
        'level': 'Intermédiaire',
        'content': """
        <h3>Générer du trafic qualifié instantanément</h3>
        <p><strong>Google Ads</strong> (anciennement Google AdWords) permet d'afficher des annonces payantes dans les résultats de recherche et sur le réseau Display.</p>
        
        <h4>Types de campagnes Google Ads :</h4>
        <table>
            <tr><th>Type</th><th>Où</th><th>Objectif</th></tr>
            <tr><td><strong>Search</strong></td><td>Résultats Google</td><td>Conversion directe</td></tr>
            <tr><td><strong>Display</strong></td><td>Sites partenaires</td><td>Notoriété, retargeting</td></tr>
            <tr><td><strong>Shopping</strong></td><td>Onglet Shopping</td><td>E-commerce</td></tr>
            <tr><td><strong>Video</strong></td><td>YouTube</td><td>Branding, engagement</td></tr>
            <tr><td><strong>Performance Max</strong></td><td>Tous canaux</td><td>Automatisation IA</td></tr>
        </table>
        
        <h4>Structure d'un compte Google Ads :</h4>
        <pre>Compte
├── Campagne 1 (budget, géo, stratégie d'enchères)
│   ├── Groupe d'annonces A (mots-clés similaires)
│   │   ├── Annonce 1
│   │   ├── Annonce 2
│   │   └── Mots-clés
│   └── Groupe d'annonces B
└── Campagne 2</pre>
        
        <h4>Le Quality Score (1-10) :</h4>
        <p>Google note vos annonces sur 3 critères :</p>
        <ol>
            <li><strong>CTR attendu</strong> : Probabilité de clic</li>
            <li><strong>Pertinence de l'annonce</strong> : Correspondance mot-clé / annonce</li>
            <li><strong>Expérience page de destination</strong> : Qualité de la landing page</li>
        </ol>
        <p>Un Quality Score élevé = <strong>coût par clic (CPC) réduit</strong> et <strong>meilleure position</strong>.</p>
        
        <h4>Rédiger une annonce efficace :</h4>
        <ul>
            <li>✅ Inclure le mot-clé principal dans le titre</li>
            <li>✅ Utiliser des chiffres ("+50% de ventes")</li>
            <li>✅ Ajouter un appel à l'action clair ("Essai gratuit")</li>
            <li>✅ Exploiter les extensions (sitelinks, prix, avis)</li>
        </ul>
        
        <h4>Stratégies d'enchères :</h4>
        <ul>
            <li><strong>CPC manuel</strong> : Contrôle total (pour débutants)</li>
            <li><strong>Maximiser les clics</strong> : Volume de trafic</li>
            <li><strong>CPA cible</strong> : Coût par acquisition fixe</li>
            <li><strong>ROAS cible</strong> : Retour sur dépense publicitaire</li>
        </ul>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Commencez avec un petit budget (10-20€/jour), testez plusieurs annonces (A/B testing), et optimisez en fonction des conversions, pas des clics.
        </div>
        """,
        'quiz': [
            {'q': "Quel type de campagne est idéal pour l'e-commerce ?", 'choices': ['Search', 'Display', 'Shopping', 'Video'], 'answer': 2},
            {'q': "Quels sont les 3 critères du Quality Score ?", 'choices': ['Budget, clics, impressions', 'CTR, pertinence, landing page', 'Position, CPC, conversions', 'Titre, description, URL'], 'answer': 1},
            {'q': "Quelle stratégie d'enchères vise un coût par acquisition fixe ?", 'choices': ['CPC manuel', 'Maximiser les clics', 'CPA cible', 'Maximiser les impressions'], 'answer': 2},
        ]
    },
    {
        'id': 4,
        'title': "Social Media Marketing",
        'title_en': "Social Media Marketing",
        'duration': '60 min',
        'level': 'Intermédiaire',
        'content': """
        <h3>Maîtriser les réseaux sociaux pour votre business</h3>
        <p>Les réseaux sociaux représentent <strong>4.9 milliards d'utilisateurs</strong> dans le monde. Chaque plateforme a ses codes et son audience.</p>
        
        <h4>Comparatif des plateformes :</h4>
        <table>
            <tr><th>Plateforme</th><th>Audience</th><th>Format star</th><th>Idéal pour</th></tr>
            <tr><td><strong>Instagram</strong></td><td>18-34 ans</td><td>Reels, Stories</td><td>Lifestyle, mode, food</td></tr>
            <tr><td><strong>TikTok</strong></td><td>16-24 ans</td><td>Vidéos courtes</td><td>Divertissement, tendances</td></tr>
            <tr><td><strong>LinkedIn</strong></td><td>Professionnels</td><td>Articles, posts texte</td><td>B2B, recrutement</td></tr>
            <tr><td><strong>Facebook</strong></td><td>35+ ans</td><td>Groupes, vidéos</td><td>Communautés locales</td></tr>
            <tr><td><strong>Twitter/X</strong></td><td>Tous âges</td><td>Threads, actualités</td><td>News, tech, politique</td></tr>
            <tr><td><strong>YouTube</strong></td><td>Tous âges</td><td>Vidéos longues</td><td>Tutoriels, éducation</td></tr>
        </table>
        
        <h4>La règle du 80/20 :</h4>
        <ul>
            <li><strong>80% de contenu de valeur</strong> : Éducatif, divertissant, inspirant</li>
            <li><strong>20% de contenu promotionnel</strong> : Produits, offres, CTA</li>
        </ul>
        
        <h4>Types de contenu qui performent :</h4>
        <ol>
            <li>🎬 <strong>Vidéos courtes</strong> : +50% d'engagement vs images</li>
            <li>📖 <strong>Carrousels</strong> : Swipe = temps passé = algorithme content</li>
            <li>💬 <strong>UGC (User Generated Content)</strong> : Authentique et gratuit</li>
            <li>🎭 <strong>Behind-the-scenes</strong> : Humanise la marque</li>
            <li>📊 <strong>Infographies</strong> : Partageables et enregistrables</li>
        </ol>
        
        <h4>Algorithme : ce qui compte</h4>
        <ul>
            <li>⏰ <strong>Engagement rapide</strong> : Interactions dans les 30 premières minutes</li>
            <li>💾 <strong>Saves & Shares</strong> : Plus valorisés que les likes</li>
            <li>⏱️ <strong>Temps passé</strong> : Vidéos regardées jusqu'au bout</li>
            <li>💬 <strong>Commentaires</strong> : Répondre = doubler la visibilité</li>
        </ul>
        
        <h4>Calendrier de publication :</h4>
        <table>
            <tr><th>Plateforme</th><th>Fréquence idéale</th><th>Meilleurs horaires</th></tr>
            <tr><td>Instagram</td><td>1-2 posts/jour</td><td>8h, 12h, 18h</td></tr>
            <tr><td>TikTok</td><td>1-3 vidéos/jour</td><td>7h, 12h, 19h</td></tr>
            <tr><td>LinkedIn</td><td>3-5 posts/semaine</td><td>8h-10h (mardi-jeudi)</td></tr>
        </table>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Ne soyez pas partout – choisissez 2-3 plateformes où votre audience est présente et excellez dessus.
        </div>
        """,
        'quiz': [
            {'q': "Quelle plateforme est idéale pour le B2B ?", 'choices': ['TikTok', 'Instagram', 'LinkedIn', 'Snapchat'], 'answer': 2},
            {'q': "Selon la règle 80/20, quel pourcentage de contenu doit être promotionnel ?", 'choices': ['80%', '50%', '20%', '10%'], 'answer': 2},
            {'q': "Quelles interactions sont les plus valorisées par les algorithmes ?", 'choices': ['Likes', 'Saves et Shares', 'Vues', 'Impressions'], 'answer': 1},
        ]
    },
    {
        'id': 5,
        'title': "Analytics & Mesure de Performance",
        'title_en': "Analytics & Performance Measurement",
        'duration': '55 min',
        'level': 'Avancé',
        'content': """
        <h3>Ce qui ne se mesure pas ne s'améliore pas</h3>
        <p><strong>Google Analytics 4 (GA4)</strong> est l'outil incontournable pour comprendre le comportement des visiteurs de votre site.</p>
        
        <h4>Métriques clés à surveiller :</h4>
        <table>
            <tr><th>Métrique</th><th>Définition</th><th>Bonne valeur</th></tr>
            <tr><td><strong>Sessions</strong></td><td>Nombre de visites</td><td>↗️ Croissance constante</td></tr>
            <tr><td><strong>Utilisateurs</strong></td><td>Visiteurs uniques</td><td>Dépend du secteur</td></tr>
            <tr><td><strong>Taux de rebond</strong></td><td>% qui quitte sans action</td><td>< 50% (contenu), < 30% (e-commerce)</td></tr>
            <tr><td><strong>Durée moyenne</strong></td><td>Temps sur le site</td><td>> 2 minutes</td></tr>
            <tr><td><strong>Pages/session</strong></td><td>Nombre de pages vues</td><td>> 2 pages</td></tr>
            <tr><td><strong>Taux de conversion</strong></td><td>Visiteurs → Actions</td><td>2-5% (e-commerce)</td></tr>
        </table>
        
        <h4>Sources de trafic :</h4>
        <ul>
            <li>🔍 <strong>Organic Search</strong> : Depuis Google (SEO)</li>
            <li>💰 <strong>Paid Search</strong> : Publicités Google Ads</li>
            <li>📱 <strong>Social</strong> : Réseaux sociaux</li>
            <li>🔗 <strong>Referral</strong> : Liens depuis d'autres sites</li>
            <li>✉️ <strong>Email</strong> : Campagnes email</li>
            <li>🔄 <strong>Direct</strong> : URL tapée directement</li>
        </ul>
        
        <h4>Configurer les conversions (GA4) :</h4>
        <ol>
            <li>Définir vos <strong>événements clés</strong> (achat, inscription, téléchargement)</li>
            <li>Marquer ces événements comme <strong>conversions</strong></li>
            <li>Attribuer une <strong>valeur monétaire</strong> si possible</li>
            <li>Créer des <strong>entonnoirs</strong> pour visualiser le parcours</li>
        </ol>
        
        <h4>UTM Parameters :</h4>
        <p>Pour tracker précisément vos campagnes, ajoutez des paramètres UTM à vos URLs :</p>
        <pre><code>https://monsite.com/page?
  utm_source=facebook
  &utm_medium=cpc
  &utm_campaign=soldes_ete_2026
  &utm_content=banner_rouge</code></pre>
        
        <h4>Tableau de bord idéal :</h4>
        <p>Créez un dashboard avec ces 5 widgets essentiels :</p>
        <ol>
            <li>📈 Trafic par jour (courbe)</li>
            <li>🌍 Sources de trafic (camembert)</li>
            <li>📱 Répartition desktop/mobile (barres)</li>
            <li>🎯 Taux de conversion (jauge)</li>
            <li>💰 Revenu par source (tableau)</li>
        </ol>
        
        <div class="lesson-tip">
            <strong>💡 À retenir :</strong> Ne vous noyez pas dans les données. Identifiez 3-5 KPIs alignés avec vos objectifs business et suivez-les religieusement.
        </div>
        """,
        'quiz': [
            {'q': "Quel taux de rebond est considéré bon pour un e-commerce ?", 'choices': ['< 30%', '< 50%', '< 70%', '< 90%'], 'answer': 0},
            {'q': "Que représente la source 'Organic Search' ?", 'choices': ['Publicités payantes', 'Trafic depuis Google (gratuit)', 'Réseaux sociaux', 'Emails'], 'answer': 1},
            {'q': "À quoi servent les paramètres UTM ?", 'choices': ['Améliorer le SEO', 'Tracker les campagnes marketing', 'Accélérer le site', 'Sécuriser les URLs'], 'answer': 1},
        ]
    }
]


@education_bp.route('/data-analyse')
@premium_required
def data_analyse():
    """Page du cours Data Analyse"""
    return render_template('education_data_analyse.html', lessons=DATA_ANALYSE_LESSONS)


@education_bp.route('/data-analyse/lesson/<int:lesson_id>')
@premium_required
def data_analyse_lesson(lesson_id):
    """Afficher une leçon spécifique de Data Analyse"""
    lesson = next((l for l in DATA_ANALYSE_LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    return render_template('education_lesson_detail.html', lesson=lesson, course='data-analyse', total_lessons=len(DATA_ANALYSE_LESSONS))


@education_bp.route('/marketing-digital')
@premium_required
def marketing_digital():
    """Page du cours Marketing Digital"""
    return render_template('education_marketing_digital.html', lessons=MARKETING_DIGITAL_LESSONS)


@education_bp.route('/marketing-digital/lesson/<int:lesson_id>')
@premium_required
def marketing_digital_lesson(lesson_id):
    """Afficher une leçon spécifique de Marketing Digital"""
    lesson = next((l for l in MARKETING_DIGITAL_LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    return render_template('education_lesson_detail.html', lesson=lesson, course='marketing-digital', total_lessons=len(MARKETING_DIGITAL_LESSONS))


@education_bp.route('/quiz/<course>/<int:lesson_id>')
@premium_required
def course_quiz(course, lesson_id):
    """Afficher le quiz d'une leçon"""
    if course == 'data-analyse':
        lessons = DATA_ANALYSE_LESSONS
    elif course == 'marketing-digital':
        lessons = MARKETING_DIGITAL_LESSONS
    else:
        return jsonify({'error': 'Course not found'}), 404
    
    lesson = next((l for l in lessons if l['id'] == lesson_id), None)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    return render_template('education_quiz.html', lesson=lesson, course=course)


@education_bp.route('/quiz/<course>/<int:lesson_id>/submit', methods=['POST'])
@premium_required
def submit_quiz(course, lesson_id):
    """Soumettre les réponses du quiz"""
    if course == 'data-analyse':
        lessons = DATA_ANALYSE_LESSONS
    elif course == 'marketing-digital':
        lessons = MARKETING_DIGITAL_LESSONS
    else:
        return jsonify({'error': 'Course not found'}), 404
    
    lesson = next((l for l in lessons if l['id'] == lesson_id), None)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    data = request.get_json() or request.form
    answers = data.get('answers', [])
    
    # Calculate score
    correct = 0
    total = len(lesson['quiz'])
    results = []
    
    for i, q in enumerate(lesson['quiz']):
        user_answer = int(answers[i]) if i < len(answers) else -1
        is_correct = user_answer == q['answer']
        if is_correct:
            correct += 1
        results.append({
            'question': q['q'],
            'user_answer': user_answer,
            'correct_answer': q['answer'],
            'is_correct': is_correct,
            'choices': q['choices']
        })
    
    score = (correct / total) * 100 if total > 0 else 0
    
    # Save progress
    if current_user.is_authenticated:
        current_user.update_progress(course, f'lesson_{lesson_id}', int(score))
    
    return jsonify({
        'score': score,
        'correct': correct,
        'total': total,
        'results': results,
        'passed': score >= 70
    })


@education_bp.route('/rate/<course>/<int:lesson_id>', methods=['POST'])
@premium_required
def rate_lesson(course, lesson_id):
    """Noter une leçon"""
    data = request.get_json() or {}
    rating = int(data.get('rating', 0))
    comment = data.get('comment', '')
    
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # In production, save to database
    return jsonify({
        'success': True,
        'message': _t('Merci pour votre évaluation !', 'Thank you for your rating!'),
        'rating': rating
    })


@education_bp.route('/quiz/<int:quiz_id>')
@premium_required
def quiz(quiz_id):
    # Placeholder: return a simple quiz payload
    sample = {
        'id': quiz_id,
        'title': 'Quiz exemple',
        'questions': [
            {'q': '2+2=?', 'choices': ['3', '4', '5'], 'answer': 1}
        ]
    }
    return jsonify(sample)


@education_bp.route('/progress', methods=['POST'])
@premium_required
def save_progress():
    data = request.get_json() or {}
    # Add user_id to track progress per user
    data['user_id'] = current_user.id
    # Save progress logic would go here
    return jsonify({'saved': True, 'user_id': current_user.id, 'data': data})


@education_bp.route('/lessons')
def lessons():
    """Page catalogue de toutes les leçons (accès libre)"""
    return render_template('education_lessons.html')


@education_bp.route('/')
def program():
    # Render the education program overview page (free preview)
    return render_template('education_program.html')
