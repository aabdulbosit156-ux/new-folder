import os
import asyncio
import os
import speech_recognition as sr
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from pydub import AudioSegment

# BOT TOKENINGIZNI SHU YERGA KIRITING
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Iltimos, muhit o'zgaruvchilarini tekshiring.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def recognize_audio(file_path: str) -> str:
    """WAV faylni qabul qilib, uni Google STT orqali matnga o'giruvchi sinxron funksiya."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Ingliz tilini aniqlash uchun language="en-US"
            text = recognizer.recognize_google(audio_data, language="en-US")
            return text
        except sr.UnknownValueError:
            return "Ovoz tushunarsiz yoki xabarda nutq yo'q."
        except sr.RequestError as e:
            return f"STT API bilan ulanishda xatolik yuz berdi: {e}"

def convert_to_wav(input_path: str, output_path: str):
    """Har qanday audio formatni WAV formatiga o'tkazuvchi funksiya."""
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Salom! Menga istalgan audio fayl (mp3, wav) yoki ovozli xabar (voice message) yuboring.\n"
        "Men uni ingliz tilidagi matnga o'girib beraman."
    )

@dp.message(F.voice | F.audio | F.document)
async def handle_audio_messages(message: Message):
    # Fayl ID sini to'g'ri turdagi xabardan ajratib olish
    if message.voice:
        file_id = message.voice.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("audio/"):
        file_id = message.document.file_id
    else:
        return

    status_msg = await message.answer("Audioni yuklab olyapman va ishlayapman... ⏳")

    original_path = f"temp_{file_id}.ext"
    wav_path = f"temp_{file_id}.wav"

    try:
        # 1. Telegram serveridan faylni yuklab olish
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, original_path)

        # 2. Faylni WAV formatiga o'tkazish (bloklanmasligi uchun to_thread orqali)
        await asyncio.to_thread(convert_to_wav, original_path, wav_path)

        # 3. WAV fayldan matnni aniqlash
        text = await asyncio.to_thread(recognize_audio, wav_path)

        # 4. Natijani foydalanuvchiga yuborish
        await status_msg.edit_text(f"**Natija:**\n\n{text}", parse_mode="Markdown")

    except Exception as e:
        await status_msg.edit_text(f"Xatolik yuz berdi: {str(e)}")
        
    finally:
        # Vaqtinchalik fayllarni diskdan tozalash
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")