#!/usr/bin/env python3
"""
Script pour synchroniser les fichiers statiques vers l'API Vercel
"""

import os
import mimetypes

def read_file_content(file_path):
    """Lit le contenu d'un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")
        return None

def get_mime_type(file_path):
    """Détermine le type MIME d'un fichier"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def generate_static_files_dict():
    """Génère le dictionnaire des fichiers statiques"""
    static_files = {}
    
    # Fichiers HTML
    html_files = [
        ('/static/index.html', 'static/index.html'),
        ('/static/dashboard.html', 'static/dashboard.html'),
    ]
    
    # Fichiers CSS
    css_files = [
        ('/static/css/styles.css', 'static/css/styles.css'),
        ('/static/style.css', 'static/style.css'),
    ]
    
    # Fichiers JavaScript
    js_files = [
        ('/static/js/config.js', 'static/js/config.js'),
        ('/static/js/auth.js', 'static/js/auth.js'),
        ('/static/js/dashboard.js', 'static/js/dashboard.js'),
        ('/static/js/calendar.js', 'static/js/calendar.js'),
        ('/static/js/admin.js', 'static/js/admin.js'),
        ('/static/js/sickness.js', 'static/js/sickness.js'),
        ('/static/js/utils.js', 'static/js/utils.js'),
        ('/static/js/main.js', 'static/js/main.js'),
    ]
    
    all_files = html_files + css_files + js_files
    
    for url_path, file_path in all_files:
        content = read_file_content(file_path)
        if content:
            static_files[url_path] = {
                "content": content,
                "mime_type": get_mime_type(file_path)
            }
            print(f"✅ Ajouté: {file_path}")
        else:
            print(f"❌ Erreur: {file_path}")
    
    return static_files

def generate_static_files_py():
    """Génère le fichier static_files.py avec tous les fichiers"""
    static_files = generate_static_files_dict()
    
    # Générer le contenu du fichier
    content = '''import mimetypes

def get_mime_type(file_path):
    """Détermine le type MIME d'un fichier"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def get_static_content(file_path):
    """Retourne le contenu des fichiers statiques embarqués"""
    static_files = {
'''
    
    # Ajouter chaque fichier
    for url_path, file_data in static_files.items():
        content += f"        '{url_path}': {{\n"
        content += f"            'content': '''{file_data['content']}''',\n"
        content += f"            'mime_type': '{file_data['mime_type']}'\n"
        content += f"        }},\n"
    
    content += '''    }
    
    return static_files.get(file_path, None)
'''
    
    # Écrire le fichier
    with open('api/static_files.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fichier api/static_files.py généré avec {len(static_files)} fichiers")

if __name__ == "__main__":
    print("🔄 Synchronisation des fichiers statiques...")
    generate_static_files_py()
    print("✅ Synchronisation terminée !") 