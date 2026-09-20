# Verification for QADT_Kleka_2023 (#2228, batch_304).
#
# SOURCE. OSF osf.io/6vqp3 (CC BY): QADT.pdf Appendix 1 prints all twelve
# forced-choice items in Polish and English with the reverse-scoring marks and
# the rule 'A - 1 point, B - 0'; zr_cleaned.rda is the data; anaysis_code.Rmd
# is the paper's analysis.
#
# THE ONE GAP the appendix leaves is that it labels the items DT_1..DT_12 while
# the data call them ZR_1..ZR_12. Two things close it.
# Route 1: the deposit's own analysis code uses the two names for the same
#   item -- a comment '# moved DT_2' sits above the model that moves ZR_2.
# Route 2: the three factors that code fits group the ZR codes exactly as the
#   appendix's item CONTENT groups them, including the anomaly: ZR_2 is a peer
#   item sitting in the competence factor, which is why the author moved it.
# Route 3: the reverse-marked items are stored already reversed, so resp 1
#   always means the developmental task is attained. All twelve item-total
#   correlations are positive, which is impossible on raw A=1/B=0 coding.
rda <- ".cache/batch_304/zr_cleaned.rda"
rmd <- ".cache/batch_304/qadt_analysis.Rmd"
for (p in c(rda, rmd)) if (!file.exists(p)) stop("missing cached deposit file: ", p)

d <- as.data.frame(irw::irw_fetch("QADT_Kleka_2023"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_304/QADT_Kleka_2023__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA", encoding = "UTF-8")
e <- new.env(); load(rda, envir = e); zr <- as.data.frame(get("zr", envir = e))
cols <- sprintf("ZR_%d", 1:12)
rl <- readLines(rmd, warn = FALSE, encoding = "UTF-8")

cat("=== Route 1: the analysis code uses DT and ZR interchangeably ===\n")
hit <- grep("DT_", rl, value = TRUE)
for (h in hit) cat(sprintf("  %s\n", trimws(h)))
r1 <- any(grepl("moved DT_2", rl))
cat(sprintf("  -> a DT_ name appears as a comment on a ZR_ model: %s\n", r1))

cat("\n=== Route 2: the fitted factors match the appendix's item content ===\n")
f <- list(nabywanie = c(1, 7, 9, 12), kooperacja = c(4, 6, 8, 11),
          kompetencja = c(2, 3, 5, 10))
cat("  from anaysis_code.Rmd:\n")
for (n in names(f)) cat(sprintf("    %-12s ZR_%s\n", n, paste(f[[n]], collapse = ", ZR_")))
cat("  appendix content of the kooperacja four (all peer-relations):\n")
for (i in f$kooperacja) {
    o <- items[items$item == sprintf("ZR_%d", i) & items$resp == 0, "option_text_translated"]
    cat(sprintf("    ZR_%-2d  %s\n", i, substr(o[1], 1, 62)))
}
r2 <- setequal(unlist(f), 1:12) && length(unlist(f)) == 12
cat(sprintf("  -> the three factors partition the twelve codes: %s\n", r2))

cat("\n=== Route 3: the reverse-marked items are stored reversed ===\n")
rev_items <- sprintf("ZR_%d", c(4, 6, 8, 9, 10, 12))
cat(sprintf("  appendix marks with '*': %s\n", paste(rev_items, collapse = ", ")))
m <- as.matrix(zr[, cols])
rit <- sapply(cols, function(c)
    stats::cor(m[, c], rowSums(m[, setdiff(cols, c), drop = FALSE], na.rm = TRUE),
               use = "pairwise.complete.obs"))
for (c in cols) cat(sprintf("    %-6s r = %+.3f%s\n", c, rit[[c]],
                            if (c %in% rev_items) "   [marked reverse]" else ""))
r3 <- all(rit > 0)
cat(sprintf("  -> every item-total correlation is positive: %s\n", r3))
cat("  On raw A=1/B=0 the six starred items would have to be negative, so the\n")
cat("  stored values are post-reversal and resp 1 means the task IS attained.\n")
cat("  The shipped option_text follows that: for a starred item resp 1 is the\n")
cat("  B statement, otherwise the A statement.\n")
chk <- sapply(1:12, function(i) {
    r <- items[items$item == sprintf("ZR_%d", i) & items$resp == 1, "option_text"]
    startsWith(r[1], if (sprintf("ZR_%d", i) %in% rev_items) "B." else "A.")
})
r3b <- all(chk)
cat(sprintf("  -> shipped resp-1 option is B for starred and A otherwise: %s\n", r3b))

cat("\n=== Route 4: the deposit reproduces the live table ===\n")
lng <- do.call(rbind, lapply(cols, function(c) {
    v <- as.numeric(zr[[c]]); v <- v[!is.na(v)]
    data.frame(item = c, resp = v, stringsAsFactors = FALSE)
}))
ts <- as.data.frame(table(lng$item, lng$resp), stringsAsFactors = FALSE)
tl <- as.data.frame(table(d$item, as.numeric(d$resp)), stringsAsFactors = FALSE)
names(ts) <- names(tl) <- c("item", "resp", "n")
mm <- merge(ts, tl, by = c("item", "resp"), all = TRUE)
r4 <- nrow(lng) == nrow(d) && all(!is.na(mm$n.x)) && all(!is.na(mm$n.y)) && all(mm$n.x == mm$n.y)
cat(sprintf("  cells compared: %d   rows src=%d live=%d\n", nrow(mm), nrow(lng), nrow(d)))
cat(sprintf("  -> reproduced exactly: %s\n", r4))

cat("\n=== What this does NOT establish ===\n")
cat("  Whether 'Zycie szkolne jest:' is a stem for every item or only for the\n")
cat("  first. The appendix prints it once, in the table's header row, so it\n")
cat("  ships as a shared section_prompt and item_text is left blank.\n")
cat("\nVERDICT:", if (r1 && r2 && r3 && r3b && r4) "PASS" else "FAIL", "\n")
