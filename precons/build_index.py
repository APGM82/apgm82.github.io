#!/usr/bin/env python3
"""
Genera el índice ligero de mazos preconstruidos para la app "Mana - MTG Archive".

Descarga el paquete oficial de mazos de MTGJSON (AllDeckFiles.zip) y, por cada mazo, extrae solo
lo necesario para una lista rica pero ligera: fileName, nombre, tipo, edición, fecha, identidad de
color (de colorIdentity) y el id de una carta de portada. NO guarda las listas de cartas, así que
el índice resultante es pequeño (~0,5 MB). Las cartas de cada mazo las baja la app bajo demanda.

Salida (junto a este script): index.json y version.json.
"""
import io
import json
import os
import sys
import urllib.request
import zipfile

ALL_DECKS_URL = "https://mtgjson.com/api/v5/AllDeckFiles.zip"
META_URL = "https://mtgjson.com/api/v5/Meta.json"
WUBRG = ["W", "U", "B", "R", "G"]
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Tipos de MTGJSON que SÍ son mazos jugables -> categoría de la app. Los tipos NO listados aquí
# (Secret Lair Drop, MTGO Redemption, Box Set, promos, boosters, toolkits, Shandalar, Sample/Demo,
# land packs...) se EXCLUYEN del índice: no son mazos preconstruidos jugables.
CATEGORY = {
    "Commander Deck": "commander",
    "MTGO Commander Deck": "commander",
    "Brawl Deck": "brawl",
    "Historic Brawl Precon Deck": "brawl",
    "Planeswalker Deck": "planeswalker",
    "Theme Deck": "theme",
    "MTGO Theme Deck": "theme",
    "Intro Pack": "theme",
    "Challenger Deck": "challenger",
    "Pioneer Challenger Deck": "challenger",
    "Event Deck": "challenger",
    "Modern Event Deck": "challenger",
    "Starter Deck": "starter",
    "Arena Starter Deck": "starter",
    "Welcome Deck": "starter",
    "Starter Kit": "starter",
    "Arena Starter Kit": "starter",
    "Spellslinger Starter Kit": "starter",
    "Duel Deck": "duel",
    "MTGO Duel Deck": "duel",
    "Duel Of The Planeswalkers Deck": "duel",
    "Jumpstart": "jumpstart",
    "Planechase Deck": "other",
    "Archenemy Deck": "other",
    "Guild Kit": "other",
    "Game Night Deck": "other",
    "World Championship Deck": "other",
    "Pro Tour Deck": "other",
    "Clash Pack": "other",
    "Premium Deck": "other",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "mana-precon-index/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return resp.read()


def color_identity(cards) -> str:
    present = set()
    for card in cards:
        for color in card.get("colorIdentity", []) or []:
            present.add(color)
    return "".join(c for c in WUBRG if c in present)


def cover_id(commander, mainboard):
    """Carta de portada: el comandante; si no, la no-tierra de mayor coste; si no, la primera."""
    for card in commander:
        sid = (card.get("identifiers") or {}).get("scryfallId")
        if sid:
            return sid
    best, best_mv, first = None, -1.0, None
    for card in mainboard:
        sid = (card.get("identifiers") or {}).get("scryfallId")
        if not sid:
            continue
        if first is None:
            first = sid
        if "Land" in (card.get("type") or ""):
            continue
        mv = card.get("manaValue") or 0
        if mv > best_mv:
            best_mv, best = mv, sid
    return best or first


def main() -> int:
    meta = json.loads(fetch(META_URL))
    version = (meta.get("data") or meta.get("meta") or {}).get("date")

    raw = fetch(ALL_DECKS_URL)
    decks = []
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".json"):
                continue
            try:
                with zf.open(name) as f:
                    data = (json.load(f) or {}).get("data") or {}
            except Exception as exc:  # noqa: BLE001 - un mazo ilegible no debe tumbar el índice
                print(f"skip {name}: {exc}", file=sys.stderr)
                continue
            if not data.get("name"):
                continue
            cat = CATEGORY.get(data.get("type", ""))
            if cat is None:
                continue  # no es un mazo jugable: fuera del índice
            commander = data.get("commander") or []
            mainboard = data.get("mainBoard") or []
            decks.append({
                "f": os.path.basename(name)[:-5],  # quita ".json"
                "n": data.get("name", ""),
                "t": data.get("type", ""),
                "cat": cat,
                "s": (data.get("code") or "").upper(),
                "d": data.get("releaseDate"),
                "c": color_identity(commander + mainboard),
                "img": cover_id(commander, mainboard),
            })

    decks.sort(key=lambda d: (d["d"] or ""), reverse=True)
    index = {"version": version, "count": len(decks), "decks": decks}
    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT_DIR, "version.json"), "w", encoding="utf-8") as f:
        json.dump({"version": version, "count": len(decks)}, f, ensure_ascii=False)

    print(f"OK: {len(decks)} mazos, versión {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
