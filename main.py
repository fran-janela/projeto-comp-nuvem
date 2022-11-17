import click

@click.command()
@click.option("--debug", default=False, help="Use debug functions.")

def main():
    print("Hello World!")

if __name__ == "__main__":
    main()