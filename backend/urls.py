"""
URL configuration for backend project.
"""
import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import FileResponse, Http404

def serve_frontend_file(request, filepath='index.html'):
    if not filepath or filepath == '/':
        filepath = 'index.html'
    
    filepath = filepath.lstrip('/')
    frontend_dir = os.path.abspath(os.path.join(settings.BASE_DIR, 'frontend'))
    full_path = os.path.abspath(os.path.join(frontend_dir, filepath))
    
    # Directory traversal check
    if not full_path.startswith(frontend_dir):
        raise Http404("Forbidden")
        
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(open(full_path, 'rb'))
        
    raise Http404(f"File not found: {filepath}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/healthcare/', include('healthcare.urls')),
    path('api/ai/', include('ai_assistant.urls')),
    path('', serve_frontend_file, {'filepath': 'index.html'}),
    re_path(r'^(?P<filepath>(?:css|js|pages|assets|images)/.+)$', serve_frontend_file),
    re_path(r'^(?P<filepath>[a-zA-Z0-9_\-]+\.html)$', serve_frontend_file),
]

