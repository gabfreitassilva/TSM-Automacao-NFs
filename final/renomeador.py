import xml.etree.ElementTree as ET
import unicodedata
import shutil
import os
import re

pasta_NFs = os.path.join(os.path.expanduser('~'), 'Downloads\\NFs_Baixadas')
pasta_XMLs = os.path.join(pasta_NFs, 'XMLs_Baixados')
pasta_final = os.path.join(pasta_NFs, 'NFs_Renomeadas')

os.makedirs(pasta_XMLs, exist_ok=True)
os.makedirs(pasta_final, exist_ok=True)

ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

def normalizar_texto(texto):
    # Normaliza qualquer texto removendo acentos e caracteres especiais
    if texto is None:
        return ""
    # Normaliza para forma de decomposição (NFD) e remove caracteres não ASCII
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    # Remove caracteres inválidos para nomes de arquivos
    return re.sub(r'[\\/*?:"<>|]', '', texto).strip()

def extrair_dados_xml(caminho_xml):
    # Extrai os dados relevantes do arquivo XML da NFe
    try:
        tree = ET.parse(caminho_xml)
        root = tree.getroot()
        
        # Encontrar a tag NFe
        nfe_element = root.find('.//nfe:NFe', ns) or root.find('.//nfeProc/nfe:NFe', ns)
        
        if nfe_element is None:
            raise ValueError("Estrutura XML não reconhecida")
        
        infNFe = nfe_element.find('nfe:infNFe', ns) # Chave da NFe
        ide = infNFe.find('nfe:ide', ns) # Número da NFe
        emit = infNFe.find('nfe:emit', ns) # Empresa da compra
        dest = infNFe.find('nfe:dest', ns) # Razão social
        
        try: # Retorna a data final no formato DD.MM.AAAA
            dh_emi = ide.find('nfe:dhEmi', ns)
            if dh_emi is not None:
                partes = dh_emi.text[:10].split('-')
                data_emissao = f"{partes[2]}.{partes[1]}.{partes[0]}"
            else:
                d_emi = ide.find('nfe:dEmi', ns)
                if d_emi is not None:
                    partes = d_emi.text.split('/')
                    data_emissao = f"{partes[0]}.{partes[1]}.{partes[2]}"
                else:
                    data_emissao = 'DATA-DESCONHECIDA'
        except (AttributeError, IndexError):
            data_emissao = 'FORMATO-INVALIDO'
        
        # Extrair razão social do destinatário
        destinatario = dest.find('nfe:xNome', ns).text if dest is not None else 'DESTINATARIO-NAO-INFORMADO'
        
        destinatario_sem_parenteses = re.sub(r'\([^)]*\)', '', destinatario) # Retira parentêses
        destinatario_normalizado = unicodedata.normalize('NFKD', destinatario_sem_parenteses) # Normaliza o texto obtido
        destinatario_sem_acentos = ''.join(c for c in destinatario_normalizado if not unicodedata.combining(c)) # Retira qualquer acento existente
        destinatario_limpo = re.sub(r'[^\w]', ' ', destinatario_sem_acentos)  # Substitui caracteres especiais por espaço
        destinatario_limpo = re.sub(r'\b(TSM)(20\d{2})\b', r'\1 \2', destinatario_limpo, flags=re.IGNORECASE) # Adiciona espaço entre TSM e o ano
        destinatario_final = (re.sub(r'\s+', ' ', destinatario_limpo).strip()).upper()  # Remove espaços extras
        
        rzsocial_destinat = ['CONSORCIO TSM 2021', 'CONSORCIO TSM 2023'] # Somente renomear com essas duas razões sociais
        # Renomeia com as duas possibilidades que eu desejo
        for razao in rzsocial_destinat:
            if razao in destinatario_final:
                destinatario_final = razao
                break

        # Extrair razão social do emitente
        emitente = emit.find('nfe:xNome', ns).text if emit is not None else 'EMITENTE-NAO-INFORMADO'
        
        rzsocial_emitente = {
            'LBZ COMECIO DE PECAS PARA REFRIGERACAO LTDA': 'LBZ',
            'SOLUTIONS PRODUTOS EM GERAL LTDA': 'SOLUTIONS', 
            'ENPECEL COMERCIAL DE MATERIAL ELETRICO LTDA': 'ENPECEL', 
            'BEMAX COMERCIO ATACADISTA DE MAQUINAS E SERVICOS EIRELI': 'BEMAX', 
            'NATURAGUA AGUAS MIN. IND. E COM. S/A': 'NATURAGUA'
        } # Somente renomear com essas razões para empresas
        
        # Verificar e substituir pelo nome simplificado
        for nome_completo, nome_simplificado in rzsocial_emitente.items():
            if nome_completo in emitente:
                emitente = nome_simplificado
                break

        # Extrair número da NF
        nNF = ide.find('nfe:nNF', ns).text if ide is not None else 'NUMERO-NF-NAO-INFORMADO'
        
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
        
        return data_emissao, normalizar_texto(destinatario_final), normalizar_texto(emitente), nNF, chave, produtos
    
    except Exception as e:
        print(f"Erro ao processar XML: {str(e)}")
        return 'ERRO-DATA', 'ERRO-DESTINATARIO', 'ERRO-EMITENTE', 'ERRO-NNF', None, []
    

def exibir_produtos(produtos):
    # Exibe os produtos formatados no terminal para escolha do nome final
    print("\n" + "="*50)
    print("PRODUTOS DA NOTA FISCAL:")
    print("="*50)
    for i, produto in enumerate(produtos, 1):
        print(f"{i}. {produto}")
    print("="*50)

# Processa todos os arquivos XML na pasta de NFs_baixadas
xml_files = [arquivo_name for arquivo_name in os.listdir(pasta_NFs) if arquivo_name.lower().endswith('.xml')]
total = len(xml_files) # Retorna quantos arquivos XML foram encontrados

print("\033c", end='')
print(f"\nIniciando processo de renomeação para {total} notas fiscais...")

for i, xml_file in enumerate(xml_files, 1):
    caminho_xml = os.path.join(pasta_NFs, xml_file)
    
    try:
        # Extrai os dados essenciais do XML
        data, destinatario, emitente, nNF, chave, produtos = extrair_dados_xml(caminho_xml)
        
        if not chave:
            print(f"\n[{i}/{total}] Chave não encontrada no XML: {xml_file}. Pulando...")
            continue
        
        # Construção do nome do arquivo PDF correspondente
        pdf_file = f"NFE-{chave}.pdf"
        caminho_pdf = os.path.join(pasta_NFs, pdf_file)
        
        if not os.path.exists(caminho_pdf):
            print(f"\n[{i}/{total}] PDF correspondente não encontrado para XML {xml_file}. Procurando variações...")
            # Tenta encontrar os arquivos PDF com a chave no nome
            pdf_candidates = [f for f in os.listdir(pasta_NFs) 
                            if chave in f and f.lower().endswith('.pdf')]
            
            if pdf_candidates:
                caminho_pdf = os.path.join(pasta_NFs, pdf_candidates[0])
                print(f"Usando arquivo PDF encontrado: {pdf_candidates[0]}")
            else:
                print(f"Nenhum PDF encontrado para a chave {chave}. Pulando...")
                continue
        
        # Exibe informações da nota fiscal para auxiliar na renomeação
        print(f"\n{'='*100}")
        print(f"[{i}/{total}] PROCESSANDO NOTA FISCAL: {nNF} ({data})")
        print(f"Destinatário: {destinatario}")
        print(f"Emitente: {emitente}")
        print(f"Chave: {chave}")
        
        # Exibir produtos se houver
        if produtos:
            exibir_produtos(produtos)
            
            # Pedir entrada do usuário para renomeação dos produtos
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
        novo_caminho = os.path.join(pasta_final, novo_nome)
        shutil.move(caminho_pdf, novo_caminho)
        shutil.move(caminho_xml, pasta_XMLs)
        
        print(f"\n\033[92m✓ Arquivo renomeado: {novo_nome}\033[0m")
        print(f"\033[92mSalvo em: {novo_caminho}\033[0m")
        
    except Exception as e:
        print(f"\n\033[91m✗ Erro ao processar {xml_file}: {str(e)}\033[0m")

print("\n" + "="*100)
print("\033[92mProcesso concluído! Todos os PDFs foram renomeados e movidos.\033[0m")
print(f"\033[92mLocal: {pasta_final}\033[0m")
print("="*100)