# verify_pang_2023_media_influence.R
#
# CLAIM UNDER TEST (two axes):
#
# (A) item_text <-> item.  data/pang_2023_nev_adoption.py assigns item codes
#     POSITIONALLY: item_cols = xlsx columns 6..45, and this table takes
#     item_cols[25:30] (0-based) == spreadsheet columns 31..35, relabelled
#     item_01..item_05.  Those five columns are the S1 file's own headers
#     Q30..Q34, the Mass media (MM) block, and their header text IS the
#     shipped item_text.  The falsifiable prediction: the full 5-level
#     response-frequency vector of xlsx column 30+k must equal the live
#     frequency vector of item_0k, cell for cell.  The five vectors are
#     mutually distinct, so this distinguishes EVERY item from every other
#     -- a swap of any two would break it.
#
# (B) option_text <-> resp.  The paper's Methods say "1 point (strongly
#     disagree) to 5 points (strongly agree)", but S2 File (the questionnaire)
#     prints the options in the order Definitely agree / Agree / Neither /
#     Disagree / Definitely disagree, and the shipped mapping follows that
#     display order (1 = Definitely agree).  Two checks below:
#       B1. The Sojump export codes single-choice options by DISPLAY POSITION:
#           under that reading the S1 demographic columns reproduce the paper's
#           own reported percentages (55.7% male; 88.5% aged 20-40;
#           90.3% bachelor's or above).
#       B2. Marker items in the sibling BI block: the sample are potential,
#           mostly non-owning users, so "I am driving and will continue to
#           drive an NEV" (Q41) must be the LEAST endorsed BI item and the
#           conditional-switch items (Q43/Q44) the most.  Under 1 = agree that
#           means mean(Q41) is the HIGHEST and mean(Q43/Q44) the LOWEST.
#
# What this does NOT establish: (B) is inference from the export's coding
# convention and from content, not from a label in the data file; the paper's
# own sentence states the opposite direction and is judged wrong here.

suppressMessages(library(irw))
suppressMessages(library(readxl))

TABLE <- "pang_2023_media_influence"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0285815.s001")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
stopifnot(ncol(raw) == 45, nrow(raw) == 309)

blk <- raw[, 31:35]                       # xlsx Q30..Q34 == item_01..item_05
cat("source columns used (headers are the shipped item_text):\n")
for (j in seq_along(blk)) cat(sprintf("  item_%02d <- %s\n", j, names(blk)[j]))

d <- irw::irw_fetch(TABLE)
live <- table(d$item, d$resp)
src  <- t(sapply(blk, function(x) table(factor(x, levels = 1:5))))
rownames(src) <- sprintf("item_%02d", 1:5)

cat("\n(A) per-item response-frequency vectors, source vs live (levels 1..5)\n")
cat(sprintf("%-9s %-24s %-24s %s\n", "item", "source (S1 xlsx)", "live (IRW)", "match"))
okA <- TRUE
for (i in rownames(src)) {
  s <- as.integer(src[i, ]); l <- as.integer(live[i, as.character(1:5)])
  m <- identical(s, l); okA <- okA && m
  cat(sprintf("%-9s %-24s %-24s %s\n", i,
              paste(s, collapse = "/"), paste(l, collapse = "/"),
              if (m) "yes" else "NO"))
}
dist <- nrow(unique(src)) == nrow(src)
cat(sprintf("all five source vectors mutually distinct: %s\n", dist))

cat("\n(B1) demographic columns read in DISPLAY order vs the paper's own text\n")
pm <- 100 * mean(raw[[2]] == 1)                       # 1 = Male (first option)
pa <- 100 * mean(raw[[3]] %in% c(1, 2))               # Under 30 / 31-40
pe <- 100 * mean(raw[[4]] %in% c(3, 4))               # Undergraduate / Master+
cat(sprintf("  male           observed %.1f%%   paper 55.7%%\n", pm))
cat(sprintf("  aged 20-40     observed %.1f%%   paper 88.5%%\n", pa))
cat(sprintf("  bachelor+      observed %.1f%%   paper 90.3%%\n", pe))
okB1 <- abs(pm - 55.7) < 0.5 && abs(pa - 88.5) < 0.5 && abs(pe - 90.3) < 0.5

cat("\n(B2) BI marker items (xlsx Q40-Q44), means under the shipped direction\n")
bi <- colMeans(raw[, 41:45])
for (j in seq_along(bi)) cat(sprintf("  %-62s %.3f\n", substr(names(bi)[j], 1, 62), bi[j]))
okB2 <- which.max(bi) == 2 && all(bi[c(4, 5)] < bi[c(1, 3)])
cat(sprintf("  'I am driving one' (Q41) is the least endorsed BI item: %s\n", okB2))
cat("  (under the paper's stated 1=strongly disagree this would mean the sample\n",
    "   endorses currently owning an NEV MORE than intending to drive one.)\n", sep = "")

cat("\nNote: (A) pins every item against every other item; (B) is a direction\n",
    "inference from the export's coding convention and item content, and it\n",
    "contradicts the paper's Methods sentence -- see the public_note.\n", sep = "")

cat(if (okA && dist && okB1 && okB2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
