
# AIShield.Watchtower 🔍 Algorithms

---

## Pseudo algorithm

*Note*: - Steps taken for the aishield.watchtower open source project
---

- *Step 100*: Check if the provided information is a collection of objects, artifacts file or not (repository check); If not then terminate

### Model scanning
- *Step 200*: Search for the model files and create a list of it.

- *Step 210*: If list is empty then terminate, else proceed to next steps

- *Step 220*: For every model file entry in list, 

    - *Step 221*: open the model file and identify input dimensions, output dimension and internal calculation

    - *Step 222*: Determine the model usecase based on input dimensions, output dimensions and internal calculation and log. If undetermined mark unknown

- *Step 230*: For every identified model with usecase, trigger the open source library based vulnerability scan for malicious code injection, unsafe execution, secrets, PII and etc.

- *Step 240*: Consolidated scan information for model file and present the report

### Model Change detection
- *Step 500*: For a given identified model file Check if the model has a history. If not then indicate subtantial change terminate

- *Step 510*: If model has history then compare checksum. If checksum is same then indicate no chaage and complete

    - *Step 511*: If checksum is not same then check if architecture is same. If architecture is not same then indicate subtantial change and complete
    
    - *Step 512*: If architecture is same then calculate distance matrix between model weights of current  and history model.
    
    - *Step 513*: If distance matrix is below a threshold then indicate minor change and complete
    
    - *Step 514*: If distance matrix is above a threshold then indicate subtantial change and complete



### Notebook scanning
- *Step 300*: Search for the model development files and create a list of it.

- *Step 310*: If list is empty then terminate, else proceed to next steps

- *Step 320*: For every model development file entry in list, 

    - *Step 321*: open the model development file and transform it in to appropriate format model development flatten file

- *Step 330*: For every model development flatten file, trigger the open source library based vulnerability scan for malicious code injection, unsafe execution, secrets, PII and etc.

- *Step 340*: Consolidated scan information for model development file and present the report

### AIShield call
- *Step 400*: For every identified model file,

    - *Step 401*: Call step 500-514 and terminate the process if status is not subtantial change
    
    - *Step 402*: based on usecase, input dimensions and output dimension; generate a configuration parameter to call proprietary tool of AIShield via API call

    - *Step 403*: Append configuration parameters of the API with the consolidated scan information for model file from step 240

    - *Step 404*: Use the configuration parametersand place a call to AIShield API call
