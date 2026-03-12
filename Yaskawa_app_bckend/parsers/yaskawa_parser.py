# ============================================================
# Yaskawa_app_bckend/parsers/yaskawa_parser.py
# ============================================================

import re

class YaskawaParser:
    """
    Parse les model codes Yaskawa et extrait les attributs techniques.
    Optimisé pour regrouper les protocoles et encodeurs par familles.
    """

    # ── Tables de décodage communes SGD (Servopacks) ─────────
    POWER_MAP_SGD = {
        # 200V Three-phase
        'R70': 0.05,  'R90': 0.1,   '1R6': 0.2,   '2R8': 0.4,
        '3R8': 0.5,   '5R5': 0.75,  '7R6': 1.0,   '120': 1.5,
        '180': 2.0,   '200': 3.0,   '330': 5.0,   '470': 6.0,
        '550': 7.5,   '590': 11.0,  '780': 15.0,
        # 400V Three-phase
        '1R9': 0.5,   '3R5': 1.0,   '5R4': 1.5,   '8R4': 2.0,
        '170': 5.0,   '210': 6.0,   '260': 7.5,   '280': 11.0,
        '370': 15.0,
    }

    VOLTAGE_MAP = {
        'A': '200V',
        'D': '400V',
        'F': '100V',
    }

    # --- REGROUPEMENT PROTOCOLES (Ordre logique) ---
    PROTOCOL_MAP_SGD = {
        # Famille Analogique / Impulsions
        '00': 'Analog voltage/pulse train reference',
        #'01': 'Analog voltage/pulse train reference', 

        # Famille MECHATROLINK
        '10': 'MECHATROLINK-II',
        '20': 'MECHATROLINK-III',
        '30': 'MECHATROLINK-III',
        '40': 'MECHATROLINK-4/III',

        # Famille Ethernet / Fieldbus
        'A0': 'EtherCAT',
        'C0': 'PROFINET',
        'M0': 'Sigma-7Siec',
        'MA': 'Bus Connection',
        #E0/
    }

    OPTION_MAP_SGD = {
        'None': 'Without options',
        '0000': 'Without options',
        '0001': 'Rack-mounted',
        '0002': 'Varnished',
        '0008': 'Single-phase 200VAC input',
        '0020': 'No dynamic brake',
    }

    SPEC_MAP_SGD = {
        'B':    'BTO specification',
        'None': 'Standard',
        '':     'Standard',
    }

    # ── Tables de décodage SGM (Moteurs) ─────────────────────
    POWER_MAP_SGM = {
        'A5': 0.05,  '01': 0.1,   'C2': 0.15,  '02': 0.2,
        '04': 0.4,   '06': 0.6,   '08': 0.75,  '09': 0.85,
        '10': 1.0,   '13': 1.3,   '15': 1.5,   '20': 2.0,
        '25': 2.5,   '30': 3.0,   '40': 4.0,   '44': 4.4,
        '50': 5.0,   '55': 5.5,   '70': 7.0,   '75': 7.5,
    }

    # --- REGROUPEMENT ENCODEURS (Ordre logique par bits) ---
    ENCODER_MAP_SGM = {
        # Famille Absolute
        'A': 'Absolute 13-bit',
        'C': 'Absolute 17-bit',
        '3': 'Absolute 20-bit',
        '7': 'Absolute 24-bit',
        '6': 'Absolute 24-bit (Batteryless)',
        'U': 'Absolute 26-bit',
        'W': 'Absolute 26-bit (Batteryless)',
        
        # Famille Incremental
        'F': 'Incremental 24-bit',
    }

    SPEC_MAP_SGM = {
        '1': 'Sans option',
        'C': 'With holding brake (24VDC)',
        'E': 'With oil seal + holding brake (24VDC)',
        '2': 'With oil seal',
    }

    # ── Logique de Parsing ───────────────────────────────────

    @classmethod
    def parse(cls, model_code: str) -> dict:
        if not model_code: return {}
        code = model_code.upper().strip()

        if code.startswith('SGDXS') or code.startswith('SGD7'):
            return cls._parse_sgd(code)
        elif code.startswith('SGMXJ') or code.startswith('SGM7') or code.startswith('SGM'):
            return cls._parse_sgm(code)
        elif code.startswith('SGL'):
            return cls._parse_sgl(code)
        return {}

    @classmethod
    def _parse_sgd(cls, code: str) -> dict:
        result = cls._get_empty_result()
        parts = code.split('-')
        result['series'] = parts[0]

        if len(parts) < 2: return result
        payload = parts[1]

        if len(payload) >= 3:
            result['power_kw'] = cls.POWER_MAP_SGD.get(payload[:3])
        if len(payload) >= 4:
            result['voltage'] = cls.VOLTAGE_MAP.get(payload[3], '')
        if len(payload) >= 6:
            result['protocol'] = cls.PROTOCOL_MAP_SGD.get(payload[4:6], 'Other')
        if len(payload) >= 11:
            result['option'] = cls.OPTION_MAP_SGD.get(payload[7:11], 'Custom/Other')
        if len(payload) >= 14:
            result['specification'] = cls.SPEC_MAP_SGD.get(payload[13], 'Standard')

        if 'OSA' in code:
            result['option'] = f"{result['option']} / Safety Option".strip()

        return result

    @classmethod
    def _parse_sgm(cls, code: str) -> dict:
        result = cls._get_empty_result()
        parts = code.split('-')
        result['series'] = parts[0]

        if len(parts) < 2: return result
        payload = parts[1]

        if len(payload) >= 2:
            result['power_kw'] = cls.POWER_MAP_SGM.get(payload[:2])
        if len(payload) >= 3:
            result['voltage'] = cls.VOLTAGE_MAP.get(payload[2], '')
        if len(payload) >= 4:
            result['encoder_type'] = cls.ENCODER_MAP_SGM.get(payload[3], 'Other')
        if len(payload) >= 7:
            spec_code = payload[6]
            result['specification'] = cls.SPEC_MAP_SGM.get(spec_code, spec_code)
            result['brake'] = spec_code in ('C', 'E')

        return result

    @classmethod
    def _parse_sgl(cls, code: str) -> dict:
        result = cls._get_empty_result()
        parts = code.split('-')
        result['series'] = parts[0]
        if len(parts) < 2: return result
        payload = parts[1]
        for i, char in enumerate(payload):
            if char in cls.VOLTAGE_MAP and i > 0:
                result['voltage'] = cls.VOLTAGE_MAP[char]
                break
        return result

    @staticmethod
    def _get_empty_result():
        return {
            'series': '', 
            'power_kw': None, 
            'voltage': '', 
            'protocol': '',
            'encoder_type': '', 
            'option': '', 
            'specification': '', 
            'brake': False,
        }