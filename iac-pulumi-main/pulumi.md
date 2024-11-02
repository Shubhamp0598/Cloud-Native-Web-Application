# iac-pulumi
## INFRASTRUCTURE AS CODE USING PULUMI
This repository contains code that creates infrastructure based on AWS profile and AWS information provided in its config file.

## Set up DNS and Email configurations
### DNS: Route53 setup
- Select a free domain from a website like https://www.namecheap.com/ or similar
- Create a hosted zone in root account with the same name as your free domain (eg: my_name.me)
- Create a hosted zone in demo/prod account with the name `demo|prod.<YOUR_FREE_DOMAIN>`
- Create a hosted zone in dev account with the name `dev.<YOUR_FREE_DOMAIN>`
- Creating a hosted zone will add NS and SOA records to your zone
- Copy NS record values from the root account and add it to `NAMESERVERS` field while registering a free domain
- Copy and paste NS record values of dev and demo accounts' hosted zones to root account hosted zone
### Email: Route53 setup
- Select any free transactional email delivery service like https://mailgun.com or similar
- Add your domain to this website (eg: my_name.me)
- Make sure to add the DKIM, SPF, MX, and CNAME records from this website to your root account

Root account hosted zone records should look something like this:

![Alt text](<Root records.png>)

## Lambda function requirement
- Clone [Lambda](https://github.com/CSYE-6225-Shivani/serverless) repository
- Follow instructions in [README.md](https://github.com/CSYE-6225-Shivani/serverless/blob/main/README.md)

## Resources created
Below are the resources that gets created through this code:

            1. Virtual Private Cloud
            2. Internet Gateway
            3. Private Route Table
            4. Public Route Table
            5. Private subnets associated with Private Route Table
            6. Public subnets associated with Public Route Table
            7. CloudWatch Role
            8. CloudWatch Policy
            9. CloudWatch Instance Profile
            10. Application Security Group
            11. Load Balancer Security Group
            12. Database/RDS Security Group
            13. Database Parameter Group
            14. RDS Subnet Group (private subnets)
            15. RDS instance associated with DB Paramater Group, DB Security Group, and RDS Subnet Group
            16. EC2 Instance
            17. A Record for EC2 instance
            18. Autoscaling launch template
            19. Load Balancer
            20. Load Balancer Target Group
            21. Load Balancer Listener
            22. Auto Scaling Group
            23. Scale Up Policy
            24. Scale Up Metric Alarm
            25. Scale Down Policy
            26. Scale Down Metric Alarm
            27. Lambda Execution Role
            28. DynamoDB Table
            29. SNS Policy
            30. DynamoDB Lambda Policy
            31. Lambda Policy
            32. GCP Storage Role
            33. GCP Service Account Key
            34. Lambda SNS Permission
            35. Lambda SNS Topic Subscription
            

## PREREQUISITES FOR RUNNING LOCALLY:
- Pulumi: https://www.pulumi.com/docs/install/
- AWS account with an organization - Add 2 accounts (dev & demo) in the organization and create admin users for each, generate AWS Access & Secret keys for both
- AWS CLI
- AWS configure setup from aws cli(profile for dev and demo accounts)

         -> aws configure –profile=dev
         -> aws configure –profile=demo
- Add access key, secret key, and nearest region here to configure your profiles
- Now to work under any profile, pass this variable first:

        - Mac:
          export AWS_PROFILE=<dev/demo>

        - Windows:
          setx AWS_PROFILE <dev/demo>


## STEPS TO FOLLOW
- Clone the repo - git clone <link>
- Check whether pulumi is installed or not - `pulumi version`
- Check available stacks 
       
        pulumi stack ls
- If no stacks are available, create one using below command and then follow along:

        pulumi new aws-python
- Change which profile to build your stack in using below command:
        
        pulumi config set aws:profile <dev/demo>
- Select a stack from multiple stacks:
        
        pulumi stack select <name>
- To change any of the variables defined in the pulumi config, use below command:


       pulumi config set <variable_name> <value>

- As of now, we have following variables defined in our pulumi config file:

                - aws:profile
                - aws:region
                - gcp:project
                - A_Record_evalTargetHealth
                - A_Record_name
                - asg_cooldown
                - asg_desired
                - asg_max
                - asg_min
                - asg_tag
                - asg_tag_key
                - asg_tag_propagate_at_launch
                - asg_tag_value
                - delete_on_termination
                - device_name
                - egress_cidr
                - egress_port
                - gcp_account_id
                - gcp_cloud_bucket
                - gcp_display_name
                - gcp_project
                - gcp_storage_role
                - hosted_zone_id
                - igw_tag_name
                - ingress_port_1
                - ingress_port_2
                - ingress_port_3
                - ingress_port_4
                - instance_ami
                - instance_type
                - key_name
                - key1
                - lambda_file
                - lambda_handler
                - lambda_runtime
                - lambda_timeout
                - launch_template_public_ip
                - lb_listener_action_type
                - lb_listener_port
                - lb_listener_protocol
                - lb_sg_tag
                - lb_tag
                - lb_tg_healthport
                - lb_tg_interval
                - lb_tg_path
                - lb_tg_port
                - lb_tg_protocol
                - lb_tg_timeout
                - lb_type
                - mailgun_api_key
                - mailgun_domain
                - parameter_group_tag
                - private_rt_tag_name
                - private_subnet1
                - private_subnet2
                - private_subnet3
                - public_rt_cidr
                - public_rt_tag_name
                - public_subnet1
                - public_subnet2
                - public_subnet3
                - rds_allocated_storage
                - rds_database
                - rds_engine
                - rds_engine_version
                - rds_ingress_port_1
                - rds_instance_class
                - rds_multi_az
                - rds_name
                - rds_password:- cloudisfantastic!
                - rds_storage_type
                - rds_tag
                - rds_username
                - scale_down_type
                - scale_up_scaling
                - scale_up_type
                - sd_metric_comparison
                - sd_metric_eval_periods
                - sd_metric_name
                - sd_metric_namespace
                - sd_metric_period
                - sd_metric_statistic
                - sd_metric_threshold
                - sg_cidr
                - ssl_certificate
                - su_metric_comparison
                - su_metric_eval_period
                - su_metric_name
                - su_metric_namespace
                - su_metric_period
                - su_metric_statistic
                - su_metric_threshold
                - userdata_group
                - userdata_user
                - value1
                - volume_size
                - volume_type
                - vpc_cidr_block
                - vpc_tag_name

-  Add SSL certificate from an SSL vendor outside AWS to AWS Certificate Manager (Get free ssl certificate from websites like zerossl or similar):

       aws acm import-certificate --certificate fileb://<certificate>.pem --certificate-chain fileb://<certificate_chain_name>.pem --private-key fileb://<private_key_name>.pem

- Once everything look okay, run below command to build your infrastructure:
        
       pulumi up

- To destroy everything, run below command:
        
       pulumi destroy