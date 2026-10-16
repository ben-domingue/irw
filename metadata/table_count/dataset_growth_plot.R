## Plot table-count growth over time for the IRW datasets.
## Left panel: core tables, summed over the item_response_warehouse shards.
## Right panel: the newer families (comps, simsyn, nom, rank, conj, itemtext),
## from the date the first of them appeared; that date is flagged on the left
## panel too. Log y-scale, since the families run from tens to thousands.
## Input: metadata/table_count/dataset_growth.csv (from dataset_growth.R)
## Output: metadata/table_count/dataset_growth.pdf

library(ggplot2)
library(patchwork)

growth <- read.csv("dataset_growth.csv")
growth$created_at <- as.POSIXct(growth$created_at, tz = "UTC")
growth <- growth[order(growth$dataset, growth$created_at), ]
## Older CSVs used long group names; map them onto the short ones.
growth$group <- sub("^nominal$", "nom", sub("^conjoint$", "conj", sub("^rankings$", "rank", growth$group)))
families <- c("comps", "simsyn", "nom", "rank", "conj", "itemtext")

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
## Start each line at its group's first version rather than a run of zeros.
first_seen <- tapply(growth$created_at, growth$group, min)
total_df <- total_df[total_df$created_at >= first_seen[total_df$group], ]

core_df <- total_df[total_df$group == "core", ]
fam_df <- total_df[total_df$group %in% families & total_df$n_tables > 0, ]
fam_df$group <- factor(fam_df$group, levels = families)
latest <- function(df) do.call(rbind, lapply(split(df, df$group, drop = TRUE), function(g) g[which.max(g$created_at), ]))

ies_start <- as.POSIXct("2024-09-01", tz = "UTC")
fam_start <- as.POSIXct(min(first_seen[families]), origin = "1970-01-01", tz = "UTC")
now <- max(growth$created_at)

p_core <- ggplot(core_df, aes(x = created_at, y = n_tables)) +
  geom_step(linewidth = 1, color = "steelblue4") +
  geom_vline(xintercept = as.numeric(c(ies_start, fam_start)), linetype = "dashed", color = "grey40") +
  annotate("text", x = c(ies_start, fam_start), y = Inf, label = c("IES start", "First newer family"),
           vjust = 1.5, hjust = -0.05, color = "grey40", size = 3.2) +
  annotate("text", x = now, y = max(core_df$n_tables), label = format(tail(core_df$n_tables, 1), big.mark = ","),
           hjust = 1.1, vjust = -0.4, size = 3.2) +
  scale_y_continuous(labels = scales::comma, limits = c(0, NA), expand = expansion(mult = c(0, 0.12))) +
  labs(x = NULL, y = "Tables", title = "Core IRW tables (all shards)") +
  theme_minimal()

fam_latest <- latest(fam_df)
## Spread the end labels so none sit closer than `gap` in log10 units.
gap <- 0.16
fam_latest <- fam_latest[order(fam_latest$n_tables), ]
fam_latest$label_y <- log10(fam_latest$n_tables)
for (k in seq_len(nrow(fam_latest))[-1])
  fam_latest$label_y[k] <- max(fam_latest$label_y[k], fam_latest$label_y[k - 1] + gap)
fam_latest$label_y <- 10^fam_latest$label_y
p_fam <- ggplot(fam_df, aes(x = created_at, y = n_tables, color = group)) +
  geom_step(linewidth = 1) +
  geom_text(data = fam_latest, aes(x = now, y = label_y, label = paste0(group, " (", n_tables, ")")),
            hjust = -0.08, size = 3.2, show.legend = FALSE) +
  scale_x_datetime(limits = c(fam_start, now), date_labels = "%b %Y", expand = expansion(mult = c(0.01, 0.18))) +
  scale_y_log10(labels = scales::comma) +
  scale_color_brewer(palette = "Dark2", guide = "none") +
  coord_cartesian(clip = "off") +
  labs(x = NULL, y = "Tables (log scale)", title = "Newer data families") +
  theme_minimal()

p <- p_core | p_fam

## An arrow from the "First newer family" line on the left to the same date on
## the right panel's x-axis. ggplot can't draw across panels, so draw the
## combined plot, locate both points on the page from the panel viewports, and
## add the arrow with grid on top.
npc_x <- function(plot, t) {
  r <- ggplot_build(plot)$layout$panel_params[[1]]$x.range
  (as.numeric(t) - r[1]) / diff(r)
}
page_loc <- function(vp, x, y) {
  grid::seekViewport(vp)
  loc <- grid::deviceLoc(grid::unit(x, "npc"), grid::unit(y, "npc"))
  grid::upViewport(0)
  loc
}

pdf("dataset_growth.pdf", width = 13, height = 5)
grid::grid.newpage()
grid::grid.draw(patchworkGrob(p))
grid::grid.force()
from <- page_loc("panel-1.11-9-11-9", npc_x(p_core, fam_start), 0.07)
to <- page_loc("panel-2.11-24-11-24", npc_x(p_fam, fam_start), 0)
grid::grid.curve(from$x, from$y, to$x, to$y, curvature = 0.1, ncp = 10, square = FALSE,
                 arrow = grid::arrow(length = grid::unit(0.1, "inches"), type = "closed"),
                 gp = grid::gpar(col = "grey40", fill = "grey40", lwd = 1.2))
invisible(dev.off())
