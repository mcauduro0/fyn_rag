#!/bin/bash

# Script de Deploy Local para Fyn RAG System
# Execute este script na sua máquina local após instalar Railway e Vercel CLI

echo "🚀 Iniciando Deploy do Fyn RAG System..."

# 1. Verificar autenticação
echo "🔍 Verificando autenticação..."
railway whoami || { echo "❌ Por favor, faça login no Railway com 'railway login'"; exit 1; }
vercel whoami || { echo "❌ Por favor, faça login na Vercel com 'vercel login'"; exit 1; }

# 2. Deploy Backend (Railway)
echo "🚂 Fazendo deploy do Backend no Railway..."
railway init
railway up --detach

# Obter URL do Backend (assumindo que o usuário configurou o domínio)
echo "⚠️  Por favor, certifique-se de gerar um domínio público no Railway (Settings > Networking)"
read -p "Cole a URL do Backend Railway aqui (ex: https://fyn-rag.up.railway.app): " BACKEND_URL

# 3. Deploy Frontend (Vercel)
echo "▲ Fazendo deploy do Frontend na Vercel..."
cd frontend
vercel --env VITE_API_URL=$BACKEND_URL --prod

echo "✅ Deploy Completo! Acesse a URL fornecida pela Vercel acima."
