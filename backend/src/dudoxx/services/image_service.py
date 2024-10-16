from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import base64
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from dudoxx.schemas.image import ImageDescription
from dudoxx.exceptions.openai_exceptions import handle_openai_api_error


class ImageService:
    def __init__(self, model="gpt-4o", image_size=(224, 224)):
        self.model = model
        self.image_size = image_size
        self.llm = ChatOpenAI(model=self.model, max_tokens=300)

    async def process_image(self, image: UploadFile) -> Image.Image:
        try:
            img = Image.open(image.file)
            img = img.convert("RGB")
            img = img.resize((224, 224))
            return img
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image processing failed: {str(e)}")

    async def encode_image(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @handle_openai_api_error
    async def generate_image_description(self, image: UploadFile) -> ImageDescription:
        processed_image = await self.process_image(image)
        base64_image = await self.encode_image(processed_image)

        messages = [
            SystemMessage(
                content="You are an AI assistant capable of analyzing and providing detailed descriptions of images."
            ),
            HumanMessage(
                content=f"Analyze the content of this image and describe what is happening in it: ![Image](data:image/png;base64,{base64_image})"
            ),
        ]

        response = self.llm.invoke(messages)
        return ImageDescription(
            description=response.content,
        )

    @handle_openai_api_error
    async def refine_description_with_langchain(self, description: str) -> ImageDescription:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant that enhances descriptions by adding vivid details and engaging language.",
                ),
                (
                    "human",
                    "Enhance the following image description to include more detail and vividness: {description}",
                ),
            ]
        )

        refined_description = self.llm.invoke(prompt.format_messages(description=description))
        return ImageDescription(
            description=refined_description.content,
        )
