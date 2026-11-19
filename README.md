# Transcript Intelligence - revised assessment

An offline, interpretable baseline for the supplied sample. No API keys or generated data. Python 3.10+.

## Run
Place the original `interview-assignment/dataset` folder next to this repository (or specify its location).

```powershell
python -m pip install -r requirements.txt
python analyze.py --dataset interview-assignment/dataset --output outputs
python -m unittest discover -s tests
```

The supplied data is not bundled for redistribution. The `outputs` directory includes derived evidence from the assignment; share privately with authorized reviewers only.

## Design decisions
- Read transcript, meeting-info and summary JSON per meeting. Speaker timestamps are already in transcript rows; events and separate speaker files are not needed for these questions.
- Keep original call-type rules: all internal-domain emails = Internal; otherwise titles beginning Support Case, Urgent: or Escalation: = Support; remaining calls = External. This is a proxy, not verified ground truth. Counts can differ with other rules.
- Match case-insensitive whole-word expressions against spoken text, using five overlapping themes. One matching segment qualifies a meeting; report both meeting counts and segment mentions. This transparent baseline is easy to audit, but broad words and company names can cause false positives; paraphrases can be missed. No independent accuracy claim. 2,496 segments have no match. A segment can contain several themes.
- Aggregate provided sentiment labels by call type and month, weighted by segment count. Unknown labels are explicitly counted. No new sentiment model, customer satisfaction score or causal claim. Speaker role is not separated.
- Count existing action items and flag whole-word risk terms. These are potential signals, not validated incidents or outstanding commitments. The stricter matching yields 49 flags instead of 50 in the previous substring baseline.
- The monthly comparison is descriptive: the provided sample composition can change, so it cannot establish company-wide trends.

## Outputs
`metrics.json`, `meetings.csv` (meeting IDs and assigned topics), `sentiment_by_type.csv`, `monthly_sentiment.csv`, `topics.csv`, `topic_evidence.csv` (actual speech, timestamp, meeting ID and speaker), `risk_actions.csv`, and two PNG charts.

## Next steps
Human-label a stratified sample, evaluate multi-label precision/recall/F1, refine broad keywords, and compare with embeddings or an LLM classifier. Separate customer/employee sentiment and verify action completion against ticket or CRM records. None of these extensions is claimed as implemented.
