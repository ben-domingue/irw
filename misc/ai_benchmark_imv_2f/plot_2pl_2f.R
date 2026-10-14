# One-panel version of the AI-benchmark IMV overview figure: the gain from a
# second factor (2PL -> exploratory two-factor 2PL), primary panel only.
# One dot per fitted matrix; the black bar is each row's median; dashed line is
# no gain. Reads ai_benchmark_imv_results.csv in this directory (IRW v512,
# run 2026-10-02; see README.md). Usage: Rscript plot_2pl_2f.R

suppressMessages({library(dplyr); library(ggplot2)})
here <- dirname(sub("--file=", "", grep("--file=", commandArgs(), value = TRUE)[1]))
if (is.na(here) || here == "") here <- "."

irw_blue <- "#2166ac"; irw_red <- "#d73027"; irw_grey <- "grey50"
theme_set(theme_minimal(base_size = 13))

res <- read.csv(file.path(here, "ai_benchmark_imv_results.csv"))
ov <- res |>
  filter(panel == "primary") |>
  mutate(who = factor(case_when(source == "human" ~ "People",
                                draw == 0 ~ "AI: full item set",
                                TRUE ~ "AI: 300-item draws"),
                      levels = c("People", "AI: 300-item draws", "AI: full item set")),
         imv = imv_2pl_2f)
ov_med <- ov |> group_by(who) |> summarise(n = n(), imv = median(imv), .groups = "drop")
print(ov_med)

set.seed(2)
p <- ggplot(ov, aes(x = imv, y = who, colour = who)) +
  geom_vline(xintercept = 0, colour = irw_grey, linetype = "dashed") +
  geom_point(size = 2.6, alpha = 0.75, position = position_jitter(width = 0, height = 0.18)) +
  geom_segment(data = ov_med, colour = "black", linewidth = 1.2,
               aes(x = imv, xend = imv, y = as.numeric(who) - 0.32, yend = as.numeric(who) + 0.32)) +
  scale_colour_manual(values = c("AI: full item set" = irw_red, "AI: 300-item draws" = irw_red,
                                 "People" = irw_blue), guide = "none") +
  labs(x = "IMV, 2PL → two-factor model", y = NULL) +
  theme(panel.grid.major.y = element_blank(), panel.grid.minor = element_blank())

ggsave(file.path(here, "fig_2pl_2f.png"), p, width = 7, height = 3.4, dpi = 200, bg = "white")
ggsave(file.path(here, "fig_2pl_2f.pdf"), p, width = 7, height = 3.4, device = cairo_pdf)
