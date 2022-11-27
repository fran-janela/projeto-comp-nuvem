from time import sleep
from rich.console import Console
from prints import *
import os
from infrastructure import *
from iam_infra import *

from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


console = Console(color_system="256")


def main():
    # ================================================================================================
    #                                            INIT
    # ================================================================================================
    allInfra = {}
    iamInfra = IAM_Infrastructure(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    tasks = ["Load Existing Infrastucture", "Init Terraform", "Refresh Apply Infrastucture", "Init IAM Configuration", "Refresh Apply IAM Configuration"]
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
                    os.system(f'cd {tf_dir} && terraform apply -var-file="config/{region}.tfvars.json" -auto-approve &> /dev/null')
            if task == "Init IAM Configuration":
                os.system(f"cd iam && terraform init &> /dev/null")
            if task == "Refresh Apply IAM Configuration":
                #if config folder exists, load it
                iam_folders = [ f.path for f in os.scandir("iam/") if f.is_dir() ]
                if "iam/config" in iam_folders:
                    iamInfra.set_infrastructure(f'iam/config/iam.tfvars.json')
                else:
                    create_iam_config_folder()
                    write_iam_json(iamInfra.IAM_infra)
                tf_iam_apply_changes()
            console.log(f"task [bold blue3]{task}[/] complete\n")

    sleep(3)

    # ================================================================================================
    #                                            MAIN LOOP
    # ================================================================================================
    current_region = ""
    ESTADO = "START_MENU"
    running = True
    invalid_input = False
    cleared_infra = False
    invalid_json_data = False
    invalid_region_for_HA = False
    
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
            console.print("[bold blue3]2[/] - Manage IAM Users & Policies") 
            console.print("[bold blue3]3[/] - List all Instances")
            console.print("\n.. or")
            console.print("type [bold red]exit[/] to exit the program")
            console.print("\n[bold grey62]Choose an option:[/]")
            available_inputs = ["1", "2", "3", "exit"]
            option = console.input("[bold blue3]>>[/] ")
            if option in available_inputs:
                if option == "1":
                    ESTADO = "CHOOSE_REGION"
                elif option == "2":
                    ESTADO = "IAM_MENU"
                elif option == "3":
                    ESTADO = "LIST_ALL_INSTANCES"
                elif option == "exit":
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
            console.print(f"[bold blue3]2[/] - [bold white]Manage Security Groups[/]")
            console.print(f"[bold blue3]3[/] - [bold white]Manage HA aplication[/]")
            console.print(f"[bold blue3]4[/] - [bold white]Change Region[/]")
            console.print(f"\n.. or")
            console.print(f"[bold white]back to main menu[/] with [bold grey27]back[/] option")
            available_input = [str(i) for i in range(1, 5)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            if invalid_region_for_HA:
                console.print("\n[bold red]Invalid Region for building HA application, only available in us-east-1 or us-east-2[/]")
                invalid_region_for_HA = False
            selection = console.input("\n [bold blue3]>>[/] ")
            if selection not in available_input:
                invalid_input = True
            else:
                if selection == "1":
                    ESTADO = "MANAGE_INSTANCES"
                    continue
                elif selection == "2":
                    ESTADO = "MANAGE_SECURITY_GROUPS"
                    continue
                elif selection == "3":
                    if current_region in ["us-east-1", "us-east-2"]:
                        ESTADO = "MANAGE_HA_APPLICATION"
                    else:
                        invalid_region_for_HA = True
                    continue
                elif selection == "4":
                    ESTADO = "CHOOSE_REGION"
                    continue
                elif selection == "back":
                    ESTADO = "START_MENU"
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
            console.print(f"[bold blue3]3[/] - [bold white]Delete Instance[/]")
            console.print(f"[bold blue3]4[/] - [bold white]Update Instances Configuration[/]")
            console.print(f"\n.. or")
            console.print(f"[bold white]back to Choose Action[/] with [bold grey27]back[/] option")
            available_input = [str(i) for i in range(1, 5)]
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
                if selection == "1":
                    ESTADO = "LIST_INSTANCES"
                    continue
                elif selection == "2":
                    ESTADO = "CREATE_INSTANCE"
                    continue
                elif selection == "3":
                    ESTADO = "DELETE_INSTANCE"
                    continue
                elif selection == "4":
                    ESTADO = "UPDATE_INSTANCE"
                    continue
                elif selection == "back":
                    ESTADO = "CHOOSE_ACTION"
                    continue
        
        # ------------------------------- LIST INSTANCES ------------------------------------
        elif ESTADO == "LIST_INSTANCES":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] List Instances", style="bold grey62", align="center")
            console.print("\nAvailable Instances:")
            id = 1
            instances_config = get_instances(current_region)
            for instance_name in instances_config.keys():
                console.print(f'[bold blue3]{id}[/] - [bold white]{instance_name}[/]')
                id+=1
            console.print(f"\n.. or")
            console.print(f"[bold white]back to Manage Instances[/] with [bold grey27]back[/] option")
            available_input = [str(i) for i in range(0, len(instances_config)+1)]
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
                    instance_name = list(instances_config.keys())[int(selection)-1]
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
            # Set Instance Count:
            console.print("\nNow, choose the [bold white]number of instances[/] for this instance configuration:")
            count = console.input("\n=> [bold blue3]Count[/]: ")
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
                        invalid_input = True
                        continue
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
            allInfra[current_region].create_instance(name, count, ami, instance_type, security_group_ids, key_name)
            write_json(allInfra[current_region].infrastructure)
            tf_apply_changes(current_region)
            ESTADO = "MANAGE_INSTANCES"

        # ------------------------------- DELETE INSTANCE ------------------------------------
        elif ESTADO == "DELETE_INSTANCE":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Delete Instance", style="bold grey62", align="center")
            instances_config = allInfra[current_region].infrastructure["instances_configuration"]
            instances_names = [instance["instance_name"] for instance in instances_config]
            for i in range(len(instances_names)):
                console.print(f"[bold blue3]{i+1}[/] - [bold white]{instances_names[i]}[/]")
            console.print(f"\n.. or")
            console.print(f"finish instances selection by typing [bold grey62]back[/]\n")
            available_input = [str(i) for i in range(1, len(instances_names)+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            instance_option = console.input("\n [bold blue3]>>[/] ")
            if instance_option not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = True
                continue
            else:
                if instance_option == "back":
                    ESTADO = "MANAGE_INSTANCES"
                    continue
                else:
                    instance_name = instances_names[int(instance_option)-1]
                    allInfra[current_region].delete_instance(instance_name)
                    write_json(allInfra[current_region].infrastructure)
                    tf_apply_changes(current_region)
                    ESTADO = "MANAGE_INSTANCES"

        # ------------------------------- UPDATE INSTANCE ------------------------------------
        elif ESTADO == "UPDATE_INSTANCE":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Update Instance", style="bold grey62", align="center")
            instances_config = allInfra[current_region].infrastructure["instances_configuration"]
            instances_names = [instance["instance_name"] for instance in instances_config]
            for i in range(len(instances_names)):
                console.print(f"[bold blue3]{i+1}[/] - [bold white]{instances_names[i]}[/]")
            console.print(f"\n.. or")
            console.print(f"finish instances selection by typing [bold grey62]back[/]\n")
            available_input = [str(i) for i in range(1, len(instances_names)+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            instance_option = console.input("\n [bold blue3]>>[/] ")
            if instance_option not in available_input:
                invalid_input = True
                continue
            else:
                if instance_option == "back":
                    ESTADO = "MANAGE_INSTANCES"
                    continue
                else:
                    instance_name = instances_names[int(instance_option)-1]
                    for instance in instances_config:
                        if instance["instance_name"] == instance_name:
                            instance_config = instance
                            break
                    changing_n_instances = True
                    while changing_n_instances:
                        clear_console()
                        inicial_print(console)
                        console.rule(f'\n[bold grey62] Updating Instance: [bold green3]{instance_config["instance_name"]}[/]', style="bold grey62", align="center")
                        # Set Instance Count:
                        console.print("\nYou want to change the [bold white]number of instances?[/]")
                        available_input = ["yes", "y", "Y", "YES", "no", "n", "N", "NO"]
                        if invalid_input:
                            console.print("\n[bold red]Invalid input, choose again please[/]")
                            invalid_input = False
                        selection = console.input("\n=> [bold blue3]Y/n[/]: ")
                        invalid_input = False
                        if selection not in available_input:
                            invalid_input = True
                            continue
                        else:
                            if selection in ["yes", "y", "Y", "YES"]:
                                console.print("\nType the [bold white]new number of instances[/]:")
                                new_n_instances = console.input("\n [bold blue3]>>[/] ")
                                allInfra[current_region].update_number_of_instances(instance_name, new_n_instances)
                            changing_n_instances = False

                    # Update instance security_group ids:
                    changing_sec_groups = True
                    while changing_sec_groups:
                        clear_console()
                        inicial_print(console)
                        console.rule(f'\n[bold grey62] Updating Instance: [bold green3]{instance_config["instance_name"]}[/]', style="bold grey62", align="center")
                        # Set Instance Count:
                        console.print("\nThis instance has the following [bold white]security groups[/]:\n")
                        available_sec_groups, available_sec_groups_ids = get_sec_groups(current_region)
                        for i in range(len(available_sec_groups_ids)):
                            if available_sec_groups_ids[i] in instance_config["security_groups_ids"]:
                                console.print(f"[bold white]● {available_sec_groups[i]}[/]")
                        console.print("\nYou want to change the [bold white]security groups?[/]")
                        console.print("\n[bold orange]OBS.:[/] If you want to change the security group list in this instance, you will need to set it all again.")
                        available_input = ["yes", "y", "Y", "YES", "no", "n", "N", "NO"]
                        if invalid_input:
                            console.print("\n[bold red]Invalid input, choose again please[/]")
                            invalid_input = False
                        selection = console.input("\n=> [bold blue3]Y/n[/]: ")
                        invalid_input = False
                        if selection not in available_input:
                            invalid_input = True
                            continue
                        else:
                            if selection in ["yes", "y", "Y", "YES"]:
                                adding_sec_groups = True
                                new_security_group_ids = []
                                while adding_sec_groups:
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
                                            invalid_input = True
                                            continue
                                        else:
                                            acepted_input = True
                                    if security_group_option == "finished":
                                        adding_sec_groups = False
                                    elif available_sec_groups_ids[int(security_group_option)-1] in new_security_group_ids:
                                        console.print("\n[bold red]This security group is already selected[/]")
                                    else:
                                        new_security_group_ids.append(available_sec_groups_ids[int(security_group_option)-1])
                                allInfra[current_region].update_instance_security_groups(instance_name, new_security_group_ids)
                            changing_sec_groups = False
                    write_json(allInfra[current_region].infrastructure)
                    tf_apply_changes(current_region)

        # ===============================================================================================
        #                                      MANAGE SEURITY GROUPS
        # ===============================================================================================

        # ---------------------------- MANAGE SEURITY GROUPS ---------------------------------
        elif ESTADO == "MANAGE_SECURITY_GROUPS":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Manage Security Groups", style="bold grey62", align="center")
            console.print(f"\n[bold blue3]1[/] - [bold white]List Security Groups[/]")
            console.print(f"[bold blue3]2[/] - [bold white]Create Security Group[/]")
            console.print(f"[bold blue3]3[/] - [bold white]Delete Security Group[/]")
            console.print(f"[bold blue3]4[/] - [bold white]Add Rule to Security Group[/]")
            console.print(f"[bold blue3]5[/] - [bold white]Delete Rule from Security Group[/]")
            console.print(f"\n.. or")
            console.print(f"[bold white]back to Choose Action[/] with [bold grey27]back[/] option\n")
            available_input = ["1", "2", "3", "4", "5"]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            option = console.input("\n [bold blue3]>>[/] ")
            acepted_input = False
            if selection not in available_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = True
                continue
            else:
                if option == "1":
                    ESTADO = "LIST_SECURITY_GROUPS"
                elif option == "2":
                    ESTADO = "CREATE_SECURITY_GROUP"
                elif option == "3":
                    ESTADO = "DELETE_SECURITY_GROUP"
                elif option == "4":
                    ESTADO = "ADD_RULE_SECURITY_GROUP"
                elif option == "5":
                    ESTADO = "DELETE_RULE_SECURITY_GROUP"
                elif option == "back":
                    ESTADO = "CHOOSE_ACTION"

        # ---------------------------- LIST SEURITY GROUPS ---------------------------------
        elif ESTADO == "LIST_SECURITY_GROUPS":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] List Security Groups", style="bold grey62", align="center")
            security_groups_config = get_sec_groups_to_list(current_region)
            sec_groups_names, sec_groups_ids = get_sec_groups(current_region)
            for i in range(len(sec_groups_names)):
                console.print(f"[bold blue3]{i+1}[/] - [bold white]{sec_groups_names[i]}[/]")
            console.print(f"\n.. or")
            console.print(f"[bold white]back to Manage Security Groups[/] with [bold grey27]back[/] option\n")
            available_input = [str(i) for i in range(1, len(sec_groups_names)+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            security_group_option = console.input("\n [bold blue3]>>[/] ")
            acepted_input = False
            if security_group_option not in available_input:
                invalid_input = True
                continue
            else:
                if security_group_option == "back":
                    ESTADO = "MANAGE_SECURITY_GROUPS"
                    continue
                else:
                    security_group_name = sec_groups_names[int(security_group_option)-1].split(" ")[0]
                    security_group = security_groups_config[security_group_name]
                    console.print("")
                    console.rule(f'[bold grey62] Security Group: [/][bold green3]{security_group_name}[/]', style="bold grey62", align="center")
                    console.print(f"\n[grey62]ID[/]: [bold white]{security_group['id']}[/]")
                    console.print(f"\n[grey62]Description[/]: [bold white]{security_group['description']}[/]")
                    console.print(f"\n[grey62]Security Group Rules[/]:")
                    for ingress in security_group['ingress']:
                        console.print(f"\n- [grey62]Ingress[/]:")
                        console.print(f"\n   ● [grey62]From Port[/]: [bold white]{ingress['from_port']}[/]")
                        console.print(f"   ● [grey62]To Port[/]: [bold white]{ingress['to_port']}[/]")
                        console.print(f"   ● [grey62]Protocol[/]: [bold white]{ingress['protocol']}[/]")
                        console.print(f"   ● [grey62]CIDR[/]: [bold white]{ingress['cidr_blocks']}[/]")
                    for egress in security_group['egress']:
                        console.print(f"\n- [grey62]Egress[/]:")
                        console.print(f"\n   ● [grey62]From Port[/]: [bold white]{egress['from_port']}[/]")
                        console.print(f"   ● [grey62]To Port[/]: [bold white]{egress['to_port']}[/]")
                        console.print(f"   ● [grey62]Protocol[/]: [bold white]{egress['protocol']}[/]")
                        console.print(f"   ● [grey62]CIDR[/]: [bold white]{egress['cidr_blocks']}[/]")
                    console.print(f"\n[grey62]Owner Id[/]: [bold white]{security_group['owner_id']}[/]")
                    console.print(f"\n[grey62]VPC Id[/]: [bold white]{security_group['vpc_id']}[/]")
                    _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                    continue
        
        # --------------------------- CREATE SECURITY GROUP --------------------------------
        elif ESTADO == "CREATE_SECURITY_GROUP":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Create Security Group", style="bold grey62", align="center")
            name = console.input("\n=> [bold blue3]Name[/]: ")
            description = console.input("\n=> [bold blue3]Description[/]: ")
            allInfra[current_region].create_security_group(name, description)
            adding_rules = True
            while adding_rules:
                clear_console()
                inicial_print(console)
                console.rule("[bold grey62] Create Security Group", style="bold grey62", align="center")
                console.print(f'\n=> ADDING RULES TO: [bold white]{name} - {description}[/]')
                console.print(f"\n[bold blue3]1[/] - [bold white]Add Ingress Rule[/]")
                console.print(f"[bold blue3]2[/] - [bold white]Add Egress Rule[/]")
                console.print(f"\n.. or")
                console.print(f"[bold white]Finish rule management[/] with [bold blue3]finished[/] option\n")
                available_input = ["1", "2"]
                available_input.append("finished")
                if invalid_input:
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    invalid_input = False
                option = console.input("\n [bold blue3]>>[/] ")
                if selection not in available_input:
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    invalid_input = True
                    continue
                else:
                    if option == "1":
                        #description, protocol, from_port, to_port, cidr_ip, security_group_name
                        description = console.input("\n=> [bold blue3]Description[/]: ")
                        # Set protocol type, beteween tcp, udp, icmp, all
                        console.print("\nNow, choose the [bold white]protocol[/] for the Ingress Rule:")
                        available_protocols_labels = {"TCP":"tcp", "UDP":"udp", "ICMP":"icmp"}
                        available_protocols = list(available_protocols_labels.values())
                        i=1
                        for available_protocol in available_protocols_labels.keys():
                            console.print(f"[bold blue3]{i}[/] - [bold white]{available_protocol}[/]")
                            i+=1
                        protocol_option = console.input("\n [bold blue3]>>[/] ")
                        invalid_input = True
                        while invalid_input:
                            if protocol_option not in [str(i) for i in range(1, len(available_protocols)+1)]:
                                console.print("\n[bold red]Invalid input, choose again please[/]")
                                continue
                            else:
                                invalid_input = False
                        protocol = available_protocols[int(protocol_option)-1]
                        # Set from_port
                        console.print("\nNow, choose the [bold white]Start Port[/] for the Ingress Rule:")
                        from_port = console.input("\n=> [bold blue3]From Port[/]: ")
                        # Set to_port
                        console.print("\nNow, choose the [bold white]End Port[/] for the Ingress Rule:")
                        to_port = console.input("\n=> [bold blue3]To Port[/]: ")
                        # Set cidr_ip
                        console.print("\nNow, choose the [bold white]Cidr Blocks[/] for the Ingress Rule:")
                        cidr_blocks = []
                        adding_cidr_ips = True
                        while adding_cidr_ips:
                            console.print("\nSet a new [bold white]Cidr Block[/] for the Ingress Rule or [bold blue3]finished[/] to finish:")
                            cidr_ip = console.input("\n=> [bold blue3]Cidr Block[/]: ")
                            if cidr_ip == "finished":
                                adding_cidr_ips = False
                            else:
                                cidr_blocks.append(cidr_ip)
                        allInfra[current_region].create_ingress_for_sg(description, protocol, from_port, to_port, cidr_blocks, name)
                    elif option == "2":
                        # Set description
                        console.print("\First, choose the [bold white]Description[/] for the Egress Rule:")
                        description = console.input("\n=> [bold blue3]Description[/]: ")
                        # Set protocol type, beteween tcp, udp, icmp, all
                        console.print("\nNow, choose the [bold white]protocol[/] for the Egress Rule:")
                        available_protocols_labels = {"TCP":"tcp", "UDP":"udp", "ICMP":"icmp", "ALL":"-1"}
                        available_protocols = list(available_protocols_labels.values())
                        i=1
                        for available_protocol in available_protocols_labels.keys():
                            console.print(f"[bold blue3]{i}[/] - [bold white]{available_protocol}[/]")
                            i+=1
                        console.print(f"\n[bold red]Note: ALL is NOT recommended, and its start and end ports must be 0[/]")
                        protocol_option = console.input("\n [bold blue3]>>[/] ")
                        invalid_input = True
                        while invalid_input:
                            if protocol_option not in [str(i) for i in range(1, len(available_protocols)+1)]:
                                console.print("\n[bold red]Invalid input, choose again please[/]")
                                continue
                            else:
                                invalid_input = False
                        protocol = available_protocols[int(protocol_option)-1]
                        # Set from_port
                        console.print("\nNow, choose the [bold white]Start Port[/] for the Egress Rule:")
                        from_port = console.input("\n=> [bold blue3]From Port[/]: ")
                        # Set to_port
                        console.print("\nNow, choose the [bold white]End Port[/] for the Egress Rule:")
                        to_port = console.input("\n=> [bold blue3]To Port[/]: ")
                        # Set cidr_ip
                        console.print("\nNow, choose the [bold white]Cidr Blocks[/] for the Egress Rule:")
                        cidr_blocks = []
                        adding_cidr_ips = True
                        while adding_cidr_ips:
                            console.print("\nSet a new [bold white]Cidr Block[/] for the Egress Rule or [bold blue3]finished[/] to finish:")
                            cidr_ip = console.input("\n=> [bold blue3]Cidr Block[/]: ")
                            if cidr_ip == "finished":
                                adding_cidr_ips = False
                            else:
                                cidr_blocks.append(cidr_ip)
                        allInfra[current_region].create_egress_for_sg(description, protocol, from_port, to_port, cidr_blocks, name)
                    elif option == "finished":
                        adding_rules = False
                        ESTADO = "MANAGE_SECURITY_GROUPS"
            write_json(allInfra[current_region].infrastructure)
            tf_apply_changes(current_region)
            sleep(2)
            ESTADO = "MANAGE_SECURITY_GROUPS"

        # --------------------------- DELETE SECURITY GROUP ---------------------------------
        elif ESTADO == "DELETE_SECURITY_GROUP":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Delete Security Group", style="bold grey62", align="center")
            console.print("\n[bold white]Security Groups[/] in the [bold white]Region[/] that are not being used:")
            sec_groups_names, sec_groups_ids = get_sec_groups(current_region)
            sec_groups_in_use = get_sec_groups_in_use(current_region)
            index_not_used_sec_groups = []
            for i in range(len(sec_groups_names)):
                if sec_groups_ids[i] not in sec_groups_in_use:
                    index_not_used_sec_groups.append(i)
            index_print = 1
            for i in range(len(sec_groups_names)):
                if i in index_not_used_sec_groups:
                    console.print(f"[bold blue3]{index_print}[/] - [bold white]{sec_groups_names[i]}[/]")
                    index_print+=1
            console.print(f"\n.. or")
            console.print(f"finish instances selection by typing [bold grey62]back[/]\n")
            available_input = [str(i) for i in range(1, len(index_not_used_sec_groups)+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            delete_sec_group_option = console.input("\n [bold blue3]>>[/] ")
            acepted_input = False
            if delete_sec_group_option not in available_input:
                invalid_input = True
                continue
            else:
                if delete_sec_group_option == "back":
                    ESTADO = "MANAGE_SECURITY_GROUPS"
                    continue
                else:
                    sec_group_name = sec_groups_names[index_not_used_sec_groups[int(delete_sec_group_option)-1]].split(" ")[0]
                    allInfra[current_region].delete_sec_group(sec_group_name)
                    write_json(allInfra[current_region].infrastructure)
                    tf_apply_changes(current_region)
                    ESTADO = "MANAGE_SECURITY_GROUPS"

        # ------------------------ ADD RULE SECURITY GROUP ------------------------------
        elif ESTADO == "ADD_RULE_SECURITY_GROUP":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Add Rule to Security Group", style="bold grey62", align="center")
            console.print("\n[bold white]Security Groups[/] in the [bold white]Region[/] that are not being used:")
            sec_groups_names, sec_groups_ids = get_sec_groups(current_region)
            for i in range(len(sec_groups_names)):
                console.print(f"[bold blue3]{i + 1}[/] - [bold white]{sec_groups_names[i]}[/]")
            console.print(f"\n.. or")
            console.print(f"exit security group selection by typing [bold grey62]back[/]\n")
            available_input = [str(i) for i in range(1, len(sec_groups_names)+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            add_rule_sec_group_option = console.input("\n [bold blue3]>>[/] ")
            acepted_input = False
            if add_rule_sec_group_option not in available_input:
                invalid_input = True
                continue
            else:
                if add_rule_sec_group_option == "back":
                    ESTADO = "MANAGE_SECURITY_GROUPS"
                    continue
                else:
                    adding_rules = True
                    invalid_input = False
                    sec_group_name = sec_groups_names[int(add_rule_sec_group_option)-1].split(" ")[0]
                    while adding_rules:
                        clear_console()
                        inicial_print(console)
                        console.rule("[bold grey62] Add Rule to Security Group", style="bold grey62", align="center")
                        console.print(f'\nChoosen Security Group: [bold white]{sec_groups_names[int(add_rule_sec_group_option)-1]}[/]')
                        console.print("\n[bold blue3]1[/] - [bold white]Ingress[/]")
                        console.print("[bold blue3]2[/] - [bold white]Egress[/]")
                        console.print(f"\n.. or")
                        console.print(f"finish adding rules by typing [bold blue3]finished[/]\n")
                        available_input = ["1", "2", "finished"]
                        if invalid_input:
                            console.print("\n[bold red]Invalid input, choose again please[/]")
                            invalid_input = False
                        option = console.input("\n [bold blue3]>>[/] ")
                        if option not in available_input:
                            invalid_input = True
                            continue
                        elif option == "finished":
                            adding_rules = False
                            ESTADO = "MANAGE_SECURITY_GROUPS"
                            continue
                        elif option == "1":
                            #description, protocol, from_port, to_port, cidr_ip, security_group_name
                            description = console.input("\n=> [bold blue3]Description[/]: ")
                            # Set protocol type, beteween tcp, udp, icmp, all
                            console.print("\nNow, choose the [bold white]protocol[/] for the Ingress Rule:")
                            available_protocols_labels = {"TCP":"tcp", "UDP":"udp", "ICMP":"icmp"}
                            available_protocols = list(available_protocols_labels.values())
                            i=1
                            for available_protocol in available_protocols_labels.keys():
                                console.print(f"[bold blue3]{i}[/] - [bold white]{available_protocol}[/]")
                                i+=1
                            protocol_option = console.input("\n [bold blue3]>>[/] ")
                            invalid_input = True
                            while invalid_input:
                                if protocol_option not in [str(i) for i in range(1, len(available_protocols)+1)]:
                                    console.print("\n[bold red]Invalid input, choose again please[/]")
                                    continue
                                else:
                                    invalid_input = False
                            protocol = available_protocols[int(protocol_option)-1]
                            # Set from_port
                            console.print("\nNow, choose the [bold white]Start Port[/] for the Ingress Rule:")
                            from_port = console.input("\n=> [bold blue3]From Port[/]: ")
                            # Set to_port
                            console.print("\nNow, choose the [bold white]End Port[/] for the Ingress Rule:")
                            to_port = console.input("\n=> [bold blue3]To Port[/]: ")
                            # Set cidr_ip
                            console.print("\nNow, choose the [bold white]Cidr Blocks[/] for the Ingress Rule:")
                            cidr_blocks = []
                            adding_cidr_ips = True
                            while adding_cidr_ips:
                                console.print("\nSet a new [bold white]Cidr Block[/] for the Ingress Rule or [bold blue3]finished[/] to finish:")
                                cidr_ip = console.input("\n=> [bold blue3]Cidr Block[/]: ")
                                if cidr_ip == "finished":
                                    adding_cidr_ips = False
                                else:
                                    cidr_blocks.append(cidr_ip)
                            allInfra[current_region].create_ingress_for_sg(description, protocol, from_port, to_port, cidr_blocks, sec_group_name)
                        elif option == "2":
                            #description, protocol, from_port, to_port, cidr_ip, security_group_name
                            description = console.input("\n=> [bold blue3]Description[/]: ")
                            # Set protocol type, beteween tcp, udp, icmp, all
                            console.print("\nNow, choose the [bold white]protocol[/] for the Egress Rule:")
                            available_protocols_labels = {"TCP":"tcp", "UDP":"udp", "ICMP":"icmp", "ALL":"all"}
                            available_protocols = list(available_protocols_labels.values())
                            i=1
                            for available_protocol in available_protocols_labels.keys():
                                console.print(f"[bold blue3]{i}[/] - [bold white]{available_protocol}[/]")
                                i+=1
                            console.print(f"\n[bold red]Note: ALL is NOT recommended, and its start and end ports must be 0[/]")
                            protocol_option = console.input("\n [bold blue3]>>[/] ")
                            invalid_input = True
                            while invalid_input:
                                if protocol_option not in [str(i) for i in range(1, len(available_protocols)+1)]:
                                    console.print("\n[bold red]Invalid input, choose again please[/]")
                                    continue
                                else:
                                    invalid_input = False
                            protocol = available_protocols[int(protocol_option)-1]
                            # Set from_port
                            console.print("\nNow, choose the [bold white]Start Port[/] for the Egress Rule:")
                            from_port = console.input("\n=> [bold blue3]From Port[/]: ")
                            # Set to_port
                            console.print("\nNow, choose the [bold white]End Port[/] for the Egress Rule:")
                            to_port = console.input("\n=> [bold blue3]To Port[/]: ")
                            # Set cidr_ip
                            console.print("\nNow, choose the [bold white]Cidr Blocks[/] for the Egress Rule:")
                            cidr_blocks = []
                            adding_cidr_ips = True
                            while adding_cidr_ips:
                                console.print("\nSet a new [bold white]Cidr Block[/] for the Egress Rule or [bold blue3]finished[/] to finish:")
                                cidr_ip = console.input("\n=> [bold blue3]Cidr Block[/]: ")
                                if cidr_ip == "finished":
                                    adding_cidr_ips = False
                                else:
                                    cidr_blocks.append(cidr_ip)
                            allInfra[current_region].create_egress_for_sg(description, protocol, from_port, to_port, cidr_blocks, sec_group_name)
                    write_json(allInfra[current_region].infrastructure)
                    tf_apply_changes(current_region)
                    sleep(2)
        
        # ------------------------ REMOVE RULE SECURITY GROUP ------------------------------
        elif ESTADO == "DELETE_RULE_SECURITY_GROUP":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Add Rule to Security Group", style="bold grey62", align="center")
            console.print("\n[bold white]Security Groups[/] in the [bold white]Region[/] that are not being used:")
            sec_groups_names, sec_groups_ids = get_sec_groups(current_region)
            for i in range(len(sec_groups_names)):
                console.print(f"[bold blue3]{i+1}[/] - [bold white]{sec_groups_names[i]}[/]")
            console.print(f"\n.. or")
            console.print(f"exit security group selection by typing [bold grey62]back[/]\n")
            available_input = [str(i) for i in range(1, len(sec_groups_names)+1)]
            available_input.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            add_rule_sec_group_option = console.input("\n [bold blue3]>>[/] ")
            acepted_input = False
            if add_rule_sec_group_option not in available_input:
                invalid_input = True
                continue
            else:
                if add_rule_sec_group_option == "back":
                    ESTADO = "MANAGE_SECURITY_GROUPS"
                    continue
                else:
                    removing_rules = True
                    invalid_input = False
                    sec_group_name = sec_groups_names[int(add_rule_sec_group_option)-1].split(" ")[0]
                    while removing_rules:
                        clear_console()
                        inicial_print(console)
                        console.rule("[bold grey62] Add Rule to Security Group", style="bold grey62", align="center")
                        console.print(f'\nChoosen Security Group: [bold white]{sec_groups_names[int(add_rule_sec_group_option)-1]}[/]')
                        console.print("\n[bold blue3]1[/] - [bold white]Ingress[/]")
                        console.print("[bold blue3]2[/] - [bold white]Egress[/]")
                        console.print(f"\n.. or")
                        console.print(f"finish adding rules by typing [bold blue3]finished[/]\n")
                        available_input = ["1", "2", "finished"]
                        if invalid_input:
                            console.print("\n[bold red]Invalid input, choose again please[/]")
                            invalid_input = False
                        option = console.input("\n [bold blue3]>>[/] ")
                        if option not in available_input:
                            invalid_input = True
                            continue
                        elif option == "finished":
                            removing_rules = False
                            ESTADO = "MANAGE_SECURITY_GROUPS"
                            continue
                        elif option == "1":
                            console.print("\n[bold white]Ingress Rules[/] in the [bold white]Security Group[/]:\n")
                            for i in range(len(allInfra[current_region].infrastructure["security_group_configurations"])):
                                if allInfra[current_region].infrastructure["security_group_configurations"][i]["sg_name"] == sec_group_name:
                                    for j in range(len(allInfra[current_region].infrastructure["security_group_configurations"][i]["ingress_ports"])):
                                        ingress = allInfra[current_region].infrastructure['security_group_configurations'][i]['ingress_ports'][j]
                                        console.print(f'[bold blue3]{ingress["id"]}[/] - [bold white]{ingress["description"]}[/]')
                                    break
                            console.print(f"\n.. or")
                            console.print(f"exit ingress rules selection by typing [bold grey62]back[/]\n")
                            available_input = []
                            for j in range(len(allInfra[current_region].infrastructure["security_group_configurations"][i]["ingress_ports"])):
                                available_input.append(str(allInfra[current_region].infrastructure["security_group_configurations"][i]["ingress_ports"][j]["id"]))
                            available_input.append("back")
                            if invalid_input:
                                console.print("\n[bold red]Invalid input, choose again please[/]")
                                invalid_input = False
                            ingress_rule_option = console.input("\n [bold blue3]>>[/] ")
                            if ingress_rule_option not in available_input:
                                invalid_input = True
                                continue
                            else:
                                if ingress_rule_option == "back":
                                    continue
                                else:
                                    allInfra[current_region].remove_ingress_rule_from_sg(int(ingress_rule_option), sec_group_name)
                        elif option == "2":
                            for i in range(len(allInfra[current_region].infrastructure["security_group_configurations"])):
                                if allInfra[current_region].infrastructure["security_group_configurations"][i]["sg_name"] == sec_group_name:
                                    for j in range(len(allInfra[current_region].infrastructure["security_group_configurations"][i]["egress_ports"])):
                                        egress = allInfra[current_region].infrastructure['security_group_configurations'][i]['egress_ports'][j]
                                        console.print(f'[bold blue3]{egress["id"]}[/] - [bold white]{egress["description"]}[/]')
                                    break
                            console.print(f"\n.. or")
                            console.print(f"exit egress rules selection by typing [bold grey62]back[/]\n")
                            available_input = []
                            for j in range(1, len(allInfra[current_region].infrastructure["security_group_configurations"][i]["egress_ports"])):
                                available_input.append(allInfra[current_region].infrastructure["security_group_configurations"][i]["egress_ports"][j]["id"])
                            available_input.append("back")
                            if invalid_input:
                                console.print("\n[bold red]Invalid input, choose again please[/]")
                                invalid_input = False
                            egress_rule_option = console.input("\n [bold blue3]>>[/] ")
                            if egress_rule_option not in available_input:
                                invalid_input = True
                                continue
                            else:
                                if egress_rule_option == "back":
                                    continue
                                else:
                                    allInfra[current_region].remove_egress_rule_from_sg(int(egress_rule_option), sec_group_name)
                    write_json(allInfra[current_region].infrastructure)
                    tf_apply_changes(current_region)
                    sleep(2)

        # ===============================================================================================
        #                                    MANAGE HA APLICATION
        # ===============================================================================================
        # ------------------------------ MANAGE HA APLICATION ------------------------------
        elif ESTADO == "MANAGE_HA_APPLICATION":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Manage HA Application", style="bold grey62", align="center")
            console.print("\n[bold blue3]1[/] - [bold white]List HA aplication URL[/]")
            console.print("[bold blue3]2[/] - [bold white]Create HA Application[/]")
            console.print("[bold blue3]3[/] - [bold white]Remove HA Application[/]")
            console.print(f"\n.. or")
            console.print(f"go back to Choose Action by typing [bold grey62]back[/]\n")
            available_input = ["1", "2", "3", "back"]
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            ha_app_option = console.input("\n [bold blue3]>>[/] ")
            if ha_app_option not in available_input:
                invalid_input = True
                continue
            else:
                if ha_app_option == "back":
                    ESTADO = "CHOOSE_ACTION"
                    continue
                elif ha_app_option == "1":
                    if allInfra[current_region].infrastructure["create_HA_infrastructure"]:
                        console.rule("[bold grey62] HA Application URL", style="bold grey62", align="center")
                        console.print(f'\n[bold white]URL[/]: [bold blue3]{get_lb_url(current_region)}[/]')
                        _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                        continue
                    else:
                        console.print("\n\n[bold red]HA Application not created[/]")
                        _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                        continue
                elif ha_app_option == "2":
                    if not allInfra[current_region].infrastructure["create_HA_infrastructure"]:
                        ESTADO = "CREATE_HA_APPLICATION"
                    else:
                        console.print("\n\n[bold red]HA Application already created[/]")
                        _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                        continue
                    continue
                elif ha_app_option == "3":
                    if allInfra[current_region].infrastructure["create_HA_infrastructure"]:
                        ESTADO = "REMOVE_HA_APPLICATION"
                    else:
                        console.print("\n\n[bold red]HA Application not created[/]")
                        _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                        continue
                    continue

        # ------------------------------ CREATE HA APLICATION ------------------------------
        elif ESTADO == "CREATE_HA_APPLICATION":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Create HA Application", style="bold grey62", align="center")
            console.print("\nIf you want to start an example of HA application, type [bold blue3]yes[/]")
            console.print(f"\n.. or")
            console.print(f"go back to Manage HA Application by typing [bold grey62]back[/]\n")
            available_input = ["yes", "Y", "YES", "Yes", "y", "back"]
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            ha_app_option = console.input("\n [bold blue3]>>[/] ")
            if ha_app_option not in available_input:
                invalid_input = True
                continue
            else:
                if ha_app_option == "back":
                    ESTADO = "MANAGE_HA_APPLICATION"
                    continue
                elif ha_app_option in ["yes", "Y", "YES", "Yes", "y"]:
                    console.rule("\n[bold grey62] Creating HA Application", style="bold grey62", align="center")
                    console.print("\n> Insert the key name to be used in the HA application")
                    key_name = console.input("\n [bold blue3]>>[/] ")
                    console.print("")
                    allInfra[current_region].add_ha_infra(key_name)
                    write_json(allInfra[current_region].infrastructure)
                    copy_files_from_dir_to_dir(f'tf-{current_region}/')
                    tf_apply_changes(current_region)
                    sleep(2)
                    ESTADO = "MANAGE_HA_APPLICATION"
                    continue

        # ------------------------------ REMOVE HA APLICATION ------------------------------
        elif ESTADO == "REMOVE_HA_APPLICATION":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Remove HA Application", style="bold grey62", align="center")
            console.print("\nIf you want to remove the HA application, type [bold blue3]yes[/]")
            console.print(f"\n.. or")
            console.print(f"go back to Manage HA Application by typing [bold grey62]back[/]\n")
            available_input = ["yes", "Y", "YES", "Yes", "y", "back"]
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            ha_app_option = console.input("\n [bold blue3]>>[/] ")
            if ha_app_option not in available_input:
                invalid_input = True
                continue
            else:
                if ha_app_option == "back":
                    ESTADO = "MANAGE_HA_APPLICATION"
                    continue
                elif ha_app_option in ["yes", "Y", "YES", "Yes", "y"]:
                    remove_HA_configurations(current_region)
                    tf_apply_changes(current_region)
                    allInfra[current_region].delete_ha_infra()
                    write_json(allInfra[current_region].infrastructure)
                    sleep(2)
                    ESTADO = "MANAGE_HA_APPLICATION"
                    continue
        # ===============================================================================================
        #                                         USER MENU
        # ===============================================================================================
        elif ESTADO == "IAM_MENU":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] IAM Menu", style="bold grey62", align="center")
            if not cleared_infra:
                console.print("\n[bold blue3]1[/] - [bold white]Manage Users[/]")
                console.print("[bold blue3]2[/] - [bold white]Manage Policies[/]")
                console.print(f"\n.. or")
                console.print(f"exit IAM menu by typing [bold grey62]back[/]")
                console.print(f"\n.. or")
                console.print(f"clear IAM Infrastructure by typing [bold red]clear[/]\n")
                available_input = ["1", "2", "back", "clear"]
                if invalid_input:
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    invalid_input = False
                option = console.input("\n [bold blue3]>>[/] ")
                if option not in available_input:
                    invalid_input = True
                    continue
                elif option == "clear":
                    cleared_infra = True
                    iamInfra.clear_infrastructure()
                    ESTADO = "IAM_MENU"
                elif option == "back":
                    ESTADO = "START_MENU"
                    continue
                elif option == "1":
                    ESTADO = "MANAGE_USERS"
                    continue
                elif option == "2":
                    ESTADO = "MANAGE_POLICIES"
                    continue
            else:
                console.print("\n[bold red]IAM Infrastructure is cleared[/]")
                console.print(f"\n.. if you want to...")
                console.print(f"restore IAM Infrastructure by typing [bold blue3]restore[/]\n")
                console.print(f"\n.. or")
                console.print(f"exit IAM menu by typing [bold grey62]back[/]")
                available_input = ["restore", "back"]
                if invalid_input:
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    invalid_input = False
                option = console.input("\n [bold blue3]>>[/] ")
                if option not in available_input:
                    invalid_input = True
                    continue
                elif option == "back":
                    ESTADO = "START_MENU"
                    continue
                elif option == "restore":
                    cleared_infra = False
                    iamInfra = IAM_Infrastructure(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                    create_iam_config_folder()
                    write_iam_json(iamInfra.IAM_infra)
                    os.system(f"cd iam && terraform init &> /dev/null")
                    tf_iam_apply_changes()
                    continue

        # ===============================================================================================
        #                                         MANAGE USERS
        # ===============================================================================================
        elif ESTADO == "MANAGE_USERS":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Manage Users", style="bold grey62", align="center")
            console.print("\n[bold blue3]1[/] - [bold white]List User[/]")
            console.print("[bold blue3]2[/] - [bold white]Create User[/]")
            console.print("[bold blue3]3[/] - [bold white]Delete User[/]")
            console.print("[bold blue3]4[/] - [bold white]Atatch Policy to User[/]")
            console.print("[bold blue3]5[/] - [bold white]Detach Policy from User[/]")
            console.print("")
            console.print(f"\n.. or")
            console.print(f"exit user management by typing [bold grey62]back[/]\n")
            available_input = ["1", "2", "3", "4", "5", "back"]
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            option = console.input("\n [bold blue3]>>[/] ")
            if option not in available_input:
                invalid_input = True
                continue
            elif option == "back":
                ESTADO = "IAM_MENU"
                continue
            elif option == "1":
                ESTADO = "LIST_USERS"
                continue
            elif option == "2":
                ESTADO = "CREATE_USER"
                continue
            elif option == "3":
                ESTADO = "DELETE_USER"
                continue
            elif option == "4":
                ESTADO = "ATTACH_POLICY_TO_USER"
                continue
            elif option == "5":
                ESTADO = "DETACH_POLICY_FROM_USER"
                continue

        # --------------------------------- LIST USERS --------------------------------
        elif ESTADO == "LIST_USERS":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] List Users", style="bold grey62", align="center")
            created_user_names = [ user["username"] for user in iamInfra.IAM_infra["users_configurations"] ]
            for username in created_user_names:
                console.print(f"\n[grey62]Username[/]: [bold white]{username}[/]")
                attached_policies = [attached["policy_name"] for attached in iamInfra.IAM_infra["user_policy_attachments"] if attached["username"] == username]
                console.print("- Attached Policies:")
                for i in range(len(attached_policies)):
                    console.print(f"   ● [bold white]{attached_policies[i]}[/]")
            _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
            ESTADO = "MANAGE_USERS"

        # -------------------------------- CREATE USER --------------------------------
        elif ESTADO == "CREATE_USER":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Create User", style="bold grey62", align="center")
            console.print("\n[bold white]Type the name of the user you want to create[/]")
            console.print(f"\n.. or")
            console.print(f"exit user creation by typing [bold grey62]back[/]\n")
            if invalid_input:
                console.print("\n[bold red]Invalid input, this username already exixts[/]")
                invalid_input = False
            user_name = console.input("\n [bold blue3]>>[/] ")
            invalid_input = False
            if user_name == "back":
                ESTADO = "MANAGE_USERS"
                continue
            else:
                created_user_names = [ user["username"] for user in iamInfra.IAM_infra["users_configurations"] ]
                if user_name in created_user_names:
                    invalid_input = True
                    continue
                else:
                    iamInfra.create_user(user_name)
                    write_iam_json(iamInfra.IAM_infra)
                    tf_iam_apply_changes()
                    sleep(2)
                    console.rule("\n[bold grey62] User Password", style="bold grey62", align="center")
                    console.print("\nThis is the [blue3]password[/] for the user [bold blue3]{0}[/]".format(user_name))
                    console.print("[bold white]{0}[/]".format(get_user_password(user_name)))
                    console.print("\n\n[bold red]Save the password before continue[/]")
                    _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                    ESTADO = "MANAGE_USERS"
                continue

        # -------------------------------- DELETE USER --------------------------------
        elif ESTADO == "DELETE_USER":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Delete User", style="bold grey62", align="center")
            created_user_names = [ user["username"] for user in iamInfra.IAM_infra["users_configurations"] ]
            for i in range(len(created_user_names)):
                console.print(f'[bold blue3]{i+1}[/] - [bold white]{created_user_names[i]}[/]')
            console.print(f"\n.. or")
            console.print(f"exit user deletion by typing [bold grey62]back[/]\n")
            available_inputs = [ str(i+1) for i in range(len(created_user_names))]
            available_inputs.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            invalid_input = False
            if selection not in available_inputs:
                invalid_input = True
                continue
            elif selection == "back":
                ESTADO = "MANAGE_USERS"
                continue
            else:
                iamInfra.delete_user(created_user_names[int(selection)-1])
                write_iam_json(iamInfra.IAM_infra)
                tf_iam_apply_changes()
                sleep(2)
                ESTADO = "MANAGE_USERS"
                continue

        # -------------------------------- ATATCH POLICY --------------------------------
        elif ESTADO == "ATTACH_POLICY_TO_USER":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Atatch Policy to User", style="bold grey62", align="center")
            created_user_names = [ user["username"] for user in iamInfra.IAM_infra["users_configurations"] ]
            for i in range(len(created_user_names)):
                console.print(f'[bold blue3]{i+1}[/] - [bold white]{created_user_names[i]}[/]')
            console.print(f"\n.. or")
            console.print(f"exit attaching policy to user by typing [bold grey62]back[/]\n")
            available_inputs = [ str(i+1) for i in range(len(created_user_names))]
            available_inputs.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            invalid_input = False
            if selection not in available_inputs:
                invalid_input = True
                continue
            elif selection == "back":
                ESTADO = "MANAGE_USERS"
                continue
            else:
                user_name = created_user_names[int(selection)-1]
                clear_console()
                inicial_print(console)
                console.rule("[bold grey62] Atatch Policy to User", style="bold grey62", align="center")
                console.print(f"\n[bold white]User:[/][bold blue3] {user_name}[/]")
                console.print(f"\n[bold white]Select the policy you want to atatch to the user:[/]")
                created_policy_names = [ policy["name"] for policy in iamInfra.IAM_infra["policies_configurations"] ]
                for i in range(len(created_policy_names)):
                    console.print(f'[bold blue3]{i+1}[/] - [bold white]{created_policy_names[i]}[/]')
                console.print(f"\n.. or")
                console.print(f"exit user deletion by typing [bold grey62]back[/]\n")
                available_inputs = [ str(i+1) for i in range(len(created_policy_names))]
                available_inputs.append("back")
                if invalid_input:
                    console.print("\n[bold red]Invalid input, choose again please[/]")
                    invalid_input = False
                selection = console.input("\n [bold blue3]>>[/] ")
                if selection not in available_inputs:
                    invalid_input = True
                    continue
                elif selection == "back":
                    ESTADO = "MANAGE_USERS"
                    continue
                else:
                    policy_name = created_policy_names[int(selection)-1]
                    iamInfra.attach_policy(user_name, policy_name)
                    write_iam_json(iamInfra.IAM_infra)
                    tf_iam_apply_changes()
                    sleep(2)
                    ESTADO = "MANAGE_USERS"
                    continue

        # -------------------------------- DETATCH POLICY --------------------------------
        elif ESTADO == "DETACH_POLICY_FROM_USER":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Detatch Policy to User", style="bold grey62", align="center")
            created_user_names = [ user["username"] for user in iamInfra.IAM_infra["users_configurations"] ]
            for i in range(len(created_user_names)):
                console.print(f'[bold blue3]{i+1}[/] - [bold white]{created_user_names[i]}[/]')
            console.print(f"\n.. or")
            console.print(f"exit detaching policy to user by typing [bold grey62]back[/]\n")
            available_inputs = [ str(i+1) for i in range(len(created_user_names))]
            available_inputs.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            invalid_input = False
            if selection not in available_inputs:
                invalid_input = True
                continue
            elif selection == "back":
                ESTADO = "MANAGE_USERS"
                continue
            else:
                selecting_detach_policy = True
                user_name = created_user_names[int(selection)-1]
                while selecting_detach_policy:
                    clear_console()
                    inicial_print(console)
                    console.rule("[bold grey62] Detatch Policy to User", style="bold grey62", align="center")
                    console.print(f"\n[bold white]User:[/][bold blue3] {user_name}[/]")
                    console.print(f"\n[bold white]Select the policy you want to detatch to the user:[/]")
                    attached_policies = [ attachment["policy_name"] for attachment in iamInfra.IAM_infra["user_policy_attachments"] if attachment["username"] == user_name ]
                    for i in range(len(attached_policies)):
                        console.print(f'[bold blue3]{i+1}[/] - [bold white]{attached_policies[i]}[/]')
                    console.print(f"\n.. or")
                    console.print(f"exit user deletion by typing [bold grey62]back[/]\n")
                    available_inputs = [ str(i+1) for i in range(len(attached_policies))]
                    available_inputs.append("back")
                    if invalid_input:
                        console.print("\n[bold red]Invalid input, choose again please[/]")
                        invalid_input = False
                    selection = console.input("\n [bold blue3]>>[/] ")
                    if selection not in available_inputs:
                        invalid_input = True
                        continue
                    elif selection == "back":
                        selecting_detach_policy = False
                        ESTADO = "MANAGE_USERS"
                        continue
                    else:
                        policy_name = attached_policies[int(selection)-1]
                        iamInfra.detach_policy(user_name, policy_name)
                        write_iam_json(iamInfra.IAM_infra)
                        tf_iam_apply_changes()
                        selecting_detach_policy = False
                        ESTADO = "MANAGE_USERS"
                        continue

        # ===============================================================================================
        #                                         MANAGE POLICIES
        # ===============================================================================================
        elif ESTADO == "MANAGE_POLICIES":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Manage Policies", style="bold grey62", align="center")
            console.print("\n[bold blue3]1[/] - [bold white]List Policies[/]")
            console.print("[bold blue3]2[/] - [bold white]Import Policy[/]")
            console.print(f"\n.. or")
            console.print(f"exit policy management by typing [bold grey62]back[/]\n")
            available_input = ["1", "2", "back"]
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            option = console.input("\n [bold blue3]>>[/] ")
            if option not in available_input:
                invalid_input = True
                continue
            elif option == "back":
                ESTADO = "IAM_MENU"
                continue
            elif option == "1":
                ESTADO = "LIST_POLICY"
                continue
            elif option == "2":
                ESTADO = "IMPORT_POLICY"
                continue

        # ----------------------------- LIST POLICY ----------------------------
        elif ESTADO == "LIST_POLICY":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] List Policies", style="bold grey62", align="center")
            console.print("\nAvailable Policies:\n")
            created_policy_names = [ policy["name"] for policy in iamInfra.IAM_infra["policies_configurations"] ]
            for i in range(len(created_policy_names)):
                console.print(f'[bold blue3]{i+1}[/] - [bold white]{created_policy_names[i]}[/]')
            console.print(f"\n.. or")
            console.print(f"exit policy listing by typing [bold grey62]back[/]\n")
            available_inputs = [ str(i+1) for i in range(len(created_policy_names))]
            available_inputs.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            invalid_input = False
            if selection not in available_inputs:
                invalid_input = True
                continue
            elif selection == "back":
                ESTADO = "MANAGE_POLICIES"
                continue
            else:
                policy_config = iamInfra.IAM_infra["policies_configurations"][int(selection)-1]
                console.rule(f'[bold grey62] Security Group: [/][bold green3]{policy_config["name"]}[/]', style="bold grey62", align="center")
                for statement in policy_config["statements"]:
                    console.print(f'\n[grey62]Statement[/]: [bold white]{statement["restriction_name"]}[/]')
                    console.print(f"\n- [grey62]Actions[/]:")
                    for action in statement["actions"]:
                        console.print(f"   ● [bold white]{action}[/]")
                    console.print(f"\n- [grey62]Resources[/]:")
                    for resource in statement["resources"]:
                        console.print(f"   ● [bold white]{resource}[/]")
                    for index in range(len(statement["conditions"])):
                        console.print(f"\n- [grey62]Condition[/]: [bold white]Number {index}[/]")
                        console.print(f'   ● [grey62]Test[/]: [bold white]{statement["conditions"][index]["test"]}[/]')
                        console.print(f'   ● [grey62]Variable[/]: [bold white]{statement["conditions"][index]["variable"]}[/]')
                        console.print(f"   ● [grey62]Values[/]:")
                        for value in statement["conditions"][index]["values"]:
                            console.print(f"       ○ [bold white]{value}[/]")
                _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                continue

        # ----------------------------- IMPORT POLICY ----------------------------
        elif ESTADO == "IMPORT_POLICY":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] Import Policy", style="bold grey62", align="center")
            console.print("\nPass the policy .json file [bold blue3]full path[/],")
            console.print(f"\n.. or")
            console.print(f"exit policy import by typing [bold grey62]back[/]\n")
            if invalid_input:
                console.print("\n[bold red]Invalid input, .json File dosen't exists on that path, please choose again.[/]")
                invalid_input = False
            if invalid_json_data:
                console.print("\n[bold red]Invalid input, .json File is not a valid policy, please choose again.[/]")
                invalid_json_data = False
            passed_path = console.input("\n [bold blue3]>>[/] ")
            if passed_path == "back":
                ESTADO = "MANAGE_POLICIES"
                continue
            else:
                if os.path.exists(passed_path) and os.path.isfile(passed_path):
                    if passed_path.endswith(".json"):
                        os.system(f'cp {passed_path} iam/policies')
                        policy_name = passed_path.split("/")[-1].split(".")[0]
                        data = read_json(f'iam/policies/{policy_name}.json')
                        try:
                            _ = json_policy_to_infra(data, policy_name)
                            iamInfra.load_policies_from_folder()
                            console.print("")
                            console.log(f'[bold blue3]Policy[/] imported [green3]successfully[/]')
                            write_iam_json(iamInfra.IAM_infra)
                            tf_iam_apply_changes()
                        except:
                            os.system(f'rm -rf iam/policies/{policy_name}.json')
                            invalid_json_data = True

        # ===============================================================================================
        #                                     LIST ALL INSTANCES
        # ===============================================================================================
        elif ESTADO == "LIST_ALL_INSTANCES":
            clear_console()
            inicial_print(console)
            console.rule("[bold grey62] List All Instances", style="bold grey62", align="center")
            console.print("\nAvailable Instances:\n")
            all_instances_config = get_all_instances_config()
            for i in range(len(all_instances_config)):
                console.print(f'[bold blue3]{i+1}[/] - [bold white]{all_instances_config[i]["name"]} \t- {all_instances_config[i]["region"]}[/]')
            console.print(f"\n.. or")
            console.print(f"exit instance listing by typing [bold grey62]back[/]\n")
            available_inputs = [ str(i+1) for i in range(len(all_instances_config))]
            available_inputs.append("back")
            if invalid_input:
                console.print("\n[bold red]Invalid input, choose again please[/]")
                invalid_input = False
            selection = console.input("\n [bold blue3]>>[/] ")
            invalid_input = False
            if selection not in available_inputs:
                invalid_input = True
                continue
            elif selection == "back":
                ESTADO = "START_MENU"
                continue
            else:
                instance_config = all_instances_config[int(selection)-1]
                console.rule(f'[bold grey62] Instance: [/][bold green3]{instance_config["name"]}[/]', style="bold grey62", align="center")
                console.print(f'\n[grey62]Region[/]: [bold white]{instance_config["region"]}[/]')
                console.print(f'\n[grey62]Instance Type[/]: [bold white]{instance_config["instance_type"]}[/]')
                console.print(f'\n[grey62]Instance State[/]: [bold white]{instance_config["instance_state"]}[/]')
                console.print(f'\n[grey62]Key Pair Name[/]: [bold white]{instance_config["key_name"]}[/]')
                console.print(f'\n[grey62]Security Groups[/]: [bold white]{instance_config["security_groups"]}[/]')
                console.print(f'\n[grey62]Public IP[/]: [bold white]{instance_config["public_ip"]}[/]')
                console.print(f'\n[grey62]Public DNS[/]: [bold white]{instance_config["public_dns"]}[/]')
                _ = console.input("\n\n [bold light_steel_blue]Press Enter to continue[/] ")
                continue

if __name__ == "__main__":
    main()