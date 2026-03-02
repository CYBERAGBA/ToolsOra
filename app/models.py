from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from tinydb import TinyDB, Query
from pathlib import Path

# ==========================================================
# DATABASE INIT
# ==========================================================

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'db.json'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
db = TinyDB(DB_PATH)

# ==========================================================
# USER MODEL (EVOLUTIVE SAAS STRUCTURE)
# ==========================================================

class User(UserMixin):
    table = db.table('users')

    def __init__(self,
                 id,
                 username,
                 email,
                 password_hash,
                 is_admin=False,
                 role="user",
                 progress=None,
                 badges=None,
                 certificates=None,
                 created_at=None):

        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.role = role
        self.progress = progress or {}
        self.badges = badges or []
        self.certificates = certificates or []
        self.created_at = created_at or datetime.utcnow().isoformat()

    # ======================================================
    # PASSWORD
    # ======================================================

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ======================================================
    # ROLE & PERMISSIONS
    # ======================================================

    def upgrade_to_premium(self):
        self.role = "premium"
        self.save()

    def downgrade_to_user(self):
        self.role = "user"
        self.save()

    def is_premium(self):
        return self.role == "premium"

    def is_admin_user(self):
        return self.is_admin or self.role == "admin"

    # ======================================================
    # PROGRESSION SYSTEM
    # ======================================================

    def get_progress(self, module, section):
        return self.progress.get(module, {}).get(section, 0)

    def update_progress(self, module, section, level):
        if module not in self.progress:
            self.progress[module] = {}
        self.progress[module][section] = level
        self.save()

    def reset_module_progress(self, module):
        if module in self.progress:
            self.progress[module] = {}
            self.save()

    # ======================================================
    # BADGES & CERTIFICATES
    # ======================================================

    def add_badge(self, badge_name):
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.save()

    def add_certificate(self, certificate_name):
        if certificate_name not in self.certificates:
            self.certificates.append(certificate_name)
            self.save()

    # ======================================================
    # STORAGE
    # ======================================================

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'role': self.role,
            'progress': self.progress,
            'badges': self.badges,
            'certificates': self.certificates,
            'created_at': self.created_at,
        }

    def save(self):
        User.table.upsert(self.to_dict(), Query().id == self.id)

    # ======================================================
    # CLASS METHODS
    # ======================================================

    @classmethod
    def create(cls, username, email, password):
        last = cls.table.all()
        next_id = (max([u.get('id', 0) for u in last]) + 1) if last else 1
        pwd = generate_password_hash(password)

        user = cls(
            id=next_id,
            username=username,
            email=email,
            password_hash=pwd,
            role="user",
            progress={},
            badges=[],
            certificates=[]
        )

        cls.table.insert(user.to_dict())
        return user

    @classmethod
    def get_by_email(cls, email):
        res = cls.table.search(Query().email == email)
        if not res:
            return None
        return cls._from_record(res[0])

    @classmethod
    def get_by_id(cls, id_):
        res = cls.table.search(Query().id == int(id_))
        if not res:
            return None
        return cls._from_record(res[0])

    @classmethod
    def get_all(cls):
        """Get all users as User objects."""
        res = cls.table.all()
        return [cls._from_record(r) for r in res]

    @classmethod
    def _from_record(cls, r):
        return cls(
            r['id'],
            r['username'],
            r['email'],
            r['password_hash'],
            r.get('is_admin', False),
            r.get('role', 'user'),
            r.get('progress', {}),
            r.get('badges', []),
            r.get('certificates', []),
            r.get('created_at')
        )

# ==========================================================
# SUBSCRIPTIONS
# ==========================================================

class Subscription:
    table = db.table('subscriptions')

    @classmethod
    def create(
        cls,
        user_id,
        plan,
        amount,
        provider,
        active=False,
        status='pending_validation',
        payment_id=None,
        duration_days=30,
        features=None
    ):
        now = datetime.utcnow()
        started_at = now.isoformat() if active else None
        ends_at = (now + timedelta(days=duration_days)).isoformat() if active else None
        rec = {
            'id': int(now.timestamp() * 1000),
            'user_id': int(user_id),
            'plan': plan,
            'amount': float(amount),
            'provider': provider,
            'status': status,
            'active': active,
            'payment_id': payment_id,
            'duration_days': int(duration_days),
            'features': features or [],
            'started_at': started_at,
            'ends_at': ends_at,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        cls.table.insert(rec)
        return rec

    @classmethod
    def get_by_id(cls, subscription_id):
        row = cls.table.get(Query().id == int(subscription_id))
        return row

    @classmethod
    def get_latest_for_user(cls, user_id):
        rows = cls.table.search(Query().user_id == int(user_id))
        if not rows:
            return None
        return sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)[0]

    @classmethod
    def get_active_for_user(cls, user_id):
        row = cls.table.get((Query().user_id == int(user_id)) & (Query().active == True))
        return row

    @classmethod
    def list_pending(cls, limit=50):
        rows = cls.table.search(Query().status == 'pending_validation')
        rows_sorted = sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)
        return rows_sorted[:limit]

    @classmethod
    def get_all(cls):
        """Get all subscriptions."""
        rows = cls.table.all()
        return sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)

    @classmethod
    def get_by_payment_id(cls, payment_id):
        rows = cls.table.search(Query().payment_id == int(payment_id))
        if not rows:
            return None
        return sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)[0]

    @classmethod
    def activate(cls, subscription_id):
        now = datetime.utcnow()
        row = cls.get_by_id(subscription_id)
        if not row:
            return None
        duration_days = int(row.get('duration_days', 30))
        updated = {
            **row,
            'active': True,
            'status': 'active',
            'started_at': now.isoformat(),
            'ends_at': (now + timedelta(days=duration_days)).isoformat(),
            'updated_at': now.isoformat(),
            'activated_at': now.isoformat()
        }
        cls.table.update(updated, Query().id == int(subscription_id))
        return updated

    @classmethod
    def cancel_user_active_subscriptions(cls, user_id):
        now = datetime.utcnow().isoformat()
        rows = cls.table.search((Query().user_id == int(user_id)) & (Query().active == True))
        for row in rows:
            cls.table.update(
                {
                    'active': False,
                    'status': 'replaced',
                    'updated_at': now
                },
                Query().id == row['id']
            )

    @classmethod
    def mark_rejected_by_payment(cls, payment_id):
        row = cls.get_by_payment_id(payment_id)
        if not row:
            return None
        now = datetime.utcnow().isoformat()
        updated = {
            **row,
            'active': False,
            'status': 'payment_rejected',
            'updated_at': now
        }
        cls.table.update(updated, Query().id == row['id'])
        return updated

# ==========================================================
# PAYMENTS
# ==========================================================

class Payment:
    table = db.table('payments')

    @classmethod
    def create_manual(
        cls,
        user_id,
        plan,
        provider,
        amount,
        transaction_ref,
        payer_phone,
        payer_name=''
    ):
        now = datetime.utcnow()
        rec = {
            'id': int(now.timestamp() * 1000),
            'user_id': int(user_id),
            'plan': plan,
            'provider': provider,
            'amount': float(amount),
            'currency': 'USD',
            'status': 'pending_manual_confirmation',
            'transaction_ref': transaction_ref,
            'payer_phone': payer_phone,
            'payer_name': payer_name,
            'merchant_phone': '+225 0768962233',
            'channel': 'mobile_money_manual',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'confirmed_at': None,
            'confirmed_by': None,
            'confirmation_note': None
        }
        cls.table.insert(rec)
        return rec

    @classmethod
    def get_by_id(cls, payment_id):
        row = cls.table.get(Query().id == int(payment_id))
        return row

    @classmethod
    def list_pending_manual(cls, limit=100):
        rows = cls.table.search(Query().status == 'pending_manual_confirmation')
        rows_sorted = sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)
        return rows_sorted[:limit]

    @classmethod
    def all_for_user(cls, user_id, limit=20):
        rows = cls.table.search(Query().user_id == int(user_id))
        rows_sorted = sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)
        return rows_sorted[:limit]

    @classmethod
    def confirm_manual(cls, payment_id, admin_user_id, confirmation_note=''):
        row = cls.get_by_id(payment_id)
        if not row:
            return None
        now = datetime.utcnow().isoformat()
        updated = {
            **row,
            'status': 'confirmed',
            'confirmed_at': now,
            'confirmed_by': int(admin_user_id),
            'confirmation_note': confirmation_note,
            'updated_at': now
        }
        cls.table.update(updated, Query().id == int(payment_id))
        return updated

    @classmethod
    def reject_manual(cls, payment_id, admin_user_id, confirmation_note=''):
        row = cls.get_by_id(payment_id)
        if not row:
            return None
        now = datetime.utcnow().isoformat()
        updated = {
            **row,
            'status': 'rejected',
            'confirmed_at': now,
            'confirmed_by': int(admin_user_id),
            'confirmation_note': confirmation_note,
            'updated_at': now
        }
        cls.table.update(updated, Query().id == int(payment_id))
        return updated

# ==========================================================
# CONTENT SYSTEM
# ==========================================================

class ContentItem:
    table = db.table('content')

    @classmethod
    def create(cls, title, body):
        rec = {
            'id': int(datetime.utcnow().timestamp() * 1000),
            'title': title,
            'body': body,
            'created_at': datetime.utcnow().isoformat()
        }
        cls.table.insert(rec)
        return rec

    @classmethod
    def all(cls, limit=10):
        rows = cls.table.all()
        rows_sorted = sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)
        return rows_sorted[:limit]

# ==========================================================
# PLUGINS
# ==========================================================

class Plugin:
    table = db.table('plugins')

    @classmethod
    def create(cls, name, description, repository, published=True):
        rec = {
            'id': int(datetime.utcnow().timestamp() * 1000),
            'name': name,
            'description': description,
            'repository': repository,
            'published': published
        }
        cls.table.insert(rec)
        return rec

# ==========================================================
# CONVERSIONS
# ==========================================================

class Conversion:
    table = db.table('conversions')

    @classmethod
    def create(cls, original, output, direction, status='done'):
        rec = {
            'id': int(datetime.utcnow().timestamp() * 1000),
            'original': original,
            'output': output,
            'direction': direction,
            'status': status,
            'created_at': datetime.utcnow().isoformat()
        }
        cls.table.insert(rec)
        return rec

    @classmethod
    def all(cls, limit=20):
        rows = cls.table.all()
        rows_sorted = sorted(rows, key=lambda r: r.get('created_at', ''), reverse=True)
        return rows_sorted[:limit]

# ==========================================================
# LOGIN MANAGER
# ==========================================================

from .extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)