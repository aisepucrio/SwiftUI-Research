import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_RAW_SO_DIR = BASE_DIR / "data" / "raw" / "stackoverflow"

BASE_URL = "https://api.stackexchange.com/2.3"
SITE = "stackoverflow"
PAGE_SIZE = 100
REQUEST_DELAY_SECONDS = 0.5
USER_AGENT = "tcc-swiftui-architecture-research/1.0"

ARCHITECTURE_PATTERNS = {
    "MV": [
        r"\bMV\b",
        r"\bmodel[\s-]?view\b(?![\s-]?(?:viewmodel|controller|presenter|intent))",
    ],
    "MVVM": [
        r"\bMVVM\b",
        r"\bmodel[\s-]?view[\s-]?viewmodel\b",
    ],
    "MVVM-C": [
        r"\bMVVM[-\s]?C\b",
        r"\bMVVM Coordinator\b",
        r"\bmodel[\s-]?view[\s-]?viewmodel[\s-]?coordinator\b",
    ],
    "MVC": [
        r"\bMVC\b",
        r"\bmodel[\s-]?view[\s-]?controller\b",
    ],
    "MVP": [
        r"\bMVP\b",
        r"\bmodel[\s-]?view[\s-]?presenter\b",
    ],
    "VIPER": [
        r"\bVIPER\b",
        r"\bview[\s-]?interactor[\s-]?presenter[\s-]?entity[\s-]?router\b",
    ],
    "TCA": [
        r"\bTCA\b",
        r"\bthe composable architecture\b",
        r"\bcomposable architecture\b",
    ],
    "MVI": [
        r"\bMVI\b",
        r"\bmodel[\s-]?view[\s-]?intent\b",
    ],
    "RIBs": [
        r"\bRIBs\b",
        r"\brouter[\s-]?interactor[\s-]?builder\b",
    ],
}

SWIFTUI_KEYWORDS = [
    "SwiftUI",
    "@State",
    "@Binding",
    "@Environment",
    "@ObservedObject",
    "@EnvironmentObject",
    "StateObject",
    "ObservableObject",
    "NavigationStack",
]

ARCHITECTURE_QUERIES = {
    "MV": [
        "SwiftUI MV",
        "SwiftUI Model View",
        "SwiftUI Model-View",
    ],
    "MVVM": [
        "SwiftUI MVVM",
        "SwiftUI Model View ViewModel",
        "SwiftUI Model-View-ViewModel",
    ],
    "MVVM-C": [
        "SwiftUI MVVM-C",
        "SwiftUI MVVM Coordinator",
        "SwiftUI Model View ViewModel Coordinator",
    ],
    "MVC": [
        "SwiftUI MVC",
        "SwiftUI Model View Controller",
        "SwiftUI Model-View-Controller",
    ],
    "MVP": [
        "SwiftUI MVP",
        "SwiftUI Model View Presenter",
        "SwiftUI Model-View-Presenter",
    ],
    "VIPER": [
        "SwiftUI VIPER",
        "SwiftUI View Interactor Presenter Entity Router",
    ],
    "TCA": [
        "SwiftUI TCA",
        "SwiftUI The Composable Architecture",
        "SwiftUI Composable Architecture",
    ],
    "MVI": [
        "SwiftUI MVI",
        "SwiftUI Model View Intent",
        "SwiftUI Model-View-Intent",
    ],
    "RIBs": [
        "SwiftUI RIBs",
        "SwiftUI Router Interactor Builder",
        "SwiftUI Router-Interactor-Builder",
    ],
}

GENERAL_SEARCH_QUERIES = ["SwiftUI architecture pattern"]

ARCH_PATTERNS = {
    arch: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for arch, patterns in ARCHITECTURE_PATTERNS.items()
}

SWIFTUI_PATTERNS = {
    kw: re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
    for kw in SWIFTUI_KEYWORDS
}


def load_api_key() -> Optional[str]:
    """Carrega a chave da API Stack Exchange a partir do arquivo .env."""
    load_dotenv(BASE_DIR / ".env")
    key = os.getenv("STACKOVERFLOW_KEY")
    if not key:
        print(
            "AVISO: STACKOVERFLOW_KEY não encontrada no .env. "
            "O limite será de 300 requisições/dia."
        )
    return key


def fetch_json(url: str) -> Dict[str, Any]:
    """Executa uma requisição GET à API Stack Exchange e retorna o JSON."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        import gzip
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
        return json.loads(raw.decode("utf-8"))


def build_url(endpoint: str, params: Dict[str, Any]) -> str:
    """Monta uma URL da API Stack Exchange removendo parâmetros nulos."""
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{BASE_URL}{endpoint}?{query}"


def find_keywords(text: str, patterns: Dict[str, Any]) -> List[str]:
    """Retorna palavras-chave cujos padrões aparecem no texto informado."""
    if not text:
        return []
    found = []
    for kw, pattern_or_patterns in patterns.items():
        if isinstance(pattern_or_patterns, list):
            if any(pattern.search(text) for pattern in pattern_or_patterns):
                found.append(kw)
        elif pattern_or_patterns.search(text):
            found.append(kw)
    return found


def iter_search_queries() -> List[str]:
    """Retorna consultas únicas preservando a ordem definida no script."""
    queries = []
    for arch_queries in ARCHITECTURE_QUERIES.values():
        queries.extend(arch_queries)
    queries.extend(GENERAL_SEARCH_QUERIES)
    return list(dict.fromkeys(queries))


def search_questions(query: str, api_key: Optional[str]) -> List[Dict[str, Any]]:
    """Busca perguntas no Stack Overflow para uma consulta SwiftUI específica."""
    questions: List[Dict[str, Any]] = []
    page = 1

    while True:
        params = {
            "site": SITE,
            "tagged": "swiftui",
            "q": query,
            "pagesize": PAGE_SIZE,
            "page": page,
            "order": "desc",
            "sort": "votes",
            "filter": "withbody",
        }
        if api_key:
            params["key"] = api_key

        url = build_url("/search/advanced", params)
        payload = fetch_json(url)

        items = payload.get("items", [])
        questions.extend(items)

        quota_remaining = payload.get("quota_remaining", "?")
        print(f"  página {page} — {len(items)} questões | quota restante: {quota_remaining}")

        if not payload.get("has_more", False) or not items:
            break

        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    return questions


def collect_all_questions(api_key: Optional[str]) -> Dict[int, Dict[str, Any]]:
    """Coleta perguntas únicas que mencionam SwiftUI e arquitetura."""
    questions_by_id: Dict[int, Dict[str, Any]] = {}

    for query in iter_search_queries():
        print(f"\nQuery: {query!r}")
        raw_questions = search_questions(query, api_key)

        for q in raw_questions:
            qid = q.get("question_id")
            if not qid:
                continue

            full_text = q.get("title", "") + "\n" + q.get("body", "")
            arch_hits = find_keywords(full_text, ARCH_PATTERNS)
            if not arch_hits:
                continue

            swiftui_hits = find_keywords(full_text, SWIFTUI_PATTERNS)
            if not swiftui_hits:
                swiftui_hits = ["swiftui (tag)"]

            if qid in questions_by_id:
                matched_queries = set(questions_by_id[qid]["matched_search_queries"].split(";"))
                matched_queries.add(query)
                questions_by_id[qid]["matched_search_queries"] = ";".join(sorted(matched_queries))
                continue

            questions_by_id[qid] = {
                "question_id": qid,
                "matched_search_queries": query,
                "title": q.get("title", ""),
                "body": q.get("body", ""),
                "tags": ",".join(q.get("tags", [])),
                "score": q.get("score", 0),
                "answer_count": q.get("answer_count", 0),
                "view_count": q.get("view_count", 0),
                "is_answered": q.get("is_answered", False),
                "accepted_answer_id": q.get("accepted_answer_id", ""),
                "author": q.get("owner", {}).get("display_name", ""),
                "created_iso": datetime.fromtimestamp(
                    q.get("creation_date", 0), tz=timezone.utc
                ).isoformat(),
                "last_activity_iso": datetime.fromtimestamp(
                    q.get("last_activity_date", 0), tz=timezone.utc
                ).isoformat(),
                "link": q.get("link", ""),
                "matched_arch_keywords": ",".join(sorted(set(arch_hits))),
                "matched_swiftui_keywords": ",".join(sorted(set(swiftui_hits))),
            }

    print(f"\nTOTAL de questões únicas coletadas: {len(questions_by_id)}")
    return questions_by_id


def fetch_answers_for_questions(
    question_ids: List[int],
    api_key: Optional[str],
    batch_size: int = 30,
) -> List[Dict[str, Any]]:
    """Busca respostas das perguntas coletadas e filtra menções a arquitetura."""
    all_answers: List[Dict[str, Any]] = []

    for i in range(0, len(question_ids), batch_size):
        batch = question_ids[i : i + batch_size]
        ids_str = ";".join(str(qid) for qid in batch)
        print(f"Buscando respostas para questões {i+1}–{i+len(batch)}...")

        params = {
            "site": SITE,
            "pagesize": PAGE_SIZE,
            "order": "desc",
            "sort": "votes",
            "filter": "withbody",
        }
        if api_key:
            params["key"] = api_key

        url = build_url(f"/questions/{ids_str}/answers", params)
        payload = fetch_json(url)

        for ans in payload.get("items", []):
            full_text = ans.get("body", "")
            arch_hits = find_keywords(full_text, ARCH_PATTERNS)
            if not arch_hits:
                continue

            all_answers.append(
                {
                    "answer_id": ans.get("answer_id", ""),
                    "question_id": ans.get("question_id", ""),
                    "body": full_text,
                    "score": ans.get("score", 0),
                    "is_accepted": ans.get("is_accepted", False),
                    "author": ans.get("owner", {}).get("display_name", ""),
                    "created_iso": datetime.fromtimestamp(
                        ans.get("creation_date", 0), tz=timezone.utc
                    ).isoformat(),
                    "last_activity_iso": datetime.fromtimestamp(
                        ans.get("last_activity_date", 0), tz=timezone.utc
                    ).isoformat(),
                    "link": ans.get("link", ""),
                    "matched_arch_keywords": ",".join(sorted(set(arch_hits))),
                }
            )

        quota_remaining = payload.get("quota_remaining", "?")
        print(f"  respostas com menção a arquitetura: {len(all_answers)} | quota: {quota_remaining}")
        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"\nTOTAL de respostas coletadas (após filtro): {len(all_answers)}")
    return all_answers


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
    """Executa a coleta de perguntas e respostas SwiftUI no Stack Overflow."""
    DATA_RAW_SO_DIR.mkdir(parents=True, exist_ok=True)

    api_key = load_api_key()
    questions_by_id = collect_all_questions(api_key)

    questions = list(questions_by_id.values())
    save_dicts_to_csv(
        questions,
        DATA_RAW_SO_DIR / "stackoverflow_swiftui_questions.csv",
    )

    question_ids = list(questions_by_id.keys())
    answers = fetch_answers_for_questions(question_ids, api_key)
    save_dicts_to_csv(
        answers,
        DATA_RAW_SO_DIR / "stackoverflow_swiftui_answers.csv",
    )
    print("\nResumo da coleta Stack Overflow:")
    print(f"  Total de perguntas coletadas: {len(questions)}")
    print(f"  Total de respostas coletadas: {len(answers)}")
    print(f"  Total de registros Q&A coletados: {len(questions) + len(answers)}")


if __name__ == "__main__":
    main()
