import boto3
from botocore.exceptions import BotoCoreError, ClientError


def get_aws_cloud_data(region="us-east-1"):
    """
    Read-only AWS resource discovery.

    This function only reads AWS resources.
    It does NOT modify or delete anything.
    """

    try:
        ec2 = boto3.client("ec2", region_name=region)
        rds = boto3.client("rds", region_name=region)

        # -------------------------------------------------
        # VPCs
        # -------------------------------------------------

        vpc_response = ec2.describe_vpcs()

        vpcs = []

        for vpc in vpc_response.get("Vpcs", []):

            vpcs.append({
                "id": vpc["VpcId"],
                "cidr": vpc.get("CidrBlock")
            })


        # -------------------------------------------------
        # Subnets
        # -------------------------------------------------

        subnet_response = ec2.describe_subnets()

        subnets = []

        for subnet in subnet_response.get("Subnets", []):

            subnets.append({
                "id": subnet["SubnetId"],
                "vpc_id": subnet["VpcId"],
                "cidr": subnet.get("CidrBlock")
            })


        # -------------------------------------------------
        # EC2 Instances
        # -------------------------------------------------

        instance_response = ec2.describe_instances()

        instances = []

        for reservation in instance_response.get(
            "Reservations", []
        ):

            for instance in reservation.get(
                "Instances", []
            ):

                instances.append({
                    "id": instance["InstanceId"],
                    "subnet_id": instance.get("SubnetId"),
                    "security_groups": [
                        group["GroupId"]
                        for group in instance.get(
                            "SecurityGroups", []
                        )
                    ]
                })


        # -------------------------------------------------
        # Security Groups
        # -------------------------------------------------

        security_group_response = (
            ec2.describe_security_groups()
        )

        security_groups = []

        for group in security_group_response.get(
            "SecurityGroups", []
        ):

            inbound_rules = []

            for permission in group.get(
                "IpPermissions", []
            ):

                protocol = permission.get(
                    "IpProtocol"
                )

                from_port = permission.get(
                    "FromPort"
                )

                to_port = permission.get(
                    "ToPort"
                )

                for ip_range in permission.get(
                    "IpRanges", []
                ):

                    inbound_rules.append({
                        "protocol": protocol,
                        "from_port": from_port,
                        "to_port": to_port,
                        "source": ip_range.get(
                            "CidrIp"
                        )
                    })


            security_groups.append({
                "id": group["GroupId"],
                "name": group.get("GroupName"),
                "vpc_id": group.get("VpcId"),
                "inbound_rules": inbound_rules
            })


        # -------------------------------------------------
        # RDS Databases
        # -------------------------------------------------

        database_response = (
            rds.describe_db_instances()
        )

        databases = []

        for database in database_response.get(
            "DBInstances", []
        ):

            databases.append({
                "id": database["DBInstanceIdentifier"],
                "subnet_group": database.get(
                    "DBSubnetGroup",
                    {}
                ).get("DBSubnetGroupName"),
                "security_groups": [
                    group["VpcSecurityGroupId"]
                    for group in database.get(
                        "VpcSecurityGroups", []
                    )
                ]
            })


        # -------------------------------------------------
        # Return normalized cloud data
        # -------------------------------------------------

        return {
            "vpcs": vpcs,
            "subnets": subnets,
            "ec2_instances": instances,
            "security_groups": security_groups,
            "databases": databases
        }


    except (BotoCoreError, ClientError) as error:

        print(f"AWS error: {error}")

        return None