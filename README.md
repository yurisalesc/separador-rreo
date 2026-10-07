# separador-rreo

Biblioteca e CLI em Python para **separar anexos RREO** publicados em diários oficiais da **FEMURN** (Federação dos Municípios do Rio Grande do Norte).

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

```python
from separador_rreo import SeparadorRreo, separar

# Atalho completo (analisa + exporta)
resultado = separar(
    "diario.pdf",
    municipalities=["Bodó", "Angicos"],
    destination="saida_rreo",
)
print(resultado.pdf_count, resultado.spreadsheet, resultado.zip_path)

# Ou em duas etapas / com mais controle
app = SeparadorRreo()
analysis, export = app.run(
    "diario.pdf",
    municipalities=["Bodó"],
    destination="saida_rreo",
)

for finding in analysis.for_municipality("Bodó"):
    print(finding.annex, finding.page_start, finding.page_end, finding.status)
```

### Extensão (Open/Closed)

Você pode acrescentar heurísticas de reconhecimento sem alterar o analisador:

```python
from separador_rreo import AnexoRecognizer, SeparadorRreo
from separador_rreo.analyzer import RreoAnalyzer

def minha_heuristica(linha: str) -> int | None:
    if "MEU PADRAO DE ANEXO 9" in linha.upper():
        return 9
    return None

recognizer = AnexoRecognizer(heuristics=[minha_heuristica])
app = SeparadorRreo(analyzer=RreoAnalyzer(recognizer=recognizer))
```

## Requisitos

- Python 3.10+
- Dependências: `pymupdf`, `openpyxl`
- PDF com **texto selecionável** (OCR prévio se o diário for só imagem)

## Testes

```bash
pytest
```

Para um teste de integração com um diário real:

```bash
separador-rreo /caminho/publicado.pdf --municipios "Bodó" --saida /tmp/rreo_out
```

## Publicação (PyPI)

### Local (com token em `~/.pypirc`)

```bash
cp .pypirc.example ~/.pypirc   # edite e cole os tokens
chmod 600 ~/.pypirc

./scripts/release.sh test      # ensaio no TestPyPI
./scripts/release.sh pypi      # publicação oficial
```

### GitHub Actions

1. Em **Settings → Secrets and variables → Actions**, crie:
   - `PYPI_API_TOKEN` — token do PyPI
   - `TEST_PYPI_API_TOKEN` — token do TestPyPI
2. Publique um **Release** no GitHub (tag `v0.1.0`, etc.) → workflow **Publish to PyPI**
3. Ou rode o workflow manualmente (**Actions → Publish to PyPI → Run workflow**) escolhendo `testpypi` ou `pypi`

Antes de cada release, atualize `version` em `pyproject.toml`.

## Autores

- **Ana Cláudia Medeiros de Carvalho** (autora principal) — anaclaudiaengmat@gmail.com
- **Yuri Sales** — yuri.sales@protonmail.com

## Licença

MIT — veja [LICENSE](LICENSE).
