type Category = "Random" | "Easy" | "Medium" | "Hard";
type Language = "German" | "English";

type DataGetSample = {
    expectedText: string;
    category: Category;
    expectedIPA: string;
    language: Language;
}
export const dataGetSample: DataGetSample[] = [
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
