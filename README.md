# separador-rreo

[![PyPI](https://img.shields.io/pypi/v/separador-rreo?label=PyPI&color=3775A9)](https://pypi.org/project/separador-rreo/) [![Python](https://img.shields.io/badge/Python-%3E%3D%203.10-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![CI](https://github.com/yurisalesc/separador-rreo/actions/workflows/ci.yml/badge.svg)](https://github.com/yurisalesc/separador-rreo/actions/workflows/ci.yml) [![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE) [![Status](https://img.shields.io/badge/status-beta-orange.svg)](https://pypi.org/project/separador-rreo/)

Biblioteca e CLI em Python para **separar anexos RREO** publicados em diários
oficiais da **FEMURN** (Federação dos Municípios do Rio Grande do Norte).

A partir de um PDF do diário com texto selecionável, o pacote:

1. Localiza cabeçalhos `PREFEITURA MUNICIPAL DE …`
2. Reconhece títulos de anexos RREO (padrões observados em publicações como Angicos, Bodó e Coronel João Pessoa)
3. Recorta cada anexo em PDF individual por município
4. Gera a planilha `Controle_Publicacoes.xlsx` para conferência manual
5. Empacota tudo em um `.zip`

## Instalação

```bash
pip install separador-rreo
```

Em desenvolvimento (clone local):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso pela linha de comando

```bash
separador-rreo diario.pdf --municipios "Bodó" "Coronel João Pessoa" "Angicos"
```

Opções:

| Opção | Descrição |
|-------|-----------|
| `pdf` | Caminho do diário FEMURN (obrigatório se houver mais de um PDF na pasta) |
| `--municipios` | Um ou mais nomes de municípios |
| `--saida` | Pasta de saída (padrão: `RREO_separados`) |
| `--version` | Mostra a versão |

Sem argumentos, o comando pergunta interativamente pelo PDF e pelos municípios:

```bash
separador-rreo
```

Também é possível executar como módulo:

```bash
python -m separador_rreo diario.pdf --municipios "Bodó"
```

### Saída gerada

```text
RREO_separados/
├── BODO/
│   ├── RREO_01_BODO.pdf
│   ├── RREO_03_BODO.pdf
│   └── …
├── Controle_Publicacoes.xlsx
RREO_separados.zip
```

A coluna **Situacao** da planilha indica:

- `Encontrado` — recorte delimitado pelo código identificador
- `Verificar limite final` — código ausente; vale conferência manual
- `Nao localizado` — anexo não encontrado para aquele município
- variações com `partes reunidas` / `multiplas publicacoes` quando há fusão ou mais de uma publicação

## Uso como biblioteca

### Separação completa

```python
from separador_rreo import separar_rreo

resultado = separar_rreo(
    "diario.pdf",
    municipios=["Bodó", "Angicos"],
    destino="saida_rreo",
)

print(resultado.quantidade_pdfs)
print(resultado.planilha)
print(resultado.arquivo_zip)
```

### Análise e exportação separadas

```python
from separador_rreo import SeparadorRreo

separador = SeparadorRreo()
analise, exportacao = separador.executar(
    "diario.pdf",
    municipios=["Bodó"],
    destino="saida_rreo",
)

for ocorrencia in analise.do_municipio("Bodó"):
    print(
        ocorrencia.anexo,
        ocorrencia.pagina_inicial,
        ocorrencia.pagina_final,
        ocorrencia.situacao.value,
    )
```

### Tipos do domínio

Os anexos e as situações são representados por enums. Isso reduz erros de
digitação e facilita comparações:

```python
from separador_rreo import AnexoRreo, SituacaoOcorrencia

if ocorrencia.anexo is AnexoRreo.BALANCO_ORCAMENTARIO:
    print("Balanço orçamentário localizado")

if ocorrencia.situacao is SituacaoOcorrencia.VERIFICAR_LIMITE_FINAL:
    print("É necessário conferir manualmente o fim do recorte")
```

### Ensinar um título novo ao reconhecedor

O pacote já conhece vários jeitos de um anexo RREO aparecer no diário
(por exemplo `ANEXO 01_RREO` ou `RREO - 4º BIM - BALANÇO ORÇAMENTÁRIO`).

Se um município publicar com um texto de título **diferente**, o pacote pode
não achar esse anexo. Nesse caso você pode passar uma função pequena que
olha cada linha do PDF e devolve o número do anexo (ou `None` se a linha
não for um título):

```python
from separador_rreo import (
    AnalisadorRreo,
    AnexoRreo,
    ReconhecedorTituloRreo,
    SeparadorRreo,
)

def reconhecer_titulo_do_meu_municipio(linha: str) -> int | None:
    # Exemplo: se a linha for um título do Anexo 9, retorne 9
    if "DEMONSTRATIVO X DO ANEXO 9" in linha.upper():
        return AnexoRreo.RECEITAS_OPERACOES_CREDITO
    return None

reconhecedor = ReconhecedorTituloRreo(
    regras_adicionais=[reconhecer_titulo_do_meu_municipio]
)
separador = SeparadorRreo(
    analisador=AnalisadorRreo(reconhecedor=reconhecedor)
)
analise, exportacao = separador.executar(
    "diario.pdf", ["Meu Município"], "saida_rreo"
)
```

As regras adicionais são executadas junto com as regras já fornecidas pelo
pacote. Assim você amplia o reconhecimento sem alterar o código interno.

## Organização do código

- `analisador.py` localiza municípios, títulos e limites dos anexos;
- `reconhecimento.py` contém as regras de reconhecimento de títulos;
- `exportacao.py` coordena a geração dos artefatos;
- `planilha.py`, `compactacao.py` e `agrupamento.py` cuidam de tarefas específicas;
- `documento_pdf.py` isola a dependência do PyMuPDF;
- `contratos.py`, `modelos.py` e `enumeracoes.py` definem os contratos e o domínio.

## Requisitos

- Python 3.10+
- Dependências: `pymupdf`, `openpyxl`
- PDF com **texto selecionável** (OCR prévio se o diário for só imagem)

## Testes

```bash
pytest
ruff check src tests
```

Há um diário de exemplo em `tests/fixtures/publicado_117684.pdf` usado no teste de integração.

## Autores

- **Ana Cláudia Medeiros de Carvalho** — anaclaudiaengmat@gmail.com
- **Yuri Henrique Sales da Costa** — yuri.sales@protonmail.com

## Licença

MIT — veja [LICENSE](LICENSE).
