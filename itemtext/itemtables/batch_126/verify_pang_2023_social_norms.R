# verify_pang_2023_social_norms.R
#
# CLAIM UNDER TEST (two axes):
#
# (A) item_text <-> item.  data/pang_2023_nev_adoption.py assigns item codes
#     POSITIONALLY: item_cols = S1 xlsx columns 6..45, and this table takes
#     item_cols[30:35] (0-based) == spreadsheet columns 36..40, relabelled
#     item_01..item_05.  Those five columns are the questionnaire's Q35-Q39,
#     the Subjective norms (SNs) block, and their wording is the shipped
#     item_text (transcribed from S2 File, whose sentences are the same items).
#     Falsifiable prediction: the full 5-level response-frequency vector of
#     live item_0k must equal that of source column 35+k, cell for cell -- and,
#     more strongly, must match NO OTHER of the 40 item columns in the file.
#
# (B) option_text <-> resp.  The paper's Methods say "1 point (strongly
#     disagree) to 5 points (strongly agree)", but S2 File (the questionnaire)
#     prints every item's options in the order Definitely agree / Agree /
#     Neither / Disagree / Definitely disagree, and the shipped mapping follows
#     that display order (1 = Definitely agree).  Two indirect checks:
#       B1. The export codes single-choice options by DISPLAY POSITION: read
#           that way the S1 demographic columns reproduce the paper's own
#           reported percentages (55.7% male, 88.5% aged 20-40, 90.3%
#           bachelor's or above).
#       B2. Marker items in the BI block: the sample are potential, mostly
#           non-owning users, so "I am driving and will continue to drive an
#           NEV" (Q41) must be the LEAST endorsed BI item and the conditional
#           switch items (Q43/Q44) the most.  Under 1 = agree, mean(Q41) is the
#           HIGHEST and Q43/Q44 the LOWEST.
#
# What this does NOT establish: (B) is an inference from the export's coding
# convention and from item content, not from any value label, and the paper's
# own Methods sentence states the opposite direction. Nothing here ties the
# shipped English to the Chinese the survey was administered in.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "pang_2023_social_norms"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0285815.s001")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
stopifnot(ncol(raw) == 45, nrow(raw) == 309)

blk <- raw[, 36:40]                       # Q35..Q39 == item_01..item_05
cat("source columns used (their wording is the shipped item_text):\n")
for (j in seq_along(blk)) cat(sprintf("  item_%02d <- %s\n", j, substr(names(blk)[j], 1, 70)))

d <- irw::irw_fetch(TABLE)
live <- table(d$item, d$resp)
src  <- t(sapply(blk, function(x) table(factor(x, levels = 1:5))))
rownames(src) <- sprintf("item_%02d", 1:5)

cat("\n(A) per-item response-frequency vectors, source vs live (levels 1..5)\n")
cat(sprintf("%-9s %-22s %-22s %s\n", "item", "source (S1 xlsx)", "live (IRW)", "match"))
okA <- TRUE
for (i in rownames(src)) {
  s <- as.integer(src[i, ]); l <- as.integer(live[i, as.character(1:5)])
  m <- identical(s, l); okA <- okA && m
  cat(sprintf("%-9s %-22s %-22s %s\n", i, paste(s, collapse = "/"),
              paste(l, collapse = "/"), if (m) "yes" else "NO"))
}

# Stronger: each live vector must be unique across ALL 40 item columns.
all40 <- t(sapply(raw[, 6:45], function(x) table(factor(x, levels = 1:5))))
cat(sprintf("\ndistinct count-vectors among all 40 item columns: %d of 40\n",
            nrow(unique(all40))))
okU <- TRUE
for (i in 1:5) {
  hits <- which(apply(all40, 1, function(r)
      identical(as.integer(r), as.integer(live[i, as.character(1:5)])))) + 5L
  cat(sprintf("  item_%02d matches source column(s): %s   (script predicts %d)\n",
              i, paste(hits, collapse = ","), 35L + i))
  okU <- okU && length(hits) == 1L && hits == 35L + i
}

cat("\n(B1) demographic columns read in DISPLAY order vs the paper's own text\n")
pm <- 100 * mean(raw[[2]] == 1)             # 1 = Male (first option)
pa <- 100 * mean(raw[[3]] %in% c(1, 2))     # Under 30 / 31-40
pe <- 100 * mean(raw[[4]] %in% c(3, 4))     # Undergraduates / Master+
cat(sprintf("  male        observed %.1f%%   paper 55.7%%\n", pm))
cat(sprintf("  aged 20-40  observed %.1f%%   paper 88.5%%\n", pa))
cat(sprintf("  bachelor+   observed %.1f%%   paper 90.3%%\n", pe))
okB1 <- abs(pm - 55.7) < 0.5 && abs(pa - 88.5) < 0.5 && abs(pe - 90.3) < 0.5

cat("\n(B2) BI marker items (xlsx Q40-Q44), means under the shipped direction\n")
bi <- colMeans(raw[, 41:45])
for (j in seq_along(bi)) cat(sprintf("  %-60s %.3f\n", substr(names(bi)[j], 1, 60), bi[j]))
okB2 <- which.max(bi) == 2 && all(bi[c(4, 5)] < bi[c(1, 3)])
cat(sprintf("  'I am driving one already' (Q41) least endorsed: %s\n", okB2))

cat("\nNote: (A) pins every item against every other item -- and against every\n",
    "other item column in the whole file. (B) is a direction inference from the\n",
    "export's coding convention and item content; it contradicts the paper's\n",
    "Methods sentence and is disclosed in the notes.\n", sep = "")

cat(if (okA && okU && okB1 && okB2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
