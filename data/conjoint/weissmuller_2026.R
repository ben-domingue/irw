##Cybercriminal legitimation-strategy choice experiment (Germany, UK) from
##Weißmüller, K. S., van den Broek, T. A., Kaufmann, A., & Watson, S. J. (2026). The dark side of
##legitimation: Experimental evidence on the effectiveness of discursive strategies used by cyber
##criminals [Data and codebook]. OSF. https://osf.io/64x73/ (project "Discrete Choice Experiment
##on the Effectiveness of Criminal Organizations' Legitimation Strategies"; no article DOI yet).
##Data: OSF doi:10.17605/OSF.IO/64X73, CC BY-NC 4.0 (node licence). Files read:
##"JUST2_GER_UK __for hypotheses testing.RData" (tibble JUST2_GER_UK, one row per respondent x
##choice set, both samples, loaded into its own environment), 2026_JUST2_DCE_german_DATASET_labels.dta
##and 2026_JUST2_DCE_uk_DATASET_numeric.dta (covariates only), 2026_CODEBOOK_DCE_JUST2.pdf (all
##vignette and question text). Read as text, not run: 2026_JUST2_DCE_uk/german_descriptive_ANALYSIS_KW.do.
##Usage: Rscript weissmuller_2026.R <dir holding those files> <output dir>
##
##Paired text-vignette choice experiment: after a scenario about a cyberattack on a national
##pharmaceutical wholesaler, each respondent saw 5 of 18 fixed choice sets of two scenarios
##("Scenario 1"/"Scenario 2"), each scenario = harm paragraph (3 levels) + media sentence (3) +
##the group's statement (11 legitimation strategies) + apology sentence (2). The 18 choice sets
##are a fixed design: the levels of both scenarios of every set are listed in the authors' .do
##files ("fill dummies for attribute levels per choicesets", identical in the UK and German .do),
##transcribed below; the RData stores only the CHOSEN scenario's levels, and those match the
##transcribed design in all 3,255 rows (task = 0 -> Scenario 1, 1 -> Scenario 2), which also
##fixes the profile order. Which 5 sets a respondent saw varies (not fixed blocks).
##Two tables, one per sample: the authors pool them for hypothesis tests, but the scenario text
##differs in language (German vs English), so the text cannot be shared:
##  weissmuller_2026_legitimation_de (Germany, April 2025, 301 respondents)
##  weissmuller_2026_legitimation_uk (UK, from 30 Sept 2025, 350 respondents)
##Article-level n in the OSF description: Germany n = 301 (1,505 obs), UK n = 350 (1,750): match.
##task = 1..5 in ascending choice-set number: the display order is NOT recorded (task_source
##inferred); trial_choiceset = the design's choice set (1-18).
##Outcomes (codebook wording):
##  choice: "Please compare the two scenarios. The two scenarios are independent from each other.
##          Based on the information you just read, please select the scenario in which the
##          group's activities seem more appropriate in your opinion." (German: "... legitimer
##          erscheinen"). Forced, no opt-out.
##  rating_responsible / rating_accountable / rating_punish: "Please indicate the degree to which
##          you agree with the following statements regarding your selection above:" "The hacker
##          group is responsible for / should be held legally accountable for / should be punished
##          for the harm associated with this incident." 1 Strongly disagree - 5 Strongly agree.
##          Asked about the chosen scenario only, so NA on the other profile.
##Attribute text: the codebook's vignette text in the language of the sample (page numbers and
##line breaks removed; the codebook's bracketed level codes dropped). The apology attribute's
##first level is "." in the codebook (no apology sentence shown) -> "(not shown)". The first
##media level is a sentence naming no outlet and stays as displayed text.
##Covariates: cov_gender (authors' female/male/diverse dummies; diverse -> other; checked against
##the German gender text), cov_age (authors' age, computed from birth year), cov_education
##(education_ger / education_uk answer text), cov_left_right (GER politics_left_right as stored,
##an 11-point slider whose midpoint is stored as "Mitte"; UK political_spectrum as stored),
##cov_realism (scenario realism 1-7, strongly disagree - strongly agree), cov_duration_sec
##(survey duration). Dropped: the authors' dummies and indices (harm_*, media_*, strategy_*,
##apology_*, strategy_cat, blame, md, psb, PD, lnPD, risk_averse, highered, ...), timestamps.
##No survey weight in the deposit. The attention check (27+3) was passed by everyone kept.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "JUST2_GER_UK __for hypotheses testing.RData"), envir = e)
s <- as.data.table(e$JUST2_GER_UK)
stopifnot(nrow(s) == 3255, s[, all(tasknumber == choiceset)], !anyNA(s[, .(task, resp, account, punitive)]))
## fixed design from the .do files: level index of Scenario 1 (A) and Scenario 2 (B) for choice sets 1..18
lv <- function(l) { x <- integer(18); for (k in names(l)) x[l[[k]]] <- as.integer(k); stopifnot(all(x > 0)); x }
D <- data.table(choiceset = 1:18,
  harm_A = lv(list(`1` = c(1,2,5,7,15), `2` = c(4,6,9,10,11,13,18), `3` = c(3,8,12,14,16,17))),
  harm_B = lv(list(`1` = c(3,4,6,8,14,17,18), `2` = c(1,2,5,12,16), `3` = c(7,9,10,11,13,15))),
  media_A = lv(list(`1` = c(2,5,6,8,9,15,16), `2` = c(1,3,4,7,11,13,17), `3` = c(10,12,14,18))),
  media_B = lv(list(`1` = c(1,11,12,13,14), `2` = c(2,6,9,10,18), `3` = c(3,4,5,7,8,15,16,17))),
  strategy_A = lv(list(`1` = c(13,16), `2` = c(3,15), `3` = c(5,12), `4` = c(6,7,8,18), `5` = 4, `7` = c(2,11,14), `8` = 10, `9` = 17, `11` = c(1,9))),
  strategy_B = lv(list(`1` = 3, `2` = 5, `3` = c(2,18), `5` = c(11,17), `6` = c(10,14,16), `8` = c(4,9,13), `9` = c(8,12), `10` = c(1,6,7), `11` = 15)),
  apology_A = lv(list(`1` = c(1,2,3,4,6,8,10,12,13,16), `2` = c(5,7,9,11,14,15,17,18))),
  apology_B = lv(list(`1` = c(5,7,8,9,12,14,17,18), `2` = c(1,2,3,4,6,10,11,13,15,16))))
m <- merge(s, D, by = "choiceset")
m[, task_chosen := as.integer(task) + 1L]
stopifnot(m[, all(fifelse(task == 0, harm == harm_A & media == media_A & strategy == strategy_A & apology == apology_A,
                                      harm == harm_B & media == media_B & strategy == strategy_B & apology == apology_B))])
## level text, codebook (UK pp. 12-13, German pp. 4-6)
uk_harm <- c(
  "Overall, the cyberattack caused minor societal harm. There were mild disruptions in the system, causing small delays in nonessential medication such as ibuprofen, cough medicine and nasal spray. This led to a handful of preventable visits to the general practitioner, but none of the patients experienced significant harm. You personally know of a close family member who felt the impact of these consequences.",
  "Overall, the cyberattack caused moderate societal harm. There were moderate disruptions in the system, causing significant delays in medication against allergies, asthma and high blood pressure. Several people required hospital admission who otherwise would not have, but no deaths were reported as a result. You personally know of a close family member who felt the impact of these consequences.",
  "Overall, the cyberattack caused significant societal harm. There were catastrophic disruptions in the system, causing extensive delays in critical medication, such as blood thinners, insulin, and chemotherapy medications. A large number of people were affected, directly resulting in a surge in hospital admissions and preventable deaths. You personally know of a close family member who felt the impact of these consequences.")
uk_media <- c(
  "You learned about the cyberattack because the group of cybercriminals provided a statement to justify their activity a few days after the incident:",
  "You learned about the cyberattack because the group of cybercriminals provided a statement to justify their activity a few days after the incident in a reputable national newspaper:",
  "You learned about the cyberattack because the group of cybercriminals provided a statement to justify their activity a few days after the incident through social media:")
uk_strategy <- c(
  "The statement was simply: “We do not comment!”",
  "“We demonstrated how easy it is to manipulate this system. The public should take it as a wake-up call. By showing how fragile this system is, we gave people the information they need to hold pharmaceutical companies accountable and demand a better system. This is really useful for society!”",
  "“We demonstrated how easy it is to manipulate this system. Compared to how fragile the drug distribution system is, our action really only caused some confusion and hardly caused any harm.”",
  "“We demonstrated how easy it is to manipulate this system. Like always, we followed the law by the book and complied with the best practices of ethical hacking at all times.”",
  "“We demonstrated how easy it is to manipulate this system. We are the only group with unique expert knowledge to expose the problems of the system. As the one and only authority of IT and cybersecurity, it was our task to intervene!”",
  "“We demonstrated how easy it is to manipulate this system. Cybersecurity breaches are a basic threat in today’s digitized business world. Systems are attacked all the time, what we did is really nothing special. The problems that followed had nothing to do with our activities, and were just business-as-usual.”",
  "“We demonstrated how easy it is to manipulate this system for the benefit of people. In a fair society that values accountability and openness, the public has the right to know how fragile the drug distribution system is. Our actions ensured that people gained access to the truth that was being unfairly concealed.”",
  "“We demonstrated how easy it is to manipulate this system. Hospitals and pharmacies deliberately chose to rely on an inherently flawed inventory system without having any backups in place. Any harm is their own fault because it was their decision to take these risks for cost-cutting, so these issues are entirely their responsibility, not ours.”",
  "“We demonstrated how easy it is to manipulate this system. The government and regulators have failed to enforce the development of a secure medicine supply chain. For them to criticise our actions having let this situation develop is hypocrisy.”",
  "“We demonstrated how easy it is to manipulate this system. Transparency is our core value in everything we do. To clear everything up, we are now making our internal discussions, motivations, and procedures available for public review, proving that our intentions were never malicious. This transparency will leave no doubt that our actions were meant to inform, not to harm.”",
  "“We demonstrated how easy it is to manipulate this system. However, our group did not intend to cause any harm. The harm caused was the result of a reckless act by a small rogue group of individuals who completely violated our values. They were removed immediately from our group. The rest of us are committed to constructive, non-disruptive efforts for the benefit of society. We should not be blamed for the failures of a few outlaws.”")
uk_apology <- c(
  ".",
  "“We never meant to harm people, and we sincerely apologize to everyone affected.”")
de_harm <- c(
  "Insgesamt verursachte der Cyberangriff geringe gesellschaftliche Schäden. Es gab leichte Störungen im System, die zu kleinen Verzögerungen bei der Versorgung mit nicht lebensnotwendigen Medikamenten wie Ibuprofen, Hustensaft und Nasenspray führte. Dies führte zu einer Handvoll vermeidbarer Arztbesuche, aber keiner der Patienten erlitt ernsthafte langfristige Schäden. Sie persönlich kennen ein enges Familienmitglied, das betroffen war.",
  "Insgesamt verursachte der Cyberangriff mittelschwere gesellschaftliche Schäden. Es gab mittelschwere Störungen im System, die zu erheblichen Verzögerungen bei der Versorgung mit Medikamenten gegen Allergien, Asthma und Bluthochdruck führten. Mehrere Personen mussten ins Krankenhaus eingeliefert werden, die andernfalls nicht dort gewesen wären, aber der Angriff verursachte keine Todesfälle. Sie persönlich kennen ein enges Familienmitglied, das betroffen war.",
  "Insgesamt verursachte der Cyberangriff erhebliche gesellschaftliche Schäden. Es gab katastrophale Störungen im System, die zu umfangreichen Verzögerungen bei der Versorgung mit kritischen Medikamenten wie Blutverdünnern, Insulin und Chemotherapie-Medikamenten führten. Eine große Anzahl von Menschen war betroffen, was zum direkten Anstieg der Krankenhauseinweisungen und vermeidbaren Todesfällen führte. Sie persönlich kennen ein enges Familienmitglied, das betroffen war.")
de_media <- c(
  "Sie haben von dem Cyberangriff erfahren, weil die cyberkriminelle Gruppe einige Tage nach dem Vorfall eine Erklärung abgegeben hat, um ihre Aktivitäten zu rechtfertigen:",
  "Sie haben von dem Cyberangriff erfahren, weil die cyberkriminelle Gruppe einige Tage nach dem Vorfall in einer renommierten nationalen Zeitung eine Erklärung veröffentlichte, um ihre Aktivitäten zu rechtfertigen:",
  "Sie haben von dem Cyberangriff erfahren, weil die cyberkriminelle Gruppe einige Tage nach dem Vorfall in den sozialen Medien eine Erklärung veröffentlichte, um ihre Aktivitäten zu rechtfertigen:")
de_strategy <- c(
  "Die Erklärung lautete einfach: „Kein Kommentar!”",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren. Das ist ein Weckruf für alle! Indem wir gezeigt haben, wie anfällig dieses System ist, haben wir den Menschen endlich die notwendigen Informationen gegeben um pharmazeutische Unternehmen zur Verantwortung zu ziehen und ein besseres System zu fordern. Das ist sehr nützlich für die Gesellschaft!”",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren. Im Vergleich dazu, wie instabil das Medikamentenverteilungssystem ist, hat unsere Aktion bloß ein bisschen Verwirrung gestiftet, und kaum Schaden angerichtet.”",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren. Wie immer haben wir uns an alle Gesetze gehalten und auch bei dieser Aktion nur ethisches Hacking betrieben.”",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren. Nur unsere Gruppe hat das nötige Expertenwissen um die Probleme des Systems aufzudecken. Wegen unserer Autorität in Sachen IT und Cybersicherheit mussten wir einfach eingreifen!“",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren. Cyberangriffe sind eine tagtägliche Bedrohung in der heutigen digitalisierten Unternehmenswelt. Systeme werden ständig angegriffen, das ist wirklich nichts Besonderes. Die Probleme, die im Nachhinein auftraten, hatten nichts mit unserer Aktion zu tun, es hätte alles so wie normal weiterlaufen sollen.”",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren, und zwar zum Wohle der Gesellschaft! In einem fairen und transparenten System hat die Öffentlichkeit das Recht zu erfahren wie fragil das System ist, auf dem die Verteilung von Medikamenten beruht. Unsere Aktion hat sichergestellt, dass die Menschen jetzt die Wahrheit kennen, jetzt kann nichts mehr verschleiert werden.”",
  "„Wir haben gezeigt, wie einfach es ist, dieses System zu manipulieren. Krankenhäuser und Apotheken haben sich bewusst dazu entschlossen, ein komplett mangelhaftes System zu nutzen, ohne jegliche Backups. Mögliche Schäden sind allein auf ihrem Mist gewachsen! Es war ihre Entscheidung, dieses Risiko einzugehen um Kosten zu sparen, daher liegen die Konsequenzen vollständig in ihrer Verantwortung, nicht in unserer.”",
  "„Wir haben offen gezeigt, wie einfach es ist, dieses System zu manipulieren. Die Regierung hat darin versagt, eine sichere Lieferkette für Medikamente zu gewährleisten. Uns für ihr grob fahrlässiges Verhalten zu beschuldigen ist komplett scheinheilig!”",
  "„Wir haben offen gezeigt, wie einfach es ist, dieses System zu manipulieren. Transparenz ist unser wichtigster Wert bei allem, was wir tun. Darum veröffentlichen wir jetzt alle unsere internen Diskussionen, Motivationen und Verfahren, um zu zeigen, dass wir keine bösen Absichten hatten. Diese Offenheit wird eindeutig beweisen, dass unsere Aktion die Leute nur informieren sollte, nicht schädigen.”",
  "„Wir haben offen gezeigt, wie einfach es ist, dieses System zu manipulieren. Allerdings hatten wir als Gruppe nie vor jemandem zu schaden. Die Probleme, die entstanden sind, gingen von einer kleinen Gruppe aus, die eigenmächtig und rücksichtslos gehandelt hat und unsere Kernwerte völlig missachtet hat. Diese Personen wurden sofort aus unserer Gruppe ausgeschlossen. Der Rest von uns setzt sich weiterhin für konstruktive Aktionen zum Wohl der Gesellschaft ein. Wir sollten nicht für die Fehltritte einiger weniger schwarzer Schafe verantwortlich gemacht werden.”")
de_apology <- c(
  ".",
  "„Wir hatten nie vor, Menschen zu verletzen, und entschuldigen uns aufrichtig bei allen Betroffenen.”")
uk_apology[1] <- "(not shown)"; de_apology[1] <- "(not shown)"
stopifnot(length(uk_strategy) == 11, length(de_strategy) == 11, lengths(list(uk_harm, uk_media, de_harm, de_media)) == 3)
g <- as.data.table(read_dta(file.path(raw, "2026_JUST2_DCE_german_DATASET_labels.dta")))
u <- unique(as.data.table(read_dta(file.path(raw, "2026_JUST2_DCE_uk_DATASET_numeric.dta")))[, .(id, education_uk, political_spectrum, Durationinseconds)])
stopifnot(nrow(g) == 301, nrow(u) == 350, uniqueN(u$id) == 350)
for (cc in c("de", "uk")) {
  x <- m[Sample == c(de = "Germany", uk = "UK")[cc]]
  L <- get(paste0(cc, "_harm")); M <- get(paste0(cc, "_media")); St <- get(paste0(cc, "_strategy")); Ap <- get(paste0(cc, "_apology"))
  setorder(x, id, choiceset); x[, task := NULL]; x[, tk := seq_len(.N), id]
  r <- rbindlist(lapply(1:2, function(p) {
    sfx <- c("A", "B")[p]
    x[, .(id = as.integer(id), task = tk, profile = p, choice = as.integer(task_chosen == p),
          rating_responsible = fifelse(task_chosen == p, as.integer(resp), NA_integer_),
          rating_accountable = fifelse(task_chosen == p, as.integer(account), NA_integer_),
          rating_punish = fifelse(task_chosen == p, as.integer(punitive), NA_integer_),
          attr_harm = L[get(paste0("harm_", sfx))], attr_media = M[get(paste0("media_", sfx))],
          attr_statement = St[get(paste0("strategy_", sfx))], attr_apology = Ap[get(paste0("apology_", sfx))],
          trial_choiceset = as.integer(choiceset),
          cov_gender = fifelse(female == 1, "female", fifelse(male == 1, "male", fifelse(diverse == 1, "other", NA_character_))),
          cov_age = as.integer(age), cov_realism = as.integer(realism))]
  }))
  if (cc == "de") {
    stopifnot(all(merge(unique(x[, .(id, female)]), g[, .(id, gender)], by = "id")[, (female == 1) == (gender == "Weiblich")]))
    cv <- g[, .(id = as.integer(id), cov_education = fifelse(education_ger == "", NA_character_, education_ger),
                cov_left_right = fifelse(politics_left_right == "", NA_character_, politics_left_right),
                cov_duration_sec = as.integer(Durationinseconds))]
  } else cv <- u[, .(id = as.integer(id), cov_education = fifelse(education_uk == "", NA_character_, education_uk),
                     cov_left_right = as.character(political_spectrum), cov_duration_sec = as.integer(Durationinseconds))]
  r <- merge(r, cv, by = "id", all.x = TRUE)
  stopifnot(r[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(r[, .(attr_harm, attr_media, attr_statement, attr_apology)]),
            r[choice == 1, all(rating_responsible %in% 1:5 & rating_accountable %in% 1:5 & rating_punish %in% 1:5)])
  setorder(r, id, task, profile)
  fwrite(r, file.path(out, sprintf("weissmuller_2026_legitimation_%s.csv", cc)))
}
