"""English and Hindi copy used by pages and reusable components."""
import streamlit as st

EN={
"nav_home":"Home","nav_check":"Check","nav_samples":"Samples","nav_insights":"Insights","language":"Language","eyebrow":"A clearer first step","headline":"Know your loan chances before you apply","subtext":"Explore how a lender might view your profile, understand the reasons, and see practical ways to improve.","start_check":"Check my loan readiness","sample_link":"See sample cases","feature1":"Instant check","feature1_body":"Get a quick educational estimate from the details you share.","feature2":"Clear reasons","feature2_body":"See which parts of your profile may help or hurt.","feature3":"How to improve","feature3_body":"Explore practical changes and see their effect on the estimate.","how_title":"How it works","step1":"Tell us about yourself","step1_body":"Share a few details about your income and credit history.","step2":"Explore your estimate","step2_body":"Review the dummy result and its plain-language reasons.","step3":"Try a what-if","step3_body":"Adjust a few numbers to explore possible changes.","privacy_note":"No sign-up needed. Nothing you enter is stored.","check_title":"Check your loan readiness","step_about":"About you","step_finances":"Your finances","step_loan":"The loan","back":"Back","continue":"Continue","run_check":"Check my readiness","summary":"Your loan summary","monthly_emi":"Monthly EMI","total_interest":"Total interest","total_repayment":"Total repayment","salary_emi":"Salary going to EMIs","affordability":"Affordability","afford_ok":"This looks manageable as a starting point.","afford_mid":"A large share of your income would go to EMIs.","afford_high":"This may leave little room for other expenses.","age":"Your age","employment":"Work type","salaried":"Salaried","self_employed":"Self-employed","job_years":"Years in your current job","home":"Where do you live?","rented":"Rented","own":"Own","own_loan":"Own with a home loan","credit_year":"Year of your first credit card or loan","income":"Yearly income","existing_emi":"Existing monthly EMIs","card_bill":"Credit card bill amount","card_usage":"How much of your card limit do you usually use?","very_little":"Very little (~10%)","third":"Around a third (~30%)","half":"About half (~50%)","almost_all":"Almost all (~90%)","no_card":"No credit card","open_accounts":"Open loans and cards","total_accounts":"Loans and cards ever","mort_accounts":"Home loans","public_records":"Past defaults or court records","bankruptcies":"Bankruptcies","cibil":"CIBIL range","cibil_help":"You can check your score for free through an RBI-registered credit bureau or your bank. This estimate does not use your CIBIL score.","excellent":"Excellent · 750+","good":"Good · 700–749","average":"Average · 650–699","low":"Low · below 650","dont_know":"Don't know","loan_amount":"Loan amount","tenure":"Repayment period","purpose":"What is the loan for?","rate":"Expected yearly interest rate (%)","years":"years","months":"months","p_debt":"Debt consolidation","p_card":"Credit card payoff","p_home":"Home improvement","p_purchase":"Big purchase","p_business":"Small business","p_vehicle":"Vehicle","p_medical":"Medical","p_other":"Other","validation":"Please check these details","income_positive":"Yearly income must be greater than zero.","loan_positive":"Loan amount must be greater than zero.","accounts_check":"Open accounts cannot be greater than total accounts.","year_check":"Please enter a valid first credit year.","estimated":"Estimated · one or more details used a safe default","checking":"Checking your profile…","strong":"Strong profile","risky":"Lenders may see this as risky","borderline":"A borderline profile","dummy_notice":"Rule-based demonstration only. This is not a lender decision or a trained model.","why":"Why this estimate?","improve":"How to improve","whatif":"What if you changed a few things?","reset":"Reset what-if","bank":"Bank rule checker","coming":"Coming soon","download":"Download report","whatsapp":"Share on WhatsApp","report":"Kreditly educational readiness estimate","report_dummy":"Dummy model · not a lender decision","risk":"Estimated risk","contributions":"What influenced this estimate","cases_title":"Example profiles","strong_tab":"Strong profiles","risky_tab":"Risky profiles","view_explanation":"View explanation","insights_title":"Model insights","todo":"TODO: replace after training","dataset":"Dataset overview","cleaning":"Cleaning steps","features":"Currency-free features","comparison":"Model comparison","confusion":"Confusion matrix","importance":"Feature importance","limitations":"Limitations and fairness","footer":"Built by Naina · INT395 Supervised Learning · Educational tool, not financial advice","reason_loan":"Your requested loan is {x}× your yearly income.","reason_dti":"About {x}% of monthly income already goes to existing EMIs.","reason_util":"You use about {x}% of your available card limit.","reason_records":"Past defaults or court records can make lenders cautious.","reason_bankruptcy":"Bankruptcy records can make lenders cautious.","reason_history":"A longer credit history can help show repayment habits.","reason_job":"Time in your current job may support income stability.","reason_mortgage":"A home loan history can add context to your credit record.","reason_term":"A longer repayment period can increase uncertainty.","reason_accounts":"Your number of active accounts is considered in this estimate.","tip_emi":"Reducing existing monthly EMIs by ₹{x} could free up room in your budget.","tip_loan":"Trying a smaller loan of ₹{x} may reduce the monthly commitment.","tip_card":"Paying down about ₹{x} of card balance may lower card usage.","wa_summary":"Kreditly estimate: {label}, estimated risk {risk}%. Educational tool only; not a lender decision.","case_strong1":"Steady income, modest loan","case_strong2":"Long credit history","case_strong3":"Low monthly commitments","case_strong4":"Small loan relative to income","case_risky1":"High existing EMIs","case_risky2":"Large loan request","case_risky3":"High card usage","case_risky4":"Shorter credit history"}
HI={
"nav_home":"होम","nav_check":"जाँचें","nav_samples":"उदाहरण","nav_insights":"जानकारी","language":"भाषा","eyebrow":"कर्ज़ से पहले एक साफ़ नज़र","headline":"आवेदन से पहले अपनी ऋण तैयारी जानें","subtext":"जानें कि ऋणदाता आपकी जानकारी को कैसे देख सकते हैं और आप क्या सुधार कर सकते हैं।","start_check":"मेरी ऋण तैयारी जाँचें","sample_link":"उदाहरण देखें","feature1":"तुरंत अनुमान","feature1_body":"आपकी दी जानकारी से एक शैक्षिक अनुमान पाएँ।","feature2":"साफ़ कारण","feature2_body":"देखें कि कौन सी बातें मदद या चिंता पैदा कर सकती हैं।","feature3":"सुधार के तरीके","feature3_body":"बदलाव करके अनुमान पर उनका असर देखें।","how_title":"यह कैसे काम करता है","step1":"अपने बारे में बताएँ","step1_body":"आय और क्रेडिट इतिहास की कुछ जानकारी दें।","step2":"अनुमान देखें","step2_body":"डमी मॉडल का नतीजा और उसके आसान कारण पढ़ें।","step3":"बदलाव करके देखें","step3_body":"कुछ राशियाँ बदलकर संभावित असर देखें।","privacy_note":"साइन अप की ज़रूरत नहीं। आपकी जानकारी सेव नहीं होती।","check_title":"अपनी ऋण तैयारी जाँचें","step_about":"आपके बारे में","step_finances":"आपकी आय और खर्च","step_loan":"ऋण","back":"पीछे","continue":"आगे","run_check":"मेरी तैयारी जाँचें","summary":"आपके ऋण का सार","monthly_emi":"हर महीने की किस्त","total_interest":"कुल ब्याज","total_repayment":"कुल भुगतान","salary_emi":"आय का हिस्सा जो किस्तों में जाता है","affordability":"भुगतान क्षमता","afford_ok":"शुरुआती तौर पर यह संभालने योग्य लगता है।","afford_mid":"आपकी आय का बड़ा हिस्सा किस्तों में जाएगा।","afford_high":"दूसरे खर्चों के लिए कम बच सकता है।","age":"आपकी उम्र","employment":"काम का प्रकार","salaried":"वेतनभोगी","self_employed":"स्वरोज़गार","job_years":"वर्तमान काम में साल","home":"आप कहाँ रहते हैं?","rented":"किराए पर","own":"अपना घर","own_loan":"गृह ऋण वाला अपना घर","credit_year":"पहले क्रेडिट कार्ड या ऋण का साल","income":"सालाना आय","existing_emi":"मौजूदा मासिक किस्तें","card_bill":"क्रेडिट कार्ड बिल की राशि","card_usage":"आप कार्ड की सीमा का कितना उपयोग करते हैं?","very_little":"बहुत कम (~10%)","third":"लगभग एक-तिहाई (~30%)","half":"लगभग आधा (~50%)","almost_all":"लगभग पूरी (~90%)","no_card":"क्रेडिट कार्ड नहीं","open_accounts":"चालू ऋण और कार्ड","total_accounts":"अब तक के ऋण और कार्ड","mort_accounts":"गृह ऋण","public_records":"पुराने डिफॉल्ट या अदालत के रिकॉर्ड","bankruptcies":"दिवालियापन के मामले","cibil":"CIBIL श्रेणी","cibil_help":"अपना स्कोर RBI-पंजीकृत क्रेडिट ब्यूरो या बैंक से मुफ़्त देख सकते हैं। यह अनुमान CIBIL स्कोर का उपयोग नहीं करता।","excellent":"बहुत अच्छा · 750+","good":"अच्छा · 700–749","average":"औसत · 650–699","low":"कम · 650 से नीचे","dont_know":"पता नहीं","loan_amount":"ऋण राशि","tenure":"भुगतान अवधि","purpose":"ऋण किसलिए है?","rate":"अनुमानित सालाना ब्याज (%)","years":"साल","months":"महीने","p_debt":"कई ऋण चुकाने के लिए","p_card":"क्रेडिट कार्ड चुकाने के लिए","p_home":"घर सुधार","p_purchase":"बड़ी खरीदारी","p_business":"छोटा व्यवसाय","p_vehicle":"वाहन","p_medical":"इलाज","p_other":"अन्य","validation":"कृपया जानकारी जाँचें","income_positive":"सालाना आय शून्य से अधिक होनी चाहिए।","loan_positive":"ऋण राशि शून्य से अधिक होनी चाहिए।","accounts_check":"चालू खाते कुल खातों से अधिक नहीं हो सकते।","year_check":"पहले क्रेडिट का सही साल भरें।","estimated":"अनुमानित · सुरक्षित डिफ़ॉल्ट इस्तेमाल हुआ","checking":"आपकी जानकारी देख रहे हैं…","strong":"अच्छी तैयारी","risky":"ऋणदाता इसे जोखिम भरा मान सकते हैं","borderline":"मध्यम तैयारी","dummy_notice":"नियमों पर आधारित प्रदर्शन मात्र। ऋणदाता का फैसला या प्रशिक्षित मॉडल नहीं।","why":"इस अनुमान का कारण","improve":"कैसे सुधारें","whatif":"कुछ बदलाव करके देखें","reset":"बदलाव रीसेट करें","bank":"बैंक नियम जाँच","coming":"जल्द आ रहा है","download":"रिपोर्ट डाउनलोड करें","whatsapp":"WhatsApp पर साझा करें","report":"Kreditly शैक्षिक तैयारी अनुमान","report_dummy":"डमी मॉडल · ऋणदाता का फैसला नहीं","risk":"अनुमानित जोखिम","contributions":"किन बातों का असर पड़ा","cases_title":"उदाहरण प्रोफ़ाइल","strong_tab":"अच्छी तैयारी","risky_tab":"जोखिम वाली तैयारी","view_explanation":"कारण देखें","insights_title":"मॉडल जानकारी","todo":"प्रशिक्षण के बाद बदलें","dataset":"डेटासेट की जानकारी","cleaning":"डेटा साफ़ करने के चरण","features":"मुद्रा रहित विशेषताएँ","comparison":"मॉडल तुलना","confusion":"कन्फ्यूज़न मैट्रिक्स","importance":"फ़ीचर महत्व","limitations":"सीमाएँ और निष्पक्षता","footer":"नैना द्वारा निर्मित · INT395 सुपरवाइज्ड लर्निंग · शैक्षिक टूल, वित्तीय सलाह नहीं","reason_loan":"आपका ऋण सालाना आय का {x} गुना है।","reason_dti":"मासिक आय का लगभग {x}% मौजूदा किस्तों में जाता है।","reason_util":"आप उपलब्ध कार्ड सीमा का लगभग {x}% उपयोग करते हैं।","reason_records":"पुराने डिफॉल्ट या अदालत के रिकॉर्ड से ऋणदाता सतर्क हो सकते हैं।","reason_bankruptcy":"दिवालियापन के रिकॉर्ड से ऋणदाता सतर्क हो सकते हैं।","reason_history":"लंबा क्रेडिट इतिहास भुगतान की आदतें दिखा सकता है।","reason_job":"मौजूदा काम में समय आय की स्थिरता दिखा सकता है।","reason_mortgage":"गृह ऋण का इतिहास आपके क्रेडिट रिकॉर्ड का संदर्भ दे सकता है।","reason_term":"लंबी भुगतान अवधि से अनिश्चितता बढ़ सकती है।","reason_accounts":"अनुमान में चालू खातों की संख्या भी शामिल है।","tip_emi":"मौजूदा मासिक किस्तें ₹{x} घटाने से बजट में जगह बन सकती है।","tip_loan":"₹{x} का छोटा ऋण लेने से मासिक भुगतान घट सकता है।","tip_card":"कार्ड बिल में लगभग ₹{x} चुकाने से उपयोग घट सकता है।","wa_summary":"Kreditly अनुमान: {label}, अनुमानित जोखिम {risk}%. केवल शैक्षिक जानकारी; ऋणदाता का फैसला नहीं।","case_strong1":"स्थिर आय, कम ऋण","case_strong2":"लंबा क्रेडिट इतिहास","case_strong3":"कम मासिक किस्तें","case_strong4":"आय के अनुपात में छोटा ऋण","case_risky1":"मौजूदा किस्तें अधिक","case_risky2":"ऋण राशि बड़ी","case_risky3":"कार्ड उपयोग अधिक","case_risky4":"क्रेडिट इतिहास छोटा"}

EN.update({"privacy_note":"No sign-up needed. Your entries stay in this session and are not saved to disk.","reason_low_loan":"Your requested loan is a smaller share of your yearly income.","reason_low_dti":"Only a small share of monthly income goes to existing EMIs.","reason_low_util":"You use a small share of your available card limit.","reason_no_records":"You reported no past defaults or court records.","reason_short_term":"The 36-month repayment period adds less time-related uncertainty.","reason_short_history":"Your credit history is still quite new.","reason_short_job":"You have spent a shorter time in your current job.","bank_card":"Bank rule checker · coming soon","sample_only":"Illustrative example · not research data","per_month":"/ month","slider_tenure":"Repayment period","simulator_result":"New estimate","feature_loan":"Loan compared with yearly income","feature_dti":"Existing monthly EMIs","feature_card":"Card limit used","feature_records":"Past defaults or court records","feature_bankruptcy":"Bankruptcy records","feature_job":"Time in current job","feature_history":"Credit history length","feature_home":"Home loans","feature_term":"Repayment period"})
HI.update({"privacy_note":"साइन अप की ज़रूरत नहीं। जानकारी इसी सेशन में रहती है और डिस्क पर सेव नहीं होती।","reason_low_loan":"आपकी ऋण राशि सालाना आय के अनुपात में कम है।","reason_low_dti":"मासिक आय का छोटा हिस्सा मौजूदा किस्तों में जाता है।","reason_low_util":"आप उपलब्ध कार्ड सीमा का छोटा हिस्सा उपयोग करते हैं।","reason_no_records":"आपने पुराने डिफॉल्ट या अदालत के रिकॉर्ड नहीं बताए।","reason_short_term":"36 महीने की अवधि से समय संबंधी अनिश्चितता कम रहती है।","reason_short_history":"आपका क्रेडिट इतिहास अभी नया है।","reason_short_job":"आप वर्तमान काम में कम समय से हैं।","bank_card":"बैंक नियम जाँच · जल्द आ रहा है","sample_only":"केवल उदाहरण · शोध डेटा नहीं","per_month":"/ महीना","slider_tenure":"भुगतान अवधि","simulator_result":"नया अनुमान","feature_loan":"सालाना आय के अनुपात में ऋण","feature_dti":"मौजूदा मासिक किस्तें","feature_card":"उपयोग की गई कार्ड सीमा","feature_records":"डिफॉल्ट या अदालत के रिकॉर्ड","feature_bankruptcy":"दिवालियापन के रिकॉर्ड","feature_job":"वर्तमान काम में समय","feature_history":"क्रेडिट इतिहास की अवधि","feature_home":"गृह ऋण","feature_term":"भुगतान अवधि"})

EN["contribution_axis"] = "Dummy contribution (direction only)"
HI["contribution_axis"] = "डमी योगदान (केवल दिशा)"
EN["reason_mid_history"]="Your credit history provides some repayment context."
HI["reason_mid_history"]="आपका क्रेडिट इतिहास भुगतान का कुछ संदर्भ देता है।"
EN["money_input_hint"]="Enter a non-negative amount using digits. Commas are optional."
HI["money_input_hint"]="राशि अंक में लिखें। कॉमा लगाना ज़रूरी नहीं है।"
EN["report_no_personal"]="No personal details are included."
HI["report_no_personal"]="इसमें कोई निजी जानकारी शामिल नहीं है।"
EN["vs_original"]="vs original"
HI["vs_original"]="पहले अनुमान से"

EN.update({
    "headline":"Explore a loan-readiness estimate",
    "subtext":"See how a profile relates to older U.S. LendingClub loan outcomes, understand the model factors, and try hypothetical changes. This model is not validated for Indian borrowers.",
    "start_check":"Explore an estimate",
    "feature3":"Try what-if changes",
    "feature3_body":"Explore hypothetical changes and see how the historical-model estimate responds.",
    "strong":"Lower historical risk estimate",
    "risky":"Higher historical risk estimate",
    "borderline":"Near the model cutoff",
    "improve":"Try hypothetical changes",
    "strong_tab":"Lower estimated risk",
    "risky_tab":"Higher estimated risk",
    "report_dummy":"Historical U.S. model estimate · not a lender decision",
    "contribution_axis":"SHAP contribution toward historical charge-off score",
    "dummy_notice":"Historical U.S. model estimate only. Not validated for Indian borrowers or a lender decision.",
    "step2_body":"Review the trained model estimate and its SHAP explanations.",
    "feature_loan_to_income":"Loan / yearly income",
    "feature_revol_bal_to_income":"Card balance / yearly income",
    "feature_dti":"Reported debt-to-income",
    "feature_revol_util":"Card limit used",
    "feature_open_acc":"Open accounts",
    "feature_total_acc":"Total credit accounts",
    "feature_pub_rec":"Public records",
    "feature_mort_acc":"Mortgage accounts",
    "feature_pub_rec_bankruptcies":"Bankruptcy records",
    "feature_term":"Repayment term",
    "feature_purpose":"Loan purpose",
    "feature_emp_length":"Employment length",
    "feature_credit_history_years":"Credit history length",
    "feature_home_ownership":"Home ownership",
    "home_other":"Other housing",
    "model_warning":"This model learned from older U.S. LendingClub loans. It has not been validated for Indian borrowers and cannot decide loan approval.",
    "model_higher":"This factor moved the model estimate toward higher historical charge-off risk: {detail}.",
    "model_lower":"This factor moved the model estimate toward lower historical charge-off risk: {detail}.",
    "factor_loan_to_income":"your requested loan is {x}× your yearly income",
    "factor_revol_bal_to_income":"your reported revolving balance is {x}% of yearly income",
    "factor_dti":"your reported debt-to-income value is {x}%",
    "factor_revol_util":"your reported card limit usage is {x}%",
    "factor_open_acc":"you report {x} open accounts",
    "factor_total_acc":"you report {x} total credit accounts",
    "factor_pub_rec":"you report {x} public records",
    "factor_mort_acc":"you report {x} mortgage accounts",
    "factor_pub_rec_bankruptcies":"you report {x} bankruptcy records",
    "factor_term":"your repayment term is {x} months",
    "factor_purpose":"the recorded loan purpose is {x}",
    "factor_emp_length":"you report {x} years in your current job",
    "factor_credit_history_years":"you report {x} years of credit history",
    "suggest_loan":"Try a loan amount of ₹{x}.",
    "suggest_emi":"If practical, lower existing monthly EMIs to ₹{x}.",
    "suggest_util":"A card usage level near {x}% may move this estimate.",
    "suggest_term":"Try a repayment term of {x} months.",
    "recommendation_note":"These are model what-if results, not promises or financial advice.",
    "no_counterfactual":"The model found no tested small change that moved this profile into STRONG.",
    "model_not_available":"The trained model artifacts are missing. Run the training notebook before starting the app.",
})
HI.update({
    "headline":"ऋण तैयारी का एक अनुमान देखें",
    "subtext":"देखें कि प्रोफ़ाइल पुराने अमेरिकी LendingClub ऋण परिणामों से कैसे जुड़ती है, मॉडल के कारण समझें और काल्पनिक बदलाव आज़माएँ। भारतीय उधारकर्ताओं के लिए यह मॉडल सत्यापित नहीं है।",
    "start_check":"अनुमान देखें",
    "feature3":"काल्पनिक बदलाव आज़माएँ",
    "feature3_body":"काल्पनिक बदलाव करके देखें कि पुराने मॉडल का अनुमान कैसे बदलता है।",
    "strong":"कम ऐतिहासिक जोखिम अनुमान",
    "risky":"अधिक ऐतिहासिक जोखिम अनुमान",
    "borderline":"मॉडल की सीमा के पास",
    "improve":"काल्पनिक बदलाव आज़माएँ",
    "strong_tab":"कम अनुमानित जोखिम",
    "risky_tab":"अधिक अनुमानित जोखिम",
    "report_dummy":"ऐतिहासिक अमेरिकी मॉडल अनुमान · ऋणदाता का फैसला नहीं",
    "contribution_axis":"ऐतिहासिक चार्ज-ऑफ स्कोर पर SHAP असर",
    "dummy_notice":"पुराने अमेरिकी डेटा पर आधारित अनुमान। भारतीय उधारकर्ताओं के लिए सत्यापित नहीं और ऋणदाता का फैसला नहीं।",
    "step2_body":"प्रशिक्षित मॉडल का अनुमान और SHAP कारण देखें।",
    "feature_loan_to_income":"ऋण / सालाना आय",
    "feature_revol_bal_to_income":"कार्ड बैलेंस / सालाना आय",
    "feature_dti":"बताया गया ऋण-आय अनुपात",
    "feature_revol_util":"उपयोग की गई कार्ड सीमा",
    "feature_open_acc":"खुले खाते",
    "feature_total_acc":"कुल क्रेडिट खाते",
    "feature_pub_rec":"सार्वजनिक रिकॉर्ड",
    "feature_mort_acc":"गृह-ऋण खाते",
    "feature_pub_rec_bankruptcies":"दिवालियापन रिकॉर्ड",
    "feature_term":"भुगतान अवधि",
    "feature_purpose":"ऋण का उद्देश्य",
    "feature_emp_length":"रोज़गार की अवधि",
    "feature_credit_history_years":"क्रेडिट इतिहास की अवधि",
    "feature_home_ownership":"घर का प्रकार",
    "home_other":"अन्य आवास",
    "model_warning":"यह मॉडल पुराने अमेरिकी LendingClub ऋणों से सीखा गया है। भारतीय उधारकर्ताओं के लिए इसका सत्यापन नहीं हुआ है और यह ऋण स्वीकृति तय नहीं कर सकता।",
    "model_higher":"इस विशेषता ने मॉडल के ऐतिहासिक चार्ज-ऑफ जोखिम अनुमान को बढ़ाया: {detail}।",
    "model_lower":"इस विशेषता ने मॉडल के ऐतिहासिक चार्ज-ऑफ जोखिम अनुमान को घटाया: {detail}।",
    "factor_loan_to_income":"आपकी मांगी गई ऋण राशि सालाना आय की {x} गुना है",
    "factor_revol_bal_to_income":"बताया गया कार्ड बैलेंस सालाना आय का {x}% है",
    "factor_dti":"आपका बताया गया ऋण-आय अनुपात {x}% है",
    "factor_revol_util":"आप कार्ड सीमा का {x}% उपयोग बताते हैं",
    "factor_open_acc":"आपके {x} खाते खुले हैं",
    "factor_total_acc":"आपके कुल {x} क्रेडिट खाते हैं",
    "factor_pub_rec":"आप {x} सार्वजनिक रिकॉर्ड बताते हैं",
    "factor_mort_acc":"आप {x} गृह-ऋण खाते बताते हैं",
    "factor_pub_rec_bankruptcies":"आप {x} दिवालियापन रिकॉर्ड बताते हैं",
    "factor_term":"आपकी भुगतान अवधि {x} महीने है",
    "factor_purpose":"दर्ज ऋण का उद्देश्य {x} है",
    "factor_emp_length":"आप वर्तमान काम में {x} साल बताते हैं",
    "factor_credit_history_years":"आप {x} साल का क्रेडिट इतिहास बताते हैं",
    "suggest_loan":"₹{x} की ऋण राशि आज़माएँ।",
    "suggest_emi":"यदि संभव हो, मौजूदा मासिक किस्तें ₹{x} तक घटाएँ।",
    "suggest_util":"कार्ड उपयोग लगभग {x}% करने से यह अनुमान बदल सकता है।",
    "suggest_term":"{x} महीने की भुगतान अवधि आज़माएँ।",
    "recommendation_note":"ये मॉडल पर आधारित कल्पित बदलाव हैं; वादा या वित्तीय सलाह नहीं।",
    "no_counterfactual":"जाँचे गए छोटे बदलावों में कोई भी इस प्रोफ़ाइल को अच्छी तैयारी तक नहीं ले गया।",
    "model_not_available":"प्रशिक्षित मॉडल फ़ाइलें नहीं मिलीं। ऐप शुरू करने से पहले प्रशिक्षण नोटबुक चलाएँ।",
})

def t(key: str, **values) -> str:
    dictionary = HI if st.session_state.get("language") == "हिं" else EN
    result = dictionary.get(key, EN.get(key, key))
    return result.format(**values) if values else result
