import json
import re
import os
import glob

# Configurações de cores para o terminal (estilo hacker)
G = '\033[92m' # Verde
Y = '\033[93m' # Amarelo
R = '\033[91m' # Vermelho
C = '\033[0m'  # Reset

print(f"{G}🚀 Monitor de Preços V5.0 - Inteligência Integrada{C}")

def gerar_possibilidades_preco(valor_input):
    base = str(valor_input).replace(',', '.')
    nums = re.sub(r'[^\d]', '', base)
    possibilidades = [nums]
    try:
        f = float(base)
        possibilidades.extend([str(f), str(int(f)), f"{f:.2f}"])
    except: pass
    return list(set(possibilidades))

def navegar_caminho(obj, caminho_str):
    """Extrai valor real de um caminho mapeado"""
    try:
        chaves = re.findall(r"['\"](.*?)['\"]", caminho_str)
        temp = obj
        for k in chaves:
            temp = temp[int(k)] if isinstance(temp, list) else temp[k]
        # Se o resultado for um dicionário (como na Pacheco), tentamos pegar o 'productName' ou 'name'
        if isinstance(temp, dict):
            for n in ['productName', 'name', 'pageTitle']:
                if n in temp: return temp[n]
        return temp
    except: return "N/A"

def achar_caminho_recursivo(obj, alvos, caminho=""):
    v_str = str(obj).strip()
    if v_str in alvos and v_str != "": return caminho
    if isinstance(obj, dict):
        for k, v in obj.items():
            novo = f"{caminho}['{k}']" if caminho else f"['{k}']"
            res = achar_caminho_recursivo(v, alvos, novo)
            if res: return res
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            novo = f"{caminho}[{i}]"
            res = achar_caminho_recursivo(v, alvos, novo)
            if res: return res
    return None

def processar():
    db_file = "database_sites.json"
    db = {}
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)

    arquivos = glob.glob("html_alvos/*.html")
    
    for caminho_arq in arquivos:
        nome_arq = os.path.basename(caminho_arq)
        print(f"\n{Y}--- Analisando: {nome_arq} ---{C}")
        
        with open(caminho_arq, 'r', encoding='utf-8') as f:
            html = f.read()

        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        dados_json = []
        for s in scripts:
            matches = re.findall(r'(\{.*\}|\[.*\])', s.strip(), re.DOTALL)
            for m in matches:
                try:
                    js = m
                    if '=' in js[:20]: js = js.split('=', 1)[1].strip().rstrip(';')
                    carregado = json.loads(js)
                    if isinstance(carregado, list): dados_json.extend(carregado)
                    else: dados_json.append(carregado)
                except: continue

        # Identifica se o site já existe no DB
        site_key = None
        for k in db:
            if k.lower() in nome_arq.lower():
                site_key = k
                break

        # MODO EXTRATOR (Se já conhece o site)
        if site_key:
            print(f"{G}✅ Site reconhecido: {site_key}{C}")
            caminhos = db[site_key]["caminhos"]
            chave_p = "preco_unitario" if "preco_unitario" in caminhos else "preco"
            chave_n = "name" if "name" in caminhos else "nome"
            
            final_p, final_n = "N/A", "N/A"
            for d in dados_json:
                p = navegar_caminho(d, caminhos[chave_p])
                if p != "N/A":
                    final_p = p
                    final_n = navegar_caminho(d, caminhos.get(chave_n, ""))
                    break
            print(f"💰 {G}Preço: R$ {final_p}{C} | 📦 Produto: {final_n}")

        # MODO IDENTIFICADOR (Se o site é novo)
        else:
            print(f"{R}❓ Site novo! Iniciando mapeamento...{C}")
            p_input = input("💰 Digite o preço que está vendo na tela: ")
            possiveis = gerar_possibilidades_preco(p_input)
            
            for d in dados_json:
                c_p = achar_caminho_recursivo(d, possiveis)
                if c_p:
                    nome_s = input(f"🌍 Nome para este site ({nome_arq}): ") or nome_arq
                    db[nome_s] = {
                        "arquitetura": "Busca_Profunda",
                        "caminhos": {"preco_unitario": c_p, "name": achar_caminho_recursivo(d, [input("📦 Nome do produto para mapear: ")])}
                    }
                    with open(db_file, 'w', encoding='utf-8') as f:
                        json.dump(db, f, indent=4)
                    print(f"{G}✅ {nome_s} salvo no banco!{C}")
                    break

if __name__ == "__main__":
    processar()
