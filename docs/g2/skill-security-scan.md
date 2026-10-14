# Agent Skill Security Scan Report

**Skill:** event-planning-coordination-brief
**Directory:** /home/mike/event-coordination/event-planning-coordination-brief
**Status:** [OK] SAFE
**Max Severity:** LOW
**Scan Duration:** 0.47s
**Timestamp:** 2026-10-14T21:52:58.140380+00:00

## Summary

- **Total Findings:** 2
- **Critical:** 0
- **High:** 0
- **Medium:** 0
- **Low:** 1
- **Info:** 1

## Findings

### LOW Severity

#### [LOW] Python bytecode cache directory detected

**Severity:** LOW
**Category:** policy_violation
**Rule ID:** PYCACHE_FILES_DETECTED
**Location:** scripts/__pycache__

**Description:** __pycache__ directory found at scripts/__pycache__/ containing 2 bytecode file(s). Pre-compiled bytecode should not be distributed in skill packages.

**Remediation:** Remove __pycache__ directories from skill packages. Ship source code only.

### INFO Severity

#### [INFO] Skill does not specify a license

**Severity:** INFO
**Category:** policy_violation
**Rule ID:** MANIFEST_MISSING_LICENSE
**Location:** SKILL.md

**Description:** Skill manifest does not include a 'license' field. Specifying a license helps users understand usage terms.

**Remediation:** Add 'license' field to SKILL.md frontmatter (e.g., MIT, Apache-2.0)

## Analyzers

The following analyzers were used:

- static_analyzer
- bytecode
- pipeline

