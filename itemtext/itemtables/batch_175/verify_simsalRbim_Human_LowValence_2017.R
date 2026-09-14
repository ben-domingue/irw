# verify_simsalRbim_Human_LowValence_2017.R  (batch_175)
#
# Picture-stimulus paired-comparison task (Pfefferle et al. 2025, BRM 57:193,
# doi:10.3758/s13428-025-02668-5). Participants saw two OASIS pictures at a time
# and pressed the arrow key for the one evoking the more positive feeling.
# item_text and option_text are blank by design (picture-stimulus ruling
# 2026-09-05); the table ships only the experiment's own instructions.
#
# The two mappings the table relies on:
#   A. item <-> stimulus. data/simsalRbim.R takes `item` verbatim from the raw
#      file's optionA/optionB values (the code IS the source value), and those
#      names are the OASIS picture themes (Table S1 / experiment page:
#      Sunset_1, Flowers_3, Food_4, Grass_1, House_1, Monkey_2, Timber_1).
#   B. resp <-> meaning. resp is quantityA/quantityB: 1 = this picture was the
#      one chosen in that trial, 0 = the other picture was chosen.
#
# Routes: (1) re-run the processing script's pivot over the raw GitHub file and
# reproduce per-item n AND per-item win count against the live table (the win
# counts are all distinct, so this separates every item from every other);
# (2) route 8/4-style semantic check: the win ranking against the OASIS valence
# norms printed in Table S1 must reproduce the paper's reported Spearman
# rho(5) = 0.86 (Results, "Humans") and be positive -- a flipped resp would give
# a negative rho; (3) exactly one of quantityA/quantityB is 1 on every raw trial.
#
# WHAT THIS DOES NOT ESTABLISH: that the 63 subject ids in the deposit are the
# 48 participants the paper reports (they are not the same count -- see
# provenance), nor the administered language of the 2017 lab run. Sunset and
# Flowers are near-tied (263 vs 267 wins; Fig. 1 shows them near-tied too), so
# the paper's 0.86 corresponds to Sunset ranked above Flowers while raw win
# counts put Flowers one ahead (rho 0.82); both are printed.

suppressMessages({library(irw); library(dplyr); library(tidyr)})

TABLE <- "simsalRbim_Human_LowValence_2017"
RAW   <- "https://raw.githubusercontent.com/mytalbot/simsalRbim_data/main/Human_LowValence_2017.txt"
OASIS <- c(Sunset = 6.07, Flowers = 5.79, Food = 5.61, Grass = 4.96,
           House = 4.71, Monkey = 4.03, Timber = 3.83)   # Table S1, low valence range
PAPER_RHO <- 0.86

raw <- read.table(RAW, header = TRUE, stringsAsFactors = FALSE)
ok3 <- all(raw$quantityA + raw$quantityB == 1)
cat(sprintf("CLAIM 3 -- raw trials: %d, trials with exactly one choice: %d\n\n",
            nrow(raw), sum(raw$quantityA + raw$quantityB == 1)))

rb <- raw %>% mutate(trial = row_number()) %>%
    pivot_longer(cols = c(optionA, optionB, quantityA, quantityB),
                 names_to = c(".value", "choice_side"),
                 names_pattern = "(option|quantity)([AB])") %>%
    rename(id = subjectID, item = option, resp = quantity)
rec <- rb %>% group_by(item) %>% summarise(n_raw = n(), wins_raw = sum(resp))

live <- irw::irw_fetch(TABLE)   # 2,646 rows
lv <- live %>% group_by(item) %>% summarise(n_live = n(), wins_live = sum(resp))

m <- merge(rec, lv, by = "item", all = TRUE)
cat("CLAIM 1 -- raw rebuild vs live, per item\n")
print(m, row.names = FALSE)
ok1 <- nrow(m) == 7 && !anyNA(m) && all(m$n_raw == m$n_live) &&
       all(m$wins_raw == m$wins_live)
cat(sprintf("=> all n and win counts equal: %s; distinct win counts: %d of %d\n\n",
            ok1, length(unique(m$wins_live)), nrow(m)))

m$p <- m$wins_live / m$n_live
m$oasis <- OASIS[m$item]
rho <- cor(m$p, m$oasis, method = "spearman")
rk <- rank(-m$p); names(rk) <- m$item
rk_paper <- rk; rk_paper[c("Sunset", "Flowers")] <- rk[c("Flowers", "Sunset")]
rho_paper_order <- cor(-rk_paper, m$oasis[match(names(rk_paper), m$item)], method = "spearman")
cat("CLAIM 2 -- choice proportion vs OASIS valence (Table S1)\n")
print(m[order(-m$p), c("item", "p", "oasis")], row.names = FALSE)
cat(sprintf("Spearman(choice proportion, OASIS valence) = %.3f\n", rho))
cat(sprintf("Same with the near-tied Sunset/Flowers pair in the paper's Fig. 1 order = %.3f (paper: %.2f)\n",
            rho_paper_order, PAPER_RHO))
cat(sprintf("Flipped resp (0 = chosen) would give %.3f\n", -rho))
ok2 <- rho > 0.7 && abs(rho_paper_order - PAPER_RHO) < 0.01

cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
