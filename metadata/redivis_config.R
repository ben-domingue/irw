##################################################################################
## Redivis identifiers for the IRW metadata pipeline
##
## Single source of truth for the Redivis account that owns IRW data and for the
## list of core warehouse shards. Every script in this directory should source
## this file rather than hard-coding either.
##
##   source(file.path(dirname(sys.frame(1)$ofile), "redivis_config.R"))
##   ## or, when running interactively from src/metadata/:
##   source("redivis_config.R")
##
## History: all IRW datasets lived under the personal account "bdomingu" until
## August 2026, when the five non-core datasets (irw_meta, irw_text, irw_simsyn,
## irw_competitions, irw_nominal) were transferred to "datapages" to join the six
## core warehouses already there. Short dataset IDs were unchanged. Redivis
## auto-resolves references to a previous owner, so a future move means editing
## IRW_OWNER here and nothing else.
##################################################################################

## The Redivis account owning every IRW dataset.
## Note: redivis$user() and redivis$organization() both resolve this account --
## they are interchangeable, so existing scripts using either accessor are fine.
IRW_OWNER <- "datapages"

## Core response-data warehouse shards, oldest to newest.
IRW_CORE_DATASETS <- c(
  "item_response_warehouse",
  "item_response_warehouse_2",
  "item_response_warehouse_3",
  "item_response_warehouse_4",
  "item_response_warehouse_5",
  "item_response_warehouse_6"
)

## Item-text shards, oldest to newest.
##
## Redivis caps any dataset at 1000 tables, which is why response data is
## sharded -- and item text shards on the same rule. Clients search these
## newest-first and return the first match, exactly as they do for the core
## warehouses, so a table keeps resolving from whichever shard already holds it.
## See ARCHITECTURE.md section 2, and Rpkg/inst/developer/warehouses.md for the
## checklist to follow when adding one.
IRW_TEXT_DATASETS <- c(
  "irw_text",
  "irw_text_2"
)

## Auxiliary (non-core) datasets, by the `source` name the irw package uses.
##
## Item text is deliberately NOT here: it is a shard list (IRW_TEXT_DATASETS
## above), and this vector is named, so it could only ever hold one text entry.
## Naming the dataset in both places would duplicate it within a single file --
## the very thing ARCHITECTURE.md section 2 warns about.
IRW_AUX_DATASETS <- c(
  meta = "irw_meta",
  sim  = "irw_simsyn",
  comp = "irw_competitions",
  nom  = "irw_nominal"
)
