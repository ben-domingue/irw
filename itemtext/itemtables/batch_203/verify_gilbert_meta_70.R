# Verification for gilbert_meta_70 (#1945, batch_203).
#
# The deposit's variable dictionary (RawTestVariables_UTK_BH.xlsx, CC0 Dataverse
# doi:10.7910/DVN/DUBA3J) names every langwrit_std12_* variable with the task it asks,
# and does so once per WAVE via a prefix: b_ baseline, e1_ midline, e2_ endline.
# Live item codes are those names with the prefix stripped, and the live `wave`
# column (0 / 0.5 / 1) carries what the prefix encoded. The renaming happened
# upstream of this repo (data/gilbert_hte/postprocessing.R points at an external
# analysis directory), so it is tested against the data rather than read off a
# script.
#
# THE TEST: for every code, the set of waves it actually appears in must equal
# the set its dictionary prefixes imply. That covers all codes, not just the
# wave-restricted ones -- a code defined b|e2 must be absent from the midline.
MAP <- c(b = 0, e1 = 0.5, e2 = 1)
D <- read.csv(".cache/gilbert_meta_73/std12_dict.csv", stringsAsFactors = FALSE)
D <- D[startsWith(D$stem, "langwrit_std12"), ]
d <- as.data.frame(readRDS(file.path(Sys.getenv("CLAUDE_JOB_DIR"), "tmp", "b203_gilbert_meta_70.rds")))
d$item <- as.character(d$item)

same <- setequal(D$stem, unique(d$item))
cat("=== dictionary vs live item sets ===\n")
cat(sprintf("  dictionary %d, live %d, identical: %s\n", nrow(D), length(unique(d$item)), same))

cat("\n=== every code's observed waves vs the waves its prefixes imply ===\n")
bad <- character(0); restricted <- 0
for (i in seq_len(nrow(D))) {
    code <- D$stem[i]
    want <- sort(unname(MAP[strsplit(D$prefixes[i], "|", fixed = TRUE)[[1]]]))
    got  <- sort(unique(d$wave[d$item == code]))
    ok   <- isTRUE(all.equal(as.numeric(want), as.numeric(got)))
    if (length(want) < 3) restricted <- restricted + 1
    if (!ok) bad <- c(bad, code)
    if (length(want) < 3 || !ok)
        cat(sprintf("  %-32s implied %-12s observed %-12s %s\n", code,
                    paste(want, collapse=","), paste(got, collapse=","),
                    if (ok) "ok" else "VIOLATION"))
}
cat(sprintf("  %d of %d codes are wave-restricted and therefore discriminating\n",
            restricted, nrow(D)))
cat(sprintf("  violations: %d%s\n", length(bad),
            if (length(bad)) paste0(" -- ", paste(bad, collapse=", ")) else ""))

cat("\n=== What this does NOT establish ===\n")
cat("  Codes sharing the same wave profile are not separated from each other,\n")
cat("  nor are members of a task family -- several items share one task\n")
cat("  description. Their assignment rests on the dictionary naming each\n")
cat("  variable, which it does. item_text is a TASK DESCRIPTION rather than a\n")
cat("  literal item, because the deposit ships four parallel forms and the live\n")
cat("  table records no form. PARTIAL for those reasons.\n")
cat("\nVERDICT:", if (!length(bad) && same) "PASS" else "FAIL", "\n")
