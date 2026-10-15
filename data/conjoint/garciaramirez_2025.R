##Pedestrian crossing choice in Ecuador, two visual discrete choice experiments, from the Zenodo deposit "Dataset and R
##Script for Visual Discrete Choice Experiments on Pedestrian Crossing Behavior in Ecuador" (Garcia-Ramirez).
##Deposit: doi:10.5281/zenodo.17794518 (concept doi 10.5281/zenodo.17794517), CC BY 4.0 (record licence cc-by-4.0).
##No article identified (the deposit names none). Files read: Data.xlsx (sheets Experimento1, Experimento2) and the R script
##in "Script 02-11-2025_Cities.docx" (read as text via pandoc, never run) for the scenario attributes and the alternative coding.
##Usage: Rscript garciaramirez_2025.R <dir holding Data.xlsx> <output dir>
##
##Two tables, one per experiment (the deposit/script treat them as two experiments with different images and estimate them
##separately; they are different samples):
##  garciaramirez_2025_crossing_noncompliant = Experimento1 (483 respondents; images show NON-compliant pedestrian behaviour)
##  garciaramirez_2025_crossing_compliant    = Experimento2 (392 respondents; images show COMPLIANT behaviour)
##(Zenodo description). The images themselves are not in the deposit.
##Design: FIXED design, all respondents saw the same 6 scenarios (columns 14-19 of each sheet, in column order = task 1-6;
##task_source inferred from column order). In each scenario respondents chose how to cross: 1. Puente peatonal (pedestrian
##bridge), 2. Cruce directo (direct crossing), 3. Interseccion semaforizada (signalised intersection) -- the three labelled
##alternatives are the profiles (1-3, attr_crossing_type). No opt-out; exactly one chosen (every cell filled).
##Scenario attributes (R script lines 511-526; the first four are read off the column headers, which hold the scenario text
##but truncate it before the distances): delay in the trip 0/5/10/0/5/10 minutes ("Retraso en el viaje: k minutos"); minor
##accompanying No/Si/No/Si/No/Si ("Menor: No (usted viaja solo/a)" / "Si (un menor lo acompana en su trayecto)"); vehicle
##flow Bajo/Medio/Alto/Bajo/Medio/Alto; additional distance to the crossing point: signalised intersection 100/150/200/150/
##100/200 m, bridge 150/200/250/200/150/250 m (script values; the direct crossing has no distance entry: stored
##"(not shown)"). Delay, minor and flow are properties of the scenario, repeated on all three profiles; distance is
##alternative-specific. Level text is Spanish (short labels from the header wording), distances are "<n> metros".
##Restrictions/level probabilities: not applicable to a fixed 6-scenario design (delay, minor and flow are confounded across
##the six scenarios). Attribute order: fixed (header order).
##Covariates: cov_gender (Hombre -> male, Mujer -> female, "Prefiero no decirlo" -> NA), cov_age (years), cov_education
##(source text, Spanish), cov_province (source text), cov_drivers_licence (source text), cov_household_income (source text, in
##minimum wages), cov_household_vehicle (source text). Dropped: start/end times and date (the date column holds impossible
##values such as 1968), typed city name, occupation, trip purpose and main mode, household size, the 15 crossing-type
##rating items and the psychometric items, free text. No survey weight. No identifying columns (the ID column is a form
##counter and is re-keyed).
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Data.xlsx")
alt_lab <- c("Puente peatonal", "Cruce directo", "Intersección semaforizada")
delay <- c(0, 5, 10, 0, 5, 10); minor <- c("No", "Sí", "No", "Sí", "No", "Sí"); flow <- c("Bajo", "Medio", "Alto", "Bajo", "Medio", "Alto")
sig <- c(100, 150, 200, 150, 100, 200); bri <- c(150, 200, 250, 200, 150, 250)
build <- function(sheet, nexp) {
  d <- suppressMessages(as.data.table(read_excel(f, sheet = sheet, .name_repair = "minimal")))
  stopifnot(nrow(d) == nexp, ncol(d) == 37)
  hdr <- gsub("\u00a0", " ", names(d))
  names(d) <- hdr
  stopifnot(all(grepl("^Retraso en el viaje: (0|5|10) minutos", hdr[14:19])),
            as.numeric(sub("^Retraso en el viaje: ([0-9]+) minutos.*", "\\1", hdr[14:19])) == delay,
            grepl("Menor: (No|S)", hdr[14:19]), grepl("Flujo vehicular:\\s*(Bajo|Medio|Alto)", hdr[14:19]))
  stopifnot(identical(sub(".*Menor: (No|Sí).*", "\\1", gsub("\n|\r", "", hdr[14:19])), c("No", "Sí", "No", "Sí", "No", "Sí")),
            identical(sub(".*Flujo vehicular:\\s*(Bajo|Medio|Alto).*", "\\1", gsub("\n|\r", "", hdr[14:19])), flow))
  ch <- sapply(14:19, function(j) as.integer(substr(trimws(d[[j]]), 1, 1)))
  stopifnot(all(ch %in% 1:3), all(substr(trimws(d[[14]]), 4, 6) %in% c("Pue", "Cru", "Int")))
  dd <- d[, .(sexo = get(hdr[7]), edad = suppressWarnings(as.integer(get(hdr[10]))), edu = get(hdr[9]), prov = get(hdr[5]),
              lic = get(hdr[11]), ing = get(hdr[35]), veh = get(hdr[36]))]
  dd[, id := .I]
  rows <- rbindlist(lapply(1:6, function(s) rbindlist(lapply(1:3, function(k) {
    data.table(id = dd$id, task = s, profile = k, choice = as.integer(ch[, s] == k),
      attr_crossing_type = alt_lab[k], attr_trip_delay = paste(delay[s], "minutos"), attr_minor_accompanying = minor[s],
      attr_vehicle_flow = flow[s],
      attr_additional_distance = if (k == 1) paste(bri[s], "metros") else if (k == 3) paste(sig[s], "metros") else "(not shown)")
  }))))
  rows <- merge(rows, dd[, .(id, cov_gender = ifelse(sexo == "Hombre", "male", ifelse(sexo == "Mujer", "female", NA)),
    cov_age = ifelse(edad >= 18 & edad <= 100, edad, NA), cov_education = edu, cov_province = prov,
    cov_drivers_licence = lic, cov_household_income = ing, cov_household_vehicle = veh)], by = "id")
  setorder(rows, id, task, profile)
  stopifnot(rows[, sum(choice), .(id, task)][, all(V1 == 1)], uniqueN(rows$id) == nexp)
  rows
}
dir.create(out, showWarnings = FALSE, recursive = TRUE)
fwrite(build(1, 483), file.path(out, "garciaramirez_2025_crossing_noncompliant.csv"))
fwrite(build(2, 392), file.path(out, "garciaramirez_2025_crossing_compliant.csv"))
