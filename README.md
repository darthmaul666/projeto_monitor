# 🚀 Monitor de Preços - Script 1 (Identificador)

Este projeto é a "Inteligência" de um monitor de preços. Ele foi desenvolvido para quebrar a cabeça sozinho e encontrar onde as informações de produtos (Preço, Nome, EAN) estão escondidas no código de qualquer site.

## 🧠 Como funciona?
O script utiliza uma técnica de **Busca Profunda em JSON**. Ele varre todos os scripts de uma página HTML salva localmente e mapeia os "endereços" (caminhos) dos dados.

## 🛠️ Tecnologias
- **Python 3**
- **JSON & Regex** (Para extração de dados)
- **Git** (Controle de versão)

## 📖 Como usar
1. Salve o HTML do produto desejado na pasta `html_alvos/`.
2. Rode o identificador: `python3 identificador_padrao.py`.
3. Digite o preço e o nome que você está vendo na tela.
4. O script aprenderá o padrão e salvará no arquivo `database_sites.json`.

## 📂 O "Cérebro" (database_sites.json)
Este arquivo armazena o DNA de cada site mapeado, permitindo que o **Script 2 (Extrator)** funcione de forma automática e instantânea para milhares de produtos.
