import json, re, os, glob
from bs4 import BeautifulSoup

# Cores para o terminal
G, Y, R, C = '\033[92m', '\033[93m', '\033[91m', '\033[0m'
print(f"{G}🛠️ Script 1 v2.2 - Identificador Universal (Full Robustness){C}")

def limpar_texto(t): return " ".join(str(t).split()).strip()

def gerar_possibilidades_preco(v):
    b = str(v).replace(',', '.')
    n = re.sub(r'[^\d]', '', b)
    return list(set([n, b, b.replace('.', ',')]))

def achar_caminho_json(obj, alvos, caminho=""):
    v_str = limpar_texto(obj)
    if v_str in alvos and v_str != "": return caminho
    if isinstance(obj, dict):
        for k, v in obj.items():
            novo = f"{caminho}['{k}']" if caminho else f"['{k}']"
            res = achar_caminho_json(v, alvos, novo)
            if res: return res
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            res = achar_caminho_json(v, alvos, f"{caminho}[{i}]")
            if res: return res
    return None

def achar_seletor_html(soup, alvo):
    """Busca no texto e nos atributos das tags (data-price, value, etc)"""
    alvo_num = re.sub(r'[^\d]', '', str(alvo))
    if not alvo_num: return None

    # 1. Tenta buscar no texto visível
    for tag in soup.find_all(string=True):
        t_limpo = re.sub(r'[^\d]', '', limpar_texto(tag))
        if alvo_num == t_limpo and len(t_limpo) > 0:
            el = tag.parent
            while el and el.name != '[document]':
                if el.get('id'): return f"#{el.get('id')}"
                if el.get('class'): return f"{el.name}.{'.'.join(el.get('class'))}"
                el = el.parent
            return tag.parent.name

    # 2. Tenta buscar dentro de ATRIBUTOS (Caso a Indiana esconda o preço)
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            val_attr = str(tag.get(attr))
            if alvo_num == re.sub(r'[^\d]', '', val_attr):
                if tag.get('id'): return f"#{tag.get('id')}"
                elif tag.get('class'): return f"{tag.name}.{'.'.join(tag.get('class'))}"
                return tag.name
    return None

def identificar():
    db_file, db = "database_sites.json", {}
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = {}

    for caminho_arq in glob.glob("html_alvos/*.html"):
        nome_arq = os.path.basename(caminho_arq)
        print(f"\n{Y}🔍 Analisando: {nome_arq}{C}")
        with open(caminho_arq, 'r', encoding='utf-8') as f:
            html = f.read()
            if len(html) < 500: continue

        soup = BeautifulSoup(html, 'html.parser')
        p_alvo, n_alvo = input("💰 Preço: "), input("📦 Nome: ")
        mapa, achou_json = {"arquitetura": None, "caminhos": {}}, False

        # Busca JSON
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for s in scripts:
            for m in re.findall(r'(\{.*\}|\[.*\])', s.strip(), re.DOTALL):
                try:
                    js = m
                    if '=' in js[:20]: js = js.split('=', 1)[1].strip().rstrip(';')
                    dados = json.loads(js)
                    if isinstance(dados, list): dados = dados[0]
                    path_p = achar_caminho_json(dados, gerar_possibilidades_preco(p_alvo))
                    if path_p:
                        mapa["arquitetura"], achou_json = "JSON", True
                        mapa["caminhos"] = {"preco": path_p, "nome": achar_caminho_json(dados, [n_alvo])}
                        break
                except: continue
            if achou_json: break

        # Busca HTML (Modo Robusto)
        if not achou_json:
            print(f"{Y}⚠️ JSON não detectado. Tentando HTML Selector...{C}")
            sel_p, sel_n = achar_seletor_html(soup, p_alvo), achar_seletor_html(soup, n_alvo)
            if sel_p:
                mapa["arquitetura"] = "HTML_SELECTOR"
                mapa["caminhos"] = {"preco": sel_p, "nome": sel_n}
            else:
                print(f"{R}❌ Valor não encontrado no arquivo.{C}"); continue

        site_key = input(f"🌍 Nome do Site: ") or nome_arq
        db[site_key] = mapa
        with open(db_file, 'w', encoding='utf-8') as f: json.dump(db, f, indent=4)
        print(f"{G}✅ {site_key} mapeado via {mapa['arquitetura']}!{C}")

if __name__ == "__main__": identificar()
