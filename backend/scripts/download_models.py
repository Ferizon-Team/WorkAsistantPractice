import sys
from pathlib import Path


def main():
    cache_dir = Path("./models")
    cache_dir.mkdir(exist_ok=True)

    print("Downloading BGE-M3...")
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("BAAI/bge-m3")

        model_path = cache_dir / "bge-m3"
        model.save(str(model_path))

        print(f"Model saved to {model_path}")

    except Exception as e:
        print(f"❌ Download failed: {e}")
        sys.exit(1)

    install_tts_model()


def install_tts_model() -> None:
    print("Downloading Silero TTS...")

    try:
        import torch

        tts_cache_dir = Path("./models") / "torch_hub"
        tts_info_dir = Path("./models") / "silero-tts"

        tts_cache_dir.mkdir(parents=True, exist_ok=True)
        tts_info_dir.mkdir(parents=True, exist_ok=True)

        torch.hub.set_dir(str(tts_cache_dir))

        language = "ru"
        model_id = "v4_ru"

        model, example_text = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language=language,
            speaker=model_id,
        )

        metadata_path = tts_info_dir / "metadata.txt"
        metadata_path.write_text(
            f"language={language}\n"
            f"model_id={model_id}\n"
            f"cache_dir={tts_cache_dir}\n"
            f"example_text={example_text}\n",
            encoding="utf-8",
        )

        print(f"Silero TTS cached in {tts_cache_dir}")
        print(f"Silero TTS metadata saved to {metadata_path}")

    except Exception as error:
        print(f"❌ TTS model download failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()