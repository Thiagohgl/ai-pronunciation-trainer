from pathlib import Path

import pandas as pd
import json
import RuleBasedModels


class TextDataset:
    def __init__(self, table, language):
        self.table_dataframe = table
        self.language = language

    def __getitem__(self, idx):
        line = [self.table_dataframe['sentence'].iloc[idx]]
        return line

    def __len__(self):
        return len(self.table_dataframe)

    def get_category_from_df(self, category_value:int):
        selector = self.table_dataframe["category"] == category_value
        df_by_category = self.table_dataframe[selector]
        return df_by_category

    def get_random_sample_from_df(self, category_value:int):
        print(f"language={self.language}, category_value={category_value}.")
        choice = self.table_dataframe.sample(n=1)
        if category_value !=0:
            df_language_filtered_by_category = self.get_category_from_df(category_value)
            choice = df_language_filtered_by_category.sample(n=1)
        sentence = choice["sentence"].iloc[0]
        print(f"sentence={sentence} ...")
        return [sentence]


sample_folder = Path(__file__).parent / "databases"
lambda_database = {}
lambda_ipa_converter = {}
available_languages = ['de', 'en']

for lang in available_languages:
    # avoid using ";" or "," as separator because these are present within the dataframe sentences
    df = pd.read_csv(sample_folder / f'data_{lang}.csv', delimiter='|')
    lambda_database[lang] = TextDataset(df, lang)
    lambda_ipa_converter[lang] = RuleBasedModels.get_phonem_converter(lang)

lambda_translate_new_sample = False


def lambda_handler(event, context):
    """
    lambda handler to return a random text sample from the dataset.

    Parameters:
        event (dict): The event data passed to the Lambda function.
        context (dict): The context in which the Lambda function is called.

    Returns:
        str: The JSON-encoded result.
    """
    try:
        body = json.loads(event['body'])

        try:
            category = int(body['category'])
        except KeyError:
            category = 0
        language = body['language']
        try:
            current_transcript = str(body["transcript"])
        except KeyError:
            current_transcript = get_random_selection(language, category)
        current_ipa = lambda_ipa_converter[language].convertToPhonem(current_transcript)

        print(f"real_transcript='{current_transcript}', ipa_transcript='{current_ipa}'.")
        result = {
            'real_transcript': [current_transcript],
            'ipa_transcript': current_ipa,
            'transcript_translation': ""
        }

        return json.dumps(result)
    except Exception as ex:
        print("ex:", ex, "#")
        raise ex


def get_random_selection(language: str, category: int) -> str:
    """
    Get a random text sample from the dataset.

    Parameters:
        language (str): The language code.
        category (int): The category value to filter the dataset.

    Returns:
        str: The selected text sample.
    """
    lambda_df_lang = lambda_database[language]
    current_transcript = lambda_df_lang.get_random_sample_from_df(category)
    print(f"category={category}, language={language}, current_transcript={current_transcript}.")
    return current_transcript[0]


def getSentenceCategory(sentence) -> int | None:
    number_of_words = len(sentence.split())
    categories_word_limits = [0, 8, 20, 100000]
    for category in range(len(categories_word_limits)-1):
        if categories_word_limits[category] < number_of_words <= categories_word_limits[category + 1]:
            return category+1
    raise ValueError(f"category not assigned for sentence '{sentence}' ...")


def get_enriched_dataframe_csv(
        language: str,
        custom_dataframe_csv_filename_no_ext: str = "data",
        custom_folder: Path = sample_folder
) -> None:
    """
    Read a csv dataframe adding a 'category' column.

    Parameters:
        language (str): The language code (e.g. "de" for German).
        custom_dataframe_csv_filename_no_ext (str): The csv dataframe without extension.
        custom_folder (Path): The folder containing the csv dataframe.

    Returns:
        None
    """
    custom_folder = Path(custom_folder).absolute()
    df_filename = custom_folder / f'{custom_dataframe_csv_filename_no_ext}_{language}.csv'
    with open(df_filename, 'r') as handle:
        df2 = pd.read_csv(handle, sep="|")
        df2["category"] = df2["sentence"].apply(getSentenceCategory)
        print("de_category added")
    output_path = custom_folder / f'{custom_dataframe_csv_filename_no_ext}_{language}.csv'
    df2.to_csv(output_path, index=False, sep="|")
    print(f"written {output_path} ...")


if __name__ == '__main__':
    get_enriched_dataframe_csv("de")
    get_enriched_dataframe_csv("en")
