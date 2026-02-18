import os
import json
from bs4 import BeautifulSoup

def limpar_preco(preco_texto):
    """Transforma entradas como '22,50' ou 'R$ 22.50' em float válido."""
    if not preco_texto:
        return None
    # Remove símbolos comuns e troca vírgula por ponto
    preco_limpo = preco_texto.replace('R$', '').replace(' ', '').replace(',', '.').strip()
    try:
        return float(preco_limpo)
    except ValueError:
        return None

def obter_entradas_blindadas():
    """Garante que o usuário não digite bobagem nos inputs."""
    while True:
        p_input = input("💰 Preço do produto (ex: 21.97): ").strip()
        p_valido = limpar_preco(p_input)
        if p_valido is not None:
            return f"{p_valido:.2f}"
        print("❌ Erro: Preço inválido! Use apenas números, ponto ou vírgula.")

def identificar():
    print("\n" + "="*50)
    print("🛠️  Script 1 v2.3 - Identificador Universal")
    print("="*50)

    pasta = "html_alvos"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
        print(f"📁 Pasta '{pasta}' criada. Coloque os HTMLs lá e rode de novo.")
        return

    arquivos = [f for f in os.listdir(pasta) if f.endswith('.html')]
    
    if not arquivos:
        print(f"⚠️  Nenhum arquivo .html encontrado em '{pasta}'.")
        return

    print(f"📦 Encontrados {len(arquivos)} arquivos para análise.")

    # Carrega banco existente ou cria um novo
    if os.path.exists('database_sites.json'):
        with open('database_sites.json', 'r', encoding='utf-8') as f:
            try:
                banco = json.load(f)
            except:
                banco = {}
    else:
        banco = {}

    for arquivo in arquivos:
        print(f"\n🔍 Analisando arquivo: {arquivo}")
        caminho_completo = os.path.join(pasta, arquivo)
        
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Entrada de dados com proteção
        p_alvo_str = obter_entradas_blindadas()
        n_alvo = input("📦 Nome do Produto (conforme o site): ").strip()
        
        # Sugere o nome do site baseado no nome do arquivo
        sugestao_nome = arquivo.replace('.html', '').lower().replace(' ', '')
        nome_site = input(f"🌍 ID do Site (Sugestão: {sugestao_nome}): ").strip().lower().replace(' ', '') or sugestao_nome

        mapeado = False

        # --- TENTATIVA 1: JSON LD ---
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list): data = data[0]
                
                def busca_json(obj, alvo_p, alvo_n):
                    path_p, path_n = None, None
                    def walk(curr, path=""):
                        nonlocal path_p, path_n
                        if isinstance(curr, dict):
                            for k, v in curr.items():
                                new_path = f"{path}['{k}']"
                                if str(v) == alvo_p: path_p = new_path
                                if isinstance(v, str) and alvo_n in v: path_n = new_path
                                walk(v, new_path)
                        elif isinstance(curr, list):
                            for i, v in enumerate(curr):
                                new_path = f"{path}[{i}]"
                                walk(v, new_path)
                    walk(obj)
                    return path_p, path_n

                p_path, n_path = busca_json(data, p_alvo_str, n_alvo)
                if p_path:
                    banco[nome_site] = {
                        "arquitetura": "JSON",
                        "caminhos": {"preco": p_path, "nome": n_path}
                    }
                    print(f"✅ {nome_site} mapeado via JSON!")
                    mapeado = True
                    break
            except:
                continue

        # --- TENTATIVA 2: HTML SELECTOR ---
        if not mapeado:
            print("⚠️ JSON não detectado. Tentando HTML Selector...")
            elemento_p = soup.find(string=lambda t: t and p_alvo_str in t)
            if elemento_p:
                pai = elemento_p.parent
                # Tenta pegar a classe para ser mais específico
                seletor = pai.name
                if pai.get('class'):
                    seletor += "." + ".".join(pai.get('class'))
                
                banco[nome_site] = {
                    "arquitetura": "HTML_SELECTOR",
                    "caminhos": {"preco": seletor, "nome": "title"}
                }
                print(f"✅ {nome_site} mapeado via HTML_SELECTOR!")
                mapeado = True
            else:
                print(f"❌ Valor {p_alvo_str} não encontrado no arquivo.")

        # Salva o banco a cada arquivo processado
        with open('database_sites.json', 'w', encoding='utf-8') as f:
            json.dump(banco, f, indent=4, ensure_ascii=False)

    print("\n✨ Processamento concluído!")

if __name__ == "__main__":
    identificar()
