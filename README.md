# IRW

## IRW Commandments
Below are critical instructions for formatting data for the IRW. More information about the IRW data standard is available in the preprint and by contacting the IRW maintainers. 
1. Numeric values of a response should be meaningful.
2. If data come from an RCT, have a `treatment` column that is 1 if response comes from a treated respondent and 0 otherwise. 
3. Response time should be in seconds. 
4. Longitudinally collected responses should be in Unix time (seconds since Jan 1 1970 UTC).
5. If there are multiple scales available, split them into mutiple files. 

## Notes about adding to the IRW
- To add data from the queue to the IRW repository there are three todo items:

  1. Create a Github issue for this repository that describes any decisions you had to make and also includes a file with | in IRW format. Note that this may not be appropriate if the data is not publicly sharable. Contact us at the below email if that is the case.
  2. Once we have confirmed that the data is appropriate, submit a pull request so that the code used to format the data gets added [here](https://github.com/ben-domingue/irw/tree/main/data).
  3. Finally, ensure the 'data index' page [here](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit#gid=0) gets updated with the relevant information.

- We have a queue of data that we aim to add to the IRW available [here](https://docs.google.com/spreadsheets/d/13EzVbybU6pIrTq6xiivLvcN9h5OMi3wGM9W-xASpMVI/edit#gid=1076583183). We have typically tried to do some initial checks to ensure that these data are appropriate, but further investigation often suggests otherwise. Please feel free to each out to us at itemresponsewarehouse@stanford.edu.

