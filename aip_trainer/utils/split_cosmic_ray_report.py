from pathlib import Path


def get_cosmic_ray_report_filtered(input_filename: str | Path, suffix: str = "filtered", separator: str = "============", filter_string_list: list[str] = None) -> None:
    """
    Filter out sections from a Cosmic Ray report file that contain a specific string.

    Parameters:
        input_filename (str): The name of the input file.
        suffix (str): The suffix to append to the output filename.
        separator (str): The separator string used to split sections in the input file.
        filter_string_list (list): A list of strings to filter out from the sections.

    Returns:
        None
    """
    if filter_string_list is None:
        filter_string_list = ["test outcome: TestOutcome.KILLED"]
    filename, ext = Path(input_filename).stem, Path(input_filename).suffix
    working_dir = input_filename.parent
    # Read the input file
    with open(input_filename, 'r') as file:
        content = file.read()

    # Split the content into sections
    sections = content.split(separator)
    filtered_sections = [section for section in sections]

    # Filter out sections containing "test outcome: TestOutcome.KILLED"
    for filter_string in filter_string_list:
        filtered_sections = [section for section in filtered_sections if filter_string not in section]

    # Join the filtered sections back into a single string
    filtered_content = separator.join(filtered_sections)

    # Write the filtered content to a new file
    with open(working_dir / f'{filename}_{suffix}{ext}', 'w') as file:
        file.write(filtered_content)



if __name__ == "__main__":
    from aip_trainer import PROJECT_ROOT_FOLDER
    _input_filename =  "cosmic-ray-models2.txt"
    get_cosmic_ray_report_filtered(PROJECT_ROOT_FOLDER / "tmp" / _input_filename)
