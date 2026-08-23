import networkx as nx


def build_cloud_topology(cloud_data):
    """
    Build a directed graph representing the cloud infrastructure.
    """

    graph = nx.DiGraph()

    # Add Internet node
    graph.add_node(
        "internet",
        type="Internet",
        name="Public Internet"
    )

    # Add VPC nodes
    for vpc in cloud_data["vpcs"]:
        graph.add_node(
            vpc["id"],
            type="VPC",
            name=vpc["name"]
        )

    # Add subnet nodes and connect them to VPC
    for subnet in cloud_data["subnets"]:
        graph.add_node(
            subnet["id"],
            type="Subnet",
            name=subnet["name"]
        )

        graph.add_edge(
            subnet["vpc_id"],
            subnet["id"]
        )

    # Add security group nodes
    for security_group in cloud_data["security_groups"]:
        graph.add_node(
            security_group["id"],
            type="SecurityGroup",
            name=security_group["name"]
        )

        # Check whether the security group allows
        # traffic from the public Internet
        for rule in security_group["inbound_rules"]:
            if rule["source"] == "0.0.0.0/0":
                graph.add_edge(
                    "internet",
                    security_group["id"]
                )

    # Add EC2 nodes and connections
    for instance in cloud_data["ec2_instances"]:
        graph.add_node(
            instance["id"],
            type="EC2",
            name=instance["name"]
        )

        graph.add_edge(
            instance["subnet_id"],
            instance["id"]
        )

        graph.add_edge(
            instance["security_group_id"],
            instance["id"]
        )

    # Add database nodes and connections
        # Add database nodes and connections
    for database in cloud_data["databases"]:
        graph.add_node(
            database["id"],
            type="Database",
            name=database["name"]
        )

        # Connect subnet to database
        graph.add_edge(
            database["subnet_id"],
            database["id"]
        )

        # If an EC2 instance is in the same subnet,
        # model its application-level access to the database.
        for instance in cloud_data["ec2_instances"]:
            if instance["subnet_id"] == database["subnet_id"]:
                graph.add_edge(
                    instance["id"],
                    database["id"]
                )

    return graph