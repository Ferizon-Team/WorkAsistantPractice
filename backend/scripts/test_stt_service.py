from faster_whisper import WhisperModel


def main():
    print("Loading model...")

    model = WhisperModel("base", device="cpu")
    audio_path = "tests/audio/sample.ogg"

    print("Transcribing...")

    segments, info = model.transcribe(audio_path)

    text = " ".join(seg.text for seg in segments)

    print("\n===== RESULT =====")
    print("TEXT:", text)
    print("LANG:", info.language)
    print("==================")

if __name__ == "__main__":
    main()
