from . import content_bp
from flask import request, jsonify, current_app
import random


def _simple_template_article(topic):
    lines = [f"Introduction sur {topic}.",
             f"Développement: points clés sur {topic}.",
             "Conclusion et pistes pour aller plus loin."]
    random.shuffle(lines)
    return '\n\n'.join(lines)


@content_bp.route('/generate_article', methods=['POST'])
def generate_article():
    payload = request.json or {}
    topic = payload.get('topic', 'Culture générale')

    # Try to use transformers for better generation; fallback to simple template
    try:
        from transformers import pipeline
        generator = pipeline('text-generation', model=payload.get('model', 'distilgpt2'))
        prompt = f"Ecris un article pédagogique sur {topic}:\n"
        out = generator(prompt, max_length=200, do_sample=True, num_return_sequences=1)
        article = out[0]['generated_text']
    except Exception as e:
        current_app.logger.warning(f"Transformers not available or failed: {e}")
        article = _simple_template_article(topic)

    return jsonify({'topic': topic, 'article': article})
