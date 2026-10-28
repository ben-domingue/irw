##Offline replay of the whole licence stack -- LICENSE_OVERRIDES then
##LICENSE_SPELLINGS -- against the real biblio exports, so a new entry can be
##counted before it ships (#3226, #3229). Not a test: it reads the published
##CSVs and prints what would change.
##Run from the metadata directory: Rscript tests/replay_license_edits.R
source("dict_union.R")
files <- c(core = "biblio.csv", comps = "comps_biblio.csv",
           conj = "conj_biblio.csv", rank = "rank_biblio.csv",
           nominal = "nominal_biblio.csv", sim = "simsyn_biblio.csv")
for (nm in names(files)) {
    f <- files[[nm]]
    if (!file.exists(f)) next
    b <- read.csv(f, stringsAsFactors = FALSE, check.names = FALSE,
                  colClasses = "character", na.strings = character(0))
    before <- b$Derived_License
    ov <- suppressMessages(suppressWarnings(apply_license_overrides(b, nm)))
    b2 <- suppressMessages(canonicalise_license_spelling(ov$biblio, nm))
    ch <- which(before != b2$Derived_License)
    cat("\n== ", nm, " (", nrow(b), " rows): ", length(ch), " changed\n", sep = "")
    if (length(ch)) {
        for (i in ch) cat("   ", b$table[i], ": ", before[i], " -> ",
                          b2$Derived_License[i], "\n", sep = "")
    }
    suppressMessages(check_license_vocabulary(b2, nm)) -> leads
    if (length(leads)) cat("   unversioned leads: ", paste(leads, collapse = ", "), "\n", sep = "")
}
