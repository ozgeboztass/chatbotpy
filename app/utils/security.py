import re
import bleach
from flask import request, abort, current_app
from functools import wraps
import html

def sanitize_input(text):
    """
    Metinleri SQL Injection ve XSS'e karşı temizler.
    
    Args:
        text (str): Temizlenecek metin
        
    Returns:
        str: Temizlenmiş metin
    """
    if text is None:
        return None
    
    # HTML karakterlerini escape et
    text = html.escape(text)
    
    # SQL Injection için yaygın kalıpları temizle
    sql_patterns = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*INSERT\s+INTO',
        r';\s*UPDATE\s+',
        r'--',
        r'/\*.*\*/',
        r'UNION\s+SELECT',
        r'EXEC\s+\w+',
        r'xp_\w+'
    ]
    
    for pattern in sql_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text

def sanitize_html(html_content, allowed_tags=None, allowed_attrs=None):
    """
    HTML içeriğini XSS'e karşı temizler.
    
    Args:
        html_content (str): Temizlenecek HTML içeriği
        allowed_tags (list): İzin verilen HTML etiketleri
        allowed_attrs (dict): İzin verilen HTML özellikleri
        
    Returns:
        str: Temizlenmiş HTML içeriği
    """
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'code', 'pre']
    
    if allowed_attrs is None:
        allowed_attrs = {
            'a': ['href', 'title', 'target'],
            '*': ['class']
        }
    
    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def validate_form_data():
    """
    Form verilerini doğrular ve temizler.
    Flask route decorator olarak kullanılır.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # POST verilerini doğrula
            if request.method == 'POST':
                form_data = request.form.to_dict()
                
                # Tüm form verilerini temizle
                for key, value in form_data.items():
                    # Özel anahtarlar (örn. csrf_token gibi) için atla
                    if key == 'csrf_token':
                        continue
                    
                    # SQL Injection koruması için temizle
                    cleaned_value = sanitize_input(value)
                    
                    # Eğer değer değiştiyse, muhtemel bir saldırı olabilir
                    if cleaned_value != value:
                        current_app.logger.warning(f"Potansiyel SQL Injection denemesi: {value}")
                        abort(400)  # Bad Request
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_content_security(content_type=None):
    """
    İçerik türünü kontrol eder ve güvenlik politikalarını uygular.
    
    Args:
        content_type (str): İçerik türü (örn. 'application/json')
        
    Returns:
        decorator: Flask route decorator'ı
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # İçerik türünü kontrol et (eğer belirtilmişse)
            if content_type and request.content_type != content_type:
                abort(415)  # Unsupported Media Type
            
            response = f(*args, **kwargs)
            
            # Content Security Policy (CSP) ekle
            if hasattr(response, 'headers'):
                response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net;"
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-Frame-Options'] = 'DENY'
                response.headers['X-XSS-Protection'] = '1; mode=block'
            
            return response
        return decorated_function
    return decorator 