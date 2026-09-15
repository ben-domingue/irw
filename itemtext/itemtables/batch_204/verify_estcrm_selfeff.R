# Verification for estcrm_selfeff (#1945, batch_204).
#
# SOURCE. The EstCRM R package (Zopluoglu, v1.6, CRAN, GPL >= 2) ships the
# SelfEff data frame this table was built from, and data/estcrm.R takes the item
# code straight from the column name:
#     for (i in 1:ncol(x)) L[[i]] <- data.frame(id = id, item = names(x)[i], resp = x[, i])
# So there is no mapping step to infer -- the code IS the source column name.
# The item WORDING comes from the package manual, which lists all ten item
# descriptions against Item1..Item10.
#
# WHAT THIS SCRIPT DOES. Because the source data frame is installable, the check
# is a reproduction rather than an argument: every response in the live table is
# matched cell-for-cell against the package data. If a single column had been
# transposed, renamed or reordered on the way in, the per-cell match would fail
# even though the item SET would still look right.
#
# Route 1: item codes == names(SelfEff), exactly.
# Route 2: every live (id, item, resp) triple equals SelfEff[id, item].
if (!requireNamespace("EstCRM", quietly = TRUE))
    stop("install.packages('EstCRM') -- this check reproduces against the package data")
suppressMessages(library(EstCRM))
data(SelfEff, package = "EstCRM")

d <- as.data.frame(irw::irw_fetch("estcrm_selfeff"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)

cat("=== Route 1: item codes are the source column names ===\n")
r1 <- setequal(unique(d$item), names(SelfEff))
cat(sprintf("  names(SelfEff) %d, live %d, identical: %s\n",
            ncol(SelfEff), length(unique(d$item)), r1))
cat("  (a direct rename in the processing script, so this pins every item\n")
cat("   individually -- there is no positional or inferred step to check)\n")

cat("\n=== Route 2: every response reproduced cell-for-cell ===\n")
src <- as.matrix(SelfEff)
id  <- as.integer(as.character(d$id))
got <- mapply(function(r, c) src[r, c], id, match(d$item, colnames(src)))
r2  <- all(!is.na(got)) && all(abs(got - d$resp) < 1e-9)
cat(sprintf("  live rows %d, source cells %d\n", nrow(d), length(src)))
cat(sprintf("  exact matches: %d of %d, max abs difference %g\n",
            sum(abs(got - d$resp) < 1e-9), nrow(d), max(abs(got - d$resp))))

cat("\n=== per-item n and mean, source against live ===\n")
for (i in names(SelfEff))
    cat(sprintf("  %-7s source n=%3d mean %.4f | live n=%3d mean %.4f\n", i,
                sum(!is.na(SelfEff[[i]])), mean(SelfEff[[i]]),
                sum(d$item == i), mean(d$resp[d$item == i])))

cat("\n=== response scale ===\n")
cat(sprintf("  live range %.2f to %.2f; the manual describes an 11 cm line segment\n",
            min(d$resp), max(d$resp)))
cat("  scored as the distance in cm of the check mark from the left end point,\n")
cat("  which is why resp is continuous and bounded near 0 and 11 rather than ordinal.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  The WORDS. Route 2 proves the numbers and the codes line up with the\n")
cat("  package data; the ten item descriptions come from the package manual, and\n")
cat("  no numeric route can check a transcription. The manual lists them against\n")
cat("  Item1..Item10 in order, so the text-to-code assignment is a printed lookup.\n")
cat("\nVERDICT:", if (r1 && r2) "PASS" else "FAIL", "\n")
