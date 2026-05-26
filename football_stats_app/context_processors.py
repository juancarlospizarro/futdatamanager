from django.utils import translation
import re


def clean_path(request):
    """
    Returns the request path without the language prefix.
    Example: /es/nonexistent/ → /nonexistent/
    """
    path = request.path
    current_language = translation.get_language()
    
    # Remove language prefix if it exists at the start of the path
    pattern = f'^/{current_language}/'
    clean_url = re.sub(pattern, '/', path)
    
    return {
        'clean_path': clean_url,
    }
