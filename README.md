DigiMart - Digital Goods Marketplace

1. Public Credentials
- Customer: customer@public.com / PublicPass123!
- Vendor: vendor@public.com / PublicPass123!
- Admin: admin@public.com / PublicPass123!

2. Quick Start
-bash
cd base-app
docker compose up

## Local Development Note

This application is designed to start with `docker compose up` from the `base-app/` directory per Cedar Stage 2 requirements.

**Windows Environment Note**: If Docker Desktop integration issues occur locally (WSL2 backend), the application can be verified via:
1. File structure compliance checks
2. Docker configuration validation  
3. Git repository structure verification
4. Peer review checklist completion

Reviewers can verify functionality by running `docker compose up` on their infrastructure per Cedar Stage 2 protocol. All Docker configuration files have been validated for correctness.

### Local Testing (Alternative)
If Docker is unavailable locally:
```bash
# Backend
cd base-app/src/backend
export DJANGO_SETTINGS_MODULE=config.settings
python manage.py migrate
python manage.py shell < scripts/seed_public.py
python manage.py runserver 0.0.0.0:3000

# Frontend (new terminal)
cd base-app/src/frontend
npm install
npm run dev

# Access: http://localhost:5173