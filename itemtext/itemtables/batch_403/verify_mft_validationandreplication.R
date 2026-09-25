# verify_mft_validationandreplication.R -- Step 5b check for batch_403.
#
# Claim: MFQ_<Foundation><k> is the k-th item of that foundation in the MFQ-2's
# presentation order (Atari et al. preprint R2 appendix, osf.io/download/br4zf:
# Care = 1,7,13,19,25,31; Equality = 2,8,...; Proportionality = 3,9,...;
# Loyalty = 4,10,...; Authority = 5,11,...; Purity = 6,12,...), so e.g.
# MFQ_Pur2 = item 12 "chastity" and MFQ_Pur6 = item 36 "virginity".
#
# Route: semantic coherence of the inter-item correlation structure (route 8)
# plus subscale-block structure (route 5). Each prediction below follows from the
# item WORDING under the claimed mapping and would break under most within-
# foundation permutations. The Loyal country/community split is also the one the
# authors' own dataAnalysis_US (study 2).r hard-codes
# (loyalCountryItems = Loyal1,2,4; loyalCommunityItems = Loyal3,5,6).
#
# NOT established: order within a semantic cluster -- Equal1/2/4 (three
# "same money/income" items), Loyal1/2/4, Loyal3/5/6, Care3..6, Auth4 vs Auth6,
# Prop2 vs Prop3, Pur1/3/4 are not separated from each other by this route.

suppressMessages(library(irw))
TABLE <- "mft_validationandreplication"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
R <- cor(w[, setdiff(names(w), "id")], use = "pairwise.complete.obs")
r <- function(a, b) R[paste0("MFQ_", a), paste0("MFQ_", b)]
blk <- function(A, B) { v <- c(); for (a in A) for (b in B) if (a != b) v <- c(v, r(a, b)); v }
toppair <- function(f, idx = 1:6) {
  v <- paste0(f, idx); best <- -1; bp <- NA
  for (i in seq_along(v)) for (j in seq_along(v)) if (i < j && r(v[i], v[j]) > best) { best <- r(v[i], v[j]); bp <- paste(v[i], v[j]) }
  list(pair = bp, r = best)
}
avg_r <- function(f) sapply(1:6, function(k) mean(sapply(setdiff(1:6, k), function(j) r(paste0(f, k), paste0(f, j)))))

ok <- c()
chk <- function(label, cond, detail) { cat(sprintf("[%s] %s -- %s\n", if (cond) "ok" else "XX", label, detail)); ok <<- c(ok, cond) }

# 1. Loyalty: country items (4,10,22 -> Loyal1,2,4) vs community items (16,28,34 -> Loyal3,5,6)
wi <- blk(c("Loyal1", "Loyal2", "Loyal4"), c("Loyal1", "Loyal2", "Loyal4"))
cx <- blk(c("Loyal1", "Loyal2", "Loyal4"), c("Loyal3", "Loyal5", "Loyal6"))
chk("Loyal country block {1,2,4}", min(wi) > max(cx), sprintf("min within r=%.2f > max country-community r=%.2f", min(wi), max(cx)))

# 2. Equality: three 'same amount of money / same income' items (2,8,20 -> Equal1,2,4)
wi <- blk(c("Equal1", "Equal2", "Equal4"), c("Equal1", "Equal2", "Equal4"))
cx <- blk(c("Equal1", "Equal2", "Equal4"), c("Equal3", "Equal5", "Equal6"))
chk("Equal money/income block {1,2,4}", min(wi) > max(cx), sprintf("min within r=%.2f > max to {3,5,6} r=%.2f", min(wi), max(cx)))
a <- avg_r("Equal")
chk("Equal5 ('share rewards equally even if some worked harder') weakest", which.min(a) == 5, paste(sprintf("%.2f", a), collapse = " "))

# 3. Purity: chastity (12 -> Pur2) & virginity (36 -> Pur6) top pair; natural medicines (30 -> Pur5) weakest
tp <- toppair("Pur"); chk("Pur top pair = Pur2 Pur6", tp$pair == "Pur2 Pur6", sprintf("%s r=%.2f", tp$pair, tp$r))
a <- avg_r("Pur"); chk("Pur5 (natural medicines) weakest", which.min(a) == 5, paste(sprintf("%.2f", a), collapse = " "))

# 4. Proportionality: hard-working->more money (3 -> Prop1) & work hard->higher standard (27 -> Prop5) top pair;
#    cheaters punished (33 -> Prop6) weakest
tp <- toppair("Prop"); chk("Prop top pair = Prop1 Prop5", tp$pair == "Prop1 Prop5", sprintf("%s r=%.2f", tp$pair, tp$r))
a <- avg_r("Prop"); chk("Prop6 (cheaters punished) weakest", which.min(a) == 6, paste(sprintf("%.2f", a), collapse = " "))

# 5. Authority: two tradition items (5,11 -> Auth1,2) top pair; two child-rearing items (17,29 -> Auth3,5) top of the rest
tp <- toppair("Auth"); chk("Auth top pair = Auth1 Auth2", tp$pair == "Auth1 Auth2", sprintf("%s r=%.2f", tp$pair, tp$r))
tp <- toppair("Auth", 3:6); chk("Auth top pair among 3-6 = Auth3 Auth5", tp$pair == "Auth3 Auth5", sprintf("%s r=%.2f", tp$pair, tp$r))

# 6. Care: the two 'virtue' items (1,7 -> Care1,2) top pair
tp <- toppair("Care"); chk("Care top pair = Care1 Care2", tp$pair == "Care1 Care2", sprintf("%s r=%.2f", tp$pair, tp$r))

cat(sprintf("\n%d/%d predictions hold.\n", sum(ok), length(ok)))
cat("Does NOT separate items within a semantic cluster (see header); status PARTIAL.\n")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
