upload_meta.py -- replace the metadata/biblio/tags Redivis tables with the
local CSVs from workflow 1 (run_pipeline.sh).

This is now a thin wrapper around `red_up`, the one uploader every IRW Redivis
dataset goes through (src/red_up/README.md). Its job is to know which thirteen
CSV stems belong in irw_meta and where to look for them; everything else --
the full replace, the preserved table description, the stray-upload warning,
the post-upload row-count check -- happens in red_up. The row-count check is
now an actual count(*) rather than numRows, which could report "no change" for
a table that had just doubled.

Usage is unchanged.

Notes before use:
1. Run workflow 1 first (run_pipeline.sh) and review its diff output --
   this script does not regenerate anything, only uploads what's already
   sitting in metadata/.
2. Credentials: the write-scoped REDIVIS_API_TOKEN, resolved by the shared
   helper src/irw_secrets.py -- an exported REDIVIS_API_TOKEN wins, otherwise
   ~/.config/irw/redivis-write.env (chmod 600, outside Dropbox, does not sync
   between machines). Same token every IRW upload uses. That's a different
   token from ~/.redivis_api_token (read-only, used by run_pipeline.sh/
   audit_tables.R) -- this needs data.edit scope.
3. Targets datapages/irw_meta at version="next" -- a DRAFT version. Nothing is
   live until you review and publish it by hand on the Redivis site afterward.
   red_up opens the draft itself if the last version has been released.

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

Known file -> table mapping (13): metadata, biblio, tags, nominal_tags,
comps_biblio, nominal_biblio, simsyn_biblio, simsyn_metadata, comps_metadata,
nominal_metadata, itemtext_metadata, collections, collection_members.
hero_stats.json is NOT here -- it's not a Redivis table, it goes to the
separate irw_site repo.

Full details: the script's own docstring, SKILL.md's "Workflow 3", and
src/red_up/README.md.
