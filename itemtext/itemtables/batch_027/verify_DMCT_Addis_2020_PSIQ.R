# verify_DMCT_Addis_2020_PSIQ.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST
#   The 35 IRW item codes (PsiQ1-PsiQ3, PsyQ4-PsyQ35, i.e. the source .sav column
#   names, item numbers 1..35) carry the canonical Psi-Q item wording, assigned as
#     1-5 vision, 6-10 sound, 11-15 smell, 16-20 taste, 21-25 touch,
#     26-30 bodily sensation, 31-35 feeling
#   and, within each block, in the order of the Psi-Q form itself
#   (vision = friend / cat / sunset / front door / bonfire, etc.).
#
# WHAT THIS SCRIPT CHECKS
#   (1) DECISIVE, block membership: the study's own .sav carries seven subscale
#       columns (PsiQ_Visual ... PsiQ_Feeling). If item n -> block assignment is
#       right, each subscale column must equal the sum of its five consecutive
#       items, participant by participant. That is the PASS/FAIL criterion.
#   (2) NOT DECISIVE, within-block order: compares this study's per-item means
#       against the Dutch Psi-Q validation (Woelk et al. 2022, OSF 6ebnw), whose
#       .sav variable labels name every item, under the two published orderings
#       (the Psi-Q form order shipped here vs. the short-form-first ordering used
#       in the Spanish/Japanese validation appendices). Printed, not gated:
#       it does NOT separate them, which is why the verification status is PARTIAL.
#
# It does not re-check item/resp set membership; validate_items.R did that.

suppressMessages({library(haven); library(irw)})

TABLE <- "DMCT_Addis_2020_PSIQ"
ITEMS <- c("PsiQ1","PsiQ2","PsiQ3", paste0("PsyQ", 4:35))

cachedir <- file.path("~/.cache/irw_itemtext_DMCT_Addis_2020_PSIQ")
cachedir <- path.expand(cachedir); dir.create(cachedir, showWarnings = FALSE, recursive = TRUE)
get <- function(url, f) { p <- file.path(cachedir, f)
  if (!file.exists(p)) download.file(url, p, quiet = TRUE); p }

## ---- live item set (server-side aggregate; no full export) -----------------
live <- tryCatch(irw::irw_table_sets(TABLE), error = function(e) NULL)
if (!is.null(live)) {
  li <- sort(as.character(live$items %||% live$item))
  cat("live item set == source .sav column names: ",
      identical(li, sort(ITEMS)), "\n\n", sep = "")
} else cat("live item set: irw_table_sets() unavailable, skipped\n\n")

## ---- (1) block membership, against the study's own subscale columns --------
sav <- read_sav(get("https://osf.io/download/brnyh/?view_only=43c4db49648f428c914ebdcc4e191f27",
                    "Data_merged_multilevel_trimmed.sav"))
sav <- sav[!duplicated(sav$Participant_Code), ]
blocks <- list(PsiQ_Visual = 1:5, PsiQ_Sound = 6:10, PsiQ_Smell = 11:15,
               PsiQ_Taste = 16:20, PsiQ_Touch = 21:25, PsiQ_Bodily = 26:30,
               PsiQ_Feeling = 31:35)
cat("(1) subscale column == sum of the five items assigned to that modality\n")
cat(sprintf("    n = %d participants\n", nrow(sav)))
worst <- 0
for (b in names(blocks)) {
  s <- rowSums(sav[, ITEMS[blocks[[b]]]])
  d <- max(abs(s - as.numeric(sav[[b]])), na.rm = TRUE)
  worst <- max(worst, d)
  cat(sprintf("    %-13s items %2d-%2d  max |sum - stored| = %g\n",
              b, min(blocks[[b]]), max(blocks[[b]]), d))
}
cat(sprintf("    worst deviation across all 7 subscales: %g\n\n", worst))

## ---- (2) within-block order: per-item means vs. the labelled Dutch sample --
nl <- read_sav(get("https://osf.io/download/fhjvx/", "Woelk_Data_Study1.sav"))
# Dutch columns run in the Psi-Q form's own order within each modality block,
# and each carries a variable label naming the item (checked below).
nlcols <- as.vector(sapply(c("Visueel","Geluid","Geur","Smaak","Aanraak","Sensatie","Gevoel"),
                           function(p) paste0(p, 1:5, "_1")))
nlmean <- sapply(nlcols, function(c) mean(nl[[c]], na.rm = TRUE))
ours   <- sapply(ITEMS, function(c) mean(sav[[c]], na.rm = TRUE))

# permutation from form order -> Spanish/Japanese appendix order, within blocks
alt <- rep(0:6, each = 5) * 5 +
       c(5,3,2,1,4,  4,2,1,5,3,  4,5,2,3,1,  5,3,1,2,4,  5,1,2,4,3,  1,5,4,2,3,  1,2,5,3,4)
cat("    Dutch item labels, form order:\n")
for (i in seq_along(nlcols))
  cat(sprintf("      %2d %-12s %s\n", i, nlcols[i],
      sub(".*- ", "", attr(nl[[nlcols[i]]], "label"))))
cat("(2) per-item means vs. Woelk et al. (2022) Dutch validation, N =", nrow(nl), "\n")
cat(sprintf("    form order shipped here : r = %.3f\n", cor(ours, nlmean)))
cat(sprintf("    appendix (ES/JP) order  : r = %.3f\n", cor(ours, nlmean[alt])))
set.seed(1); nullr <- replicate(5000, {
  p <- unlist(lapply(0:6, function(b) b*5 + sample(5)))
  cor(ours, nlmean[p]) })
cat(sprintf("    within-block random permutations: mean r = %.3f, P(r >= shipped) = %.3f\n",
            mean(nullr), mean(nullr >= cor(ours, nlmean))))
cat("    => this route does NOT separate the two published orderings. Within-block\n")
cat("       position rests on the Psi-Q form's own numbering (Woelk .sav variable\n")
cat("       labels; psytests.org form), not on these data. Status is PARTIAL.\n\n")

cat(if (worst == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
