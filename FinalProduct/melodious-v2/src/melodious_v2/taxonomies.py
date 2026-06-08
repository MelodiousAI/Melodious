"""Taxonomy definitions for full detection and semantic assembly."""

from __future__ import annotations

from dataclasses import dataclass


DEEPSCORES_136_CLASS_NAMES = [
    "brace",
    "ledgerLine",
    "repeatDot",
    "segno",
    "coda",
    "clefG",
    "clefCAlto",
    "clefCTenor",
    "clefF",
    "clefUnpitchedPercussion",
    "clef8",
    "clef15",
    "timeSig0",
    "timeSig1",
    "timeSig2",
    "timeSig3",
    "timeSig4",
    "timeSig5",
    "timeSig6",
    "timeSig7",
    "timeSig8",
    "timeSig9",
    "timeSigCommon",
    "timeSigCutCommon",
    "noteheadBlackOnLine",
    "noteheadBlackOnLineSmall",
    "noteheadBlackInSpace",
    "noteheadBlackInSpaceSmall",
    "noteheadHalfOnLine",
    "noteheadHalfOnLineSmall",
    "noteheadHalfInSpace",
    "noteheadHalfInSpaceSmall",
    "noteheadWholeOnLine",
    "noteheadWholeOnLineSmall",
    "noteheadWholeInSpace",
    "noteheadWholeInSpaceSmall",
    "noteheadDoubleWholeOnLine",
    "noteheadDoubleWholeOnLineSmall",
    "noteheadDoubleWholeInSpace",
    "noteheadDoubleWholeInSpaceSmall",
    "augmentationDot",
    "stem",
    "tremolo1",
    "tremolo2",
    "tremolo3",
    "tremolo4",
    "tremolo5",
    "flag8thUp",
    "flag8thUpSmall",
    "flag16thUp",
    "flag32ndUp",
    "flag64thUp",
    "flag128thUp",
    "flag8thDown",
    "flag8thDownSmall",
    "flag16thDown",
    "flag32ndDown",
    "flag64thDown",
    "flag128thDown",
    "accidentalFlat",
    "accidentalFlatSmall",
    "accidentalNatural",
    "accidentalNaturalSmall",
    "accidentalSharp",
    "accidentalSharpSmall",
    "accidentalDoubleSharp",
    "accidentalDoubleFlat",
    "keyFlat",
    "keyNatural",
    "keySharp",
    "articAccentAbove",
    "articAccentBelow",
    "articStaccatoAbove",
    "articStaccatoBelow",
    "articTenutoAbove",
    "articTenutoBelow",
    "articStaccatissimoAbove",
    "articStaccatissimoBelow",
    "articMarcatoAbove",
    "articMarcatoBelow",
    "fermataAbove",
    "fermataBelow",
    "caesura",
    "restDoubleWhole",
    "restWhole",
    "restHalf",
    "restQuarter",
    "rest8th",
    "rest16th",
    "rest32nd",
    "rest64th",
    "rest128th",
    "restHNr",
    "dynamicP",
    "dynamicM",
    "dynamicF",
    "dynamicS",
    "dynamicZ",
    "dynamicR",
    "graceNoteAcciaccaturaStemUp",
    "graceNoteAppoggiaturaStemUp",
    "graceNoteAcciaccaturaStemDown",
    "graceNoteAppoggiaturaStemDown",
    "ornamentTrill",
    "ornamentTurn",
    "ornamentTurnInverted",
    "ornamentMordent",
    "stringsDownBow",
    "stringsUpBow",
    "arpeggiato",
    "keyboardPedalPed",
    "keyboardPedalUp",
    "tuplet3",
    "tuplet6",
    "fingering0",
    "fingering1",
    "fingering2",
    "fingering3",
    "fingering4",
    "fingering5",
    "slur",
    "beam",
    "tie",
    "restHBar",
    "dynamicCrescendoHairpin",
    "dynamicDiminuendoHairpin",
    "tuplet1",
    "tuplet2",
    "tuplet4",
    "tuplet5",
    "tuplet7",
    "tuplet8",
    "tuplet9",
    "tupletBracket",
    "staff",
    "ottavaBracket",
]

DEEPSCORES_136_NAME_TO_ID = {
    name: idx for idx, name in enumerate(DEEPSCORES_136_CLASS_NAMES)
}

SEMANTIC_GROUPS = [
    "clef",
    "notehead",
    "stem",
    "beam",
    "flag",
    "rest",
    "accidental",
    "key_signature",
    "time_signature",
    "articulation",
    "dynamic",
    "ornament",
    "connector",
    "tuplet",
    "staff",
    "ledger",
    "bar_or_repeat",
    "other",
]


@dataclass(frozen=True)
class Taxonomy:
    """Named taxonomy used by detector and assembly code."""

    taxonomy_id: str
    class_names: list[str]

    @property
    def name_to_id(self) -> dict[str, int]:
        return {name: idx for idx, name in enumerate(self.class_names)}


DEEPSCORES_136 = Taxonomy(
    taxonomy_id="deepscores_136",
    class_names=DEEPSCORES_136_CLASS_NAMES,
)


def semantic_group_for_class(class_name: str) -> str:
    """Map a full detector class name into an assembly/export semantic group."""
    lower = class_name.lower()

    if "clef" in lower:
        return "clef"
    if "notehead" in lower or "gracenote" in lower:
        return "notehead"
    if lower == "stem":
        return "stem"
    if lower == "beam":
        return "beam"
    if lower.startswith("flag"):
        return "flag"
    if lower.startswith("rest"):
        return "rest"
    if lower.startswith("accidental"):
        return "accidental"
    if lower.startswith("key"):
        return "key_signature"
    if lower.startswith("timesig"):
        return "time_signature"
    if lower.startswith("artic") or "fermata" in lower or lower == "caesura":
        return "articulation"
    if lower.startswith("dynamic"):
        return "dynamic"
    if lower.startswith("ornament") or "trill" in lower:
        return "ornament"
    if lower in {"slur", "tie"}:
        return "connector"
    if lower.startswith("tuplet"):
        return "tuplet"
    if lower == "staff":
        return "staff"
    if lower == "ledgerline":
        return "ledger"
    if lower in {"repeatdot", "segno", "coda"}:
        return "bar_or_repeat"
    return "other"


SEMANTIC_OMR_V2_CLASS_MAP = {
    name: semantic_group_for_class(name) for name in DEEPSCORES_136_CLASS_NAMES
}


def validate_taxonomies() -> None:
    """Fail fast if the full taxonomy drifts from the expected 136 classes."""
    if len(DEEPSCORES_136_CLASS_NAMES) != 136:
        raise ValueError("deepscores_136 must contain exactly 136 classes.")
    if len(set(DEEPSCORES_136_CLASS_NAMES)) != 136:
        raise ValueError("deepscores_136 contains duplicate class names.")

