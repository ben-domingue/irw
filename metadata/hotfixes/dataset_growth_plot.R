## Plot table-count growth over time for the 3 core IRW datasets.
## Top panel: total tables across all 3 datasets combined.
## Bottom panel: each dataset separately.
## Input: metadata/hotfixes/dataset_growth.csv (from dataset_growth.R)
## Output: metadata/hotfixes/dataset_growth.png

library(ggplot2)
library(patchwork)

growth <- read.csv("metadata/hotfixes/dataset_growth.csv")
growth$created_at <- as.POSIXct(growth$created_at, tz = "UTC")
growth <- growth[order(growth$dataset, growth$created_at), ]

## Combine the 3 datasets' step functions into one total-over-time series:
## at every version timestamp (across all datasets), carry forward each
## dataset's most recent table count and sum them.
all_times <- sort(unique(growth$created_at))
by_dataset <- split(growth, growth$dataset)
totals <- Reduce(`+`, lapply(by_dataset, function(df) {
  idx <- findInterval(all_times, df$created_at)
  vals <- df$n_tables[pmax(idx, 1)]
  vals[idx == 0] <- 0
  vals
}))
total_df <- data.frame(created_at = all_times, n_tables = totals)

xlim <- range(growth$created_at)

p_total <- ggplot(total_df, aes(x = created_at, y = n_tables)) +
  geom_step(linewidth = 1, color = "black") +
  scale_x_datetime(limits = xlim) +
  labs(x = NULL, y = "Total tables", title = "Growth of the IRW core datasets") +
  theme_minimal()

p_by_dataset <- ggplot(growth, aes(x = created_at, y = n_tables, color = dataset)) +
  geom_step(linewidth = 1) +
  scale_x_datetime(limits = xlim) +
  labs(x = NULL, y = "Number of tables", color = "Dataset") +
  theme_minimal()

p <- p_total / p_by_dataset

ggsave("metadata/hotfixes/dataset_growth.png", p, width = 8, height = 8, dpi = 150)
