## Pull timestamped table counts across every version of the IRW datasets on
## Redivis -- the core warehouses, the competitions/nominal/simsyn shards, and
## the item-text shards -- for plotting growth over time.
## Output: metadata/table_count/dataset_growth.csv

library(redivis)
Sys.setenv(REDIVIS_API_TOKEN = trimws(readLines("~/.redivis_api_token", n = 1)))
source("../redivis_config.R")

datasets <- rbind(
  data.frame(dataset = IRW_CORE_DATASETS, group = "core"),
  data.frame(dataset = IRW_AUX_DATASETS[c("comp", "nom", "sim", "conj")],
             group   = c("comps", "nominal", "simsyn", "conjoint")),
  data.frame(dataset = IRW_TEXT_DATASETS, group = "itemtext")
)

rows <- list()
for (i in seq_len(nrow(datasets))) {
  name <- datasets$dataset[i]
  ds <- redivis$organization(IRW_OWNER)$dataset(name, version = "latest")
  versions <- ds$list_versions()
  for (v in versions) {
    p <- v$properties
    if (isTRUE(p$isDeleted)) next
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
      created_at   = as.POSIXct(p$createdAt / 1000, origin = "1970-01-01", tz = "UTC"),
      released_at  = as.POSIXct(p$releasedAt / 1000, origin = "1970-01-01", tz = "UTC"),
      n_tables     = n_tables
    )
  }
  message(name, ": done (", length(versions), " versions)")
}

growth <- do.call(rbind, rows)
growth <- growth[order(growth$dataset, growth$created_at), ]
write.csv(growth, "dataset_growth.csv", row.names = FALSE)
