from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_exa import ExaSearchRetriever, TextContentsOptions
from langchain_google_genai import ChatGoogleGenerativeAI
import os

os.environ["EXA_API_KEY"] = "cfe8b21e-8495-4173-9ec2-cd47ee61fb83"
os.environ["GOOGLE_API_KEY"] = "AIzaSyCN5vX6x7qDo3FVZqSYKyrpeA6Od3HCe4I"


def external_search(query1):
    # retrieve 5 documents, with content truncated at 1000 characters
    retriever = ExaSearchRetriever(
        k=10, text_contents_options=TextContentsOptions(max_length=200000)
    )

    prompt = PromptTemplate.from_template(
        """ You are a public-private partnership expert. Conduct the necessary benchmark studies that are very detailed to answer this prompt: {query}
        \n here are examples of already made benchmark studies you should follow: 
        Example 1: Free Industrial Zone Hualing Kutaisi 2, Georgia
1. Project presentation
The Hualing FIZ project started in June 2012 when the Georgian government and the Hualing 
Group (China) signed a memorandum on establishing a free industrial zone in the city of 
Kutaisi. For a US$ 40 million investment, the Hualing Group was granted 36 hectares of land 
for use.
The Hualing Free Industrial Zone is located in the city of Kutaisi on the premises of a former 
motorcar factory close both to a highway and to a railroad. The distance to the closest airport 
in 19 kilometers (less than 12 miles) and to the seaport in Poti  95 kilometers (less than 
60 miles).
The following products were manufactured in the zone: ferroalloys, solar panels, matrasses, 
paper, construction materials, furniture, and textile. Besides, wood and stone are processed 
in this Zone. It is worth noting that not only foreign companies are present here: around 
25% of the FIZ companies belong to Georgian citizens. Many companies located in the Zone 
use it as a logistic center that allows optimizing the import  warehouse  export commerce. 
A substantial portion of the Hualing FIZ businesses is engaged in processing wood and 
manufacturing consumer goods.
2. Project Contractuel Structure
The agreement between the Georgian government and the Hualing Group on establishing a 
tax haven was signed on May 20, 2015. This agreement granted the Hualing Group the 
status of the FIZ administrator. According to the agreement, the precise area of the Zone is 
359 251 square meters (around 429 660 square yards), and the contract duration is thirty 
years.
Over the two and a half years the Hualing FIZ has been in operation, it has managed to 
attract to Georgia US$ 70 million in investment money. As of June 2018, 130 business 
companies are registered in this Zone.                                                                                                                                                                                                                                                                                                                                                     3. Lessons Learned 
Strategic Partnership for Development: The collaboration between the Georgian government and the Hualing Group (China) reflects the importance of forming strategic partnerships to drive economic development. The Memorandum of Understanding signed in June 2012 paved the way for the establishment of the free industrial zone, leveraging a US$ 40 million investment from the Hualing Group.
Utilization of Brownfield Sites: The decision to locate the Free Industrial Zone on the premises of a former motorcar factory demonstrates the effective utilization of brownfield sites. Repurposing existing infrastructure can reduce initial investment costs and accelerate the project's implementation.
Inclusive Participation of Local Businesses:  Approximately 25% of the businesses in the Free Industrial Zone are owned by Georgian citizens, showcasing the inclusive participation of local businesses. This involvement not only fosters economic growth but also promotes a sense of ownership and community engagement.
Long-Term Contractual Commitment: The 30-year duration of the agreement between the Georgian government and the Hualing Group underscores the importance of long-term commitments for the success of industrial zone projects. Such extended contractual periods provide stability for investors and encourage sustained development.
Investment Attraction and Company Registration: The Free Industrial Zone has successfully attracted US$ 70 million in investment over two and a half years, with 130 registered business companies as of June 2018. This underscores the attractiveness of the project and its ability to stimulate economic activity and foreign direct investment.
Regular Monitoring and Evaluation: Regular monitoring and evaluation of the Free Industrial Zone's performance are essential for tracking progress and making informed decisions. This ongoing assessment allows for timely adjustments to strategies and ensures the sustained success of the project.
Example 2: Bir jdid proche du périmètee du projet de Sidi Rahal -Maroc
Projet dirrigation dune surface de 3200 ha à Azemmour-Bir jdid provinde del jadida 
1. Présentation du projet  
La zone touchée, qui s'est développée pour produire des légumes et des légumes, connaît 
désormais une baisse de l'activité agricole en raison de la rareté et de la salinisation des eaux 
souterraines, qui sont la seule source utilisée pour l'irrigation. L'objectif du projet est d'obtenir 
15 millions de m3/an d'eau de surface du bassin versant Oum Er-Rbia pour protéger l'irrigation 
d'une zone de 3 200 hectares, dont bénéficient plus de 600 agriculteurs.
Le projet prévoit la construction d'un ouvrage de captage au niveau du réservoir de Sidi Daoui, 
une station de pompage d'un débit de 1,3 m3/s, 7,5 km d'adduct et un réseau d'irrigation de 
160 km pour desservir les champs nécessitant des outils. avec des techniques d'irrigation 
goutte à goutte pour économiser et améliorer l'eau.                      
2.  Structure contractuelle du projet                                                                                                                                                                                                                                                                                                                                               Le projet d'un investissement de 366 millions de DH sera mis en uvre sur la base d'une 
concession d'un partenaire privé qui sera chargé de participer au financement, à la conception, 
à la construction et à la gestion des infrastructures d'irrigation pour une durée de 30 ans. 
Pour assurer la tarification de l'eau d'irrigation, qui tient compte de la solvabilité des 
agriculteurs, l'Etat consacre 321 MDH aux infrastructures du projet, soit 88% du coût total de 
l'investissement initial. 
Le recours au PPP vise à mettre en uvre et à gérer le projet selon les meilleurs standards de 
qualité, sur la base d'un cahier des charges détaillé sous stricte supervision, ce qui assurera la 
poursuite du projet avec une meilleure utilisation et récupération dans l'eau.
Le partenaire retenu dans l'appel d'offres international est la Société Nouvelle des Conduites 
d'Eau (SNCE), société marocaine qui a récemment créé une société dédiée au projet : « 
Société Nouvelle Doukkala des Eaux - SNDKE SA ».
En mars 2014, la délégation devrait lancer une campagne de souscription de projets auprès des 
agriculteurs et la construction devrait démarrer d'ici la fin de la même année.
Le projet a un impact socio-économique important sur la zone et devrait améliorer les revenus 
et les conditions de vie des bénéficiaires. Il sera possible de diversifier et d'intensifier la 
production agricole, notamment la gestion des marchés, l'arboriculture et l'élevage laitier. La 
création d'emplois a finalement été analysée selon 1 915 emplois directs (gestion de la 
production et périmètre) et 1 900 emplois indirects (démarrage et suivi de production). 
L'augmentation de la valeur ajoutée agricole est estimée à 175 MDH par an.                                                                                                                                                                                                                                                                   3. Leçons tirées                                                                                                                                                                                                                                                                                                                                                                                        
Réponse à la Pénurie d'Eau et Salinisation :

Le projet Bir Jdid démontre la nécessité de trouver des solutions innovantes face à la raréfaction et à la salinisation des eaux souterraines, qui affectent négativement l'activité agricole. Le passage à l'eau de surface peut contribuer à la durabilité de l'irrigation.
Adoption de Techniques d'Irrigation Efficaces :

L'intégration de techniques d'irrigation goutte à goutte dans le projet souligne l'importance d'adopter des pratiques agricoles plus efficaces et économes en eau. Cela témoigne d'une vision axée sur la durabilité et la préservation des ressources.
Partenariat Public-Privé (PPP) pour le Financement et la Gestion :

L'utilisation d'un modèle de partenariat public-privé (PPP) permet de mobiliser des ressources privées pour le financement, la conception, la construction et la gestion du projet. Cette approche peut renforcer l'efficacité opérationnelle et la viabilité financière à long terme.
Participation Financière de l'État et Tarification Juste de l'Eau :

L'État contribue significativement au projet, consacrant 88% du coût total initial d'investissement. Cela garantit un financement solide pour les infrastructures tout en permettant une tarification de l'eau d'irrigation équitable, tenant compte de la solvabilité des agriculteurs.
Supervision Rigoureuse et Cahier des Charges Détaillé :

L'accent mis sur une supervision stricte et un cahier des charges détaillé dans le cadre du PPP vise à assurer la qualité et la conformité aux normes élevées. Cela peut être considéré comme une leçon importante pour garantir la réussite des projets d'infrastructure.
Impact Socio-Économique Positif :

Le projet souligne l'importance d'évaluer l'impact socio-économique des initiatives. En générant des emplois directs et indirects, en diversifiant les activités agricoles et en augmentant la valeur ajoutée, le projet contribue au développement durable de la région.
Consultation Communautaire et Sensibilisation :

La campagne de souscription de projets auprès des agriculteurs souligne l'importance de la consultation communautaire et de la sensibilisation. Impliquer les bénéficiaires dès le début peut favoriser l'acceptation du projet et garantir son succès.
Diversification Agricole :

La possibilité de diversifier et d'intensifier la production agricole, y compris la gestion des marchés, l'arboriculture et l'élevage laitier, démontre la vision holistique du projet pour améliorer la résilience économique de la région.
    """
    )

    llm = ChatGoogleGenerativeAI(model="gemini-pro")

    chain = (
        RunnableParallel({"context": retriever, "query": RunnablePassthrough()})
        | prompt
        | llm
    )
    query = """

    Make sure to follow this structure and to make the flow of the paragraphs coherent. Rich and well structured paragraphs
    Each benchmark study should follow this structure:

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

#query1 = "benchmark study for operational Botanical Gardens PPP projects #in Tunisia"
#search_externally = external_search(query1)