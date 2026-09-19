# Verification for FEDSP_Trzcinska_2023_MonKnow (#1945, batch_204).
#
# SOURCE. The deposit's own SPSS file, data-3.sav (osf.io/sa87b; Trzcinska,
# Family Economic Deprivation and Self-esteem among Preschoolers). Its VARIABLE
# LABELS carry the whole content of this two-item measure:
#     c_MonKnow_1  "condition1: 2zl vs 5zl"
#     c_MonKnow_2  "condition2: 5 x 5zl vs 2 x 20zl vs 1 x 50zl"
# That is level 1 of the source ranking -- the label is attached to the column
# the live code was taken from, so there is no mapping step at all.
#
# WHY THE SHIPPED TEXT IS BRACKETED. The labels describe a STIMULUS, not a
# question: the child was shown coins and notes and asked which was worth more.
# The administered question wording is nowhere in the deposit, so item_text
# ships the set-up in brackets, '[children were shown: a 2 zl coin and a 5 zl
# coin]', rather than invent a stem or leave the reader with a bare code.
#
# Route 1: the labels exist and name the two codes (re-read here, not quoted).
# Route 2: the processing script reproduced exactly -- the deposit filter and
#   the distinct() give back the live row count and per-item proportions.
if (!requireNamespace("haven", quietly = TRUE)) stop("needs haven to read the .sav")
SAV <- ".cache/batch_204/fedsp_data-3.sav"
if (!file.exists(SAV)) stop("missing cached deposit file: ", SAV)
suppressWarnings(suppressMessages({library(haven); library(dplyr)}))
s <- read_sav(SAV)

d <- as.data.frame(irw::irw_fetch("FEDSP_Trzcinska_2023_MonKnow"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== Route 1: the .sav's own variable labels ===\n")
codes <- grep("^c_MonKnow_", names(s), value = TRUE)
for (v in codes) cat(sprintf("  %-14s label: %s\n", v, attr(s[[v]], "label")))
r1 <- setequal(codes, unique(d$item))
cat(sprintf("  labelled c_MonKnow_ columns %d, live codes %d, identical: %s\n",
            length(codes), length(unique(d$item)), r1))
cat("  Note c_MonKnow (no trailing underscore) is labelled 'sum of points from\n")
cat("  condition 1 and 2' and is a composite; starts_with('c_MonKnow_') in the\n")
cat("  processing script excludes it, so no derived score reaches this table.\n")

cat("\n=== Route 2: the processing script reproduced ===\n")
# data/FEDSP_Trzcinska_2024.R, verbatim in effect:
f <- s[!is.na(s$child_age_in_months) & !is.na(s$c_PSIAT), ]
m <- f |> select(id = number, starts_with("c_MonKnow_")) |> distinct()
cat(sprintf("  deposit rows %d -> after the age/PSIAT filter %d -> after distinct() %d\n",
            nrow(s), nrow(f), nrow(m)))
cat(sprintf("  implied long rows %d; live rows %d\n", nrow(m) * length(codes), nrow(d)))
r2a <- nrow(m) * length(codes) == nrow(d)
r2b <- TRUE
for (v in codes) {
    a <- as.numeric(m[[v]]); b <- d$resp[d$item == v]
    same <- length(a) == length(b) && abs(mean(a, na.rm=TRUE) - mean(b, na.rm=TRUE)) < 1e-9 &&
            identical(sort(a), sort(as.numeric(b)))
    r2b <- r2b && same
    cat(sprintf("  %-14s reproduced n=%3d p=%.4f | live n=%3d p=%.4f | identical: %s\n",
                v, length(a), mean(a, na.rm=TRUE), length(b), mean(b, na.rm=TRUE), same))
}
cat("  The whole response vector matches, not just its mean, so the filter, the\n")
cat("  dyad dedup and the column selection are all confirmed rather than assumed.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The administered question. The .sav labels give the stimulus for each\n")
cat("  condition and nothing in the deposit prints what the child was asked, so\n")
cat("  item_text is a bracketed description of the set-up. It is deliberately not\n")
cat("  written as a question: no route could check wording that is not published.\n")
cat("\nVERDICT:", if (r1 && r2a && r2b) "PASS" else "FAIL", "\n")
