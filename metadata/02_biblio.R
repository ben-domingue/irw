
##################################################################################
##Construct biblio.csv
library(gsheet)
source("gsheet_retry.R")  ## retrying gsheet2tbl; see that file
source("dict_union.R")    ## the automated-row union; see that file (#1732)

library(redivis)
source("redivis_config.R")
library(httr)
library(glue)
library(dplyr)
library(progress)
library(jsonlite)
library(purrr)

add_json_field <- function(key, value) {
  if (!is.na(value)) {
    return(paste0('  "', key, '": "', value, '"'))
  }
  return(NULL)
}

# Function to Generate BibTex from DOI
fetch_bibtex_from_doi <- function(filename, doi) {
    print(filename)
    if (is.na(doi) || doi == "") {
    return(NA_character_)  # Return NA if DOI is missing
  }
  url <- paste0("https://doi.org/", doi)
  response <- tryCatch({
    GET(url, add_headers(Accept = "application/x-bibtex"))
  }, error = function(e) {
    warning(glue("Error fetching dataset: {filename} - {e$message}"))
    return(NULL)
  }
  )
  if (!is.null(response) && status_code(response) == 200) {
    return(content(response, as = "text", encoding = "UTF-8"))
  } else {
    warning(glue("Failed to fetch BibTeX for dataset: {filename}"))
    return(NA_character_)
  }
}

# Function to call Claude and generate JSON formatted BibTeX output
anthropic_chat <- function(prompt, model = "claude-haiku-4-5", max_tokens = 1024) {
  api_key <- Sys.getenv("ANTHROPIC_API_KEY")
  if (nchar(api_key) == 0) {
    api_key <- readline("Enter your Anthropic API key: ")
    Sys.setenv(ANTHROPIC_API_KEY = api_key)
  }
  system_prompt <- "You are an expert in structured data extraction. You will receive details of a dataset and should return a BibTeX citation of the dataset in JSON format. Respond with ONLY the raw JSON object -- no markdown code fences, no commentary."
  response <- POST(
    url = "https://api.anthropic.com/v1/messages",
    add_headers(
      "x-api-key" = api_key,
      "anthropic-version" = "2023-06-01"
    ),
    content_type_json(),
    encode = "json",
    body = toJSON(list(
      model = model,
      max_tokens = max_tokens,
      system = system_prompt,
      messages = list(
        list(role = "user", content = prompt)
      )
    ), auto_unbox = TRUE)
  )
  if (status_code(response) != 200) {
    stop("Error: ", content(response, as = "parsed")$error$message)
  }
  parsed_response <- content(response, as = "parsed")
  if (!is.null(parsed_response$content) && length(parsed_response$content) > 0) {
    json_text <- parsed_response$content[[1]]$text
    json_text <- gsub("^```json\\s*|```\\s*$", "", json_text)  # strip fences if the model adds them anyway
    bibtex_entry <- fromJSON(json_text)$bibtex  # Extract only the BibTeX field
    return(bibtex_entry)
  } else {
    return(NULL) # Failed
  }
}

## A BibTeX value is "blank" if it is NA or whitespace-only. nzchar(NA) is TRUE,
## so the is.na() arm has to come first.
blank_bibtex <- function(x) is.na(x) | trimws(x) == ""

## Reuse BibTeX already generated on a previous run.
##
## getrows() takes its baseline from the *Redivis* biblio table, so a dictionary
## row that has not been published there yet looks brand new on every run. Rows
## with no DOI fall through fetch_bibtex_from_doi() to generate_bibtex(), which
## calls Claude -- and the model does not return byte-identical BibTeX twice. On
## 2026-08-31 that churned 31 tables (the mexico_2023_mobility_*,
## spain_2017_politics_*, spain_2018_housing_* and colombia_2023_politics_network
## families, none of them published to biblio on Redivis). The churn is not
## cosmetic: three lost their {{corporate author}} double-bracing -- which makes
## BibTeX parse an institution as a personal name -- and mexico_2023_mobility_assets
## came back with an empty author field.
##
## Publishing the draft would mask it, but only until the next unpublished row
## shows up, and it leaves every intervening weekly run emitting a noisy diff that
## a real regression could hide in. Seeding from file.out instead makes the run
## idempotent regardless of publish state: generate once, then reuse.
seed_from_local <- function(biblio, file.out) {
  if (!file.exists(file.out)) return(biblio)
  ## trim_ws=FALSE: the cache must be byte-faithful. doi.org returns BibTeX with
  ## a leading space, and readr trims it by default -- which would rewrite 55
  ## rows on the first seeded run for no reason other than the read.
  local <- tryCatch(readr::read_csv(file.out, show_col_types = FALSE, trim_ws = FALSE),
                    error = function(e) NULL)
  if (is.null(local) || !all(c("table", "BibTex") %in% names(local))) return(biblio)
  local <- local[!blank_bibtex(local$BibTex), , drop = FALSE]
  if (nrow(local) == 0) return(biblio)

  lkey <- tolower(local$table)
  local <- local[!duplicated(lkey), , drop = FALSE]
  lkey  <- lkey[!duplicated(lkey)]

  ## (a) backfill rows the Redivis table has but with no BibTeX
  idx <- which(blank_bibtex(biblio$BibTex))
  hit <- match(tolower(biblio$table)[idx], lkey)
  ok  <- !is.na(hit)
  if (any(ok)) {
    biblio$BibTex[idx[ok]] <- local$BibTex[hit[ok]]
    message(sprintf("  seeded %d BibTeX value(s) from %s", sum(ok), file.out))
  }

  ## (b) carry over rows the Redivis table does not have at all -- the case that
  ## caused the churn. Non-public rows are dropped downstream as before.
  extra <- local[is.na(match(lkey, tolower(biblio$table))), , drop = FALSE]
  if (nrow(extra) > 0) {
    biblio <- dplyr::bind_rows(biblio, extra)
    message(sprintf("  carried over %d cached row(s) absent from the Redivis table", nrow(extra)))
  }
  biblio
}

# Function to iterate through new_data_rows for BibTex
generate_bibtex <- function(df) {
  missing_bibtex_indices <- which(is.na(df$BibTex) | df$BibTex == "")
  if (length(missing_bibtex_indices) == 0) {
    message("No missing BibTeX entries found.")
    return(df)
  }
  pb <- progress_bar$new(
    format = "Generating BibTeX [:bar] :percent (:current/:total) - ETA: :eta",
    total = length(missing_bibtex_indices),
    width = 50
  )
  for (i in missing_bibtex_indices) {
    # Build JSON lines dynamically
    fields <- list(
      add_json_field("reference",   df$Reference_x[i]),
      add_json_field("url",         df$URL__for_data_[i])
    )
    # Remove NULLs and collapse into JSON object
    json_body <- paste("{\n", paste(Filter(Negate(is.null), fields), collapse = ",\n"), "\n}")
    # Only proceed if JSON has at least one field
    if (nchar(json_body) > 5) {
      prompt <- paste(
        "Extract a valid BibTeX citation in JSON format for the following citation:\n",
        json_body,
        "\nReturn a JSON object with a single key 'bibtex'."
      )
    } else {
      message(sprintf("Skipping row %d — all fields are NA.", i))
    }
    df$BibTex[i] <- anthropic_chat(prompt)
    pb$tick()
    Sys.sleep(1) # Limit the call-rate to Anthropic
  }
  return(df)
}

getrows<-function(l) {
    for (i in 1:length(l)) assign(names(l)[i],l[[i]])
    ## Union the automated dictionary rows before anything reads irw_dict, so
    ## every consumer below sees one merged dictionary (#1732 / roadmap 6b).
    ## Column-wise: a human cell wins the cell it occupies, an automated cell
    ## fills a cell the human left blank. See dict_union.R for why this differs
    ## from 03_tags.R, which supersedes whole rows and strands 19-76 tables per
    ## column (#1863). Sources with no automated file configured are unaffected.
    if (!is.null(l$file.auto)) {
        auto <- read_dict_auto(l$file.auto, name)
        auto <- drop_dead_dict_rows(auto, l$file.live, name,
                                    pending.file = l$file.pending)
        u <- union_dict(irw_dict, auto, name)
        irw_dict <- u$dict
        write_dict_provenance(u$provenance, l$file.prov)
    }
    ## The refresh log sits beside the CSV it explains: biblio.csv ->
    ## biblio_refresh_log.csv. Derived rather than configured so all four
    ## sources get one without four more list entries.
    file.refresh <- if (is.null(l$file.refresh)) sub("\\.csv$", "_refresh_log.csv", file.out) else l$file.refresh
    ## Read the current biblio file
    user <- redivis$user(user)
    dataset <- user$dataset(dataset)
    biblio_table <- dataset$table(table)
    biblio <- biblio_table$to_tibble()
    head(biblio)
    ## reuse previously generated BibTeX before deciding what is "new"
    biblio <- seed_from_local(biblio, file.out)
    ##
    irw_notpub <- irw_dict[irw_dict$`Public Reshare?`!="Public",]
    ## Find rows in dictionary whose Filename is not in biblio
    new_data_rows <- irw_dict[is.na(match(tolower(irw_dict$table), tolower(biblio$table))) | is.na(biblio$BibTex[match(tolower(irw_dict$table), tolower(biblio$table))]), ]
    ##remove nonpublic elements before calling ChatGPT
    new_data_rows <- new_data_rows[!new_data_rows$table %in% irw_notpub$table,]
    ## the 4 dictionary sheets (core/comps/nom/sim) are independently
    ## maintained and have drifted: core's license column is "Derived License"
    ## (with a space), comps/nom/sim already use "Derived_License" (underscore)
    ## -- confirmed 2026-08-02. Normalize to Derived_License before select()
    ## so this works across all 4 without hardcoding either sheet's spelling.
    if ("Derived License" %in% names(new_data_rows) && !("Derived_License" %in% names(new_data_rows))) {
        new_data_rows <- dplyr::rename(new_data_rows, Derived_License=`Derived License`)
    }
    ## `DOI (for data)` reaches this frame from dict_union.R, not the sheet
    ## (#1690). A source with no automated file never gains the column, so it is
    ## created blank rather than assumed.
    if (!("DOI (for data)" %in% names(new_data_rows))) {
        new_data_rows[["DOI (for data)"]] <- NA_character_
    }
    new_data_rows <- new_data_rows |>
    select(table, Reference, `DOI (for paper)`, `DOI (for data)`, Description, `URL (for data)`, Derived_License) |>
    rename(DOI__for_paper_=`DOI (for paper)`, DOI__for_data_=`DOI (for data)`,
           Reference_x=Reference, URL__for_data_=`URL (for data)`)
    ## Cite the paper where there is one, the deposit otherwise. Without the
    ## fallback every row #1690 splits would lose the BibTeX it has today and
    ## drop through to generate_bibtex(), which is a regression dressed as a fix
    ## -- the deposit's citation is the right one for a dataset with no paper.
    new_data_rows <- new_data_rows %>%
        mutate(BibTex = map2_chr(table,
                                 ifelse(dict_blank(DOI__for_paper_),
                                        DOI__for_data_, DOI__for_paper_),
                                 fetch_bibtex_from_doi))
    new_data_rows <- generate_bibtex(new_data_rows)
    biblio <- bind_rows(biblio, new_data_rows)
    ##remove nonpublic elements
    test<-biblio$table %in% irw_notpub$table
    biblio<-biblio[!test,]
    ##no csv
    biblio$table<-gsub(".csv","",fixed=TRUE,biblio$table)
    ## Refresh the five dictionary-owned columns on EVERY row, not just the new
    ## ones (#2001). new_data_rows above is, by construction, the rows biblio
    ## does not have; without this a correction typed into the sheet for an
    ## already-published table reaches nobody. Fills blanks, prefers the
    ## dictionary on conflict, and never blanks a biblio value from an empty
    ## dictionary cell. See refresh_biblio_from_dict() in dict_union.R.
    refreshed <- refresh_biblio_from_dict(biblio, irw_dict, name, log.file = file.refresh)
    biblio <- refreshed$biblio
    ## Runs before apply_data_doi(): the refresh never blanks a paper DOI, and
    ## the deposit-DOI retirement below is the one thing entitled to.

    ## Save the updated biblio to a CSV file
    ## Custom licence terms, for EVERY row rather than only the new ones.
    ##
    ## 238 Public tables publish `Derived_License = "Custom"` -- the bare word,
    ## with no terms a user can reach. metadata/hotfixes/fix-licenses.R added
    ## them to biblio.csv once (Rpkg#93) and the next run of this script erased
    ## them, because the column vector below rebuilds biblio.csv from a fixed
    ## list. Doing it here is what that hotfix could not make stick, which is
    ## why it is retired. The join itself lives in dict_union.R so it can be
    ## replayed offline against the real biblio.csv.
    biblio <- apply_custom_license_terms(biblio, irw_dict, name)
    ## Tables built from more than one deposit need both attributions;
    ## biblio carries only one licence and one reference (#1694). Fills a
    ## blank Custom_License_Terms only, so the sheet still wins the cell.
    biblio <- apply_license_attribution(biblio, name)
    ## Blank-only fill for the OSF deposits that set no licence; the sheet
    ## always wins, so a real licence recorded later supersedes it.
    biblio <- apply_osf_permission(biblio, name)
    ## Same carry-through, for the paper/deposit DOI split (#1690).
    biblio <- apply_data_doi(biblio, irw_dict, name)
    ## Correct the Descriptions that name an instrument the table does not
    ## contain (#1898, #1925, #1929, #1951, #1972). MUST run after the refresh
    ## above, which re-asserts the sheet's value on every row -- an override
    ## placed before it would be overwritten on every run. Applies to the export
    ## only; the sheet is untouched, and each entry disarms itself the moment
    ## someone corrects the sheet by hand. See DESCRIPTION_OVERRIDES.
    biblio <- apply_description_overrides(biblio, name)

    biblio<-biblio[,
                   c("table","DOI__for_paper_", "DOI__for_data_", "Reference_x",
                     "URL__for_data_",
                     "Derived_License", "Custom_License_Terms", "Description", "BibTex")]
    readr::write_csv(biblio, file.out)
}


dbs<-list(
    ##`file.auto` is what makes a source part of #1732: only core has an
    ##automated writer today. The other three are sheet-only, exactly as
    ##03_tags.R leaves comp/sim tag-less, and adding a file here is the whole
    ##opt-in.
    core=list(name="core",
              irw_dict=gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315'),
              user=IRW_OWNER,
              dataset="irw_meta",
              table="biblio",
              file.out="biblio.csv",
              file.auto="../automated_finding/dictionary_auto.csv",
              file.live="metadata.csv",
              file.prov="biblio_provenance.csv",
              file.pending="biblio_pending.csv"),
    comps=list(name="comps",
              irw_dict=gsheet2tbl('https://docs.google.com/spreadsheets/d/1WZZYyVC2cmw8CUJM69qP0F_ZlQjQfdkCZbdsG-8mUrs/edit?gid=1337607315#gid=1337607315'),
              user=IRW_OWNER,
              dataset="irw_meta",
              table="comps_biblio",
              file.out="comps_biblio.csv"),
    nom=list(name="nom",
              irw_dict=gsheet2tbl('https://docs.google.com/spreadsheets/d/12tM4vADKcUm5LGOGRwQ5_HKkdYa3mZUaKbFUqgs2U_w/edit?gid=1337607315#gid=1337607315'),
             user=IRW_OWNER,
             dataset="irw_meta",
             table="nominal_biblio",
             file.out="nominal_biblio.csv"),
    sim=list(name="sim",
              irw_dict=gsheet2tbl('https://docs.google.com/spreadsheets/d/1_2SR1_miAqUy0HWFQqo5vrBVrIN4V1FU6RfavBc7WdA/edit?gid=1337607315#gid=1337607315'),
             user=IRW_OWNER,
             dataset="irw_meta",
             table="simsyn_biblio",
             file.out="simsyn_biblio.csv")
)

for (i in 1:length(dbs)) {
    print(i)
    getrows(dbs[[i]])
}

