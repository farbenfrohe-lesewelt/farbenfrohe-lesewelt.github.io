from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mention_radar.classifier import classify
from mention_radar.crawler import MentionCrawler
from mention_radar.exporters import export_all
from mention_radar.models import Seed
from mention_radar.safety import dedupe_urls, extract_urls_from_csv, load_config, normalize_url, read_seed_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lokales Werkzeug für menschengeprüfte redaktionelle Erwähnungsmöglichkeiten.")
    parser.add_argument("--config", default="", help="Pfad zu einer YAML-Konfiguration.")
    parser.add_argument("--input-csv", default="", help="Manuell gepflegte CSV mit Spalte url.")
    parser.add_argument("--import-csv", default="", help="CSV-Export aus Browser oder Suchwerkzeug; URLs werden daraus gelesen.")
    parser.add_argument("--feed", action="append", default=[], help="Öffentlicher RSS- oder Atom-Feed.")
    parser.add_argument("--url", action="append", default=[], help="Einzelne ausdrücklich übergebene öffentliche URL.")
    parser.add_argument("--output-dir", default="", help="Lokaler Ausgabeordner.")
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
    for feed_url in args.feed:
        for url in crawler.parse_feed(feed_url):
            seeds.append(Seed(url=normalize_url(url), source="feed", notes=feed_url))
    unique_urls = dedupe_urls(seed.url for seed in seeds)
    by_url = {seed.url: seed for seed in seeds if seed.url}
    return [by_url.get(url, Seed(url=url)) for url in unique_urls]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config or None)
    if args.output_dir:
        config["output_dir"] = args.output_dir
    crawler = MentionCrawler(config)
    seeds = collect_seeds(args, crawler)
    if not seeds:
        print("Keine Eingaben gefunden. Nutzen Sie --input-csv, --import-csv, --feed oder --url.", file=sys.stderr)
        return 2
    candidates = []
    for seed in seeds:
        fetch = crawler.fetch(seed.url)
        candidates.append(classify(fetch, seed.name))
    output_dir = Path(config.get("output_dir", "local-data/mention-radar"))
    export_all(candidates, output_dir, generate_drafts=not args.no_drafts and bool(config.get("generate_drafts", True)))
    print(f"Fertig. Ausgaben: {output_dir}")
    print(f"Kandidaten: {len(candidates)}")
    print(f"Klasse A: {sum(1 for item in candidates if item.candidate_class == 'A')}")
    print(f"Klasse B: {sum(1 for item in candidates if item.candidate_class == 'B')}")
    print(f"Ausgeschlossen: {sum(1 for item in candidates if item.candidate_class in {'C', 'D'})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
