# verify_hirwa_2024_antibiotic_attitudes.R
#
# CLAIM UNDER TEST. The IRW item codes item_01..item_09 are assigned
# POSITIONALLY by data/hirwa_2024_antibiotic_attitudes.py
# (`{col: f"item_{i+1:02d}"}` over the columns of S6 Table's header row), so the
# shipped item_text must be the S6 header at that position. The falsifiable
# prediction: the paper's Table 5 publishes Agree/Neutral/Disagree counts for all
# nine attitude items, in the same order, and those counts must reproduce the
# live per-item resp distribution (2=Agree, 1=Neutral, 0=Disagree) cell for cell.
#
# All nine published triples are distinct, so a match distinguishes EVERY item
# from every other item -- swapping any two item_texts breaks it.

suppressMessages(library(irw))

TABLE <- "hirwa_2024_antibiotic_attitudes"

# Hirwa et al. (2024) PLOS ONE 19(4): e0300742, Table 5 "Questions on attitudes
# toward AMR and AMU (N = 441)", rows 1-9 in printed order:
#   columns are Agree, Neutral, Disagree counts.
PUBLISHED <- rbind(
  item_01 = c(agree = 255, neutral = 172, disagree =  14),
  item_02 = c(247,  70, 124),
  item_03 = c(276, 118,  47),
  item_04 = c(323,  44,  74),
  item_05 = c(338,  85,  18),
  item_06 = c(240, 168,  33),
  item_07 = c( 22,  68, 351),
  item_08 = c(236, 105, 100),
  item_09 = c(356,  55,  30))
rownames(PUBLISHED) <- sprintf("item_%02d", 1:9)

d <- irw::irw_fetch(TABLE)
tt <- table(factor(d$item, levels = rownames(PUBLISHED)),
            factor(d$resp, levels = c(2, 1, 0)))   # 2=Agree, 1=Neutral, 0=Disagree

cat(sprintf("%-8s %-24s %-24s\n", "item", "published A/N/D", "live resp2/resp1/resp0"))
ok <- TRUE
for (i in rownames(PUBLISHED)) {
    p <- PUBLISHED[i, ]; o <- as.integer(tt[i, ])
    same <- all(p == o); ok <- ok && same
    cat(sprintf("%-8s %-24s %-24s %s\n", i,
                paste(p, collapse = "/"), paste(o, collapse = "/"),
                if (same) "match" else "MISMATCH"))
}

# All published triples distinct -> the route separates every pair of items.
cat(sprintf("\ndistinct published triples: %d of %d\n",
            nrow(unique(PUBLISHED)), nrow(PUBLISHED)))

cat("Note: this pins item_text to item code for all 9 items and pins the option\n",
    "direction (resp 2 = Agree, 0 = Disagree, uniformly, NOT the paper's\n",
    "correct/neutral/incorrect rubric). It does not establish the 5-point\n",
    "administered anchors, which the deposit collapses to three.\n", sep = "")

cat(if (ok && nrow(unique(PUBLISHED)) == nrow(PUBLISHED))
        "VERDICT: PASS\n" else "VERDICT: FAIL\n")
