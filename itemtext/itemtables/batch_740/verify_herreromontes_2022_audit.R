# Step 5b verification for herreromontes_2022_audit (batch_740).
#
# Claim: item AUDIT_i carries the stem the codebook (PeerJ s002.docx) gives for
# AUDIT_i, and option_text<->resp follows the codebook coding (Never=0 ...).
# Falsifiable prediction: the paper's Table 2 (Herrero-Montes et al. 2022,
# PeerJ 10:e13368) prints, for each numbered stem 1-10, the count of the
# 142 respondents choosing each response option. If item text were permuted,
# or an option direction flipped, the live item x resp counts would not
# reproduce those columns. Published counts are hard-coded below (Total column;
# "-" read as 0). Items 9-10 have options only at resp 0/2/4.

suppressMessages(library(irw))
TABLE <- "herreromontes_2022_audit"

PUB <- rbind(
  AUDIT_1  = c( 14, 45, 61, 22, 0),
  AUDIT_2  = c( 73, 46, 15,  4, 4),
  AUDIT_3  = c( 83, 37, 16,  6, 0),
  AUDIT_4  = c(122, 16,  4,  0, 0),
  AUDIT_5  = c(123, 16,  3,  0, 0),
  AUDIT_6  = c(117, 17,  5,  3, 0),
  AUDIT_7  = c( 90, 45,  6,  1, 0),
  AUDIT_8  = c( 96, 39,  7,  0, 0),
  AUDIT_9  = c(123,  0, 13,  0, 6),
  AUDIT_10 = c(130,  0,  6,  0, 6))
colnames(PUB) <- 0:4

d <- irw::irw_fetch(TABLE)
obs <- unclass(table(factor(d$item, levels = rownames(PUB)),
                     factor(d$resp, levels = 0:4)))

ok <- TRUE
cat(sprintf("%-9s %-26s %-26s %s\n", "item", "published (resp 0..4)", "live (resp 0..4)", "match"))
for (it in rownames(PUB)) {
  m <- all(PUB[it, ] == obs[it, ])
  ok <- ok && m
  cat(sprintf("%-9s %-26s %-26s %s\n", it, paste(PUB[it, ], collapse = "/"),
              paste(obs[it, ], collapse = "/"), m))
}

# Does the route separate every item from every other? Each published count
# vector must be unique, otherwise two items could be swapped undetected.
keys <- apply(PUB, 1, paste, collapse = "/")
distinct <- length(unique(keys)) == nrow(PUB)
cat(sprintf("\ncells compared: %d; distinct published count vectors: %d of %d\n",
            length(PUB), length(unique(keys)), nrow(PUB)))
# Any permutation of item labels other than identity breaks the match:
perm_ok <- sum(sapply(rownames(PUB), function(a)
  sum(sapply(rownames(PUB), function(b) all(PUB[a, ] == obs[b, ])))))
cat(sprintf("live rows matching each published row: %d total (10 = one-to-one)\n", perm_ok))
cat("Not established by this route: the administered Spanish wording itself (not deposited);\n",
    "the shipped English is the study's own codebook rendering.\n", sep = "")

cat(if (ok && distinct && perm_ok == 10) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
