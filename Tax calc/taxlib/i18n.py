import json
import os
from . import config

_LANG = 'en'

def get_language():
    global _LANG
    try:
        _LANG = config.get('language') or 'en'
    except Exception:
        _LANG = 'en'
    return _LANG

def set_language(lang):
    global _LANG
    _LANG = lang
    try:
        config.set('language', lang)
    except Exception:
        pass

_TRANSLATIONS = {
    'en': {
        'export_pdf': 'Export PDF',
        'export_xlsx': 'Export Excel',
    },
    'hi': {
        'export_pdf': 'पीडीएफ़ निर्यात',
        'export_xlsx': 'एक्सेल निर्यात',
    }
}

def t(key):
    lang = get_language()
    return _TRANSLATIONS.get(lang, {}).get(key, key)

"""Internationalization scaffolding (very small) for TaxFlow.

This module provides a minimal translate() function and language selection.
"""
from typing import Dict
from .config import get, set

_RESOURCES: Dict[str, Dict[str, str]] = {
    'en': {
        'chart_type': 'Chart Type:',
        'export_pdf': 'Export PDF',
        'export_excel': 'Export Excel',
        'calculate_tax': 'Calculate Tax'
    },
    'hi': {
        'chart_type': 'चार्ट प्रकार:',
        'export_pdf': 'पीडीएफ निर्यात',
        'export_excel': 'एक्सेल निर्यात',
        'calculate_tax': 'कर गणना'
    }
}


def get_language():
    return get('language', 'en')


def set_language(lang: str):
    set('language', lang)


def t(key: str) -> str:
    lang = get_language()
    return _RESOURCES.get(lang, _RESOURCES['en']).get(key, key)
