# SwiftUI Research

Data collection and analysis project about software architectures used with SwiftUI.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Download the lexicon used by NLTK for sentiment analysis:

```bash
python -m nltk.downloader vader_lexicon
```

## API Configuration

Create a `.env` file in the project root using `.env.example` as a template:

```bash
cp .env.example .env
```

Fill in the required variables:

```dotenv
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=
GITHUB_TOKEN=
STACKOVERFLOW_KEY=
```

The `.env` file contains real keys and tokens, so it is excluded from Git by `.gitignore`.

## How to Run

To run the full analysis pipeline using the data already available in `data/raw`:

```bash
python scripts/rodar_pesquisa.py
```

This command runs the Reddit, Stack Overflow, GitHub, Forms, and qualitative analyses. It then runs the cross-source comparisons and generates the word clouds.

Results are saved in:

- `data/processed/`: processed CSV files
- `outputs/`: generated charts and reports

## Data Collection

The collection scripts can be run individually when the raw data needs to be updated:

```bash
python scripts/coleta/reddit_script.py
python scripts/coleta/github_script.py
python scripts/coleta/stackoverflow_script.py
```

They use the credentials configured in `.env` and write the collected data to `data/raw`.

## Individual Analyses

Specific analyses can also be run individually:

```bash
python scripts/analise/analise_reddit.py
python scripts/analise/analise_stackoverflow.py
python scripts/analise/analise_github.py
python scripts/analise/analise_forms.py
python scripts/analise/analise_qualitativa_reddit.py
python scripts/analise/comparacao_fontes.py
python scripts/analise/gerar_nuvens_palavras.py
```

## Security

Do not commit files with real credentials. Use `.env.example` only as a template and keep keys in the local `.env` file.
