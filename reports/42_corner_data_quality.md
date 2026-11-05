# Corner data relationship audit

Inputs: 45 corner records, 21 phase-shot records and 45 taker records from the existing five-match France study.

- nonempty_corners: 0 violations; PASS.
- duplicate_corner_keys: 0 violations; PASS.
- duplicate_shot_keys: 0 violations; PASS.
- duplicate_taker_keys: 0 violations; PASS.
- missing_taker_records: 0 violations; PASS.
- unknown_taker_corners: 0 violations; PASS.
- unknown_shot_corners: 0 violations; PASS.
- blank_taker_names: 0 violations; PASS.
- missing_identity_fields: 0 violations; PASS.

Overall structural audit: **PASS**.

## Why this matters

A duplicate positive corner could change a rate from 1/2 to 2/3. An inner join could silently remove a corner with missing taker metadata. A shot linked to the wrong match/corner key could be lost or assigned incorrectly. We inspect incoming records before putting them into the reporting database.

Temporary staging tables allow problematic records to be counted instead of failing at the first insertion. The final reporting tables retain their strict keys and foreign-key constraints. Full identities use match ID plus corner ID, or match ID plus shot ID. A missing taker is an error under this report's complete-metadata requirement; a corner without a shot is valid and must remain in the denominator.

The duplicate checks count key groups appearing more than once; relationship/name checks count affected records. These violation counts have different meanings and must not be added into a count of unique bad events. One record can fail several checks. An empty corner input fails, rather than receiving an all-clear result.

## How the audit is used

Run `python 59_corner_data_quality.py` in Spyder or the local environment. It saves the audit evidence and report, then exits unsuccessfully if any check fails. The lesson 58 player-report loader calls the same validation before loading records; the research runner executes this audit before lesson 58. No records are automatically dropped or repaired.

The nine checks pass on our current records. That does not prove the provider annotated every action correctly or that all real corners were captured. It also does not validate every field type, event timing, model assumption or tactical conclusion. Previous evidence checks cover additional source hashes and phase logic. This is a focused relationship audit, not a universal data-quality certificate.

## Learn and reproduce

[Short lesson](../lessons/0041-corner-data-quality.html) · [SQL checks](../sql/59_corner_relationship_audit.sql) · [Saved evidence](../data/59_corner_data_quality_evidence.json).

Worked assignment completed with assistance. Tests deliberately introduce synthetic defects into tiny examples; no corruption was found or introduced into the actual source data.

Primary reference: [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html), which enforce the existence of related parent records. The audit additionally checks the report-specific requirement that every corner has taker metadata.
