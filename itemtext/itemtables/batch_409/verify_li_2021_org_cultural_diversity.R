# verify_li_2021_org_cultural_diversity.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST (mapping_basis = paper_order): the nine sentences shipped as item_text
# are the S1 Appendix's two unlabelled-code sub-blocks, "Different organizational
# management styles" items 1-4 -> OCD1..OCD4 and "Organizational responsiveness styles"
# items 1-5 -> OCD5..OCD9, in listing order. The appendix never prints the OCD prefix and
# restarts its numbering at the second sub-block, so the 1-9 concatenation is inferred.
#
# ROUTE 1 (published per-item statistics). Li, Wu & Xiong (2021) PLOS ONE 16(5):e0250878
# Table 2 (t002, an IMAGE) reports a one-factor CFA of OCD on the five retained items
# OCD2, OCD4, OCD6, OCD7, OCD9. Refitting it on the live data must reproduce those
# loadings, and a sweep of all 15,120 ordered 5-of-9 assignments must put the identity
# first. This pins the LIVE COLUMNS to the paper's own codes; it says nothing about text.
#
# ROUTE 5/8 (block structure + semantic coherence). A 2-factor EFA (promax) on OCD1-9.
# A correct mapping predicts (a) the tight responsiveness cluster lies wholly inside the
# shipped responsiveness block OCD5-9, and (b) OCD1 and OCD3 -- the two shipped "informal"
# items ("relies on an informal organization", "prefers informal over formal
# communication") -- share a factor. Under a random text permutation the chance a given
# 4-item cluster falls inside a fixed 5-item block is C(5,4)/C(9,4) = 5/126 = 0.040.
#
# WHAT THIS DOES NOT ESTABLISH: the 4|5 sub-block boundary is NOT reproduced -- OCD5
# ("trusts outsiders") loads with the management-style items, and the contiguous 1-4 /
# 5-9 two-factor CFA ranks 6th of 126 splits (factor r = 0.89). Nothing orders items
# within either sub-block. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABLE <- "li_2021_org_cultural_diversity"
PUB_ITEMS <- c("OCD2", "OCD4", "OCD6", "OCD7", "OCD9")
PUB_LOAD  <- c(0.677, 0.707, 0.864, 0.802, 0.765)
PUB_R2    <- c(0.458, 0.500, 0.746, 0.643, 0.585)
TOL <- 0.01
it <- paste0("OCD", 1:9)

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[complete.cases(w[, it]), it]
cat(sprintf("live data: %d respondents x 9 items\n\n", nrow(w)))

fit_load <- function(vars) {
    f <- lavaan::cfa(paste("F =~", paste(vars, collapse = " + ")), data = w, std.lv = TRUE)
    p <- lavaan::parameterEstimates(f, standardized = TRUE)
    p <- p[p$op == "=~", ]
    list(load = setNames(p$std.all, p$rhs), r2 = lavaan::inspect(f, "r2")[vars])
}
fit <- fit_load(PUB_ITEMS)
cat("ROUTE 1 -- one-factor CFA on the five items Table 2 retained\n")
cat(sprintf("%-6s %9s %9s %8s %9s %9s %8s\n", "item", "pub.load", "obs.load", "diff", "pub.R2", "obs.R2", "diff"))
for (i in seq_along(PUB_ITEMS))
    cat(sprintf("%-6s %9.3f %9.4f %8.4f %9.3f %9.4f %8.4f\n", PUB_ITEMS[i], PUB_LOAD[i],
                fit$load[i], fit$load[i] - PUB_LOAD[i], PUB_R2[i], fit$r2[i], fit$r2[i] - PUB_R2[i]))
worst <- max(abs(c(fit$load - PUB_LOAD, fit$r2 - PUB_R2)))
cat(sprintf("largest deviation: %.4f (tolerance %.2f)\n\n", worst, TOL))

perm <- function(v) if (length(v) <= 1) list(v) else
    do.call(c, lapply(seq_along(v), function(i) lapply(perm(v[-i]), function(p) c(v[i], p))))
labs <- character(0); ssd <- numeric(0)
for (cc in combn(9, 5, simplify = FALSE)) {
    f <- fit_load(it[cc])
    for (p in perm(1:5)) {
        lab <- it[cc][p]
        labs <- c(labs, paste(lab, collapse = ","))
        ssd <- c(ssd, sum((unname(f$load[lab]) - PUB_LOAD)^2))
    }
}
o <- order(ssd)
cat(sprintf("ROUTE 1 rival sweep -- %d ordered 5-of-9 assignments, SSD to published loadings\n", length(ssd)))
for (i in 1:5) cat(sprintf("  %-28s SSD = %.6f\n", labs[o[i]], ssd[o[i]]))
best_ok <- labs[o[1]] == paste(PUB_ITEMS, collapse = ",")
cat(sprintf("best assignment is the paper's: %s; runner-up %.0fx worse\n\n",
            best_ok, ssd[o[2]] / max(ssd[o[1]], 1e-12)))

cat("ROUTE 5/8 -- 2-factor EFA (promax), loadings\n")
fa <- factanal(w, 2, rotation = "promax")
L <- unclass(fa$loadings)
print(round(L, 3))
dom <- apply(abs(L), 1, which.max)
fr <- dom[["OCD9"]]                       # the factor the responsiveness cluster defines
cluster <- names(dom)[dom == fr]
other   <- names(dom)[dom != fr]
cat(sprintf("  responsiveness-defined factor: {%s}\n", paste(cluster, collapse = ",")))
cat(sprintf("  other factor:                  {%s}\n", paste(other, collapse = ",")))
inside <- all(cluster %in% paste0("OCD", 5:9))
cat(sprintf("  (a) cluster lies wholly inside shipped responsiveness block OCD5-9: %s (chance 5/126 = 0.040 for a 4-item cluster)\n", inside))
informal <- dom[["OCD1"]] == dom[["OCD3"]]
cat(sprintf("  (b) the two 'informal' items OCD1, OCD3 share a factor: %s (r = %.2f)\n", informal, cor(w$OCD1, w$OCD3)))
cat(sprintf("  NOT reproduced: OCD5 dominant factor = %s (shipped as responsiveness)\n",
            if (dom[["OCD5"]] == fr) "responsiveness" else "management-style"))

cs <- combn(9, 4)
chis <- apply(cs, 2, function(a) {
    b <- setdiff(1:9, a)
    m <- suppressWarnings(lavaan::cfa(paste0("A =~ ", paste(it[a], collapse = "+"),
                           "\nB =~ ", paste(it[b], collapse = "+")), data = w, std.lv = TRUE))
    lavaan::fitMeasures(m, "chisq")
})
rk <- rank(chis)[which(apply(cs, 2, function(a) all(a == 1:4)))]
cat(sprintf("  contiguous 1-4 / 5-9 two-factor CFA ranks %d of %d splits by chi-square (best: {%s} chi2 %.1f vs shipped %.1f)\n\n",
            rk, ncol(cs), paste(it[cs[, which.min(chis)]], collapse = ","), min(chis),
            chis[which(apply(cs, 2, function(a) all(a == 1:4)))]))

cat("SCOPE. Route 1 pins the live columns to the paper's codes. Route 5/8 corroborates the\n")
cat("text-to-code tie coarsely: the tight 4-item cluster sits inside the shipped\n")
cat("responsiveness block and the two 'informal' items co-load. NOT established: the 4|5\n")
cat("sub-block boundary (OCD5 co-loads with management style), or any order within a\n")
cat("sub-block. PARTIAL.\n")
cat(if (worst <= TOL && best_ok && inside && informal) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
