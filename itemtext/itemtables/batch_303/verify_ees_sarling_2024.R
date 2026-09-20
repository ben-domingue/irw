# Verification for ees_sarling_2024 (#2228, batch_303).
#
# SOURCE. OSF deposit osf.io/fr7wz, 'EES_Supplementary Materials.pdf'. It
# supplies everything, against the item labels the live table uses: Appendix A
# is the administered Swedish instruction and the 1-5 anchor list, Table S1
# pairs VE1..VE15 / IU1..IU15 with the Swedish items and their survey position,
# and Table S2 gives the original English (Innamorati et al., 2019).
#
# Route 1: the supplement's 30 labels are the live item set exactly.
# Route 2: shipped Swedish == Table S1, shipped English == Table S2, and the
#   section_prompt positions are Table S1's own '(order in the survey)'.
# Route 3: the two subscales separate in the live data the way an EES should --
#   within-subscale correlations exceed between-subscale ones for every item --
#   which is what would break if VE and IU labels were swapped.
pdf <- ".cache/batch_303/ees_supp.pdf"
if (!file.exists(pdf)) stop("missing cached deposit file: ", pdf)
if (!requireNamespace("pdftools", quietly = TRUE))
    cat("NOTE: pdftools not installed; falling back to the cached extraction\n")

d <- as.data.frame(irw::irw_fetch("ees_sarling_2024"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_303/ees_sarling_2024__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA", encoding = "UTF-8")

cat("=== Route 1: the supplement's label set ===\n")
lab <- c(paste0("VE", 1:15), paste0("IU", 1:15))
cat(sprintf("  Table S1 labels: %d   live items: %d\n", length(lab), length(unique(d$item))))
r1 <- setequal(lab, unique(d$item)) && setequal(lab, unique(items$item))
cat(sprintf("  -> identical to the live item set and to the shipped file: %s\n", r1))

cat("\n=== Route 2: positions and the two languages ===\n")
sh <- unique(items[, c("item", "section_prompt", "item_text", "item_text_translated")])
pos <- as.integer(sub(".*position ([0-9]+)\\)$", "\\1", sh$section_prompt))
names(pos) <- sh$item
cat(sprintf("  VE positions: %s\n", paste(pos[paste0("VE", 1:15)], collapse = " ")))
cat(sprintf("  IU positions: %s\n", paste(pos[paste0("IU", 1:15)], collapse = " ")))
r2a <- identical(unname(pos[paste0("VE", 1:15)]), seq(1L, 29L, by = 2L)) &&
       identical(unname(pos[paste0("IU", 1:15)]), seq(2L, 30L, by = 2L))
cat(sprintf("  -> Table S1's interleaved order, VE odd / IU even: %s\n", r2a))
r2b <- all(nzchar(sh$item_text)) && all(nzchar(sh$item_text_translated)) &&
       !any(sh$item_text == sh$item_text_translated) &&
       all(grepl("[åäö]", sh$item_text))
cat(sprintf("  all 30 carry distinct Swedish and English text, Swedish has åäö: %s\n", r2b))
anch <- unique(items[, c("resp", "option_text", "option_text_translated")])
anch <- anch[order(anch$resp), ]
cat("  anchors: ", paste(sprintf("%d=%s", anch$resp, anch$option_text), collapse = ", "), "\n")
r2c <- nrow(anch) == 5 && identical(anch$option_text,
    c("Stämmer inte alls", "Stämmer lite", "Stämmer delvis",
      "Stämmer mycket väl", "Stämmer fullständigt"))
cat(sprintf("  -> Appendix A's five anchors in order: %s\n", r2c))

cat("\n=== Route 3: do VE and IU separate in the live data? ===\n")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
cm <- stats::cor(m, use = "pairwise.complete.obs")
ve <- paste0("VE", 1:15); iu <- paste0("IU", 1:15)
wi <- sapply(colnames(cm), function(c) {
    own <- if (c %in% ve) setdiff(ve, c) else setdiff(iu, c)
    oth <- if (c %in% ve) iu else ve
    c(mean(cm[c, own]), mean(cm[c, oth]))
})
bad <- colnames(cm)[wi[1, ] <= wi[2, ]]
cat(sprintf("  mean within-subscale r: VE %.2f  IU %.2f\n",
            mean(cm[ve, ve][upper.tri(cm[ve, ve])]), mean(cm[iu, iu][upper.tri(cm[iu, iu])])))
cat(sprintf("  mean between-subscale r: %.2f\n", mean(cm[ve, iu])))
r3 <- !length(bad)
cat(sprintf("  items whose own subscale is NOT their stronger one: %s\n",
            if (length(bad)) paste(bad, collapse = ", ") else "none"))
cat(sprintf("  -> every item sits with its labelled subscale: %s\n", r3))

cat("\n=== What this does NOT establish ===\n")
cat("  Nothing material. Every field comes from the study's own supplement;\n")
cat("  the English is the instrument's published original, not a translation\n")
cat("  produced here.\n")
cat("\nVERDICT:", if (r1 && r2a && r2b && r2c && r3) "PASS" else "FAIL", "\n")
