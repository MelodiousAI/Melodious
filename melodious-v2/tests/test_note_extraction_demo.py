from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

from melodious_v2.omr.note_extraction import (
    CandidateRelationship,
    DetectionCandidate,
    StaffSystem,
    _merge_staff_system_candidates,
    detect_staff_systems,
    document_key_fifths,
    events_from_candidates,
    extract_notes_from_image,
    key_signatures_from_symbols,
    notes_from_candidates,
    pitch_from_y,
    write_midi,
    write_musicxml,
)


class NoteExtractionDemoTest(unittest.TestCase):
    def _synthetic_staff_image(self, path: Path) -> None:
        image = Image.new("L", (420, 180), color=255)
        draw = ImageDraw.Draw(image)
        lines = [60, 70, 80, 90, 100]
        for y in lines:
            draw.line((40, y, 380, y), fill=0, width=1)
        for x, y in [(120, 95), (170, 85), (220, 75), (270, 65)]:
            draw.ellipse((x - 6, y - 4, x + 6, y + 4), fill=0)
            draw.line((x + 6, y, x + 6, y - 35), fill=0, width=2)
        image.save(path)

    def test_staff_detection_and_pitch_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "staff.png"
            self._synthetic_staff_image(image_path)
            image = Image.open(image_path).convert("L")
            import numpy as np

            staff_systems = detect_staff_systems(np.asarray(image))
            self.assertEqual(len(staff_systems), 1)
            step, octave, midi_pitch = pitch_from_y(staff_systems[0].bottom_y, staff_systems[0])
            self.assertEqual((step, octave, midi_pitch), ("E", 4, 64))

    def test_staff_detection_keeps_light_staff_lines(self) -> None:
        image = Image.new("L", (520, 360), color=255)
        draw = ImageDraw.Draw(image)
        for base_y, fill in [(70, 0), (210, 205)]:
            for offset in range(0, 50, 10):
                draw.line((45, base_y + offset, 470, base_y + offset), fill=fill, width=1)
        draw.text((180, 25), "Light staff regression", fill=0)

        import numpy as np

        staff_systems = detect_staff_systems(np.asarray(image))
        self.assertEqual(len(staff_systems), 2)
        self.assertEqual([round(staff.spacing) for staff in staff_systems], [10, 10])

    def test_staff_detection_keeps_compact_low_resolution_staff(self) -> None:
        image = Image.new("L", (300, 120), color=255)
        draw = ImageDraw.Draw(image)
        for y in [40, 45, 50, 55, 60]:
            draw.line((25, y, 275, y), fill=0, width=1)

        import numpy as np

        staff_systems = detect_staff_systems(np.asarray(image))
        self.assertEqual(len(staff_systems), 1)
        self.assertAlmostEqual(staff_systems[0].spacing, 5.0)

    def test_staff_merge_prefers_wider_overlapping_five_line_group(self) -> None:
        compact_false_group = StaffSystem(
            index=0,
            line_y=(118.0, 123.5, 129.0, 135.0, 141.0),
            spacing=5.75,
            start_x=36.0,
            end_x=698.0,
        )
        full_staff_group = StaffSystem(
            index=0,
            line_y=(120.5, 129.5, 135.5, 141.5, 150.5),
            spacing=7.5,
            start_x=35.0,
            end_x=698.0,
        )

        staff_systems = _merge_staff_system_candidates([compact_false_group, full_staff_group])

        self.assertEqual(len(staff_systems), 1)
        self.assertEqual(staff_systems[0].line_y, full_staff_group.line_y)

    def test_pitch_mapping_respects_notehead_line_or_space_class(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(120.5, 129.5, 135.5, 141.5, 150.5),
            spacing=7.5,
            start_x=35.0,
            end_x=698.0,
        )

        self.assertEqual(
            pitch_from_y(126.63382720947266, staff, "noteheadBlackInSpace"),
            ("E", 5, 76),
        )
        self.assertEqual(
            pitch_from_y(129.64337158203125, staff, "noteheadBlackOnLine"),
            ("D", 5, 74),
        )

    def test_detected_key_flat_applies_b_flat_pitch(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        key_flat = DetectionCandidate(
            class_id=67,
            class_name="keyFlat",
            confidence=0.9,
            bbox_xyxy=(56.0, 68.0, 64.0, 84.0),
            source="unit",
        )
        b_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackOnLine",
            confidence=0.9,
            bbox_xyxy=(120.0, 76.0, 132.0, 84.0),
            source="unit",
        )

        key_signatures = key_signatures_from_symbols([key_flat], [staff], [b_note])
        extracted = notes_from_candidates(
            [b_note],
            [staff],
            pitch_symbols=[key_flat],
            key_signatures=key_signatures,
            default_quarter_length=1.0,
        )

        self.assertEqual(key_signatures, {0: {"B": -1}})
        self.assertEqual(document_key_fifths(key_signatures), -1)
        self.assertEqual(extracted[0].step, "B")
        self.assertEqual(extracted[0].alter, -1)
        self.assertEqual(extracted[0].midi_pitch, 70)
        self.assertEqual(extracted[0].pitch_source, "key_signature:flat")

        with tempfile.TemporaryDirectory() as tmp:
            musicxml_path = Path(tmp) / "key_flat.musicxml"
            write_musicxml(extracted, musicxml_path, title="Key Flat", key_fifths=-1)
            text = musicxml_path.read_text(encoding="utf-8")
        self.assertIn("<fifths>-1</fifths>", text)
        self.assertIn("<alter>-1</alter>", text)

    def test_explicit_accidental_must_match_note_staff_step(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(120.5, 129.5, 135.5, 141.5, 150.5),
            spacing=7.5,
            start_x=35.0,
            end_x=698.0,
        )
        e_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(120.0, 123.5, 127.0, 129.7),
            source="unit",
        )
        d_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackOnLine",
            confidence=0.9,
            bbox_xyxy=(150.0, 126.6, 157.0, 132.7),
            source="unit",
        )
        d_sharp = DetectionCandidate(
            class_id=3,
            class_name="accidentalSharp",
            confidence=0.9,
            bbox_xyxy=(111.0, 123.0, 118.0, 134.0),
            source="unit",
        )
        d_sharp_near_d = DetectionCandidate(
            class_id=3,
            class_name="accidentalSharp",
            confidence=0.9,
            bbox_xyxy=(142.0, 123.0, 148.0, 134.0),
            source="unit",
        )

        extracted = notes_from_candidates(
            [e_note, d_note],
            [staff],
            pitch_symbols=[d_sharp, d_sharp_near_d],
            default_quarter_length=1.0,
        )

        self.assertEqual((extracted[0].step, extracted[0].alter), ("E", 0))
        self.assertEqual((extracted[1].step, extracted[1].alter), ("D", 1))

    def test_cv_extraction_writes_real_midi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "staff.png"
            self._synthetic_staff_image(image_path)
            result = extract_notes_from_image(
                image_path=image_path,
                output_dir=tmp_path / "out",
                checkpoint_path=None,
                use_cv_fallback=True,
                default_quarter_length=1.0,
            )
            self.assertGreaterEqual(len(result.notes), 3)
            midi_path = Path(result.artifacts.midi_path)  # type: ignore[union-attr]
            self.assertTrue(midi_path.exists())
            self.assertGreater(midi_path.stat().st_size, 26)
            self.assertEqual(midi_path.read_bytes()[:4], b"MThd")

    def test_rhythm_inference_uses_beams_flags_and_dots(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        notes = [
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(100.0, 91.0, 112.0, 99.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(150.0, 81.0, 162.0, 89.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(200.0, 71.0, 212.0, 79.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(250.0, 61.0, 262.0, 69.0),
                source="unit",
            ),
        ]
        symbols = [
            DetectionCandidate(
                class_id=2,
                class_name="augmentationDot",
                confidence=0.8,
                bbox_xyxy=(116.0, 92.0, 119.0, 95.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=3,
                class_name="beam",
                confidence=0.8,
                bbox_xyxy=(145.0, 45.0, 166.0, 49.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=4,
                class_name="flag16thUp",
                confidence=0.8,
                bbox_xyxy=(207.0, 30.0, 216.0, 52.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=5,
                class_name="stem",
                confidence=0.8,
                bbox_xyxy=(261.0, 30.0, 264.0, 69.0),
                source="unit",
            ),
        ]

        extracted = notes_from_candidates(
            notes,
            [staff],
            rhythm_symbols=symbols,
            default_quarter_length=1.0,
        )

        self.assertEqual([note.quarter_length for note in extracted], [1.5, 0.5, 0.25, 1.0])
        self.assertEqual(
            [note.rhythm_source for note in extracted],
            [
                "black_notehead_quarter_rule_no_stem+augmentation_dot",
                "beam_x1",
                "flag",
                "stem_quarter",
            ],
        )
        self.assertTrue(extracted[0].dotted)
        self.assertFalse(extracted[0].stem_detected)
        self.assertTrue(extracted[3].stem_detected)

    def test_relationships_can_drive_stem_and_beam_rhythm(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        beamed_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(120.0, 91.0, 132.0, 99.0),
            source="yolo",
        )
        stemmed_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(220.0, 81.0, 232.0, 89.0),
            source="yolo",
        )
        beam = DetectionCandidate(
            class_id=47,
            class_name="beam",
            confidence=0.8,
            bbox_xyxy=(10.0, 10.0, 50.0, 14.0),
            source="yolo_tiled_0",
        )
        stem = DetectionCandidate(
            class_id=1,
            class_name="stem",
            confidence=0.8,
            bbox_xyxy=(10.0, 40.0, 12.0, 85.0),
            source="yolo_tiled_0",
        )
        extracted = notes_from_candidates(
            [beamed_note, stemmed_note],
            [staff],
            rhythm_symbols=[beam, stem],
            rhythm_relationships=[
                CandidateRelationship(beam, beamed_note, "beam_notegroup", 0.91),
                CandidateRelationship(stem, stemmed_note, "stem_notehead", 0.92),
            ],
            default_quarter_length=1.0,
        )

        self.assertEqual([note.quarter_length for note in extracted], [0.5, 1.0])
        self.assertEqual([note.rhythm_source for note in extracted], ["gnn_beam_x1", "gnn_stem_quarter"])
        self.assertFalse(extracted[0].stem_detected)
        self.assertTrue(extracted[1].stem_detected)

    def test_rest_candidates_are_exported_and_advance_onset(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        first_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(100.0, 91.0, 112.0, 99.0),
            source="unit",
        )
        rest = DetectionCandidate(
            class_id=2,
            class_name="restQuarter",
            confidence=0.85,
            bbox_xyxy=(148.0, 72.0, 158.0, 92.0),
            source="unit",
        )
        second_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(200.0, 91.0, 212.0, 99.0),
            source="unit",
        )

        events = events_from_candidates([first_note, second_note], [staff], rest_candidates=[rest])

        self.assertEqual([event.event_type for event in events], ["note", "rest", "note"])
        self.assertEqual([event.quarter_length for event in events], [1.0, 1.0, 1.0])
        self.assertEqual([event.onset_quarter for event in events], [0.0, 1.0, 2.0])

        with tempfile.TemporaryDirectory() as tmp:
            musicxml_path = Path(tmp) / "rests.musicxml"
            write_musicxml(events, musicxml_path, title="Rests")
            xml = musicxml_path.read_text(encoding="utf-8")
        self.assertIn("<rest/>", xml)
        self.assertEqual(xml.count("<note>"), 3)

    def test_mixed_beam_groups_do_not_force_shortest_neighbor_duration(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        eighth_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(100.0, 91.0, 112.0, 99.0),
            source="unit",
        )
        sixteenth_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(170.0, 91.0, 182.0, 99.0),
            source="unit",
        )
        symbols = [
            DetectionCandidate(
                class_id=3,
                class_name="stem",
                confidence=0.9,
                bbox_xyxy=(112.0, 55.0, 115.0, 96.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=3,
                class_name="stem",
                confidence=0.9,
                bbox_xyxy=(182.0, 55.0, 185.0, 96.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=4,
                class_name="beam",
                confidence=0.9,
                bbox_xyxy=(88.0, 55.0, 210.0, 58.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=4,
                class_name="beam",
                confidence=0.9,
                bbox_xyxy=(140.0, 62.0, 210.0, 65.0),
                source="unit",
            ),
        ]

        extracted = notes_from_candidates([eighth_note, sixteenth_note], [staff], rhythm_symbols=symbols)

        self.assertEqual([note.quarter_length for note in extracted], [0.5, 0.25])
        self.assertEqual([note.rhythm_source for note in extracted], ["beam_x1", "beam_x2"])

    def test_annotation_notehead_before_staff_music_is_filtered(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(100.0, 112.0, 124.0, 136.0, 148.0),
            spacing=12.0,
            start_x=40.0,
            end_x=380.0,
        )
        tempo_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(78.0, 70.0, 94.0, 84.0),
            source="unit",
        )
        first_score_note = DetectionCandidate(
            class_id=1,
            class_name="noteheadHalfInSpace",
            confidence=0.9,
            bbox_xyxy=(118.0, 102.0, 136.0, 120.0),
            source="unit",
        )

        events = events_from_candidates([tempo_note, first_score_note], [staff])

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].x_center, first_score_note.x_center)

    def test_small_noteheads_do_not_consume_normal_rhythm(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        normal_left = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(100.0, 91.0, 118.0, 106.0),
            source="unit",
        )
        small_middle = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(145.0, 93.0, 154.0, 102.0),
            source="unit",
        )
        normal_right = DetectionCandidate(
            class_id=1,
            class_name="noteheadBlackInSpace",
            confidence=0.9,
            bbox_xyxy=(190.0, 91.0, 208.0, 106.0),
            source="unit",
        )

        events = events_from_candidates([normal_left, small_middle, normal_right], [staff])

        self.assertEqual(len(events), 2)
        self.assertEqual([event.x_center for event in events], [normal_left.x_center, normal_right.x_center])

    def test_slur_and_tie_symbols_are_written_to_musicxml(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        notes = [
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(100.0, 91.0, 112.0, 99.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(170.0, 91.0, 182.0, 99.0),
                source="unit",
            ),
        ]
        slur = DetectionCandidate(
            class_id=120,
            class_name="slur",
            confidence=0.9,
            bbox_xyxy=(100.0, 63.0, 182.0, 69.0),
            source="unit",
        )
        tie = DetectionCandidate(
            class_id=122,
            class_name="tie",
            confidence=0.9,
            bbox_xyxy=(100.0, 104.0, 182.0, 110.0),
            source="unit",
        )

        events = events_from_candidates(notes, [staff], notation_symbols=[slur, tie])

        self.assertEqual(events[0].slur_starts, (1,))
        self.assertEqual(events[1].slur_stops, (1,))
        self.assertEqual(events[0].tie_starts, (1,))
        self.assertEqual(events[1].tie_stops, (1,))

        with tempfile.TemporaryDirectory() as tmp:
            musicxml_path = Path(tmp) / "curves.musicxml"
            write_musicxml(events, musicxml_path, title="Curves")
            xml = musicxml_path.read_text(encoding="utf-8")
        self.assertIn('<slur type="start"', xml)
        self.assertIn('<slur type="stop"', xml)
        self.assertIn('<tie type="start"/>', xml)
        self.assertIn('<tie type="stop"/>', xml)

    def test_yolo_extraction_does_not_invent_cv_dots_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "staff_with_speck.png"
            self._synthetic_staff_image(image_path)
            image = Image.open(image_path).convert("L")
            draw = ImageDraw.Draw(image)
            draw.ellipse((140, 91, 144, 95), fill=0)
            image.save(image_path)

            note = DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(120.0, 91.0, 132.0, 99.0),
                source="yolo",
            )

            with patch(
                "melodious_v2.omr.note_extraction.yolo_detection_candidates",
                return_value=[note],
            ):
                result = extract_notes_from_image(
                    image_path=image_path,
                    output_dir=tmp_path / "out",
                    checkpoint_path=tmp_path / "fake.pt",
                    snapshot_live_checkpoint=False,
                    use_cv_fallback=True,
                    default_quarter_length=1.0,
                )

            self.assertEqual(len(result.notes), 1)
            self.assertFalse(result.notes[0].dotted)
            self.assertEqual(result.notes[0].quarter_length, 1.0)
            self.assertIn("only detector-confirmed augmentationDot", " ".join(result.warnings))

    def test_yolo_extraction_keeps_detector_confirmed_dots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "staff.png"
            self._synthetic_staff_image(image_path)
            note = DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(120.0, 91.0, 132.0, 99.0),
                source="yolo",
            )
            dot = DetectionCandidate(
                class_id=2,
                class_name="augmentationDot",
                confidence=0.9,
                bbox_xyxy=(138.0, 92.0, 142.0, 96.0),
                source="yolo",
            )

            with patch(
                "melodious_v2.omr.note_extraction.yolo_detection_candidates",
                return_value=[note, dot],
            ):
                result = extract_notes_from_image(
                    image_path=image_path,
                    output_dir=tmp_path / "out",
                    checkpoint_path=tmp_path / "fake.pt",
                    snapshot_live_checkpoint=False,
                    use_cv_fallback=True,
                    default_quarter_length=1.0,
                )

            self.assertEqual(len(result.notes), 1)
            self.assertTrue(result.notes[0].dotted)
            self.assertEqual(result.notes[0].quarter_length, 1.5)

    def test_midi_writer_handles_empty_note_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            midi_path = Path(tmp) / "empty.mid"
            write_midi([], midi_path)
            self.assertEqual(midi_path.read_bytes()[:4], b"MThd")


if __name__ == "__main__":
    unittest.main()
