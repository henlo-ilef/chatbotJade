from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_exa import ExaSearchRetriever, TextContentsOptions
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.retrievers import TavilySearchAPIRetriever
os.environ["GOOGLE_API_KEY"] = "AIzaSyDhpqwIfCULLr6Gv3s955rxIRXyRtDDyhk"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
os.environ['TAVILY_API_KEY'] = "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"

# Load model directly
llm_gemini = ChatGoogleGenerativeAI(model="gemini-pro")
from langchain_community.llms import CTransformers
mistral = CTransformers(model='tas444/mistral-7b-v2-Benchmark-Studies_PPP_GGUF',model_file="mistral-7b-v2-Benchmark-Studies_PPP_GGUF-unsloth.Q4_K_M.gguf",
                            model_type='llama',
                            config={'max_new_tokens': 12000,
                                    'temperature' :0.6,
                                    'top_k':60,
                                    'top_p':0.95,
                                    'context_length': 14000}
                            )
from langchain.llms import CTransformers
from langchain import PromptTemplate, LLMChain
config={'max_new_tokens': 12000,
                                'temperature' :0.2,
                                'top_k':60,
                                'top_p':0.95,
                                'context_length': 17000}
llm = CTransformers(model='TheBloke/Mistral-7B-Instruct-v0.2-GGUF',model_file="mistral-7b-instruct-v0.2.Q4_K_M.gguf", config=config)

def finetune_context(query):
    base_query = """
    This benchmark study should include:

    1.Project Overview:
    Here, the project is presented in general, covering:
    Components (e.g., length for highways, capacity for factories/stations/power plants, etc.)
    Location
    Etc.

    2.Project Contractual Structure:
    Identify:
    Stakeholders:
    Private Partner
    Public Partner
    PPP Mode (concession, joint-venture, PPP with public payment)
    PPP Structure (BOT, BOO, DBFOM, EPC+F, etc.)
    PPP Contract Duration
    Contract Signing Date
    Project Status (under construction, in the bidding phase, or operational)
    If the project is operational, specify the date of execution if possible
    Project Financing
    Debt/Equity Ratio
    Funding Sources
    Investment Costs (CAPEX)
    Operating Costs (OPEX if possible)
    Information on revenues if possible (source, amount of generated revenue, e.g., toll rates for highway projects, service fees, rent for real estate projects, etc.)
    Develop a graph for each project explaining the contractual structure (examples can be found in the benchmark study database).

    3.Lessons Learned/Recommendations/Best Practices/Mistakes to Avoid:
    The purpose of this section is to provide a concise and enlightening synthesis of key lessons drawn from the analysis of PPP project case studies, emphasizing successes, failures, best practices, and pitfalls to avoid. It aims to equip readers with practical knowledge and actionable recommendations for the design, implementation, and management of future PPP projects. This section should serve as a guide to:
    Identify and understand success factors
    Analyze the causes of failure
    Formulate specific recommendations
    Share best practices
    Highlight mistakes and pitfalls to avoid
    Identify the best PPP structure for the studied project

    All conclusions should be drawn from the benchmark projects studied and not simply from general, standard, and vague recommendations that apply to any project.
    """
    context = mistral.invoke(query+base_query)
    return context


retriever = TavilySearchAPIRetriever(k=10)
def get_project_name(text):
    template = """<s>[INST] You are a helpful, respectful analysis writer . Answer exactly in few words from the context
    Make sure to just give the names of the project, nothing else:
    {context}
    {question} [/INST] </s>
    """

    #### Prompt
    question_p = """What is the the project we're using as an example to conduct the benchmark study called"""
    context_p =text
    prompt = PromptTemplate(template=template, input_variables=["question","context"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    response = llm_chain.run({"question":question_p,"context":context_p})
    title= response
    return title

def get_info_title(title):
    #Getting the info on the title
    prompt = PromptTemplate.from_template(
    """You are a public private partnerships analysis expert. Give these information to each project example mentioned in the query :1.Project Overview:
    Here, the project is presented in general, covering:
    Components (e.g., length for highways, capacity for factories/stations/power plants, etc.)
    Location
    Etc.

    2.Project Contractual Structure:
    Identify:
    Stakeholders:
    Private Partner
    Public Partner
    PPP Mode (concession, joint-venture, PPP with public payment)
    PPP Structure (BOT, BOO, DBFOM, EPC+F, etc.)
    PPP Contract Duration
    Contract Signing Date
    Project Status (under construction, in the bidding phase, or operational)
    If the project is operational, specify the date of execution if possible
    Project Financing
    Debt/Equity Ratio
    Funding Sources
    Investment Costs (CAPEX)
    Operating Costs (OPEX if possible)
    Information on revenues if possible (source, amount of generated revenue, e.g., toll rates for highway projects, service fees, rent for real estate projects, etc.)
    Develop a graph for each project explaining the contractual structure (examples can be found in the benchmark study database).

    3.Lessons Learned/Recommendations/Best Practices/Mistakes to Avoid:
    The purpose of this section is to provide a concise and enlightening synthesis of key lessons drawn from the analysis of PPP project case studies, emphasizing successes, failures, best practices, and pitfalls to avoid. It aims to equip readers with practical knowledge and actionable recommendations for the design, implementation, and management of future PPP projects. This section should serve as a guide to:
    Identify and understand success factors
    Analyze the causes of failure
    Formulate specific recommendations
    Share best practices
    Highlight mistakes and pitfalls to avoid
    Identify the best PPP structure for the studied project
    this section should also include:
    "In this project, the "public authority" signed a (for example) 25 years availability payment PPP with "private partner name". *Risks** related to... were handled by while the commercial risks were assumed by...(public or private partner)then mention:
    the debt/ equity ratio of the project
    the challenges faced during the project
    financial performance of the project
    sources de revenue
    impact of inflation/exchange rate
    role of the government
    Guarantees
    And the mention any specific aspects such as contract renegotiation, role (leverage) of IFIs (international financial institutions etc...
    All conclusions should be drawn from the benchmark projects studied and not simply from general, standard, and vague recommendations that apply to any project.
    query: {query}
    <context>
    {context}
    </context"""
    )


    chain = (
        RunnableParallel({"context": retriever, "query": RunnablePassthrough()})
        | prompt
        | llm_gemini
    )

    docs = retriever.invoke(title)
    urls = [doc.metadata['source'] for doc in docs]

    # Affichage des URLs
    print(urls)
    query="""Give me these info: """
    info_title = chain.invoke(title)
    return info_title,urls

def update_finetuned_result(info_title,finetuned_text):
        
    template = """<s>[INST] You are a helpful, respectful analysis writer . Correct the information in the text1 based on the data in the text2. Don't change the structure of text1. I want the final output to be text1 corrected with information from text2. But keep the structure of text1 as the output meaning you should keep the project presentation, the contractual structure and the lessons learned sections, only correct and update them with information from text2 or add information from text2 to text1:
    \n text1: {text1}
    \n text2: {text2} [/INST] </s>
    """

    #### Prompt
    text1_p = finetuned_text
    text2_p =info_title
    prompt = PromptTemplate(template=template, input_variables=["text1","text2"])
    llm_chain = LLMChain(prompt=prompt, llm=llm_gemini)
    response = llm_chain.run({"text1":text1_p,"text2":text2_p})
    updated_text= response
    return updated_text
    
def update_analysis(updated_text,extra_info):
    
    template = """<s>[INST] You are a helpful, respectful analysis writer . Only correct the lessons learned section of this text so that it follows this structure: for each project there is an example on how it should go and what this section should include:
    "In this project, the "public authority" signed a (for example) 25 years availability payment PPP with "private partner name". *Risks** related to... were handled by while the commercial risks were assumed by...(public or private partner)then mention:
    the debt/ equity ratio of the project
    the challenges faced during the project
    financial performance of the project
    sources de revenue
    impact of inflation/exchange rate
    role of the government
    Guarantees
    And the mention any specific aspects such as contract renegotiation, role (leverage) of IFIs (international financial institutions etc...
    \n Here is extra information that can help you in the analysis : {extra_info}
    \n text: {text} [/INST]
     give me the whole original text as an output only update the lessons learned section so it follows the structure I showed you </s>
    """

    #### Prompt
    text = updated_text
    extra_info =extra_info
    prompt = PromptTemplate(template=template, input_variables=["text","extra_info"])
    llm_chain = LLMChain(prompt=prompt, llm=llm_gemini)
    response = llm_chain.run({"text":text,"extra_info":extra_info})
    return response
def correct_french(updated_text):
    print("starting update2")
    final_result = llm_gemini.invoke("Correct the French of this text: "+ updated_text)
    print("finished update 2 within function")
    return final_result

def get_final_result(query):
    finetuned_context = finetune_context(query)
    print(finetuned_context)
    title = get_project_name(finetuned_context)
    info_title, urls = get_info_title(title)
    print("info extracted")
    updated_text = update_finetuned_result(info_title, finetuned_context)
    print("update 1 done")
    final_result = update_analysis(updated_text,info_title.content)
    print("update 2 done")
    if "é" in query:
        print("starting french correction")
        final_result = correct_french(updated_text).content 
        print("french corrected")
    return final_result + "\n" +urls

#query = 
"""
finetuned_context = finetune_context(query)
print("*************FINETUNEDCONTEXT********************\n ",finetuned_context)
title = get_project_name(finetuned_context)
print("*************PROJECTTITLE********************\n ",title)
info_title,urls = get_info_title(title)
print("*************INFOTITLE********************\n ",info_title)
updated_text=update_finetuned_result(info_title,finetuned_context)
print("*************UPDATEDTEXT********************\n ",updated_text)
fused_text = text_fusion(updated_text,info_title)
print("*************FINALRESULTFUSION*********************************************************************************************************************************************************************************************************************************\n ",fused_text)
corrected_french = correct_french(fused_text)
print("**********************************************CORRECTEDFRENCH***********************"+corrected_french.content)"""