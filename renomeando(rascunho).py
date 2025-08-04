import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import unicodedata

# Configurações de pastas
downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
destino = os.path.join(downloads, 'NFs_Renomeadas')

# Criar pasta destino se não existir
os.makedirs(destino, exist_ok=True)

# Namespace padrão das NFe
ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

def normalizar_texto(texto):
    """Normaliza texto removendo acentos e caracteres especiais"""
    if texto is None:
        return ""
    # Normaliza para forma de decomposição (NFD) e remove caracteres não ASCII
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    # Remove caracteres inválidos para nomes de arquivos
    return re.sub(r'[\\/*?:"<>|]', '', texto).strip()

def extrair_dados_xml(caminho_xml):
    """Extrai dados relevantes do arquivo XML da NFe"""
    try:
        tree = ET.parse(caminho_xml)
        root = tree.getroot()
        
        # Encontrar a tag NFe
        nfe_element = root.find('.//nfe:NFe', ns) or root.find('.//nfeProc/nfe:NFe', ns)
        
        if nfe_element is None:
            raise ValueError("Estrutura XML não reconhecida")
        
        infNFe = nfe_element.find('nfe:infNFe', ns)
        ide = infNFe.find('nfe:ide', ns)
        emit = infNFe.find('nfe:emit', ns)
        dest = infNFe.find('nfe:dest', ns)
        
        # Extrair data de emissão
        dh_emi = ide.find('nfe:dhEmi', ns)
        if dh_emi is not None:
            data_emissao = dh_emi.text[:10]  # Formato: AAAA-MM-DD
        else:
            d_emi = ide.find('nfe:dEmi', ns)
            if d_emi is not None:
                # Converter de DD/MM/AAAA para AAAA-MM-DD
                partes = d_emi.text.split('/')
                data_emissao = f"{partes[2]}-{partes[1]}-{partes[0]}"
            else:
                data_emissao = 'DATA-DESCONHECIDA'
        
        # Extrair razão social do destinatário
        destinatario = dest.find('nfe:xNome', ns).text if dest is not None else 'DESTINATARIO-NAO-INFORMADO'
        
        # Extrair razão social do emitente
        emitente = emit.find('nfe:xNome', ns).text if emit is not None else 'EMITENTE-NAO-INFORMADO'
        
        # Extrair número da NF
        nNF = ide.find('nfe:nNF', ns).text if ide is not None else 'NNF-NAO-INFORMADO'
        
        # Extrair chave da NFe
        chave_element = infNFe.get('Id')
        chave = chave_element.replace('NFe', '') if chave_element else None
        
        # Extrair produtos
        produtos = []
        for det in infNFe.findall('nfe:det', ns):
            prod = det.find('nfe:prod', ns)
            if prod is not None:
                xProd = prod.find('nfe:xProd', ns)
                if xProd is not None and xProd.text:
                    produtos.append(normalizar_texto(xProd.text))
        
        return data_emissao, normalizar_texto(destinatario), normalizar_texto(emitente), nNF, chave, produtos
    
    except Exception as e:
        print(f"Erro ao processar XML: {str(e)}")
        return 'ERRO-DATA', 'ERRO-DESTINATARIO', 'ERRO-EMITENTE', 'ERRO-NNF', None, []

def exibir_produtos(produtos):
    """Exibe produtos formatados no terminal"""
    print("\n" + "="*50)
    print("PRODUTOS DA NOTA FISCAL:")
    print("="*50)
    for i, produto in enumerate(produtos, 1):
        print(f"{i}. {produto}")
    print("="*50)

# Processar todos os arquivos XML na pasta de Downloads
xml_files = [arquivo_name for arquivo_name in os.listdir(downloads) if arquivo_name.lower().endswith('.xml')]
total = len(xml_files)

print(f"\nIniciando processo de renomeação para {total} notas fiscais...")

for i, xml_file in enumerate(xml_files, 1):
    caminho_xml = os.path.join(downloads, xml_file)
    
    try:
        # Extrair dados do XML
        data, destinatario, emitente, nNF, chave, produtos = extrair_dados_xml(caminho_xml)
        
        if not chave:
            print(f"\n[{i}/{total}] Chave não encontrada no XML: {xml_file}. Pulando...")
            continue
        
        # Construir nome do arquivo PDF correspondente
        pdf_file = f"NFE-{chave}.pdf"
        caminho_pdf = os.path.join(downloads, pdf_file)
        
        if not os.path.exists(caminho_pdf):
            print(f"\n[{i}/{total}] PDF correspondente não encontrado para XML {xml_file}. Procurando variações...")
            # Tentar encontrar arquivos PDF com a chave no nome
            pdf_candidates = [f for f in os.listdir(downloads) 
                            if chave in f and f.lower().endswith('.pdf')]
            
            if pdf_candidates:
                caminho_pdf = os.path.join(downloads, pdf_candidates[0])
                print(f"Usando arquivo PDF encontrado: {pdf_candidates[0]}")
            else:
                print(f"Nenhum PDF encontrado para a chave {chave}. Pulando...")
                continue
        
        # Exibir informações da nota fiscal
        print(f"\n{'='*100}")
        print(f"[{i}/{total}] PROCESSANDO NOTA FISCAL: {nNF} ({data})")
        print(f"Destinatário: {destinatario}")
        print(f"Emitente: {emitente}")
        print(f"Chave: {chave}")
        
        # Exibir produtos se houver
        if produtos:
            exibir_produtos(produtos)
            
            # Pedir entrada do usuário para os produtos
            entrada_valida = False
            while not entrada_valida:
                print("\nComo você deseja nomear a parte dos produtos?")
                print("(Deixe em branco para usar os primeiros produtos automaticamente)")
                entrada_produtos = input(">> ").strip()
                
                # Validar entrada
                if entrada_produtos == "":
                    # Usar produtos automaticamente
                    if len(produtos) <= 4:
                        produtos_str = " - " + " - ".join(produtos)
                    else:
                        produtos_str = " - " + " - ".join(produtos[:3]) + " - e outros"
                    entrada_valida = True
                elif len(entrada_produtos) > 150:
                    print("Entrada muito longa! Máximo de 150 caracteres.")
                else:
                    # Validar caracteres perigosos
                    if re.search(r'[\\/*?:"<>|]', entrada_produtos):
                        print("Entrada contém caracteres inválidos: \\ / * ? : \" < > |")
                    else:
                        produtos_str = " - " + entrada_produtos
                        entrada_valida = True
        else:
            print("\nNenhum produto encontrado nesta nota fiscal.")
            produtos_str = ""
        
        # Criar novo nome para o arquivo PDF
        novo_nome = f"{data} - {destinatario} - {emitente} - NF {nNF}{produtos_str}.pdf"
        
        # Garantir que o nome não seja muito longo
        if len(novo_nome) > 220:
            print(f"Aviso: Nome do arquivo muito longo ({len(novo_nome)} caracteres). Reduzindo...")
            novo_nome = novo_nome[:220] + ".pdf"
        
        # Mover e renomear o arquivo PDF
        novo_caminho = os.path.join(destino, novo_nome)
        shutil.move(caminho_pdf, novo_caminho)
        
        print(f"\n✓ Arquivo renomeado: {novo_nome}")
        print(f"Salvo em: {novo_caminho}")
        
    except Exception as e:
        print(f"\n✗ Erro ao processar {xml_file}: {str(e)}")

print("\n" + "="*100)
print("Processo concluído! Todos os PDFs foram renomeados e movidos.")
print(f"Local: {destino}")
print("="*100)