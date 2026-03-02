# Architecture SaaS éducatif (Mobile Money manuel -> CinetPay)

## Objectif
Mettre en place un tunnel d’abonnement simple pour le marché local (Côte d’Ivoire) avec paiement manuel Orange Money / Wave, puis évoluer vers une intégration API CinetPay sans réécrire la logique métier.

## Plans
- Starter: 3000 FCFA
- Pro: 5000 FCFA
- Elite: 8000 FCFA

Le catalogue est centralisé dans `app/payments/services.py` (`PLAN_CATALOG`) pour garantir la cohérence entre UI, validation et back-office.

## Flux actuel (manuel)
1. L’utilisateur choisit un plan sur `/modules/saas`.
2. Il paie via Orange Money ou Wave au `+225 0768962233`.
3. Il soumet `provider + numéro payeur + référence transaction`.
4. Le système crée:
   - un `Payment` en statut `pending_manual_confirmation`
   - un `Subscription` en statut `pending_validation` (inactive)
5. Un admin valide depuis `/payments/admin/manual`.
6. À la confirmation:
   - paiement => `confirmed`
   - abonnement => `active`
   - rôle utilisateur => `premium`

## Évolutivité CinetPay
La couche `PaymentGateway` sépare l’orchestration métier de l’intégration fournisseur:
- `ManualMobileMoneyGateway`: mode actuel
- `CinetPayGateway`: point d’entrée prévu pour API + webhook

### Ce qui ne change pas avec CinetPay
- Le modèle `Subscription`
- Le moteur d’activation (`confirm -> activate`)
- La page pricing et le catalogue des plans

### Ce qui sera ajouté
- Initialisation transaction CinetPay
- Signature webhook et vérification serveur-à-serveur
- Mapping automatique des statuts CinetPay vers `Payment`

## KPI marketing recommandés
- Taux de conversion visite pricing -> paiement soumis
- Taux de validation admin < 10 minutes
- Taux d’activation J+1
- Répartition des ventes par plan (objectif: Pro majoritaire)
- Rétention à 30 jours
