from pydantic import Field
from typing import List
from workflow_logic.util import LLMConfig, ApiType, FileReference, MessageDict
from workflow_logic.core.api.engines.api_engine import APIEngine
from workflow_logic.core.parameters import FunctionParameters, ParameterDefinition
from openai import AsyncOpenAI

class OpenAISpeechToTextEngine(APIEngine):
    input_variables: FunctionParameters = Field(
        default=FunctionParameters(
            type="object",
            properties={
                "file_reference": ParameterDefinition(
                    type="object",
                    description="FileReference object for the audio file to transcribe."
                ),
                "model": ParameterDefinition(
                    type="string",
                    description="The name of the speech-to-text model to use.",
                    default="whisper-1"
                )
            },
            required=["file_reference"]
        )
    )
    required_api: ApiType = Field(ApiType.LLM_MODEL, title="The API engine required")

    async def generate_api_response(self, api_data: LLMConfig, file_reference: FileReference, model: str = "whisper-1") -> MessageDict:
        """
        Transcribes speech to text using OpenAI's API.

        Args:
            api_data (LLMConfig): Configuration data for the API (e.g., API key, base URL).
            file_reference (FileReference): FileReference object for the audio file to transcribe.
            model (str): The name of the speech-to-text model to use.

        Returns:
            MessageDict: A message dict containing the transcription.
        """
        client = AsyncOpenAI(
            api_key=api_data.api_key,
            base_url=api_data.base_url
        )

        try:
            with open(file_reference.filepath, "rb") as audio_file:
                transcription = await client.audio.transcriptions.create(
                    model=model, 
                    file=audio_file, 
                    response_format="text"
                )

            return MessageDict(
                role="assistant",
                content=transcription,
                generated_by="speech_to_text_model",
                type="text",
                references=[file_reference],
                creation_metadata={
                    "model": model,
                }
            )
        except Exception as e:
            raise Exception(f"Error in OpenAI speech-to-text API call: {str(e)}")