<div align="center">

<a href="https://posit-dev.github.io/pointblank/"><img src="https://posit-dev.github.io/pointblank/assets/pointblank_logo.svg" width="75%"/></a>

_सुंदर और शक्तिशाली डेटा वैलिडेशन_

[![Python Versions](https://img.shields.io/pypi/pyversions/pointblank.svg)](https://pypi.python.org/pypi/pointblank)
[![PyPI](https://img.shields.io/pypi/v/pointblank)](https://pypi.org/project/pointblank/#history)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pointblank)](https://pypistats.org/packages/pointblank)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/pointblank.svg)](https://anaconda.org/conda-forge/pointblank)
[![License](https://img.shields.io/github/license/posit-dev/pointblank)](https://img.shields.io/github/license/posit-dev/pointblank)

[![CI Build](https://github.com/posit-dev/pointblank/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/posit-dev/pointblank/actions/workflows/ci-tests.yaml)
[![Codecov branch](https://img.shields.io/codecov/c/github/posit-dev/pointblank/main.svg)](https://codecov.io/gh/posit-dev/pointblank)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Documentation](https://img.shields.io/badge/docs-project_website-blue.svg)](https://posit-dev.github.io/pointblank/)

[![Contributors](https://img.shields.io/github/contributors/posit-dev/pointblank)](https://github.com/posit-dev/pointblank/graphs/contributors)
[![Discord](https://img.shields.io/discord/1345877328982446110?color=%237289da&label=Discord)](https://discord.com/invite/YH7CybCNCQ)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1%20adopted-ff69b4.svg)](https://www.contributor-covenant.org/version/2/1/code_of_conduct.html)

</div>

<div align="center">
   <a href="../README.md">English</a> |
   <a href="README.fr.md">Français</a> |
   <a href="README.de.md">Deutsch</a> |
   <a href="README.it.md">Italiano</a> |
   <a href="README.es.md">Español</a> |
   <a href="README.pt-BR.md">Português</a> |
   <a href="README.nl.md">Nederlands</a> |
   <a href="README.zh-CN.md">简体中文</a> |
   <a href="README.ja.md">日本語</a> |
   <a href="README.ko.md">한국어</a> |
   <a href="README.ar.md">العربية</a>
</div>

## पॉइन्टब्लैंक क्या है?

पॉइन्टब्लैंक पाइथन के लिए एक शक्तिशाली, किन्तु सुंदर डेटा वैलिडेशन फ्रेमवर्क है जो डेटा क्वालिटी सुनिश्चित करने के तरीके को बदल देता है। इसके सहज, चेनेबल API के साथ, आप अपने डेटा को व्यापक गुणवत्ता जाँचों के खिलाफ तेज़ी से वैलिडेट कर सकते हैं और शानदार, इंटरैक्टिव रिपोर्ट्स के माध्यम से परिणाम देख सकते हैं जो डेटा की समस्याओं को तुरंत कार्रवाई योग्य बनाते हैं।

चाहे आप डेटा साइंटिस्ट हों, डेटा इंजीनियर, या एनालिस्ट, पॉइन्टब्लैंक आपको डेटा क्वालिटी की समस्याओं को पकड़ने में मदद करता है, इससे पहले कि वे आपके विश्लेषण या डाउनस्ट्रीम सिस्टम को प्रभावित करें।

## 30 सेकंड में शुरुआत करें

```python
import pointblank as pb

validation = (
   pb.Validate(data=pb.load_dataset(dataset="small_table"))
   .col_vals_gt(columns="d", value=100)             # मान > 100 वैलिडेट करें
   .col_vals_le(columns="c", value=5)               # मान <= 5 वैलिडेट करें
   .col_exists(columns=["date", "date_time"])       # कॉलम मौजूद हैं या नहीं जाँचें
   .interrogate()                                   # निष्पादित करें और परिणाम एकत्र करें
)

# REPL से वैलिडेशन रिपोर्ट प्राप्त करें:
validation.get_tabular_report().show()

# नोटबुक से बस इसका उपयोग करें:
validation
```

<div align="center">
<img src="https://posit-dev.github.io/pointblank/assets/pointblank-tabular-report.png" width="800px">
</div>

<br>

## पॉइन्टब्लैंक क्यों चुनें?

- **आपके मौजूदा स्टैक के साथ काम करता है**: पोलर्स, पांडास, डकडीबी, MySQL, पोस्टग्रेSQL, SQLite, पारक्वेट, PySpark, स्नोफ्लेक, और अधिक के साथ निर्बाध रूप से एकीकृत होता है!
- **सुंदर, इंटरैक्टिव रिपोर्ट्स**: क्रिस्टल-क्लियर वैलिडेशन परिणाम जो समस्याओं को हाइलाइट करते हैं और डेटा क्वालिटी को संप्रेषित करने में मदद करते हैं
- **संयोजनीय वैलिडेशन पाइपलाइन**: वैलिडेशन स्टेप्स को एक पूर्ण डेटा क्वालिटी वर्कफ्लो में श्रृंखलाबद्ध करें
- **थ्रेशोल्ड-आधारित अलर्ट**: कस्टम एक्शन्स के साथ 'चेतावनी', 'त्रुटि', और 'महत्वपूर्ण' थ्रेशोल्ड सेट करें
- **व्यावहारिक आउटपुट**: वैलिडेशन परिणामों का उपयोग टेबल्स को फ़िल्टर करने, समस्याग्रस्त डेटा निकालने, या डाउनस्ट्रीम प्रक्रियाओं को ट्रिगर करने के लिए करें

## वास्तविक जगत का उदाहरण

```python
import pointblank as pb
import polars as pl

# अपना डेटा लोड करें
sales_data = pl.read_csv("sales_data.csv")

# व्यापक वैलिडेशन बनाएं
validation = (
   pb.Validate(
      data=sales_data,
      tbl_name="sales_data",           # रिपोर्टिंग के लिए टेबल का नाम
      label="वास्तविक जगत का उदाहरण.",  # वैलिडेशन के लिए लेबल, रिपोर्ट में दिखता है
      thresholds=(0.01, 0.02, 0.05),   # चेतावनियों, त्रुटियों और महत्वपूर्ण समस्याओं के लिए थ्रेशोल्ड सेट करें
      actions=pb.Actions(              # किसी भी थ्रेशोल्ड उल्लंघन के लिए एक्शन्स परिभाषित करें
         critical="स्टेप {step} में बड़ी डेटा क्वालिटी समस्या मिली ({time})."
      ),
      final_actions=pb.FinalActions(   # संपूर्ण वैलिडेशन के लिए अंतिम एक्शन्स परिभाषित करें
         pb.send_slack_notification(
            webhook_url="https://hooks.slack.com/services/your/webhook/url"
         )
      ),
      brief=True,                      # प्रत्येक स्टेप के लिए स्वचालित रूप से जनरेट किए गए ब्रीफ जोड़ें
   )
   .col_vals_between(            # सटीकता के साथ संख्यात्मक रेंज जाँचें
      columns=["price", "quantity"],
      left=0, right=1000
   )
   .col_vals_not_null(           # सुनिश्चित करें कि '_id' से समाप्त होने वाले कॉलम में null मान नहीं हैं
      columns=pb.ends_with("_id")
   )
   .col_vals_regex(              # रेगुलर एक्सप्रेशन के साथ पैटर्न वैलिडेट करें
      columns="email",
      pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
   )
   .col_vals_in_set(             # श्रेणीबद्ध मान जाँचें
      columns="status",
      set=["pending", "shipped", "delivered", "returned"]
   )
   .conjointly(                  # कई शर्तों को जोड़ें
      lambda df: pb.expr_col("revenue") == pb.expr_col("price") * pb.expr_col("quantity"),
      lambda df: pb.expr_col("tax") >= pb.expr_col("revenue") * 0.05
   )
   .interrogate()
)
```

```
स्टेप 7 में बड़ी डेटा क्वालिटी समस्या मिली (2025-04-16 15:03:04.685612+00:00).
```

```python
# HTML रिपोर्ट प्राप्त करें जिसे आप अपनी टीम के साथ साझा कर सकें
validation.get_tabular_report().show("browser")
```

<div align="center">
<img src="https://posit-dev.github.io/pointblank/assets/pointblank-sales-data.png" width="800px">
</div>

```python
# एक विशिष्ट स्टेप से असफल रिकॉर्ड्स की रिपोर्ट प्राप्त करें
validation.get_step_report(i=3).show("browser")  # स्टेप 3 से असफल रिकॉर्ड्स प्राप्त करें
```

<div align="center">
<img src="https://posit-dev.github.io/pointblank/assets/pointblank-step-report.png" width="800px">
</div>

<br>

## कमांड लाइन इंटरफेस (CLI)

पॉइन्टब्लैंक में `pb` नामक एक शक्तिशाली CLI उपयोगिता शामिल है जो आपको कमांड लाइन से सीधे डेटा वैलिडेशन वर्कफ़लो चलाने की अनुमति देता है। CI/CD पाइपलाइनों, निर्धारित डेटा गुणवत्ता जांच, या त्वरित वैलिडेशन कार्यों के लिए परफेक्ट है।

<div align="center">
<img src="https://posit-dev.github.io/pointblank/assets/vhs/cli-complete-workflow.gif" width="800px">
</div>

**अपने डेटा की खोज करें**

```bash
# अपने डेटा का त्वरित पूर्वावलोकन प्राप्त करें
pb preview small_table

# GitHub URLs से डेटा पूर्वावलोकन
pb preview "https://github.com/user/repo/blob/main/data.csv"

# Parquet फाइलों में गुम मानों की जांच करें
pb missing data.parquet

# डेटाबेस कनेक्शन से स्तंभ सारांश जेनरेट करें
pb scan "duckdb:///data/sales.ddb::customers"
```

**आवश्यक वैलिडेशन चलाएं**

```bash
# डुप्लिकेट पंक्तियों की जांच करें
pb validate small_table --check rows-distinct

# GitHub से सीधे डेटा वैलिडेट करें
pb validate "https://github.com/user/repo/blob/main/sales.csv" --check col-vals-not-null --column customer_id

# Parquet डेटासेट में null मान न होने की पुष्टि करें
pb validate "data/*.parquet" --check col-vals-not-null --column a

# डिबगिंग के लिए असफल डेटा निकालें
pb validate small_table --check col-vals-gt --column a --value 5 --show-extract
```

**CI/CD के साथ एकीकृत करें**

```bash
# स्वचालन के लिए एक्जिट कोड का उपयोग करें (0 = पास, 1 = फेल)
pb validate small_table --check rows-distinct --exit-code
```

## विशेषताएं जो पॉइन्टब्लैंक को अलग बनाती हैं

- **पूर्ण वैलिडेशन वर्कफ्लो**: डेटा एक्सेस से वैलिडेशन से रिपोर्टिंग तक एक ही पाइपलाइन में
- **सहयोग के लिए बनाया गया**: सुंदर इंटरैक्टिव रिपोर्ट्स के माध्यम से सहकर्मियों के साथ परिणाम साझा करें
- **व्यावहारिक आउटपुट**: वही प्राप्त करें जिसकी आपको आवश्यकता है: गणना, निकासी, सारांश, या पूर्ण रिपोर्ट
- **लचीला परिनियोजन**: नोटबुक, स्क्रिप्ट या डेटा पाइपलाइन में उपयोग करें
- **अनुकूलन योग्य**: अपनी विशिष्ट आवश्यकताओं के अनुसार वैलिडेशन स्टेप्स और रिपोर्टिंग को अनुकूलित करें
- **अंतर्राष्ट्रीयकरण**: रिपोर्ट्स 20 से अधिक भाषाओं में जनरेट की जा सकती हैं, जिनमें अंग्रेजी, स्पेनिश, फ्रेंच और जर्मन शामिल हैं

## दस्तावेज़ीकरण और उदाहरण

हमारे [दस्तावेज़ीकरण साइट](https://posit-dev.github.io/pointblank) पर जाएँ:

- [यूजर गाइड](https://posit-dev.github.io/pointblank/user-guide/)
- [API संदर्भ](https://posit-dev.github.io/pointblank/reference/)
- [उदाहरण गैलरी](https://posit-dev.github.io/pointblank/demos/)
- [पॉइंटब्लॉग](https://posit-dev.github.io/pointblank/blog/)

## समुदाय से जुड़ें

हम आपसे सुनना पसंद करेंगे! हमसे जुड़ें:

- [GitHub Issues](https://github.com/posit-dev/pointblank/issues) बग रिपोर्ट और फीचर अनुरोधों के लिए
- [_Discord सर्वर_](https://discord.com/invite/YH7CybCNCQ) चर्चाओं और सहायता के लिए
- [योगदान दिशानिर्देश](https://github.com/posit-dev/pointblank/blob/main/CONTRIBUTING.md) यदि आप पॉइन्टब्लैंक को सुधारने में मदद करना चाहते हैं

## इंस्टॉलेशन

आप pip का उपयोग करके पॉइन्टब्लैंक इंस्टॉल कर सकते हैं:

```bash
pip install pointblank
```

आप Conda-Forge से पॉइन्टब्लैंक भी इंस्टॉल कर सकते हैं:

```bash
conda install conda-forge::pointblank
```

यदि आपके पास Polars या Pandas इंस्टॉल नहीं है, तो आपको पॉइन्टब्लैंक का उपयोग करने के लिए उनमें से एक को इंस्टॉल करने की आवश्यकता होगी।

```bash
pip install "pointblank[pl]" # Polars के साथ पॉइन्टब्लैंक इंस्टॉल करें
pip install "pointblank[pd]" # Pandas के साथ पॉइन्टब्लैंक इंस्टॉल करें
```

DuckDB, MySQL, PostgreSQL, या SQLite के साथ पॉइन्टब्लैंक का उपयोग करने के लिए, उपयुक्त बैकएंड के साथ Ibis इंस्टॉल करें:

```bash
pip install "pointblank[duckdb]"   # Ibis + DuckDB के साथ पॉइन्टब्लैंक इंस्टॉल करें
pip install "pointblank[mysql]"    # Ibis + MySQL के साथ पॉइन्टब्लैंक इंस्टॉल करें
pip install "pointblank[postgres]" # Ibis + PostgreSQL के साथ पॉइन्टब्लैंक इंस्टॉल करें
pip install "pointblank[sqlite]"   # Ibis + SQLite के साथ पॉइन्टब्लैंक इंस्टॉल करें
```

## तकनीकी विवरण

पॉइन्टब्लैंक, Polars और Pandas DataFrames के साथ काम करने के लिए [Narwhals](https://github.com/narwhals-dev/narwhals) का उपयोग करता है और डेटाबेस और फाइल फॉर्मेट सपोर्ट के लिए [Ibis](https://github.com/ibis-project/ibis) के साथ एकीकृत होता है। यह आर्किटेक्चर विभिन्न स्रोतों से टेबुलर डेटा को वैलिडेट करने के लिए एक सुसंगत API प्रदान करता है।

## पॉइन्टब्लैंक में योगदान देना

पॉइन्टब्लैंक के चल रहे विकास में योगदान देने के कई तरीके हैं। कुछ योगदान सरल हो सकते हैं (जैसे टाइपो ठीक करना, दस्तावेज़ीकरण में सुधार, फीचर अनुरोधों या समस्याओं के लिए इश्यूज दर्ज करना, आदि) और अन्य को अधिक समय और देखभाल की आवश्यकता हो सकती है (जैसे प्रश्नों के उत्तर देना और कोड परिवर्तन के साथ PRs सबमिट करना)। बस यह जानें कि आप जो भी मदद कर सकते हैं उसकी बहुत सराहना की जाएगी!

शुरू करने के बारे में जानकारी के लिए कृपया [योगदान दिशानिर्देश](https://github.com/posit-dev/pointblank/blob/main/CONTRIBUTING.md) पढ़ें।

## रोडमैप

हम सक्रिय रूप से पॉइन्टब्लैंक को इन विशेषताओं के साथ बढ़ा रहे हैं:

1. व्यापक डेटा क्वालिटी जाँच के लिए अतिरिक्त वैलिडेशन मेथड्स
2. उन्नत लॉगिंग क्षमताएं
3. थ्रेशोल्ड उल्लंघन के लिए मैसेजिंग एक्शन्स (स्लैक, ईमेल)
4. LLM-पावर्ड वैलिडेशन सुझाव और डेटा डिक्शनरी जनरेशन
5. पाइपलाइन पोर्टेबिलिटी के लिए JSON/YAML कॉन्फिगरेशन
6. कमांड लाइन से वैलिडेशन के लिए CLI उपयोगिता
7. विस्तारित बैकएंड समर्थन और प्रमाणीकरण
8. उच्च-गुणवत्ता दस्तावेज़ीकरण और उदाहरण

यदि आपके पास फीचर्स या सुधारों के लिए कोई विचार है, तो हमसे साझा करने में संकोच न करें! हम हमेशा पॉइन्टब्लैंक को बेहतर बनाने के तरीके तलाश रहे हैं।

## आचार संहिता

कृपया ध्यान दें कि पॉइन्टब्लैंक प्रोजेक्ट [योगदानकर्ता आचार संहिता](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) के साथ जारी किया गया है। <br>इस प्रोजेक्ट में भाग लेकर, आप इसके नियमों का पालन करने के लिए सहमत हैं।

## 📄 लाइसेंस

पॉइन्टब्लैंक MIT लाइसेंस के अंतर्गत लाइसेंस प्राप्त है।

© Posit Software, PBC.

## 🏛️ गवर्नेंस

इस प्रोजेक्ट का मुख्य रूप से रखरखाव
[Rich Iannone](https://bsky.app/profile/richmeister.bsky.social) द्वारा किया जाता है। अन्य लेखक कभी-कभी
इन कार्यों में सहायता कर सकते हैं।
