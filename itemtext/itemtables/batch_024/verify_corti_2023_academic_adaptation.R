#!/usr/bin/env Rscript
# verify_corti_2023_academic_adaptation.R
#
# MAPPING check (not plumbing). The IRW item codes P1_a..P1_g ARE the source
# SPSS column names (data/corti_2023_academic_adaptation.py melts ITEM_COLS
# verbatim), and each column carries its own Spanish variable label -- so the
# code->text tie is at the source. This script re-derives the independent
# corroboration: the PLOS paper prints per-item means broken down by degree
# programme (Tables 3, 4 and 5), and each of the seven items has a DISTINCT
# triple of degree means, so matching those triples distinguishes every item
# from every other item.
#
# It also ties the .sav columns to the live IRW table without exporting it,
# using irw::irw_table_sets(per_item=TRUE): per-item non-missing n.

suppressMessages({library(haven); library(irw)})

url <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0294440.s001")
tmp <- file.path(tempdir(), "corti_s001.sav")
if (!file.exists(tmp)) download.file(url, tmp, mode = "wb", quiet = TRUE)
d <- haven::read_sav(tmp)

items <- c("P1_a","P1_b","P1_c","P1_d","P1_e","P1_f","P1_g")
# shipped item_text, in the same order
shipped <- c("Estoy satisfecho con los estudios elegidos",
             "Me siento cómodo con el ambiente educativo",
             "Estoy disfrutando con los estudios",
             "Estoy satisfecho con mi vida de estudiante",
             "Me gusta el nivel de estimulación académica de la clase",
             "Estoy satisfecho con las asignaturas",
             "Me gusta lo que estoy aprendiendo en las clases")

ok <- TRUE

cat("== 1. SPSS variable label vs shipped item_text ==\n")
for (i in seq_along(items)) {
  lab <- attr(d[[items[i]]], "label")
  agree <- identical(as.character(lab), shipped[i])
  ok <- ok && agree
  cat(sprintf("  %-5s label=%-58s shipped_matches=%s\n", items[i], lab, agree))
}

cat("\n== 2. Paper degree-group means (Tables 3/4/5) vs computed ==\n")
# ensenyament: 1=ADE/BAM, 2=Pedagogia, 3=Ed. Infantil
paper <- rbind(
  P1_a = c(BAM=4.05, Ped=4.30, ECE=4.53),  # T3 "Degree chosen"
  P1_b = c(3.71, 4.17, 3.81),              # T4 "Educational atmosphere"
  P1_c = c(3.57, 4.09, 3.42),              # T3 "Enjoyment of studies"
  P1_d = c(3.87, 4.20, 3.52),              # T5 "My student life"
  P1_e = c(2.78, 3.48, 3.06),              # T4 "Academic stimulation"
  P1_f = c(3.25, 3.28, 2.77),              # T3 "Modules"
  P1_g = c(3.67, 3.96, 3.65))              # T3 "Classroom learning"
colnames(paper) <- c("BAM","Ped","ECE")

comp <- t(sapply(items, function(v)
  tapply(as.numeric(d[[v]]), as.numeric(d$ensenyament), mean, na.rm = TRUE)))
colnames(comp) <- c("BAM","Ped","ECE")

for (i in items) {
  dif <- max(abs(comp[i, ] - paper[i, ]))
  agree <- dif <= 0.011
  ok <- ok && agree
  cat(sprintf("  %-5s paper=%s computed=%s maxdiff=%.4f ok=%s\n", i,
              paste(sprintf("%.2f", paper[i, ]), collapse="/"),
              paste(sprintf("%.2f", comp[i, ]), collapse="/"), dif, agree))
}

cat("\n== 3. Each item's degree-mean triple is unique (route distinguishes all 7) ==\n")
rounded <- apply(round(comp, 2), 1, paste, collapse="/")
cat("  distinct triples:", length(unique(rounded)), "of", length(items), "\n")
ok <- ok && length(unique(rounded)) == length(items)
# and no other item's paper triple is within tolerance of a given item's data
crosshits <- 0
for (i in items) for (j in items) if (i != j && max(abs(comp[i, ] - paper[j, ])) <= 0.011) crosshits <- crosshits + 1
cat("  off-diagonal matches within tolerance:", crosshits, "(want 0)\n")
ok <- ok && crosshits == 0

cat("\n== 4. .sav columns tie to live IRW items (per-item n, no export) ==\n")
s <- try(irw::irw_table_sets("corti_2023_academic_adaptation", source = "core",
                             per_item = TRUE), silent = TRUE)
if (inherits(s, "try-error")) {
  cat("  irw_table_sets() unavailable; skipping (steps 1-3 stand alone)\n")
} else {
  pi <- as.data.frame(s$per_item)
  ncol_n <- intersect(c("n","n_resp","count"), names(pi))[1]
  live <- setNames(as.numeric(pi[[ncol_n]]), pi$item)[items]
  sav  <- sapply(items, function(v) sum(!is.na(d[[v]])))
  cat("  live:", paste(live, collapse=","), "\n")
  cat("  .sav:", paste(sav,  collapse=","), "\n")
  agree <- all(live == sav); ok <- ok && agree
  cat("  identical:", agree, "\n")
}

cat("\nNOT established by this route: the response-anchor wording (1..5 is\n")
cat("unlabelled in both the .sav and the paper, so option_text ships blank).\n\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
