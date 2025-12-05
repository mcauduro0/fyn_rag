#!/bin/bash

# Script para atualizar o Frontend na Vercel com a URL do Backend DigitalOcean

echo "🚀 Atualizando Frontend Fyn RAG..."

# Verificar login Vercel
vercel whoami || { echo "❌ Por favor, faça login na Vercel com 'vercel login'"; exit 1; }

# Solicitar URL do Backend
echo "ℹ️  Acesse o dashboard do DigitalOcean App Platform e copie a URL do seu app (ex: https://fyn-rag-backend-xxxx.ondigitalocean.app)"
read -p "Cole a URL do Backend aqui: " BACKEND_URL

# Remover barra final se existir
BACKEND_URL=${BACKEND_URL%/}

echo "🔗 Configurando VITE_API_URL para: $BACKEND_URL"

# Deploy na Vercel
cd frontend
vercel --env VITE_API_URL=$BACKEND_URL --prod

echo "✅ Frontend atualizado com sucesso!"
