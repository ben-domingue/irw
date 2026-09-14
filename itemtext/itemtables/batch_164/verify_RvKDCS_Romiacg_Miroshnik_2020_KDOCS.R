# Step 5b evidence for RvKDCS_Romiacg_Miroshnik_2020_KDOCS -- re-runnable.
#
# The claim: item_text for KDOCS-1..KDOCS-50 is the wording the study's own online
# form attached to the form field of that exact name, and the live IRW item code IS
# that same field/column. Three independent links, all machine-checked here:
#
#   LINK A (code -> administered wording).  OSF g5bk4 "1. Materials/HTML study code.txt"
#     is the administered questionnaire source. Each item is a <p><b> N. text</b> block
#     followed by five {{field type="radio" name="KDOCS-k" ...}} tags. Parsing it gives
#     code -> wording with no inference. The form's PRESENTATION order is NOT the code
#     order (screen 1 = KDOCS-15, screen 2 = KDOCS-32, screen 3 = KDOCS-47, ...), so a
#     positional or off-by-one misread would be loudly visible, not silent.
#
#   LINK B (code -> live data).  data/RvKDCS_Romiacg_Miroshnik_2020.R pivots the columns
#     of "Raw data (K-DOCS; English).xlsx" that start with "KDOCS", keeping their names.
#     Checked at the CELL level: every live (id, item, resp) triple against the raw
#     sheet. Permutation-proof -- swapping any two codes breaks it (control printed).
#
#   LINK C (code -> canonical K-DOCS item number).  Independent of A and B: the item
#     wording published by the rights holder (drjamescaufman.com / K-DOCS page) is
#     compared position by position with the Russian this table ships. If code n did
#     not correspond to canonical item n, the Russian at code n would be a translation
#     of some other English item. Scored automatically by a content-word lexicon and
#     printed in full for a human read.
#
# Corroboration: the canonical K-DOCS subscale blocks (Self/Everyday 1-11, Scholarly
# 12-22, Performance 23-32, Mechanical/Scientific 33-41, Artistic 42-50) are a
# structural prediction about the correlation matrix, and the raw workbook's own
# formulas define Performance/Scientific/Artistic over exactly those contiguous code
# ranges. Plus the option -> resp direction check.

suppressMessages({library(irw); library(readxl)})

TABLE <- "RvKDCS_Romiacg_Miroshnik_2020_KDOCS"
CSV   <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                   paste0(TABLE, "__items.csv"))
if (!file.exists(CSV)) CSV <- file.path("itemtables", "batch_164", paste0(TABLE, "__items.csv"))
CACHE <- file.path("itemtext", ".cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- tempdir()
HTML_URL <- "https://osf.io/download/64f468046d1e89198a151562/"   # HTML study code.txt
XLSX_URL <- "https://osf.io/download/5faa8f20d1894f01de68b801/"   # Raw data (K-DOCS; English).xlsx

fetch <- function(url, path, mode = "wb") {
    if (!file.exists(path)) download.file(url, path, mode = mode, quiet = TRUE)
    path
}
ok <- TRUE
items <- read.csv(CSV, stringsAsFactors = FALSE, encoding = "UTF-8")

## ---- LINK A: parse the administered form -----------------------------------
html <- fetch(HTML_URL, file.path(CACHE, "study_code.txt"))
raw  <- readLines(html, warn = FALSE)
txt  <- paste(iconv(raw, from = "CP1251", to = "UTF-8"), collapse = "\n")

chunks <- strsplit(txt, "<p><b>", fixed = TRUE)[[1]]
form <- do.call(rbind, lapply(seq_along(chunks), function(i) {
    b <- chunks[i]
    if (!grepl("</b>", b, fixed = TRUE)) return(NULL)
    code <- unique(gsub('name="|"', "", regmatches(b, gregexpr('name="[^"]+"', b))[[1]]))
    if (length(code) != 1 || !grepl("^KDOCS-", code)) return(NULL)
    w <- sub("</b>.*$", "", b)
    w <- trimws(gsub("\\s+", " ", sub("^\\s*[0-9]+\\.\\s*", "", w)))
    labs <- gsub('.*label="|"$', "", regmatches(b, gregexpr('label="[^"]*"', b))[[1]])
    vals <- gsub('.*value="|"$', "", regmatches(b, gregexpr('value="[^"]*"', b))[[1]])
    data.frame(item = code, form_text = w, screen = i,
               v = paste(vals, collapse = "|"), l = paste(labs, collapse = "|"),
               stringsAsFactors = FALSE)
}))
form$screen <- rank(form$screen)
cat("== LINK A: administered form (OSF g5bk4, HTML study code.txt)\n")
cat("KDOCS item blocks parsed:", nrow(form), "\n")

ship <- unique(items[, c("item", "item_text", "item_text_translated")])
ship$item_text <- trimws(gsub("\\s+", " ", ship$item_text))
cmp <- merge(ship, form[, c("item", "form_text", "screen")], by = "item")
cmp <- cmp[order(as.integer(sub("KDOCS-", "", cmp$item))), ]
nA <- sum(cmp$item_text == cmp$form_text)
cat(sprintf("LINK A: %d/%d shipped item_text identical to the form field's own wording\n",
            nA, nrow(cmp)))
cat(sprintf("code order vs screen order: Spearman rho = %.3f  (0 = fully scrambled)\n",
            suppressWarnings(cor(as.integer(sub("KDOCS-", "", cmp$item)), cmp$screen,
                                 method = "spearman"))))
cat(sprintf("  e.g. screen 1 -> %s, screen 2 -> %s, screen 3 -> %s\n\n",
            form$item[form$screen == 1], form$item[form$screen == 2], form$item[form$screen == 3]))
if (nA != 50 || nrow(cmp) != 50) ok <- FALSE

## option labels, same source (all 50 items share one scale)
optship <- unique(items[, c("resp", "option_text")])
optship <- optship[order(optship$resp), ]
formlab <- strsplit(form$l[1], "\\|")[[1]]
formval <- strsplit(form$v[1], "\\|")[[1]]
nsets <- length(unique(form$l))
cat("== option_text vs the form's radio labels\n")
cat("distinct label sets across the 50 item blocks:", nsets, "\n")
for (i in seq_along(formlab))
    cat(sprintf("  resp=%s  form value=%-3s  %-34s | shipped: %s\n",
                optship$resp[i], formval[i], formlab[i], optship$option_text[i]))
nO <- sum(trimws(optship$option_text) == trimws(formlab))
cat(sprintf("option labels identical: %d/5 (form values S1..S5 in ascending order)\n\n", nO))
if (nO != 5 || nsets != 1) ok <- FALSE

## ---- LINK B: live data IS the named raw column, cell for cell ---------------
xl <- fetch(XLSX_URL, file.path(CACHE, "raw.xlsx"))
rw  <- readxl::read_xlsx(xl, sheet = "Dataset")
cols <- paste0("KDOCS-", 1:50)
kd  <- rw[, c("ID", cols)]
long <- data.frame(
    id   = rep(as.integer(kd$ID), 50),
    item = rep(cols, each = nrow(kd)),
    raw  = as.integer(unlist(kd[, cols], use.names = FALSE)),
    stringsAsFactors = FALSE)
long <- long[!is.na(long$raw), ]
live <- irw::irw_fetch(TABLE)
m <- merge(live, long, by = c("id", "item"))
bad <- sum(m$resp != m$raw)
cat("== LINK B: live table vs the raw workbook column of the same name\n")
cat(sprintf("live rows %d | raw non-missing cells %d | joined on (id,item) %d | disagreeing cells %d\n",
            nrow(live), nrow(long), nrow(m), bad))
if (nrow(m) != nrow(live) || bad != 0) ok <- FALSE
shift <- long
shift$item <- paste0("KDOCS-", ((as.integer(sub("KDOCS-", "", shift$item)) %% 50) + 1))
ms <- merge(live, shift, by = c("id", "item"))
cat(sprintf("control: same join under a 1-position code shift -> %d disagreeing cells\n\n",
            sum(ms$resp != ms$raw)))

## ---- LINK C: canonical K-DOCS item n vs the Russian at code n ---------------
# The English shipped in item_text_translated is the rights holder's own published
# K-DOCS wording, aligned by item number. Score the alignment against the Russian
# with a small content-word lexicon so the correspondence is a number, not a claim.
lex <- list(
 c("денег","money"), c("справиться со сложной","cope with a difficult"),
 c("Научить","Teaching"), c("баланс","balance"), c("порадовать","happy"),
 c("собственными проблемами","personal problems"), c("помощи другим","help people"),
 c("наилучшее решение","best solution"), c("поездку","trip"), c("посредника","Mediating"),
 c("расслабленно","relaxed"), c("статью для газеты","article for a newspaper"),
 c("письмо редактору","letter to the editor"), c("ресурсов","sources"),
 c("противоречивому","controversial"), c("контекста","context"),
 c("подборку статей","assortment of articles"), c("не согласен","not personally agree"),
 c("книге","book"), c("исправлений","revising"), c("обратную связь","constructive feedback"),
 c("новый взгляд","new way to think"), c("стихотворение","poem"),
 c("смешной песенки","funny song"), c("стишок","rhymes"), c("песню","song"),
 c("музыкальном инструменте","musical instrument"), c("YouTube","YouTube"),
 c("хором","harmony"), c("рэпа","rap"), c("Публично исполнять","Playing music in public"),
 c("пьесе","play"), c("дерева","wood"), c("компьютера","computer"),
 c("компьютерную программу","computer program"), c("математические","math"),
 c("Разбирать механические","Taking apart machines"), c("робота","robot"),
 c("научного эксперимента","scientific experiment"), c("теорему","proof"),
 c("металла","metal"), c("инопланетянина","alien"), c("зарисовки","Sketching"),
 c("закорючки","Doodling"), c("фотоальбома","scrapbook"), c("фото","photograph"),
 c("скульптуру","sculpture"), c("картину","painting"),
 c("интерпретацию классического","interpretation of a classic"), c("музей","museum"))
cat("== LINK C: canonical K-DOCS item n  vs  administered Russian at code n\n")
hits <- 0
for (n in 1:50) {
    ru <- cmp$item_text[cmp$item == paste0("KDOCS-", n)]
    en <- cmp$item_text_translated[cmp$item == paste0("KDOCS-", n)]
    good <- grepl(lex[[n]][1], ru, fixed = TRUE) && grepl(lex[[n]][2], en, fixed = TRUE)
    hits <- hits + good
    cat(sprintf("  %-9s %-4s RU: %-72s\n            EN: %s\n", paste0("KDOCS-", n),
                if (good) "ok" else "MISS", substr(ru, 1, 72), en))
}
cat(sprintf("LINK C: %d/50 code positions where the Russian and the rights holder's English\n", hits))
cat("        agree on a distinctive content word (lexicon fixed in this script)\n\n")
if (hits != 50) ok <- FALSE

## ---- corroboration 1: canonical subscale blocks in the correlation matrix ----
ld <- as.data.frame(live[, c("id", "item", "resp")])
w <- reshape(ld, idvar = "id", timevar = "item", direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- as.matrix(w[, cols])
R <- cor(w, use = "pairwise.complete.obs")
grp <- list(Everyday = 1:11, Scholarly = 12:22, Performance = 23:32,
            MechSci = 33:41, Artistic = 42:50)
gof <- sapply(cols, function(it) {
    n <- as.integer(sub("KDOCS-", "", it))
    own <- names(grp)[sapply(grp, function(g) n %in% g)]
    ms <- sapply(names(grp), function(g) {
        idx <- setdiff(paste0("KDOCS-", grp[[g]]), it); mean(R[it, idx]) })
    c(own = ms[[own]], best = names(which.max(ms)), bestv = max(ms))
})
nblk <- sum(unlist(gof["best", ]) == sapply(cols, function(it) {
    n <- as.integer(sub("KDOCS-", "", it)); names(grp)[sapply(grp, function(g) n %in% g)] }))
cat("== corroboration 1: canonical K-DOCS subscale blocks vs the correlation matrix\n")
cat(sprintf("items loading strongest on their canonical subscale: %d/50\n", nblk))
miss <- cols[unlist(gof["best", ]) != sapply(cols, function(it) {
    n <- as.integer(sub("KDOCS-", "", it)); names(grp)[sapply(grp, function(g) n %in% g)] })]
cat("  exceptions:", paste(miss, collapse = ", "), "\n")
cat("  (the study's own workbook reassigns KDOCS-16 and KDOCS-22 to its Everyday sum and\n")
cat("   drops KDOCS-12 from its Scholarly sum, so these are the Russian factor solution,\n")
cat("   not a mapping error; the workbook's Performance/Scientific/Artistic sums are\n")
cat("   literally SUM(KDOCS-23:KDOCS-32), SUM(KDOCS-33:KDOCS-41), SUM(KDOCS-42:KDOCS-50))\n\n")
if (nblk < 40) ok <- FALSE

## ---- corroboration 2: option direction --------------------------------------
mn <- tapply(live$resp, live$item, mean)
cat("== corroboration 2: response direction (5 = 'Намного более творческий')\n")
top <- sort(mn, decreasing = TRUE)[1:4]; bot <- sort(mn)[1:4]
cat("  highest:", paste(sprintf("%s %.2f", names(top), top), collapse = "  "), "\n")
cat("  lowest :", paste(sprintf("%s %.2f", names(bot), bot), collapse = "  "), "\n")
cat("  everyday acts (KDOCS-1 'no money', KDOCS-5 'make myself happy', KDOCS-8 'best\n")
cat("  solution') top out; specialist acts (KDOCS-35 'writing a computer program',\n")
cat("  KDOCS-31 'playing music in public', KDOCS-40 'algebraic proof') bottom out.\n")
cat("  A reversed key would make writing a computer program the most creative act.\n")
dirok <- mn[["KDOCS-1"]] > mn[["KDOCS-35"]] && mn[["KDOCS-5"]] > mn[["KDOCS-40"]]
if (!dirok) ok <- FALSE

cat("\nWhat this does NOT establish: LINK A and LINK B tie all 50 codes to their wording\n")
cat("documentarily and at the cell level, so nothing on the item axis is left open.\n")
cat("On the OPTION axis the five labels are verbatim from the same form and identical\n")
cat("across all 50 blocks, but their S1..S5 -> 1..5 order is INFERRED from the form's\n")
cat("ascending presentation (the workbook already stores integers, so no label->integer\n")
cat("key exists to read). That inference is corroborated only by the direction check\n")
cat("above, which pins the direction, not any interior permutation of levels 2/3/4.\n")
cat("LINK C compares the shipped English to the Russian; it does not audit the quality\n")
cat("of the Russian adaptation against the original beyond that content-word match.\n")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
