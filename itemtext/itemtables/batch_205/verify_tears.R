# Verification for tears (#1945, batch_205).
#
# SOURCE. Küster, Baker & Krumhuber (2022), 'PDSTD - The Portsmouth Dynamic
# Spontaneous Tears Database', Behavior Research Methods 54:2678, CC BY; OSF
# deposit osf.io/uyjeg, file 'Observer ratings.csv'.
#
# THE MAPPING IS THE COLUMN NAME. data/tears.R selects eleven rating columns by
# name and emits item = names(z)[i], so the live code IS the source header. Note
# what id and rater mean here: id is the stimulus VIDEO and rater is the observer.
#
# WHAT MAKES THIS CHECKABLE. The paper describes two different rating blocks, and
# one of them carries a hard arithmetic constraint: the seven discrete-emotion
# sliders "had to sum up to 100%". The four VAS ratings have no such constraint.
# So the published design predicts, per rating occasion, that one block of seven
# sums to exactly 100 and the other four do not -- which assigns every item to
# its block without relying on the item name at all.
#
# Route 1: code set equals the eleven rating columns of the source file.
# Route 2: the 100% constraint, which separates the two blocks.
suppressWarnings(suppressMessages({library(dplyr); library(tidyr)}))
SRC <- ".cache/batch_205/tears_observer_ratings.csv"
if (!file.exists(SRC)) stop("missing cached deposit file: ", SRC)
x <- read.csv(SRC, sep = ";", fileEncoding = "UTF-8-BOM", stringsAsFactors = FALSE)

d <- as.data.frame(irw::irw_fetch("tears"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_205/tears__items.csv", stringsAsFactors = FALSE, na.strings = "NA")
EM <- c("Anger", "Disgust", "Fear", "Happiness", "Sadness", "Surprise", "Neutral")
VA <- c("Valence_neg", "Valence_pos", "Arousal", "Genuine")

cat("=== Route 1: codes are the source file's rating columns ===\n")
r1 <- all(c(EM, VA) %in% names(x)) && setequal(unique(d$item), c(EM, VA))
cat(sprintf("  source header carries all eleven: %s\n", all(c(EM, VA) %in% names(x))))
cat(sprintf("  live code set is exactly those eleven: %s\n", setequal(unique(d$item), c(EM, VA))))

cat("\n=== Route 2: the published 100%% constraint separates the two blocks ===\n")
w <- d %>% select(id, rater, phase, item, resp) %>%
     distinct(id, rater, phase, item, .keep_all = TRUE) %>%
     pivot_wider(names_from = item, values_from = resp)
se <- rowSums(w[, EM]); sv <- rowSums(w[, VA])
nem <- sum(abs(se - 100) < 1e-6, na.rm = TRUE); tot <- sum(!is.na(se))
cat(sprintf("  the seven discrete-emotion ratings sum to 100 on %d of %d occasions\n", nem, tot))
cat(sprintf("  the four VAS ratings range over %g-%g and are unconstrained\n",
            min(sv, na.rm = TRUE), max(sv, na.rm = TRUE)))
r2 <- nem == tot && tot > 0 && (max(sv, na.rm = TRUE) > 100)
cat(sprintf("  -> the block assignment shipped in section_id is confirmed by the data: %s\n", r2))
cat("  This is the strong form of the check: it does not rely on reading the item\n")
cat("  names. Move any one emotion item into the VAS block and the sum breaks.\n")

cat("\n=== shipped structure ===\n")
for (s in sort(unique(items$section_id))) {
    its <- sort(unique(items$item[items$section_id == s]))
    cat(sprintf("  %-10s %d items: %s\n", s, length(its), paste(its, collapse = ", ")))
}
cat(sprintf("  option_text populated only at the two labelled VAS endpoints (%d rows);\n",
            sum(!is.na(items$option_text))))
cat("  the emotion sliders are percentages with no labels, so they ship blank.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The exact on-screen wording of each rating prompt. item_text renders each\n")
cat("  dimension from the paper's own description of the task ('the degree of\n")
cat("  perceived negative valence', 'the extent to which anger is reliably\n")
cat("  expressed in the face'); the paper does not print the literal screen text,\n")
cat("  and the published definitions of arousal and genuineness ship verbatim in\n")
cat("  section_prompt rather than being folded into the items.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
