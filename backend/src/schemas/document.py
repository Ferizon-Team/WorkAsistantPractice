from pydantic import BaseModel, Field

class SematicSearchResult(BaseModel):
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