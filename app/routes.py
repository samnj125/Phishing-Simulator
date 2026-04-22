from flask import Blueprint, render_template, redirect, url_for, request, jsonify, send_file
from app import db
from app.models import Campaign, Target, EmailTemplate
from datetime import datetime
import io


main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Homepage — shows all campaigns."""
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return render_template('index.html', campaigns=campaigns)


@main.route('/campaign/new', methods=['GET', 'POST'])
def new_campaign():
    """
    GET  → show the 'create campaign' form
    POST → receive the form data and save to database
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        campaign = Campaign(name=name, description=description)
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('main.view_campaign', id=campaign.id))

    return render_template('new_campaign.html')


@main.route('/campaign/<int:id>')
def view_campaign(id):
    """Shows a single campaign with all its targets and stats."""
    campaign = Campaign.query.get_or_404(id)

    total = len(campaign.targets)
    opened = sum(1 for t in campaign.targets if t.email_opened)
    clicked = sum(1 for t in campaign.targets if t.link_clicked)
    submitted = sum(1 for t in campaign.targets if t.creds_submitted)

    stats = {
        'total': total,
        'opened': opened,
        'clicked': clicked,
        'submitted': submitted,
        'click_rate': round((clicked / total * 100), 1) if total > 0 else 0,
        'submit_rate': round((submitted / total * 100), 1) if total > 0 else 0,
    }

    return render_template('campaign.html', campaign=campaign, stats=stats)


@main.route('/campaign/<int:id>/add_target', methods=['POST'])
def add_target(id):
    """Adds a single target to a campaign."""
    campaign = Campaign.query.get_or_404(id)
    email = request.form.get('email')
    name = request.form.get('name', '')

    target = Target(campaign_id=campaign.id, email=email, name=name)
    db.session.add(target)
    db.session.commit()
    return redirect(url_for('main.view_campaign', id=id))


@main.route('/track/open/<token>')
def track_open(token):

    target = Target.query.filter_by(token=token).first()
    if target and not target.email_opened:
        target.email_opened = True
        target.opened_at = datetime.utcnow()
        db.session.commit()

    pixel = bytes([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
        0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00,
        0x0a, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9c, 0x62, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0d, 0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49,
        0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82
    ])
    return send_file(io.BytesIO(pixel), mimetype='image/png')


@main.route('/track/click/<token>')
def track_click(token):

    target = Target.query.filter_by(token=token).first()
    if target and not target.link_clicked:
        target.link_clicked = True
        target.clicked_at = datetime.utcnow()
        db.session.commit()

    # Send them to the fake login page, keeping their token
    return redirect(url_for('main.fake_login', token=token))


@main.route('/login/<token>', methods=['GET', 'POST'])
def fake_login(token):

    target = Target.query.filter_by(token=token).first_or_404()

    if request.method == 'POST':

        if not target.creds_submitted:
            target.creds_submitted = True
            target.submitted_at = datetime.utcnow()
            db.session.commit()

        return redirect(url_for('main.training', token=token))

    return render_template('fake_login.html', target=target)


@main.route('/training/<token>')
def training(token):
    """
    The education page shown after the target 'falls' for the phish.
    This is the most important page — it teaches them what just happened.
    """
    target = Target.query.filter_by(token=token).first_or_404()
    return render_template('training.html', target=target)
