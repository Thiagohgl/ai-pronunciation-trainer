
import pandas as pd
import json
import RuleBasedModels
import epitran
import random
import pickle


class TextDataset():
    def __init__(self, table):
        self.table_dataframe = table
        self.number_of_samples = len(table)

    def __getitem__(self, idx):

        line = [self.table_dataframe['sentence'].iloc[idx]]
        return line

    def __len__(self):
        return self.number_of_samples


sample_folder = "./databases/"
lambda_database = {}
lambda_ipa_converter = {}
available_languages = ['de', 'en']

for language in available_languages:
    df = pd.read_csv(sample_folder+'data_'+language+'.csv',delimiter=';')
    lambda_database[language] = TextDataset(df)
    lambda_ipa_converter[language] = RuleBasedModels.get_phonem_converter(language)

lambda_translate_new_sample = False


def lambda_handler(event, context):

    body = json.loads(event['body'])

    category = int(body['category'])

    language = body['language']

    sample_in_category = False

    while(not sample_in_category):
        valid_sequence = False
        while not valid_sequence:
            try:
                sample_idx = random.randint(0, len(lambda_database[language]))
                current_transcript = lambda_database[language][
                    sample_idx]
                valid_sequence = True
            except:
                pass

        sentence_category = getSentenceCategory(
            current_transcript[0])

        sample_in_category = (sentence_category ==
                              category) or category == 0

    translated_trascript = ""

    current_ipa = lambda_ipa_converter[language].convertToPhonem(
        current_transcript[0])

    result = {'real_transcript': current_transcript,
              'ipa_transcript': current_ipa,
              'transcript_translation': translated_trascript}

    return json.dumps(result)


def getSentenceCategory(sentence) -> int:
    number_of_words = len(sentence.split())
    categories_word_limits = [0, 8, 20, 100000]
    for category in range(len(categories_word_limits)-1):
        if number_of_words > categories_word_limits[category] and number_of_words <= categories_word_limits[category+1]:
            return category+1
