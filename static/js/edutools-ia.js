/**
 * EduTools-IA - Le co-pilote intelligent omniprésent
 * 3 super-pouvoirs : Dashboard Progression, Sandbox Code, Prompt-to-Report
 */

class EdutoolsIA {
  constructor() {
    console.log('🤖 EdutoolsIA initializing...');
    this.isOpen = false;
    this.currentMode = null;
    this.currentPage = this.detectCurrentPage();
    console.log('📍 Current page detected:', this.currentPage);
    this.setupButton();
    console.log('✅ Button setup');
    this.initModal();
    console.log('✅ Modal initialized');
  }

  /**
   * Détecte la page actuelle via l'URL
   */
  detectCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('/modules/education')) return 'education';
    if (path.includes('/modules/saas')) return 'saas';
    if (path.includes('/modules/automation')) return 'automation';
    if (path.includes('/dashboard')) return 'dashboard';
    if (path.includes('/technologie')) return 'technologie';
    return 'home';
  }

  /**
   * Configure le bouton flottant créé en HTML
   */
  setupButton() {
    console.log('🎨 Setting up button listeners...');
    const button = document.getElementById('edutools-ia-button');
    console.log('🔍 Found button element:', button);
    
    if (!button) {
      console.error('❌ Button element not found in DOM!');
      return;
    }
    
    const btnElement = button.querySelector('.ia-button');
    console.log('🔍 Found button inner:', btnElement);
    
    if (btnElement) {
      btnElement.addEventListener('click', () => {
        console.log('🖱️ Button clicked!');
        this.toggleModal();
      });
      console.log('✅ Click listener added to button');
    } else {
      console.error('❌ Could not find .ia-button element!');
    }
  }

  /**
   * Crée la modale principale avec les 3 modes
   */
  initModal() {
    const modal = document.createElement('div');
    modal.id = 'edutools-ia-modal';
    modal.className = 'ia-modal ia-hidden';
    modal.innerHTML = `
      <div class="ia-modal-content">
        <!-- Header avec menu -->
        <div class="ia-header">
          <div class="ia-title">
            <span class="ia-icon">🤖</span>
            <h2>EduTools-IA</h2>
          </div>
          <button class="ia-close">&times;</button>
        </div>

        <!-- Détection de contexte -->
        <div class="ia-context-banner" id="contextBanner"></div>

        <!-- Menu principal (3 pouvoirs) -->
        <div class="ia-menu" id="mainMenu">
          <button class="ia-power-btn" data-power="progression">
            <span class="icon">📊</span>
            <div>
              <strong>Dashboard Progression</strong>
              <small>Suivi des quiz, déblocage SaaS</small>
            </div>
          </button>
          <button class="ia-power-btn" data-power="sandbox">
            <span class="icon">💻</span>
            <div>
              <strong>Bac à Sable Créatif</strong>
              <small>Générer HTML, CSS, JS, Python...</small>
            </div>
          </button>
          <button class="ia-power-btn" data-power="report">
            <span class="icon">📈</span>
            <div>
              <strong>Générateur Prompt-to-Report</strong>
              <small>Analyse de données → PDF</small>
            </div>
          </button>
        </div>

        <!-- Contenu dynamique -->
        <div class="ia-content" id="iaContent"></div>
      </div>
    `;
    document.body.appendChild(modal);

    // Event listeners
    modal.querySelector('.ia-close').addEventListener('click', () => this.toggleModal());
    modal.querySelectorAll('.ia-power-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const power = e.currentTarget.dataset.power;
        this.switchMode(power);
      });
    });

    // Fermer avec Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) this.toggleModal();
    });
  }

  /**
   * Bascule la modale
   */
  toggleModal() {
    this.isOpen = !this.isOpen;
    const modal = document.getElementById('edutools-ia-modal');
    if (this.isOpen) {
      modal.classList.remove('ia-hidden');
      this.updateContextBanner();
    } else {
      modal.classList.add('ia-hidden');
    }
  }

  /**
   * Met à jour la bannière de contexte
   */
  updateContextBanner() {
    const banner = document.getElementById('contextBanner');
    const messages = {
      education: '📚 Vous êtes en mode Éducation. Besoin de suivre vos progrès ?',
      saas: '🚀 Mode SaaS actif. Créez des rapports ou convertissez des devises !',
      automation: '⚙️ Mode Automatisation. Générez du code prêt à utiliser !',
      dashboard: '📊 Dashboard ouvert. Analysez vos statistiques !',
      technologie: '💡 Cours Technologie actif. Testez votre code en sandbox !',
      home: '👋 Bienvenue ! Explorez nos 3 piliers : Éducation, SaaS, Automatisation.'
    };
    banner.textContent = messages[this.currentPage] || messages.home;
  }

  /**
   * Change de mode (Pouvoir)
   */
  switchMode(power) {
    this.currentMode = power;
    const content = document.getElementById('iaContent');
    
    document.querySelectorAll('.ia-power-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.power === power);
    });

    switch(power) {
      case 'progression':
        this.renderProgressionDashboard(content);
        break;
      case 'sandbox':
        this.renderSandbox(content);
        break;
      case 'report':
        this.renderReportGenerator(content);
        break;
    }
  }

  /**
   * POUVOIR #1 : Dashboard de Progression
   */
  renderProgressionDashboard(container) {
    container.innerHTML = `
      <div class="ia-panel">
        <h3>🎯 Votre Progression</h3>
        
        <div class="progress-section">
          <div class="stat-block">
            <div class="stat-label">Quiz Complétés</div>
            <div class="stat-value" id="quizCount">0</div>
            <div class="stat-bar">
              <div class="progress-fill" id="quizProgress" style="width: 0%"></div>
            </div>
          </div>

          <div class="stat-block">
            <div class="stat-label">Outils SaaS Débloqués</div>
            <div class="stat-value" id="toolsCount">3</div>
            <div class="stat-bar">
              <div class="progress-fill" style="width: 60%"></div>
            </div>
          </div>

          <div class="stat-block">
            <div class="stat-label">Score Moyen</div>
            <div class="stat-value" id="avgScore">--</div>
            <div class="stat-bar">
              <div class="progress-fill" id="scoreProgress" style="width: 0%"></div>
            </div>
          </div>
        </div>

        <hr class="ia-divider">

        <h4>💡 Recommandation Personnalisée</h4>
        <div class="recommendation-box" id="recommendation">
          <p>Chargement de vos données...</p>
        </div>

        <button class="ia-action-btn" onclick="window.location.href='/dashboard'">
          📊 Ouvrir Dashboard Complet
        </button>
      </div>
    `;

    // Charger les données de progression (simulées pour demo)
    this.loadProgressionData();
  }

  /**
   * Charge et affiche les données de progression
   */
  loadProgressionData() {
    // Simulation - à remplacer par un appel API réel
    const mockData = {
      quizzes: 7,
      score: 82,
      tools: 3,
      lastActivity: 'Quiz Machine Learning'
    };

    document.getElementById('quizCount').textContent = mockData.quizzes;
    document.getElementById('quizProgress').style.width = (mockData.quizzes * 10) + '%';
    document.getElementById('avgScore').textContent = mockData.score + '%';
    document.getElementById('scoreProgress').style.width = mockData.score + '%';

    // Recommandation intelligente
    const recommendation = document.getElementById('recommendation');
    if (mockData.score < 60) {
      recommendation.innerHTML = `
        <p><strong>⚠️ Progression lente</strong><br>
        Je vous recommande si vous avez un peu de temps :</p>
        <a href="/modules/education/lessons" class="rec-link">
          📚 Revoir "Machine Learning"
        </a>
      `;
    } else if (mockData.score > 80) {
      recommendation.innerHTML = `
        <p><strong>🎉 Excellent travail !</strong><br>
        Vous avez débloqué un nouvel outil :</p>
        <div class="new-tool">
          <strong>🌍 Convertisseur de Devise</strong> (SaaS)
          <br><small>Convertissez instantanément entre 200+ devises</small>
          <a href="/modules/saas" class="rec-link">Découvrir</a>
        </div>
      `;
    } else {
      recommendation.innerHTML = `
        <p><strong>📈 Vous progressez bien !</strong><br>
        Je vous recommande le cours :</p>
        <a href="/modules/technologie/" class="rec-link">
          🚀 Avancer en Technologie
        </a>
      `;
    }
  }

  /**
   * POUVOIR #2 : Bac à Sable (Code Generator)
   */
  renderSandbox(container) {
    container.innerHTML = `
      <div class="ia-panel">
        <h3>💻 Bac à Sable Créatif</h3>
        
        <div class="sandbox-section">
          <label>Qu'est-ce que vous voulez créer ?</label>
          <textarea id="sandboxPrompt" placeholder="Ex: Un formulaire de contact coloré en bleu avec animation au survol..." rows="3"></textarea>
          
          <div class="language-selector">
            <label>Langage :</label>
            <select id="codeLanguage">
              <option value="html+css+js">HTML + CSS + JavaScript</option>
              <option value="python">Python</option>
              <option value="javascript">JavaScript pur</option>
              <option value="cpp">C++</option>
              <option value="css">CSS Avancé</option>
            </select>
          </div>

          <button class="ia-action-btn" onclick="edutoolsIA.generateCode()">
            ✨ Générer le Code
          </button>
        </div>

        <div id="sandboxOutput" class="sandbox-output ia-hidden">
          <h4 class="output-title">Code Généré :</h4>
          <pre id="generatedCode"></pre>
          <button class="copy-btn" onclick="edutoolsIA.copyToClipboard()">📋 Copier le Code</button>
          <button class="copy-btn secondary" onclick="edutoolsIA.openInEditor()">🖊️ Ouvrir dans Éditeur</button>
        </div>
      </div>
    `;
  }

  /**
   * Génère du code basé sur le prompt utilisateur
   */
  generateCode() {
    const prompt = document.getElementById('sandboxPrompt').value;
    const language = document.getElementById('codeLanguage').value;

    if (!prompt.trim()) {
      alert('Décrivez ce que vous voulez créer !');
      return;
    }

    // Template de code selon le langage (simplifié pour la démo)
    const codeTemplates = {
      'html+css+js': this.generateWebCode(prompt),
      'python': this.generatePythonCode(prompt),
      'javascript': this.generateJSCode(prompt),
      'cpp': this.generateCppCode(prompt),
      'css': this.generateCSSCode(prompt)
    };

    const code = codeTemplates[language] || 'Code non disponible';
    document.getElementById('generatedCode').textContent = code;
    document.getElementById('sandboxOutput').classList.remove('ia-hidden');
    
    // Message de confirmation
    console.log(`✨ Code ${language} généré pour : "${prompt}"`);
  }

  generateWebCode() {
    return `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ma Création</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .container {
      background: white;
      padding: 40px;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      max-width: 500px;
      width: 90%;
    }
    h1 { color: #333; margin-bottom: 20px; text-align: center; }
    input, textarea { 
      width: 100%;
      padding: 12px;
      margin: 10px 0;
      border: 2px solid #ddd;
      border-radius: 8px;
      font-size: 14px;
    }
    button {
      width: 100%;
      padding: 12px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
  </style>
</head>
<body>
  <div class="container">
    <h1>✨ Bienvenue !</h1>
    <input type="text" placeholder="Votre nom...">
    <textarea placeholder="Votre message..."></textarea>
    <button>Envoyer</button>
  </div>
</body>
</html>`;
  }

  generatePythonCode() {
    return `# Code Python généré par EduTools-IA

def main():
    """Fonction principale"""
    print("🐍 Bienvenue dans Python !")
    
    # Exemple simple
    liste = [1, 2, 3, 4, 5]
    result = sum(liste)
    print(f"Somme: {result}")
    
    # Boucle
    for item in liste:
        print(f"  - {item}")

if __name__ == "__main__":
    main()`;
  }

  generateJSCode() {
    return `// JavaScript pur - EduTools-IA

const app = {
  init() {
    this.setupListeners();
    console.log('✨ App initialisée !');
  },
  
  setupListeners() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-action]')) {
        const action = e.target.dataset.action;
        console.log(\`Action: \${action}\`);
      }
    });
  },
  
  fetchData() {
    return fetch('/api/data')
      .then(r => r.json())
      .catch(err => console.error('Erreur:', err));
  }
};

document.addEventListener('DOMContentLoaded', () => app.init());`;
  }

  generateCppCode() {
    return `#include <iostream>
#include <string>

int main() {
    std::cout << "🎯 Hello from C++!" << std::endl;
    
    // Variables
    int number = 42;
    std::string message = "EduTools-IA";
    
    std::cout << "Nombre: " << number << std::endl;
    std::cout << "Message: " << message << std::endl;
    
    return EXIT_SUCCESS;
}`;
  }

  generateCSSCode() {
    return `:root {
  --primary: #667eea;
  --secondary: #764ba2;
  --text: #333;
  --light: #f5f5f5;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--light);
  color: var(--text);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Animations */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.element { animation: slideUp 0.3s ease-out; }`;
  }

  copyToClipboard() {
    const code = document.getElementById('generatedCode').textContent;
    navigator.clipboard.writeText(code).then(() => {
      alert('✅ Code copié dans le presse-papiers !');
    });
  }

  openInEditor() {
    alert('🖊️ Feature "Ouvrir dans Éditeur" - Intégration en cours d\'implémentation');
  }

  /**
   * POUVOIR #3 : Générateur Prompt-to-Report
   */
  renderReportGenerator(container) {
    container.innerHTML = `
      <div class="ia-panel">
        <h3>📈 Générateur Prompt-to-Report</h3>
        
        <div class="report-section">
          <label>Décrivez vos données ou votre besoin :</label>
          <textarea id="reportPrompt" placeholder="Ex: Analyse les ventes mensuelles de janvier à mars: Jan 5000€, Fev 7200€, Mar 8900€..." rows="4"></textarea>
          
          <div class="data-type">
            <label>Format des données :</label>
            <select id="dataFormat">
              <option value="text">Texte libre</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </div>

          <label>Style du rapport :</label>
          <select id="reportStyle">
            <option value="executive">Executive Summary</option>
            <option value="detailed">Rapport Détaillé</option>
            <option value="infographic">Infographie</option>
          </select>

          <button class="ia-action-btn" onclick="edutoolsIA.generateReport()">
            📊 Générer Rapport
          </button>
        </div>

        <div id="reportOutput" class="report-output ia-hidden">
          <h4>📄 Rapport Généré :</h4>
          <div id="reportContent" class="report-preview"></div>
          <button class="ia-action-btn" onclick="edutoolsIA.downloadPDF()">
            📥 Télécharger en PDF
          </button>
        </div>
      </div>
    `;
  }

  generateReport() {
    const prompt = document.getElementById('reportPrompt').value;
    const format = document.getElementById('dataFormat').value;
    const style = document.getElementById('reportStyle').value;

    if (!prompt.trim()) {
      alert('Entrez vos données à analyser !');
      return;
    }

    // Génération d'un rapport simulé
    const reportTemplate = `
      <h4>${style === 'executive' ? '⚡ Résumé Exécutif' : style === 'detailed' ? '📑 Rapport Détaillé' : '🎨 Infographie'}</h4>
      <p><strong>Données analysées :</strong> ${prompt.substring(0, 100)}...</p>
      <p><strong>Format source :</strong> ${format}</p>
      <hr>
      <h4>📊 Analyse Préliminaire</h4>
      <ul>
        <li>✅ Tendance positive identifiée</li>
        <li>📈 Croissance de 30% détectée</li>
        <li>🎯 Recommandation : Maintenir la dynamique</li>
      </ul>
      <hr>
      <p><em>Rapport généré par EduTools-IA - ${new Date().toLocaleDateString('fr-FR')}</em></p>
    `;

    document.getElementById('reportContent').innerHTML = reportTemplate;
    document.getElementById('reportOutput').classList.remove('ia-hidden');
  }

  downloadPDF() {
    alert('📥 Téléchargement PDF - Intégration en cours d\'implémentation');
    // À implémenter avec une librairie comme jsPDF
  }
}

// Initialiser au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 DOMContentLoaded - Creating EdutoolsIA instance...');
  window.edutoolsIA = new EdutoolsIA();
  console.log('✅ EdutoolsIA instance created:', window.edutoolsIA);
});

// Fallback si DOMContentLoaded ne se déclenche pas
if (document.readyState === 'loading') {
  console.log('⏳ Document still loading...');
} else {
  console.log('📄 Document already loaded - Creating EdutoolsIA instance...');
  window.edutoolsIA = new EdutoolsIA();
}
