# Step 5b verification for gordils_2021_behavioral_avoidance (batch_041).
#
# mapping_basis = paper_order. The IRW item codes AVOID1..AVOID11 ARE the raw
# supplementary spreadsheet's own column names (S1/S4 Data, .s004/.s007 xlsx;
# data/gordils_2021_interracial.py melts them unchanged), so there is no
# positional rename to check. The one inference is that column AVOIDk carries
# the k-th item of the "Perceived Behavioral Avoidance" list in the paper's
# S1 Appendix, which numbers nothing and only presents the 11 items in order.
#
# That inference makes four falsifiable predictions about the live data, from
# the CONTENT of the text we assigned to each position. All four are stated
# before looking, and any of them breaking would mean the order is wrong.
#
#   P1  AVOID4 = "avoid having romantic relationships" has the HIGHEST mean.
#       Interracial romantic involvement is the most-avoided contact domain in
#       the intergroup-contact literature; on a perceived-prevalence scale it
#       must top a list whose other domains are conversation, shopping and work.
#   P2  AVOID6 ("shopping in stores") and AVOID8 ("working with each other")
#       are the TWO LOWEST means -- the two domains that are structurally
#       hardest to avoid, being commercial and workplace settings.
#   P3  The single largest off-diagonal correlation in the 11x11 matrix is
#       r(AVOID10, AVOID11) -- appendix positions 10 and 11 are near-synonymous
#       ("if they had a choice, they would rather not interact" /
#        "if they can avoid interacting, they do").
#   P4  {AVOID9, AVOID10, AVOID11} is the tightest of all 165 item triples.
#       Appendix positions 9-11 are the three general "if ... interact" items,
#       grammatically and semantically distinct from the eight domain-specific
#       ones; a permuted assignment would not put them together.
#
# What this does NOT establish: it does not distinguish every item from every
# other. Within the domain-specific block, positions 1/2/3 (conversations /
# friendships / leisure time) are mutually interchangeable as far as these
# statistics go, as are 5 and 7. Status is therefore PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "gordils_2021_behavioral_avoidance"
ITEMS <- paste0("AVOID", 1:11)

d <- as.data.frame(irw::irw_fetch(TABLE))
d <- d[!is.na(d$resp), ]

mu <- tapply(d$resp, d$item, mean)[ITEMS]
cat("-- per-item means --\n")
for (i in ITEMS) cat(sprintf("%-8s %6.3f\n", i, mu[[i]]))

w <- reshape(d[, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
C <- cor(w[, ITEMS], use = "pairwise.complete.obs")

p1 <- ITEMS[which.max(mu)]
lo <- ITEMS[order(mu)][1:2]
cat(sprintf("\nP1 highest mean : %s (%.3f)   expected AVOID4\n", p1, max(mu)))
cat(sprintf("P2 lowest two   : %s (%.3f), %s (%.3f)   expected AVOID6 & AVOID8\n",
            lo[1], mu[[lo[1]]], lo[2], mu[[lo[2]]]))

M <- C; diag(M) <- -Inf
ij <- which(M == max(M), arr.ind = TRUE)[1, ]
pair <- sort(ITEMS[c(ij[1], ij[2])])
cat(sprintf("P3 max pair r   : %s-%s r=%.3f   expected AVOID10-AVOID11\n",
            pair[1], pair[2], max(M)))

tri <- combn(11, 3)
sc <- apply(tri, 2, function(k) mean(c(C[k[1], k[2]], C[k[1], k[3]], C[k[2], k[3]])))
ord <- order(sc, decreasing = TRUE)
cat("\nP4 tightest triples of all 165 (mean within-triple r):\n")
for (z in ord[1:4])
    cat(sprintf("   {%s}  %.4f\n",
                paste(ITEMS[tri[, z]], collapse = ", "), sc[z]))
best <- sort(ITEMS[tri[, ord[1]]])

ok <- p1 == "AVOID4" &&
      setequal(lo, c("AVOID6", "AVOID8")) &&
      identical(pair, c("AVOID10", "AVOID11")) &&
      identical(best, c("AVOID10", "AVOID11", "AVOID9"))

cat("\nNote: this pins the two structural blocks (domain-specific positions 1-8 vs\n",
    "general 'if ... interact' positions 9-11), the top and bottom of the mean\n",
    "ordering, and the adjacent 10/11 pair. It does NOT separate positions 1/2/3\n",
    "from one another, nor 5 from 7. PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
