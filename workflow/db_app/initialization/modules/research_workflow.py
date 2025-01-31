from typing import List, Dict, Any
from pydantic import Field
from workflow.db_app.initialization.modules.init_module import InitializationModule, get_prompt_file

class ResearchWorkflowModule(InitializationModule):
    """This module defines the research workflow, its tasks, agents and prompts."""
    name: str = "research_workflow"
    dependencies: List[str] = ["base", "base_tasks"]
    data: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

research_workflow_module = ResearchWorkflowModule(
    data={
        "parameters": [
            {
                "key": "outputs_research_brief_task",
                "type": "string",
                "description": "The research brief created based on the user prompt",
            },
            {
                "key": "outputs_research_check_task",
                "type": "string",
                "description": "The conclusion of the data retrieval check during the research process",
            },
            {
                "key": "outputs_data_retrieval_task",
                "type": "string",
                "description": "The research data retrieval task output",
            },
        ],
        "prompts": [
            {
                "key": "brief_specialist_prompt",
                "name": "Brief Specialist",
                "content": get_prompt_file("brief_specialist.prompt"),
            },
            {
                "key": "data_retrieval_expert_prompt",
                "name": "Data Retrieval Expert",
                "content": get_prompt_file("data_retrieval_expert.prompt"),
            },
            {
                "key": "research_check_prompt",
                "name": "Research Check Agent",
                "content": get_prompt_file("research_check_agent.prompt"),
            },
            {
                "key": "research_summary_agent_prompt",
                "name": "Research Summary Agent",
                "content": get_prompt_file("research_summarizer.prompt"),
            },
            {
                "key": "data_retrieval_task_prompt",
                "name": "Data Retrieval Task",
                "content": get_prompt_file("data_retrieval_task.prompt"),
                "is_templated": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "outputs_research_brief_task": "outputs_research_brief_task",
                        "outputs_research_check_task": "outputs_research_check_task",
                    },
                    "required": ["outputs_research_brief_task"]
                }
            },
            {
                "key": "research_check_task_prompt",
                "name": "Research Check Task",
                "content": get_prompt_file("research_check_task.prompt"),
                "is_templated": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "outputs_research_brief_task": "outputs_research_brief_task",
                        "outputs_data_retrieval_task": "outputs_data_retrieval_task",
                    },
                    "required": ["outputs_data_retrieval_task", "outputs_research_brief_task"]
                }
            },
            {
                "key": "research_summary_task_prompt",
                "name": "Resarch Summary Task",
                "content": get_prompt_file("research_summary_task.prompt"),
                "is_templated": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_parameter",
                        "outputs_data_retrieval_task": "outputs_data_retrieval_task",
                    },
                    "required": ["prompt", "outputs_data_retrieval_task"]
                }
            },
        ],
        "agents": [
            {
                "key": "brief_specialist",
                "name": "brief_specialist",
                "system_message": "brief_specialist_prompt",
                "models": {
                    "chat": "GPT4o",
                },
                "max_consecutive_auto_reply": 1,
                "has_functions": False,
                "has_code_exec": False,                
            },
            {
                "key": "data_retrieval_expert",
                "name": "data_retrieval_expert",
                "system_message": "data_retrieval_expert_prompt",
                "models": {
                    "chat": "gpt-4o-mini",
                },
                "max_consecutive_auto_reply": 1,
                "has_functions": True,
                "has_code_exec": False,                
            },
            {
                "key": "research_check",
                "name": "research_check",
                "system_message": "research_check_prompt",
                "models": {
                    "chat": "GPT4o",
                },
                "max_consecutive_auto_reply": 1,
                "has_functions": False,
                "has_code_exec": False,                
            },
            {
                "key": "research_summarizer_agent",
                "name": "research_summarizer_agent",
                "system_message": "research_summary_agent_prompt",
                "models": {
                    "chat": "GPT4o",
                },
                "max_consecutive_auto_reply": 1,
                "has_functions": False,
                "has_code_exec": False,
            },
        ],
        "tasks": [
            {
                "key": "research_brief_task",
                "task_type": "PromptAgentTask",
                "task_name": "research_brief_task",
                "task_description": "Takes a simple prompt and generates a research brief",
                "agent": "brief_specialist",
                "required_apis": ["llm_api"],
                "templates": {
                    "task_template": "basic_prompt"
                },
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_parameter",
                    },
                    "required": ["prompt"]
                },
            },
            {
                "key": "data_retrieval_task",
                "task_type": "PromptAgentTask",
                "task_name": "data_retrieval_task",
                "task_description": "Generates tool calls for data retrieval based on the prompt",
                "agent": "data_retrieval_expert",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "outputs_research_brief_task": "outputs_research_brief_task",
                        "outputs_research_check_task": "outputs_research_check_task",
                    },
                    "required": ["outputs_research_brief_task"]
                },
                "tasks":{
                    "exa_search": "exa_search",
                    "wikipedia_search": "wikipedia_search",
                    "google_search": "google_search",
                    "arxiv_search": "arxiv_search",
                },
                "required_apis": ["llm_api"],
                "templates": {
                    "task_template": "data_retrieval_task_prompt"
                }
            },
            {
                "key": "research_check_task",
                "task_type": "CheckTask",
                "task_name": "research_check_task",
                "task_description": "Checks the data retrieval results and generates a conclusion",
                "agent": "research_check",
                "exit_code_response_map": {"APPROVED": 0, "REJECTED": 2},
                "exit_codes": {0: "Data retrieval approved", 1: "Response generation failed", 2: "Deta retrieval rejected"},
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "outputs_research_brief_task": "outputs_research_brief_task",
                        "outputs_data_retrieval_task": "outputs_data_retrieval_task",
                    },
                    "required": ["outputs_data_retrieval_task", "outputs_research_brief_task"]
                },
                "templates": {
                    "task_template": "research_check_task_prompt"
                }
            },
            {
                "key": "research_summary_task",
                "task_type": "PromptAgentTask",
                "task_name": "research_summary_task",
                "task_description": "Generates a summary of the data retrieved during the research process",
                "agent": "research_summarizer_agent",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_parameter",
                        "outputs_data_retrieval_task": "outputs_data_retrieval_task",
                    },
                    "required": ["prompt", "outputs_data_retrieval_task"]
                },
                "templates": {
                    "task_template": "research_summary_task_prompt"
                }
            },
            {
                "key": "research_workflow",
                "task_type": "Workflow",
                "task_name": "research_workflow",
                "task_description": "Executes the research workflow based on a string prompt",
                "tasks": {
                    "research_brief_task": "research_brief_task",
                    "data_retrieval_task": "data_retrieval_task",
                    "research_check_task": "research_check_task",
                    "research_summary_task": "research_summary_task",
                },
                "start_task": "research_brief_task",
                "tasks_end_code_routing": {
                    "research_brief_task": {
                        0: ("data_retrieval_task", False),
                        1: ("plan_workflow", True),
                    },
                    "data_retrieval_task": {
                        0: ("research_check_task", False),
                        1: ("data_retrieval_task", True),
                    },
                    "research_check_task": {
                        0: ("research_summary_task", False),
                        1: ("research_check_task", True),
                        2: ("research_summary_task", True),
                    },
                    "research_summary_task": {
                        0: (None, False),
                        1: ("research_summary_task", True),
                    },
                },
                "max_attempts": 3,
                "recursive": False,
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_parameter",
                    },
                    "required": ["prompt"]
                }
            }
        ]
    }
)