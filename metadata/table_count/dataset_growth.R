## Pull timestamped table counts across every version of the IRW datasets on
## Redivis -- the core warehouses, the competitions/nominal/simsyn datasets, and
## the item-text and conjoint shards -- for plotting growth over time.
## Output: metadata/table_count/dataset_growth.csv
##
## Incremental: a released version never changes, so its row is reused from the
## existing CSV and only new or unreleased versions are fetched. Rerunning to
## update is cheap. Delete dataset_growth.csv to force a full re-fetch.

library(redivis)
Sys.setenv(REDIVIS_API_TOKEN = trimws(readLines("~/.redivis_api_token", n = 1)))
source("../redivis_config.R")

datasets <- rbind(
  data.frame(dataset = IRW_CORE_DATASETS, group = "core"),
  data.frame(dataset = IRW_AUX_DATASETS[c("comp", "nom", "sim")],
             group   = c("comps", "nom", "simsyn")),
  data.frame(dataset = IRW_CONJ_DATASETS, group = "conj"),
  data.frame(dataset = IRW_RANK_DATASETS, group = "rank"),
  data.frame(dataset = IRW_TEXT_DATASETS, group = "itemtext")
)

fmt_time <- function(ms) format(as.POSIXct(ms / 1000, origin = "1970-01-01", tz = "UTC"), "%Y-%m-%d %H:%M:%OS3")

cache <- if (file.exists("dataset_growth.csv")) read.csv("dataset_growth.csv", colClasses = "character") else
  data.frame(dataset = character(), tag = character(), is_released = character())
cache <- cache[cache$is_released == "TRUE", ]
cache_key <- paste(cache$dataset, cache$tag)

rows <- list()
for (i in seq_len(nrow(datasets))) {
  name <- datasets$dataset[i]
  ds <- redivis$organization(IRW_OWNER)$dataset(name, version = "current")
  versions <- ds$list_versions()
  n_new <- 0
  for (v in versions) {
    p <- v$properties
    if (isTRUE(p$isDeleted)) next
    hit <- match(paste(name, p$tag), cache_key)
    if (isTRUE(p$isReleased) && !is.na(hit)) {
      row <- cache[hit, ]
      row$group <- datasets$group[i]
      rows[[length(rows) + 1]] <- row
      next
    }
    n_new <- n_new + 1
    d <- v$dataset()
    n_tables <- length(d$list_tables())
    ## NOTE: releasedAt is unreliable for a growth timeline -- it was bulk-set
    ## to a recent re-release date for many older versions (e.g. v1.0 shows
    ## createdAt 2024-11-26 but releasedAt 2026-07-20). createdAt reflects
    ## when each version was actually created and is used here instead.
    rows[[length(rows) + 1]] <- data.frame(
      dataset      = name,
      group        = datasets$group[i],
      tag          = p$tag,
      is_released  = isTRUE(p$isReleased),
      created_at   = fmt_time(p$createdAt),
      released_at  = if (is.null(p$releasedAt)) NA else fmt_time(p$releasedAt),
      n_tables     = n_tables
    )
  }
  message(name, ": ", length(versions), " versions, ", n_new, " fetched")
}

growth <- do.call(rbind, lapply(rows, function(r) { r[] <- lapply(r, as.character); r }))
growth <- growth[order(growth$dataset, growth$created_at), ]
write.csv(growth, "dataset_growth.csv", row.names = FALSE)
