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

running = True


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
                    allInfra[region].set_infrastructure(f"{tf_dir}/config/{region}.tfvars.json")
            if task == "Init Terraform":
                for tf_dir in tf_dirs:
                    os.system(f"cd {tf_dir} && terraform init")
            if task == "Refresh Apply Infrastucture":
                for tf_dir in tf_dirs:
                    region = get_region_from_dir(tf_dir)
                    os.system(f'cd {tf_dir} && terraform apply -var-file="config/{region}.tfvars.json" -auto-approve')
            console.print("\n")
            console.log(f"task [bold blue3]{task}[/] complete\n")
    
    inicial_print(console)

    # ================================================================================================
    #                                            MAIN LOOP
    # ================================================================================================
    current_region = ""
    ESTADO = "CHOOSE_REGION"
    while running:
        # ------------------------------- CHOOSE or CREATE REGION ------------------------------------
        if ESTADO == "CHOOSE_REGION":
            console.print("\n")
            console.rule("[bold grey62] Choose or Create Region", style="bold grey62", align="center")
            console.print("\nAvailable Regions:")
            id = 1
            for region in all_created_regions:
                console.print(f"[bold blue3]{id}[/] - [bold white]{region}[/]")
                id+=1
            console.print(f"\n.. or")
            console.print(f"[bold white]create a new region[/] with [bold blue3]create[/] option")
            console.print(f"[bold white]delete a region[/] with [bold red]delete[/] option")
            available_input = [str(i) for i in range(1, len(all_created_regions)+1)]
            available_input.append("create")
            available_input.append("delete")
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
                else:
                    current_region = all_created_regions[int(selection)-1]
                    ESTADO = "CHOOSE_ACTION"
                    continue

        # ------------------------------- CREATE REGION ------------------------------------
        elif ESTADO == "CREATE_REGION":
            available_regions = ["us-west-1", "us-west-2", "us-east-1", "us-east-2", "sa-east-1"]
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
        # ------------------------------- CHOOSE ACTION ------------------------------------
        elif ESTADO == "CHOOSE_ACTION":
            console.rule("[bold grey62] Choose Action", style="bold grey62", align="center")
            console.print("\nAvailable Actions:")
            console.print(f"[bold blue3]1[/] - [bold white]Create Infrastructure[/]")
            console.print(f"[bold blue3]2[/] - [bold white]Destroy Infrastructure[/]")
            console.print(f"[bold blue3]3[/] - [bold white]Change Region[/]")
            console.print(f"[bold blue3]4[/] - [bold white]Exit[/]")
            available_input = [str(i) for i in range(1, 5)]
            selection = console.input("\n [bold blue3]>>[/] ")



if __name__ == "__main__":
    main()