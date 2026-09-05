"""The Redivis destinations red_up can upload to, and how it guesses one.

There is deliberately no dataset list in this file. `metadata/redivis_config.R`
is already authoritative for the owner and the dataset names (ARCHITECTURE.md
section 5), and the project already carries three files that each call
themselves the single source of truth -- they have drifted once (#1733). So
this module *parses* the R file rather than restating it, and raises rather
than guessing if it cannot.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: Filenames matching this go to the item-text dataset, never to a shard.
ITEMS_SUFFIX = "__items.csv"

#: How each non-core dataset is labelled in the menu. Keys are the `source`
#: names `redivis_config.R` uses. Note "pairs" is `irw_competitions`: there is
#: no `irw_pairs` dataset and never has been.
#:
#: "text" is the odd one out: item text is a *shard list*
#: (`IRW_TEXT_DATASETS`), not an entry in `IRW_AUX_DATASETS`, for the same
#: reason the core warehouses are a list -- Redivis caps a dataset at 1000
#: tables. Its label still lives here so the menu reads uniformly.
AUX_LABELS = {
    "text": "item text (__items.csv)",
    "meta": "metadata tables",
    "nom": "nominal",
    "comp": "pairs / competitions",
    "sim": "simulated + synthetic",
}


class ConfigError(RuntimeError):
    """redivis_config.R could not be located or parsed."""


@dataclass(frozen=True)
class Target:
    """One Redivis dataset the uploader can write to."""

    name: str          # the Redivis dataset name, e.g. "item_response_warehouse_6"
    label: str         # what the menu shows
    kind: str          # "core" | "aux"
    source: str | None = None   # the aux `source` key ("text", "meta", ...), else None

    @property
    def is_itemtext(self) -> bool:
        return self.source == "text"

    @property
    def is_meta(self) -> bool:
        return self.source == "meta"


def find_config(start: Path | None = None) -> Path:
    """Locate metadata/redivis_config.R by walking up from this file.

    Walking up from `__file__` (not from the cwd) is deliberate: red_up is
    meant to run from any directory, so the config must be found relative to
    the installed package, which lives inside the `src` checkout.
    """
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        candidate = parent / "metadata" / "redivis_config.R"
        if candidate.is_file():
            return candidate
    raise ConfigError(
        "Could not find metadata/redivis_config.R above "
        f"{here}. red_up must be installed from the `src` checkout so it can "
        "read the authoritative dataset list."
    )


def _parse_char_vector(text: str, symbol: str) -> list[tuple[str | None, str]]:
    """Pull `SYMBOL <- c("a", "b")` or `c(k = "a", ...)` out of R source.

    Returns (name_or_None, value) pairs in file order. Comments are stripped
    first so a commented-out dataset name is not picked up as a live one.
    """
    match = re.search(rf"^{re.escape(symbol)}\s*<-\s*c\((.*?)\)", text, re.S | re.M)
    if not match:
        raise ConfigError(f"{symbol} not found in redivis_config.R")
    body = re.sub(r"#[^\n]*", "", match.group(1))
    pairs = re.findall(r"(?:(\w+)\s*=\s*)?[\"']([^\"']+)[\"']", body)
    out = [(key or None, value) for key, value in pairs]
    if not out:
        raise ConfigError(f"{symbol} in redivis_config.R parsed to nothing")
    return out


def load_registry(config_path: Path | None = None) -> tuple[str, list[Target]]:
    """Return (owner, targets) read from redivis_config.R.

    Core shards come first, oldest to newest, then the aux datasets in the
    order AUX_LABELS declares (so the menu reads text/meta/nominal/pairs/sim
    rather than whatever order the R file happens to use).
    """
    path = config_path or find_config()
    text = path.read_text()

    owner_match = re.search(r"^IRW_OWNER\s*<-\s*[\"']([^\"']+)[\"']", text, re.M)
    if not owner_match:
        raise ConfigError(f"IRW_OWNER not found in {path}")
    owner = owner_match.group(1)

    targets = [
        Target(name=value, label="response data", kind="core")
        for _, value in _parse_char_vector(text, "IRW_CORE_DATASETS")
    ]
    if not targets:
        raise ConfigError("IRW_CORE_DATASETS is empty")
    targets[-1] = Target(
        name=targets[-1].name, label="response data (newest shard)", kind="core"
    )

    # Item-text shards, appended before the other aux datasets so the menu
    # still reads text / meta / nominal / pairs / sim.
    text_shards = [
        Target(name=value, label=AUX_LABELS["text"], kind="aux", source="text")
        for _, value in _parse_char_vector(text, "IRW_TEXT_DATASETS")
    ]
    if not text_shards:
        raise ConfigError("IRW_TEXT_DATASETS is empty")
    if len(text_shards) > 1:
        text_shards[-1] = Target(
            name=text_shards[-1].name,
            label=f"{AUX_LABELS['text']} -- newest shard",
            kind="aux", source="text",
        )
    targets.extend(text_shards)

    aux = dict(
        (key, value)
        for key, value in _parse_char_vector(text, "IRW_AUX_DATASETS")
        if key
    )
    if "text" in aux:
        # Declared in two places, which is how the three "single source of
        # truth" files drifted before (#1733). Refuse rather than pick one.
        raise ConfigError(
            "redivis_config.R declares item text twice: `text` is a key in "
            "IRW_AUX_DATASETS and IRW_TEXT_DATASETS also exists. Item text is a "
            "shard list -- remove the `text =` entry from IRW_AUX_DATASETS."
        )
    unknown = set(aux) - set(AUX_LABELS)
    if unknown:
        raise ConfigError(
            f"redivis_config.R has aux source(s) red_up does not know: "
            f"{sorted(unknown)}. Add them to AUX_LABELS in targets.py."
        )
    for source, label in AUX_LABELS.items():
        if source != "text" and source in aux:
            targets.append(
                Target(name=aux[source], label=label, kind="aux", source=source)
            )
    return owner, targets


def newest_shard(targets: list[Target]) -> Target:
    """The shard new response data goes to by default."""
    core = [t for t in targets if t.kind == "core"]
    if not core:
        raise ConfigError("no core shards in the registry")
    return core[-1]


def text_shards(targets: list[Target]) -> list[Target]:
    """Every item-text shard, oldest to newest."""
    return [t for t in targets if t.is_itemtext]


def newest_text_shard(targets: list[Target]) -> Target | None:
    """The shard new item text goes to by default."""
    shards = text_shards(targets)
    return shards[-1] if shards else None


def itemtext_target(targets: list[Target]) -> Target | None:
    """The item-text destination: the newest shard.

    Uploading into an *older* text shard would be the shadowing bug in reverse
    -- clients resolve newest-first, so a table written to shard 1 while shard 2
    holds a copy stays invisible.
    """
    return newest_text_shard(targets)


#: Columns a table must have to belong in a given destination.
#:
#: Response data (the shards, plus nominal and simsyn) is `datastandard.md`'s
#: schema. Item text is the shape `itemtext/join.R` writes. Two destinations
#: are deliberately unchecked: `irw_competitions` holds pairwise/arena data
#: whose columns vary by sport and source, and `irw_meta` holds thirteen
#: pipeline outputs that each have their own schema -- membership in that fixed
#: list is the gate there, not a column set.
REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "response": ("id", "item", "resp"),
    "text": ("table", "item", "item_text"),
    "comp": (),
    "meta": (),
}


def required_columns(target: Target) -> tuple[str, ...]:
    return REQUIRED_COLUMNS.get(target.source or "response",
                                REQUIRED_COLUMNS["response"])


def eligible(path: Path, target: Target) -> str | None:
    """Why `path` must not go to `target`, or None if it may.

    This is the guard against the failure that `itemtext/itemtables/clean/`
    exists to clean up after: the old uploaders walked a directory and turned
    *every* .csv into a Redivis table, so a `notes.csv` or `provenance.csv`
    sitting beside the real output became a table. Those files legitimately
    live in item-text batch directories, so they are excluded rather than
    treated as an error -- but they are always named on screen, never dropped
    quietly.
    """
    is_items = path.name.endswith(ITEMS_SUFFIX)
    if target.is_itemtext and not is_items:
        return f"not {ITEMS_SUFFIX} -- {target.name} holds item text only"
    if not target.is_itemtext and is_items:
        return f"{ITEMS_SUFFIX} is item text, not response data"
    return None


def guess_target(files: list[Path], targets: list[Target]) -> Target:
    """Pick the default destination from the filenames.

    *Any* `*__items.csv` present means this is an item-text directory --
    response-data batches never contain one, whereas item-text batches
    routinely carry a `provenance.csv`, `notes.csv` and `audit_report.csv`
    alongside the real output. Guessing by majority would send those three to
    a warehouse shard. Everything that does not fit the chosen target is
    excluded by `eligible` and listed.
    """
    if any(f.name.endswith(ITEMS_SUFFIX) for f in files):
        target = itemtext_target(targets)
        if target is None:
            raise ConfigError("no item-text dataset in redivis_config.R")
        return target
    return newest_shard(targets)
