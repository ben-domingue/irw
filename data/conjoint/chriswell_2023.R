##Paired neighbourhood-organizing vignettes (Mexico City) from
##Chriswell, K., & Huberts, A. (2023). Collective action infrastructure: The downstream effects
##of urban neighborhood organizing. Comparative Political Studies.
##https://doi.org/10.1177/00104140231193018
##Replication data: Harvard Dataverse doi:10.7910/DVN/A8THZ9, CC0 1.0. Files read:
##cai_survey.Rdata (data frame `dat`, loaded into its own environment);
##ChriswellHuberts_codebook.docx, README.rtf and replication_vignettes_cai.R read as text.
##Usage: Rscript chriswell_2023.R <dir holding cai_survey.Rdata> <output dir>
##
##Online Qualtrics survey, Mexico City, August 2021, recruited through Facebook ads with a
##lottery incentive; 1,690 responses in the file (README). The authors' vignette code keeps
##respondents with last_answer >= 79; this script keeps everyone who answered a vignette.
##Each respondent saw three vignette sets, each a table of two colonias with a Problem,
##the Neighbors' Response, and a Result (Spanish text as displayed, from the Qualtrics
##embedded data), then questions about how hard it would be for the neighbours of each
##colonia to organize around a second problem (trial_problem_asked, randomized, the same for
##both colonias of a set). Sets 1 and 2 share one design and are tasks 1 and 2 of one table;
##set 3 adds a row and asks different questions, so it is its own table (one task):
##  chriswell_2023_organizing_pairs (sets 1-2; colonias "Alcatraz"/"Magnolia" and
##    "Dalia"/"Orquídea" are profiles 1/2, as in the authors' code):
##    attr_problem: "Problemas con la frecuencia y presion del suministro de agua" /
##      "Un aumento en tiroteos por la colonia"
##    attr_neighbors_response: "Compartieron informacion entre vecinos por WhatsApp" /
##      "No se organizaron" / "Se organizaron para solicitar ayuda de la alcaldia" / a private
##      response that depends on the problem ("Se organizaron entre vecinos para compartir su
##      agua y pedir pipas privadas" with water, "... para monitorear la colonia" with shootings)
##    attr_result: success/failure text that depends on the problem ("Se resolvieron sus
##      problemas de agua" / "Sus problemas de agua seguían" / "Se redujo la tasa de crimen" /
##      "La tasa de crimen se mantuvo")
##    rating: "How difficult do you think it would be for the neighbors to organize in the
##      first/second colonia?" (authors' English rendering; respondents saw Spanish:
##      translated), stored 1 = Extremely difficult, 2 = Somewhat difficult, 3 = Neither easy
##      nor difficult, 4 = Somewhat easy, 5 = Extremely easy (the source stores the answer
##      text; order from the authors' factor levels). Higher = easier.
##    rating_organize: "Which colonia(s) do you think the neighbors will organize?" (translated)
##      answered once per set with both / one / neither; stored per colonia, 1 = this colonia
##      named (alone or "Both"), 0 = not. Not a pick-one choice, hence a 0/1 rating.
##  chriswell_2023_organizing_formal (set 3): attr_problem and attr_neighbors_response as
##    above (no "No se organizaron" level; the monitoring text also appears with a doubled
##    space and with a doubled "para", stored as displayed), attr_group ("Crearon un grupo de
##    vecinos que se junta regularmente" / "Los vecinos se conocieron entre ellos"),
##    attr_result ("Gracias a sus esfuerzos, ..." / "A pesar de sus esfuerzos, ..." texts).
##    rating: difficulty of organizing "among themselves, without the government";
##    rating_government: difficulty of organizing "to ask the government for help";
##    same 1-5 coding (translated wording, authors' code comments).
##Task order: set 1 then set 2 as numbered by the authors (display order of the sets is not
##otherwise documented). Restrictions (yes): the private response and the result texts are
##conditional on the problem (see the stored levels). One respondent with English attribute
##text (user_language EN) answered no vignette question. One respondent answered all three
##sets but has no attribute values (not saved): dropped. Rows with no outcome are omitted
##(4 tasks in the pairs table keep only one colonia).
##Personal data in the deposit, dropped: location_latitude / location_longitude (Qualtrics),
##colonia of residence (colonia_name, cve_col, colonia_*_other free text), free-text answers;
##Qualtrics response_id re-keyed to integers (row order).
##Covariates: cov_gender (Female -> female, Male -> male, Non-binary / Other -> other, Prefer
##not to say -> NA), cov_age (typed; whole numbers 12-100 kept, the file holds 0, 0.39, 0.58;
##ages 12-17 occur and are kept as typed), cov_education (educ answer text, Spanish),
##cov_alcaldia (borough), cov_time_neighborhood, cov_know_neighbors, cov_housing_type,
##cov_housing_ownership, cov_pol_nat (national party coalition inclination; not party ID),
##answer text as stored. No survey weight.
##Check: mean ease rating is higher after a success result than a failure (pairs table
##3.0-3.1 vs 2.5) and lowest when neighbours did not organize (2.1); the article's numbers
##were not compared.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "cai_survey.Rdata"), envir = e)
s <- as.data.table(e$dat); s[, rid := .I]
stopifnot(nrow(s) == 1690)
lv <- c("Extremely difficult", "Somewhat difficult", "Neither easy nor difficult", "Somewhat easy", "Extremely easy")
code5 <- function(x) { x <- as.character(x); stopifnot(all(x %in% c(NA, lv))); match(x, lv) }
gmap <- c(Female = "female", Male = "male", "Non-binary" = "other", Other = "other", "Prefer not to say" = NA)
stopifnot(all(s$gender %in% c(NA, names(gmap))))
ch <- function(x) { x <- as.character(x); fifelse(x == "", NA_character_, x) }
cv <- s[, .(rid, cov_gender = unname(gmap[as.character(gender)]),
            cov_age = fifelse(!is.na(age) & age == round(age) & age >= 12 & age <= 100, as.integer(age), NA_integer_),
            cov_education = ch(educ), cov_alcaldia = ch(alcaldia), cov_time_neighborhood = ch(time_neighborhood),
            cov_know_neighbors = ch(know_neighbors), cov_housing_type = ch(housing_type),
            cov_housing_ownership = ch(housing_ownership), cov_pol_nat = ch(pol_nat))]
names_v <- list(c("Colonia Alcatraz", "Colonia Magnolia"), c("Colonia Dalia", "Colonia Orquídea"))
rows <- list()
for (t in 1:2) {
  org <- trimws(as.character(s[[paste0("c", t, "_3")]]))
  for (p in 1:2) {
    nm <- names_v[[t]][p]
    stopifnot(all(org %in% c(NA, names_v[[t]], paste("Both", names_v[[t]][1], "and", names_v[[t]][2]),
                             paste("Neither", names_v[[t]][1], "nor", names_v[[t]][2]))))
    rows[[length(rows) + 1]] <- data.table(rid = s$rid, task = t, profile = p,
      rating = code5(s[[paste0("c", t, "_", p)]]),
      rating_organize = fifelse(is.na(org), NA_integer_, as.integer(org == nm | startsWith(org, "Both"))),
      attr_problem = s[[sprintf("choice%d_prob1_%dA", t, p)]], attr_neighbors_response = s[[sprintf("choice%d_neighbors_%dA", t, p)]],
      attr_result = s[[sprintf("choice%d_resp2_%dA", t, p)]], trial_problem_asked = s[[sprintf("choice%d_prob2_1A", t)]])
  }
}
d12 <- rbindlist(rows)
d3 <- rbindlist(lapply(1:2, function(p) data.table(rid = s$rid, task = 1L, profile = p,
  rating = code5(s[[paste0("c3_", p)]]), rating_government = code5(s[[paste0("c3_", p + 2)]]),
  attr_problem = s[[paste0("choice1_prob1_", p)]], attr_neighbors_response = s[[paste0("choice1_neighbors_", p)]],
  attr_group = s[[paste0("choice1_resp1_", p)]], attr_result = s[[paste0("choice1_resp2_", p)]],
  trial_problem_asked = s$choice1_prob2_1)))
finish <- function(d, outs, name) {
  d <- d[d[, Reduce(`|`, lapply(.SD, function(v) !is.na(v))), .SDcols = outs]]
  ac <- grep("^attr_|^trial_", names(d), value = TRUE)
  miss <- d[, Reduce(`|`, lapply(.SD, function(v) is.na(v) | v == "")), .SDcols = ac]
  cat(name, "rows with an outcome but missing attribute text (dropped):", sum(miss), "\n")
  d <- d[!miss]
  stopifnot(d[, all(grepl("[áéíóúñ]|Problemas|aumento|vecinos|organizaron|crimen|agua|Crearon|Compartieron", get(ac[1])))])
  d <- merge(d, cv, by = "rid", sort = FALSE)
  ids <- sort(unique(d$rid)); d[, id := match(rid, ids)][, rid := NULL]
  setcolorder(d, c("id", "task", "profile", outs))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  cat(name, nrow(d), uniqueN(d$id), "\n")
}
finish(d12, c("rating", "rating_organize"), "chriswell_2023_organizing_pairs")
finish(d3, c("rating", "rating_government"), "chriswell_2023_organizing_formal")
