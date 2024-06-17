from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from templates import extractor_template
import pandas as pd
import chardet

openai_api_key='Your OpenAI API Key'

def parser(customer_review):
    part_schema = ResponseSchema(
    name = "part",
    description = "车辆的哪一个位置受损了？ \
        如果找到该信息，则输出该部位名称，否则输出未知。"
    )
    severity_schema = ResponseSchema(
        name = "severity",
        description= "损伤程度：车辆受损的程度如何？ \
            车辆的损伤程度是轻微、正常还是严重？如果找到该信息，则输出该程度，否则输出未知。"
    )

    response_schemas = [part_schema, severity_schema]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    
    prompt = ChatPromptTemplate.from_template(template=extractor_template)
    messages = prompt.format_messages(text=customer_review, format_instructions=format_instructions)
    
    chat = ChatOpenAI(temperature=0.0, openai_api_key=openai_api_key)
    response = chat(messages)
    
    output_dict = output_parser.parse(response.content)
    return output_dict

def read_csv_references(file_path):  
    df = pd.read_csv(file_path)
    # print(df)
    # df = pd.read_csv(file_path)
    references = df.to_dict(orient='records')
    return references
    
    
    
    
    
    
    
    