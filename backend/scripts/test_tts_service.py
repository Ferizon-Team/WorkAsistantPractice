import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.service.model_manager_service import model_manager
from src.service.tts_service import TTSService


def main():
    tts_model = model_manager.get_tts_model()

    if tts_model is None:
        print("TTS model is not loaded")
        return

    service = TTSService(
        model=tts_model,
        output_dir="storage/tts",
        audio_format="wav",
    )

    result = service.synthesize(
        text="Кирилл аниме тянка Биби ждет тебя в бравл старсе заходи скорее",
        file_name="real_tts_test",
    )

    print(result)
    print("File exists:", Path(result.audio_path).exists())


if __name__ == "__main__":
    main()