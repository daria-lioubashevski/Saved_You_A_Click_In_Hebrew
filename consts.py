ARTICLE_TITLE_COLUMN_NAME = 'art_title'
BODY_COLUMN_NAME = 'Body'
LABEL_COLUMN_NAME = POST_TEST_COLUMN_NAME = 'post_text'
MODEL_INPUT_COLUMN_NAME = 'Text'

FAILED_TO_OPEN_VAL = "FAILED"
SHORTEN_CODE = 'bit.ly'
BAD_ART_TITLE_STRINGS_REG = "None|Error|Page not found|Forbidden|404|Not Acceptable|Just a moment|הודעת שגיאה|העמוד לא נמצא"
NEWSPAPER_NAME_STRINGS = ['TheMarker', 'חדשות מעריב', 'הארץ', 'חדשות 13', 'רשת 13',
                          'N12', 'ישראל היום', 'טיים אאוט', 'מעריב', 'TMI', 'וואלה! כסף', 'וואלה! בריאות',
                          'tvbee', 'גיקטיים', 'ערוץ 7', 'וואלה!']
BAD_POST_TEXT_STRINGS_REG = "אמורה להיות המילה היחידה בהן|לא נכנסנו|אמ;לק|בתגובות|סתם"
POST_STRINGS_TO_REMOVE = ["שמחנו לעזור."]
ARTICLE_TITLE_STRINGS_TO_REMOVE = ["<.*>", "|", "<", ">"]
MAX_TITLE_POST_TEXT_SIMILAR_FACTOR = 0.6

MODEL_INPUT_FORMAT = "question: {} context: {}"
BAD_TOKENS = ['<extra_id_0>', '<extra_id_40>', '<extra_id_1>']
MODEL_INPUT_IDS = 'input_ids'
MODEL_ATTENTION_MASK = 'attention_mask'
MAX_GENERATION_LENGTH = 50

MT5_MODELS_DICT = {'mb': 'google/mt5-base',
                   'ml': 'google/mt5-large',
                   'mxl': 'google/mt5-xl'}

PADDING = "max_length"
TRAIN_CSV_PATH = "train.csv"
VALIDATION_CSV_PATH = "val.csv"

AMLK_PAGE_NAME = "this.is.amlk"
LINK_PATTERN = 'href="https://l.facebook.com/l.php\?..(.*?)\&amp\;'
BAIT_PATTERN_1 = '<div class="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"><div dir="auto" style="text-align: ?start;?">(.*?)<'
BAIT_PATTERN_2 = '<div class="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"><div dir="auto" style="text-align: ?start;?">.*?</span>(.*?)<'
BAIT_PATTERN_3 = ' -webkit-box;"><span dir="auto">(.*?)<'

TMI_PREFIX = 'tmi.maariv.co.il'
WALLA_PREFIX = 'walla.co.il'
MAKO_PREFIX = 'mako.co'
ISRAELHAYOM_PREFIX = 'israelhayom.co.il'
