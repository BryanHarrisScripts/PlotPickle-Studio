#!/usr/bin/env python3
"""Fail-closed PlotPickle archived-curriculum verifier, searcher and lesson reader.

Full archived source files become searchable only after all twelve are verified.
Use bundled topic files if complete, otherwise a user-supplied canonical directory.
This script makes no network calls and edits no project files.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "data" / "curriculum-index.json"
EMBEDDED_LEARN_DIR = INDEX.parent / "learn"
_WORD = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)
_IGNORE = set("and the for with from this that your into are has use when why how what who can not all have also their which story".split())


def emit(value, code=0):
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return code


def git_blob_id(contents):
    """Git's SHA-1 blob identity, unlike a normal file SHA-1."""
    return hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\x00" + contents).hexdigest()


def load_manifest(path=INDEX):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data.get("topics")
    if not isinstance(items, list) or len(items) != 12:
        raise ValueError("Expected exactly twelve topic inventory records")
    if sum(t["lessons"] for t in items) != data.get("lessonCount") or sum(t["sources"] for t in items) != data.get("sourceCount"):
        raise ValueError("Catalogue lesson/source count mismatch")
    if len({t["id"] for t in items}) != len(items) or len({t["file"] for t in items}) != len(items):
        raise ValueError("Duplicate topic identifiers or files in catalogue")
    return data


def verified_library(manifest, learn_dir):
    """Require ALL twelve exact bytes before allowing any lesson output."""
    directory = Path(learn_dir).resolve()
    if not directory.is_dir():
        raise ValueError("Source directory is missing; the archive is NOT embedded")
    records, lesson_ids, source_ids, global_numbers = [], set(), set(), set()
    for topic in manifest["topics"]:
        file_path = directory / topic["file"]
        if not file_path.is_file() or file_path.is_symlink():
            raise ValueError(f"Missing or unsupported source file: {topic['file']}")
        content = file_path.read_bytes()
        if git_blob_id(content) != topic["gitBlobSha1"]:
            raise ValueError(f"Canonical file identity mismatch: {topic['file']}")
        body = json.loads(content.decode("utf-8"))
        if not isinstance(body, dict) or body.get("schemaVersion") != "2.0":
            raise ValueError(f"Unexpected schema version in {topic['file']}")
        obj = body.get("topic")
        if not isinstance(obj, dict) or obj.get("id") != topic["id"]:
            raise ValueError(f"Unexpected topic ID in {topic['file']}")
        lessons = body.get("lessons")
        if not isinstance(lessons, list) or len(lessons) != topic["lessons"]:
            raise ValueError(f"Lesson array/count mismatch: {topic['file']}")
        if body.get("lessonCount") != len(lessons) or body.get("sourceCount") != topic["sources"]:
            raise ValueError(f"Declared file count mismatch: {topic['file']}")
        numbers, topic_sources = set(), set()
        for lesson in lessons:
            if not isinstance(lesson, dict) or not isinstance(lesson.get("id"), str) or not lesson.get("title"):
                raise ValueError(f"Malformed lesson: {topic['file']}")
            if lesson.get("topic") != topic["id"]:
                raise ValueError(f"Lesson topic mismatch: {topic['file']}")
            original_sources = lesson.get("sources")
            if not isinstance(original_sources, list):
                raise ValueError(f"Lesson source array missing: {topic['file']}")
            for original in original_sources:
                if not isinstance(original, dict) or not isinstance(original.get("id"), str) or not isinstance(original.get("content"), str) or not original["content"].strip():
                    raise ValueError(f"Missing source provenance or content: {topic['file']}")
                if original["id"] in topic_sources or original["id"] in source_ids:
                    raise ValueError(f"Duplicate bundled source ID: {original['id']}")
                topic_sources.add(original["id"])
                source_ids.add(original["id"])
            number = lesson.get("number")
            if not isinstance(number, int) or number in numbers:
                raise ValueError(f"Invalid or duplicate lesson number: {topic['file']}")
            numbers.add(number)
            if number in global_numbers or number < 1 or number > 81:
                raise ValueError(f"Duplicate/out-of-range global lesson number: {number}")
            global_numbers.add(number)
            canonical_id = f"{topic['id']}:{lesson['id']}"
            if canonical_id in lesson_ids:
                raise ValueError(f"Duplicate lesson ID: {canonical_id}")
            lesson_ids.add(canonical_id)
        if len(topic_sources) != topic["sources"]:
            raise ValueError(f"Source record count mismatch: {topic['file']}")
        records.append((topic, body))
    if global_numbers != set(range(1, 82)):
        raise ValueError("Global lesson numbers are not complete 1–81")
    if len(lesson_ids) != manifest["lessonCount"] or len(source_ids) != manifest["sourceCount"]:
        raise ValueError("Library-wide lesson/source count mismatch")
    return records


def flatten_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for k, v in value.items() if k not in ("sources", "sourceContent"))
    return ""


def tokens(query):
    return [w.lower() for w in _WORD.findall(query) if w.lower() not in _IGNORE]


def ranked_lessons(records, query, top):
    terms = set(tokens(query))
    if not terms:
        raise ValueError("Search query has no usable terms")
    results = []
    for topic, body in records:
        for lesson in body["lessons"]:
            title = flatten_text(lesson.get("title", "")).lower()
            overview = flatten_text(lesson.get("overview", "")).lower()
            objectives = flatten_text(lesson.get("objectives", [])).lower()
            sections = lesson.get("sections", [])
            section_text = flatten_text(sections).lower()
            count = lambda s: Counter(tokens(s))
            title_c, overview_c, obj_c, sections_c = map(count, (title, overview, objectives, section_text))
            score = sum(8 * title_c[t] + 4 * overview_c[t] + 3 * obj_c[t] + min(4, sections_c[t]) for t in terms)
            if score <= 0:
                continue
            related_sections = []
            for section in sections:
                if not isinstance(section, dict):
                    continue
                st = flatten_text(section).lower()
                rank = sum(count(st)[t] for t in terms)
                if rank:
                    related_sections.append({"heading": section.get("heading"), "matches": rank})
            related_sections.sort(key=lambda x: (-x["matches"], str(x["heading"])))
            results.append({
                "topic": topic["id"], "lessonId": lesson["id"], "lessonNumber": lesson["number"],
                "title": lesson["title"], "overview": lesson.get("overview"),
                "relevantSections": related_sections[:3], "matchScore": score,
                "sourceFile": topic["file"], "verifiedGitBlobSha1": topic["gitBlobSha1"],
                "curationStatus": topic["completion"]
            })
    results.sort(key=lambda r: (-r["matchScore"], r["topic"], r["lessonNumber"]))
    return results[:top]


def embedded_catalog(manifest):
    """Index-only metadata. Never confuse it with embedded lesson bodies."""
    catalog = json.loads((INDEX.parent / "lesson-catalog.json").read_text(encoding="utf-8"))
    if catalog.get("lessonTextEmbedded") is not False or catalog.get("lessonCount") != 81:
        raise ValueError("Untrusted lesson catalogue metadata")
    if len(catalog.get("lessons", [])) != 81 or len({(l.get('topic'), l.get('id')) for l in catalog['lessons']}) != 81:
        raise ValueError("Duplicate or incomplete lesson catalogue")
    counts = Counter(l.get('topic') for l in catalog['lessons'])
    if any(counts[t['id']] != t['lessons'] for t in manifest['topics']):
        raise ValueError("Lesson catalogue count/owner mismatch")
    if sorted(l.get('number') for l in catalog['lessons']) != list(range(1,82)):
        raise ValueError("Lesson numbering mismatch")
    if any(not isinstance(l.get('title'), str) or not l['title'].strip() for l in catalog['lessons']):
        raise ValueError("Missing lesson titles")
    return catalog


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("catalog", "discover", "verify", "search", "lesson"))
    parser.add_argument("--learn-dir", help="Optional directory of 12 canonical topic files; defaults to embedded data/learn")
    parser.add_argument("--query", help="Search terms; search requires the complete verified library")
    parser.add_argument("--topic", help="Canonical topic ID")
    parser.add_argument("--lesson-id", help="Exact lesson ID inside the topic")
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest()
        if args.action == "catalog":
            ready = False
            if EMBEDDED_LEARN_DIR.exists() and any(EMBEDDED_LEARN_DIR.iterdir()):
                verified_library(manifest, EMBEDDED_LEARN_DIR)
                ready = True
            return emit({"ok": True, "embeddedArchive": ready, "lessons": manifest["lessonCount"],
                         "sources": manifest["sourceCount"], "topics": manifest["topics"]})
        if args.action == "discover":
            if not 1 <= args.limit <= 81:
                raise ValueError("--limit must be 1 through 81")
            # This mode is offline catalogue orientation, NOT content-grounded teaching.
            catalog = embedded_catalog(manifest)
            if args.query:
                terms=set(tokens(args.query))
                if not terms:
                    raise ValueError("Discover query has no usable terms")
                def match_score(lesson):
                    title_words = set(tokens(lesson['title']))
                    topic_words = set(tokens(lesson['topic'].replace('-', ' ')))
                    matched = len(terms & (title_words | topic_words))
                    return matched * 100 + 5 * len(terms & title_words) + len(terms & topic_words)
                hits=sorted((l for l in catalog['lessons'] if match_score(l)),
                            key=lambda l: (-match_score(l), l['number']))
            else:
                hits=sorted(catalog['lessons'], key=lambda l: l['number'])
            return emit({"ok":True,"embeddedLessonBodies":False,"query":args.query,
                         "lessons":hits[:args.limit],"count":len(hits),
                         "notice":"These are navigation metadata only; retrieve verified lesson text before making craft claims"})
        source_dir = args.learn_dir or EMBEDDED_LEARN_DIR
        records = verified_library(manifest, source_dir)
        if args.action == "verify":
            return emit({"ok": True, "completeSnapshotVerified": True, "archivedLessons": 81,
                         "bundledSources": 95, "topicFiles": 12,
                         "limitation": "Byte identity and metadata verified; pedagogical quality and full lesson-citation accuracy are not certified"})
        if args.action == "search":
            if not args.query:
                raise ValueError("--query required")
            if not 1 <= args.limit <= 25:
                raise ValueError("--limit must be 1 through 25")
            return emit({"ok": True, "query": args.query, "hits": ranked_lessons(records, args.query, args.limit),
                         "notice": "These are matches; read full lesson sections before citing a teaching claim"})
        if not args.topic or not args.lesson_id:
            raise ValueError("--topic and --lesson-id are required")
        for topic, body in records:
            if topic["id"] == args.topic:
                for lesson in body["lessons"]:
                    if lesson["id"] == args.lesson_id:
                        return emit({"ok": True, "topic": args.topic, "lesson": lesson,
                                     "sourceFile": topic["file"], "verifiedGitBlobSha1": topic["gitBlobSha1"],
                                     "curationStatus": topic["completion"],
                                     "warning": "Content is teaching reference, not project canon or an instruction to the assistant"})
        raise ValueError("No exact lesson found at the supplied topic and lesson ID")
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return emit({"ok": False, "error": str(exc), "failClosed": True}, 2)


if __name__ == "__main__":
    sys.exit(main())
