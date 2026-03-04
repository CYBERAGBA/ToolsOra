from flask import render_template, request, redirect, session, url_for, jsonify, abort, send_file, Response
from flask_login import login_required, current_user
from . import main_bp
from app.models import User, Subscription, Payment
from app.security import admin_required
import os
from datetime import datetime


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate dynamic sitemap.xml for SEO."""
    base_url = request.url_root.rstrip('/')
    
    # Core pages
    urls = [
        ('/', 'weekly', 1.0),
        ('/dashboard', 'weekly', 0.8),
    ]
    
    # Module pages
    modules = [
        ('aiml', 'AI/ML Content Generation'),
        ('automation', 'Business Process Automation'),
        ('content', 'Content Management'),
        ('education', 'Educational Tools'),
        ('export', 'Data Export'),
        ('notifications', 'Notifications'),
        ('plugins', 'Plugins & Extensions'),
        ('rewards', 'Rewards & Gamification'),
        ('saas', 'SaaS Management'),
        ('scheduling', 'Schedule Management'),
        ('sms', 'SMS & Communications'),
    ]
    
    for module_name, _ in modules:
        urls.append((f'/{module_name}', 'weekly', 0.7))
    
    # Generate XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for path, changefreq, priority in urls:
        xml_content += f'''  <url>
    <loc>{base_url}{path}</loc>
    <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>
'''
    
    xml_content += '</urlset>'
    
    return Response(xml_content, mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    """Generate robots.txt for search engine crawling."""
    robots_content = '''User-agent: *
Allow: /
Allow: /static/
Allow: /dashboard
Disallow: /admin/
Disallow: /api/
Disallow: /*.json$
Disallow: /private/

# Crawl-delay for respectful crawling
Crawl-delay: 1

# Sitemaps
Sitemap: ''' + request.url_root.rstrip('/') + '''/sitemap.xml

# Google Search Console
User-agent: Googlebot
Allow: /
Crawl-delay: 0.1

# Block bad bots
User-agent: MJ12bot
Disallow: /

User-agent: AhrefsBot
Disallow: /

User-agent: SemrushBot
Disallow: /
'''
    return Response(robots_content, mimetype='text/plain')


@main_bp.route('/<filename>')
def serve_verification_files(filename):
    """Serve verification files from static folder."""
    verification_files = [
        'google3100977de9b5bc49.html',
    ]
    
    if filename in verification_files:
        file_path = os.path.join(os.path.dirname(__file__), '../../static', filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='text/html')
    
    abort(404)


@main_bp.route('/test-edutools')
def test_edutools():
    return render_template('test_edutools.html')


@main_bp.route('/test-button')
def test_button():
    return render_template('test_simple_button.html')


@main_bp.route('/content')
def content():
    return render_template('content.html')


@main_bp.route('/plugins')
def plugins():
    return render_template('plugins.html')


@main_bp.route('/set-language/<lang>')
def set_language(lang):
    supported_languages = ['fr', 'en']
    if lang in supported_languages:
        session['lang'] = lang

    next_url = request.args.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)

    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Example dashboard; modules will extend this
    return render_template('dashboard.html', user=current_user)


@main_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with subscription and payment management."""
    # Get summary data
    all_users = User.get_all()
    all_subscriptions = Subscription.get_all()
    pending_payments = Payment.list_pending_manual(limit=200)
    active_subscriptions = [s for s in all_subscriptions if s.get('active')]
    pending_subscriptions = [s for s in all_subscriptions if s.get('status') == 'pending_validation']
    
    # Calculate stats
    total_users = len(all_users)
    total_subscriptions = len(all_subscriptions)
    active_count = len(active_subscriptions)
    pending_count = len(pending_subscriptions)
    pending_payments_count = len(pending_payments)
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_subscriptions=total_subscriptions,
        active_subscriptions_count=active_count,
        pending_subscriptions_count=pending_count,
        pending_payments_count=pending_payments_count,
        all_users=all_users,
        pending_payments=pending_payments,
        pending_subscriptions=pending_subscriptions,
        all_subscriptions=all_subscriptions
    )
