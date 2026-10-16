## MRE variant of dataset_growth_plot.R: every series on one panel, with the
## x-axis as log(days before today). The axis is reversed so time runs left to
## right: the oldest versions are on the left and today is on the right.
## Input: dataset_growth.csv (canonical copy at ~/Dropbox/projects/irw/dataset_growth.csv)
## Output: metadata/table_count/dataset_growth_mre.pdf

library(ggplot2)

growth <- read.csv("~/Dropbox/projects/irw/dataset_growth.csv")
growth$created_at <- as.POSIXct(growth$created_at, tz = "UTC")
growth <- growth[order(growth$dataset, growth$created_at), ]
growth$group <- sub("^nominal$", "nom", sub("^conjoint$", "conj", sub("^rankings$", "rank", growth$group)))
families <- c("comps", "simsyn", "nom", "rank", "conj", "itemtext")

## Step functions summed over datasets, as in dataset_growth_plot.R. Today is
## appended so every line runs up to the present.
today <- as.POSIXct(Sys.time(), tz = "UTC")
all_times <- sort(unique(c(growth$created_at, today)))
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
first_seen <- tapply(growth$created_at, growth$group, min)
total_df <- total_df[total_df$created_at >= first_seen[total_df$group], ]
total_df <- total_df[total_df$group == "core" | (total_df$group %in% families & total_df$n_tables > 0), ]

## Days before today, then log of that. Versions made today (0 days) are
## dropped because log(0) is -Inf.
total_df$days_ago <- as.numeric(difftime(today, total_df$created_at, units = "days"))
total_df <- total_df[total_df$days_ago > 0, ]
total_df$log_days_ago <- log(total_df$days_ago)
total_df$group <- factor(total_df$group, levels = c("core", families))

ends <- do.call(rbind, lapply(split(total_df, total_df$group, drop = TRUE), function(g) g[which.min(g$days_ago), ]))

p <- ggplot(total_df, aes(x = log_days_ago, y = n_tables, color = group)) +
  geom_step(linewidth = 0.9) +
  geom_text(data = ends, aes(label = paste0(group, " (", format(n_tables, big.mark = ","), ")")),
            hjust = -0.08, size = 3, show.legend = FALSE) +
  scale_y_log10(labels = scales::comma) +
  scale_x_reverse(breaks = log(c(1, 7, 30, 90, 365, 730)),
                  labels = c("1 d", "1 wk", "1 mo", "3 mo", "1 yr", "2 yr")) +
  scale_color_brewer(palette = "Dark2") +
  coord_cartesian(clip = "off") +
  labs(x = "Time before today (log scale)", y = "Tables (log scale)", color = NULL,
       title = "IRW table count over time, all series") +
  theme_minimal() +
  theme(legend.position = "bottom", plot.margin = margin(5, 80, 5, 5))

pdf("dataset_growth_mre.pdf", width = 7, height = 7)
print(p)
invisible(dev.off())

png("dataset_growth_mre.png", width = 2100, height = 2100, res = 300)
print(p)
invisible(dev.off())
