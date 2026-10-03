# verify_phq9_xiong_2025.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: live codes phq1..phq9 carry the canonical PHQ-9 wording in
# the form's printed numbering (phq1 = "Little interest or pleasure in doing
# things" ... phq9 = "Thoughts that you would be better off dead or of hurting
# yourself in some way"), and resp 0/1/2/3 = Not at all / Several days / More
# than half the days / Nearly every day, ascending.
#
# The OSF deposit (osf.io/wg568, four .sav files) has NO variable labels and
# NO value labels on phq1..phq9, and the paper (PAID 246:113343) is closed
# access, so the tie rests on the column names' numbering matching the PHQ-9
# form. data/ders16_xiong_2025.R melts the columns by name (starts_with("phq")),
# so the IRW code IS the source column name -- what is inferred is what the
# NAME means.
#
# Predictions (each breaks under a permutation of the item labels):
#   P0  live table == deposit: per-item x per-level counts of live phq1..9 equal
#       the pooled four .sav files cell for cell (ties this check's deposit-side
#       numbers to the live table; not itself mapping evidence).
#   P1  MARKER (route 7): phq9 (suicidal ideation) has the lowest mean AND the
#       highest share of zeros of the nine.
#   P2  SLEEP TWIN (cross-instrument content twin): the deposit also holds the
#       PCL-5; PCL-5 item 20 is "Trouble falling or staying asleep". phq3 (sleep)
#       and pcl20 must be each other's highest-correlated partner across the
#       9 x 20 PHQ x PCL matrix (mutual argmax). Caveat: pcl20's identity is
#       itself the canonical-numbering assumption for the sibling table; the
#       mutual maximum at a wide margin is what makes it corroborating rather
#       than circular -- two independent orderings would not coincide by chance.
#   P3  BLOCKS (route 5): two-factor split, somatic {3,4,5} vs
#       cognitive/affective {2,6,7,8,9}, item 1 excluded (cross-loads): mean
#       within-block r exceeds mean cross-block r for both blocks.
#   P4  RESP DIRECTION: phq9 >= 80% at 0 (reversed coding would put >=80% of a
#       community/student/prisoner pool at "Nearly every day" suicidal thoughts);
#       deposit PHQ_T == raw row sum, and PHQ_YN == (PHQ_T >= 10), the PHQ-9's
#       standard cut-off, with zero disagreements.
#
# WHAT THIS DOES NOT ESTABLISH: pins phq9 and phq3 individually and block
# membership of {4,5} vs {2,6,7,8}. It does NOT separate phq4 from phq5, does NOT
# separate phq2, phq6, phq7, phq8 from one another, and does not pin phq1.
# Status: PARTIAL.

suppressMessages(library(irw))

TABLE <- "phq9_xiong_2025"
IT  <- paste0("phq", 1:9)
PCL <- paste0("pcl", 1:20)
V   <- "view_only=3b9ee6f978a648deb17d81d244d6c158"
SAV <- c(ado = "https://osf.io/download/cr5e9/",
         col = "https://osf.io/download/pcqjk/",
         com = "https://osf.io/download/jfz9s/",
         pri = "https://osf.io/download/66f3d7e045964aa0dba859b8/")

# --- live -------------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
cat(sprintf("live table: %d rows, %d respondents\n", nrow(d), length(unique(d$id))))
live_tab <- table(factor(d$item, IT), factor(d$resp, 0:3))

# --- deposit ----------------------------------------------------------------
dep <- do.call(rbind, lapply(names(SAV), function(k) {
  tf <- tempfile(fileext = ".sav")
  utils::download.file(paste0(SAV[[k]], "?", V), tf, quiet = TRUE, mode = "wb")
  x <- tryCatch(haven::read_sav(tf), error = function(e) haven::read_sav(tf, encoding = "latin1"))
  x <- as.data.frame(lapply(as.data.frame(x)[, c(IT, PCL, "PHQ_T", "PHQ_YN")], as.numeric))
  x
}))
cat(sprintf("deposit: %d respondents (4 .sav files pooled)\n\n", nrow(dep)))
dep_tab <- t(sapply(IT, function(i) table(factor(dep[[i]], 0:3))))
p0 <- all(as.matrix(unclass(live_tab)) == dep_tab)
cat("P0 per-item level counts, live vs deposit\n")
for (i in IT) cat(sprintf("  %-5s live %s | deposit %s\n", i,
    paste(live_tab[i, ], collapse = "/"), paste(dep_tab[i, ], collapse = "/")))
cat(sprintf("  -> identical: %s\n\n", p0))

# --- P1 ---------------------------------------------------------------------
w <- dep[, IT]
mu <- colMeans(w); z <- colMeans(w == 0) * 100
cat("P1 per-item mean / %zero\n")
for (i in IT) cat(sprintf("  %-5s mean %.3f  %%zero %.1f\n", i, mu[i], z[i]))
p1 <- names(which.min(mu)) == "phq9" && names(which.max(z)) == "phq9"
cat(sprintf("  -> lowest mean %s, highest %%zero %s (predicted phq9)\n\n",
            names(which.min(mu)), names(which.max(z))))

# --- P2 ---------------------------------------------------------------------
R <- cor(dep[, c(IT, PCL)])[IT, PCL]
cat("P2 best PCL-5 partner per PHQ item (r, runner-up)\n")
for (i in IT) { s <- sort(R[i, ], decreasing = TRUE)
  cat(sprintf("  %-5s %-5s %.3f  (next %s %.3f)\n", i, names(s)[1], s[1], names(s)[2], s[2])) }
s20 <- sort(R[, "pcl20"], decreasing = TRUE)
cat(sprintf("  pcl20's best PHQ partner: %s %.3f (next %s %.3f)\n",
            names(s20)[1], s20[1], names(s20)[2], s20[2]))
p2 <- names(which.max(R["phq3", ])) == "pcl20" && names(s20)[1] == "phq3"
cat(sprintf("  -> mutual argmax phq3<->pcl20: %s\n\n", p2))

# --- P3 ---------------------------------------------------------------------
C <- cor(w)
SOM <- c("phq3", "phq4", "phq5"); COG <- c("phq2", "phq6", "phq7", "phq8", "phq9")
wi <- function(g) mean(C[g, g][upper.tri(C[g, g])])
cr <- mean(C[SOM, COG])
cat(sprintf("P3 within somatic %.3f, within cognitive %.3f, across %.3f\n\n", wi(SOM), wi(COG), cr))
p3 <- wi(SOM) > cr && wi(COG) > cr

# --- P4 ---------------------------------------------------------------------
rs <- rowSums(w)
dmax <- max(abs(rs - dep$PHQ_T))
yn <- table(cut10 = rs >= 10, PHQ_YN = dep$PHQ_YN)
print(yn)
p4 <- z["phq9"] >= 80 && dmax == 0 && sum(diag(yn)) == nrow(dep)
cat(sprintf("P4 phq9 %%zero %.1f; max|PHQ_T - rowsum| %.3f; PHQ_YN == (sum>=10): %s\n\n",
            z["phq9"], dmax, sum(diag(yn)) == nrow(dep)))

ok <- c(P0 = p0, P1 = p1, P2 = p2, P3 = p3, P4 = unname(p4))
for (p in names(ok)) cat(sprintf("%s: %s\n", p, if (ok[p]) "PASS" else "FAIL"))
cat("Scope: pins phq9 and phq3, somatic/cognitive block membership and the resp\n",
    "direction; does NOT separate phq4 from phq5, nor phq2/phq6/phq7/phq8, and does\n",
    "not pin phq1 -- PARTIAL.\n", sep = "")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
