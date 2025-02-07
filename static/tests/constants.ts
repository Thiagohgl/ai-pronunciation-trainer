type Category = "Random" | "Easy" | "Medium" | "Hard";
type Language = "German" | "English";

type DataGetSample = {
    expectedText: string;
    category: Category;
    expectedIPA: string;
    language: Language;
}
interface CustomDataWithTestAudio extends DataGetSample {
    expectedRecordedIPAScript: string;
    expectedPronunciationAccuracy: string;
    expectedSectionAccuracyScore: string;
    testAudioFile: string;
}
export const dataGetSample: DataGetSample[] = [
    {
        expectedText: "Marie leidet an Hashimoto-Thyreoiditis.",
        category: "Random",
        expectedIPA: "/ maːriː laɪ̯dɛːt aːn haːshiːmoːtoː-tyːrɛːɔɪ̯diːtiːs. /",
        language: "German"
    },
    {
        expectedText: "Marie leidet an Hashimoto-Thyreoiditis.",
        category: "Easy",
        expectedIPA: "/ maːriː laɪ̯dɛːt aːn haːshiːmoːtoː-tyːrɛːɔɪ̯diːtiːs. /",
        language: "German"
    },
    {
        expectedText: "Es ist einfach, den Status quo beibehalten; das heißt aber nicht, dass das auch das Richtige ist.",
        category: "Medium",
        expectedIPA: "/ ɛːs ɪst aɪ̯nfax, dɛːn staːtuːs kvoː baɪ̯beːaltɛːn; daːs haɪ̯st aːbɛːr nɪçt, das daːs aʊ̯x daːs rɪçtiːɡɛː ɪst. /",
        language: "German"
    },
    {
        expectedText: "Diana kam in 𝑖ℎ𝑟𝑒𝑚 zweitbesten Kleid vorbei und sah genauso aus, wie es sich ziemt, wenn man zum Tee geladen wird.",
        category: "Hard",
        expectedIPA: "/ diːaːnaː kaːm iːn 𝑖ℎ𝑟𝑒𝑚 t͡svaɪ̯tbɛstɛːn klaɪ̯d foːrbaɪ̯ ʊnd zaː ɡɛːnaʊ̯zoː aʊ̯s, viː ɛːs zɪç t͡simt, vɛn maːn t͡suːm teː ɡɛːlaːdɛːn viːrd. /",
        language: "German"
    },
    {
        expectedText: "Mary has Hashimoto's.",
        category: "Random",
        expectedIPA: "/ ˈmɛri həz hashimoto's. /",
        language: "English"
    },
    {
        expectedText: "Mary has Hashimoto's.",
        category: "Easy",
        expectedIPA: "/ ˈmɛri həz hashimoto's. /",
        language: "English"
    },
    {
        expectedText: "Following the status quo is easy, but that doesn't necessarily mean it's the right thing to do.",
        category: "Medium",
        expectedIPA: "/ ˈfɑloʊɪŋ ðə ˈstætəs kwoʊ ɪz ˈizi, bət ðət ˈdəzənt ˌnɛsəˈsɛrəli min ɪts ðə raɪt θɪŋ tɪ du. /",
        language: "English"
    },
    {
        expectedText: "Diana came over, dressed in HER second-best dress and looking exactly as it is proper to look when asked out to tea.",
        category: "Hard",
        expectedIPA: "/ daɪˈænə keɪm ˈoʊvər, drɛst ɪn hər second-best drɛs ənd ˈlʊkɪŋ ɪgˈzæktli ɛz ɪt ɪz ˈprɑpər tɪ lʊk wɪn æst aʊt tɪ ti. /",
        language: "English"
    }
]

export const customDataWithTestAudio: CustomDataWithTestAudio[] = [
    {
        expectedText: "Hallo, wie geht es dir?",
        category: "Easy",
        expectedIPA: "/ haloː, viː ɡeːt ɛːs diːr? /",
        language: "German",
        expectedRecordedIPAScript: "/ haloː, viː ɡeːt ɛːs diːr? /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 0 - (",
        testAudioFile: "test_de_easy.wav"
    },
    {
        expectedText: "Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau.",
        category: "Medium",
        expectedIPA: "/ diː køːniːɡ-lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdɛŋkmaːl iːm statsbaːd bryːkɛːnaʊ̯. /",
        language: "German",
        expectedRecordedIPAScript: "/  diː køːniːɡ-lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdaŋkmaːl iːm statsbadbryːkɛːnaʊ̯. /",
        expectedPronunciationAccuracy: "67%",
        expectedSectionAccuracyScore: "| Score: 100 - (",
        testAudioFile: "test_de_medium.wav"
    },
    {
        expectedText: "Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau, einem Ortsteil des drei Kilometer nordöstlich gelegenen Bad Brückenau im Landkreis Bad Kissingen in Bayern.",
        category: "Hard",
        expectedIPA: "/ diː køːniːɡ-lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdɛŋkmaːl iːm statsbaːd bryːkɛːnaʊ̯, aɪ̯nɛːm oːrtstaɪ̯l dɛːs draɪ̯ kiːloːmɛːtɛːr noːrdœstlɪç ɡɛːlɛːɡɛːnɛːn baːd bryːkɛːnaʊ̯ iːm landkraɪ̯s baːd kɪzɪŋɛːn iːn baɪ̯ɛːrn. /",
        language: "German",
        expectedRecordedIPAScript: "/  diː køːniːɡ-lʊtvɛːɡaɪ̯çɛː ɪst aɪ̯n naːtuːrdaŋkmaːl iːm statsbaːd bryːkɛːnaʊ̯, aɪ̯nɛːm oːrt staɪ̯l dɛːs 3 km noːrdœstlɪç ɡɛːlɛːɡɛːnɛːn baːd bryːkɛːnaʊ̯ iːm landkraɪ̯sbaːd kɪzɪŋɛːn iːn baɪ̯ɛːrn. /",
        expectedPronunciationAccuracy: "77%",
        expectedSectionAccuracyScore: "| Score: 167 - (",
        testAudioFile: "test_de_hard.wav"
    },
    {
        expectedText: "Hi there, how are you?",
        category: "Easy",
        expectedIPA: "/ haɪ ðɛr, haʊ ər ju? /",
        language: "English",
        expectedRecordedIPAScript: "/ haɪ ðɛr, haʊ ər ju? /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 244 - (",
        testAudioFile: "test_en_easy.wav"
    },
    {
        expectedText: "Rome is home to some of the most beautiful monuments in the world.",
        category: "Medium",
        expectedIPA: "/ roʊm ɪz hoʊm tɪ səm əv ðə moʊst ˈbjutəfəl ˈmɑnjəmənts ɪn ðə wərld. /",
        language: "English",
        expectedRecordedIPAScript:  "/ roʊm ɪz hoʊm tɪ səm əv ðə moʊst ˈbjutəfəl ˈmɑnjəmənts ɪn ðə wərld. /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 344 - (",
        testAudioFile: "test_en_medium.wav"
    },
    {
        expectedText: "Some machine learning models are designed to understand and generate human-like text based on the input they receive.",
        category: "Hard",
        expectedIPA: "/ səm məˈʃin ˈlərnɪŋ ˈmɑdəlz ər dɪˈzaɪnd tɪ ˌəndərˈstænd ənd ˈʤɛnərˌeɪt human-like tɛkst beɪst ɔn ðə ˈɪnˌpʊt ðeɪ rɪˈsiv. /",
        language: "English",
        expectedRecordedIPAScript: "/ səm məˈʃin ˈlərnɪŋ ˈmɑdəlz ər dɪˈzaɪnd tɪ ˌəndərˈstænd ənd ˈʤɛnərˌeɪt human-like tɛkst beɪst ɔn ðə ˈɪnˌpʊt ðeɪ rɪˈsiv. /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 444 - (",
        testAudioFile: "test_en_hard.wav"
    }
]
