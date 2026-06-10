from pydantic import BaseModel, Fiel


class SematicSearchResult(BaseModel):
	id : int
	title : str
	text : str
	category : str | None
	similarity : float = Field(ge = 0, le = 1)
	chunk_index : int
	metadata : dict | None = {}


class LoadDocument(BaseModel):
	title: str
	text: str
	category: str | None = None

class StreamTextChunk(BaseModel):
	event : str
	content : str | None = None
