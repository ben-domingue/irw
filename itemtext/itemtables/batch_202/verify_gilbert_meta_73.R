# Verification for gilbert_meta_73 (#1945, batch_202).
#
# The deposit's variable dictionary (RawTestVariables_UTK_BH.xlsx) names all 36
# mathwrit_std35_* variables, each prefixed by wave: b_ for baseline, e1_/e2_ for
# the two endlines. The live item codes are those names with the prefix stripped,
# and the live `wave` column (0, 0.5, 1) carries what the prefix encoded.
#
# That yields a prediction the response data can refute: a code the dictionary
# defines ONLY with a b_ prefix must appear only at wave 0, and a code defined
# only with e1_/e2_ must never appear at wave 0. Six codes are baseline-only and
# five are endline-only, so 11 of the 36 are testable this way.
D <- read.csv(".cache/gilbert_meta_73/std35_dict.csv", stringsAsFactors = FALSE)
d <- as.data.frame(readRDS(file.path(Sys.getenv("CLAUDE_JOB_DIR"), "tmp",
                                     "b202_gilbert_meta_73.rds")))
d$item <- as.character(d$item)

cat("=== dictionary vs live item sets ===\n")
cat(sprintf("  dictionary codes: %d   live codes: %d   identical sets: %s\n",
            nrow(D), length(unique(d$item)), setequal(D$code, unique(d$item))))

base_only <- D$code[D$prefixes == "b"]
end_only  <- D$code[D$prefixes == "e1|e2"]
allw      <- D$code[grepl("^b\\|", D$prefixes)]
cat(sprintf("  baseline-only: %d   endline-only: %d   all-wave: %d\n",
            length(base_only), length(end_only), length(allw)))

waves_of <- function(code) sort(unique(d$wave[d$item == code]))
cat("\n=== baseline-only codes must appear at wave 0 ONLY ===\n")
ok1 <- TRUE
for (c in base_only) {
    w <- waves_of(c); good <- identical(as.numeric(w), 0)
    ok1 <- ok1 && good
    cat(sprintf("  %-26s waves %-14s %s\n", c, paste(w, collapse=","), if (good) "ok" else "VIOLATION"))
}
cat("\n=== endline-only codes must NEVER appear at wave 0 ===\n")
ok2 <- TRUE
for (c in end_only) {
    w <- waves_of(c); good <- !(0 %in% w) && length(w) > 0
    ok2 <- ok2 && good
    cat(sprintf("  %-26s waves %-14s %s\n", c, paste(w, collapse=","), if (good) "ok" else "VIOLATION"))
}
cat("\n=== all-wave codes should span baseline and endline ===\n")
ok3 <- all(vapply(allw, function(c) { w <- waves_of(c); (0 %in% w) && any(w > 0) }, logical(1)))
cat(sprintf("  %d of %d span both: %s\n", sum(vapply(allw, function(c) {
    w <- waves_of(c); (0 %in% w) && any(w > 0) }, logical(1))), length(allw), ok3))

cat("\n=== What this does NOT establish ===\n")
cat("  The 25 all-wave codes are not separated from each other by this route, and\n")
cat("  neither are the members of a task family (mul_a..mul_e all read\n")
cat("  \"Multiplication\"). Their assignment rests on the dictionary naming each\n")
cat("  variable, which it does. Recorded PARTIAL for that reason, and because the\n")
cat("  shipped item_text is a task description rather than the literal problem --\n")
cat("  see provenance for why the literal problems cannot be attached to a code.\n")
cat("\nVERDICT:", if (ok1 && ok2 && ok3 && setequal(D$code, unique(d$item))) "PASS" else "FAIL", "\n")
