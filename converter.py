import os
import argparse
import logging
from pathlib import Path
from PIL import Image

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("converter.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def convert_image(input_path: Path, output_path: Path, target_format: str):
    """Конвертирует одно изображение с обработкой прозрачности."""
    try:
        with Image.open(input_path) as img:
            # Нормализуем формат: Pillow понимает JPEG, а не JPG
            save_format = "JPEG" if target_format.upper() == "JPG" else target_format.upper()

            # Обработка прозрачности для JPEG (JPG не поддерживает альфа-канал)
            if save_format == "JPEG":
                if img.mode in ("RGBA", "P"):
                    # Создаем белый фон
                    background = Image.new("RGB", img.size, (255, 255, 255))

                    # Если режим P (палитра), конвертируем в RGBA для корректной работы маски
                    if img.mode == "P":
                        img = img.convert("RGBA")

                    # Накладываем изображение на фон, используя альфа-канал как маску
                    # split()[-1] берет последний канал (альфа-канал)
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != "RGB":
                    # Для других режимов (например, L, CMYK) просто конвертируем в RGB
                    img = img.convert("RGB")

            # Сохраняем изображение
            img.save(output_path, format=save_format)

            logger.info(f"Успешно конвертировано: {input_path.name} -> {output_path.name}")
            return True

    except Exception as e:
        logger.error(f"Ошибка при обработке {input_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Конвертер изображений CLI")
    parser.add_argument("--format", type=str, required=True, help="Целевой формат (JPG, PNG, WEBP)")
    parser.add_argument("--input", type=str, default="input", help="Папка с исходными файлами (по умолчанию: input)")
    parser.add_argument("--output", type=str, default="output", help="Папка для результатов (по умолчанию: output)")

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    target_format = args.format.upper()

    # Создаем папку вывода, если её нет
    output_dir.mkdir(parents=True, exist_ok=True)

    # Проверка наличия папки ввода
    if not input_dir.exists():
        logger.error(f"Папка ввода '{input_dir}' не найдена. Создайте её и положите туда картинки.")
        return

    # Поддерживаемые расширения
    supported_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
    files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_extensions]

    if not files:
        logger.info(f"В папке '{input_dir}' не найдено поддерживаемых изображений.")
        return

    logger.info(f"Начинаю конвертацию {len(files)} файлов в формат {target_format}...")

    success_count = 0
    error_count = 0

    for file_path in files:
        # Формируем имя выходного файла с новым расширением
        output_filename = file_path.stem + f".{target_format.lower()}"
        output_path = output_dir / output_filename

        if convert_image(file_path, output_path, target_format):
            success_count += 1
        else:
            error_count += 1

    logger.info("--- ИТОГ ---")
    logger.info(f"Успешно: {success_count}")
    logger.info(f"Ошибок: {error_count}")


if __name__ == "__main__":
    main()
