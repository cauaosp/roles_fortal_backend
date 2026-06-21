#!/bin/sh

echo "Executando fetch dos artigos..."
python fetch_articles.py

echo "Fetch sendo precessado... Subindo site em 8s..."
sleep 8

echo "Subindo site..."
exec python site.py
