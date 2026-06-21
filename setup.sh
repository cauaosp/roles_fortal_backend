#!/bin/sh

echo "Executando fetch dos artigos..."
python fetch_articles.py

echo "Fetch processado. Subindo site..."
exec python site.py
