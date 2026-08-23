def get_mock_cloud_data():
    """
    Returns sample cloud infrastructure data
    for AeroDrift development and testing.
    """

    cloud_data = {
        "vpcs": [
            {
                "id": "vpc-001",
                "name": "production-vpc",
                "cidr": "10.0.0.0/16"
            }
        ],

        "subnets": [
            {
                "id": "subnet-001",
                "name": "private-subnet",
                "vpc_id": "vpc-001",
                "cidr": "10.0.1.0/24",
                "public": False
            }
        ],

        "ec2_instances": [
            {
                "id": "ec2-001",
                "name": "production-server",
                "subnet_id": "subnet-001",
                "security_group_id": "sg-001"
            }
        ],

        "security_groups": [
            {
                "id": "sg-001",
                "name": "production-security-group",
                "inbound_rules": [
                    {
                        "protocol": "tcp",
                        "port": 22,
                        "source": "0.0.0.0/0"
                    }
                ]
            }
        ],

        "databases": [
            {
                "id": "db-001",
                "name": "production-database",
                "subnet_id": "subnet-001",
                "public": False
            }
        ]
    }

    return cloud_data