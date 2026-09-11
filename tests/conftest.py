# ABOUTME: Config compartilhada dos testes: ambiente antes de importar a app.
# ABOUTME: Nao usa SECRETS_DIR: cai no fallback de variaveis de ambiente.
import os

os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_NAME', 'todolist')
os.environ.setdefault('DB_USER', 'todolist')
os.environ.setdefault('DB_PASSWORD', 'todolist')
os.environ.setdefault('SESSION_KEY', 'test-session-key')
os.environ.setdefault('ADMIN_USER', 'admin')
os.environ.setdefault('ADMIN_PASSWORD', 'admin')
os.environ.setdefault('CLEANUP_TOKEN', 'test-cleanup-token')
