### Sample video | CI/CD Pipeline
https://github.com/user-attachments/assets/3d50cd2e-2521-43ab-a16e-0952b0f67405

### Overall Diagram | CI/CD Pipeline
![image](https://github.com/user-attachments/assets/6b8f97c1-e8f4-40eb-bfa0-f4e27f8cbd78)

### Diagram break down | CI/CD Pipeline
```Notes```: This CI/CD is used to test the Python scrapping script itself, the libray used for the test is ```Unittest```, some funcitons are tested with ```Mock objects``` to isolate the web interactions environment from the actual logic within the codes being tested. Each function will be tested with ```Mock objects``` individually and the ```main function``` will be tested with actual browser running.

1. Developers push code to the VCS (GitHub): When the developers push their codes to GitHub, the ```python-test.yml``` file located in the ```${{ github.workspace }}/.github/workflows``` will be executed, each stage within this pipeline requires its previous stage to pass.
2. ```Testing stage``` performed by ```GitHub Actions```: This is the first stage of the CI/CD pipeline, where's the codes will be compiled and tested, this stage typically check for mainly 2 things:
   * ```Unit test``` for each function within the main script, it will be tested with the ```Mock objects``` -> Mainly check for code's logic, inlcuding syntax or code errors happening at compiled time
   * ```Main test``` for the entire script interacting with the actual web browser's interactions and capchas handling  -> Mainly check for code's resilience, including issues happening when capchas were found, DOM elements are not available to interact, page's load state is taking longer time than exepcted ...
3. ```Analysis page``` performed by ```Github Actions```: This is the 2nd stage of the CI/CD pipeline, where's the code's potential issues will be checked, this stage typically check for mainly 2 things:
   * ```Test coverage```: Check the % test coverage of the testing script in the first step covers how many ```code lines``` in the script, the test needs to at least reach the threshhold of ```80%``` test covreage on the main script in order to pass
   * ```Code Analysis```: Identify for potential issues, bugs, code's redundance, code's duplications, and code's maintainability. This is also the main function of ```SonarQube```, to actually check if there's any part of the codes that can be refactored for better performance -> Mainly check for code quality 
4. ```Build Stage``` performed by ```Github Actions```: This is the last stage of the CI/CD pipeline, where's the code will be built to the ```Docker image``` that can be later pulled and used by other developers, this stage typically prevent 2 things:
   * Prevent the issue of ```This code works on my computer but not yours```: Docker ensures the versions are in sync and in place for all libraries and dependencies used in the applications or scripts
   * Prevent the deployment issues: ```Docker Image``` is lightweight and it can be deployed again on the ```Docker Container``` to simplify the set up process. Each ```Docker Image``` will be taged with its own version, hence, this facilitates developers to actually track back their development process on a script or an application
  
### Sample video | Playwright Scrapper
https://github.com/user-attachments/assets/b2e8e157-ecd9-4ae7-8433-196ad13f79f2

### Overall Rating Stamps Diagram | Playwright Scrapper
![image](https://github.com/user-attachments/assets/870b7b75-981b-4dff-bac8-9772730e3af2)

### Rating Stamps Diagram Break Down | Playwright Scrapper
```Notes```: The Playwright script is used to scrape 3 main metrics from Lazada, which are:
* ```Total Ratings```: The ratings counted since that SKU was initially created on the Lazada
* ```Selling Price```: The actual price sold to the users after exlcude all fees and selling-related costs idenfified by Lazada
* ```Current ratings```: The ratings the SKU received for the specifc ```start_date``` and ```end_date``` parameters
For the ```Total Ratings```, and the ```Selling price```, these metrics can be taken directly from Lazada through DOM elements, specfically, ```Current Ratings``` will be calculated as:
  1. Initialize the ```Current rating``` at 0
  2. Scrape the ```Rating stamp``` (The time at which that rating/comments were made) from each page, for each page, there will be 5 stamps that can be scrapped
  3. Check if the ```Rating stamp``` falls within the ```start_date``` and ```end_date``` parameters, if the requirement meets, rating count will be increased by 1
  4. Check if there's any next button to press, or if the ```page's number is less than 60``` (For Lazada, the ```page limits``` is at 60, meaning that every historical ratings that go beyond this page will display the same type of information or there will be no information to be displayed)
  5. If the requirements in the ```4th step``` met, scrapper will move to the next page and continue the first 3 steps, scrapper will stop if:
     * There's no next button to press
     * The scrapper finds the ```Rating stamp``` falls within the ```Month minus 1``` (Since the sort option is set to ```Recent```, the ```Rating stamp``` will be displayed from latest to earliest, if there's the rating stamp falls within the ```Month minus 1```, going all the pages beyond this current page will only see the ```Rating stamp``` out of the ```start_date``` and ```end_date``` check scope -> The loop should be exited)
     * There's no ```Sort bar``` on the SKU's ratings. If there's no sort bar, this means that the SKU's ratings only existed within 1 page, or it doesn't have any ratings at all (If the SKU didn't have any ratings, the scrapper will return an immediate ```Current ratings``` at 0 
