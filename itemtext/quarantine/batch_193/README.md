# batch_193 quarantine

`tsai_2017_treeit_h13_control`, `tsai_2017_treeit_h14_document`, `tsai_2017_treeit_h1_consistency` — extracted and gated clean (audit_batch PASS, verify_batch PASS, lint clean,
irw-validate ok; mapping PARTIAL), then PULLED at triage on 2026-09-11 by Ben's ruling on
the tsai_2017_treeit family rights escalation. Never uploaded, so there is nothing to withdraw.

Instrument: the Treeit Heuristic Evaluation checklist (Tsai et al. 2017, PLOS ONE,
doi:10.1371/journal.pone.0180102, S1), adapted from Zhang et al. (2003) J Biomed Inform
36:23-30. Crossref lists Zhang 2003 under the Elsevier open-archive user licence ("may not
redistribute, display or adapt"), and each heuristic's `instructions` line very likely
reproduces Zhang's wording (unconfirmed: ScienceDirect returned 403).

Ben's ruling: ship only the three TAM tables (tam_bi, tam_peou, tam_pu — Davis 1989
adaptation, no shared wording with Zhang, VERIFIED) and block all thirteen heuristic
tables. The rights question is unresolved and the heuristic tables are low value on
their own: within-block item order is not established for any of them, and the S3
deposit carries heavy identical-answer columns (H2-4 = H6-3 in 101/101 rows).
`tsai_2017_treeit_h8_message` was already blocked by its round (batch_196) and stays blocked.

What would change it: the Zhang 2003 heuristic descriptions confirmed as not reproduced,
or a grant covering them. The provenance and notes rows in `itemtables/batch_193/` carry
the full mapping evidence.

DO NOT upload. If Ben reverses, these files are ready to move back as-is.
