from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session
import pandas as pd
import re
import os
import uuid
from werkzeug.utils import secure_filename
import io
import shutil
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = "phone_normalizer_secret_key"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Папки для временных файлов
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
for folder in [UPLOAD_FOLDER, RESULT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_and_separate_by_type(file_path, phone_column_identifier, type_column_identifier, sort_column=None):
    """
    Загружает Excel файл, нормализует номера телефонов в указанном столбце,
    разделяет данные по типу участника и сортирует в алфавитном порядке.

    Возвращает:
    - словарь типов участников с соответствующими DataFrame
    - DataFrame с валидными записями (общий файл)
    - DataFrame с невалидными записями
    """
    try:
        # Читаем файл Excel с помощью openpyxl
        df = pd.read_excel(file_path, engine='openpyxl')

    except Exception as e:
        raise Exception(f"Ошибка при загрузке файла: {str(e)}")

    # Определяем столбец с телефонами (по имени или индексу)
    if isinstance(phone_column_identifier, int) or (
            isinstance(phone_column_identifier, str) and phone_column_identifier.isdigit()):
        column_index = int(phone_column_identifier)
        if column_index < 0 or column_index >= len(df.columns):
            raise Exception(f"Индекс столбца с телефонами {column_index} вне диапазона (0-{len(df.columns) - 1})")
        phone_column = df.columns[column_index]
    else:
        phone_column = phone_column_identifier
        if phone_column not in df.columns:
            raise Exception(
                f"Столбец с телефонами '{phone_column}' не найден в файле. Доступные столбцы: {', '.join(df.columns)}")

    # Определяем столбец с типом участника (по имени или индексу)
    if isinstance(type_column_identifier, int) or (
            isinstance(type_column_identifier, str) and type_column_identifier.isdigit()):
        column_index = int(type_column_identifier)
        if column_index < 0 or column_index >= len(df.columns):
            raise Exception(f"Индекс столбца с типом участника {column_index} вне диапазона (0-{len(df.columns) - 1})")
        type_column = df.columns[column_index]
    else:
        type_column = type_column_identifier
        if type_column not in df.columns:
            raise Exception(
                f"Столбец с типом участника '{type_column}' не найден в файле. Доступные столбцы: {', '.join(df.columns)}")

    # Создаем новую колонку для отметки ошибок
    df['_номер_валиден'] = True
    df['_причина_ошибки'] = ''

    # Функция для нормализации номера телефона к формату 79998887766
    def normalize_phone(row):
        phone = row[phone_column]
        original_phone = str(phone) if not pd.isna(phone) else ""

        if pd.isna(phone) or not original_phone.strip():
            row['_номер_валиден'] = False
            row['_причина_ошибки'] = 'Пустой номер'
            return phone

        # Преобразуем телефон в строку
        phone_str = str(phone).strip()

        # Удаляем все, кроме цифр и знака +
        # Сначала сохраняем +, если он есть в начале
        starts_with_plus = phone_str.startswith('+')
        phone_digits = re.sub(r'[^\d]', '', phone_str)

        # Минимальное количество цифр для валидного номера
        if len(phone_digits) < 7:
            row['_номер_валиден'] = False
            row['_причина_ошибки'] = f'Недостаточно цифр: {len(phone_digits)}'
            return original_phone

        # Обрабатываем международные форматы
        if starts_with_plus:
            # Если номер начинается с +, это международный формат

            # Если уже начинается с +7, +8 -> убираем + и обрабатываем как обычно
            if phone_digits.startswith('7') or phone_digits.startswith('8'):
                # pass - обработаем ниже
                pass
            # Другие международные коды
            elif len(phone_digits) >= 9:  # Минимальная длина: код страны (1-3 цифры) + номер (мин. 7 цифр)
                # Заменяем код страны на 7, оставляем только значимую часть номера

                # Определяем длину кода страны (обычно 1-3 цифры)
                # Это эвристика - предполагаем, что национальный номер имеет 9-10 цифр
                if len(phone_digits) >= 11:
                    # Если номер длинный, предполагаем код страны 1-2 цифры
                    return '7' + phone_digits[-10:] if len(phone_digits[-10:]) == 10 else '7' + phone_digits[-9:]
                else:
                    # Для более коротких номеров, предполагаем что код страны 1-3 цифры
                    country_code_len = len(phone_digits) - 9 if len(phone_digits) - 9 > 0 else 1
                    return '7' + phone_digits[country_code_len:]

        # Обработка стандартных форматов
        if len(phone_digits) == 11:
            # Если первая цифра 8 или другая (кроме 7), заменяем на 7
            if phone_digits[0] != '7':
                return '7' + phone_digits[1:]
            # Если уже начинается с 7, оставляем как есть
            return phone_digits
        elif len(phone_digits) == 10:
            # Добавляем 7 в начало для 10-значных номеров (без кода страны)
            return '7' + phone_digits
        elif len(phone_digits) > 11:
            # Слишком длинный номер, отмечаем как потенциально проблемный
            row['_номер_валиден'] = False
            row['_причина_ошибки'] = f'Слишком длинный номер: {len(phone_digits)} цифр'
            # Но все равно пытаемся обработать, извлекая основную часть
            return '7' + phone_digits[-10:]
        else:
            # Для более коротких номеров (7-9 цифр) добавляем 7 в начало
            # Но отмечаем их как потенциально проблемные
            if len(phone_digits) < 10:
                row['_номер_валиден'] = False
                row['_причина_ошибки'] = f'Короткий номер: {len(phone_digits)} цифр'
            return '7' + phone_digits

    # Применяем функцию нормализации к каждой строке
    for idx, row in df.iterrows():
        df.loc[idx, phone_column] = normalize_phone(row)

    # Разделяем на два DataFrame - валидные и невалидные номера
    valid_df = df[df['_номер_валиден']].copy()
    invalid_df = df[~df['_номер_валиден']].copy()

    # Удаляем служебные колонки
    for df_clean in [valid_df, invalid_df]:
        if '_номер_валиден' in df_clean.columns:
            df_clean.drop('_номер_валиден', axis=1, inplace=True)

    # В валидном DF удаляем причину ошибки, а в невалидном оставляем
    if '_причина_ошибки' in valid_df.columns:
        valid_df.drop('_причина_ошибки', axis=1, inplace=True)

    # Определяем столбец для сортировки (если не указан, используем первый столбец)
    if sort_column is None or sort_column not in valid_df.columns:
        sort_column = valid_df.columns[0]  # Первый столбец по умолчанию

    # Разделяем данные по типу участника
    type_dfs = {}
    unique_types = valid_df[type_column].dropna().unique()

    for participant_type in unique_types:
        # Фильтруем данные по типу и создаем копию
        type_df = valid_df[valid_df[type_column] == participant_type].copy()

        # Сортируем данные по указанному столбцу
        if sort_column in type_df.columns:
            type_df = type_df.sort_values(by=sort_column)

        # Сохраняем DataFrame в словарь
        type_dfs[str(participant_type)] = type_df

    return type_dfs, valid_df, invalid_df


@app.route('/', methods=['GET', 'POST'])
def index():
    # Очистка старых файлов при посещении главной страницы
    clean_old_files()

    if request.method == 'POST':
        # Проверяем, был ли загружен файл
        if 'file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Файл не выбран')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Генерируем уникальное имя файла
            filename = secure_filename(file.filename)
            unique_filename = f"{str(uuid.uuid4())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Сохраняем файл
            file.save(filepath)

            # Получаем идентификаторы столбцов
            phone_column = request.form.get('phone_column', '').strip()
            type_column = request.form.get('type_column', '').strip()
            sort_column = request.form.get('sort_column', '').strip() or None

            if not phone_column:
                flash('Необходимо указать название или номер столбца с телефонами')
                os.remove(filepath)  # Удаляем загруженный файл
                return redirect(request.url)

            if not type_column:
                flash('Необходимо указать название или номер столбца с типом участника')
                os.remove(filepath)  # Удаляем загруженный файл
                return redirect(request.url)

            try:
                # Обрабатываем файл
                type_dfs, valid_df, invalid_df = normalize_and_separate_by_type(
                    filepath, phone_column, type_column, sort_column
                )

                # Создаем уникальный идентификатор для результатов
                result_id = str(uuid.uuid4())
                result_dir = os.path.join(app.config['RESULT_FOLDER'], result_id)
                os.makedirs(result_dir, exist_ok=True)

                # Определяем имена для выходных файлов
                all_valid_filename = f"all_processed_{os.path.splitext(filename)[0]}.xlsx"
                invalid_filename = f"errors_{os.path.splitext(filename)[0]}.xlsx"

                # Сохраняем общий файл со всеми валидными записями
                valid_path = os.path.join(result_dir, all_valid_filename)
                valid_df.to_excel(valid_path, index=False, engine='openpyxl')

                # Сохраняем данные об ошибках только если они есть
                has_errors = not invalid_df.empty
                if has_errors:
                    invalid_path = os.path.join(result_dir, invalid_filename)
                    invalid_df.to_excel(invalid_path, index=False, engine='openpyxl')

                # Сохраняем отдельные файлы для каждого типа участника
                type_files = {}
                for type_name, type_df in type_dfs.items():
                    # Создаем безопасное имя файла
                    safe_type_name = re.sub(r'[^\w\-_]', '_', str(type_name))
                    type_filename = f"type_{safe_type_name}_{os.path.splitext(filename)[0]}.xlsx"
                    type_path = os.path.join(result_dir, type_filename)

                    # Сохраняем DataFrame
                    type_df.to_excel(type_path, index=False, engine='openpyxl')

                    # Сохраняем информацию о файле
                    type_files[type_name] = {
                        'filename': type_filename,
                        'count': len(type_df)
                    }

                # Сохраняем информацию о времени создания
                with open(os.path.join(result_dir, "timestamp.txt"), "w") as f:
                    f.write(datetime.now().isoformat())

                # Удаляем временный файл
                os.remove(filepath)

                # Сохраняем информацию о результатах в сессии для будущего доступа
                session['result_id'] = result_id
                session['all_valid_filename'] = all_valid_filename
                session['invalid_filename'] = invalid_filename if has_errors else None
                session['original_filename'] = filename
                session['has_errors'] = has_errors
                session['error_count'] = len(invalid_df) if has_errors else 0
                session['success_count'] = len(valid_df)
                session['type_files'] = type_files

                # Перенаправляем на страницу результатов
                return redirect(url_for('result'))

            except Exception as e:
                flash(f'Ошибка обработки файла: {str(e)}')
                # Удаляем временный файл в случае ошибки
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
        else:
            flash('Разрешены только файлы Excel (.xlsx, .xls)')
            return redirect(request.url)

    return render_template('index.html')


@app.route('/result', methods=['GET'])
def result():
    """Отображение результатов обработки и ссылок для скачивания"""
    # Проверяем наличие данных о результатах в сессии
    result_id = session.get('result_id')
    if not result_id:
        flash('Не найдены данные о результатах обработки. Пожалуйста, загрузите файл заново.')
        return redirect(url_for('index'))

    all_valid_filename = session.get('all_valid_filename')
    invalid_filename = session.get('invalid_filename')
    original_filename = session.get('original_filename')
    has_errors = session.get('has_errors', False)
    error_count = session.get('error_count', 0)
    success_count = session.get('success_count', 0)
    type_files = session.get('type_files', {})

    # Проверяем, существуют ли файлы с результатами
    result_dir = os.path.join(app.config['RESULT_FOLDER'], result_id)
    valid_exists = os.path.exists(os.path.join(result_dir, all_valid_filename))
    invalid_exists = invalid_filename and os.path.exists(os.path.join(result_dir, invalid_filename))

    if not valid_exists:
        flash('Файлы с результатами не найдены. Пожалуйста, загрузите файл заново.')
        return redirect(url_for('index'))

    # Проверяем существование файлов для каждого типа
    type_files_valid = {}
    for type_name, file_info in type_files.items():
        filename = file_info['filename']
        if os.path.exists(os.path.join(result_dir, filename)):
            type_files_valid[type_name] = file_info

    return render_template(
        'result.html',
        result_id=result_id,
        all_valid_filename=all_valid_filename,
        invalid_filename=invalid_filename,
        original_filename=original_filename,
        has_errors=has_errors,
        error_count=error_count,
        success_count=success_count,
        total_count=error_count + success_count,
        type_files=type_files_valid
    )


@app.route('/download/<result_id>/<filename>', methods=['GET'])
def download_file(result_id, filename):
    """Скачивание обработанного файла"""
    # Проверяем безопасность пути
    result_dir = os.path.join(app.config['RESULT_FOLDER'], result_id)
    filepath = os.path.join(result_dir, filename)

    if not os.path.exists(filepath):
        flash('Запрошенный файл не найден.')
        return redirect(url_for('index'))

    # Отправляем файл пользователю
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/preview', methods=['POST'])
def preview_columns():
    """Предварительный просмотр столбцов в загруженном файле"""
    if 'file' not in request.files:
        return {'error': 'Файл не найден'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'Имя файла пустое'}, 400

    if not allowed_file(file.filename):
        return {'error': 'Неподдерживаемый формат файла'}, 400

    try:
        # Сохраняем временный файл
        filename = secure_filename(file.filename)
        unique_filename = f"{str(uuid.uuid4())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        try:
            # Читаем только заголовки файла с помощью openpyxl
            df = pd.read_excel(filepath, engine='openpyxl', nrows=0)

            # Получаем список столбцов с их индексами
            columns = [{'index': i, 'name': col} for i, col in enumerate(df.columns)]

            # Удаляем временный файл
            os.remove(filepath)

            return {'columns': columns}

        except Exception as e:
            # Удаляем временный файл
            if os.path.exists(filepath):
                os.remove(filepath)
            return {'error': str(e)}, 500

    except Exception as e:
        # Удаляем временный файл в случае ошибки
        if os.path.exists(filepath):
            os.remove(filepath)
        return {'error': str(e)}, 500


def clean_old_files():
    """Удаляет файлы старше 24 часов"""
    current_time = datetime.now()

    # Очистка папки с результатами
    try:
        for result_id in os.listdir(app.config['RESULT_FOLDER']):
            result_dir = os.path.join(app.config['RESULT_FOLDER'], result_id)
            timestamp_file = os.path.join(result_dir, "timestamp.txt")

            if os.path.exists(timestamp_file):
                with open(timestamp_file, "r") as f:
                    timestamp_str = f.read().strip()
                    timestamp = datetime.fromisoformat(timestamp_str)

                if (current_time - timestamp) > timedelta(hours=24):
                    shutil.rmtree(result_dir)
            else:
                # Если нет файла с временем, удаляем папку как потенциально устаревшую
                shutil.rmtree(result_dir)
    except Exception as e:
        print(f"Ошибка при очистке результатов: {str(e)}")

    # Очистка папки с загрузками
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))

            if (current_time - file_modified_time) > timedelta(hours=24):
                os.remove(filepath)
    except Exception as e:
        print(f"Ошибка при очистке загрузок: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)