# -*- coding: utf-8 -*-
"""groq_inference.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1e6JNc6A8u7yX0FJfW2akNS59a4-flxx7
"""

pip install langchain groq

pip install langchain-groq

import getpass
import os

# if "GROQ_API_KEY" not in os.environ:
#     os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")

from google.colab import userdata

GROQ_API_KEY = userdata.get('GROQ_API_KEY')

print("API Key loaded successfully")

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Initialize the model
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # groq_api_key=""
)

# Simple prompt
response = llm.invoke("Explain how photosynthesis works in simple terms.")
print(response.content)

res=llm.invoke("Can you convert text my name is abhishek in hindi")

res.content



"""## Output Parser"""

from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List,Literal

class Review(BaseModel):
  summary:str=Field(description="A Brief summary of resport")
  sentiment:Literal['pos','neg']=Field(description="Give me the sentiment of above report")

from langchain_core.prompts import ChatPromptTemplate,PromptTemplate

parser=PydanticOutputParser(pydantic_object=Review)

prompt=PromptTemplate(
    template="Based on text provided \n {text}\n\n{format_instruction}",
    input_variables=["text"],
    partial_variables={"format_instruction":parser.get_format_instructions()}
)

text="""The Apple iPhone 11 is a reliable and well-performing smartphone launched in 2019, featuring a powerful A13 Bionic chip, improved dual-camera system, and better battery life than its predecessors. It offers a 6.1-inch Liquid Retina display with vibrant colors and decent brightness, making it suitable for everyday use and media consumption. The device runs on iOS, ensuring smooth software updates and a secure ecosystem. Its Night mode and enhanced computational photography deliver impressive photo quality, especially in low light. However, the display lacks the higher resolution and ProMotion found in newer models. The iPhone 11 also misses out on features like a headphone jack and expandable storage. Some users find it slightly bulky compared to newer lightweight phones. While its performance remains strong for most tasks, it may struggle with future apps optimized for newer chips. Overall, the iPhone 11 is a solid choice for those seeking a durable, user-friendly phone at a more affordable price point."""

prompt.invoke({'text':text})

chain = prompt | llm | parser

res=chain.invoke({'text':"I had pruchased  One plus mobile. It has some hang issue. it gets slow some times and display is not up to the mark. Ealier version of One plus mobile has good performance but i find this One plus 9 model not good"})

print(res)



"""## Runnable"""

from langchain.schema.runnable import RunnablePassthrough,RunnableParallel,RunnableLambda

parser=StrOutputParser()

prompt1=PromptTemplate(
    template="Provide me a detailed about topic :{topic}",
    input_variables=["topic"]
)

prompt2=PromptTemplate(
    template="Based on the text provided give me a 5 point summary of the text {text}",
    input_variables=["text"]
)

## Sequential Chain

chain=prompt1 | llm | parser | prompt2 | llm | parser

response=chain.invoke({'topic':'Cancer'})

print(response)

## parallel Chain

prompt3=PromptTemplate(
    template="Merge the documents and give the complete text and its summary \n text:{text} \n\n summary:{summary}",
    input_variables=["text","summary"]
)

parallel_chain=RunnableParallel(
    {'text':RunnablePassthrough(),
    'summary':prompt2 | llm | parser}
)

merge_chain=prompt3 | llm | parser

chain = prompt1 | llm | parser |parallel_chain | merge_chain

response= chain.invoke({'topic':'Cancer'})

print(response)

## Conditional Chain

from langchain.schema.runnable import RunnableBranch

import random

prompt=PromptTemplate(
    template="give me a samll report about topic :{topic}",
    input_variables=['topic']
)

prompt3=PromptTemplate(
    template="Merge the documents and give the complete text and its length \n text:{report} \n\n length:{length}",
    input_variables=["report","length"]
)

parser=StrOutputParser()

# Function to clean unwanted newlines and whitespaces
def clean_text(text):
    return text.replace("\n\n", " ").replace("\n", " ").strip()

conditional_chain=RunnableBranch(
    (lambda x:len(x.split())>500 , RunnableParallel({'report':RunnablePassthrough(),'length':RunnableLambda(lambda x:f'The number is greater than 200{len(x.split())}')})),
    (lambda x:len(x.split())<=500, RunnableParallel({'report':RunnablePassthrough(),'length':RunnableLambda(lambda x:f'The number is smaller than 200{len(x.split())}')})),
    RunnablePassthrough()
)

merge_chain=prompt3 | llm | parser

chain = prompt | llm | parser| conditional_chain | merge_chain

res=chain.invoke({'topic':'black hole'})

print(res)

