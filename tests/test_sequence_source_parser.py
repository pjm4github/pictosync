"""Tests for mermaid/sequence_source_parser.py — Step 1 of the two-step
sequence diagram pipeline.

Validates that sequence diagram source text (.mmd/.mermaid) is correctly
parsed into participants, messages, notes, and blocks.
"""
from __future__ import annotations

import pytest
from mermaid.sequence_source_parser import (
    SeqBlock,
    SeqMessage,
    SeqNote,
    SeqParseResult,
    SeqParticipant,
    parse_sequence_source,
    parse_sequence_source_file,
)


# ═══════════════════════════════════════════════════════════
# Test fixture — parse the test data file
# ═══════════════════════════════════════════════════════════

class TestSequenceFile:
    """Test parsing of the test_data/MERMAID/sequence.mermaid file."""

    @pytest.fixture()
    def result(self) -> SeqParseResult:
        return parse_sequence_source_file("test_data/MERMAID/sequence.mermaid")

    def test_participant_count(self, result):
        assert len(result.participants) == 5

    def test_participant_aliases(self, result):
        aliases = [p.alias for p in result.participants]
        assert aliases == ["web", "blog", "account", "mail", "db"]

    def test_participant_labels(self, result):
        labels = {p.alias: p.label for p in result.participants}
        assert labels["web"] == "Web Browser"
        assert labels["blog"] == "Blog Service"
        assert labels["db"] == "Storage"

    def test_all_are_participants(self, result):
        """All declared participants are 'participant' type (not actor)."""
        for p in result.participants:
            assert p.actor_type == "participant"

    def test_message_count(self, result):
        assert len(result.messages) == 10

    def test_first_message(self, result):
        m = result.messages[0]
        assert m.from_alias == "web"
        assert m.to_alias == "account"
        assert m.text == "Logs in using credentials"
        assert m.line_type == "solid"
        assert m.arrow_type == "arrow"
        assert m.activate is True  # ->>+ means activate

    def test_dotted_message(self, result):
        """blog--)mail is a dotted point arrow."""
        dotted_points = [m for m in result.messages
                         if m.line_type == "dotted" and m.arrow_type == "point"]
        assert len(dotted_points) == 2  # blog--)mail and blog--)db

    def test_dotted_arrow_message(self, result):
        """blog-->>-web is a dotted arrow with deactivate."""
        m = result.messages[-1]  # last message
        assert m.from_alias == "blog"
        assert m.to_alias == "web"
        assert m.line_type == "dotted"
        assert m.arrow_type == "arrow"
        assert m.deactivate is True

    def test_deactivate_modifier(self, result):
        """account->>-web has deactivate modifier."""
        deact = [m for m in result.messages if m.deactivate]
        assert len(deact) >= 1

    def test_note_count(self, result):
        assert len(result.notes) == 2

    def test_first_note(self, result):
        n = result.notes[0]
        assert n.placement == "over"
        assert n.actors == ["web", "db"]
        assert "logged in" in n.text

    def test_block_count(self, result):
        assert len(result.blocks) == 2  # alt + par

    def test_alt_block(self, result):
        alt = next(b for b in result.blocks if b.block_type == "alt")
        assert alt.label == "Credentials not found"
        # alt has two sections: the initial + else
        assert len(alt.sections) == 2
        assert alt.sections[1][0] == "Credentials found"

    def test_par_block(self, result):
        par = next(b for b in result.blocks if b.block_type == "par")
        assert par.label == "Notifications"
        # par has two sections: initial + and
        assert len(par.sections) == 2
        assert par.sections[1][0] == "Response"


# ═══════════════════════════════════════════════════════════
# Inline source tests (no file dependency)
# ═══════════════════════════════════════════════════════════

class TestInlineParsing:
    """Test parsing from inline source strings."""

    def test_minimal_sequence(self):
        src = """sequenceDiagram
        Alice->>Bob: Hello
        Bob->>Alice: Hi
        """
        r = parse_sequence_source(src)
        assert len(r.participants) == 2
        assert len(r.messages) == 2

    def test_auto_participant_registration(self):
        """Participants used in messages but not declared are auto-registered."""
        src = """sequenceDiagram
        Alice->>Bob: Hello
        """
        r = parse_sequence_source(src)
        assert len(r.participants) == 2
        aliases = {p.alias for p in r.participants}
        assert "Alice" in aliases
        assert "Bob" in aliases

    def test_explicit_participant_not_duplicated(self):
        """Explicitly declared participants are not duplicated by messages."""
        src = """sequenceDiagram
        participant Alice
        participant Bob
        Alice->>Bob: Hello
        """
        r = parse_sequence_source(src)
        assert len(r.participants) == 2

    def test_participant_as_label(self):
        src = """sequenceDiagram
        participant A as Alice
        participant B as Bob
        A->>B: Hello
        """
        r = parse_sequence_source(src)
        assert r.participants[0].alias == "A"
        assert r.participants[0].label == "Alice"
        assert r.participants[1].alias == "B"
        assert r.participants[1].label == "Bob"

    def test_actor_type(self):
        src = """sequenceDiagram
        actor Alice
        participant Bob
        Alice->>Bob: Hello
        """
        r = parse_sequence_source(src)
        alice = next(p for p in r.participants if p.alias == "Alice")
        assert alice.actor_type == "actor"
        bob = next(p for p in r.participants if p.alias == "Bob")
        assert bob.actor_type == "participant"

    def test_all_arrow_types(self):
        src = """sequenceDiagram
        A->>B: solid arrow
        A-->>B: dotted arrow
        A->B: solid open
        A-->B: dotted open
        A-xB: solid cross
        A--xB: dotted cross
        A-)B: solid point
        A--)B: dotted point
        """
        r = parse_sequence_source(src)
        assert len(r.messages) == 8
        expected = [
            ("solid", "arrow"),
            ("dotted", "arrow"),
            ("solid", "open"),
            ("dotted", "open"),
            ("solid", "cross"),
            ("dotted", "cross"),
            ("solid", "point"),
            ("dotted", "point"),
        ]
        for msg, (lt, at) in zip(r.messages, expected):
            assert msg.line_type == lt, f"Expected {lt} for '{msg.text}'"
            assert msg.arrow_type == at, f"Expected {at} for '{msg.text}'"

    def test_activation_modifiers(self):
        src = """sequenceDiagram
        Alice->>+Bob: Hello
        Bob->>-Alice: Bye
        """
        r = parse_sequence_source(src)
        assert r.messages[0].activate is True
        assert r.messages[0].deactivate is False
        assert r.messages[1].activate is False
        assert r.messages[1].deactivate is True

    def test_note_left_of(self):
        src = """sequenceDiagram
        participant Alice
        Note left of Alice: Important
        """
        r = parse_sequence_source(src)
        assert len(r.notes) == 1
        assert r.notes[0].placement == "left_of"
        assert r.notes[0].actors == ["Alice"]
        assert r.notes[0].text == "Important"

    def test_note_right_of(self):
        src = """sequenceDiagram
        participant Alice
        Note right of Alice: Details
        """
        r = parse_sequence_source(src)
        assert len(r.notes) == 1
        assert r.notes[0].placement == "right_of"

    def test_note_over_multiple(self):
        src = """sequenceDiagram
        participant A
        participant B
        Note over A,B: Shared note
        """
        r = parse_sequence_source(src)
        assert len(r.notes) == 1
        assert r.notes[0].placement == "over"
        assert r.notes[0].actors == ["A", "B"]

    def test_loop_block(self):
        src = """sequenceDiagram
        loop Every minute
            A->>B: Ping
        end
        """
        r = parse_sequence_source(src)
        assert len(r.blocks) == 1
        assert r.blocks[0].block_type == "loop"
        assert r.blocks[0].label == "Every minute"

    def test_opt_block(self):
        src = """sequenceDiagram
        opt Extra
            A->>B: Bonus
        end
        """
        r = parse_sequence_source(src)
        assert len(r.blocks) == 1
        assert r.blocks[0].block_type == "opt"

    def test_critical_block(self):
        src = """sequenceDiagram
        critical Establish connection
            A->>B: Connect
        end
        """
        r = parse_sequence_source(src)
        assert len(r.blocks) == 1
        assert r.blocks[0].block_type == "critical"

    def test_alt_else(self):
        src = """sequenceDiagram
        alt Success
            A->>B: OK
        else Failure
            A->>B: Error
        end
        """
        r = parse_sequence_source(src)
        assert len(r.blocks) == 1
        blk = r.blocks[0]
        assert blk.block_type == "alt"
        assert len(blk.sections) == 2
        assert blk.sections[0][0] == "Success"
        assert blk.sections[1][0] == "Failure"

    def test_par_and(self):
        src = """sequenceDiagram
        par Task 1
            A->>B: Do X
        and Task 2
            A->>C: Do Y
        end
        """
        r = parse_sequence_source(src)
        assert len(r.blocks) == 1
        blk = r.blocks[0]
        assert blk.block_type == "par"
        assert len(blk.sections) == 2
        assert blk.sections[1][0] == "Task 2"

    def test_title(self):
        src = """sequenceDiagram
        title My Diagram
        A->>B: Hello
        """
        r = parse_sequence_source(src)
        assert r.title == "My Diagram"

    def test_autonumber(self):
        src = """sequenceDiagram
        autonumber
        A->>B: Hello
        """
        r = parse_sequence_source(src)
        assert r.autonumber is True

    def test_comments_stripped(self):
        src = """sequenceDiagram
        %% This is a comment
        Alice->>Bob: Hello %% inline comment
        """
        r = parse_sequence_source(src)
        assert len(r.messages) == 1


# ═══════════════════════════════════════════════════════════
# Error handling
# ═══════════════════════════════════════════════════════════

class TestErrorHandling:
    """Test error cases."""

    def test_non_sequence_raises(self):
        with pytest.raises(ValueError, match="Not a sequence diagram"):
            parse_sequence_source("flowchart LR\n  A --> B")

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="Not a sequence diagram"):
            parse_sequence_source("")

    def test_c4_raises(self):
        with pytest.raises(ValueError, match="Not a sequence diagram"):
            parse_sequence_source("C4Context\n  Person(a, \"A\")")
