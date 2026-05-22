import csv
import json
import os
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_RAW_GITHUB_DIR = BASE_DIR / "data" / "raw" / "github"

BASE_URL = "https://api.github.com"
USER_AGENT = "tcc-swiftui-architecture-research/1.0"
MAX_PAGES_PER_QUERY = 10 

ARCHITECTURE_QUERIES = {
    "MV": [
        "MV",
        "Model View",
        "Model-View",
    ],
    "MVVM": [
        "MVVM",
        "Model View ViewModel",
        "Model-View-ViewModel",
    ],
    "MVVM-C": [
        "MVVM-C",
        "MVVM Coordinator",
        "Model View ViewModel Coordinator",
    ],
    "MVC": [
        "MVC",
        "Model View Controller",
        "Model-View-Controller",
    ],
    "MVP": [
        "MVP",
        "Model View Presenter",
        "Model-View-Presenter",
    ],
    "VIPER": [
        "VIPER",
        "View Interactor Presenter Entity Router",
    ],
    "TCA": [
        "TCA",
        "The Composable Architecture",
        "ComposableArchitecture",
    ],
    "MVI": [
        "MVI",
        "Model View Intent",
        "Model-View-Intent",
    ],
    "RIBs": [
        "RIBs",
        "Router Interactor Builder",
        "Router-Interactor-Builder",
    ],
}


class RateLimiter:
    """Token bucket compartilhado entre threads."""

    def __init__(self, calls_per_minute: int) -> None:
        """Configura o intervalo mínimo entre chamadas à API."""
        self._interval = 60.0 / calls_per_minute
        self._lock = threading.Lock()
        self._last_call = 0.0

    def acquire(self) -> None:
        """Bloqueia a thread até que uma nova chamada possa ser feita."""
        with self._lock:
            now = time.monotonic()
            wait = self._interval - (now - self._last_call)
            if wait > 0:
                time.sleep(wait)
            self._last_call = time.monotonic()


def load_token() -> Optional[str]:
    """Carrega o token do GitHub a partir do arquivo .env, quando disponível."""
    load_dotenv(BASE_DIR / ".env")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("AVISO: GITHUB_TOKEN não encontrado no .env. Limite: 10 req/min.")
    return token


def fetch_json(url: str, token: Optional[str], max_retries: int = 3) -> Dict[str, Any]:
    """Executa uma requisição GET à API do GitHub e retorna o JSON decodificado."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)

    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            retry_after = e.headers.get("Retry-After")
            rate_remaining = e.headers.get("X-RateLimit-Remaining")
            rate_reset = e.headers.get("X-RateLimit-Reset")

            should_retry = e.code in {403, 429, 500, 502, 503, 504}
            if not should_retry or attempt == max_retries:
                raise RuntimeError(
                    f"GitHub API falhou ({e.code}) para {url}: {body[:300]}"
                ) from e

            wait_seconds = 30
            if retry_after and retry_after.isdigit():
                wait_seconds = int(retry_after)
            elif rate_remaining == "0" and rate_reset and rate_reset.isdigit():
                wait_seconds = max(int(rate_reset) - int(time.time()) + 5, wait_seconds)

            print(
                f"  AVISO: GitHub API retornou {e.code}; "
                f"tentando novamente em {wait_seconds}s ({attempt}/{max_retries})"
            )
            time.sleep(wait_seconds)
        except URLError as e:
            if attempt == max_retries:
                raise RuntimeError(f"Falha de rede ao acessar {url}: {e}") from e
            wait_seconds = 10 * attempt
            print(
                f"  AVISO: falha de rede; "
                f"tentando novamente em {wait_seconds}s ({attempt}/{max_retries})"
            )
            time.sleep(wait_seconds)

    raise RuntimeError(f"GitHub API falhou para {url}")


def _repo_to_row(
    architecture: str,
    repo: Dict[str, Any],
    source: str,
    matched_query: str,
) -> Dict[str, Any]:
    """Converte um payload de repositório do GitHub para uma linha tabular."""
    return {
        "architecture": architecture,
        "source": source,
        "matched_queries": matched_query,
        "repo_id": repo.get("id", ""),
        "full_name": repo.get("full_name", ""),
        "name": repo.get("name", ""),
        "description": repo.get("description", ""),
        "topics": ",".join(repo.get("topics", [])),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "watchers": repo.get("watchers_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "language": repo.get("language", ""),
        "created_iso": repo.get("created_at", ""),
        "updated_iso": repo.get("updated_at", ""),
        "url": repo.get("html_url", ""),
    }


def search_repos(
    architecture: str,
    keyword: str,
    token: Optional[str],
    limiter: RateLimiter,
) -> Dict[int, Dict[str, Any]]:
    """Busca repositórios SwiftUI por nome, descrição e tópicos."""
    results: Dict[int, Dict[str, Any]] = {}
    query = f"swiftui {keyword} language:swift"

    for page in range(1, MAX_PAGES_PER_QUERY + 1):
        params = urllib.parse.urlencode({
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page,
        })
        limiter.acquire()
        payload = fetch_json(f"{BASE_URL}/search/repositories?{params}", token)
        items = payload.get("items", [])

        if not items:
            break

        for repo in items:
            rid = repo.get("id")
            if rid and rid not in results:
                results[rid] = _repo_to_row(architecture, repo, "repo_search", keyword)

        if len(items) < 100:
            break

    print(f"  [{architecture} | {keyword}] repo_search: {len(results)} repos")
    return results


def search_readme(
    architecture: str,
    keyword: str,
    token: Optional[str],
    limiter: RateLimiter,
) -> Dict[int, Dict[str, Any]]:
    """Busca a palavra-chave em arquivos README de repositórios Swift."""
    results: Dict[int, Dict[str, Any]] = {}
    query = f"swiftui {keyword} language:swift filename:README"

    for page in range(1, MAX_PAGES_PER_QUERY + 1):
        params = urllib.parse.urlencode({
            "q": query,
            "per_page": 100,
            "page": page,
        })
        limiter.acquire()
        payload = fetch_json(f"{BASE_URL}/search/code?{params}", token)
        items = payload.get("items", [])

        if not items:
            break

        for item in items:
            repo = item.get("repository", {})
            rid = repo.get("id")
            if rid and rid not in results:
                results[rid] = _repo_to_row(architecture, repo, "readme_search", keyword)

        if len(items) < 100:
            break

    print(f"  [{architecture} | {keyword}] readme_search: {len(results)} repos")
    return results


def merge_repo_results(
    merged: Dict[int, Dict[str, Any]],
    new_rows: Dict[int, Dict[str, Any]],
) -> None:
    """Adiciona resultados ao acumulador, preservando fontes e queries encontradas."""
    for rid, row in new_rows.items():
        if rid not in merged:
            merged[rid] = row
            continue

        sources = set(merged[rid]["source"].split(";"))
        sources.update(row["source"].split(";"))
        merged[rid]["source"] = ";".join(sorted(sources))

        queries = set(merged[rid]["matched_queries"].split(";"))
        queries.update(row["matched_queries"].split(";"))
        merged[rid]["matched_queries"] = ";".join(sorted(queries))


def collect_architecture(
    architecture: str,
    keywords: List[str],
    token: Optional[str],
    limiter: RateLimiter,
) -> List[Dict[str, Any]]:
    """Coleta repositórios de uma arquitetura e consolida resultados duplicados."""
    merged: Dict[int, Dict[str, Any]] = {}
    for keyword in keywords:
        repo_results = search_repos(architecture, keyword, token, limiter)
        readme_results = search_readme(architecture, keyword, token, limiter)
        merge_repo_results(merged, repo_results)
        merge_repo_results(merged, readme_results)

    return list(merged.values())


def save_dicts_to_csv(rows: List[Dict[str, Any]], filename: Path) -> None:
    """Salva uma lista de dicionários em CSV usando as chaves da primeira linha."""
    if not rows:
        print(f"Nenhuma linha para salvar em {filename}.")
        return
    fieldnames = list(rows[0].keys())
    with filename.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Arquivo salvo: {filename} (linhas: {len(rows)})")


def main() -> None:
    """Executa a coleta paralela de repositórios SwiftUI no GitHub."""
    DATA_RAW_GITHUB_DIR.mkdir(parents=True, exist_ok=True)

    token = load_token()
    calls_per_minute = 28 if token else 9
    limiter = RateLimiter(calls_per_minute)

    all_repos: List[Dict[str, Any]] = []
    print(f"Iniciando coleta paralela ({len(ARCHITECTURE_QUERIES)} arquiteturas)...\n")

    with ThreadPoolExecutor(max_workers=len(ARCHITECTURE_QUERIES)) as executor:
        futures = {
            executor.submit(collect_architecture, arch, keywords, token, limiter): arch
            for arch, keywords in ARCHITECTURE_QUERIES.items()
        }
        for future in as_completed(futures):
            arch = futures[future]
            repos = future.result()
            print(f"[{arch}] concluído — {len(repos)} repos únicos")
            all_repos.extend(repos)

    save_dicts_to_csv(
        all_repos,
        DATA_RAW_GITHUB_DIR / "github_swiftui_repos.csv",
    )
    unique_repo_ids = {
        row["repo_id"]
        for row in all_repos
        if row.get("repo_id")
    }
    print("\nResumo da coleta GitHub:")
    print(f"  Total de linhas coletadas: {len(all_repos)}")
    print(f"  Total de repositórios únicos: {len(unique_repo_ids)}")


if __name__ == "__main__":
    main()
