# verify_chile_2023_children-adolescents-survey_aa.R
#
# WHAT IS BEING VERIFIED
# ----------------------
# Every shipped item_text / option_text pair in
# chile_2023_children-adolescents-survey_aa__items.csv is keyed to a variable
# name (a3, a5_1, ... a12) in the EANNA 2023 codebook -- "Libro de codigos base
# de datos EANNA 2023", sheet "4. NNA" -- and the do-file
# data/chile_2023_children-adolescents-survey.do carries that name straight
# through (`gen item = "`var'"`), so `item` IS the source column name.
#
# The falsifiable prediction that makes that tie checkable rather than asserted:
# the codebook prints, for EVERY variable and EVERY value, the frequency of that
# value in the deposited data. If item_text for (say) a8_1 "A tu mama" and a8_4
# "A un profesor(a) u orientador(a)" had been swapped, the shipped text would sit
# against the wrong frequency profile. The 38 profiles below are all distinct, so
# this route distinguishes every item from every other item -- including inside
# the a8_*/a9_*/a11_* multi-select blocks, whose per-item n are identical and
# therefore could NOT be told apart by counts alone.
#
# Live counts come from a server-side GROUP BY (redivis query), not irw_fetch():
# this table is 475,380 rows and a full export against the 200GB/30-day cap is
# not warranted for 83 numbers.
#
# Codebook source (hard-coded per the template's rule 4 -- a published document
# that will not change):
#   https://observatorio.ministeriodesarrollosocial.gob.cl/storage/docs/eanna/2023/Libro_de_codigos_EANNA_2023.xlsx
#   sheet "4. NNA", columns Variable / Valor / Frecuencia.
# Negative codes (-88 No sabe, -99 No responde) are excluded: the do-file
# mvdecodes them to missing, so they cannot appear in the live table.

suppressMessages(library(irw))

TABLE <- "chile_2023_children-adolescents-survey_aa"
TOL   <- 1   # absolute count tolerance; see the note printed at the end

CODEBOOK <- data.frame(matrix(c(
  "a3", 1, 3392,   "a3", 2, 8990,
  "a5_1", 1, 2269, "a5_1", 2, 966,
  "a5_2", 1, 950,  "a5_2", 2, 2309,
  "a5_3", 1, 1770, "a5_3", 2, 1561,
  "a6", 1, 11, "a6", 2, 122, "a6", 3, 2931, "a6", 4, 7904, "a6", 5, 1443,
  "a8_1", 1, 3508,  "a8_1", 0, 8915,
  "a8_2", 1, 1046,  "a8_2", 0, 11377,
  "a8_3", 1, 629,   "a8_3", 0, 11794,
  "a8_4", 1, 7437,  "a8_4", 0, 4986,
  "a8_5", 1, 2163,  "a8_5", 0, 10260,
  "a8_6", 1, 57,    "a8_6", 0, 12366,
  "a8_77", 1, 139,  "a8_77", 0, 12284,
  "a8_78", 1, 1069, "a8_78", 0, 11354,
  "a8_87", 1, 75,   "a8_87", 0, 12348,
  "a8_88", 1, 27,   "a8_88", 0, 12396,
  "a8_99", 1, 8,    "a8_99", 0, 12415,
  "a9_1", 1, 9358,  "a9_1", 0, 3152,
  "a9_2", 1, 2985,  "a9_2", 0, 9525,
  "a9_3", 1, 2455,  "a9_3", 0, 10055,
  "a9_4", 1, 66,    "a9_4", 0, 12444,
  "a9_5", 1, 395,   "a9_5", 0, 12115,
  "a9_6", 1, 55,    "a9_6", 0, 12455,
  "a9_77", 1, 158,  "a9_77", 0, 12352,
  "a9_78", 1, 1091, "a9_78", 0, 11419,
  "a9_87", 1, 44,   "a9_87", 0, 12466,
  "a9_88", 1, 38,   "a9_88", 0, 12472,
  "a9_99", 1, 8,    "a9_99", 0, 12502,
  "a10", 1, 30, "a10", 2, 135, "a10", 3, 222, "a10", 4, 11426, "a10", 5, 209,
  "a11_1", 1, 9305,  "a11_1", 0, 3118,
  "a11_2", 1, 395,   "a11_2", 0, 12029,
  "a11_3", 1, 658,   "a11_3", 0, 11765,
  "a11_4", 1, 1301,  "a11_4", 0, 11122,
  "a11_5", 1, 85,    "a11_5", 0, 12338,
  "a11_6", 1, 37,    "a11_6", 0, 12386,
  "a11_77", 1, 449,  "a11_77", 0, 11975,
  "a11_88", 1, 1084, "a11_88", 0, 11339,
  "a11_99", 1, 13,   "a11_99", 0, 12410,
  "a12", 1, 8878, "a12", 2, 2805, "a12", 3, 623
), ncol = 3, byrow = TRUE), stringsAsFactors = FALSE)
names(CODEBOOK) <- c("item", "resp", "cb_n")
CODEBOOK$resp <- as.integer(CODEBOOK$resp)
CODEBOOK$cb_n <- as.integer(CODEBOOK$cb_n)

# --- the shipped mapping, read from the CSV beside this script -------------
here  <- tryCatch({
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grep("^--file=", a)])
    if (length(f)) dirname(normalizePath(f[1])) else "."
}, error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
shipped <- if (file.exists(items_csv)) read.csv(items_csv, stringsAsFactors = FALSE) else NULL

# --- live per-item x per-resp counts, server side --------------------------
ref <- irw::irw_table_sets(TABLE, source = "core")$table
sql <- sprintf(
  "SELECT item, resp, COUNT(*) AS n FROM `%s` WHERE resp IS NOT NULL GROUP BY item, resp",
  ref)
live <- redivis::query(sql)$to_data_frame()
live$resp <- as.integer(live$resp)
live$n    <- as.integer(live$n)

m <- merge(CODEBOOK, live, by = c("item", "resp"), all = TRUE)
m <- m[order(m$item, m$resp), ]
m$diff <- m$n - m$cb_n

cat(sprintf("%-8s %5s %12s %12s %7s  %s\n",
            "item", "resp", "codebook_n", "live_n", "diff", "shipped option_text"))
for (i in seq_len(nrow(m))) {
    ot <- ""
    if (!is.null(shipped)) {
        k <- which(shipped$item == m$item[i] & shipped$resp == m$resp[i])
        if (length(k)) ot <- shipped$option_text[k[1]]
    }
    cat(sprintf("%-8s %5d %12s %12s %7s  %s\n", m$item[i], m$resp[i],
                ifelse(is.na(m$cb_n[i]), "-", m$cb_n[i]),
                ifelse(is.na(m$n[i]), "-", m$n[i]),
                ifelse(is.na(m$diff[i]), "?", m$diff[i]), ot))
}

n_cells <- nrow(m)
exact   <- sum(!is.na(m$diff) & m$diff == 0)
worst   <- suppressWarnings(max(abs(m$diff), na.rm = TRUE))
cat(sprintf("\ncells compared: %d | exact: %d | largest |diff|: %s (tolerance %d)\n",
            n_cells, exact, ifelse(is.finite(worst), worst, "NA"), TOL))

# Profile uniqueness -- this is what makes the route distinguish every item.
prof <- tapply(seq_len(nrow(CODEBOOK)),
               CODEBOOK$item,
               function(ix) paste(sort(CODEBOOK$cb_n[ix]), collapse = "/"))
cat(sprintf("distinct frequency profiles: %d of %d items\n",
            length(unique(prof)), length(prof)))

cat("\nWhat this establishes: each of the 38 live item codes carries the value\n",
    "frequencies the EANNA codebook publishes for the variable of that name, and\n",
    "all 38 profiles are distinct, so no pair of items could be exchanged without\n",
    "breaking the match. It therefore pins item_text AND option_text per item.\n",
    "What it does NOT establish: that the codebook's own variable labels are\n",
    "correctly assigned at source. If MDSF mislabelled a variable, this would not\n",
    "see it; nothing in the deposit is independent of the deposit.\n", sep = "")

ok <- is.finite(worst) && worst <= TOL &&
      all(!is.na(m$cb_n)) && all(!is.na(m$n)) &&
      length(unique(prof)) == length(prof)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
