.PHONY: install install-backend install-frontend run-backend run-frontend test-backend test help

help:
	@echo "make install           - backend + frontend deps"
	@echo "make install-backend   - pip install -r backend/requirements.txt"
	@echo "make install-frontend  - npm install in frontend/"
	@echo "make run-backend       - FastAPI :8000 (cwd backend/)"
	@echo "make run-frontend      - Vite :5173"
	@echo "make test / test-backend - pytest in backend/"

install: install-backend install-frontend

install-backend:
	cd backend && python -m pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

run-backend:
	cd backend && python -m uvicorn aiuthor.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

test-backend:
	cd backend && python -m pytest tests/ -q

test: test-backend
