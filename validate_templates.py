
import os
import django
from django.conf import settings
from django.template import engines
from django.template.loader import get_template
from django.template.exceptions import TemplateSyntaxError

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.getcwd(), 'dashboard', 'templates')],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'dashboard',
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.humanize',
            'django.contrib.staticfiles',
        ]
    )
    django.setup()

def validate_templates():
    template_dir = os.path.join(os.getcwd(), 'dashboard', 'templates')
    has_errors = False
    
    print(f"Scanning templates in: {template_dir}")
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.getcwd())
                
                try:
                    # Try to load/compile the template
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    
                    # We manually compile to catch syntax errors
                    engines['django'].from_string(template_content)
                    
                    print(f"✅ Valid: {rel_path}")
                except TemplateSyntaxError as e:
                    print(f"❌ SYNTAX ERROR in {rel_path}: {e}")
                    has_errors = True
                except Exception as e:
                    print(f"⚠️  Error processing {rel_path}: {e}")
                    has_errors = True

    if has_errors:
        print("\nSUMMARY: Template errors found! detailed above.")
        exit(1)
    else:
        print("\nSUMMARY: All templates passed syntax check.")
        exit(0)

if __name__ == "__main__":
    validate_templates()
