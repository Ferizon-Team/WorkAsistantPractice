from pydantic import BaseModel

class Source(BaseModel):
	title: str
	similarity : float
	snippet : str

class AnswerQuestionResponse(BaseModel):
	answer: str
	sources: list[Source] = []
	confidence : float
	context_used : int

