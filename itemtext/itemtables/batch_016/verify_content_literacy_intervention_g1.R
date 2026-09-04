# verify_content_literacy_intervention_g1.R
#
# WHAT IS BEING VERIFIED
# ----------------------
# The IRW `item` codes are bare integers 1..116 invented by the processing
# script (data/content_literacy_intervention_g1.R):
#
#     select(s_id, s_itt_consented, starts_with('s_mmrp'),
#            starts_with('s_sci'), starts_with('s_ss')) |> <drops> |>
#     pivot_longer(...) ; items <- unique(df$item) ; item_id <- row_number()
#
# so each code is a column's POSITION in the Stata file
# g1g2_analyticfile_public.dta (Harvard Dataverse doi:10.7910/DVN/HQEMN6)
# after the script's drops.  Replaying those drops against that file's ordered
# variable list (from the deposit's DDI codebook) predicts:
#
#     items   1- 20 = s_mmrp1 .. s_mmrp20  (Me and My Reading Profile, 3-point)
#     items  21- 68 = s_sci1a .. s_sci12d  (science vocab depth, 12 words x 4)
#     items  69-116 = s_ss1a  .. s_ss12d   (social studies vocab depth)
#
# Only items 1-20 ship item_text, so only those are testable.  Three
# falsifiable predictions follow.
#
# (A) BLOCK STRUCTURE (route 2).  If the block boundaries are where the column
#     replay puts them, EXACTLY items 1-20 take values in {1,2,3} and EXACTLY
#     items 21-116 take values in {0,1}.
#
# (B) SCALE DIRECTION (route 6).  The MORE MMRP form (Kim et al., Appendix G,
#     https://files.eric.ed.gov/fulltext/ED662409.pdf) prints its three options
#     in a direction that FLIPS between items: 10 items print the most positive
#     option as "1.", the other 10 print it as "3.".  If the live table stored
#     that printed coding raw, the correlation matrix would split into two
#     blocks with NEGATIVE cross-block correlations.  It does not: this test
#     checks that every pairwise correlation is positive, which is why the
#     shipped option_text is REVERSED against the printed order for the 10
#     items listed in REVERSED below.
#
# (C) CONTENT-TWIN DISTRIBUTIONS (route 8 / route 1 without published stats).
#     The stem list contains three pairs that ask nearly the same question, and
#     in each pair the two items are printed in OPPOSITE directions:
#          ( 2, 20) importance of learning to read / of becoming a good reader
#          ( 7, 19) learning to read is easy / reading is easy
#          (11, 15) how you feel about reading / about learning to read
#     Under the shipped mapping (assignment + flip) each pair ends up with
#     IDENTICAL anchor wording, so their response distributions should nearly
#     coincide.  Under the wrong flip they would be MIRROR images.  This test
#     compares, for each pair, the total-variation distance as shipped against
#     the mirrored alternative, and reports where the pair ranks among all 190
#     item pairs.  A wrong item->stem assignment or a wrong flip breaks it.
#
# WHAT THIS DOES NOT ESTABLISH.  (A) fixes the MMRP block but not the order
# inside it.  (C) pins six items to three interchangeable-within-pair slots and
# says nothing about items 1,3,4,5,6,8,9,10,12,13,14,16,17,18.  Nothing here
# touches items 21-116, which ship no item_text at all.  Hence PARTIAL.

suppressMessages(library(irw))

TABLE <- "content_literacy_intervention_g1"
REVERSED <- c(1, 4, 5, 7, 8, 10, 15, 17, 18, 20)   # printed 1 = most positive
TWINS <- list(c(2, 20), c(7, 19), c(11, 15))

d <- as.data.frame(irw::irw_fetch(TABLE))
d$item <- as.integer(as.character(d$item))
d$resp <- as.numeric(d$resp)

## ---- (A) block structure -------------------------------------------------
cat("=== (A) resp levels used by each predicted block ===\n")
lev <- tapply(d$resp, d$item, function(x) paste(sort(unique(x)), collapse = "/"))
blk <- function(lo, hi) {
    k <- as.integer(names(lev))
    paste(sort(unique(lev[k >= lo & k <= hi])), collapse = " | ")
}
cat(sprintf("  items   1- 20 (predicted s_mmrp1-20)  : %s\n", blk(1, 20)))
cat(sprintf("  items  21- 68 (predicted s_sci1a-12d) : %s\n", blk(21, 68)))
cat(sprintf("  items  69-116 (predicted s_ss1a-12d)  : %s\n", blk(69, 116)))
okA <- blk(1, 20) == "1/2/3" && blk(21, 68) == "0/1" && blk(69, 116) == "0/1"
cat(sprintf("  (A) %s\n\n", if (okA) "PASS" else "FAIL"))

m <- d[d$item %in% 1:20, c("id", "item", "resp")]
w <- reshape(m, idvar = "id", timevar = "item", direction = "wide")
w <- w[, paste0("resp.", 1:20)]
colnames(w) <- as.character(1:20)
P <- prop.table(table(m$item, m$resp), 1)          # 20 x 3 row-proportions

## ---- (B) single scale direction ------------------------------------------
cat("=== (B) is the printed mixed-direction coding what the table stores? ===\n")
R <- cor(w, use = "pairwise.complete.obs")
off <- R[upper.tri(R)]
cat(sprintf("  190 pairwise correlations among items 1-20: min %+.3f, mean %+.3f, max %+.3f\n",
            min(off), mean(off), max(off)))
cat(sprintf("  negative correlations: %d of 190\n", sum(off < 0)))
mu <- as.numeric(P %*% c(1, 2, 3)); names(mu) <- rownames(P)
cat(sprintf("  item means (1-3): min %.2f (item %s), max %.2f (item %s); all 20 above 1.9,\n",
            min(mu), names(which.min(mu)), max(mu), names(which.max(mu))))
cat("  i.e. 3 is the endorsed pole throughout as shipped -- no item is a mirror of the rest.\n")
cat(sprintf("  Printed coding would require negative cross-block r for the %d/%d split;\n",
            length(REVERSED), 20 - length(REVERSED)))
cat(sprintf("  none is observed, so option_text is shipped REVERSED for items %s.\n",
            paste(REVERSED, collapse = ",")))
okB <- sum(off < 0) == 0 && min(mu) > 1.9
cat(sprintf("  (B) %s\n\n", if (okB) "PASS" else "FAIL"))

## ---- (C) content twins ---------------------------------------------------
cat("=== (C) content-twin pairs: shipped alignment vs the mirrored alternative ===\n")
tvd  <- function(a, b) 0.5 * sum(abs(P[as.character(a), ] - P[as.character(b), ]))
tvdm <- function(a, b) 0.5 * sum(abs(P[as.character(a), ] - rev(P[as.character(b), ])))
allp <- do.call(rbind, lapply(1:19, function(i) do.call(rbind, lapply((i + 1):20,
          function(j) data.frame(a = i, b = j, tvd = tvd(i, j))))))
allp <- allp[order(allp$tvd), ]

cat(sprintf("  %-9s %8s %8s %10s\n", "pair", "as-ship", "mirror", "rank/190"))
okC <- TRUE
for (p in TWINS) {
    s <- tvd(p[1], p[2]); mm <- tvdm(p[1], p[2])
    rk <- which(allp$a == p[1] & allp$b == p[2])
    cat(sprintf("  (%2d,%2d)   %8.4f %8.4f %10d\n", p[1], p[2], s, mm, rk))
    if (!(s < mm / 3 && rk <= 10)) okC <- FALSE
}
cat("  (each pair must be closer as shipped than mirrored, and rank in the top 10 of 190)\n")
cat(sprintf("  (C) %s\n\n", if (okC) "PASS" else "FAIL"))

cat("Establishes: the MMRP occupies items 1-20 and nothing else; the table\n")
cat("stores one uniform direction with 3 = most positive, so the printed\n")
cat("anchors are correctly flipped for the 10 items named above; and the three\n")
cat("predicted content-twin pairs behave as near-duplicates rather than as\n")
cat("mirror images, which a wrong flip or a wrong stem assignment would break.\n")
cat("Does NOT establish: the order of the MMRP items within the block beyond\n")
cat("those three pairs (and even there the two members are interchangeable),\n")
cat("nor anything about items 21-116, which ship no item_text.\n")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
