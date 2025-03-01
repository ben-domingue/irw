
##################################################################################
##Construct biblio.csv
library(gsheet)
library(redivis)
library(httr)
library(glue)
library(dplyr)
library(progress)
library(jsonlite)

# Function to Generate BibTex from DOI
fetch_bibtex_from_doi <- function(filename, doi) {
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

# Function to call ChatGPT and generate JSON formatted BibTeX output
openai_chat <- function(prompt, model = "gpt-4o", temperature = 0) {
  api_key <- Sys.getenv("OPENAI_API_KEY")
  
  if (nchar(api_key) == 0) {
    api_key <- readline("Enter your OpenAI API key: ")
    Sys.setenv(OPENAI_API_KEY = api_key)
  }
  
  response <- POST(
    url = "https://api.openai.com/v1/chat/completions", 
    add_headers(Authorization = paste("Bearer", api_key)),
    content_type_json(),
    encode = "json",
    body = toJSON(list(
      model = model,
      messages = list(
        list(role = "system", content = "You are an expert in structured data extraction. You will receive details of a dataset and should return a BibTeX citation of the dataset in JSON format."),
        list(role = "user", content = prompt)
      ),
      response_format = list(type="json_object"),  # Ensure structured JSON response
      temperature = temperature
    ), auto_unbox = TRUE)
  )
  
  if (status_code(response) != 200) {
    stop("Error: ", content(response, as = "parsed")$error$message)
  }
  
  parsed_response <- content(response, as = "parsed")
  if (!is.null(parsed_response$choices) && length(parsed_response$choices) > 0) {
    json_text <- parsed_response$choices[[1]]$message$content
    bibtex_entry <- fromJSON(json_text)$bibtex  # Extract only the BibTeX field
    return(bibtex_entry)
  } else {
    return(NULL) # Failed
  }
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
    prompt <- paste(
      "Extract a valid BibTeX citation in JSON format for the following dataset. They should all start with @misc:\n",
      "{\n",
      '  "table": "', df$table[i], '",\n',
      '  "reference": "', df$Reference[i], '",\n',
      '  "description": "', df$Description[i], '",\n',
      '  "url": "', df$`URL (for data)`[i], '"\n',
      "}\n",
      "Return a JSON object with a single key 'bibtex'."
    )
    df$BibTex[i] <- openai_chat(prompt)
    
    pb$tick()
    Sys.sleep(1) # Limit the call-rate to OpenAI
  }
  
  return(df)
}

# Google Spreadsheet URL or Sheet ID
irw_dict <- gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=0#gid=0')
irw_notpub <- irw_dict[irw_dict$`Public Reshare?`!="Public",]

# Read the current biblio file
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta:bdxt:latest")
biblio_table <- dataset$table("biblio:qahg")
biblio <- biblio_table$to_tibble()
head(biblio)

# Find rows in dictionary whose Filename is not in biblio
new_data_rows <- irw_dict[!(tolower(irw_dict$table) %in% tolower(biblio$table)), ]
##remove nonpublic elements before calling ChatGPT
new_data_rows <- new_data_rows[!new_data_rows$table %in% irw_notpub$table,]
new_data_rows <- new_data_rows |>
  select(table, Reference, `DOI (for paper)`, Description, `URL (for data)`) |>
  rename(DOI__for_paper_=`DOI (for paper)`, Reference_x=Reference, URL__for_data_=`URL (for data)`)
new_data_rows <- new_data_rows %>%
    mutate(BibTex = map2_chr(table, DOI__for_paper_, fetch_bibtex_from_doi))
new_data_rows <- generate_bibtex(new_data_rows)


biblio <- bind_rows(biblio, new_data_rows)
##remove nonpublic elements
test<-biblio$table %in% irw_notpub$table
biblio<-biblio[!test,]

##no csv
biblio$table<-gsub(".csv","",fixed=TRUE,biblio$table)
     
## Save the updated biblio to a CSV file
biblio<-biblio[,
c("table","DOI__for_paper_", "Reference_x",  "URL__for_data_", 
"Derived_License", "Description", "BibTex")]

readr::write_csv(biblio, "biblio.csv")
