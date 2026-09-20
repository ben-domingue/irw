# Verification for gilbert_meta_72 (#2228, batch_302).  STATUS: PARTIAL.
#
# SOURCE. Banerjee, Banerji, Berry, Duflo, Kannan, Mukerji et al. (2017), 'From
# proof of concept to scalable policies', deposit Harvard Dataverse
# doi:10.7910/DVN/DUBA3J, CC0 -- the same deposit worked in batch_202 and
# batch_203. This table is the standard 3-5 Hindi written test; batch_203's
# gilbert_meta_70 is the standard 1-2 version of the same instrument family.
#
# ITEM TEXT IS THE TASK DESCRIPTION, NOT A LITERAL QUESTION, and that is
# deliberate for the same reason as its siblings: the deposit ships FOUR
# parallel forms of this test whose content differs, and the live table records
# no form, so no literal item is a property of a code. What IS a property of the
# code is the task, and the deposit's own variable dictionary
# (RawTestVariables_UTK_BH.xlsx) names it for every one.
#
# Route 1: every live code resolves to a dictionary entry.
# Route 2: task families must cluster in difficulty.
set.seed(302)
if (!requireNamespace("jsonlite", quietly = TRUE)) stop("needs jsonlite")
MAP <- ".cache/batch_302/g72_dict.json"
if (!file.exists(MAP)) stop("missing extracted dictionary: ", MAP)
dict <- jsonlite::fromJSON(MAP)
d <- as.data.frame(irw::irw_fetch("gilbert_meta_72"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_302/gilbert_meta_72__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== Route 1: dictionary coverage ===\n")
live <- sort(unique(d$item))
r1 <- setequal(live, names(dict)) && length(live) == 53
cat(sprintf("  live codes %d; dictionary entries %d; identical: %s\n",
            length(live), length(dict), r1))
cat("  48 came from the baseline sheet and 5 (comp01a/b, comp02a/b, word_dic4)\n")
cat("  from the endline sheet, where they carry an e1_ prefix.\n")
tb <- table(unlist(dict))
cat("  task families:\n")
for (k in names(sort(tb, decreasing = TRUE))) cat(sprintf("    %-52s %2d\n", k, tb[[k]]))

cat("\n=== Route 2: do task families cluster in difficulty? ===\n")
p <- sapply(live, function(i) mean(d$resp[d$item == i], na.rm = TRUE))
fam <- unlist(dict)[live]
sizes <- table(fam); multi <- names(sizes)[sizes > 1]
stat <- function(g) {
    v <- c(); for (f in multi) { idx <- which(g == f); if (length(idx) > 1) v <- c(v, var(p[idx])) }
    mean(v)
}
obs <- stat(fam)
null <- replicate(4000, stat(sample(fam)))
pv <- (1 + sum(null <= obs)) / (1 + length(null))
cat(sprintf("  %d families, %d with more than one item\n", length(sizes), length(multi)))
cat(sprintf("  mean within-family variance of p-correct: observed %.5f\n", obs))
cat(sprintf("  same-sized random groupings (4000): mean %.5f, min %.5f\n", mean(null), min(null)))
cat(sprintf("  permutation p = %.4f (lower observed variance = tighter clustering)\n", pv))
r2 <- pv < 0.05
cat(sprintf("  -> %s\n", if (r2) "families cluster far more tightly than chance"
                          else "no clustering detected"))
cat("  Items sharing a dictionary description are the same task, so their pass\n")
cat("  rates should be more alike than an arbitrary grouping would give. If the\n")
cat("  descriptions had been attached to the wrong codes that would disappear.\n")

cat("\n=== per-family difficulty, for a human read ===\n")
for (f in names(sort(sapply(names(sizes), function(f) mean(p[fam == f])))))
    cat(sprintf("  %-52s n=%2d  p %.3f\n", substr(f, 1, 52), sum(fam == f), mean(p[fam == f])))

cat("\n=== What this does NOT establish ===\n")
cat("  Any literal question. The deposit publishes four parallel forms and the\n")
cat("  response table records no form, so a code names a task and a position, not\n")
cat("  a question -- the same limit as gilbert_meta_68/69/70 and the reason the\n")
cat("  upstream form variable is worth carrying (see the data-side issue). Nor\n")
cat("  does it separate items within a family: the three letter-dictation items\n")
cat("  are interchangeable as far as any test here goes.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
