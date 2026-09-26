#!/usr/bin/env python3
"""Recompute Papaya's retained Q8-vs-ONNX same-checkpoint comparison.

This is upstream provenance evidence only. It does not compare against the
pinned Python-Laya reference capture used by SEI #597.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-upstream-same-checkpoint/v1"
UPSTREAM_REPOSITORY = "m0rphtail/papaya"
UPSTREAM_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
PAPAYA_PATH = "benchmarks/results/ours.json"
PAPAYA_BLOB = "53fe8d4c7481d09d291dfc3914e730a5c36bbab0"
ONNX_PATH = "benchmarks/results/navopw-on-typed-decisions.json"
ONNX_BLOB = "ef9d27f18f2428d02e51e356cb2b4136a578deed"
README_BLOB = "ab6ca374dda4b61c38824c95d18d703327c64293"


class ComparisonError(ValueError):
    pass


def git_blob_oid(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load(path: Path, expected_blob: str, label: str) -> dict[str, Any]:
    data = path.read_bytes()
    actual = git_blob_oid(data)
    if actual != expected_blob:
        raise ComparisonError(
            f"{label} Git blob mismatch: expected {expected_blob}, got {actual}"
        )
    try:
        value = json.loads(data)
    except json.JSONDecodeError as exc:
        raise ComparisonError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"{label} root must be an object")
    return value


def _score_argmax(answer: dict[str, Any]) -> int:
    probs = answer.get("probabilities")
    if not isinstance(probs, dict) or not probs:
        raise ComparisonError("score answer requires probabilities")
    return int(max(probs.items(), key=lambda item: float(item[1]))[0])


def _summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "max": None}
    return {
        "n": len(values),
        "mean": sum(values) / len(values),
        "max": max(values),
    }


def compare_payloads(papaya: dict[str, Any], onnx: dict[str, Any]) -> dict[str, Any]:
    if papaya.get("label") != "laya-cpp":
        raise ComparisonError("unexpected Papaya result label")
    if onnx.get("label") != "navopw-typed":
        raise ComparisonError("unexpected ONNX result label")
    if papaya.get("n") != 48 or onnx.get("n") != 48:
        raise ComparisonError("same-checkpoint comparison must contain 48 cases")

    arows = papaya.get("results")
    brows = onnx.get("results")
    if not isinstance(arows, list) or not isinstance(brows, list):
        raise ComparisonError("results must be arrays")
    if len(arows) != 48 or len(brows) != 48:
        raise ComparisonError("retained results length drift")

    a_ids = [row.get("id") for row in arows]
    b_ids = [row.get("id") for row in brows]
    if a_ids != b_ids or len(set(a_ids)) != 48:
        raise ComparisonError("case identity/order drift")

    by_type = {"choice": 0, "noul": 0, "score": 0}
    choice_agree = 0
    noul_agree = 0
    score_argmax_agree = 0
    score_argmax_mismatches: list[dict[str, Any]] = []
    score_abs: list[float] = []
    noul_abs: list[float] = []
    confidence_abs: list[float] = []
    probability_abs: list[float] = []
    token_agree = 0

    for arow, brow in zip(arows, brows):
        if (
            arow.get("usage", {}).get("input_tokens")
            == brow.get("usage", {}).get("input_tokens")
        ):
            token_agree += 1
        aans = arow.get("answers")
        bans = brow.get("answers")
        if not isinstance(aans, dict) or not isinstance(bans, dict):
            raise ComparisonError("answers must be objects")
        if list(aans) != list(bans):
            raise ComparisonError(f"question identity/order drift in {arow.get('id')}")

        for qid, aa in aans.items():
            ba = bans[qid]
            if aa.get("type") != ba.get("type"):
                raise ComparisonError(f"answer type drift in {arow.get('id')}/{qid}")
            qtype = aa.get("type")
            if qtype not in by_type:
                raise ComparisonError(f"unsupported answer type: {qtype!r}")
            by_type[qtype] += 1

            if qtype == "choice":
                if aa.get("choice") == ba.get("choice"):
                    choice_agree += 1
            elif qtype == "noul":
                av = float(aa["noul"])
                bv = float(ba["noul"])
                noul_abs.append(abs(av - bv))
                if (av >= 0.5) == (bv >= 0.5):
                    noul_agree += 1
            else:
                av = float(aa["score"])
                bv = float(ba["score"])
                score_abs.append(abs(av - bv))
                ai = _score_argmax(aa)
                bi = _score_argmax(ba)
                if ai == bi:
                    score_argmax_agree += 1
                else:
                    score_argmax_mismatches.append(
                        {
                            "case_id": arow["id"],
                            "question_id": qid,
                            "papaya_argmax": ai,
                            "onnx_argmax": bi,
                            "papaya_score": av,
                            "onnx_score": bv,
                        }
                    )

            if "confidence" in aa and "confidence" in ba:
                confidence_abs.append(
                    abs(float(aa["confidence"]) - float(ba["confidence"]))
                )
            ap = aa.get("probabilities")
            bp = ba.get("probabilities")
            if ap is not None or bp is not None:
                if (
                    not isinstance(ap, dict)
                    or not isinstance(bp, dict)
                    or list(ap) != list(bp)
                ):
                    raise ComparisonError(
                        f"probability-key drift in {arow.get('id')}/{qid}"
                    )
                probability_abs.extend(
                    abs(float(ap[k]) - float(bp[k])) for k in ap
                )

    if by_type != {"choice": 72, "noul": 72, "score": 96}:
        raise ComparisonError(f"question-type counts drift: {by_type!r}")

    papaya_mean = float(papaya["mean_s"])
    onnx_mean = float(onnx["mean_s"])
    return {
        "schema": SCHEMA,
        "source": {
            "repository": UPSTREAM_REPOSITORY,
            "revision": UPSTREAM_REVISION,
            "papaya_results": {"path": PAPAYA_PATH, "git_blob": PAPAYA_BLOB},
            "onnx_results": {"path": ONNX_PATH, "git_blob": ONNX_BLOB},
            "readme_git_blob": README_BLOB,
        },
        "population": {
            "cases": 48,
            "questions": sum(by_type.values()),
            "by_type": by_type,
            "case_order_equal": True,
            "input_token_count_equal": token_agree == 48,
            "input_token_count_equal_cases": token_agree,
        },
        "agreement": {
            "choice_selected_label": {
                "agree": choice_agree,
                "n": by_type["choice"],
            },
            "noul_boolean_at_0_5": {
                "agree": noul_agree,
                "n": by_type["noul"],
            },
            "published_discrete_scope": {
                "agree": choice_agree + noul_agree,
                "n": by_type["choice"] + by_type["noul"],
            },
            "score_probability_argmax": {
                "agree": score_argmax_agree,
                "n": by_type["score"],
                "mismatches": score_argmax_mismatches,
            },
        },
        "numeric_deltas": {
            "score_expected_value_abs": _summary(score_abs),
            "noul_probability_abs": _summary(noul_abs),
            "confidence_abs": _summary(confidence_abs),
            "answer_probability_abs": _summary(probability_abs),
        },
        "upstream_environment_performance": {
            "papaya_mean_s": papaya_mean,
            "onnx_mean_s": onnx_mean,
            "onnx_over_papaya_mean_ratio": onnx_mean / papaya_mean,
            "papaya_total_s": float(papaya["total_s"]),
            "onnx_total_s": float(onnx["total_s"]),
        },
        "scope": {
            "upstream_retained_output_recalculation": True,
            "same_checkpoint_identity_independently_attested": False,
            "onnx_model_bytes_attested": False,
            "onnx_runtime_bytes_attested": False,
            "python_laya_reference_comparison": False,
            "sei_live_capture": False,
            "jev_provider_identity": False,
            "task_quality_reproduction": False,
            "shipping_performance_claim": False,
            "numeric_acceptance_threshold": False,
            "tolerance_context_only": True,
        },
    }


def compare_files(papaya_path: Path, onnx_path: Path) -> dict[str, Any]:
    return compare_payloads(
        _load(papaya_path, PAPAYA_BLOB, "Papaya results"),
        _load(onnx_path, ONNX_BLOB, "ONNX results"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("papaya_results", type=Path)
    parser.add_argument("onnx_results", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = compare_files(args.papaya_results, args.onnx_results)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
