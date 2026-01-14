# IRW
The Item Response Warehouse (IRW) is an **open-source, large-scale** repository designed to advance psychometric research by standardizing and aggregating a large volume of item response datasets. 

## IRW Menu
- [IRW Website: ](https://datapages.github.io/irw/)has a high-level overview of the datasets.
- [IRW Paper: ](https://osf.io/preprints/psyarxiv/7bd54)describes IRW in detail, including data format, inclusion criteria, and our vision in the future
- [IRW Data Dictionary: ](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=0#gid=0)maintains a record of the descriptions, origins, and licenses of the processed datasets.
- [IRW Datasets: ](https://redivis.com/datasets/as2e-cv7jb41fd/tables)stores all processed datasets on Redivis.
- [IRW Code: ](https://github.com/KingArthur0205/irw/tree/main/data)a list of code used to standardize datasets into IRW format.
- **Contact Us:** for any question, please contact us at itemresponsewarehouse@stanford.edu.

## Installation & Getting Started
The easiest way to get access to IRW data is via the `irw` R package. See additional instructions [here](https://itemresponsewarehouse.org/analysis.html). For guidance to use IRW for data analysis in Python or R, please refer to the [IRW website](https://datapages.github.io/irw/analysis.html) for comprehensive explanations and examples.



## IRW Commandments
Below are critical instructions for formatting data for the IRW. More information about the IRW data standard is available [here](https://itemresponsewarehouse.org/standard.html). 
1. Numeric values of `resp` should be meaningful (i.e., at least ordinal).
2. If data come from an RCT, have a `treatment` column that is 1 if response comes from a treated respondent and 0 otherwise.  
3. Response time should be in seconds.   
4. Longitudinally collected responses should be in Unix time (seconds since Jan 1 1970 UTC).
5. If there are multiple scales available, split them into mutiple files.  

## Adding to the IRW
- To add data from the queue to the IRW repository there are three todo items: 

  1. Create a Github issue for this repository that describes any decisions you had to make and also includes a file with | in IRW format. Note that this may not be appropriate if the data is not publicly sharable. Contact us at the below email if that is the case.
  2. Once we have confirmed that the data is appropriate, submit a pull request so that the code used to format the data gets added [here](https://github.com/ben-domingue/irw/tree/main/data). The pull request should go to the original repository (not your forked version of it) and to the main branch (unless you have a need to create a new branch). 
  3. Finally, ensure the 'data index' page  [here](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit#gid=0) gets updated with the relevant information. 

- We have a queue of data that we aim to add to the IRW available  [here](https://github.com/ben-domingue/irw/issues). We have typically tried to do some initial checks to ensure that these data are appropriate, but further investigation often suggests otherwise. Please feel free to each out to us at itemresponsewarehouse@stanford.edu. 

