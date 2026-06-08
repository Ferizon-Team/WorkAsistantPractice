from pydantic import BaseModel

class Source(BaseModel):
	id : int
	title: str
	similarity : float
	snippet : str

class AnswerQuestionResponse(BaseModel):
	answer: str
	sources: list[Source] = []
	confidence : float = 0
	context_used : int = 0

