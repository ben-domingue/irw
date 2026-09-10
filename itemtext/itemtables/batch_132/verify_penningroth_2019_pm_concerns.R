# verify_penningroth_2019_pm_concerns.R
#
# CLAIM: each `any***c` item code carries the concern category named in the shipped
# item_text. 14 of the 15 abbreviations are defined outright on the deposit's own
# META-DATA sheet (S1 File, PLOS ONE 10.1371/journal.pone.0216888); `frnd` is absent
# from that list and is tied to "friendship" by elimination against the paper's ordered
# 15-label list, which matches the DATASET sheet's column order exactly.
#
# FALSIFIABLE PREDICTION: paper Table 4 prints, for 14 named concern categories, the
# percentage of the overall sample (and of each age group) that reported a PM task
# related to that category. Those are the exact quantities mean(resp)*100 computes per
# item in the live table. A permuted label mapping breaks the correspondence.

suppressMessages(library(irw))

TABLE <- "penningroth_2019_pm_concerns"

# Paper Table 4 (10.1371/journal.pone.0216888.t004): overall %, young %, older %.
# "other" (anyothrc) is not in Table 4 -- the paper drops the rarely used category.
PUB <- data.frame(
  item    = c("anyprpc","anyyheac","anyprfc","anyeduc","anyleisc","anyoheac",
              "anyfrndc","anyselfc","anytravc","anykidc","anyretic","anymarc",
              "anyworlc","anywarc"),
  label   = c("Property","Own health","Profession","Education","Leisure","Others' health",
              "Friendship","Self/growth","Travel","Children","Retirement",
              "Marriage/relatives","World issues","War/terrorism"),
  overall = c(55.1, 40.4, 33.7, 31.5, 29.2, 28.1, 24.7, 24.7, 20.2, 16.9, 16.9, 15.7, 11.2, 9.0),
  young   = c(53.6, 39.3, 42.9, 48.2, 26.8, 28.6, 28.6, 26.8, 23.2, 14.3, 14.3, 19.6,  5.4, 1.8),
  older   = c(57.6, 42.4, 18.2,  3.0, 33.3, 27.3, 18.2, 21.2, 15.2, 21.2, 21.2,  9.1, 21.2, 21.2),
  stringsAsFactors = FALSE)

TOL <- 0.06  # papers round to 1 dp; 0.05 plus float slack

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
grp <- as.numeric(d$cov_group_young_vs_older)   # 1 = young, 2 = older

pct <- function(sub) {
  v <- tapply(sub$resp, sub$item, mean) * 100
  v[PUB$item]
}
obs_all <- pct(d)
obs_y   <- pct(d[grp == 1, ])
obs_o   <- pct(d[grp == 2, ])

cat(sprintf("n ids: %d (young %d, older %d)\n\n",
            length(unique(d$id)), length(unique(d$id[grp == 1])), length(unique(d$id[grp == 2]))))
cat(sprintf("%-10s %-19s %7s %7s %7s %7s %7s %7s\n",
            "item", "shipped label", "pub%", "obs%", "pubY%", "obsY%", "pubO%", "obsO%"))
for (i in seq_len(nrow(PUB)))
  cat(sprintf("%-10s %-19s %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f\n",
              PUB$item[i], PUB$label[i], PUB$overall[i], obs_all[i],
              PUB$young[i], obs_y[i], PUB$older[i], obs_o[i]))

worst <- max(abs(c(obs_all - PUB$overall, obs_y - PUB$young, obs_o - PUB$older)))
cat(sprintf("\nlargest deviation across 42 published cells: %.3f pp (tolerance %.2f)\n", worst, TOL))

# Tie-breaking: does any OTHER item reproduce a given row's triple as well?
amb <- character(0)
for (i in seq_len(nrow(PUB))) {
  trip <- c(PUB$overall[i], PUB$young[i], PUB$older[i])
  hits <- names(obs_all)[ abs(obs_all - trip[1]) <= TOL &
                          abs(obs_y   - trip[2]) <= TOL &
                          abs(obs_o   - trip[3]) <= TOL ]
  if (length(hits) > 1) amb <- c(amb, sprintf("%s <-> %s", PUB$item[i], paste(hits, collapse = "/")))
}
cat("rows matched by more than one item: ", if (length(amb)) paste(unique(amb), collapse = "; ") else "none", "\n", sep = "")

cat("Note: anyothrc ('other') is absent from Table 4 and is NOT checked by this route;\n",
    "it is pinned by the META-DATA sheet's explicit 'othr=other'. Children/Retirement\n",
    "share all three published percentages, so this route cannot separate them either --\n",
    "they are separated by META-DATA's explicit 'kid=children' and 'reti=retirement'.\n", sep = "")

# The ONLY tolerated ambiguity is the {anykidc, anyretic} pair, whose three published
# percentages are identical; that pair is pinned by META-DATA, not by this route.
EXPECTED_AMB <- c("anykidc <-> anykidc/anyretic", "anyretic <-> anykidc/anyretic")
unexpected <- setdiff(unique(amb), EXPECTED_AMB)
cat("unexpected ambiguities: ", if (length(unexpected)) paste(unexpected, collapse = "; ") else "none", "\n", sep = "")

ok <- worst <= TOL && length(unexpected) == 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
