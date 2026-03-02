from dataclasses import dataclass
from typing import Dict, List


MERCHANT_PHONE = '+225 0768962233'


@dataclass(frozen=True)
class Plan:
    code: str
    name: str
    amount_usd: int
    pitch: str
    highlights: List[str]
    cta_label: str

    @property
    def amount_fcfa(self) -> int:
        return self.amount_usd


PLAN_CATALOG: Dict[str, Plan] = {
    'starter': Plan(
        code='starter',
        name='Starter',
        amount_usd=5,
        pitch='Parfait pour démarrer un parcours éducatif IA sans friction.',
        highlights=['1 parcours guidé', 'Suivi de progression', 'Support standard'],
        cta_label='Commencer maintenant'
    ),
    'pro': Plan(
        code='pro',
        name='Pro',
        amount_usd=9,
        pitch='Le plan le plus choisi pour apprendre plus vite et produire mieux.',
        highlights=['Tout Starter', 'Ressources premium', 'Templates et exercices avancés'],
        cta_label='Accélérer mon niveau'
    ),
    'elite': Plan(
        code='elite',
        name='Elite',
        amount_usd=15,
        pitch='Pour les profils ambitieux qui visent un vrai avantage compétitif.',
        highlights=['Tout Pro', 'Coaching prioritaire', 'Accès anticipé aux nouveautés'],
        cta_label='Passer en Elite'
    )
}


def get_plan(plan_code: str) -> Plan:
    if not plan_code:
        return PLAN_CATALOG['pro']
    return PLAN_CATALOG.get(plan_code, PLAN_CATALOG['pro'])


def get_plan_rows() -> List[dict]:
    rows = []
    for code in ['starter', 'pro', 'elite']:
        plan = PLAN_CATALOG[code]
        rows.append(
            {
                'code': plan.code,
                'name': plan.name,
                'amount_usd': plan.amount_usd,
                'amount_fcfa': plan.amount_fcfa,
                'pitch': plan.pitch,
                'highlights': plan.highlights,
                'cta_label': plan.cta_label,
                'is_popular': plan.code == 'pro'
            }
        )
    return rows


class PaymentGateway:
    provider_name = 'generic'

    def build_manual_payment_instruction(self, plan: Plan) -> dict:
        raise NotImplementedError


class ManualMobileMoneyGateway(PaymentGateway):
    provider_name = 'mobile_money_manual'

    def build_manual_payment_instruction(self, plan: Plan) -> dict:
        return {
            'provider': self.provider_name,
            'channels': ['orange_money', 'wave'],
            'merchant_phone': MERCHANT_PHONE,
            'amount_usd': plan.amount_usd,
            'amount_fcfa': plan.amount_fcfa,
            'message': (
                f"Envoyez l'équivalent de ${plan.amount_usd} USD via Orange Money ou Wave au {MERCHANT_PHONE}. "
                "Ajoutez ensuite la référence de transaction pour validation admin."
            )
        }


class CinetPayGateway(PaymentGateway):
    provider_name = 'cinetpay'

    def initialize_payment(self, amount_usd: int, customer_name: str, customer_phone: str) -> dict:
        return {
            'provider': self.provider_name,
            'status': 'not_implemented',
            'amount_usd': amount_usd,
            'amount_fcfa': amount_usd,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'next_step': 'Implémenter l’appel API CinetPay + webhook sécurisé.'
        }


def get_gateway(provider: str) -> PaymentGateway:
    if provider == 'cinetpay':
        return CinetPayGateway()
    return ManualMobileMoneyGateway()
