# Verification for gilbert_meta_71 mathwrit_std12 mathematics (#1945, batch_203).
#
# The deposit's variable dictionary (RawTestVariables_UTK_BH.xlsx, CC0
# Dataverse doi:10.7910/DVN/DUBA3J) names every _* variable with the task
# it asks, prefixed by wave: b_ baseline, e1_/e2_ endline. The live item codes
# are those names with the prefix stripped and the live `wave` column carries
# what the prefix encoded. The renaming happened upstream of this repo
# (data/gilbert_hte/postprocessing.R points at an external analysis directory),
# so it is tested against the data rather than read off a script.
#
# The prediction the data can refute: a code the dictionary defines ONLY with a
# b_ prefix must appear only at the baseline wave, and one defined only with
# e1_/e2_ must never appear there.
D <- read.csv(".cache/gilbert_meta_73/std12_dict.csv", stringsAsFactors = FALSE)
D <- D[startsWith(D$stem, ""), ]
d <- as.data.frame(readRDS(file.path(Sys.getenv("CLAUDE_JOB_DIR"), "tmp",
                                     "b203_gilbert_meta_71 mathwrit_std12 mathematics.rds")))
d$item <- as.character(d$item)

cat("=== dictionary vs live item sets ===\n")
cat(sprintf("  dictionary %d, live %d, identical: %s\n", nrow(D),
            length(unique(d$item)), setequal(D$stem, unique(d$item))))

waves <- sort(unique(d$wave))
base_w <- min(waves)
cat(sprintf("  waves present: %s (baseline taken as %s)\n",
            paste(waves, collapse = ", "), base_w))

base_only <- D$stem[D$prefixes == "b"]
end_only  <- D$stem[!grepl("b", D$prefixes)]
wof <- function(c) sort(unique(d$wave[d$item == c]))

ok1 <- ok2 <- TRUE
cat("\n=== baseline-only codes must appear at the baseline wave ONLY ===\n")
if (!length(base_only)) cat("  (none in this block)\n")
for (c in base_only) {
    w <- wof(c); good <- identical(as.numeric(w), as.numeric(base_w)); ok1 <- ok1 && good
    cat(sprintf("  %-34s waves %-12s %s\n", c, paste(w, collapse=","), if (good) "ok" else "VIOLATION"))
}
cat("\n=== endline-only codes must NEVER appear at baseline ===\n")
if (!length(end_only)) cat("  (none in this block)\n")
for (c in end_only) {
    w <- wof(c); good <- !(base_w %in% w) && length(w) > 0; ok2 <- ok2 && good
    cat(sprintf("  %-34s waves %-12s %s\n", c, paste(w, collapse=","), if (good) "ok" else "VIOLATION"))
}

cat("\n=== What this does NOT establish ===\n")
cat("  Codes available in all waves are not separated from each other, nor are\n")
cat("  members of a task family -- several items share one task description.\n")
cat("  Their assignment rests on the dictionary naming each variable, which it\n")
cat("  does. item_text is a TASK DESCRIPTION rather than a literal item, because\n")
cat("  the deposit ships four parallel forms and the live table records no form.\n")
cat("  Recorded PARTIAL for those reasons.\n")
cat("\nVERDICT:", if (ok1 && ok2 && setequal(D$stem, unique(d$item))) "PASS" else "FAIL", "\n")
