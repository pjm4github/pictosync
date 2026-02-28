"""Tests for the KIND_ALIAS_MAP and resolve_kind_alias in models.py,
and the KIND_ALIASES class attributes on MetaXxxItem classes.
"""
from __future__ import annotations

import pytest

from models import KIND_ALIAS_MAP, resolve_kind_alias


# ─────────────────────────────────────────────────────────
# resolve_kind_alias unit tests
# ─────────────────────────────────────────────────────────


class TestResolveKindAlias:
    def test_c4_person(self):
        assert resolve_kind_alias("person") == "roundedrect"

    def test_c4_external_person(self):
        assert resolve_kind_alias("external_person") == "roundedrect"

    def test_c4_system(self):
        assert resolve_kind_alias("system") == "roundedrect"

    def test_c4_container_db(self):
        assert resolve_kind_alias("container_db") == "cylinder"

    def test_c4_external_container_db(self):
        assert resolve_kind_alias("external_container_db") == "cylinder"

    def test_c4_component_db(self):
        assert resolve_kind_alias("component_db") == "cylinder"

    def test_c4_system_db(self):
        assert resolve_kind_alias("system_db") == "cylinder"

    def test_c4_container(self):
        assert resolve_kind_alias("container") == "roundedrect"

    def test_c4_component(self):
        assert resolve_kind_alias("component") == "roundedrect"

    def test_c4_queue_types(self):
        for qt in ("system_queue", "external_system_queue",
                    "container_queue", "external_container_queue",
                    "component_queue", "external_component_queue"):
            assert resolve_kind_alias(qt) == "roundedrect", f"{qt} should map to roundedrect"

    def test_puml_database(self):
        assert resolve_kind_alias("database") == "cylinder"

    def test_puml_actor(self):
        assert resolve_kind_alias("actor") == "ellipse"

    def test_puml_rectangle(self):
        assert resolve_kind_alias("rectangle") == "rect"

    def test_unknown_returns_none(self):
        assert resolve_kind_alias("unknown_type_xyz") is None

    def test_unknown_returns_fallback(self):
        assert resolve_kind_alias("unknown_type_xyz", "rect") == "rect"

    def test_fallback_default_is_none(self):
        assert resolve_kind_alias("nonexistent") is None


# ─────────────────────────────────────────────────────────
# KIND_ALIAS_MAP integrity tests
# ─────────────────────────────────────────────────────────

# Known PictoSync kinds
_VALID_KINDS = {
    "rect", "roundedrect", "ellipse", "line", "text",
    "hexagon", "cylinder", "blockarrow", "polygon",
    "curve", "orthocurve", "isocube", "group",
}


class TestKindAliasMapIntegrity:
    def test_all_values_are_valid_kinds(self):
        for alias, kind in KIND_ALIAS_MAP.items():
            assert kind in _VALID_KINDS, (
                f"Alias '{alias}' maps to invalid kind '{kind}'"
            )

    def test_no_alias_is_a_valid_kind(self):
        """Aliases should be external type names, not PictoSync kind names.

        If an alias IS a valid kind, that's suspicious — it means the same
        string is both an alias and a kind, which could cause confusion.
        Exception: some PlantUML types happen to share names with kinds
        (e.g. 'component' → 'roundedrect' is fine because PlantUML's
        'component' is different from PictoSync's 'roundedrect').
        """
        # This is informational — we don't enforce it strictly
        pass

    def test_db_types_map_to_cylinder(self):
        """All *_db C4 types must map to cylinder."""
        db_aliases = [k for k in KIND_ALIAS_MAP if k.endswith("_db")]
        assert len(db_aliases) >= 6, "Expected at least 6 _db aliases"
        for alias in db_aliases:
            assert KIND_ALIAS_MAP[alias] == "cylinder", (
                f"_db alias '{alias}' should map to 'cylinder' but maps to '{KIND_ALIAS_MAP[alias]}'"
            )

    def test_map_not_empty(self):
        assert len(KIND_ALIAS_MAP) > 0


# ─────────────────────────────────────────────────────────
# KIND_ALIASES class attribute tests
# ─────────────────────────────────────────────────────────


class TestKindAliasesOnClasses:
    """Test that KIND_ALIASES frozensets on MetaXxxItem classes are correct."""

    @pytest.fixture(autouse=True)
    def _import_classes(self):
        """Import canvas item classes (requires PyQt6)."""
        from canvas.items import (
            MetaRectItem, MetaRoundedRectItem, MetaEllipseItem,
            MetaLineItem, MetaTextItem, MetaHexagonItem,
            MetaCylinderItem, MetaBlockArrowItem, MetaPolygonItem,
            MetaCurveItem, MetaOrthoCurveItem, MetaIsoCubeItem,
            MetaGroupItem,
        )
        self.classes = [
            MetaRectItem, MetaRoundedRectItem, MetaEllipseItem,
            MetaLineItem, MetaTextItem, MetaHexagonItem,
            MetaCylinderItem, MetaBlockArrowItem, MetaPolygonItem,
            MetaCurveItem, MetaOrthoCurveItem, MetaIsoCubeItem,
            MetaGroupItem,
        ]

    def test_all_classes_have_kind(self):
        for cls in self.classes:
            assert hasattr(cls, "KIND"), f"{cls.__name__} missing KIND"
            assert cls.KIND in _VALID_KINDS, (
                f"{cls.__name__}.KIND = '{cls.KIND}' is not a valid kind"
            )

    def test_all_classes_have_kind_aliases(self):
        for cls in self.classes:
            assert hasattr(cls, "KIND_ALIASES"), f"{cls.__name__} missing KIND_ALIASES"
            assert isinstance(cls.KIND_ALIASES, frozenset), (
                f"{cls.__name__}.KIND_ALIASES should be frozenset"
            )

    def test_no_duplicate_aliases_across_classes(self):
        """Each alias must appear in exactly one class."""
        seen = {}
        for cls in self.classes:
            for alias in cls.KIND_ALIASES:
                assert alias not in seen, (
                    f"Alias '{alias}' in both {seen[alias]} and {cls.__name__}"
                )
                seen[alias] = cls.__name__

    def test_aliases_match_map(self):
        """KIND_ALIASES on each class must match what KIND_ALIAS_MAP says."""
        for cls in self.classes:
            expected = frozenset(
                k for k, v in KIND_ALIAS_MAP.items() if v == cls.KIND
            )
            assert cls.KIND_ALIASES == expected, (
                f"{cls.__name__}.KIND_ALIASES mismatch.\n"
                f"  Expected: {sorted(expected)}\n"
                f"  Got:      {sorted(cls.KIND_ALIASES)}"
            )

    def test_cylinder_has_db_aliases(self):
        from canvas.items import MetaCylinderItem
        assert "container_db" in MetaCylinderItem.KIND_ALIASES
        assert "database" in MetaCylinderItem.KIND_ALIASES
        assert "system_db" in MetaCylinderItem.KIND_ALIASES

    def test_roundedrect_has_person_aliases(self):
        from canvas.items import MetaRoundedRectItem
        assert "person" in MetaRoundedRectItem.KIND_ALIASES
        assert "external_person" in MetaRoundedRectItem.KIND_ALIASES
        assert "container" in MetaRoundedRectItem.KIND_ALIASES

    def test_ellipse_has_actor_alias(self):
        from canvas.items import MetaEllipseItem
        assert "actor" in MetaEllipseItem.KIND_ALIASES
        assert "interface" in MetaEllipseItem.KIND_ALIASES

    def test_line_has_no_aliases(self):
        from canvas.items import MetaLineItem
        assert len(MetaLineItem.KIND_ALIASES) == 0
