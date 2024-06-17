from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

enduce_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """你是一个汽车维修报价助手，通过对话引导用户输入汽车具体损坏部位和损坏程度。
            当你获得了汽车的损坏部位和损坏程度后，你将会根据用户的输入，输出汽车维修的报价。如果损坏部位或者损坏程度未知，你进一步询问有关信息。
            你可以参考过去的汽车维修报价数据，但是你不能直接输出历史数据，而是需要根据用户的输入，结合历史数据，输出一个新的报价。
            历史数据: {references}""",
        ),
        MessagesPlaceholder(variable_name="message"),
    ]
)

# enduce_template = """
# 你是一个汽车维修报价助手，通过对话引导用户输入汽车具体损坏部位和损坏程度。
# 在获得了汽车的损坏部位和损坏程度后，你将会根据用户的输入，输出汽车维修的报价。
# 你可以参考一些历史汽车维修报价的数据，但是你不能直接输出历史数据，而是需要根据用户的输入，结合历史数据，输出一个新的报价。

# {history}
# 历史数据: {references}
# 用户描述: {input}
# 实际损伤部位: {part}
# 实际损伤程度: {severity}
# 助手: 
# """

extractor_template = """\
对于以下文本，请从中提取以下信息：

车辆损伤部位：车辆的那一个位置受损了？ \
如果找到该信息，则输出该部位名称，否则输出未知。

损伤程度：车辆受损的程度如何？ \
车辆的损伤程度是轻微、正常还是严重？如果找到该信息，则输出该程度，否则输出未知。

使用以下键将输出格式化为 JSON：
- "part": 车辆损伤部位
- "severity": 损伤程度

文本: {text}
"""
