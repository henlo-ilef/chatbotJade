
def external_search(query1):
    # retrieve 5 documents, with content truncated at 1000 characters
    retriever = ExaSearchRetriever(
        k=10, text_contents_options=TextContentsOptions(max_length=200000)
    )

    prompt = PromptTemplate.from_template(
        """ You are a public-private partnership expert. Conduct the necessary benchmark studies that are very detailed to answer this prompt: {query}
         """
    )


    chain = (
        RunnableParallel({"context": retriever, "query": RunnablePassthrough()})
        | prompt
        | llm
    )
    query = """
    qui repondent a ces question:
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

    Make sure its a well structured document and not bullet points. It should include well elaborated paragraphs etc.

    Provide the urls as a source.
    """


    result = chain.invoke(query1+query)
    output = result.content
    print(output)
    return output

query1 = "Donne moi les informations sure:Port sec de Kigali - Rwanda"
search_externally = external_search(query1)


"""os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

# Load model directly
from langchain import HuggingFaceHub
llm = HuggingFaceHub(
    repo_id="katkout2313/mistral-7b-v2-PPPFinal_GGUF",
    model_kwargs={"temperature":0.2, "max_length":180},
    task="text-generation"

) """