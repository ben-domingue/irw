# verify_marquessanchez_2023_kidmed.R -- Step 5b, mapping_basis = reconstructed
#
# CLAIM UNDER TEST: each IRW item code (a Spanish food abbreviation) carries the
# KIDMED item this extraction assigned to it. The falsifiable part of that claim
# is STRUCTURAL, and the source .sav supplies it in three author-computed
# composites that were never shipped to IRW:
#
#   ALIFYV -- "fruta y verdura" subscore. If ALIFD/ALI2FD/ALIVD/ALI2VD really are
#             KIDMED items 1-4 (the two fruit and two vegetable items), their sum
#             must equal it row for row.
#   ALIMH  -- "malos habitos" subscore. KIDMED subtracts a point for fast food,
#             breakfast pastries and daily sweets, so this must equal
#             ALIH + ALIBI + ALIGC exactly -- and must NOT contain ALIDES.
#   ALI    -- the 0-12 KIDMED total, which fixes the SIGN of every item.
#
# The ALIDES result is the reason this matters: it enters the total POSITIVELY and
# is absent from ALIMH, so in this table resp = 1 means the respondent does NOT
# skip breakfast. The shipped option_text for ALIDES is flipped accordingly.
#
# WHAT THIS DOES NOT ESTABLISH: it pins two blocks, every sign, and (via the
# nesting asymmetry below) which fruit/vegetable item is the "second/more than
# once" one. It does NOT separate ALIP, ALIL, ALIPA, ALIC, ALIFS, ALILAC and
# ALIY from one another -- those rest on the Spanish abbreviation in the item
# code (pescado, legumbres, pasta, cereales, frutos secos, lacteo, yogur), not on
# any number here. Hence status = PARTIAL, not VERIFIED.

suppressMessages({library(irw); library(haven)})

TABLE <- "marquessanchez_2023_kidmed"
SRC <- paste0("https://journals.plos.org/plosone/article/file?",
              "id=10.1371/journal.pone.0289553.s001&type=supplementary")

tf <- tempfile(fileext = ".sav")
download.file(SRC, tf, quiet = TRUE, mode = "wb")
sav <- as.data.frame(haven::read_sav(tf))

POS4 <- c("ALIFD", "ALI2FD", "ALIVD", "ALI2VD")
NEG  <- c("ALIH", "ALIBI", "ALIGC")
ALL  <- c(POS4, "ALIP", "ALIH", "ALIL", "ALIPA", "ALIC", "ALIFS",
          "ALIAO", "ALIDES", "ALILAC", "ALIBI", "ALIY", "ALIGC")

ok <- logical(0)

## 0. bridge: the live table's per-item proportions are the .sav columns
d <- irw::irw_fetch(TABLE)
live <- tapply(d$resp, d$item, mean)[ALL]
savp <- sapply(ALL, function(c) mean(sav[[c]], na.rm = TRUE))
cat(sprintf("%-8s %8s %8s\n", "item", "live", ".sav"))
for (i in ALL) cat(sprintf("%-8s %8.4f %8.4f\n", i, live[[i]], savp[[i]]))
cat(sprintf("max |live - .sav| = %.6g\n\n", max(abs(live - savp))))
ok <- c(ok, max(abs(live - savp)) < 1e-9)

cc <- complete.cases(sav[, c(ALL, "ALI", "ALIFYV", "ALIMH")])
s <- sav[cc, ]
cat("complete cases used:", nrow(s), "\n\n")

## 1. fruit/vegetable block
m1 <- sum(rowSums(s[, POS4]) == s$ALIFYV)
cat(sprintf("ALIFYV == ALIFD+ALI2FD+ALIVD+ALI2VD : %d/%d rows\n", m1, nrow(s)))
ok <- c(ok, m1 == nrow(s))

## 2. negative block, and ALIDES excluded from it
m2 <- sum(rowSums(s[, NEG]) == s$ALIMH)
m2d <- sum(rowSums(s[, c(NEG, "ALIDES")]) == s$ALIMH)
cat(sprintf("ALIMH  == ALIH+ALIBI+ALIGC          : %d/%d rows\n", m2, nrow(s)))
cat(sprintf("  same with ALIDES added in         : %d/%d rows (must be far lower)\n",
            m2d, nrow(s)))
ok <- c(ok, m2 == nrow(s), m2d < m2)

## 3. signed total: +1 for the 11 positives scored, -1 for the three negatives
posn <- setdiff(ALL, c(NEG, "ALIAO"))
tot <- rowSums(s[, posn]) - rowSums(s[, NEG])
m3 <- sum(tot == s$ALI)
alt <- rowSums(s[, setdiff(posn, "ALIDES")]) - rowSums(s[, c(NEG, "ALIDES")])
cat(sprintf("\nALI == sum(11 positives, excl. ALIAO) - sum(3 negatives): %d/%d rows\n",
            m3, nrow(s)))
cat(sprintf("  with ALIDES treated as a NEGATIVE item                 : %d/%d rows\n",
            sum(alt == s$ALI), nrow(s)))
ok <- c(ok, m3 / nrow(s) > 0.95, sum(alt == s$ALI) < m3)

## 4. nesting asymmetry separates item 1 from 2, and item 3 from 4
a <- sum(s$ALIFD == 1 & s$ALI2FD == 0); b <- sum(s$ALI2FD == 1 & s$ALIFD == 0)
cc2 <- sum(s$ALIVD == 1 & s$ALI2VD == 0); dd <- sum(s$ALI2VD == 1 & s$ALIVD == 0)
cat(sprintf("\nfruit  : FD=1,2FD=0 %3d vs 2FD=1,FD=0 %3d\n", a, b))
cat(sprintf("veg    : VD=1,2VD=0 %3d vs 2VD=1,VD=0 %3d\n", cc2, dd))
cat("  (a 'second piece'/'more than once' item must be the RARER one)\n")
ok <- c(ok, a > 3 * b, cc2 > 3 * dd)

## 5. semantic ceiling: olive oil at home, in Spain
cat(sprintf("\nALIAO endorsement (Uses olive oil at home): %.3f -- highest of all %s\n",
            savp[["ALIAO"]], ifelse(savp[["ALIAO"]] == max(savp), "16 items", "??")))
ok <- c(ok, savp[["ALIAO"]] == max(savp))

cat(sprintf("\nchecks passed: %d/%d\n", sum(ok), length(ok)))
cat("Note: this pins the fruit/vegetable block, the negative block, every item's\n",
    "sign and the first-vs-second fruit/vegetable pairs. It does NOT separate the\n",
    "remaining positive items from one another; that rests on the item codes.\n", sep = "")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
