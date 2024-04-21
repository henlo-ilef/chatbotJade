from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_community.llms import CTransformers
from langchain import PromptTemplate, LLMChain

os.environ["GOOGLE_API_KEY"] = "AIzaSyDhpqwIfCULLr6Gv3s955rxIRXyRtDDyhk"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
os.environ['TAVILY_API_KEY'] = "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"

# **************************************Loading the models directly**********************************
from langchain_community.llms import Ollama

mistral = Ollama(model="mistral")
mistralppp = Ollama(model="henloilef/pppmistral")
gemini = ChatGoogleGenerativeAI(model="gemini-pro")                        

def titre(Content):
    context =Content
    llm1 = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key="AIzaSyDhpqwIfCULLr6Gv3s955rxIRXyRtDDyhk",
                             temperature=0.3)


    question="Give me a title that resumes this message in 30 characters maximum :"+context

#chain.run(input_documents=context, question=question)
    result = llm1.invoke(question)
    return result.content

# ********************************Fine Tuned Context ********************************
def get_projects(query):
    template = """<s>[INST] Based on this query:{query} give me 4 Public private partnership projects that can help me conduct benchmark studies. Make sure they are public private partnerships that can help me conduct benchmark studies. Make sure the projects respect what is demanded in the query
    Only give me the projects titles seperated by a semicolon. Emphasis on the seperation using a semicolon and not a \n     [/INST] </s>
    """

    #### Prompt
    prompt = PromptTemplate(template=template, input_variables=["query"])
    llm_chain = LLMChain(prompt=prompt, llm=gemini)
    response = llm_chain.run({"query":query})
    projects = response.split(";")
    return projects

def get_projectPresentation(project):
    query = """
    You are a Public Private Partnerships analysis expert. Here is an Instruction:
    ### Input:
    I am working on a PPP project called """+project+""" . Give me this info so i can conduct benchmark studies using it. 1.Project Overview:
        Here, the project is presented in general, covering:
        Components (e.g., length for highways, capacity for factories/stations/power plants, etc.)
        Location
        Etc.
    ### Give it the appropriate benchmark study response

    """
    #### Prompt
    response = mistralppp.invoke(query)
    response = response.replace('### Response:\n', '').replace('{', '').rstrip('}')

    return response

def get_projectContract(project):
    query = """
    You are a Public Private Partnerships analysis expert. Here is an Instruction:
    ### Input:
    I am working on a PPP project """+project+""" . Give me its contractual structure that should include:
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

    ### Give it the appropriate benchmark study response

"""
    response = mistralppp.invoke(query)
    response = response.replace('### Response:\n', '').replace('{', '').rstrip('}')
    return response

retriever = TavilySearchAPIRetriever(k=15,include_images=True)
def get_info_title(project):
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

    query: {query}
    <context>
    {context}
    </context"""
    )


    chain = (
        RunnableParallel({"context": retriever, "query": RunnablePassthrough()})
        | prompt
        | gemini
    )

    docs = retriever.invoke(project)
    urls = [doc.metadata['source'] for doc in docs]
    images_list = []
    for document in docs:
        # Extraire les images de chaque document
        images = document.metadata['images']  # Assurez-vous que la structure de 'document' est correcte
        for image in images:
            if image not in images_list:  # Éviter les doublons
                images_list.append(image)

    # Affichage des URLs
    print(urls)
    info_title = chain.invoke(project)
    return info_title,urls,images_list[0]

def update_finetuned_result(info_title,finetuned_text):

    template = """<s>[INST] You are a helpful, respectful analysis writer . Correct the information in the text1 based on the data in the text2
        \n text1: {text1}
    \n text2: {text2}
    I want the output to be the same structure of the first text1. I want the output to be in a coherent paragraph format not bullet points
    [/INST] </s>
    """
    text1_p = finetuned_text
    text2_p =info_title
    prompt = PromptTemplate(template=template, input_variables=["text1","text2"])
    llm_chain = LLMChain(prompt=prompt, llm=mistral)
    response = llm_chain.run({"text1":text1_p,"text2":text2_p})
    updated_text= response
    return updated_text

def toEnglish(query):
    template = """<s>[INST] Translate this query to english:{query}     [/INST] </s>
    """
    prompt = PromptTemplate(template=template, input_variables=["query"])
    llm_chain = LLMChain(prompt=prompt, llm=gemini)
    response = llm_chain.run({"query":query})
    return response
def toFrench(text):
    template = """<s>[INST] Translate this text to french:{text}     [/INST] </s>
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    llm_chain = LLMChain(prompt=prompt, llm=gemini)
    response = llm_chain.run({"text":text})
    return response
 

def analyse_finetuned_result(benchmark_study):     
    #### Prompt
    template = """<s>[INST] You are a helpful, respectful analysis writer . Analyze the following benchmark studies and generate a lessons learned text that follows this structure (make it in paragraphs and not bullet points):
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
    All conclusions should be drawn from the benchmark projects studied and not simply from general, standard, and vague recommendations that apply to any project.    \n benchmark_study: {benchmark_study} [/INST] </s>
    """
    prompt = PromptTemplate(template=template, input_variables=["benchmark_study"])
    llm_chain = LLMChain(prompt=prompt, llm=gemini)
    response = llm_chain.run({"benchmark_study":benchmark_study})
    return response

def get_response(query):
    french = False
    if "é" in query:
        query = toEnglish(query)
        french = True
    projects = get_projects(query)
    print(projects)
    texts = []
    sources = []
    images = []
    i=0
    for project in projects:
        pp = get_projectPresentation(project)
        pc = get_projectContract(project)
        text = project + "\n" + pp + "\n" + pc 
        print(i)
        print(text)
        info_title,urls,image = get_info_title(project)
        images.append(image)
        updated_text = update_finetuned_result(info_title,text)
        urls = "\n".join(urls)
        updated_text += "\n" + "Sources: " + urls
        texts.append(updated_text)
        sources.append(urls)
        i+=1
    text = "\n".join(texts)
    print("analyzing **************************************************")
    analysis = analyse_finetuned_result(text)
    print(analysis)
    text += "\n" + analysis
    if french:
        text = toFrench(text)
    return text,images
    
query = """
I am involved in the implementation of the PPP project of the Single Window for Foreign Trade of Mauritania (GUCE), an initiative aimed at centralizing and digitizing all administrative processes related to foreign trade (import, export, transit). This system will replace previous, fragmented, and manual methods with an integrated computer solution that will handle pre-clearance to post-clearance steps. The GUCE will simplify and harmonize procedures while speeding up commercial operations through document digitization and reducing the need for physical travel for the parties involved.

In this context, I am looking for a benchmark study on similar technological PPP projects that have implemented non-physical solutions such as software, databases, digital platforms, and information systems. The objective is to understand the financing mechanisms of these projects, including funding sources and capital structures, such as the debt/equity ratio. This analysis will help guide strategic and financial decisions for the GUCE.
"""
projects = ['- Public Private Partnership for the Single Window for Foreign Trade of the Dominican Republic','\n- Public Private Partnership for the Single Window for Foreign Trade of Peru\n','- Public Private Partnership for the Single Window for Foreign Trade of Chile\n','- Public Private Partnership for the Single Window for Foreign Trade of Brazil']



