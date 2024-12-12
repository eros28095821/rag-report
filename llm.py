import chainlit as cl
import pandas as pd
import re
from langchain_ollama import ChatOllama
# 定義清理函式
def clean_input_text(input_text):
    """
    清理用戶輸入文本：
    - 移除多餘空白字符和換行。
    - 替換全形空格為半形空格。
    """
    # 移除多餘空白字符和換行
    cleaned_text = re.sub(r'\s+', ' ', input_text.strip())
    # 將全形空格替換為半形空格
    cleaned_text = cleaned_text.replace("\u3000", " ")
    return cleaned_text
# 初始化模型
llm = ChatOllama(
    model="kenneth85/llama-3-taiwan:8b-instruct",
    temperature=0.1,
)

# 读取 Excel 文件并加载案件参考数据
def load_reference_cases(file_path, max_cases=5, max_chars_per_case=200):
    try:
        df = pd.read_excel(file_path, sheet_name='判決書550筆ver1')
        reference_cases = []
        for index, row in df.iterrows():
            case_summary = f"案件{index + 1}：原告{row.get('Unnamed: 5', '未知原告')}，被告{row.get('Unnamed: 6', '未知被告')}，事故緣由：{row.get('Unnamed: 7', '未知事故緣由')}。"
            reference_cases.append(case_summary[:max_chars_per_case])  # 截取到最大字符數
            if len(reference_cases) >= max_cases:
                break
        return reference_cases
    except Exception as e:
        print("读取 Excel 文件时出错：", e)
        return []

# 生成律师函
def generate_lawyer_letter(reference_cases, case_data):
    reference_text = "\n".join(reference_cases)
    compensation_details = "\n".join([f"    - {item}：{amount}元" for item, amount in case_data['賠償項目'].items()])

    case_exp = """
    範例案件1：在交通事故中，原告因被告駕駛車輛不當操作而受傷，引用第184條和第193條作為侵權賠償條款。
    範例案件2：多人共同造成原告受傷，但無法確定具體加害人時，引用第185條作為連帶賠償依據。
    範例案件3：被告駕駛機車行駛途中疏忽駕駛，撞傷行人，依第191-2條駕駛人應負賠償責任。
    範例案件4：被告在營業性運輸活動中操作失當，導致原告受傷，依第191-3條被告應負特別損害賠償責任。
    範例案件5：原告因被告在交通事故中造成重傷，依第193條請求其醫療費、看護費等損害賠償。
    範例案件6：原告因被告的過失行為遭受嚴重精神創傷，依第195條請求精神慰撫金。
    範例案件7：原告的車輛在交通事故中損壞，依第217條請求財產損害賠償。
    範例案件8：被告酒駕並肇事，原告引用《道路交通管理處罰條例》第62條以加強賠償依據。
    範例案件9：被告因超速駕駛導致車禍，原告引用《道路交通管理處罰條例》第43條，以證明被告違規行為。
    範例案件10：被告駕駛車輛未遵守安全駕駛規範，違反《道路交通管理處罰條例》第82條，原告引用此條款作為賠償依據。
    """
    prompt = f"""
    以下是一些已審結的案件摘要，可作為參考依據：
    {reference_text}{case_exp}

    根據以下新案件資料，生成一份完整的民事交通事故起訴狀草稿，包括詳細的事實描述、法律條款引用和賠償請求，格式要求如下：

    新案件資料：
    - 原告：{case_data['原告']}
    - 被告：{case_data['被告']}
    - 事故經過：{case_data['事故緣由']}
    - 賠償費用明細：
    {compensation_details}
    - 賠償費用總金額：{case_data['總金額']}元

    起訴狀格式應包括：
    一、事實緣由：
    描述事故發生的經過。

    二、被害結果：
    詳細描述原告受傷或財產損失情況，包含醫療需求、治療過程及後遺症。

    三、損害賠償的事實及金額：分別列出醫療費用、看護費用、工作損失、精神慰撫金等，並計算總金額。

    四、引用法律條款：
    明確列出相關的法律條款並根據案件的情況說明該條款如何適用於賠償請求。

    五、賠償請求：
    列出以上賠償項目及其金額，使用詳細說明以表達合理性。
    """
    try:
        response = llm.invoke([{"role": "user", "content": prompt}])
        lawyer_letter = response.content.replace("\\n", "\n")
        return lawyer_letter
    except Exception as e:
        print("生成律師函時出錯：", e)
        return None

@cl.on_chat_start
async def on_chat_start():
    try:
        file_path = "/home/chen/rag-copy/起訴狀案例測試.xlsx"
        reference_cases = load_reference_cases(file_path, max_cases=5, max_chars_per_case=200)
        cl.user_session.set("reference_cases", reference_cases)
        await cl.Message(content="系統已準備好！請開始提問。").send()
    except Exception as e:
        await cl.Message(content=f"初始化失敗：{str(e)}").send()


@cl.on_message
async def on_message(message: cl.Message):
    # 初始化 reference_cases
    reference_cases = None

    try:
        # 獲取參考案件
        reference_cases = cl.user_session.get("reference_cases")
        print("reference_cases:", reference_cases)
        if reference_cases is None:
            await cl.Message(content="請先重新啟動會話以加載參考案件資料！").send()
            return

        # 清理用戶輸入
        user_input = message.content.strip()
        cleaned_input = clean_input_text(user_input)

        # 模擬用戶案件資料
        case_data = {
            "原告": "陳秀珍",
            "被告": "蕭秀蘭",
            "事故緣由": cleaned_input,
            "賠償項目": {
                "醫藥費用": 23388,
                "看護費用": 198000,
                "喪失工作所得": 274800,
                "精神慰撫金": 2450000,
                "車輛修理費用": 54800,
            },
            "總金額": 3000988,
        }

        # 生成律師函
        lawyer_letter = generate_lawyer_letter(reference_cases, case_data)
        await cl.Message(content=f"生成的律師函：\n\n{lawyer_letter}").send()

    except Exception as e:
        await cl.Message(content=f"發生錯誤：{str(e)}").send()
