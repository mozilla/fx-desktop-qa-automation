import os
import sys
import textwrap


def get_class_name(tokenized):
    return "".join(word.capitalize() for word in tokenized)


def get_snake_case(tokenized):
    file_name = ""
    for token in tokenized:
        file_name += token.lower() + "_"
    file_name = file_name[: len(file_name) - 1]
    return file_name


def get_file_name(tokenized):
    file_name = get_snake_case(tokenized)

    if type == "pom":
        file_name = "page_object_" + file_name
    else:
        file_name = "browser_object_" + file_name
    return file_name


def create_pom_or_bom():
    object_name = input(
        "Enter the name of the POM/BOM (space separated \
                        e.g you want to create the AutofillPopup BOM, type autofill popup) you want to create: "
    )

    tokenized = object_name.split(" ")

    type = input("POM or BOM? ").lower()
    while type != "pom" and type != "bom":
        type = input("POM or BOM? (Type POM or BOM): ").lower()

    url_template = input(
        "What is the default landing page for this POM/BOM? type N/A for no applicable template: "
    )
    if url_template == "N/A":
        url_template = ""

    file_name = get_file_name(tokenized)

    class_name = get_class_name(tokenized)

    class_content = textwrap.dedent(f"""\
from modules.page_base import BasePage

class {class_name}(BasePage):
    \"\"\"
    Documentation for the class can go here.
    \"\"\"

    URL_TEMPLATE = "{url_template}"
""")

    try:
        with open(f"modules/{file_name}.py", "w") as file:
            file.write(class_content)
        with open(f"modules/data/{file_name}.components.json", "w") as file:
            file.write("{}")
        print(
            f"{file_name}.py was created and {file_name}.components.json was crated, a new class {class_name} was added inside the Python file!"
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def create_suite():
    suite_name = input(
        "Enter the name of the suite (space separated, eg if the suite is called Autofill Form, I will type Autofill Form): "
    )
    suite_id = input("Enter the id of your suite: ")

    tokenized = suite_name.split(" ")

    folder_name = get_snake_case(tokenized)

    try:
        os.mkdir(f"tests/{folder_name}")
        print(f"Directory tests/{folder_name} created.")
    except FileExistsError:
        print("Directory already exists.")
    except OSError as error:
        print(f"Error: {error}")

    contents = textwrap.dedent(f"""\
import pytest


@pytest.fixture()
def suite_id():
    return ("{suite_id}", "{suite_name}")


@pytest.fixture()
def set_prefs():
    ""\"Set prefs\"""
    return []
""")

    try:
        with open(f"tests/{folder_name}/conftest.py", "w") as file:
            file.write(contents)

        print(
            f"conftest.py was created within your new directory: tests/{folder_name}/"
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def main():
    while True:
        print(
            "What would you like to create? New Suite or new POM/BOMs? (Type suite or obj or exit): "
        )
        type = input().lower()

        if type == "exit":
            break

        while type != "suite" and type != "obj":
            type = input("suite or obj?: ")

        if type == "suite":
            create_suite()
        else:
            create_pom_or_bom()


if __name__ == "__main__":
    main()
