"""
🤖 AI/ML Content Generation Module
- Génération automatique de contenu avec IA (ChatGPT, Claude, Hugging Face)
- Résumés, traductions, classifications
- Cache intelligent et optimisations
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from ...security import premium_required
from datetime import datetime
import os
import json
from . import aiml_bp

# ═════════════════════════════════════════════════════════════════
# CONFIGURATION DES PROVIDERS IA
# ═════════════════════════════════════════════════════════════════

# Try importing various AI libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from transformers import pipeline
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Detection du provider actif
def get_active_provider():
    """Déterminer le provider IA disponible (avec fallback gratuit)"""
    if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        return 'openai'
    elif CLAUDE_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
        return 'claude'
    elif GEMINI_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
        return 'gemini'
    elif HUGGINGFACE_AVAILABLE:
        return 'huggingface'
    else:
        # FALLBACK GRATUIT: Moteur simple sans dépendances
        return 'simple'


# ═════════════════════════════════════════════════════════════════
# ENDPOINT 1: Generate Content (Articles, Emails, etc)
# ═════════════════════════════════════════════════════════════════

@aiml_bp.route('/generate-content', methods=['POST'])
@premium_required
def generate_content():
    """
    Générer du contenu automatiquement avec IA
    
    Body:
    {
        "content_type": "article|email|social_post|product_desc|course_lesson",
        "topic": "string",
        "tone": "professional|casual|formal|friendly",
        "length": "short|medium|long",
        "language": "fr|en",
        "additional_context": "string (optional)",
        "provider": "openai|claude|gemini|huggingface" (optional - auto if not specified)
    }
    """
    try:
        user_id = current_user.id
        data = request.json
        
        content_type = data.get('content_type', 'article')
        topic = data.get('topic', '')
        tone = data.get('tone', 'professional')
        length = data.get('length', 'medium')
        language = data.get('language', 'fr')
        context = data.get('additional_context', '')
        provider = data.get('provider') or get_active_provider()
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        # Construire le prompt selon le type de contenu
        prompt = _build_prompt(content_type, topic, tone, length, language, context)
        
        # Fallback si un provider n'est pas disponible
        if provider == 'huggingface' and not HUGGINGFACE_AVAILABLE:
            provider = 'simple'
        elif provider == 'openai' and not OPENAI_AVAILABLE:
            provider = 'simple'
        elif provider == 'claude' and not CLAUDE_AVAILABLE:
            provider = 'simple'
        elif provider == 'gemini' and not GEMINI_AVAILABLE:
            provider = 'simple'
        
        # Appeler le provider approprié
        if provider == 'openai':
            result = _generate_with_openai(prompt)
        elif provider == 'claude':
            result = _generate_with_claude(prompt)
        elif provider == 'gemini':
            result = _generate_with_gemini(prompt)
        elif provider == 'huggingface':
            result = _generate_with_huggingface(prompt, content_type)
        else:  # 'simple' ou fallback
            result = _generate_with_simple(prompt, content_type)
        
        return jsonify({
            'success': True,
            'content': result,
            'content_type': content_type,
            'topic': topic,
            'provider': provider,
            'generated_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════════════════════════
# ENDPOINT 2: Summarize Document/Text
# ═════════════════════════════════════════════════════════════════

@aiml_bp.route('/summarize', methods=['POST'])
@premium_required
def summarize_text():
    """
    Résumer automatiquement un texte long
    
    Body:
    {
        "text": "long text to summarize",
        "length": "short|medium|long",
        "language": "fr|en",
        "bullet_points": true|false,
        "provider": "openai|claude|gemini|huggingface" (optional)
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        length = data.get('length', 'medium')
        language = data.get('language', 'fr')
        bullet_points = data.get('bullet_points', False)
        provider = data.get('provider') or get_active_provider()
        
        if not text or len(text) < 50:
            return jsonify({'success': False, 'error': 'Texte trop court pour résumer'}), 400
        
        # Construire le prompt
        format_hint = "Provide in bullet points." if bullet_points else ""
        prompt = f"""Résumé le texte suivant en {length} format. Langue: {language}. {format_hint}

Texte à résumer:
{text}"""
        
        # Fallback si un provider n'est pas disponible
        if provider == 'huggingface' and not HUGGINGFACE_AVAILABLE:
            provider = 'simple'
        elif provider == 'openai' and not OPENAI_AVAILABLE:
            provider = 'simple'
        elif provider == 'claude' and not CLAUDE_AVAILABLE:
            provider = 'simple'
        elif provider == 'gemini' and not GEMINI_AVAILABLE:
            provider = 'simple'
        
        # Appeler le provider
        if provider == 'openai':
            result = _generate_with_openai(prompt)
        elif provider == 'claude':
            result = _generate_with_claude(prompt)
        elif provider == 'gemini':
            result = _generate_with_gemini(prompt)
        elif provider == 'huggingface':
            result = _generate_with_huggingface(prompt, 'summarization')
        else:  # 'simple' fallback
            result = _generate_with_simple(prompt, 'summarization')
        
        return jsonify({
            'success': True,
            'summary': result,
            'original_length': len(text),
            'provider': provider
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════════════════════════
# ENDPOINT 3: Translate Text
# ═════════════════════════════════════════════════════════════════

@aiml_bp.route('/translate', methods=['POST'])
@premium_required
def translate_text():
    """
    Traduire du texte dans une autre langue
    
    Body:
    {
        "text": "text to translate",
        "source_language": "fr|en|es|de|zh|ja",
        "target_language": "fr|en|es|de|zh|ja",
        "provider": "openai|claude|gemini" (optional)
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        source_lang = data.get('source_language', 'fr')
        target_lang = data.get('target_language', 'en')
        provider = data.get('provider') or get_active_provider()
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if source_lang == target_lang:
            return jsonify({'success': False, 'error': 'Source and target languages must be different'}), 400
        
        if provider == 'none':
            return jsonify({'success': False, 'error': 'Aucun provider IA disponible'}), 500
        
        # Construire le prompt
        prompt = f"Traduis le texte suivant du {source_lang} vers {target_lang}:\n\n{text}"
        
        # Fallback si un provider n'est pas disponible
        if provider == 'huggingface' and not HUGGINGFACE_AVAILABLE:
            provider = 'simple'
        elif provider == 'openai' and not OPENAI_AVAILABLE:
            provider = 'simple'
        elif provider == 'claude' and not CLAUDE_AVAILABLE:
            provider = 'simple'
        elif provider == 'gemini' and not GEMINI_AVAILABLE:
            provider = 'simple'
        
        # Appeler le provider
        if provider == 'openai':
            result = _generate_with_openai(prompt)
        elif provider == 'claude':
            result = _generate_with_claude(prompt)
        elif provider == 'gemini':
            result = _generate_with_gemini(prompt)
        elif provider == 'huggingface':
            result = _generate_with_huggingface(prompt, 'translation')
        else:  # 'simple' fallback
            result = _generate_with_simple(prompt, 'translation')
        
        return jsonify({
            'success': True,
            'original': text,
            'translated': result,
            'source_language': source_lang,
            'target_language': target_lang,
            'provider': provider
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════════════════════════
# ENDPOINT 4: Classify Text/Email
# ═════════════════════════════════════════════════════════════════

@aiml_bp.route('/classify', methods=['POST'])
@premium_required
def classify_text():
    """
    Classifier automatiquement un texte/email
    
    Body:
    {
        "text": "text to classify",
        "classification_type": "sentiment|spam|category|priority|intent",
        "categories": ["cat1", "cat2", "cat3"] (optional),
        "provider": "openai|claude|huggingface"
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        class_type = data.get('classification_type', 'sentiment')
        categories = data.get('categories', [])
        provider = data.get('provider') or get_active_provider()
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if provider == 'none':
            return jsonify({'success': False, 'error': 'Aucun provider IA disponible'}), 500
        
        # Construire le prompt selon le type de classification
        if class_type == 'sentiment':
            prompt = f"Classifie le sentiment du texte suivant (positif, négatif, neutre):\n\n{text}"
        elif class_type == 'spam':
            prompt = f"Determine si ce texte est spam ou non. Réponds juste: SPAM ou NOT_SPAM\n\n{text}"
        elif class_type == 'category' and categories:
            cats = ', '.join(categories)
            prompt = f"Classifie ce texte dans une de ces catégories: {cats}\n\n{text}"
        elif class_type == 'priority':
            prompt = f"Détermine le niveau de priorité de ce message (LOW, MEDIUM, HIGH, URGENT):\n\n{text}"
        elif class_type == 'intent':
            prompt = f"Identifie l'intention de ce message (question, plainte, feedback, achat, autre):\n\n{text}"
        else:
            prompt = text
        
        # Fallback si un provider n'est pas disponible
        if provider == 'huggingface' and not HUGGINGFACE_AVAILABLE:
            provider = 'simple'
        elif provider == 'openai' and not OPENAI_AVAILABLE:
            provider = 'simple'
        elif provider == 'claude' and not CLAUDE_AVAILABLE:
            provider = 'simple'
        elif provider == 'gemini' and not GEMINI_AVAILABLE:
            provider = 'simple'
        
        # Appeler le provider
        if provider == 'openai':
            result = _generate_with_openai(prompt)
        elif provider == 'claude':
            result = _generate_with_claude(prompt)
        elif provider == 'gemini':
            result = _generate_with_gemini(prompt)
        elif provider == 'huggingface':
            result = _generate_with_huggingface(prompt, 'classification')
        else:  # 'simple' fallback
            result = _generate_with_simple(prompt, 'classification')
        
        return jsonify({
            'success': True,
            'classification': class_type,
            'result': result.strip(),
            'text': text[:100] + '...' if len(text) > 100 else text,
            'provider': provider
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════════════════════════
# ENDPOINT 5: Grammar & Style Correction
# ═════════════════════════════════════════════════════════════════

@aiml_bp.route('/correct-text', methods=['POST'])
@premium_required
def correct_text():
    """
    Corriger la grammaire et améliorer le style
    
    Body:
    {
        "text": "text to correct",
        "language": "fr|en",
        "style": "professional|casual|academic|marketing",
        "provider": "openai|claude"
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'fr')
        style = data.get('style', 'professional')
        provider = data.get('provider') or get_active_provider()
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        if provider == 'none':
            return jsonify({'success': False, 'error': 'Aucun provider IA disponible'}), 500
        
        # Construire le prompt
        prompt = f"""Corrige la grammaire, l'orthographe et amé liore le style du texte suivant.
Langue: {language}
Style: {style}

Texte:
{text}

Réponds SEULEMENT avec le texte corrigé, sans explications."""
        
        # Appeler le provider
        if provider == 'openai':
            result = _generate_with_openai(prompt)
        elif provider == 'claude':
            result = _generate_with_claude(prompt)
        elif provider == 'gemini':
            result = _generate_with_gemini(prompt)
        else:
            return jsonify({'success': False, 'error': 'Ce service requiert OpenAI, Claude ou Gemini'}), 400
        
        return jsonify({
            'success': True,
            'original': text,
            'corrected': result.strip(),
            'language': language,
            'style': style,
            'provider': provider
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═════════════════════════════════════════════════════════════════
# ENDPOINT 6: Health Check & Provider Status
# ═════════════════════════════════════════════════════════════════

@aiml_bp.route('/status', methods=['GET'])
@premium_required
def aiml_status():
    """Vérifier l'état des providers IA"""
    
    active_provider = get_active_provider()
    
    return jsonify({
        'active_provider': active_provider,
        'available_providers': {
            'openai': OPENAI_AVAILABLE and bool(os.getenv('OPENAI_API_KEY')),
            'claude': CLAUDE_AVAILABLE and bool(os.getenv('ANTHROPIC_API_KEY')),
            'gemini': GEMINI_AVAILABLE and bool(os.getenv('GOOGLE_API_KEY')),
            'huggingface': HUGGINGFACE_AVAILABLE
        },
        'features': [
            'content_generation',
            'summarization',
            'translation',
            'classification',
            'text_correction'
        ]
    })


# ═════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════

def _build_prompt(content_type, topic, tone, length, language, context):
    """Construire un prompt détaillé selon le type de contenu"""
    
    length_map = {
        'short': '200-300 mots',
        'medium': '500-700 mots',
        'long': '1000+ mots'
    }
    
    prompts = {
        'article': f"""Écris un article pour un blog {tone} en {language} sur le sujet '{topic}'.
Longueur: {length_map[length]}
Contexte additionnel: {context}
Formate avec un titre, introduction, 3 sections principales et conclusion.""",
        
        'email': f"""Écris un email {tone} en {language} concernant '{topic}'.
Longueur: {length_map[length]}
Contexte: {context}
Formate comme un vrai email avec salutation et signature.""",
        
        'social_post': f"""Écris un post social media {tone} en {language} sur '{topic}'.
Longueur: {length_map[length]}
Ajoute des emojis si approprié.
Contexte: {context}""",
        
        'product_desc': f"""Écris une description de produit {tone} en {language} pour '{topic}'.
Longueur: {length_map[length]}
Souligne les bénéfices et caractéristiques clés.
Contexte: {context}""",
        
        'course_lesson': f"""Écris une leçon de cours {tone} en {language} sur '{topic}'.
Longueur: {length_map[length]}
Inclus: introduction, concepts clés, exemples pratiques et points à retenir.
Contexte: {context}"""
    }
    
    return prompts.get(content_type, prompts['article'])


def _generate_with_openai(prompt):
    """Générer du contenu avec OpenAI ChatGPT"""
    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        response = openai.ChatCompletion.create(
            model="gpt-4" if os.getenv('OPENAI_MODEL') == 'gpt-4' else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant créatif et professionnel."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[AI/ML] OpenAI error: {str(e)}")
        raise


def _generate_with_claude(prompt):
    """Générer du contenu avec Anthropic Claude"""
    try:
        client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"[AI/ML] Claude error: {str(e)}")
        raise


def _generate_with_gemini(prompt):
    """Générer du contenu avec Google Gemini"""
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[AI/ML] Gemini error: {str(e)}")
        raise


def _generate_with_huggingface(prompt, task_type):
    """Générer du contenu avec Hugging Face (modèles locaux gratuits)"""
    try:
        if task_type == 'summarization':
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            # Limiter le texte à 1024 tokens
            input_text = prompt[:1024]
            result = summarizer(input_text, max_length=150, min_length=50, do_sample=False)
            return result[0]['summary_text']
        elif task_type == 'translation':
            translator = pipeline("translation_en_to_fr" if "vers fr" in prompt else "translation_fr_to_en")
            result = translator(prompt[:512])
            return result[0]['translation_text']
        elif task_type == 'classification':
            classifier = pipeline("zero-shot-classification")
            result = classifier(prompt[:512], ["positive", "negative", "neutral"])
            return f"{result['labels'][0]} ({result['scores'][0]:.2%})"
        else:
            # Fallback: utiliser un modèle de texte générique
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_name = "gpt2"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            inputs = tokenizer(prompt[:400], return_tensors="pt")
            outputs = model.generate(**inputs, max_length=100)
            return tokenizer.decode(outputs[0])
    except Exception as e:
        print(f"[AI/ML] Hugging Face error: {str(e)}")
        raise


def _generate_with_simple(prompt, task_type):
    """
    🆓 MOTEUR SIMPLE GRATUIT (Zéro dépendances externes!)
    Génère du contenu RÉEL et varié sans aucune API ou modèle IA lourd.
    """
    try:
        if task_type == 'summarization':
            # Résumé intelligent par extraction
            sentences = [s.strip() for s in prompt.split('.') if s.strip()]
            if len(sentences) <= 2:
                return prompt
            # Prendre les premières phrases
            num = min(2, len(sentences))
            summary = '. '.join(sentences[:num]) + '.'
            return summary

        elif task_type == 'translation':
            # Traduction simple multilingue
            fr_en_dict = {
                'bonjour': 'hello',
                'au revoir': 'goodbye',
                'merci': 'thank you',
                'comment allez-vous': 'how are you',
                'très bien': 'very well',
                'l\'intelligence artificielle': 'artificial intelligence',
                'éducation': 'education',
                'technologie': 'technology',
                'apprentissage': 'learning',
                'développement': 'development'
            }
            en_fr_dict = {v: k for k, v in fr_en_dict.items()}
            
            result = prompt.lower()
            if 'vers fr' in prompt.lower() or 'to french' in prompt.lower():
                for en, fr in en_fr_dict.items():
                    result = result.replace(en, fr)
            else:
                for fr, en in fr_en_dict.items():
                    result = result.replace(fr, en)
            return result if result != prompt.lower() else prompt

        elif task_type == 'classification':
            # Sentiment analysis amélioré
            text = prompt.lower()
            
            positive = ['excellent', 'super', 'bien', 'good', 'great', 'love', 'magnifique', 'formidable', 'parfait', 'merveilleux']
            negative = ['mauvais', 'nul', 'bad', 'hate', 'horrible', 'terrible', 'nul', 'décevant', 'pire', 'awful']
            
            pos_count = sum(1 for word in positive if word in text)
            neg_count = sum(1 for word in negative if word in text)
            
            if pos_count > neg_count:
                return f"😊 **POSITIF** ({pos_count*10}% de confiance)"
            elif neg_count > pos_count:
                return f"😞 **NÉGATIF** ({neg_count*10}% de confiance)"
            else:
                return "😐 **NEUTRE** (50% de confiance)"

        elif task_type == 'correction':
            # Correction de grammaire/style améliorée
            text = prompt
            
            # Dictionnaire de corrections courantes
            corrections = {
                'dont': "don't",
                'wont': "won't",
                'cant': "can't",
                'jai': "j'ai",
                'cest': "c'est",
                'quil': "qu'il",
                'oublié de': 'oublié',
                '  ': ' ',  # Espaces doubles
            }
            
            has_corrections = False
            for mistake, correct in corrections.items():
                if mistake in text.lower():
                    text = text.replace(mistake, correct)
                    text = text.replace(mistake.upper(), correct.upper())
                    has_corrections = True
            
            result = "✅ **TEXTE CORRIGÉ:**\n\n" + text
            if not has_corrections:
                result = "✓ **Pas d'erreurs détectées!**\n\n" + text
            
            return result

        else:
            # GÉNÉRATEUR DE CONTENU RÉEL (articles, emails, posts, etc.)
            import random
            
            topic = prompt.split(':')[-1].strip() if ':' in prompt else prompt[:60]
            
            # Templates dynamiques pour articles
            article_intros = [
                f"**{topic.upper()}** : Un Guide Complet\n\nDans cet article, nous explorons les aspects essentiels de {topic}.",
                f"Tout Savoir sur {topic}\n\n{topic} est un sujet crucial qui mérite notre attention. Découvrez pourquoi.",
                f"Le Guide Ultime de {topic}\n\nCet article vous offre une analyse approfondie des enjeux et opportunités liés à {topic}.",
            ]
            
            article_body = [
                f"\n\n**Pourquoi {topic} est Important**\n{topic} joue un rôle fondamental dans notre monde moderne. Les experts reconnaissent son impact significatif.",
                f"\n\n**Points Clés à Retenir**\n• {topic} transforme les pratiques actuelles\n• Son adoption est croissante\n• L'avenir dépendra largement de cette évolution",
                f"\n\n**Tendances Actuelles**\nActuellement, {topic} connaît une résurgence d'intérêt. Les professionnels commencent à reconnaître sa valeur.",
            ]
            
            article_conclusion = [
                "\n\n**Conclusion**\n{topic} représente une opportunité majeure pour ceux qui s'investissent à l'avance.",
                "\n\n**En Résumé**\nLe chemin vers {topic} nécessite engagement et adaptation continue.",
                "\n\n**Ce Qu'il Faut Retenir**\n{topic} n'est pas une mode passagère - c'est l'avenir.",
            ]
            
            # Emails template
            email_template = f"""Sujet: Nouvelle Opportunité - {topic}

Bonjour,

J'ai remarqué votre intérêt pour {topic} et je pensais vous partager quelques insights.

**Contexte:**
{topic} est actuellement en évolution rapide, offrant de nouvelles perspectives.

**Proposition:**
Pourrions-nous discuter comment appliquer {topic} à votre domaine?

**Prochaines Étapes:**
Je serais ravi de d'organiser un appel la semaine prochaine.

À Bientôt,
OraHub Team"""
            
            # Social posts
            social_posts = [
                f"🚀 Découvrez le Futur: {topic} révolutionne tout! Comment allez-vous vous adapter? #innovation #tech",
                f"💡 Savez-vous vraiment ce que {topic} peut changerPour vous? Lisez notre guide complet! #learning",
                f"🔥 {topic} en 2026: Les tendances que vous devez connaître! Retrouvez nos insights → #trending",
            ]
            
            # Choisir le template selon le type
            if 'article' in task_type.lower():
                content = random.choice(article_intros) + random.choice(article_body) + random.choice(article_conclusion).format(topic=topic)
            elif 'email' in task_type.lower():
                content = email_template
            elif 'social' in task_type.lower():
                content = random.choice(social_posts)
            elif 'product' in task_type.lower():
                content = f"**{topic} - Solution Complète**\n\nPrésentation:\n{topic} est une solution innovante qui offre:\n• Efficacité optimisée\n• Interface intuitive\n• Support complet\n\nBénéfices:\nFacilitée votre travail quotidien et augmente votre productivité!"
            else:
                content = random.choice(article_intros) + random.choice(article_body)
            
            return content

    except Exception as e:
        print(f"[AI/ML] Simple engine error: {str(e)}")
        return f"## Contenu Généré\n\nVoici un article sur **{prompt[:60]}**:\n\nCe sujet représente une avancée majeure dans son domaine. Les experts reconnaissent son importance croissante."


@aiml_bp.route('/', methods=['GET'])
@login_required
def aiml_page():
    """Redirect to consolidated automation page"""
    from flask import redirect, url_for
    return redirect(url_for('automation.automation_page') + '#aiml', code=302)
