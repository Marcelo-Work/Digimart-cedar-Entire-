#!/bin/bash
PASS=0
FAIL=0

# Function to check and count
check() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
        ((PASS++))
    else
        echo "❌ $2"
        ((FAIL++))
    fi
}

# File existence checks
[ -f "base-app/docker-compose.yml" ]; check $? "docker-compose.yml exists"
[ -f "base-app/src/backend/Dockerfile" ]; check $? "Backend Dockerfile exists"
[ -f "base-app/src/frontend/Dockerfile.ecs" ]; check $? "Frontend Dockerfile.ecs exists"
[ -f "evaluation/attack_scope.json" ]; check $? "attack_scope.json exists"
[ -f "CHECKLIST_STAGE_2.md" ]; check $? "CHECKLIST_STAGE_2.md exists"

# Content checks
grep -q "condition: service_healthy" base-app/docker-compose.yml; check $? "docker-compose.yml: service_healthy"
grep -q "proxy_pass http://localhost:3000" base-app/deployment/nginx/nginx.ecs.conf; check $? "nginx.ecs.conf: localhost"
grep -q '"@playwright/test": "1.58.2"' base-app/src/frontend/package.json; check $? "package.json: Playwright 1.58.2"
grep -q '"is_allowed": true' evaluation/attack_scope.json; check $? "attack_scope.json: is_allowed=true"

# Executable checks
[ -x "build-and-push-ecs.sh" ]; check $? "build-and-push-ecs.sh executable"
[ -x "base-app/src/backend/entrypoint.sh" ]; check $? "entrypoint.sh executable"

# Git checks
cd reference-solutions
[ -d ".git" ]; check $? "reference-solutions/.git exists"
branch_count=$(git branch 2>/dev/null | wc -l)
[ "$branch_count" -eq 11 ]; check $? "reference-solutions has 11 branches"
cd ..

echo ""
echo "=========================================="
echo "  RESULTS: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED - Ready to submit!"
    exit 0
else
    echo "⚠️ Fix $FAIL issue(s) before submitting"
    exit 1
fi