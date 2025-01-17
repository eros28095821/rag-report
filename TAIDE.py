import subprocess
import re

# 自定义函数，用于从输入中提取信息并生成律师函
def extract_case_data(lawyer_text):
    # 使用正则表达式提取关键信息
    原告 = re.search(r'原告：(.+?)，', lawyer_text).group(1) if re.search(r'原告：(.+?)，', lawyer_text) else "未知原告"
    被告 = re.search(r'被告：(.+?)，', lawyer_text).group(1) if re.search(r'被告：(.+?)，', lawyer_text) else "未知被告"
    事故緣由 = re.search(r'事故發生緣由\s*(.+?)\s*二、', lawyer_text, re.DOTALL).group(1).strip() if re.search(r'事故發生緣由\s*(.+?)\s*二、', lawyer_text, re.DOTALL) else "未知事故緣由"
    事故時間 = re.search(r'事故發生時間：(.+?)\s*事故地點：', lawyer_text).group(1) if re.search(r'事故發生時間：(.+?)\s*事故地點：', lawyer_text) else "未知時間"
    事故地點 = re.search(r'事故地點：(.+?)\s*醫藥費用：', lawyer_text).group(1) if re.search(r'事故地點：(.+?)\s*醫藥費用：', lawyer_text) else "未知地點"

    # 这里可以优化正则表达式以确保能提取到金额
    醫藥費用 = re.search(r'醫藥費用：([\d,]+)元', lawyer_text).group(1).replace(',', '') if re.search(r'醫藥費用：([\d,]+)元', lawyer_text) else "0"
    看護費用 = re.search(r'看護費用：([\d,]+)元', lawyer_text).group(1).replace(',', '') if re.search(r'看護費用：([\d,]+)元', lawyer_text) else "0"
    喪失工作所得 = re.search(r'喪失工作所得：([\d,]+)元', lawyer_text).group(1).replace(',', '') if re.search(r'喪失工作所得：([\d,]+)元', lawyer_text) else "0"
    精神慰撫金 = re.search(r'精神慰撫金：([\d,]+)元', lawyer_text).group(1).replace(',', '') if re.search(r'精神慰撫金：([\d,]+)元', lawyer_text) else "0"
    總金額 = re.search(r'總金額：([\d,]+)元', lawyer_text).group(1).replace(',', '') if re.search(r'總金額：([\d,]+)元', lawyer_text) else "0"
     # 打印提取的信息以供调试
    print("提取的信息:")
    print(f"原告: {原告}, 被告: {被告}, 醫藥費用: {醫藥費用}, 看護費用: {看護費用}, 喪失工作所得: {喪失工作所得}, 精神慰撫金: {精神慰撫金}, 總金額: {總金額},事故時間: {事故時間},  事故地點: {事故地點}")
    return {
        '原告': 原告,
        '被告': 被告,
        '事故緣由': 事故緣由,
        '醫藥費用': 醫藥費用,
        '看護費用': 看護費用,
        '喪失工作所得': 喪失工作所得,
        '精神慰撫金': 精神慰撫金,
        '總金額': 總金額,
        '事故時間': 事故時間,
        '事故地點': 事故地點,
    }
# 自定义函数，用于生成律师函
def generate_lawyer_letter(case_data):
    # 创建生成的律師函的提示文本
    prompt = f"""
    你是一個中華民國的民法專長的律師，你要根據中華民國民法正確引用民法法條，並且要正確引用以下的中華民國民法內容。
######
第 184 條
因故意或過失，不法侵害他人之權利者，負損害賠償責任。故意以背於善良風俗之方法，加損害於他人者亦同。
違反保護他人之法律，致生損害於他人者，負賠償責任。但能證明其行為無過失者，不在此限。
第 185 條
數人共同不法侵害他人之權利者，連帶負損害賠償責任。不能知其中孰為加害人者亦同。
造意人及幫助人，視為共同行為人。
第 191 條
土地上之建築物或其他工作物所致他人權利之損害，由工作物之所有人負賠償責任。但其對於設置或保管並無欠缺，或損害非因設置或保管有欠缺，或於防止損害之發生，已盡相當之注意者，不在此限。
前項損害之發生，如別有應負責任之人時，賠償損害之所有人，對於該應負責者，有求償權。
第 191-1 條
商品製造人因其商品之通常使用或消費所致他人之損害，負賠償責任。但其對於商品之生產、製造或加工、設計並無欠缺或其損害非因該項欠缺所致或於防止損害之發生，已盡相當之注意者，不在此限。
前項所稱商品製造人，謂商品之生產、製造、加工業者。其在商品上附加標章或其他文字、符號，足以表彰係其自己所生產、製造、加工者，視為商品製造人。
商品之生產、製造或加工、設計，與其說明書或廣告內容不符者，視為有欠缺。
商品輸入業者，應與商品製造人負同一之責任。
第 191-2 條
汽車、機車或其他非依軌道行駛之動力車輛，在使用中加損害於他人者，駕駛人應賠償因此所生之損害。但於防止損害之發生，已盡相當之注意者，不在此限。
第 191-3 條
經營一定事業或從事其他工作或活動之人，其工作或活動之性質或其使用之工具或方法有生損害於他人之危險者，對他人之損害應負賠償責任。但損害非由於其工作或活動或其使用之工具或方法所致，或於防止損害之發生已盡相當之注意者，不在此限。
第 193 條
不法侵害他人之身體或健康者，對於被害人因此喪失或減少勞動能力或增加生活上之需要時，應負損害賠償責任。
前項損害賠償，法院得因當事人之聲請，定為支付定期金。但須命加害人提出擔保。
第 195 條
不法侵害他人之身體、健康、名譽、自由、信用、隱私、貞操，或不法侵害其他人格法益而情節重大者，被害人雖非財產上之損害，亦得請求賠償相當之金額。其名譽被侵害者，並得請求回復名譽之適當處分。
前項請求權，不得讓與或繼承。但以金額賠償之請求權已依契約承諾，或已起訴者，不在此限。
前二項規定，於不法侵害他人基於父、母、子、女或配偶關係之身分法益而情節重大者，準用之。
######

你主要是要撰寫交通事故的民事起訴狀，並且只針對慰撫金部分的案件作撰寫。慰撫金基本上只會用到以上民法的內容，你閱讀完需要改寫的內容之後思考一下再使用正確的民法法條。
以下是一個正確的民事交通事故起訴狀的範本，請你根據使用者提供的內容，然後生成符合範本的內容，以下是我要你生成的訴訟狀的法律結構：
請根據以下信息生成一份完整的民事交通事故起訴狀，包括必要的法律條款和賠償項目：

請根據以下案件信息生成一份民事交通事故起訴狀：
請確保生成的起訴狀包含：
1. 事實緣由
2. 引用相關法條
3. 賠償請求及詳細說明

生成的起訴狀應使用法律術語，並按上述要求進行結構化。
請確保結構完整，使用法律術語，並引用相關的民法條款。起訴狀的結構如下：

一、事實緣由：
[在此填寫詳細的事實緣由，使用法律用語]

二、引用法條：
[在此引用相關的法律條款，例如第184條和第193條，並簡要說明適用情況]

三、賠償請求：
|---(一) 相關的賠償大項，以及說明，說明要很詳細。撰寫金額的時候統一使用'位數逗號的數字'；
|         |---1. 醫療費用：[金額]，說明要很詳細；
|---(六) 綜上所陳，請求總計賠償金額為：{case_data['總金額']}

    """

    # 使用 Ollama CLI 调用模型
    result = subprocess.run(
        ["ollama", "run", "jcai/llama3-taide-lx-8b-chat-alpha1:f16", prompt],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("生成律師函時出錯：", result.stderr)
        return None

    lawyer_letter = result.stdout.strip()
    
    return lawyer_letter

# 使用者輸入模擬律師內容
lawyer_text = """
一、 事故發生緣由

被告於民國99年1月14日23時59分許，駕駛車牌3423-UG號自用小貨車，沿屏東縣潮州鎮○○路由永德路西向東直行方向行駛，行至光春路與永德路路口前，未暫停讓幹線道車先行，因而碰撞行駛於幹線道之原告機車，致原告受有傷害。

二、 被告受傷情形

原告因被告上開行為，受有頭部外傷腦震盪、左股骨骨折、顏面裂傷2公分、左膝後十字韌帶撕裂性骨折之傷害。

三、 包含請求賠償的事實根據

原告因被告上開行為，支出醫療費用新臺幣25,940元；住院看護費用37,500元，及在家看護費用共計9萬元；又原告因上開車禍事故，受傷復原期間至少1年無法工作，以原告受傷前每月投保勞工保險薪資19,200元計算，受有工作收入損失115,200元；再者，原告因上開傷害住院三次，長期無法自由行動，原告身心、精神嚴重受創、痛苦甚深，請求精神慰撫金15萬元，以上請求項目金額合計418,640元，依據侵權行為法律關係，請求被告賠償等語，並聲明：被告應給付原告418,640元，及自起訴狀繕本送達被告翌日即99年12月5日起至清償日止，按週年利率百分之5計算之利息；願供擔保請准宣告假執行。

"""

# 提取案件資料
case_data = extract_case_data(lawyer_text)
# 手动输入更正信息
print("\n請手動更正提取的信息（直接按Enter保持不變）：")
原告 = input(f"原告（目前為 {case_data['原告']}）：") or case_data['原告']
被告 = input(f"被告（目前為 {case_data['被告']}）：") or case_data['被告']
醫藥費用 = input(f"醫藥費用（目前為 {case_data['醫藥費用']}）：") or case_data['醫藥費用']
看護費用 = input(f"看護費用（目前為 {case_data['看護費用']}）：") or case_data['看護費用']
喪失工作所得 = input(f"喪失工作所得（目前為 {case_data['喪失工作所得']}）：") or case_data['喪失工作所得']
精神慰撫金 = input(f"精神慰撫金（目前為 {case_data['精神慰撫金']}）：") or case_data['精神慰撫金']
總金額 = input(f"總金額（目前為 {case_data['總金額']}）：") or case_data['總金額']
事故時間 = input(f"事故時間（目前為 {case_data['事故時間']}）：") or case_data['事故時間']
事故地點 = input(f"事故地點（目前為 {case_data['事故地點']}）：") or case_data['事故地點']
# 更新案件资料
case_data['原告'] = 原告
case_data['被告'] = 被告
case_data['醫藥費用'] = 醫藥費用
case_data['看護費用'] = 看護費用
case_data['喪失工作所得'] = 喪失工作所得
case_data['精神慰撫金'] = 精神慰撫金
case_data['總金額'] = 總金額
case_data['事故時間'] = 事故時間
case_data['事故地點'] = 事故地點
# 打印最终的案件资料
print("\n最终的案件资料:")
print(case_data)
# 生成律師函並打印
lawyer_letter = generate_lawyer_letter(case_data)
if lawyer_letter:
    print("\n生成的律師函：\n", lawyer_letter)
