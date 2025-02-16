type Category = "Random" | "Easy" | "Medium" | "Hard";
type Language = "German" | "English";

export type DataGetSample = {
    expectedText: string;
    category: Category;
    expectedIPA: string;
    language: Language;
}
export interface CustomDataWithTestAudio extends DataGetSample {
    expectedRecordedIPAScript: string;
    expectedPronunciationAccuracy: string;
    expectedSectionAccuracyScore: string;
    testAudioFile: string;
    useDTW?: boolean;
}
export const dataGetSample: DataGetSample[] = [
    {
        expectedText: 'Er ist ein begeisterter Theaterliebhaber.',
        category: 'Random',
        expectedIPA: '/ ɛɐ̯ ɪst aɪ̯n bɛːɡaɪ̯stɛːrtɛːr tɛːaːtɛːrliːbhaːbɛːr. /',
        language: 'German'
    },
    {
        expectedText: 'Sie will niemanden heiraten.',
        category: 'Easy',
        expectedIPA: '/ ziː vɪl niːmandɛːn haɪ̯raːtɛːn. /',
        language: 'German'
    },
    {
        expectedText: 'Leg das Buch dorthin, wo du es gefunden hast.',
        category: 'Medium',
        expectedIPA: '/ lɛːɡ daːs bʊx doːrtiːn, voː duː ɛːs ɡɛːfʊndɛːn hast. /',
        language: 'German'
    },
    {
        expectedText: 'Eine Frau braucht neun Monate, um ein Kind zur Welt zu bringen, aber das heißt nicht, dass es neun zusammen in einem Monat schaffen könnten.',
        category: "Hard",
        expectedIPA: '/ aɪ̯nɛː fraʊ̯ braʊ̯xt nɔɪ̯n moːnaːtɛː, uːm aɪ̯n kɪnd t͡suːr vɛlt t͡suː brɪŋɛːn, aːbɛːr daːs haɪ̯st nɪçt, das ɛːs nɔɪ̯n t͡suːzamɛːn iːn aɪ̯nɛːm moːnaːt ʃafɛːn kœntɛːn. /',
        language: "German"
    },
    {
        expectedText: 'That was the first time, in the history of chess, that a machine (Deep Blue) defeated a Grand Master (Garry Kasparov).',
        category: 'Hard',
        expectedIPA: '/ ðət wɑz ðə fərst taɪm, ɪn ðə ˈhɪstəri əv ʧɛs, ðət ə məˈʃin (dip blu) dɪˈfitɪd ə grænd ˈmæstər (ˈgɛri ˈkæspərɑv). /',
        language: 'English'
    },
    {
        expectedText: 'He is a passionate theatregoer.',
        category: 'Random',
        expectedIPA: '/ hi ɪz ə ˈpæʃənət theatregoer. /',
        language: 'English'
    },
    {
        expectedText: 'Lemons are usually sour.',
        category: 'Easy',
        expectedIPA: '/ ˈlɛmənz ər ˈjuʒəwəli saʊər. /',
        language: 'English'
    },
    {
        expectedText: 'Tom read the Bible in its entirety, from the beginning to the end.',
        category: 'Medium',
        expectedIPA: '/ tɑm rɛd ðə ˈbaɪbəl ɪn ɪts ɪnˈtaɪərti, frəm ðə bɪˈgɪnɪŋ tɪ ðə ɛnd. /',
        language: 'English'
    }
    /**/
]

export const customDataWithTestAudioNoUseDTW: CustomDataWithTestAudio[] = [
    {
        expectedText: "Hallo, wie geht es dir?",
        category: "Easy",
        expectedIPA: "/ haloː, viː ɡeːt ɛːs diːr? /",
        language: "German",
        expectedRecordedIPAScript: "/ haloː, viː ɡeːt ɛːs diːr? /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 0 - (",
        testAudioFile: "test_de_easy.wav",
        useDTW: false
    },
    {
        expectedText: "Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau.",
        category: "Medium",
        expectedIPA: "/ diː køːniːɡ-lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdɛŋkmaːl iːm statsbaːd bryːkɛːnaʊ̯. /",
        language: "German",
        expectedRecordedIPAScript: "/  diː køːniːɡ-lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdaŋkmaːl iːm statsbadbryːkɛːnaʊ̯. /",
        expectedPronunciationAccuracy: "65%",
        expectedSectionAccuracyScore: "| Score: 100 - (",
        testAudioFile: "test_de_medium.wav",
        useDTW: false
    },
    {
        expectedText: "Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau, einem Ortsteil des drei Kilometer nordöstlich gelegenen Bad Brückenau im Landkreis Bad Kissingen in Bayern.",
        category: "Hard",
        expectedIPA: "/ diː køːniːɡ-lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdɛŋkmaːl iːm statsbaːd bryːkɛːnaʊ̯, aɪ̯nɛːm oːrtstaɪ̯l dɛːs draɪ̯ kiːloːmɛːtɛːr noːrdœstlɪç ɡɛːlɛːɡɛːnɛːn baːd bryːkɛːnaʊ̯ iːm landkraɪ̯s baːd kɪzɪŋɛːn iːn baɪ̯ɛːrn. /",
        language: "German",
        expectedRecordedIPAScript: "/  diː køːniːɡ lʊdviːɡ-aɪ̯çɛː ɪst aɪ̯n naːtuːrdaŋkmaːl iːm statsbaːd bryːkɛːnaʊ̯, aɪ̯nɛːm oːrt staɪ̯l dɛːs 3 km noːrdœstlɪç ɡɛːlɛːɡɛːnɛːn baːd bryːkɛːnaʊ̯ iːm landkraɪ̯sbaːd ɡɛːzɪŋɛːn iːn baɪ̯ɛːrn. /",
        expectedPronunciationAccuracy: "81%",
        expectedSectionAccuracyScore: "| Score: 165 - (",
        testAudioFile: "test_de_hard.wav",
        useDTW: false
    },
    {
        expectedText: "Hi there, how are you?",
        category: "Easy",
        expectedIPA: "/ haɪ ðɛr, haʊ ər ju? /",
        language: "English",
        expectedRecordedIPAScript: "/ haɪ ðɛr, haʊ ər ju? /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 246 - (",
        testAudioFile: "test_en_easy.wav",
        useDTW: false
    },
    {
        expectedText: "Rome is home to some of the most beautiful monuments in the world.",
        category: "Medium",
        expectedIPA: "/ roʊm ɪz hoʊm tɪ səm əv ðə moʊst ˈbjutəfəl ˈmɑnjəmənts ɪn ðə wərld. /",
        language: "English",
        expectedRecordedIPAScript:  "/ roʊm ɪz hoʊm tɪ səm əv ðə moʊst ˈbjutəfəl ˈmɑnjəmənts ɪn ðə wərld. /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 346 - (",
        testAudioFile: "test_en_medium.wav",
        useDTW: false
    },
    {
        expectedText: "Some machine learning models are designed to understand and generate human-like text based on the input they receive.",
        category: "Hard",
        expectedIPA: "/ səm məˈʃin ˈlərnɪŋ ˈmɑdəlz ər dɪˈzaɪnd tɪ ˌəndərˈstænd ənd ˈʤɛnərˌeɪt human-like tɛkst beɪst ɔn ðə ˈɪnˌpʊt ðeɪ rɪˈsiv. /",
        language: "English",
        expectedRecordedIPAScript: "/ səm məˈʃin ˈlərnɪŋ ˈmɑdəlz ər dɪˈzaɪnd tɪ ˌəndərˈstænd ənd ˈʤɛnərˌeɪt human-like tɛkst beɪst ɔn ðə ˈɪnˌpʊt ðeɪ rɪˈsiv. /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 446 - (",
        testAudioFile: "test_en_hard.wav",
        useDTW: false
    }
]

const customDataWithTestAudioWithUseDTW: CustomDataWithTestAudio[] = [
    {
        expectedText: "Hallo, wie geht es dir?",
        category: "Easy",
        expectedIPA: "/ hallo, wie geht ɛs dir? /",
        language: "German",
        expectedRecordedIPAScript: "/ hɛˈloʊ, haʊ ɪz ɪt goʊɪŋ? /",
        expectedPronunciationAccuracy: "35%",
        expectedSectionAccuracyScore: "| Score: 546 - (",
        testAudioFile: "test_de_easy.wav",
        useDTW: true
    },
    {
        expectedText: "Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau.",
        category: "Medium",
        expectedIPA: "/ daɪ könig-ludwig-eiche ist aɪn naturdenkmal ɪm staatsbad brückenau. /",
        language: "German",
        expectedRecordedIPAScript: "/ ðə köhne glət wie geiche ɪz ə ˈnæʧərəl ˈpeɪnɪŋ ɪn ðə ˈsɪti əv bæd brückenau. /",
        expectedPronunciationAccuracy: "53%",
        expectedSectionAccuracyScore: "| Score: 581 - (",
        testAudioFile: "test_de_medium.wav",
        useDTW: true
    },
    {
        expectedText: "Die König-Ludwig-Eiche ist ein Naturdenkmal im Staatsbad Brückenau, einem Ortsteil des drei Kilometer nordöstlich gelegenen Bad Brückenau im Landkreis Bad Kissingen in Bayern.",
        category: "Hard",
        expectedIPA: "/ daɪ könig-ludwig-eiche ist aɪn naturdenkmal ɪm staatsbad brückenau, einem ortsteil dɪ drei ˈkɪləˌmitər nordöstlich gelegenen bæd brückenau ɪm landkreis bæd kissingen ɪn bayern. /",
        language: "German",
        expectedRecordedIPAScript: "/ ðə kwin əv glutwig ɪz ə ˈnæʧərəl ˈpeɪnɪŋ ɪn ðə ˈsɪti əv bæd brückenau, ə pleɪs əv θri ˈkɪləˌmitərz nɔrθ əv ðə gegegenen bæd brückenau ɪn ðə landkreisbadgesingen ɪn bayern. /",
        expectedPronunciationAccuracy: "50%",
        expectedSectionAccuracyScore: "| Score: 634 - (",
        testAudioFile: "test_de_hard.wav",
        useDTW: true
    },
    {
        expectedText: "Hi there, how are you?",
        category: "Easy",
        expectedIPA: "/ haɪ ðɛr, haʊ ər ju? /",
        language: "English",
        expectedRecordedIPAScript: "/ haɪ ðɛr, haʊ ər ju? /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 684 - (",
        testAudioFile: "test_en_easy.wav",
        useDTW: true
    },
    {
        expectedText: "Rome is home to some of the most beautiful monuments in the world.",
        category: "Medium",
        expectedIPA: "/ roʊm ɪz hoʊm tɪ səm əv ðə moʊst ˈbjutəfəl ˈmɑnjəmənts ɪn ðə wərld. /",
        language: "English",
        expectedRecordedIPAScript:  "/ roʊm ɪz hoʊm tɪ səm əv ðə moʊst ˈbjutəfəl ˈmɑnjəmənts ɪn ðə wərld. /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 784 - (",
        testAudioFile: "test_en_medium.wav",
        useDTW: true
    },
    {
        expectedText: "Some machine learning models are designed to understand and generate human-like text based on the input they receive.",
        category: "Hard",
        expectedIPA: "/ səm məˈʃin ˈlərnɪŋ ˈmɑdəlz ər dɪˈzaɪnd tɪ ˌəndərˈstænd ənd ˈʤɛnərˌeɪt human-like tɛkst beɪst ɔn ðə ˈɪnˌpʊt ðeɪ rɪˈsiv. /",
        language: "English",
        expectedRecordedIPAScript: "/ səm məˈʃin ˈlərnɪŋ ˈmɑdəlz ər dɪˈzaɪnd tɪ ˌəndərˈstænd ənd ˈʤɛnərˌeɪt human-like tɛkst beɪst ɔn ðə ˈɪnˌpʊt ðeɪ rɪˈsiv. /",
        expectedPronunciationAccuracy: "100%",
        expectedSectionAccuracyScore: "| Score: 884 - (",
        testAudioFile: "test_en_hard.wav",
        useDTW: true
    }
]

export const objectUseDTW = {
    false: customDataWithTestAudioNoUseDTW,
    true: customDataWithTestAudioWithUseDTW
}