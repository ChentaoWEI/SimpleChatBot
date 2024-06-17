import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, scrolledtext
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from utils import openai_api_key
from utils import parser, read_csv_references
from templates import enduce_prompt
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.pydantic_v1 import BaseModel, Field

references = read_csv_references('references.csv')
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

class repairEstimation(BaseModel):
    Overview: str = Field(description="对用户输入的车辆损伤部位和损伤程度的描述")
    Advice: str = Field(description="对用户的建议")
    Price: float = Field(description="维修报价")

# 初始化OpenAI语言模型
model = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key).with_structured_output(repairEstimation)
config = {"configurable": {"session_id": "abc11"}}


def judgement(input_dict):
    # 判断解析的结果是否已经获得了车辆损伤部位和损伤程度
    ans = {'part':False, 'severity':False}
    if input_dict['part'] != '未知':
        ans['part'] = True
    if input_dict['severity'] != '未知' and input_dict['severity'] in ['轻微', '正常', '严重']:
        ans['severity'] = True
    return ans



class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot")
        
        self.chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, state='disabled')
        self.chat_window.grid(row=0, column=0, padx=10, pady=10)
        
        self.input_field = tk.Entry(root, width=50)
        self.input_field.grid(row=1, column=0, padx=10, pady=10)
        self.input_field.bind("<Return>", self.send_message)
        self.problems = {}
        
        
        self.tree = ttk.Treeview(self.root, columns=("Key", "Value"), show="headings")
        self.tree.heading("Key", text="Key")
        self.tree.heading("Value", text="Value")
        self.tree.grid(row=2, column=0, sticky="nsew")
        self.root.grid_rowconfigure(2, weight=1)
        # self.columns = ("Key", "Value")
        # self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        # self.tree.heading("Key", text="Key")
        # self.tree.heading("Value", text="Value")
        
        self.new_conversation()
        self.display_message("System", "Please describe the issue with your car in detail.")
    
    
    def new_conversation(self):
        # self.chain = enduce_prompt | model
        self.chain = RunnableWithMessageHistory(
            enduce_prompt | model,
            get_session_history,
            input_messages_key="message",
        )
        self.config = config
        self.chat_window.config(state='normal')
        self.chat_window.delete(1.0, tk.END)
        self.chat_window.config(state='disabled')
        
    def send_message(self, event):
        user_input = self.input_field.get()
        if user_input:
            self.input_field.delete(0, tk.END)
            self.display_message("User", user_input)
            # 如果用户还没有描述车辆的损伤部位和损伤程度
            if not self.problems:
                problems = parser(user_input)
                self.problems = problems
                if judgement(problems)['part'] and judgement(problems)['severity']:
                    self.display_message("System", "感谢您的描述，我们已经获得了您车辆的损伤部位和损伤程度。")
                    self.display_message("System", f"损伤部位: {self.problems['part']}")
                    self.display_message("System", f"损伤程度: {self.problems['severity']}")
                    self.display_message("System", "请稍等，我们正在为您查询维修报价。")
                    message = f"损伤部位: {self.problems['part']}, 损伤程度: {self.problems['severity']}，用户输入: {user_input}"
                    response = self.chain.invoke(
                        {"message": message,"references":references,},
                        config = self.config
                    )

                    self.display_message("AI", response)
                    self.display_table(response)
                elif not judgement(problems)['part']:
                    self.display_message("System", "请再次描述您车辆的损伤部位。")
                elif not judgement(problems)['severity']:
                    self.display_message("System", "请再次描述您车辆的损伤程度。")
                else:
                    self.display_message("System", "请再次描述您车辆的损伤部位和损伤程度。")
            else:
                problems = parser(user_input)
                # 如果用户描述的车辆损伤部位和损伤程度和之前描述的一样
                if self.problems['part'] == problems['part'] and self.problems['severity'] == problems['severity']:
                    self.display_message("System", "您已经描述过了，请等待我们为您查询维修报价。")
                # 如果用户描述的车辆损伤部位和损伤程度和之前描述的不一样
                else:
                    self.problems = problems

                message = f"损伤部位: {self.problems['part']}, 损伤程度: {self.problems['severity']}，用户输入: {user_input}"
                response = self.chain.invoke(
                        {"message": message,"references":references,},
                        config = self.config
                    )
                self.display_message("AI", response)
                self.display_table(response)
            # self.display_message("AI", response)
    
    def display_message(self, sender, message):
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, f"{sender}: {message}\n")
        self.chat_window.config(state='disabled')
        self.chat_window.yview(tk.END)
        
    def display_table(self, response):
        # 清空表格
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 插入新数据
        for key,val in self.problems.items():
            self.tree.insert("", "end", values=(key, val))
        self.tree.insert("", "end", values=("维修报价", response.Price))
        # for fieldname, value in response:
        #     self.tree.insert("", "end", values=(fieldname, value))

        # 显示表格
        # self.tree.pack(fill=tk.BOTH, expand=True)

def open_chat_window():
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()

# 打开新的对话窗口
open_chat_window()
