##Visions for the development of Siechnice (Poland): discrete choice experiment with an opt-out, paper survey
##Błaszczyk, M., & Krysiński, D. (2025). Siechnice Urban Development Preferences Survey 2025 -- Replication Data [Data set].
##RODBUK Cracow Open Research Data Repository. (The README cites "Siechnice CBC Survey Data" 2024; no paper DOI listed.)
##Deposit: doi:10.34616/4CMFXK (uwr.rodbuk.pl, a Dataverse installation), CC0 1.0 (record licence field and README), no restricted files.
##Files read: siechnice_dane_long.tab (saved as long.tab; the deposit's siechnice_dane_long.csv), 00_README.txt, the Block 1
##questionnaire PDF (pdftotext; displayed card text) and SIECHNICE_PLAN_EKSPERYMENTU.csv (design: not needed to build).
##Usage: Rscript blaszczyk_2025.R <dir holding long.tab> <output dir>
##
##384 adult residents of Siechnice (a satellite town of Wroclaw), paper-and-pencil interviews by trained interviewers (IPC
##research institute), 2024. Each respondent did 12 choice tasks: development vision A, vision B, or "none of the above -- I prefer
##the natural development of the town" (the fixed opt-out; it has no attributes, so it is not a profile: opt_out = yes). Vision =
##5 attributes with 4 levels each (5 for the first): city direction, public-investment priority, spatial development (housing
##form), social-policy priority, environment approach. Fixed blocked design generated with R idefix (D-error 0.090): 24 profiles
##(cards), 5 questionnaire blocks of 12 tasks each, every respondent in one block (blok; 75-80 respondents per block).
##Levels: the data file stores short Polish keyword labels (e.g. "Specjalistyczny"); the text respondents saw is the full sentence
##on each card of the Block 1 questionnaire PDF, so attr_ stores that sentence, mapped from the keyword (verified one sentence per
##keyword across the 24 cards; the exception is that cards 21 and 24 print a shortened sentence for the levels "Usługi zdrowotne"
##and "Rezydencjalny": the full variant used on the other cards is stored). Attribute names are the questionnaire's, in English
##here. Blocks 2-5 are said to use the same card set. Hyphens broken by line wrap in the pdf were restored by hand (two words).
##Outcome: choice = wybor on alternatives 1 and 2 (1 = chosen; 0 on both profiles when the opt-out was chosen: 394 of 4,608 tasks).
##Question: "Która wizja rozwoju Siechnic byłaby według Państwa lepsza? Wizja A / Wizja B / Żadna z powyższych - wolę naturalny rozwój
##miasta" (Which vision for the development of Siechnice would be better in your view?). profile = alternative position (1 = A, 2 = B).
##Dropped: the opt-out rows (alternatywa 3), the status_quo flag, the profile/card id. Demographic and metropolitan-orientation
##items are not in the deposit (held back by the authors). The respondent id (block_respondent) is re-keyed to integers; no PII.
##Restrictions: the authors state none; a blocked design means some pairs of levels never co-occur within a block (observed).
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lv1 <- c(
  "Lokalny" = "Miasto priorytetowo wspiera rozwój małych i średnich firm zakładanych przez mieszkańców, dążąc do jak największej autonomii i samowystarczalności.",
  "Przemysłowy" = "Miasto aktywnie przyciąga i wspiera na swoim terenie duże, zewnętrzne firmy produkcyjne i logistyczne, tworząc nowe strefy przemysłowe.",
  "Rezydencjalny" = "Miasto rozwija się jako spokojne miejsce do życia z dobrym dostępem do usług metropolitalnych Wrocławia. Polityka miasta wspiera głównie wysokiej jakości budownictwo mieszkaniowe i podstawowe, lokalne usługi.",
  "Specjalistyczny" = "Miasto specjalizuje się w branży medycznej, stając się regionalnym centrum oferującym zaawansowane usługi medyczne i opiekuńcze.",
  "Usługowy" = "Miasto stawia na rozwój szerokiej oferty handlowo-usługowej, stając się ponadlokalnym centrum, które częściowo konkuruje, a częściowo uzupełnia ofertę Wrocławia.")
lv2 <- c(
  "Obiekty usługowe" = "Priorytetem jest budowa jednego lub kilku dużych, centralnych obiektów użyteczności publicznej, np. nowoczesnej hali sportowo-widowiskowej czy aquaparku.",
  "Połączenia z Wrocławiem" = "Główny nacisk kładziony jest na infrastrukturę transportową -- remonty i budowę nowych dróg oraz zwiększenie częstotliwości połączeń kolejowych z Wrocławiem.",
  "Przestrzenie publiczne" = "Inwestycje koncentrują się na poprawie jakości życia wewnątrz miasta -- tworzeniu i modernizacji miejsc spotkań dla mieszkańców, takich jak parki, skwery, place zabaw czy rynek.",
  "Tereny przemysłowe" = "Pieniądze publiczne inwestowane są w przygotowanie infrastruktury na nowych terenach przeznaczonych dla fabryk i firm, aby przyciągnąć zewnętrznych inwestorów.")
lv3 <- c(
  "Budynki wielorodzinne" = "Promowany jest rozwój miasta w oparciu o gęstą zabudowę wielorodzinną (bloki 4-5 piętrowe), co pozwala na efektywne wykorzystanie terenu.",
  "Domy jednorodzinne" = "Miasto aktywnie udostępnia i uzbraja nowe działki budowlane z przeznaczeniem dla osób prywatnych, które chcą samodzielnie wybudować dom jednorodzinny.",
  "Rewitalizacja" = "Główny nacisk kładzie się na rewitalizację historycznej zabudowy poprzemysłowej i mieszkalnej „starych\" Siechnic, by ożywić te tereny, zachowując ich klimat i charakter.",
  "Zabudowa zwarta" = "Preferuje się budowę zorganizowanych osiedli o niższej, ale wciąż zwartej zabudowie, takich jak domy w zabudowie szeregowej czy bliźniaczej.")
lv4 <- c(
  "Młode rodziny" = "Miasto koncentruje swoje działania i budżet na zapewnieniu jak najlepszych warunków dla rodzin z małymi dziećmi (budowa żłobków, przedszkoli, szkół).",
  "Oferta kulturalna" = "Priorytetem jest wspieranie lokalnych artystów, organizacji pozarządowych (NGO) oraz finansowanie szerokiej gamy wydarzeń kulturalnych.",
  "Partycypacja społeczna" = "Polityka społeczna skupia się na tworzeniu narzędzi i programów, które aktywizują mieszkańców i wspierają ich własne pomysły (np. budżet obywatelski).",
  "Usługi zdrowotne" = "Miasto skupia się na zapewnieniu wsparcia seniorom i osobom z potrzebami zdrowotnymi (inwestuje w dzienny dom opieki, usługi opiekuńcze).")
lv5 <- c(
  "Maksymalizacja zieleni" = "Ochrona istniejącej przyrody i tworzenie nowych terenów zielonych jest absolutnym priorytetem, nawet jeśli oznacza to rezygnację z niektórych inwestycji.",
  "Priorytet gospodarczy" = "Najważniejszy jest szybki rozwój gospodarczy i tworzenie miejsc pracy, nawet jeśli odbywać ma się kosztem ochrony środowiska przyrodniczego.",
  "Rekultywacja terenów" = "Działania pro-środowiskowe koncentrują się na naprawianiu szkód i przywracaniu zieleni na terenach już zdegradowanych (np. po hucie).",
  "Zrównoważone podejście" = "Rozwój gospodarczy i ochrona zieleni są równie ważne, a nowe inwestycje są realizowane z poszanowaniem dla przyrody.")
x <- fread(file.path(raw, "long.tab"), encoding = "UTF-8")
x <- x[!is.na(respondent_id)]
stopifnot(nrow(x) == 13824, uniqueN(x$respondent_id) == 384, x[alternatywa == 3, all(status_quo == 1)],
          x[, .(ch = sum(wybor)), by = .(respondent_id, zadanie)][, all(ch == 1)])
p <- x[alternatywa < 3]
stopifnot(nrow(p) == 9216, !anyNA(p[, .(atr1, atr2, atr3, atr4, atr5)]), all(p$atr1 %in% names(lv1)), all(p$atr2 %in% names(lv2)),
          all(p$atr3 %in% names(lv3)), all(p$atr4 %in% names(lv4)), all(p$atr5 %in% names(lv5)))
rk <- unique(p[, .(respondent_id, blok)])
rk <- rk[order(blok, as.integer(sub("_.*", "", respondent_id)))]
rk[, id := .I]
d <- merge(p, rk[, .(respondent_id, id)], by = "respondent_id")
d <- d[, .(id, task = zadanie, profile = alternatywa, choice = wybor,
           attr_city_direction = unname(lv1[atr1]), attr_public_investment = unname(lv2[atr2]),
           attr_spatial_development = unname(lv3[atr3]), attr_social_policy = unname(lv4[atr4]),
           attr_environment = unname(lv5[atr5]), trial_block = blok)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "blaszczyk_2025_siechnice_development.csv"))
