# -*- coding: utf-8 -*-
"""
Dictionnaire de traduction global — FTTH AirPON ML
Toutes les valeurs fixes traduites en FR / EN / AR
"""

GLOBAL_TR = {
    # Saisons
    'Saison_Seche'         : {'fr': 'Saison Sèche',                   'en': 'Dry Season',            'ar': 'الموسم الجاف'},
    'Saison_Pluies'        : {'fr': 'Saison des Pluies',              'en': 'Rainy Season',           'ar': 'موسم الأمطار'},
    'Intersaison'          : {'fr': 'Intersaison',                    'en': 'Inter-Season',           'ar': 'الموسم الانتقالي'},
    # Localisations
    "N'Djamena_Centre"     : {'fr': "N'Djamena Centre",               'en': "N'Djamena Center",       'ar': 'إنجامينا المركز'},
    "N'Djamena_Sud"        : {'fr': "N'Djamena Sud",                  'en': "N'Djamena South",        'ar': 'إنجامينا الجنوب'},
    "N'Djamena_Nord"       : {'fr': "N'Djamena Nord",                 'en': "N'Djamena North",        'ar': 'إنجامينا الشمال'},
    'Moundou'              : {'fr': 'Moundou',                        'en': 'Moundou',                'ar': 'موندو'},
    'Sarh'                 : {'fr': 'Sarh',                           'en': 'Sarh',                   'ar': 'سارح'},
    'Abéché'               : {'fr': 'Abéché',                         'en': 'Abeche',                 'ar': 'أبشه'},
    'Kélo'                 : {'fr': 'Kélo',                           'en': 'Kelo',                   'ar': 'كيلو'},
    'Doba'                 : {'fr': 'Doba',                           'en': 'Doba',                   'ar': 'دوبا'},
    'Bongor'               : {'fr': 'Bongor',                         'en': 'Bongor',                 'ar': 'بونغور'},
    # Types de zone
    'Urbaine_Dense'        : {'fr': 'Urbaine Dense',                  'en': 'Dense Urban',            'ar': 'حضرية كثيفة'},
    'Urbaine_Moyenne'      : {'fr': 'Urbaine Moyenne',                'en': 'Medium Urban',           'ar': 'حضرية متوسطة'},
    'Peri_Urbaine'         : {'fr': 'Péri-Urbaine',                   'en': 'Peri-Urban',             'ar': 'شبه حضرية'},
    'Péri_Urbaine'         : {'fr': 'Péri-Urbaine',                   'en': 'Peri-Urban',             'ar': 'شبه حضرية'},
    'Rurale'               : {'fr': 'Rurale',                         'en': 'Rural',                  'ar': 'ريفية'},
    # Terrains
    'Plat'                 : {'fr': 'Plat',                           'en': 'Flat',                   'ar': 'مستوٍ'},
    'Accidenté'            : {'fr': 'Accidenté',                      'en': 'Rugged',                 'ar': 'وعر'},
    'Inondable'            : {'fr': 'Inondable',                      'en': 'Flood-prone',            'ar': 'عرضة للفيضانات'},
    'Sableux'              : {'fr': 'Sableux',                        'en': 'Sandy',                  'ar': 'رملي'},
    # Oui / Non
    'Oui'                  : {'fr': 'Oui',                            'en': 'Yes',                    'ar': 'نعم'},
    'Non'                  : {'fr': 'Non',                            'en': 'No',                     'ar': 'لا'},
    # Équipements
    'OLT'                  : {'fr': 'OLT',                            'en': 'OLT',                    'ar': 'OLT'},
    'ONT'                  : {'fr': 'ONT',                            'en': 'ONT',                    'ar': 'ONT'},
    'Splitter'             : {'fr': 'Diviseur (Splitter)',            'en': 'Splitter',               'ar': 'مقسم الإشارة'},
    'Cable_Fibre'          : {'fr': 'Câble Fibre Optique',            'en': 'Fiber Optic Cable',      'ar': 'كابل الألياف البصرية'},
    'Connecteur'           : {'fr': 'Connecteur',                     'en': 'Connector',              'ar': 'موصل'},
    'Boitier_Etanche'      : {'fr': 'Boîtier Étanche',               'en': 'Waterproof Box',         'ar': 'علبة مقاومة للماء'},
    'Antenne_AirPON'       : {'fr': 'Antenne AirPON',                'en': 'AirPON Antenna',         'ar': 'هوائي AirPON'},
    # Types de panne
    'Rupture_Cable'        : {'fr': 'Rupture de Câble',               'en': 'Cable Break',            'ar': 'انقطاع الكابل'},
    'Perte_Signal'         : {'fr': 'Perte de Signal',                'en': 'Signal Loss',            'ar': 'فقدان الإشارة'},
    'Surtension'           : {'fr': 'Surtension',                     'en': 'Overvoltage',            'ar': 'تجاوز الجهد'},
    'Corrosion'            : {'fr': 'Corrosion',                      'en': 'Corrosion',              'ar': 'التآكل'},
    'Obstruction_Physique' : {'fr': 'Obstruction Physique',           'en': 'Physical Obstruction',   'ar': 'عائق جسدي'},
    'Defaut_Connecteur'    : {'fr': 'Défaut Connecteur',              'en': 'Connector Fault',        'ar': 'عطل الموصل'},
    'Panne_OLT'            : {'fr': 'Panne OLT',                      'en': 'OLT Failure',            'ar': 'عطل OLT'},
    'Degradation_Lente'    : {'fr': 'Dégradation Lente',              'en': 'Slow Degradation',       'ar': 'تدهور تدريجي'},
    # Sévérité
    'Faible'               : {'fr': 'Faible',                         'en': 'Low',                    'ar': 'منخفضة'},
    'Moyenne'              : {'fr': 'Moyenne',                        'en': 'Medium',                 'ar': 'متوسطة'},
    'Élevée'               : {'fr': 'Élevée',                         'en': 'High',                   'ar': 'عالية'},
    'Critique'             : {'fr': 'Critique',                       'en': 'Critical',               'ar': 'حرجة'},
    # SLA
    'Respecté'             : {'fr': 'Respecté',                       'en': 'Respected',              'ar': 'محترم'},
    'Non Respecté'         : {'fr': 'Non Respecté',                   'en': 'Not Respected',          'ar': 'غير محترم'},
    # Résultats Déploiement
    'Réussi'               : {'fr': 'Réussi',                         'en': 'Successful',             'ar': 'ناجح'},
    'En_retard'            : {'fr': 'En Retard',                      'en': 'Delayed',                'ar': 'متأخر'},
    'Échoué'               : {'fr': 'Échoué',                         'en': 'Failed',                 'ar': 'فاشل'},
    # Résultats Maintenance
    'Préventive'           : {'fr': 'Préventive',                     'en': 'Preventive',             'ar': 'وقائي'},
    'Corrective'           : {'fr': 'Corrective',                     'en': 'Corrective',             'ar': 'تصحيحي'},
    'Urgente'              : {'fr': 'Urgente',                        'en': 'Urgent',                 'ar': 'عاجل'},
    # Unités de temps
    'jours'                : {'fr': 'jours',                          'en': 'days',                   'ar': 'أيام'},
    'heures'               : {'fr': 'heures',                         'en': 'hours',                  'ar': 'ساعات'},
    'mois'                 : {'fr': 'mois',                           'en': 'months',                 'ar': 'أشهر'},
    'ans'                  : {'fr': 'ans',                            'en': 'years',                  'ar': 'سنوات'},
}


def tr(key, lang):
    """Traduit une valeur selon la langue (fr, en, ar)."""
    return GLOBAL_TR.get(key, {}).get(lang, key)


def tr_list(lst, lang):
    """Traduit une liste de valeurs selon la langue."""
    return [tr(v, lang) for v in lst]


def reverse_tr(val_tr, lang):
    """Retrouve la clé originale à partir d'une valeur traduite."""
    for k, v in GLOBAL_TR.items():
        if v.get(lang) == val_tr or v.get('fr') == val_tr:
            return k
    return val_tr
