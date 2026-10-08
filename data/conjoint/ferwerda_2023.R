##Two Italian COVID conjoints (two panel waves) from
##Ferwerda, J., Magni, G., Hooghe, L., & Marks, G. (2024). How crises shape circles of
##solidarity: Evidence from the COVID-19 pandemic in Italy. Comparative Political Studies,
##57(2), 356-381 (online 2023). https://doi.org/10.1177/00104140231169028
##Replication data: Harvard Dataverse doi:10.7910/DVN/LKGEF8, CC0 1.0, no restricted files.
##Files read: wave1_numeric.csv, wave2_numeric.csv (Qualtrics exports with numeric answer
##codes and the randomizer's F-<task>-<profile>-<row> fields holding the Italian level text,
##three header rows; wave 2 is Latin-1), combined_waves.Rdata (object sdata: panel
##covariates). Codebook: codebook.pdf; English glosses from translation.R (read as text).
##Usage: Rscript ferwerda_2023.R <raw dir> <output dir>
##
##TWO TABLES (different attribute sets, outcomes and fieldings):
##  ferwerda_2023_guideline_violators (wave 1, Aug-Sep 2020): "Immagini che Lei venga assunto
##    dal Servizio Sanitario Nazionale e venga incaricato di sviluppare una campagna
##    informativa per incoraggiare i residenti in Italia a indossare le mascherine e a
##    mantenere il distanziamento sociale. Consideri i due ipotetici individui qui sotto.
##    Secondo Lei quale dei due individui sarebbe più probabile di violare le linee guida di
##    sanità pubblica?" (later tasks: "E se dovesse scegliere tra i due individui qui sotto,
##    secondo Lei quale sarebbe più probabile di violare le linee guida di sanità pubblica?")
##    Individuo 1 / Individuo 2, forced. choice = 1 for the individual judged MORE LIKELY TO
##    VIOLATE the guidelines (direction kept as asked: being chosen is unfavourable).
##    4 tasks, 7 attributes: Età (anni) Meno di 30/31-45/46-60/Più di 60; Luogo di nascita
##    Nord Italia/Centro Italia/Sud Italia/Spagna/Olanda/Cina/Marocco/Nigeria/Africa;
##    Condizione economica Povertà/Classe media/Benestante/Miliardario; Partito politico
##    Partito Democratico/Movimento 5 Stelle/Lega/Forza Italia/Fratelli d'Italia; Sesso
##    Donna/Uomo; Istruzione Scuola media/Istituto professionale/Liceo/Laurea; Condizione di
##    salute Scarsa/Buona/Eccellente.
##  ferwerda_2023_vaccine_priority (wave 2, Feb 2021): "Al momento non ci sono abbastanza
##    vaccini per tutti e non è possibile distribuirli a tutta la popolazione. Consideri i
##    due individui qui sotto. Se lei fosse incaricato di decidere come distribuire i
##    vaccini, quale dei seguenti cittadini italiani dovrebbe avere la priorità secondo lei?"
##    (later: "E quale dei seguenti cittadini italiani dovrebbe avere la priorità secondo
##    lei?"). choice = 1 for the individual who should get priority. 5 tasks, 8 attributes:
##    Età Meno di 30/31-49/50-64/65-79/Più di 80; Luogo di nascita Nord/Centro/Sud
##    Italia/Spagna/Marocco/Nigeria; Condizione economica; Partito politico; Sesso;
##    Istruzione; Condizione di salute Disabile/Malattia cronica preesistente/Buona
##    salute/Salute eccellente; Condizione lavorativa Insegnante/Lavoratore essenziale/Forze
##    dell'Ordine/Infermiere/Lavoratore da casa/Disoccupato.
##Level text is Italian, as displayed. The wave-2 export has the accents stripped
##("Piu_ di 80", "Poverta", "Eta"); restored here to "Più di 80" and "Povertà" (the wave-1
##spelling). Attribute row order was randomized once per respondent (verified fixed across
##tasks): attrpos_* (1 = top). The wave-1 level "Africa" for birthplace appears for some
##respondents (the authors drop those profile rows); kept here.
##TASK MAPPING (wave 1): the questions pipe different randomizer sets than their order
##suggests: Q15.1 shows F-1, Q15.3 shows F-3, Q15.5 shows F-2, Q15.7 shows F-4 (question
##text in the export's header row). Here task = question order (1-4) with the profiles that
##question displayed; trial_profile_set = the randomizer set (F-index). Verified in the data:
##attributes explain the Q15.3 answers with F-3 (R2 0.027) but not with F-2 (0.004), and the
##Q15.5 answers with F-2 (0.025) but not F-3 (0.006). The authors' read.qualtrics call maps
##Q15.3 -> F-2 and Q15.5 -> F-3, so their wave-1 estimates pair two of the four tasks with
##the wrong profiles. FOR BEN: authors' error, not fixed in their numbers.
##Wave 2 maps in order (Q15.1, Q160, Q161, Q15.3, Q15.5 -> F-1..F-5).
##Sample: every response with at least one answered task (wave 1: most of the 8,577 export
##rows are panel members who never reached the conjoint). cov_in_authors_sample = 1 for
##respondents in sdata with both_waves == 1 and a consistent age across waves (the
##authors' analysis sample for both waves).
##Ids: Qualtrics ResponseIds re-keyed to integers (id); cov_panel_id = the panel PID
##re-keyed to integers with ONE mapping for both tables, so the same person can be linked
##across waves. Some PIDs appear on more than one response in a wave.
##Covariates (from sdata, wave-1 measures; codebook.pdf): cov_female 1/0; cov_age 1=18-24
##2=25-34 3=35-44 4=45-54 5=55-64 6=65+; cov_leftright 0-10 (left-right self-placement,
##11-point); cov_vote 1=M5S 2=Lega 3=Forza Italia 4=PD 5=Fratelli d'Italia 6=Italia Viva
##9=Sinistra/MDP/Articolo 1 10=Più Europa 13=other 14=will not vote; cov_region 1-7
##(anonymized); cov_non_citizen 1/0. Dropped: dates, Finished flag, other sdata items.
##PII in deposit (not read into the table): Qualtrics ResponseIds and panel PIDs.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "combined_waves.Rdata"), envir = e); sd <- as.data.table(e$sdata)
sd[, PID := format(PID, scientific = FALSE, trim = TRUE)]
sd <- sd[PID != "NA" & !is.na(PID)]
auth <- sd[both_waves == 1 & abs(w2_age - age) <= 1, PID]
cv <- sd[, .(PID, cov_female = as.integer(female), cov_age = as.integer(age), cov_leftright = as.numeric(leftright),
             cov_vote = as.integer(votechoice_current), cov_region = as.integer(region), cov_non_citizen = as.integer(non_citizen))]
cv <- unique(cv)   # sdata repeats a few PIDs as identical rows
stopifnot(!anyDuplicated(cv$PID))
x1 <- fread(file.path(raw, "wave1_numeric.csv"), colClasses = "character", encoding = "UTF-8", na.strings = "")[-(1:2)]
x2 <- fread(file.path(raw, "wave2_numeric.csv"), colClasses = "character", encoding = "Latin-1", na.strings = "")[-(1:2)]
pids <- unique(na.omit(c(x1$PID, x2$PID)))
an <- c("Età (anni)" = "age", "Eta (anni)" = "age", "Luogo di nascita" = "birthplace", "Condizione economica" = "economic_status",
        "Partito politico" = "party", "Sesso" = "gender", "Istruzione" = "education", "Condizione di salute" = "health",
        "Condizione lavorativa" = "occupation")
build <- function(x, qs, sets, nattr) {
  rn <- sapply(1:nattr, function(k) x[[sprintf("F-1-%d", k)]])
  for (t in sets) stopifnot(all(sapply(1:nattr, function(k) x[[sprintf("F-%d-%d", t, k)]]) == rn))
  short <- matrix(an[rn], nrow(x)); stopifnot(!anyNA(short))
  d <- rbindlist(lapply(seq_along(qs), function(t) rbindlist(lapply(1:2, function(p) {
    ans <- x[[qs[t]]]; stopifnot(all(is.na(ans) | ans %in% c("1", "2")))
    lv <- sapply(1:nattr, function(k) x[[sprintf("F-%d-%d-%d", sets[t], p, k)]])
    y <- data.table(r = seq_len(nrow(x)), task = t, profile = p, choice = as.integer(ans == as.character(p)), trial_profile_set = sets[t])
    for (nm in unique(an)) {
      m <- short == nm
      if (!any(m)) next
      j <- max.col(m, ties.method = "first")
      y[, paste0("attr_", nm) := lv[cbind(seq_len(nrow(x)), j)]]
      y[, paste0("attrpos_", nm) := j]
    }
    y
  }))))
  d <- d[!is.na(choice)]
  stopifnot(d[, sum(choice), .(r, task)][, all(V1 == 1)])
  d[, `:=`(PID = x$PID[r], rid = x$ResponseId[r])]
  stopifnot(!anyDuplicated(x$ResponseId))
  setorder(d, r, task, profile)
  d[, id := match(r, unique(r))]
  d[, cov_panel_id := match(PID, pids)]
  d[, cov_in_authors_sample := as.integer(!is.na(PID) & PID %in% auth)]
  d <- merge(d, cv, by = "PID", all.x = TRUE, sort = FALSE)
  d[, c("r", "PID", "rid") := NULL]
  ac <- sort(grep("^attr_", names(d), value = TRUE)); pc <- sort(grep("^attrpos_", names(d), value = TRUE))
  setcolorder(d, c("id", "task", "profile", "choice", ac, pc, "trial_profile_set"))
  setorder(d, id, task, profile)
  d
}
d1 <- build(x1, c("Q15.1", "Q15.3", "Q15.5", "Q15.7"), c(1L, 3L, 2L, 4L), 7)
fwrite(d1, file.path(out, "ferwerda_2023_guideline_violators.csv"))
d2 <- build(x2, c("Q15.1", "Q160", "Q161", "Q15.3", "Q15.5"), 1:5, 8)
d2[attr_age == "Piu_ di 80", attr_age := "Più di 80"][attr_economic_status == "Poverta", attr_economic_status := "Povertà"]
d2[, trial_profile_set := NULL]
fwrite(d2, file.path(out, "ferwerda_2023_vaccine_priority.csv"))
