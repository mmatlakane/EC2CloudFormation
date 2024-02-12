#!/usr/bin/env python3
import boto3
import time

client = boto3.client("sts")
account_id = client.get_caller_identity()["Account"]
cf = boto3.client("cloudformation", region_name="us-east-1")

accounts = {"1234567890": "STAGING", "9876543210": "PRODUCTION"}

try:
    command_a = input(
        f"You are about to destroy the stack in the {accounts[account_id]} account - Are you sure? (y/n)"
    )
except:
    print("Invalid account active.")
    exit()

if command_a.lower() == "y":
    # Prompt user for destroy confirmation
    command_b = input(
        "Are you sure you want to destroy the entire stack? Type 'destroy' to confirm: "
    )

    # Check if command is 'destroy'
    if command_b.lower() == "destroy":
        # Get all stack names in the account
        stacks = cf.list_stacks(
            StackStatusFilter=["CREATE_COMPLETE", "UPDATE_COMPLETE"]
        )

        # Destroy CF stacks one by one
        for stack in stacks["StackSummaries"]:
            stack_name = stack["StackName"]
            print(f"Deleting stack: {stack_name}")
            cf.delete_stack(StackName=stack_name)

            # Wait for the stack to be deleted
            while True:
                try:
                    status = cf.describe_stacks(StackName=stack_name)["Stacks"][0][
                        "StackStatus"
                    ]
                except:
                    print(f"Stack {stack_name} has been deleted")
                    break
                if status == "DELETE_COMPLETE":
                    print(f"Stack {stack_name} has been deleted")
                    break
                print(".", end="", flush=True)
                time.sleep(5)

    if command_b.lower() != "destroy":
        print("Aborted")

if command_a.lower() != "y":
    print("Aborted")
