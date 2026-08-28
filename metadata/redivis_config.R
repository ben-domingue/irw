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
## August 2026, when the five auxiliary datasets (irw_meta, irw_text, irw_simsyn,
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

## Auxiliary (non-core) datasets, by the `source` name the irw package uses.
IRW_AUX_DATASETS <- c(
  meta = "irw_meta",
  text = "irw_text",
  sim  = "irw_simsyn",
  comp = "irw_competitions",
  nom  = "irw_nominal"
)
