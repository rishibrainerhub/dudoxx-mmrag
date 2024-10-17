from fastapi import UploadFile
from PIL import Image
import io
import base64
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from dudoxx.schemas.image import ImageDescription
from dudoxx.exceptions.openai_exceptions import handle_openai_api_error
from dudoxx.exceptions.image_exceptions import ErrorEncodingImage, ErrorProcessingImage


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
            raise ErrorProcessingImage(f"Error processing image: {str(e)}")

    async def encode_image(self, image: Image.Image) -> str:
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            raise ErrorEncodingImage(f"Error encoding image: {str(e)}")

    @handle_openai_api_error
    async def generate_image_description(self, image: UploadFile) -> ImageDescription:
        processed_image = await self.process_image(image)
        base64_image = await self.encode_image(processed_image)

        messages = [
            SystemMessage(content="Describe what you see in the image in 1-2 short, simple sentences."),
            HumanMessage(content=f"What is in this image? ![Image](data:image/png;base64,{base64_image})"),
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
                    "Add 1-2 simple details about color, size, or action to the description. Keep it brief and natural.",
                ),
                ("human", "Add a few more simple details to this description: {description}"),
            ]
        )

        refined_description = self.llm.invoke(prompt.format_messages(description=description))
        return ImageDescription(
            description=refined_description.content,
        )
