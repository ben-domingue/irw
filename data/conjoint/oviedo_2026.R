##Threatened waterbird conservation choice experiment (Spain, Portugal) from
##Oviedo, J. L., Campos, P., Caparrós, A., Muñoz Arroyo, G., & De la Cruz, A. (2026).
##Integrating threatened biodiversity in monetary ecosystem accounting: Choice experiments and
##simulated exchange values. Environmental and Resource Economics, 89(8).
##https://doi.org/10.1007/s10640-026-01102-4
##Replication data: Zenodo record 21133199, doi:10.5281/zenodo.21133199, CC BY 4.0 (record
##licence; the README states none). Files read: "SEV BIO DATASET.csv" (from "Data SEV BIO paper
##ERE.zip"; semicolon-separated), with "SEV BIO DATASET coding.xlsx" and
##README_SEV_BIO_paper_ERE.txt for the coding and "SEV BIO SURVEY QUESTIONNAIRE FINAL VERSION.pdf"
##(English version) for the displayed text. The article was not read.
##Usage: Rscript oviedo_2026.R <dir holding SEV BIO DATASET.csv> <output dir>
##
##979 online respondents (Tickstat platform, 12 Sep - 8 Oct 2019; 800 Spain, 179 Portugal,
##pooled in one dataset and one model by the authors: one table, cov_country), 4 choice sets
##each. Each set shows PROGRAM A, PROGRAM B and NO PROGRAM (columns), described by the change
##in the number of "vulnerable", "endangered" and "critically endangered" waterbird species in
##coastal salt marshes of the SW Iberian Peninsula over 30 years and a one-time income-tax
##increase. NO PROGRAM is the status quo and shows its own (fixed) outcomes on screen
##(3 MORE vulnerable, 2 MORE endangered, 1 MORE critically endangered; no payment), so it is
##profile 3 (A = 1, B = 2), and choice is a pick among three: no separate opt-out.
##Fixed blocked design: only 30 distinct A/B profiles occur and A/B level counts mirror each
##other; the design generator and blocks are not documented.
##Level text. The data store each level as the change in the number of species relative to the
##status quo after 30 years (coding xlsx; the status quo is 16 vulnerable, 10 endangered, 8
##critically endangered from today's 13 / 8 / 7, questionnaire p. 6). The displayed cell text is
##rebuilt from the questionnaire's template (p. 7 example "9 LESS "vulnerable" species (from 13
##to 4)", ""Vulnerable" species DO NOT CHANGE (13)", "3 MORE "vulnerable" species (from 13 to
##16)"): n = status quo + change; n = today -> DO NOT CHANGE; n < today -> "<today - n> LESS".
##All coded levels fit this template; the four example sets in the PDF show most of the 12 non-status-quo cells. The English
##questionnaire is a translation; respondents presumably saw Spanish or Portuguese (not
##documented): label text is English.
##attr_tax: the one-time tax amount as coded (50, 100, 200, 400; 0 for NO PROGRAM). The
##questionnaire's tax cells are blank in the deposited PDF, so the displayed format (currency
##sign, "0" vs blank for NO PROGRAM) is unknown; amounts are presumably euros (income question
##in EUR).
##Outcome choice: "Please, indicate the program that you would choose" (PROGRAM A / PROGRAM B /
##NO PROGRAM), exactly one per set (checked). No covariates are deposited besides country
##(1 Spain, 2 Portugal; coding xlsx). Dropped: ASC and the squared terms (derived),
##Observation number (sequential), the respondent ids are the authors' integer codes (kept).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "SEV BIO DATASET.csv"), sep = ";")
setnames(s, make.names(names(s)))
stopifnot(nrow(s) == 11748, uniqueN(s$Respondent.Id) == 979, s[, .N, Respondent.Id][, all(N == 12)])
txt <- function(ch, today, sq, word, cap) {
  n <- sq + ch
  fifelse(n == today, sprintf('"%s" species DO NOT CHANGE (%d)', cap, today),
  fifelse(n < today, sprintf('%d LESS "%s" species (from %d to %d)', today - n, word, today, n),
                     sprintf('%d MORE "%s" species (from %d to %d)', n - today, word, today, n)))
}
d <- s[, .(id = as.integer(Respondent.Id), task = as.integer(Choice.set),
           profile = c(A = 1L, B = 2L, "NO PROGRAM" = 3L)[Alternative], choice = as.integer(Choice),
           attr_vulnerable = txt(Vul, 13L, 16L, "vulnerable", "Vulnerable"),
           attr_endangered = txt(End, 8L, 10L, "endangered", "Endangered"),
           attr_critically_endangered = txt(Cri, 7L, 8L, "critically endangered", "Critically endangered"),
           attr_tax = as.character(Tax),
           cov_country = c("Spain", "Portugal")[Country])]
stopifnot(!anyNA(d), d[, sum(choice), .(id, task)][, all(V1 == 1)], d[, .N, .(id, task)][, all(N == 3)],
          s[Alternative == "NO PROGRAM", all(Vul == 0 & End == 0 & Cri == 0 & Tax == 0)],
          d[profile == 3, all(attr_vulnerable == '3 MORE "vulnerable" species (from 13 to 16)')])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "oviedo_2026_waterbirds.csv"))
