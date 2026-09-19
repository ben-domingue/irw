# verify_poza2026_hlseu.R -- Step 5b mapping evidence, re-runnable.
#
# CLAIM UNDER TEST: the k-th row of Table S1 of Bas-Sarmiento et al. (2020,
# IJERPH 17:8181) -- the Arabic/French HLS-EU-Q16 adaptation actually
# administered here -- is HLS-EU-Q16 item k, and therefore belongs to column
# PREGUNTAk (whose SPSS variable label reads "kHLS-EU").
#
# FALSIFIABLE PREDICTION: the source .sav carries six *derived* composite
# variables whose own labels name the item numbers they sum. Three of them
# (HLinteractiva / HLFuncional / HLCritica) partition 1..16 by health-literacy
# COMPETENCE -- access, understand, appraise+apply. Table S1's rows carry that
# competence in their leading verb (Trouver/Repérer = access; Comprendre =
# understand; Évaluer/Utiliser/Suivre/Décide = appraise+apply). If the row order
# were permuted across competence classes, the two partitions would disagree.
# Three more (Cuidado/Prevencion/Promocion) partition 1..16 by DOMAIN.
#
# This script recomputes the composites from the raw PREGUNTA columns (proving
# the labels really do name those columns), then compares the competence
# partition implied by the SHIPPED item_text against the .sav's.

suppressMessages({ library(haven) })

TABLE   <- "poza2026_hlseu"
SAV_URL <- "https://ndownloader.figshare.com/files/61057522"   # Datos_HL_Migrant_.sav
ITEMS   <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                     paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS)) ITEMS <- file.path("itemtables", "batch_142", paste0(TABLE, "__items.csv"))

tmp <- tempfile(fileext = ".sav")
utils::download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
d <- haven::read_sav(tmp)
P <- function(ns) rowSums(sapply(ns, function(n) as.numeric(d[[paste0("PREGUNTA", n)]])))
# some respondents skipped items; compare only rows where every input is observed
cc <- stats::complete.cases(sapply(1:16, function(n) as.numeric(d[[paste0("PREGUNTA", n)]])))

cat("=== 0. (plumbing, NOT mapping evidence) is this .sav the file the live table came from? ===\n")
liven <- c(PREGUNTA1=96, PREGUNTA2=100, PREGUNTA3=101, PREGUNTA4=101, PREGUNTA5=91,
           PREGUNTA6=98, PREGUNTA7=101, PREGUNTA8=90, PREGUNTA9=99, PREGUNTA10=99,
           PREGUNTA11=101, PREGUNTA12=100, PREGUNTA13=101, PREGUNTA14=101,
           PREGUNTA15=100, PREGUNTA16=92)   # irw::irw_table_sets(per_item=TRUE), 2026-09-10
savn <- sapply(names(liven), function(k) sum(!is.na(d[[k]])))
cat(sprintf("  per-item non-missing n, .sav vs live: %d/16 identical (total %d vs %d)\n",
            sum(savn == liven), sum(savn), sum(liven)))
cat("  This only says the deposit is the right file; it says nothing about which text goes with which code.\n\n")
ok0 <- all(savn == liven)

cat("=== 1. the .sav's derived composites really are sums of the PREGUNTA columns ===\n")
comp <- list(
  ResultadoHLSEU = 1:16,                 # label "TOTAL"
  HLinteractiva  = c(1, 2, 8, 13),       # label "1,2,8,13"        access
  HLFuncional    = c(3, 4, 9, 10, 14, 15), # label "3,4,9,10,14,15" understand
  HLCritica      = c(5, 11, 16, 6, 7, 12), # label "5,11,16,6,7,12" appraise+apply
  CuidadoHCHL    = 1:7,                  # label "1,2,3,4,5,6,7"   health care
  PrevencionDCHL = 8:12,                 # label "8,9,10,11,12"    disease prevention
  PromocionHPHL  = 13:16                 # label "13,14,15,16"     health promotion
)
n <- sum(cc)
cat(sprintf("  (%d of %d respondents answered all 16 items; composites compared on those)\n", n, nrow(d)))
for (k in names(comp)) {
  diff <- abs(as.numeric(d[[k]]) - P(comp[[k]]))[cc]
  cat(sprintf("  %-15s label=%-18s exact for %3d/%3d rows (max |diff| = %.0f)\n",
              k, dQuote(attr(d[[k]], "label")), sum(diff < 1e-9), n, max(diff)))
}
# Known source defect: PrevencionDCHL is labelled 8..12 but is actually 9..12.
alt <- abs(as.numeric(d$PrevencionDCHL) - P(9:12))[cc]
cat(sprintf("  PrevencionDCHL recomputed as items 9-12 instead: exact for %d/%d rows\n",
            sum(alt < 1e-9), n))
cat("  -> the authors dropped item 8 from their own DP sum; item 8's domain is still\n")
cat("     pinned to DP because it is in neither CuidadoHCHL (1-7) nor PromocionHPHL (13-16).\n")

ok1 <- all(sapply(setdiff(names(comp), "PrevencionDCHL"),
                  function(k) all(abs(as.numeric(d[[k]]) - P(comp[[k]]))[cc] < 1e-9))) &&
       all(alt < 1e-9)

cat("\n=== 2. competence class implied by the SHIPPED item_text ===\n")
it <- read.csv(ITEMS, stringsAsFactors = FALSE, fileEncoding = "UTF-8")
it <- it[!duplicated(it$item), c("item", "item_text")]
num <- as.integer(sub("^PREGUNTA", "", it$item))
it  <- it[order(num), ]; num <- sort(num)
fr  <- sub("^.*\\[French version\\] ", "", it$item_text)
# Classification rule, fixed a priori from the HLS-EU competence definitions:
#   access/obtain  = the item is about FINDING something  (trouver / repérer)
#   understand     = the item begins "Comprendre"
#   appraise+apply = everything else (Évaluer / Envisager / Utiliser / Suivre / Décide)
verb <- sub("^([[:alpha:]\u00c0-\u017f]+).*$", "\\1", fr)
cls <- ifelse(grepl("trouver|Trouver|Répérer|Repérer", fr), "access",
       ifelse(grepl("^Comprendre$", verb), "understand", "appraise_apply"))
# the cruder leading-verb-only rule, reported for honesty (it misroutes item 8,
# whose French renders the canonical "find information on..." as
# "Suivre les renseignements pour trouver la solution ...")
cls0 <- ifelse(grepl("^(Trouver|Répérer|Repérer)$", verb), "access",
        ifelse(grepl("^Comprendre$", verb), "understand", "appraise_apply"))
for (i in seq_along(num))
  cat(sprintf("  PREGUNTA%-2d  verb=%-11s -> %-14s | %s\n", num[i], verb[i], cls[i], substr(fr[i], 1, 58)))

derived <- split(num, cls)
stated  <- list(access = sort(comp$HLinteractiva),
                understand = sort(comp$HLFuncional),
                appraise_apply = sort(comp$HLCritica))
cat("\n  derived from shipped text : access=", paste(sort(derived$access), collapse = ","),
    " | understand=", paste(sort(derived$understand), collapse = ","),
    " | appraise_apply=", paste(sort(derived$appraise_apply), collapse = ","), "\n", sep = "")
cat("  stated by the .sav labels : access=", paste(stated$access, collapse = ","),
    " | understand=", paste(stated$understand, collapse = ","),
    " | appraise_apply=", paste(stated$appraise_apply, collapse = ","), "\n", sep = "")
ok2 <- all(sapply(names(stated), function(k)
  identical(as.integer(sort(derived[[k]])), as.integer(sort(stated[[k]])))))
cat("  partitions identical: ", ok2, sep = "")
cat(sprintf("   (%d/16 items land in the class the .sav names)\n",
            sum(unlist(lapply(names(stated), function(k) sum(num[cls == k] %in% stated[[k]]))))))
cat(sprintf("  leading-verb-only rule (no \"contains trouver\") would score %d/16: it puts\n",
            sum(unlist(lapply(names(stated), function(k) sum(num[cls0 == k] %in% stated[[k]]))))))
cat("  item 8 in appraise+apply because its French begins \"Suivre\"; the .sav puts 8 in\n")
cat("  access, and the item is canonically \"find information on managing mental health\".\n")

cat("\n=== 3. what the cross-classification does and does not pin ===\n")
dom <- ifelse(num <= 7, "HC", ifelse(num <= 12, "DP", "HP"))
cell <- paste(dom, cls, sep = "/")
tab <- split(num, cell)
uniq <- names(tab)[sapply(tab, length) == 1]
for (k in names(tab))
  cat(sprintf("  %-22s -> items %s%s\n", k, paste(tab[[k]], collapse = ","),
              if (length(tab[[k]]) == 1) "   [UNIQUELY PINNED]" else ""))
cat(sprintf("\n  uniquely pinned by the data: %d of 16 items (%s).\n", length(uniq),
            paste(unlist(tab[uniq]), collapse = ", ")))
cat("  NOT established: the order WITHIN each multi-item cell -- {1,2}, {3,4}, {5,6,7},\n")
cat("  {9,10}, {11,12}, {14,15}. Those rest on 1:1 semantic correspondence between the\n")
cat("  Table S1 rows and the canonical HLS-EU-Q16 numbering, which this data cannot test.\n")
cat("  Status is therefore PARTIAL, not VERIFIED.\n")

cat(if (ok0 && ok1 && ok2) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")
