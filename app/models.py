from app import db
from datetime import datetime
import uuid


class Campaign(db.Model):

    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)

    targets = db.relationship('Target', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.name}>'


class Target(db.Model):

    __tablename__ = 'targets'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey(
        'campaigns.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120))

    token = db.Column(db.String(36), default=lambda: str(
        uuid.uuid4()), unique=True)

    email_sent = db.Column(db.Boolean, default=False)
    email_opened = db.Column(db.Boolean, default=False)
    link_clicked = db.Column(db.Boolean, default=False)
    creds_submitted = db.Column(db.Boolean, default=False)

    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Target {self.email}>'


class EmailTemplate(db.Model):

    __tablename__ = 'email_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body_html = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EmailTemplate {self.name}>'
