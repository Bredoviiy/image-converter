import argparse
import logging
from pathlib import Path
from PIL import Image


def setup_logging(log_file: str = "converter.log"):
    """Настраивает логирование в файл и консоль."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def convert_images(input_dir: str, output_dir: str, target_format: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Создаем папку для результатов
    output_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        logging.error(f"Папка '{input_path}' не найдена.")
        return

    # Поддерживаемые расширения
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
    files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]

    if not files:
        logging.info(f"В папке '{input_path}' нет поддерживаемых изображений.")
        return

    logging.info(f"Начинаю конвертацию {len(files)} файлов в формат {target_format.upper()}...")

    success_count = 0
    error_count = 0

    # Нормализуем формат для Pillow: JPG → JPEG
    pillow_format = "JPEG" if target_format.upper() in ["JPG", "JPEG"] else target_format.upper()

    for file in files:
        try:
            with Image.open(file) as img:
                # Обработка прозрачности для JPEG
                if pillow_format == "JPEG" and img.mode in ("RGBA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA":
                        background.paste(img, mask=img.split())
                    elif img.mode == "P":
                        background.paste(img, mask=img)
                    img = background

                new_name = f"{file.stem}.{target_format.lower()}"
                output_file = output_path / new_name

                img.save(output_file, format=pillow_format)
                logging.info(f"✅ Успешно: {file.name} -> {new_name}")
                success_count += 1

        except Exception as e:
            logging.error(f"❌ Ошибка при обработке {file.name}: {e}")
            error_count += 1

    logging.info("--- ИТОГ ---")
    logging.info(f"Успешно: {success_count}")
    logging.info(f"Ошибок: {error_count}")


def main():
    parser = argparse.ArgumentParser(description="Конвертер изображений на Python")
    parser.add_argument("--input", type=str, default="input", help="Папка с исходными изображениями")
    parser.add_argument("--output", type=str, default="converted", help="Папка для результатов")
    parser.add_argument("--format", type=str, default="PNG", choices=["JPG", "JPEG", "PNG", "WEBP"],
                        help="Целевой формат")

    args = parser.parse_args()

    setup_logging()
    convert_images(args.input, args.output, args.format)


if __name__ == "__main__":
    main()
