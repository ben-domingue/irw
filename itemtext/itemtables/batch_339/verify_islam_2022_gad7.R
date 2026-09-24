# verify_islam_2022_gad7.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: live item codes GAD1..GAD7 carry the canonical GAD-7 item
# wording in the official form's numbering (GAD4 = "Trouble relaxing",
# GAD5 = "Being so restless that it is hard to sit still", ...).
# The study's S1 .xlsx (PLOS 10.1371/journal.pone.0279062.s001) has bare
# headers GAD1..GAD7 and no labels; data/islam_2022_online_addiction.py melts
# them by name (code IS the column name, no positional step). What is inferred
# is what the column NAME means.
#
# Complication: the paper's Methods lists the items as "1) nervousness,
# 2) inability to stop worrying, 3) excessive worry, 4) restlessness,
# 5) difficulty in relaxing, 6) easy irritation, 7) fear of something awful
# happening" -- canonical items 4 and 5 swapped. That sentence is a widely
# copied boilerplate (Europe PMC: 16 unrelated papers carry the same
# "inability to stop worrying, excessive worry, restlessness" sequence), so it
# is not evidence of a non-standard administration. This script tests the only
# mapping-sensitive prediction the deposit offers for that pair:
#
#   P1  corr(GAD5, PHQ8) > corr(GAD4, PHQ8)
#       PHQ-9 item 8 is its only psychomotor item ("...so fidgety or restless
#       that you have been moving around a lot more than usual"), the content
#       twin of canonical GAD-7 item 5 (restlessness). Under the paper's
#       swapped numbering the inequality would be expected to reverse.
#
# Plumbing check (not evidence): live cells equal the deposit's cells, so the
# PHQ half from the deposit is correctly aligned with the live GAD half.
#
# WHAT THIS DOES NOT ESTABLISH: P1's margin is small (bootstrap printed below;
# the interval includes 0), so even the 4/5 order is only weakly supported.
# Nothing here separates GAD1/2/3/6/7 from one another. Status: NO_ROUTE for
# item identity; the mapping rests on the official form's numbering.

suppressMessages(library(irw))
TABLE <- "islam_2022_gad7"
XLSX  <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0279062.s001")

d <- as.data.frame(irw::irw_fetch(TABLE))
gad <- paste0("GAD", 1:7); phq <- paste0("PHQ", 1:9)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

tf <- tempfile(fileext = ".xlsx")
utils::download.file(XLSX, tf, quiet = TRUE, mode = "wb")
x <- as.data.frame(readxl::read_excel(tf))
x$id <- seq_len(nrow(x))            # the processing script's row-index id
m <- merge(w[, c("id", gad)], x[, c("id", phq, paste0(gad))], by = "id",
           suffixes = c("", ".src"))
same <- sum(sapply(gad, function(g) sum(m[[g]] == m[[paste0(g, ".src")]])))
cat(sprintf("plumbing: merged n = %d; live==deposit GAD cells %d / %d\n\n",
            nrow(m), same, 7 * nrow(m)))

r <- function(a, b, dd = m) cor(dd[[a]], dd[[b]])
c8 <- sapply(gad, r, b = "PHQ8")
cat("corr(GAD_i, PHQ8)  [PHQ-9's only psychomotor restlessness item]\n")
for (g in gad) cat(sprintf("  %-5s %6.3f\n", g, c8[g]))
p1 <- unname(c8["GAD5"] > c8["GAD4"])
cat(sprintf("  P1: GAD5 %.3f vs GAD4 %.3f (diff %+.3f) -> %s\n",
            c8["GAD5"], c8["GAD4"], c8["GAD5"] - c8["GAD4"],
            if (p1) "canonical order favoured" else "paper's swapped order favoured"))

set.seed(1)
bd <- replicate(2000, { s <- m[sample(nrow(m), replace = TRUE), ]
                        r("GAD5", "PHQ8", s) - r("GAD4", "PHQ8", s) })
q <- quantile(bd, c(.025, .975))
cat(sprintf("  bootstrap diff 95%% CI [%+.3f, %+.3f]; share > 0 = %.2f\n",
            q[1], q[2], mean(bd > 0)))
cat("  -> weak: the interval includes 0, so this does not PIN items 4/5.\n\n")

mu <- sapply(gad, function(g) mean(m[[g]]))
cat("item means (descriptive only):",
    paste(sprintf("%s %.2f", gad, mu), collapse = "; "), "\n\n")

cat("Scope: no route distinguishes GAD1/2/3/6/7; items 4/5 only weakly -> NO_ROUTE.\n")
ok <- p1 && same == 7 * nrow(m)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
