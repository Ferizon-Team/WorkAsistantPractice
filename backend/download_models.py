import os
import sys
from pathlib import Path


def main():
	cache_dir = Path("./models")
	cache_dir.mkdir(exist_ok = True)

	print("📥 Downloading BGE-M3...")
	try:
		from sentence_transformers import SentenceTransformer

		model = SentenceTransformer('BAAI/bge-m3')

		model_path = cache_dir / "bge-m3"
		model.save(str(model_path))

		print(f"Model saved to {model_path}")

	except Exception as e:
		print(f"❌ Download failed: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()