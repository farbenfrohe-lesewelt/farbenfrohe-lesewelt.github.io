from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mention_radar.classifier import classify
from mention_radar.crawler import MentionCrawler
from mention_radar.exporters import export_all
from mention_radar.history import apply_tracking, load_tracking, tracking_path, write_tracking
from mention_radar.models import Candidate, Seed
from mention_radar.safety import (
    dedupe_urls,
    default_run_dir,
    extract_urls_from_csv,
    load_config,
    normalize_url,
    read_feed_list,
    read_seed_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lokales Werkzeug fuer menschengepruefte redaktionelle Erwaehnungsmoeglichkeiten.")
    parser.add_argument("--config", default="", help="Pfad zu einer YAML-Konfiguration.")
    parser.add_argument("--input-csv", default="", help="Manuell gepflegte CSV mit Spalte url.")
    parser.add_argument("--import-csv", default="", help="CSV-Export aus Browser oder Suchwerkzeug; URLs werden daraus gelesen.")
    parser.add_argument("--feed", action="append", default=[], help="Oeffentlicher RSS- oder Atom-Feed.")
    parser.add_argument("--feed-list", default="", help="Textdatei mit einer Feed-URL pro Zeile.")
    parser.add_argument("--url", action="append", default=[], help="Einzelne ausdruecklich uebergebene oeffentliche URL.")
    parser.add_argument("--output-dir", default="", help="Expliziter lokaler Ausgabeordner. Ohne Angabe wird ein datierter Run erzeugt.")
    parser.add_argument("--no-drafts", action="store_true", help="Keine Entwurfsdateien erzeugen.")
    return parser


def collect_seeds(args: argparse.Namespace, crawler: MentionCrawler) -> list[Seed]:
    seeds: list[Seed] = []
    if args.input_csv:
        seeds.extend(read_seed_csv(args.input_csv))
    if args.import_csv:
        seeds.extend(Seed(url=url, source="csv-import") for url in extract_urls_from_csv(args.import_csv))
    for url in args.url:
        seeds.append(Seed(url=normalize_url(url), source="single-url"))
    feed_urls = list(args.feed or [])
    if args.feed_list:
        feed_urls.extend(read_feed_list(args.feed_list))
    for feed_url in dedupe_urls(feed_urls):
        for url in crawler.parse_feed(feed_url):
            seeds.append(Seed(url=normalize_url(url), source="feed", notes=feed_url))
    unique_urls = dedupe_urls(seed.url for seed in seeds)
    by_url = {seed.url: seed for seed in seeds if seed.url}
    return [by_url.get(url, Seed(url=url)) for url in unique_urls]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config or None)
    output_dir = Path(args.output_dir) if args.output_dir else default_run_dir(config.get("output_dir", "local-data/mention-radar"))
    crawler = MentionCrawler(config)
    seeds = collect_seeds(args, crawler)
    if not seeds:
        print("Keine Eingaben gefunden. Nutzen Sie --input-csv, --import-csv, --feed, --feed-list oder --url.", file=sys.stderr)
        return 2

    fetches = []
    for seed in seeds:
        fetches.extend(crawler.fetch_seed_with_follow(seed.url))

    candidates_by_url: dict[str, Candidate] = {}
    class_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    for fetch in fetches:
        seed_name = next((seed.name for seed in seeds if seed.url == fetch.seed_url and seed.name), "")
        candidate = classify(fetch, seed_name)
        existing = candidates_by_url.get(candidate.relevant_page)
        if existing is None or (class_rank.get(candidate.candidate_class, 9), -candidate.score) < (class_rank.get(existing.candidate_class, 9), -existing.score):
            candidates_by_url[candidate.relevant_page] = candidate
    candidates = list(candidates_by_url.values())

    track_file = tracking_path("local-data/mention-radar")
    tracking = load_tracking(track_file)
    new_count, known_count = apply_tracking(candidates, tracking)
    export_all(candidates, output_dir, generate_drafts=not args.no_drafts and bool(config.get("generate_drafts", True)))
    write_tracking(candidates, track_file, tracking)

    successful = sum(1 for fetch in fetches if fetch.status_code and not fetch.error and not fetch.skipped_reason)
    robots_skipped = sum(1 for fetch in fetches if "robots.txt" in fetch.skipped_reason)
    technical_errors = sum(1 for fetch in fetches if fetch.error)
    print("Mention Radar Zusammenfassung")
    print(f"Eingegebene Seeds: {len(seeds)}")
    print(f"Erfolgreich abgerufen: {successful}")
    print(f"Durch robots.txt uebersprungen: {robots_skipped}")
    print(f"Technische Fehler: {technical_errors}")
    print(f"Klasse A: {sum(1 for item in candidates if item.candidate_class == 'A')}")
    print(f"Klasse B: {sum(1 for item in candidates if item.candidate_class == 'B')}")
    print(f"Klasse C: {sum(1 for item in candidates if item.candidate_class == 'C')}")
    print(f"Klasse D: {sum(1 for item in candidates if item.candidate_class == 'D')}")
    print(f"Neu gegenueber frueheren Laeufen: {new_count}")
    print(f"Bereits bekannte Kandidaten: {known_count}")
    print(f"Run-Ordner: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
