import pulumi
import pulumi_aws as aws
import pulumi_gcp as gcp
import base64
import json


# Get data from pulumi profile config files

config = pulumi.Config()
cidr_block = config.require("vpc_cidr_block")
key_name = config.require("key_name")
instance_type = config.require("instance_type")
instance_ami = config.require("instance_ami")
asg_tag = config.require("asg_tag")
igw_tag_name = config.require("igw_tag_name")
private_rt_tag_name = config.require("private_rt_tag_name")
private_subnet1 = config.require("private_subnet1")
private_subnet2 = config.require("private_subnet2")
private_subnet3 = config.require("private_subnet3")
public_rt_cidr = config.require("public_rt_cidr")
public_rt_tag_name = config.require("public_rt_tag_name")
public_subnet1 = config.require("public_subnet1")
public_subnet2 = config.require("public_subnet2")
public_subnet3 = config.require("public_subnet3")
sg_cidr = config.require("sg_cidr")
vpc_tag_name = config.require("vpc_tag_name")
ingress_port_1 = config.require("ingress_port_1")
ingress_port_2 = config.require("ingress_port_2")
ingress_port_3 = config.require("ingress_port_3")
ingress_port_4 = config.require("ingress_port_4")
egress_port = config.require("egress_port")
egress_cidr = config.require("egress_cidr")
delete_on_termination = config.require("delete_on_termination")
volume_size = config.require("volume_size")
volume_type = config.require("volume_type")
rds_tag = config.require("rds_tag")
parameter_group_tag = config.require("parameter_group_tag")
rds_ingress_port_1 = config.require("rds_ingress_port_1")
rds_username = config.require("rds_username")
rds_password = config.require("rds_password")
rds_database = config.require("rds_database")
rds_name = config.require("rds_name")
rds_engine = config.require("rds_engine")
rds_engine_version = config.require("rds_engine_version")
rds_instance_class = config.require("rds_instance_class")
rds_multi_az = config.require("rds_multi_az")
rds_allocated_storage = config.require("rds_allocated_storage")
rds_storage_type = config.require("rds_storage_type")
userdata_user = config.require("userdata_user")
userdata_group = config.require("userdata_group")
parameter_group_tag = config.require("parameter_group_tag")
hosted_zone_id = config.require("hosted_zone_id")
A_Record_name = config.require("A_Record_name")
lb_sg_tag = config.require("lb_sg_tag")
launch_template_public_ip = config.require("launch_template_public_ip")
asg_desired = config.require("asg_desired")
asg_max = config.require("asg_max")
asg_min = config.require("asg_min")
asg_cooldown = config.require("asg_cooldown")
device_name = config.require("device_name")
key1 = config.require("key1")
value1 = config.require("value1")
lb_tag = config.require("lb_tag")
lb_type = config.require("lb_type")
A_Record_evalTargetHealth = config.require("A_Record_evalTargetHealth")
asg_tag_key = config.require("asg_tag_key")
asg_tag_propagate_at_launch = config.require("asg_tag_propagate_at_launch")
asg_tag_value = config.require("asg_tag_value")
lb_listener_action_type = config.require("lb_listener_action_type")
lb_listener_port = config.require("lb_listener_port")
lb_listener_protocol = config.require("lb_listener_protocol")
lb_tg_interval = config.require("lb_tg_interval")
lb_tg_path = config.require("lb_tg_path")
lb_tg_port = config.require("lb_tg_port")
lb_tg_protocol = config.require("lb_tg_protocol")
lb_tg_timeout = config.require("lb_tg_timeout")
scale_down_type = config.require("scale_down_type")
scale_up_scaling = config.require("scale_up_scaling")
scale_up_type = config.require("scale_up_type")
sd_metric_comparison = config.require("sd_metric_comparison")
sd_metric_eval_periods = config.require("sd_metric_eval_periods")
sd_metric_name = config.require("sd_metric_name")
sd_metric_namespace = config.require("sd_metric_namespace")
sd_metric_period = config.require("sd_metric_period")
sd_metric_statistic = config.require("sd_metric_statistic")
sd_metric_threshold = config.require("sd_metric_threshold")
su_metric_comparison = config.require("su_metric_comparison")
su_metric_eval_period = config.require("su_metric_eval_period")
su_metric_name = config.require("su_metric_name")
su_metric_namespace = config.require("su_metric_namespace")
su_metric_period = config.require("su_metric_period")
su_metric_statistic = config.require("su_metric_statistic")
su_metric_threshold = config.require("su_metric_threshold")
lb_tg_healthport = config.require("lb_tg_healthport")
gcp_account_id = config.require("gcp_account_id")
gcp_display_name = config.require("gcp_display_name")
gcp_project = config.require("gcp_project")
gcp_cloud_bucket = config.require("gcp_cloud_bucket")
mailgun_domain = config.require("mailgun_domain")
mailgun_api_key = config.require("mailgun_api_key")
lambda_timeout = config.require("lambda_timeout")
gcp_storage_role = config.require("gcp_storage_role")
lambda_file = config.require("lambda_file")
lambda_handler = config.require("lambda_handler")
lambda_runtime = config.require("lambda_runtime")
ssl_certificate = config.require("ssl_certificate")

aws_config = pulumi.Config("aws")
aws_region = aws_config.require("region")

PUBLIC_SUBNETS = [public_subnet1, public_subnet2, public_subnet3]
PRIVATE_SUBNETS = [private_subnet1, private_subnet2, private_subnet3]

# Get number of availability zones in the selected region to decide number of public & private subnets
# Create 1 public and 1 private subnet in each AZ and do not create more than 6 subnets in total -- Requirement
available = aws.get_availability_zones(state="available")
public_subnets = []
private_subnets = []

# Creating VPC
myvpc = aws.ec2.Vpc("myvpc",
    cidr_block=cidr_block,
    tags={
        "Name": vpc_tag_name,
    })

# Assign Availability Zone number to a variable called number_of_az
number_of_az = len(available.names)

# Condition to decide how many AZ to create. For eg: If there are total of 2 AZ for a region, then 1 public & 1 private subnet will be created 
# in each AZ - Total 4 subnets (2 public and 2 private)
if number_of_az >= 3:
    for i in range(3):
        public_subnet = aws.ec2.Subnet(f"public-subnet-{i}",
                                   availability_zone=available.names[i],
                                   cidr_block=PUBLIC_SUBNETS[i],
                                   map_public_ip_on_launch=True,
                                   vpc_id=myvpc.id)
        private_subnet = aws.ec2.Subnet(f"private-subnet-{i}",
                                    availability_zone=available.names[i],
                                    cidr_block=PRIVATE_SUBNETS[i],
                                    map_public_ip_on_launch=False,
                                    vpc_id=myvpc.id)
        public_subnets.append(public_subnet)
        private_subnets.append(private_subnet)
else:
    for i in range(number_of_az):
        public_subnet = aws.ec2.Subnet(f"public-subnet-{i}",
                                    availability_zone=available.names[i],
                                    cidr_block=PUBLIC_SUBNETS[i],
                                    map_public_ip_on_launch=True,
                                    vpc_id=myvpc.id)
        private_subnet = aws.ec2.Subnet(f"private-subnet-{i}",
                                        availability_zone=available.names[i],
                                        cidr_block=PRIVATE_SUBNETS[i],
                                        map_public_ip_on_launch=False,
                                        vpc_id=myvpc.id)
        public_subnets.append(public_subnet)
        private_subnets.append(private_subnet)

# Create internet gateway to provide internet access
mygw = aws.ec2.InternetGateway("mygw",
    vpc_id=myvpc.id,
    tags={
        "Name": igw_tag_name,
    })

# Creating public route table
public_rt = aws.ec2.RouteTable("PublicRouteTable",
    vpc_id=myvpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block=public_rt_cidr,
            gateway_id=mygw.id,
        ),
    ],
    tags={
        "Name": public_rt_tag_name,
    })

# Creating private route table
private_rt = aws.ec2.RouteTable("PrivateRouteTable",
    vpc_id=myvpc.id,
    tags={
        "Name": private_rt_tag_name,
    })

# Associate public subnets with public route table and private subnets with private route table
for i, public_subnet in enumerate(public_subnets):
    aws.ec2.RouteTableAssociation(f"public-subnet-association-{i}",
                                  subnet_id=public_subnet.id,
                                  route_table_id=public_rt.id)

for i, private_subnet in enumerate(private_subnets):
    aws.ec2.RouteTableAssociation(f"private-subnet-association-{i}",
                                  subnet_id=private_subnet.id,
                                  route_table_id=private_rt.id)

# Creating Load Balancer Security Group to allow traffic from 80 and 443 ports and forward traffic to port 5000
load_balancer_sg = aws.ec2.SecurityGroup("load_balancer_security_group",
    description="Security group for load balancer",
    vpc_id=myvpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="Allow traffic on port 80",
            from_port=ingress_port_2,
            to_port=ingress_port_2,
            protocol="tcp",
            cidr_blocks=[sg_cidr],
            ),
        aws.ec2.SecurityGroupIngressArgs(
            description="Allow traffic on port 443",
            from_port=ingress_port_3,
            to_port=ingress_port_3,
            protocol="tcp",
            cidr_blocks=[sg_cidr],
            ),
            ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=ingress_port_4,
        to_port=ingress_port_4,
        protocol="tcp",
        cidr_blocks=[egress_cidr],
    )],
    tags={
        "Name": lb_sg_tag,
    })
  
# Creating security group for webapp
application_sg = aws.ec2.SecurityGroup("application_security_group",
    description="Security group for webapp",
    vpc_id=myvpc.id,
    #opts=pulumi.ResourceOptions(depends_on=[load_balancer_sg])
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="Allow traffic on port 22",
            from_port=ingress_port_1,
            to_port=ingress_port_1,
            protocol="tcp",
            cidr_blocks=[sg_cidr],
            ),
        aws.ec2.SecurityGroupIngressArgs(
            description="Allow traffic on port 5000",
            from_port=ingress_port_4,
            to_port=ingress_port_4,
            protocol="tcp",
            security_groups=[load_balancer_sg.id],
            ),
        ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=egress_port,
        to_port=egress_port,
        protocol="-1",
        cidr_blocks=[egress_cidr],
    )],
    tags={
        "Name": asg_tag,
    })

# Creating security group for RDS/database
database_sg = aws.ec2.SecurityGroup("database_security_group",
    description="Allow PostgreSQL traffic",
    vpc_id=myvpc.id,
    #opts=pulumi.ResourceOptions(depends_on=[application_sg])
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="Allow traffic on port 5432",
            from_port=rds_ingress_port_1,
            to_port=rds_ingress_port_1,
            protocol="tcp",
            security_groups=[application_sg.id]
            ),
        ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        from_port=egress_port,
        to_port=egress_port,
        protocol="-1",
        cidr_blocks=[egress_cidr],
    )],
    tags={
        "Name": rds_tag,
    })

# Creating RDS Parameter Group to attach with RDS
db_parameter_group = aws.rds.ParameterGroup("db-parameter-group",
    family="postgres15",
    tags={
        "Name" : parameter_group_tag,
    })

# Create a list of private subnet ids
private_subnet_ids = [subnet.id for subnet in private_subnets]

# Create RDS Subnet group to assign private subnet ids to RDS
rds_subnet_group = aws.rds.SubnetGroup("rds_subnet_group",
                                       subnet_ids=private_subnet_ids,
                                       description="csye6225 RDS Subnet Group",
                                       name="csye6225-rds-subnet-group")


# Create RDS instance in private subnet
rds_instance = aws.rds.Instance("rds_instance",
    db_name=rds_name,
    allocated_storage=rds_allocated_storage,
    storage_type=rds_storage_type,
    engine=rds_engine,
    engine_version=rds_engine_version,
    instance_class=rds_instance_class,
    identifier=rds_name,
    multi_az=rds_multi_az,
    parameter_group_name=db_parameter_group.name,
    password=rds_password,
    db_subnet_group_name = rds_subnet_group.name,
    username=rds_username,
    skip_final_snapshot= True,
    vpc_security_group_ids = [database_sg.id])


# Create SNS topic
sns_topic = aws.sns.Topic("sns-topic")


# Define user data to manipulate data on instance when it initializes for the first time
def user_data(endpoint, sns_arn, rds_username, rds_password, rds_database, userdata_user, userdata_group, aws_region):
    user_data = f'''#!/bin/bash
ENV_FILE="/opt/webapp.properties"
echo "RDS_HOSTNAME={endpoint}" > ${{ENV_FILE}}
echo "RDS_USERNAME={rds_username}" >> ${{ENV_FILE}}
echo "RDS_PASSWORD={rds_password}" >> ${{ENV_FILE}}
echo "RDS_DATABASE={rds_database}" >> ${{ENV_FILE}}
echo "DATABASE_URL=postgresql://{rds_username}:{rds_password}@{endpoint}/{rds_database}" >> ${{ENV_FILE}}
echo "SNS_TOPIC_ARN={sns_arn}" >> ${{ENV_FILE}}
echo "REGION={aws_region}" >> ${{ENV_FILE}}
$(sudo chown {userdata_user}:{userdata_group} ${{ENV_FILE}})
$(sudo chmod 400 ${{ENV_FILE}})
$(sudo chown -R {userdata_user}:{userdata_group} /opt/webapp)
$(sudo chown {userdata_user}:{userdata_group} /opt/users.csv)
$(sudo chown {userdata_user}:{userdata_group} /opt/webapp.log)
$(sudo systemctl start webapp)
$(sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/amazon-cloudwatch-agent.json -s)
$(sudo systemctl enable amazon-cloudwatch-agent)
$(sudo systemctl start amazon-cloudwatch-agent)
$(sudo rm -rf /opt/webapp/__pycache__/)
$(sudo chown {userdata_user}:{userdata_group} /opt/amazon-cloudwatch-agent.json)
'''
    return user_data
 
# Store user data coming from other AWS resources to a variable and call the function user_data
generate_user_data = pulumi.Output.all(
    rds_instance.endpoint,
    sns_topic.arn,
    rds_username,
    rds_password,
    rds_database,
    userdata_user,
    userdata_group,
    aws_region,
).apply(lambda args: user_data(*args))

# encode user data to use it in autoscaling launch template
encoded_user_data = generate_user_data.apply(lambda data: base64.b64encode(data.encode()).decode())

# Create IAM role for CloudWatch
cloudwatch_role = aws.iam.Role("my-cloudwatch-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                }
            }
        ]
    }""",
)

# Attach CloudWatchAgentServer policy to cloudwatch_role
cloudwatch_policy_attachment = aws.iam.PolicyAttachment("cloudwatch-policy-attachment",
    policy_arn="arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    roles=[cloudwatch_role.name],
)

sns_policy_attachment = aws.iam.PolicyAttachment("sns-policy-attachment",
     policy_arn="arn:aws:iam::aws:policy/AmazonSNSFullAccess",
     roles=[cloudwatch_role.name],
)

# Create an IAM role for Lambda
lambda_role = aws.iam.Role("lambda-execution-role", 
     assume_role_policy=json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Sid": "",
        "Principal": {
            "Service": "lambda.amazonaws.com",
        },
    }],
})
)

# Attach the AWS managed policy to lambda_role
lambda_policy_attachment = aws.iam.PolicyAttachment("lambda-policy-attachment",
     policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
     roles=[lambda_role.name],
)

#  Attach the AWS managed policy to lambda_role
dynamodb_lambda_policy_attachment = aws.iam.PolicyAttachment("dynamodb-lambda-policy-attachment",
     policy_arn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
     roles=[lambda_role.name],
)

# Create an IAM instance profile
cloudwatch_instance_profile = aws.iam.InstanceProfile("my-cloudwatch-instance-profile",
    role=cloudwatch_role.name,  # Associate the role with the instance profile
)

# Creating a launch template for auto scaling
autoscaling_launch_template = aws.ec2.LaunchTemplate("autoscaling-launch-template",
    block_device_mappings=[aws.ec2.LaunchTemplateBlockDeviceMappingArgs(
        device_name=device_name,
        ebs=aws.ec2.LaunchTemplateBlockDeviceMappingEbsArgs(
            volume_size=volume_size,
            volume_type=volume_type,
            delete_on_termination=delete_on_termination,
        ),
    )],
    iam_instance_profile=aws.ec2.LaunchTemplateIamInstanceProfileArgs(
        name=cloudwatch_instance_profile.name
    ),
    image_id=instance_ami,
    instance_type=instance_type,
    key_name=key_name,
    network_interfaces=[aws.ec2.LaunchTemplateNetworkInterfaceArgs(
        associate_public_ip_address=launch_template_public_ip,
        subnet_id=public_subnet.id,
        security_groups=[application_sg.id],
    )],
    tag_specifications=[aws.ec2.LaunchTemplateTagSpecificationArgs(
        resource_type="instance",
        tags={
            key1 : value1, 
        },
    )],
    user_data=encoded_user_data,
    )

# Create a list of public subnet ids
public_subnet_ids = [subnet.id for subnet in public_subnets]

# Create load balancer to balance load across instances
load_balancer = aws.lb.LoadBalancer("webapp-alb",
                                    load_balancer_type=lb_type,
                                    security_groups=[load_balancer_sg.id],
                                    subnets = public_subnet_ids,
                                    tags={
                                        "Name" : lb_tag
                                    })
# Create load balancer target group to attach instances to be load balanced by load balancer and to send requests to instances on port 5000
# Add health check details to ensure that instances in the target group are healthy
lb_target_group = aws.lb.TargetGroup("webapp-target-group",
                                     port=lb_tg_port,
                                     protocol=lb_tg_protocol,
                                     vpc_id=myvpc.id,
                                     health_check=aws.lb.TargetGroupHealthCheckArgs(
                                         interval=lb_tg_interval,
                                         path=lb_tg_path,
                                         port=lb_tg_healthport,
                                         protocol=lb_tg_protocol,
                                         timeout=lb_tg_timeout,
                                     ))
# Create load balancer listener group to enable listening through load balancer on port 80
lb_listener = aws.lb.Listener("webapp-alb-listener",
                              load_balancer_arn=load_balancer.arn,
                              port=lb_listener_port,
                              protocol=lb_listener_protocol,
                              certificate_arn = ssl_certificate,
                              default_actions=[aws.lb.ListenerDefaultActionArgs(
                                  type=lb_listener_action_type,
                                  target_group_arn=lb_target_group.arn,
                              )],
                              )

# Create autoscaling group using autoscaling launch template created earlier. Also defining minimum, maximum, and desired number of instances
# to make sure that required number of healthy instances are always available at all times
auto_scaling_group = aws.autoscaling.Group("auto-scaling-group",
    desired_capacity=asg_desired,
    max_size=asg_max,
    min_size=asg_min,
    target_group_arns=[lb_target_group.arn],
    opts=pulumi.ResourceOptions(depends_on=[autoscaling_launch_template, rds_instance, lb_target_group]),
    launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
        id=autoscaling_launch_template.id,
        version="$Latest",
    ),
    default_cooldown=asg_cooldown,
    tags=[
        {
            "key": asg_tag_key,
            "value": asg_tag_value,
            "propagate_at_launch": asg_tag_propagate_at_launch,
        },
    ],
)

# Define scale up policy - scale up by 1 instance
scale_up_policy = aws.autoscaling.Policy("scale-up-policy",
                                         scaling_adjustment=scale_up_scaling,
                                         adjustment_type=scale_up_type,
                                         autoscaling_group_name=auto_scaling_group.name)

# Uses scale up policy if this metric alarm triggers
# scale_up_metric_alarm monitors CPU Utilization of an instance and triggers and alarm if it is >5%
scale_up_metric_alarm = aws.cloudwatch.MetricAlarm("scale-up-metric-alarm",
                                                   comparison_operator=su_metric_comparison,
                                                   evaluation_periods=su_metric_eval_period,
                                                   metric_name=su_metric_name,
                                                   namespace=su_metric_namespace,
                                                   period=su_metric_period,
                                                   statistic=su_metric_statistic,
                                                   threshold=su_metric_threshold,
                                                   dimensions={
                                                       "AutoScalingGroupName" : auto_scaling_group.name
                                                   },
                                                   alarm_description="This metric triggers if average EC2 CPU Utilization is more than 5%",
                                                   alarm_actions=[scale_up_policy.arn])
# Define scale down policy - scale down by 1 instance
scale_down_policy = aws.autoscaling.Policy("scale-down-policy",
                                           scaling_adjustment=-1,
                                           adjustment_type=scale_down_type,
                                           autoscaling_group_name=auto_scaling_group.name)

# Uses scale down policy if this metric alarm triggers
# scale_down_metric_alarm monitors CPU Utilization of an instance and triggers an alarm if it is <5%
scale_down_metric_alarm = aws.cloudwatch.MetricAlarm("scale-down-metric-alarm",
                                                     comparison_operator=sd_metric_comparison,
                                                     evaluation_periods=sd_metric_eval_periods,
                                                     metric_name=sd_metric_name,
                                                     namespace=sd_metric_namespace,
                                                     period=sd_metric_period,
                                                     statistic=sd_metric_statistic,
                                                     threshold=sd_metric_threshold,
                                                     dimensions={
                                                         "AutoScalingGroupName" : auto_scaling_group.name
                                                     },
                                                     alarm_description="This metric triggers if average EC2 CPU Utilization is less than 3%",
                                                     alarm_actions=[scale_down_policy.arn])

# Create A record for instances in load balancer - point a group of public ips to DNS
A_Record = aws.route53.Record("A_Record",
    zone_id=hosted_zone_id,
    name=A_Record_name,
    type="A",
    aliases=[{
        "name" : load_balancer.dns_name,
        "zoneId" : load_balancer.zone_id,
        "evaluateTargetHealth" : A_Record_evalTargetHealth,
    }]) 

# Create gcp service account
gcp_service_account = gcp.serviceaccount.Account("serviceAccount",
    account_id=gcp_account_id,
    display_name=gcp_display_name)

# Extract the email using apply
email = gcp_service_account.email.apply(lambda email: f"serviceAccount:{email}")

# Grant 'roles/storage.admin' role to the service account
storage_admin_role_binding = gcp.projects.IAMMember(
    "grant-storage-admin-role",
    member=email,
    role=gcp_storage_role,
    project=gcp_project,
    opts=pulumi.ResourceOptions(depends_on=[gcp_service_account]),
)

# Creating service account key
gcp_svc_key = gcp.serviceaccount.Key("serviceAccountKey",
    service_account_id=gcp_service_account.name,)

# DynamoDB Table
dynamodb_user_table = aws.dynamodb.Table(
    "userTable",
    attributes=[
        {"name": "id", "type": "S"},
        {"name": "email", "type": "S"},
        {"name": "submissionAttempt", "type": "S"},
        {"name": "submissionUrl", "type": "S"},
        {"name": "submissionId", "type": "S"},
        {"name": "fileName", "type": "S"},
    ],
    hash_key="id",
    read_capacity=1,
    write_capacity=1,
    global_secondary_indexes=[
        {
            "name": "EmailIndex",
            "projection_type": "ALL",
            "read_capacity": 1,
            "write_capacity": 1,
            "hash_key": "email",
        },
        {
            "name": "SubmissionUrlIndex",
            "projection_type": "ALL",
            "read_capacity": 1,
            "write_capacity": 1,
            "hash_key": "submissionUrl",
        },
        {
            "name": "SubmissionIdIndex",
            "projection_type": "ALL",
            "read_capacity": 1,
            "write_capacity": 1,
            "hash_key": "submissionId",
        },
        {
            "name": "SubmissionAttemptIndex",
            "projection_type": "ALL",
            "read_capacity": 1,
            "write_capacity": 1,
            "hash_key": "submissionAttempt",
        },
        {
            "name": "fileNameIndex",
            "projection_type": "ALL",
            "read_capacity": 1,
            "write_capacity": 1,
            "hash_key": "fileName",
        },
    ],
)

# Create lambda function
func = aws.lambda_.Function("lambda-function",
    code=pulumi.FileArchive(lambda_file),
    role=lambda_role.arn,
    handler=lambda_handler,
    runtime=lambda_runtime,
    timeout=lambda_timeout,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "GCP_BUCKET_NAME" : gcp_cloud_bucket,
            "GOOGLE_CRED" : gcp_svc_key.private_key,
            "MAILGUN_DOMAIN" : mailgun_domain,
            "MAILGUN_API_KEY" : mailgun_api_key,
            "DYNAMODB_TABLE_NAME" : dynamodb_user_table.name,
            "AWS_REGION_DETAILS" : aws_region,

        },
))
with_sns = aws.lambda_.Permission("withSns",
    action="lambda:InvokeFunction",
    function=func.name,
    principal="sns.amazonaws.com",
    source_arn=sns_topic.arn)
lambda_ = aws.sns.TopicSubscription("lambda-subscription",
    topic=sns_topic.arn,
    protocol="lambda",
    endpoint=func.arn)