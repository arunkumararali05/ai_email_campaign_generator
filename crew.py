from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from langchain_groq import ChatGroq

@CrewBase
class emailCrew():
    agents_config = '/home/arun-kumar-arali/Downloads/Epsilon-Project/config/agents.yaml'
    tasks_config = '/home/arun-kumar-arali/Downloads/Epsilon-Project/config/tasks.yaml'

    def __init__(self, temperature) -> None:
        self.groq_llm = ChatGroq(temperature=temperature, model_name= "llama3-70b-8192")
        self.new_llm = ChatGroq(model_name = 'llama3-8b-8192')
    
    @agent
    def campaign_information_generator(self) -> Agent:
        return Agent(
            config = self.agents_config['campaign_information_generator'],
            llm = self.new_llm
        )
    @agent
    def email_marketing_expert(self) -> Agent:
        return Agent(
            config = self.agents_config['email_marketing_expert'],
            llm = self.groq_llm
        )
    @agent
    def final_output_editor(self) -> Agent:
        return Agent(
            config = self.agents_config['final_output_editor'],
            llm = self.groq_llm
        )
    
    @task
    def campaign_information_generation_task(self) -> Task:
        return Task(
            config = self.tasks_config['campaign_information_generation_task'],
            agent = self.campaign_information_generator()
        )
    @task
    def emailTask(self) -> Task:
        return Task(
            config = self.tasks_config['email_generation_task'],
            agent = self.email_marketing_expert()
        )
    @task
    def editorTask(self) -> Task:
        return Task(
            config = self.tasks_config['editor_task'],
            agent = self.final_output_editor()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents= self.agents,
            tasks = self.tasks,
            process = Process.sequential
        )
