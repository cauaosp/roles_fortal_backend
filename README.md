# Backend do Rolê Fortal 🌊

> repositório responsável pelas raspagens dos jornais, processamento e armazenamento dos artigos.

Centralizador de notícias para se manter atualizado sobre cultura, lazer e acontecimentos de Fortaleza e Ceará com os principais jornais do estado.

<img width="400" alt="role-fortal" src="https://github.com/user-attachments/assets/423b83d6-394b-4785-ad53-acbc1aa6f5e2" />

🌐 url pública: https://roles-fortal-frontend.cauaosp20.workers.dev/

---

## 🖧 Repositórios
- Infra: https://github.com/cauaosp/roles_fortal_infra
- Front: https://github.com/cauaosp/roles_fortal_frontend
- Back: https://github.com/cauaosp/roles_fortal_backend

## 🏗️ Stacks

💻 Backend: `Python` • `Flask` • `SQLAlchemy`

🎨 Frontend: `Vite` • `TypeScript` • `React`

🗄️ Banco de Dados: `Supabase` • `PostgreSQL`

☸️ Infra: `Docker` • `Kubernetes` • `Minikube`

📡 Deploy: `Cloudflare Pages` • `Github Pages`

## 🔄 Fluxo de Dados

1) ⏰ GitHub Actions (cron a cada 12h)
2) 🕷️ Scrapers (Python + aiohttp)
3) 🧹 Normalização (dataclass + helpers)
4) 🔗 SQLAlchemy ORM (inserção no banco)
5) 🗄️ Supabase (PostgreSQL)
6) 📡 Data API (REST)
7) 🎨 Frontend (React + supabase-js)

## 📰 Jornais

Os jornais foram escolhidos com base na regionalidade, preciso de notícias que sejam sobre fortal.

- O POVO
- DIÁRIO DO NORDESTE
- O ESTADO CE
- VERDES MARES
- CEARÁ AGORA
- TRIBUNAL DE CONTAS DO CEARÁ
- TERRA DA LUZ
- JORNAL JANGADEIRO

## 📌 Próximas Funcionalidades

-  Buscador por texto
-  Ordenação das notícias
-  Algoritmo de categorização da notícia
-  Adicionar banco de cacheamento

###### ☸️ Desenvolvido por [Cauã Paiva](https://github.com/cauaosp)
