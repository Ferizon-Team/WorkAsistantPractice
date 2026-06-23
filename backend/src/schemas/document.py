from pydantic import BaseModel, Field


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

class StreamContentAnswer(BaseModel):
	text : str | None = None
	media : str | None = None


class StreamChunkAnswer(BaseModel):
	event : str
	content : str | StreamContentAnswer | None = None

class StreamContentRequest(BaseModel):
	text : str | None = None
	media : str | None = None

class StreamRequest(BaseModel):
	event : str
	content : str | StreamContentRequest | None = None


