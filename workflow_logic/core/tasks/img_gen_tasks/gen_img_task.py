from typing import List, Tuple, Union, Dict, Optional
from pydantic import Field
from workflow_logic.core.tasks.agent_tasks import BasicAgentTask
from workflow_logic.core.parameters import FunctionParameters, ParameterDefinition
from workflow_logic.core.data_structures import MessageDict, ApiType
from workflow_logic.core.api import APIManager
from workflow_logic.util import LOGGER

class GenerateImageTask(BasicAgentTask):
    input_variables: FunctionParameters = Field(
        default=FunctionParameters(
            type="object",
            properties={
                "prompt": ParameterDefinition(
                    type="string",
                    description="A text description of the desired image(s)."
                ),
                "n": ParameterDefinition(
                    type="integer",
                    description="The number of images to generate.",
                    default=1
                ),
                "size": ParameterDefinition(
                    type="string",
                    description="The size of the generated images.",
                    default="1024x1024"
                ),
                "quality": ParameterDefinition(
                    type="string",
                    description="The quality of the image generation.",
                    default="standard"
                )
            },
            required=["prompt"]
        )
    )
    required_apis: List[ApiType] = Field([ApiType.IMG_GENERATION], description="A list of required APIs for the task")

    async def generate_response(self, api_manager: APIManager, **kwargs) ->  Tuple[List[MessageDict], int, Optional[Union[List[MessageDict], Dict[str, str]]]]:
        prompt: str = kwargs.get('prompt', "")
        n: int = kwargs.get('n', 1)
        size: str = kwargs.get('size', "1024x1024")
        quality: str = kwargs.get('quality', "standard")

        new_messages = await self.agent.generate_image(api_manager=api_manager, prompt=prompt, n=n, size=size, quality=quality)
        if not new_messages:
            LOGGER.error("No messages returned from agent.")
            return [], 1, None
        return [new_messages], 0, None