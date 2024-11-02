# serverless
### Repository to store code for Lambda functions

#### This code runs as a part of pulumi build. So run as explained below

1. Clone the repo using git clone command
2. Go to the folder where this repository folder exist and run below command for each package mentioned in requirements.txt


       pip install --target ./serverless/ <package_name>

3. Once all the packages have been installed, select all the files in the serverless folder and compress them to create a zip file (The name that you give to this file should be passed as an environment variable in pulumi config file with .zip extension)

4. Go to iac-pulumi folder (or any folder where your pulumi code resides) and copy the zip file created in the previous step in this folder

5. Run the `pulumi up` command from your pulumi code folder and it should read the content in the zip folder to build your lambda function
