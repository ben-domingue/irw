# Shared verification for the three chile_2023_social-welfare-survey_* tables (#1945, batch_204).
# Sourced by the three per-table wrappers, which set TB and SHEET first.
#
# SOURCE. Encuesta de Bienestar Social 2023 (EBS 2023), Subsecretaría de Evaluación Social /
# Instituto Nacional de Estadísticas, Chile. The codebook 'libro_de_codigos_ebs_2023.xlsx'
# carries one sheet per questionnaire module, and each sheet lists every variable with its
# Name, its Label (the question as asked), each permitted value, that value's Spanish label,
# and -- crucially -- the observed FREQUENCY of that value in the published data.
#
# WHY THAT LAST COLUMN MATTERS. It turns verification from an argument into a reproduction.
# If the item codes, the value codes and the value labels have all been carried across
# correctly, then the codebook's frequency for a given (item, value) must equal the number of
# rows the live table has at that item and that value. It is a joint test: a wrong item
# mapping, a shifted value coding or a mismatched sample would each break it.
#
# SCOPE. Only categorical values carry a frequency, so the test covers those. The duration and
# count items (the u*_a "¿Por cuánto tiempo...?" series and ss8 "¿Cuántas veces...?") are
# genuinely numeric, have no value labels in the codebook, and ship with option_text blank --
# they are outside this check by construction, not by omission. Negative codes (-99 no
# responde, -88 no sabe, -89 no aplica) are missing-data markers and are absent from the live
# table, so they are excluded too.
suppressWarnings(suppressMessages(library(jsonlite)))
CB <- ".cache/batch_204/chile_codebook.json"
if (!file.exists(CB)) stop("missing extracted codebook: ", CB)
cb <- fromJSON(CB, simplifyVector = FALSE)[[SHEET]]

d <- as.data.frame(irw::irw_fetch(TB))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv(file.path("itemtables/batch_204", paste0(TB, "__items.csv")),
                  stringsAsFactors = FALSE, na.strings = "NA")

cat("=== 1. item sets: live vs codebook module", SHEET, "===\n")
cat(sprintf("  codebook %d, live %d, identical: %s\n",
            length(cb), length(unique(d$item)), setequal(names(cb), unique(d$item))))

cat("\n=== 2. codebook frequencies reproduced from the live table ===\n")
tb <- table(d$item, d$resp)
tot <- ok <- 0; bad <- character(0)
for (code in names(cb)) {
    if (!code %in% rownames(tb)) next
    for (v in names(cb[[code]]$vals)) {
        f <- cb[[code]]$vals[[v]]$freq
        if (is.null(f) || is.na(suppressWarnings(as.numeric(v))) || as.numeric(v) < 0) next
        key <- as.character(as.integer(as.numeric(v)))
        if (!key %in% colnames(tb)) next
        got <- tb[code, key]; tot <- tot + 1
        if (got == f) ok <- ok + 1
        else bad <- c(bad, sprintf("%s v=%s codebook %s live %s", code, key, f, got))
    }
}
cat(sprintf("  %d of %d (item, value) frequencies match EXACTLY%s\n", ok, tot,
            if (!length(bad)) "" else paste0(" -- mismatches: ", paste(head(bad, 5), collapse="; "))))

cat("\n=== 3. option_text coverage ===\n")
lab <- unique(items$item[!is.na(items$option_text)])
nolab <- setdiff(unique(items$item), lab)
cat(sprintf("  items with labelled options: %d; without: %d\n", length(lab), length(nolab)))
cat(sprintf("  the unlabelled ones are the numeric items: %s\n",
            if (!length(nolab)) "(none)" else paste(nolab, collapse=", ")))
cat("  (the codebook gives no value labels for these because the answer is a duration or a count)\n")

cat("\nVERDICT:", if (!length(bad) && setequal(names(cb), unique(d$item))) "PASS" else "FAIL", "\n")
