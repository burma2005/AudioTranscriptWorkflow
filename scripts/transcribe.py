import os
import sys
import datetime
import whisper
import glob

# 1. 強防呆機制：動態尋找 FFmpeg 路徑並加入環境變數（Windows 用 winget 安裝的情境）
local_app_data = os.environ.get("LOCALAPPDATA", "")
if local_app_data:
    ffmpeg_search_path = os.path.join(
        local_app_data, "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "*", "bin"
    )
    ffmpeg_dirs = glob.glob(ffmpeg_search_path)
    if ffmpeg_dirs:
        ffmpeg_dir = ffmpeg_dirs[0]
        if ffmpeg_dir not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

# 2. 接收相對路徑參數，避免寫死絕對路徑
if len(sys.argv) < 3:
    print("Usage: python scripts/transcribe.py <audio_path> <output_path>")
    print("Example: python scripts/transcribe.py input/meeting.m4a output/transcripts/meeting_transcript.md")
    sys.exit(1)

audio_path = sys.argv[1]
output_path = sys.argv[2]

def transcribe():
    # 3. 自動建立輸出目錄，避免目錄不存在時拋出 FileNotFoundError
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print("載入 Whisper 模型 (base)...")
    model = whisper.load_model("base")
    print(f"開始轉錄: {audio_path}")

    start_time = datetime.datetime.now()
    result = model.transcribe(audio_path, verbose=True, language="zh")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 語音逐字稿\n\n")
        f.write(f"**轉錄日期**: {datetime.date.today()}\n")
        f.write(f"**音檔來源**: {os.path.basename(audio_path)}\n\n")
        f.write("---\n\n")

        for segment in result["segments"]:
            timestamp = str(datetime.timedelta(seconds=int(segment["start"])))
            text = segment["text"].strip()
            f.write(f"[{timestamp}] {text}\n")

    elapsed = datetime.datetime.now() - start_time
    print(f"✅ 轉錄完成！共耗時: {elapsed}")
    print(f"📄 逐字稿已儲存至: {output_path}")

if __name__ == "__main__":
    transcribe()

