##Asylum-seeker conjoint (15 European countries) from
##Bansak, K., Hainmueller, J., & Hangartner, D. (2016). How economic, humanitarian, and
##religious concerns shape European attitudes toward asylum-seekers. Science, 354(6309),
##217-222. https://doi.org/10.1126/science.aag2147
##Replication data: Harvard Dataverse doi:10.7910/DVN/KL0FDF, CC0 1.0. Files read:
##conjoint_data_final.csv and respondent_data_final.csv (Dataverse "original format"
##downloads), with conjoint_variable_codebook.pdf and respondent_variable_codebook.pdf
##for the level labels. ConjointRegressions.R was read as text, not run.
##Usage: Rscript bansak_2016.R <dir holding the two .csv files> <output dir>
##
##bansak_2016_asylum: online survey of eligible voters in 15 European countries (Austria,
##  Czech Republic, Denmark, France, Germany, Greece, Hungary, Italy, Netherlands, Norway,
##  Poland, Spain, Sweden, Switzerland, United Kingdom; about 1,200 each), fielded 2016.
##  ONE TABLE with cov_country: the same design (same 9 attributes and levels, translated)
##  was fielded in every country, and the deposit stores only the English master labels,
##  so splitting by country would not change what attr_* hold. Each respondent saw 5
##  pairs of asylum-seeker profiles (10 profiles; source "mix" A..J = task 1 profile 1,
##  task 1 profile 2, task 2 profile 1, ...). attr_* hold the codebook's English level
##  labels; the language attribute was shown with the respondent's national language in
##  place of the codebook's "[language of respondent's country]", which is kept verbatim
##  because the deposit does not say which language was named in multilingual countries.
##  The deposit does not record attribute order or document randomization restrictions.
##  Outcomes: choice = pref (1 = the preferred profile of the pair; forced choice, no
##  opt-out) and rating = rate (1-7 "degree of support" for granting asylum, per the
##  codebook; higher = more supportive, raw scale kept). The exact question wording is in
##  the article's Supplementary Materials, which are not in the deposit and were not
##  retrieved. The authors' derived ratebin and ratescaled are dropped.
##  9 respondents (90 profiles) have no attribute levels at all in the deposit and are
##  dropped (the authors drop them too), leaving 18,021 respondents; the paper reports
##  18,000 voters (a round number) and 180,000 profiles.
##  Covariates: cov_country (text), cov_survey_weight (entropy-balancing post-stratification
##  weight, NA for 147 respondents with missing education; the authors top-code it at 6
##  for analysis, it is kept raw here), cov_home_born (1 = born in country), cov_asylum_home
##  (-2 greatly decrease ... 2 greatly increase the number granted asylum), cov_ideology
##  (0 left - 10 right), cov_party_id (party of identification, as the text of the
##  country-specific answer option, in the national language as listed under "Party codes"
##  in respondent_variable_codebook.pdf; the codes run 1..k per country and every country's
##  range matches the codebook list; includes each country's "Other" and "no party" option),
##  cov_empathy1 (empathic concern, -6..6), cov_empathy2 (perspective taking, -6..6),
##  cov_gender (female/male, from Female, "indicator for being female" in the respondent
##  codebook: 1 = female, 0 = male; no other option recorded), cov_age (years; codebook
##  "Age - self-reported age"), cov_employment (1 paid
##  employee, 2 self-employed, 3 student, 4 unemployed searching, 5 unemployed not
##  searching, 6 chronic illness/disability, 7 retired, 8 working at home), cov_eisced
##  (education, European ISCED level 1-7 as coded by the authors; the deposit gives no
##  labels for the levels, so it keeps its code and its name), cov_income_decile.
##  Dropped: Qualtrics respid (re-keyed to the deposit's integer id), survey duration, the
##  party's Chapel Hill placement (lrgen, an external score), and derived bins/dummies/
##  counts (L/C/R, Ideo5, OldAge, AgeGroup, HighEducation, Empathy sum, NAsySeek*, Cat*).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
cj <- fread(file.path(raw, "conjoint_data_final.csv")); rs <- fread(file.path(raw, "respondent_data_final.csv"))
cj <- cj[!is.na(cconsist)]
k <- match(cj$mix, LETTERS[1:10]); stopifnot(!anyNA(k))
d <- data.table(id = as.integer(cj$id), task = (k + 1L) %/% 2L, profile = 2L - k %% 2L,
                choice = as.integer(cj$pref), rating = as.integer(cj$rate))
labs <- list(
  consistency = c("No inconsistencies", "Minor inconsistencies", "Major inconsistencies"),
  gender = c("Female", "Male"),
  origin = c("Syria", "Afghanistan", "Kosovo", "Eritrea", "Pakistan", "Ukraine", "Iraq"),
  age = c("21 years", "38 years", "62 years"),
  occupation = c("Unemployed", "Cleaner", "Farmer", "Accountant", "Teacher", "Doctor"),
  vulnerability = c("None", "Post-traumatic stress disorder (PTSD)", "Victim of torture", "No surviving family members", "Physically handicapped"),
  reason = c("Persecution for political views", "Persecution for religious beliefs", "Persecution for ethnicity", "Seeking better economic opportunities"),
  religion = c("Christian", "Agnostic", "Muslim"),
  language = c("Speaks fluent [language of respondent's country]", "Speaks broken [language of respondent's country]", "Speaks no [language of respondent's country]"))
src <- c(consistency = "cconsist", gender = "cgender", origin = "corigin", age = "cage", occupation = "cjob",
         vulnerability = "cvulner", reason = "creason", religion = "creligion", language = "clang")
for (v in names(src)) { x <- labs[[v]][cj[[src[[v]]]]]; stopifnot(!anyNA(x)); d[, paste0("attr_", v) := x] }
pty <- list(  # respondent_variable_codebook.pdf, "Party codes", in code order 1..k
  "United Kingdom" = c("Conservative Party", "Labour Party", "United Kingdom Independence Party", "The British National Party", "Scottish National Party", "Plaid Cymru - Party of Wales", "Liberal Democrats Party", "Green Party", "Sinn Féin", "Democratic Unionist Party", "Ulster Unionist Party / Conservative & Ulster Unionist Alliance", "Social Democratic & Labour Party", "Other", "No Party"),
  Germany = c("Christlich Demokratische Union (CDU) / Christlich Soziale Union (CSU)", "Sozialdemokratische Partei Deutschlands (SPD)", "Bündnis 90 / Die Grünen (Grüne)", "Die Linke (Linke)", "Freie Demokratische Partei Deutschlands (FDP)", "Piratenpartei Deutschland (Piraten)", "Alternative für Deutschland (AfD)", "Familien-Partei Deutschland", "Freie Wähler (FW)", "Nationaldemokratische Partei Deutschlands (NPD)", "Ökologisch-Demokratische Partei (ÖDP)", "Partei Bibeltreuer Christen (PBC)", "Die Republikaner (REP)", "Partei Mensch Umwelt Tierschutz (Tierschutzpartei)", "Sonstige", "Nein, Sie stehen keiner Partei nahe"),
  Austria = c("Sozialdemokratische Partei Österreichs (SPÖ)", "Österreichische Volkspartei (ÖVP)", "Freiheitliche Partei Österreichs (FPÖ)", "Bündnis Zukunft Österreich (BZÖ)", "Die Grünen – Die grüne Alternative", "Kommunistische Partei Österreichs (KPÖ)", "Piratenpartei", "Der Wandel", "NEOS - Das neue Österreich", "Die Reformkonservativen – REKOS", "Sonstige", "Nein, Sie stehen keiner Partei nahe"),
  Switzerland = c("Union démocratique du centre (UDC)", "Parti socialiste (PS)", "PLR. Les Libéraux-Radicaux", "Parti démocrate-chrétien (PDC)", "Les Verts (PES)", "Parti vert liberal (PEL // PVL)", "Parti bourgeois démocrate (PBD)", "Parti évangélique populaire (PEV)", "Union démocratique fédérale (UDF)", "Lega dei Ticinesi", "Parti du travail (PdT) / Parti ouvrier populaire (POP)", "Mouvement des Citoyens Romands", "Sonstige / Autre", "Nein, Sie stehen keiner Partei nahe / Non, vous ne vous sentez pas proche d’un parti politique"),
  France = c("Union des Démocrates et Indépendants, Mouvement Démocrate (UDI / MoDem)", "Nouveau Parti anticapitaliste (NPA)", "Front de Gauche (FdG) (Parti communiste ou Parti de Gauche)", "Parti Socialiste (PS)", "Parti radical de gauche", "Europe Ecologie - Les Verts (EELV)", "Lutte ouvrière (LO)", "Union pour un Mouvement Populaire (UMP)", "Front national (FN)", "Debout la République (DLR)", "Union pour les Outre-Mer", "Alliance des régionalistes, écologistes et progressistes des Outre-Mer régions et peuples solidaires", "Nouvelle Donne", "Autre", "Non, vous ne vous sentez pas proche d’un parti politique"),
  Italy = c("Italia dei Valori - Di Pietro", "Lega Nord", "Partito Democratico", "Forza Italia", "Nuovo Centrodestra", "Unione dei Democratici Cristiani e Democratici di Centro (UDC)", "Popolari per l'Italia", "Fratelli d'Italia - Alleanza Nazionale", "Scelta Civica", "Centro Democratico", "Movimento Cinque Stelle", "Südtiroler Volkspartei (Partito popolare sudtirolese)", "Sinistra Ecologia e Liberta", "Altro", "No, non mi sento vicino a nessun partito politico in particolare"),
  Spain = c("PSOE - Partido Socialista Obrero Español / Partit dels Socialistes de Catalunya", "PP - Partido Popular", "IU - Izquierda Unida", "ICV - Iniciativa per Catalunya Verds", "ANOVA - Irmandade Nacionalista", "UPyD - Unión Progreso y Democracia", "CDC - Convergència Democràtica de Catalunya", "EAJ-PNV - Partido Nacionalista Vasco", "Unió - Unió Democràtica de Catalunya", "CC - Coalición Canaria", "CxG - Compromiso por Galicia", "ERC - Esquerra Republicana de Catalunya", "NECat - Nova Esquerra Catalana", "BNG - Bloque Nacionalista Galego", "EH Bildu - Euskal Herria Bildu", "Equo", "Ciudadanos - Partido de la Ciutadanía", "VOX", "Podemos", "Otro", "No, no se considera próximo/a a ningún partido"),
  Denmark = c("A. Socialdemokratiet", "B. Det Radikale Venstre", "C. Det Konservative Folkeparti", "F. Socialistisk Folkeparti (SF)", "O. Dansk Folkeparti", "I. Liberal Alliance", "V. Venstre, Danmarks liberale parti", "K. Kristendemokraterne", "Ø. Enhedslisten - de rød-grønne", "Andet", "Nej, du føler ikke, at dine holdninger ligger tæt op ad et af de politiske partier?"),
  Sweden = c("Vänsterpartiet", "Socialdemokraterna", "Centerpartiet", "Folkpartiet liberalerna", "Moderata Samlingspartiet", "Kristdemokraterna", "Miljöpartiet de gröna", "Sverigedemokraterna", "Feministiskt initiativ", "Piratpartiet", "Annat", "Nej, du anser dig inte stå nära något politiskt parti"),
  Greece = c("Νέα Δημοκρατία", "Πανελλήνιο Σοσιαλιστικό Κίνημα", "Κομμουνιστικό Κόμμα Ελλάδας", "Συνασπισμός Ριζοσπαστικής Αριστεράς", "Λαϊκός Ορθόδοξος Συναγερμός -Γ. Καρατζαφέρης", "Οικολόγοι Πράσινοι", "Χρυσή Αυγή", "Ανεξάρτητοι Έλληνες", "Δημοκρατική Αριστερά", "Το Ποτάμι", "Άλλο", "Όχι, δεν συµµερίζεστε τις απόψεις κανενός πολιτικού κόµµατος"),
  Netherlands = c("Christen Democratisch Appèl", "Partij van de Arbeid", "Socialistische Partij", "Volkspartij voor Vrijheid en Democratie", "GroenLinks", "Partij voor de Vrijheid", "ChristenUnie - Staatkundig Gereformeerde Partij", "Democraten 66", "Partij voor de Dieren", "50Plus", "Anders", "Nee, u voelt zich niet verbonden met één bepaalde politieke partij"),
  "Czech Republic" = c("Občanská demokratická strana", "Česká strana sociálně demokratická", "Komunistická strana Čech a Moravy (KSČM)", "Křesťanská a demokratická unie – Československá strana lidová", "Věci veřejné", "TOP 09", "ANO 2011", "Strana zelených", "Úsvit přímé demokracie", "Česká pirátská strana", "Strana svobodných občanů", "Národní socialisté – levice 21. století", "STAN (Starostové a nezávislí)", "Hlavu vzhůru - volební blok", "Strana práv občanů", "Dělnická strana", "Republika", "Romská demokratická strana", "SNK Evropští demokraté", "Strana zdravého rozumu - nechceme euro - za Evropu svobodných států", "Úsvit přímé demokracie Tomia Okamury", "VIZE 2014", "Volte Pravý Blok - www.cibulka.net", "Jiné", "Ne, žádná politická strana vám nepřijde blízká"),
  Hungary = c("Együtt 2014 - Párbeszéd Magyarországért", "Magyar Szocialista Párt", "Demokratikus Koalíció", "Fidesz - Magyar Polgári Szövetség - Keresztény Demokrata Néppárt", "Jobbik Magyarországért Mozgalom", "Lehet Más a Politika", "Egyéb", "Nem, nem érzi magát közelinek egy politikai párthoz sem"),
  Norway = c("Rødt", "Sosialistisk Venstreparti", "Det Norske Arbeiderparti", "Venstre", "Kristelig Folkeparti", "Senterpartiet", "Høyre", "Fremskrittspartiet", "Kystpartiet", "Miljøpartiet De Grønne", "Andre partier/lister", "NEI"),
  Poland = c("Prawo i Sprawiedliwość", "Nowoczesna", "Platforma Obywatelska", "Kukiz’15", "Polskie Stronnictwo Ludowe", "Sojusz Lewicy Demokratycznej", "Partia Razem", "Polska Razem", "Solidarna Polska", "Kongres Nowej Prawicy", "Koalicja Odnowy Rzeczypospolitej Wolność i Nadzieja", "Unia Pracy", "Inne", "Nie, żadna partia polityczna nie jest Panu(i) bliska"))
stopifnot(setequal(names(pty), rs$cty), rs[, all(PartyID >= 1 & PartyID <= lengths(pty)[cty])])
rs[, party_txt := mapply(function(cc, k) pty[[cc]][k], cty, PartyID)]
stopifnot(all(rs$Female %in% 0:1))
r <- rs[, .(id, cov_country = cty, cov_survey_weight = weight, cov_home_born = HomeBorn, cov_asylum_home = AsylumHome,
            cov_ideology = IdeoScale, cov_party_id = party_txt, cov_empathy1 = Empathy1, cov_empathy2 = Empathy2,
            cov_gender = c("male", "female")[Female + 1L], cov_age = Age, cov_employment = as.integer(sub("\\..*", "", EmpStatus)),
            cov_eisced = EISCED, cov_income_decile = IncomeDecile)]
stopifnot(!anyNA(r$cov_employment), uniqueN(r$id) == nrow(r))
d <- merge(d, r, by = "id", all.x = TRUE); stopifnot(!anyNA(d$cov_country))
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bansak_2016_asylum.csv"))
