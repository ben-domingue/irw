## Plot table-count growth over time for the IRW datasets.
## Top panel: total tables per group (core, comps, nominal, simsyn, itemtext).
## Bottom panel: each core dataset separately.
## Input: metadata/table_count/dataset_growth.csv (from dataset_growth.R)
## Output: metadata/table_count/dataset_growth.pdf

library(ggplot2)
library(patchwork)

growth <- read.csv("dataset_growth.csv")
growth$created_at <- as.POSIXct(growth$created_at, tz = "UTC")
growth <- growth[order(growth$dataset, growth$created_at), ]

## Combine datasets' step functions into one total-over-time series: at every
## version timestamp, carry forward each dataset's most recent table count and
## sum them.
all_times <- sort(unique(growth$created_at))
step_total <- function(df) {
  Reduce(`+`, lapply(split(df, df$dataset), function(d) {
    idx <- findInterval(all_times, d$created_at)
    vals <- d$n_tables[pmax(idx, 1)]
    vals[idx == 0] <- 0
    vals
  }))
}
total_df <- do.call(rbind, lapply(split(growth, growth$group), function(g) {
  data.frame(group = g$group[1], created_at = all_times, n_tables = step_total(g))
}))

xlim <- range(growth$created_at)
ies_start <- as.POSIXct("2024-09-01", tz = "UTC")

p_total <- ggplot(total_df, aes(x = created_at, y = n_tables, color = group)) +
  geom_step(linewidth = 1) +
  geom_vline(xintercept = as.numeric(ies_start), linetype = "dashed", color = "grey40") +
  annotate("text", x = ies_start, y = Inf, label = "IES start", vjust = 1.5, hjust = -0.1, color = "grey40", size = 3.2) +
  scale_x_datetime(limits = xlim) +
  labs(x = NULL, y = "Total tables", color = "Group", title = "Growth of the IRW datasets") +
  theme_minimal()

core <- growth[growth$group == "core", ]
p_by_dataset <- ggplot(core, aes(x = created_at, y = n_tables, color = dataset)) +
  geom_step(linewidth = 1) +
  geom_vline(xintercept = as.numeric(ies_start), linetype = "dashed", color = "grey40") +
  scale_x_datetime(limits = xlim) +
  labs(x = NULL, y = "Number of tables", color = "Core dataset") +
  theme_minimal()

p <- p_total / p_by_dataset

ggsave("dataset_growth.pdf", p, width = 8, height = 8, dpi = 150)
