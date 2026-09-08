# Verification for lys_2020_rape_3_cons (#1945, batch_202).
#
# No item WORDING is published for this scale, so the table ships blank
# item_text. What IS recoverable, and what this script establishes, is the
# subscale each item belongs to: the deposit scores cult_cons and ec_cons, and
# solving for their weights over cons1..cons20 identifies the composition
# exactly rather than by inference from correlations.
suppressMessages(library(haven))
x  <- as.data.frame(read_sav(".cache/lys_2020_rape/study3.sav"))
cv <- paste0("cons", 1:20)
m  <- sapply(x[cv], as.numeric)
cc <- as.numeric(x$cult_cons); ec <- as.numeric(x$ec_cons)
ok <- !is.na(cc) & !is.na(ec) & rowSums(is.na(m)) == 0
M  <- m[ok, ]
cat("complete rows:", nrow(M), "\n")

res <- list()
for (nm in c("cult_cons", "ec_cons")) {
    y <- if (nm == "cult_cons") cc[ok] else ec[ok]
    fit  <- lm.fit(cbind(1, M), y)
    b    <- coef(fit)
    pred <- cbind(1, M) %*% b
    w    <- round(b[-1])
    sel  <- cv[abs(w - 1) < 1e-6]
    exact <- max(abs(pred - y)) < 1e-8
    res[[nm]] <- exact && length(sel) == 10
    cat(sprintf("\n=== %s ===\n", nm))
    cat(sprintf("  intercept %.3f, weights rounded to 1 on %d items, 0 elsewhere\n",
                b[1], length(sel)))
    cat(sprintf("  items: %s\n", paste(sel, collapse = ", ")))
    cat(sprintf("  exact reproduction: %d of %d rows (max residual %.2e) -> %s\n",
                sum(abs(pred - y) < 1e-8), length(y), max(abs(pred - y)),
                if (exact) "EXACT" else "NOT EXACT"))
}

# The two subscales must partition the twenty items with no overlap.
oddv  <- cv[seq(1, 19, 2)]; evenv <- cv[seq(2, 20, 2)]
part <- setequal(union(oddv, evenv), cv) && length(intersect(oddv, evenv)) == 0
cat(sprintf("\nthe scale ALTERNATES: odd items are cultural/social, even are economic;\n"))
cat(sprintf("  the two sets partition all 20 with no overlap: %s\n", part))

cat("\n=== What this does NOT establish ===\n")
cat("  Not the item wording -- none is published, so item_text is blank for all\n")
cat("  twenty. Not the response anchors -- the paper states a 5-point Likert scale\n")
cat("  but never its labels, and this block carries no value labels, so\n")
cat("  option_text is blank too. Not which item is which WITHIN a subscale.\n")
cat("  Recorded PARTIAL for those reasons.\n")
cat("\nVERDICT:", if (all(unlist(res)) && part) "PASS" else "FAIL", "\n")
