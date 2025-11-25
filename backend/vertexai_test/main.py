import vertexai
from vertexai.language_models import TextEmbeddingModel

vertexai.init(project="HoosStudying-cs4750", location="us-central1")
model = TextEmbeddingModel.from_pretrained("text-embedding-005")
