from time import sleep
from rich.console import Console
from prints import *
import os
from infrastructure import *

from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

allInfra = {}

console = Console(color_system="256")


def main():
    # ================================================================================================
    #                                            INIT
    # ================================================================================================
    tasks = ["Load Existing Infrastucture", "Init Terraform", "Refresh Apply Infrastucture"]
    tf_dirs = all_tf_dirs()
    all_created_regions = all_created_regions_from_dir(tf_dirs)

    with console.status("[bold green]Working on tasks...") as status:
        while tasks:
            task = tasks.pop(0)
            if task == "Load Existing Infrastucture":
                for tf_dir in tf_dirs:
                    region = get_region_from_dir(tf_dir)
                    allInfra[region] = Infrastructure(region, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                    # if config file already exists, load it
                    if os.path.isfile(f'tf-{region}/config/{region}.tfvars.json'):
                        allInfra[region].set_infrastructure(f'tf-{region}/config/{region}.tfvars.json')
                    else:
                        write_json(allInfra[region].infrastructure)
            if task == "Init Terraform":
                for tf_dir in tf_dirs:
                    os.system(f"cd {tf_dir} && terraform init &> /dev/null")
            if task == "Refresh Apply Infrastucture":
                for tf_dir in tf_dirs:
                    region = get_region_from_dir(tf_dir)
                    os.system(f'cd {tf_dir} && terraform apply -var-file="config/{region}.tfvars.json" -auto-approve')
            console.log(f"task [bold blue3]{task}[/] complete\n")

    # ================================================================================================
    #                                            MAIN LOOP
    # ================================================================================================
    current_region = ""
    ESTADO = "START_MENU"
    running = True
    invalid_input = False
    
    while running:
        # ===============================================================================================
        #                                          STATE MENU
        # ===============================================================================================
        if ESTADO == "START_MENU":
            clear_console()
            console.rule("[bold grey62] Welcome to", style="bold grey62", align="center")   
            inicial_print(console)
            console.rule("\n[bold grey62] User or Region", style="bold grey62", align="center")
            console.print("\nAvailable Options:")
            console.print("[bold blue3]1[/] - Manage Regions")
            console.print("[bold blue3]2[/] - Create or List Users")
            console.print("[bold blue3]3[/] - Exit")
            console.print("\n[bold grey62]Choose an option:[/]")
            available_inputs = ["1", "2", "3"]
            option = console.input("[bold blue3]>>[/] ")
            if option in available_inputs:
                if option == "1":
                    ESTADO = "CHOOSE_REGION"
                elif option == "2":
                    ESTADO = "CHOOSE_USER"
                elif option == "3":
                    running = False
            else:
                console.print("[bold red]Invalid option[/]")
                sleep(1)

        # ===============================================================================================
        #                                         REGION MENU
        # ===============================================================================================

        # ------------------------------- CHOOSE or CREATE REGION ------------------------------------
        if ESTADO == "CHOOSE_REGION":
            clear_console()
            inicial_print(console)
            console.rule("\n[bold grey62] Choose or Create Region", style="bold grey62", align="center")
            console.print("\nAvailable Regions:")
            id = 1
            for region in all_created_regions:
                console.print(f"[bold blue3]{id}[/] - [bold white]{region}[/]")
                id+=1
            console.print(f"\n.. or")
            console.print(f"[bold white]create a new region[/] with [bold blue3]create[/] option")
            console.print(f"[bold white]delete a region[/] with [bold red]delete[/] option")
            console.print(f"\n.. or")
            console.print(f"[bold white]back to main menu[/] with [bold grey27]back[/] option")
            available_input = [str(i) for i in range(1, len(all_created_regions)+1)]
            available_input.append("create")
            available_input.append("delete")
            available_input.append("back")
            selection = console.input("\n [bold blue3]>>[/] ")
            if selection.lower() not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                continue
            else:
                if selection.lower() == "create":
                    ESTADO = "CREATE_REGION"
                    continue
                elif selection.lower() == "delete":
                    ESTADO = "DELETE_REGION"
                    continue
                elif selection.lower() == "back":
                    ESTADO = "START_MENU"
                    continue
                else:
                    current_region = all_created_regions[int(selection)-1]
                    ESTADO = "CHOOSE_ACTION"
                    continue

        # ------------------------------- CREATE REGION ------------------------------------
        elif ESTADO == "CREATE_REGION":
            available_regions = ["us-west-1", "us-west-2", "us-east-1", "us-east-2", "sa-east-1", "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ap-northeast-2", "ap-south-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-north-1", "me-south-1", "sa-east-1", "us-gov-east-1", "us-gov-west-1"]
            for region in all_created_regions:
                available_regions.remove(region)
            console.print("\n")
            console.rule("[bold grey62] Create Region", style="bold grey62", align="center")
            console.print("\n [bold white]Enter the name of the region[/] (without spaces or special characters)")
            console.print("Available Regions:")
            id = 1
            for region in available_regions:
                console.print(f"[bold blue3]{id}[/] - [bold white]{region}[/]")
                id+=1
            available_input = [i for i in range(1, len(available_regions)+1)]
            choosen_region_id = int(console.input("\n [bold blue3]>>[/] "))
            if choosen_region_id not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                continue
            else:
                region = available_regions[choosen_region_id-1]
                allInfra[region] = Infrastructure(region, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                create_new_region_dir(region)
                write_json(allInfra[region].infrastructure)
                console.log(f"task [bold blue3]Create Directory & Infra File[/] complete\n")
                tf_create_region(region)
                console.log(f"task [bold blue3]Init Region[/] complete\n")
                tf_apply_changes(region)
                console.log(f"task [bold blue3]Apply Infra in Region[/] complete\n")
                tf_dirs = all_tf_dirs()
                all_created_regions = all_created_regions_from_dir(tf_dirs)
                current_region = region
                ESTADO = "CHOOSE_ACTION"
                continue

        # ------------------------------- DELETE REGION ------------------------------------
        elif ESTADO == "DELETE_REGION":
            console.print("\n")
            console.rule("[bold grey62] Delete Region", style="bold grey62", align="center")
            console.print("\nAvailable Regions:")
            id = 1
            for region in all_created_regions:
                console.print(f"[bold blue3]{id}[/] - [bold white]{region}[/]")
                id+=1
            available_input = [i for i in range(1, len(all_created_regions)+1)]
            choosen_region_id = int(console.input("\n [bold blue3]>>[/] "))
            if choosen_region_id not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                continue
            else:
                tf_destroy_region(all_created_regions[choosen_region_id-1])
                remove_region_dir(all_created_regions[choosen_region_id-1])
                tf_dirs = all_tf_dirs()
                all_created_regions = all_created_regions_from_dir(tf_dirs)
                ESTADO = "CHOOSE_REGION"
                continue

        # ===============================================================================================
        #                                         ACTION MENU
        # ===============================================================================================

        # ------------------------------- CHOOSE ACTION ------------------------------------
        elif ESTADO == "CHOOSE_ACTION":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Choose Action", style="bold grey62", align="center")
            console.print("\nAvailable Actions:")
            console.print(f"[bold blue3]1[/] - [bold white]Manage Instances[/]")
            console.print(f"[bold blue3]2[/] - [bold white]Change Region[/]")
            console.print(f"[bold blue3]3[/] - [bold white]Exit[/]")
            available_input = [str(i) for i in range(1, 4)]
            selection = console.input("\n [bold blue3]>>[/] ")
            if selection not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                continue
            else:
                if selection == "1":
                    ESTADO = "MANAGE_INSTANCES"
                    continue
                elif selection == "2":
                    current_region = ""
                    ESTADO = "CHOOSE_REGION"
                    continue
                elif selection == "3":
                    running = False
                    continue
        
        # ===============================================================================================
        #                                         MANAGE INSTANCES
        # ===============================================================================================

        # ------------------------------- MANAGE INSTANCES ------------------------------------
        elif ESTADO == "MANAGE_INSTANCES":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Manage Instances", style="bold grey62", align="center")
            console.print("\nAvailable Actions:")
            console.print(f"[bold blue3]1[/] - [bold white]List Instances[/]")
            console.print(f"[bold blue3]2[/] - [bold white]Create Instance[/]")
            console.print(f"[bold blue3]3[/] - [bold white]Update Instance[/]")
            console.print(f"[bold blue3]4[/] - [bold white]Delete Instance[/]")
            console.print(f"[bold blue3]5[/] - [bold white]Back[/]")
            available_input = [str(i) for i in range(1, 6)]
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            if selection not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = True
                continue
            else:
                if selection == "1":
                    ESTADO = "LIST_INSTANCES"
                    continue
                elif selection == "2":
                    ESTADO = "CREATE_INSTANCE"
                    continue
                elif selection == "3":
                    ESTADO = "UPDATE_INSTANCE"
                    continue
                elif selection == "4":
                    ESTADO = "DELETE_INSTANCE"
                    continue
                elif selection == "5":
                    ESTADO = "CHOOSE_ACTION"
                    continue
        
        # ------------------------------- LIST INSTANCES ------------------------------------
        elif ESTADO == "LIST_INSTANCES":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] List Instances", style="bold grey62", align="center")
            console.print("\nAvailable Instances:")
            id = 1
            for instance in allInfra[current_region].infrastructure["instances_configuration"]:
                console.print(f'[bold blue3]{id}[/] - [bold white]{instance["instance_name"]}[/]')
                id+=1
            console.print(f"\n.. or")
            console.print(f"[bold white]back to main menu[/] with [bold grey27]back[/] option")
            available_input = [str(i) for i in range(0, len(allInfra[current_region].infrastructure["instances_configuration"])+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            if selection not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = True
                continue
            else:
                if selection == "back":
                    ESTADO = "MANAGE_INSTANCES"
                    continue
                else:
                    instances_config = get_instances(current_region)
                    instance_name = allInfra[current_region].infrastructure["instances_configuration"][int(selection)-1]["instance_name"]
                    instance = instances_config[instance_name]
                    console.rule(f'\n[bold grey62] Instance: [/][bold green3]{instance_name}[/]', style="bold grey62", align="center")
                    console.print(f'\n[grey62] Instance ID: [/][bold white]{instance["id"]}[/]')
                    console.print(f'\n[grey62] Instance Type: [/][bold white]{instance["instance_type"]}[/]')
                    console.print(f'\n[grey62] Instance State: [/][bold white]{instance["instance_state"]}[/]')
                    console.print(f'\n[grey62] Public IP: [/][bold white]{instance["public_ip"]}[/]')
                    console.print(f'\n[grey62] Public DNS: [/][bold white]{instance["public_dns"]}[/]')
                    console.print(f'\n[grey62] Key Name: [/][bold white]{instance["key_name"]}[/]')
                    console.print(f'\n[grey62] Security Groups: [/][bold white]{instance["security_groups"]}[/]')
                    _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                    continue



        # ------------------------------- CREATE INSTANCE ------------------------------------
        elif ESTADO == "CREATE_INSTANCE":
            name = ""
            instance_type = ""
            ami = allInfra[current_region].ami_reference[current_region]
            security_group_ids = []
            key_name = ""

            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Create Instance", style="bold grey62", align="center")
            # Name instance:
            console.print("\nFirst, choose the [bold white]name[/] for the instance:")
            accepted_name = False
            while not accepted_name:
                choosen_name = console.input("\n=> [bold blue3]Name[/]: ")
                if choosen_name == "":
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    continue
                else:
                    name = choosen_name
                    accepted_name = True
            # Set instance type:
            console.print("\nNow, choose the [bold white]instance type[/] for the instance:")
            for i in range(len(allInfra[current_region].available_instnce_types)):
                console.print(f"[bold blue3]{i+1}[/] - [bold white]{allInfra[current_region].available_instnce_types[i]}[/]")
            available_input = [str(i) for i in range(1, len(allInfra[current_region].available_instnce_types)+1)]
            instance_type_option = console.input("\n=> [bold blue3]Instance Type[/]: ")
            acepted_input = False
            while not acepted_input:
                if instance_type_option not in available_input:
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    instance_type_option = console.input("\n=> [bold blue3]Instance Type[/]: ")
                else:
                    acepted_input = True
            instance_type = allInfra[current_region].available_instnce_types[int(instance_type_option)-1]
            # Set security group:
            console.print("\nNow, choose the [bold white]security groups[/] for the instance:")
            adding_sec_groups = True
            while adding_sec_groups:
                available_sec_groups, available_sec_groups_ids = get_sec_groups(current_region)
                for i in range(len(available_sec_groups)):
                    console.print(f"[bold blue3]{i+1}[/] - [bold white]{available_sec_groups[i]}[/]")
                console.print(f"\n.. or")
                console.print(f"finish security groups selection by typing [bold blue3]finished[/]\n")
                available_input = [str(i) for i in range(1, len(available_sec_groups)+1)]
                available_input.append("finished")
                security_group_option = console.input("\n=> [bold blue3]Security Group[/]: ")
                acepted_input = False
                while not acepted_input:
                    if security_group_option not in available_input:
                        console.print("\n[bold red]Invalid input, choose again please[/]")
                        security_group_option = console.input("\n=> [bold blue3]Security Group[/]: ")
                    else:
                        acepted_input = True
                if security_group_option == "finished":
                    adding_sec_groups = False
                elif available_sec_groups_ids[int(security_group_option)-1] in security_group_ids:
                    console.print("\n[bold red]This security group is already selected[/]")
                else:
                    security_group_ids.append(available_sec_groups_ids[int(security_group_option)-1])
            # Set key name:
            console.print("\nFor Last, choose the [bold white]key pair name[/] for the instance:")
            key_name = console.input("\n=> [bold blue3]Key Pair Name[/]: ")
            # Create instance:
            allInfra[current_region].create_instance(name, ami, instance_type, security_group_ids, key_name)
            write_json(allInfra[current_region].infrastructure)
            tf_apply_changes(current_region)
            ESTADO = "MANAGE_INSTANCES"


if __name__ == "__main__":
    main()