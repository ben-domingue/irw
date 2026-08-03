upload_meta.py -- replace the metadata/biblio/tags Redivis tables with the
local CSVs from workflow 1 (run_pipeline.sh).

Notes before use:
1. Run workflow 1 first (run_pipeline.sh) and review its diff output --
   this script does not regenerate anything, only uploads what's already
   sitting in metadata/.
2. Credentials: reuses the write-scoped REDIVIS_API_TOKEN already sitting in
   ../../../../data/add2redivis/.env (same token add2redivis/upload.py uses).
   That's a different token from ~/.redivis_api_token (read-only, used by
   run_pipeline.sh/audit_tables.R) -- this script needs data.edit scope.
3. Targets redivis.user("bdomingu").dataset("irw_meta", version="next") --
   a DRAFT version. Nothing is live until you review and publish it by hand
   on the Redivis site afterward.

How to run (from metadata/):

  python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --dry-run
      # see the plan (which files, which tables, row counts) without
      # uploading anything -- always do this first

  python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py
      # upload all known files present in metadata/, with a y/n confirm

  python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py biblio tags
      # only these two

  python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --yes
      # skip the confirmation prompt

Known file -> table mapping: metadata, biblio, tags, comps_biblio,
nominal_biblio, simsyn_biblio, simsyn_metadata, comps_metadata,
nominal_metadata, itemtext_metadata. hero_stats.json is NOT here -- it's
not a Redivis table, it goes to the separate irw_site repo.

Full details: see the script's own docstring and SKILL.md's "Workflow 3".
