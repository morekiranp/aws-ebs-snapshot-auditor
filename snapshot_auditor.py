import boto3

def lambda_handler(event, context):
    # Create an EC2 client using boto3
    my_ec2 = boto3.client('ec2')

    # Retrieve all EBS snapshots owned by this AWS account
    # These snapshots could belong to both active and deleted EC2 instances
    my_snapshots_response = my_ec2.describe_snapshots(OwnerIds=['self'])

    # Retrieve all currently running EC2 instances
    # We use a filter to include only instances in the 'running' state
    my_instances_response = my_ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    # Maintain a set of active (running) EC2 instance IDs for quick lookup
    my_active_instance_ids = set()

    # Extract instance IDs from the response
    for my_reservation in my_instances_response['Reservations']:
        for my_instance in my_reservation['Instances']:
            my_active_instance_ids.add(my_instance['InstanceId'])

    # Loop through each snapshot and determine if it should be deleted
    # Criteria for deletion:
    #   1. The snapshot is not associated with any volume.
    #   2. The snapshot’s associated volume does not exist or
    #      is not attached to any running EC2 instance.
    for my_snapshot in my_snapshots_response['Snapshots']:
        my_snapshot_id = my_snapshot['SnapshotId']
        my_volume_id = my_snapshot.get('VolumeId')

        if not my_volume_id:
            # Case 1: The snapshot is not attached to any volume
            # → Safe to delete since it's not in use
            my_ec2.delete_snapshot(SnapshotId=my_snapshot_id)
            print(f"Deleted EBS snapshot {my_snapshot_id} as it was not attached to any volume.")
        else:
            # Case 2: The snapshot is linked to a volume, check if the volume still exists
            try:
                my_volume_response = my_ec2.describe_volumes(VolumeIds=[my_volume_id])

                # If the volume exists but has no active attachments, it is unused
                if not my_volume_response['Volumes'][0]['Attachments']:
                    my_ec2.delete_snapshot(SnapshotId=my_snapshot_id)
                    print(f"Deleted EBS snapshot {my_snapshot_id} as it was taken from a volume not attached to any running instance.")
            except my_ec2.exceptions.ClientError as my_error:
                # Handle case where the associated volume no longer exists
                if my_error.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    my_ec2.delete_snapshot(SnapshotId=my_snapshot_id)
                    print(f"Deleted EBS snapshot {my_snapshot_id} as its associated volume was not found.")
