"""
Multi-language support for CampaignPilot.
Supported: cs (Czech), en (English), de (German), ru (Russian), es (Spanish)
"""

TRANSLATIONS = {
    # ── Navigation ──
    "nav_dashboard": {"cs": "Dashboard", "en": "Dashboard", "de": "Dashboard", "ru": "Панель управления", "es": "Panel"},
    "nav_campaigns": {"cs": "Kampaně", "en": "Campaigns", "de": "Kampagnen", "ru": "Кампании", "es": "Campañas"},
    "nav_templates": {"cs": "Šablony", "en": "Templates", "de": "Vorlagen", "ru": "Шаблоны", "es": "Plantillas"},
    "nav_contacts": {"cs": "Kontakty", "en": "Contacts", "de": "Kontakte", "ru": "Контакты", "es": "Contactos"},
    "nav_lists": {"cs": "Seznamy", "en": "Lists", "de": "Listen", "ru": "Списки", "es": "Listas"},
    "nav_servers": {"cs": "Mail Servery", "en": "Mail Servers", "de": "Mail Server", "ru": "Почтовые серверы", "es": "Servidores"},
    "nav_domains": {"cs": "Limity domén", "en": "Domain Limits", "de": "Domain-Limits", "ru": "Лимиты доменов", "es": "Límites de dominio"},
    "nav_overview": {"cs": "Přehled", "en": "Overview", "de": "Übersicht", "ru": "Обзор", "es": "Resumen"},
    "nav_infrastructure": {"cs": "Infrastruktura", "en": "Infrastructure", "de": "Infrastruktur", "ru": "Инфраструктура", "es": "Infraestructura"},
    "nav_logout": {"cs": "Odhlásit se", "en": "Log out", "de": "Abmelden", "ru": "Выйти", "es": "Cerrar sesión"},

    # ── Login ──
    "login_title": {"cs": "Přihlášení", "en": "Login", "de": "Anmeldung", "ru": "Вход", "es": "Iniciar sesión"},
    "login_subtitle": {"cs": "Email Campaign Management System", "en": "Email Campaign Management System", "de": "Email-Kampagnen-Management-System", "ru": "Система управления email-кампаниями", "es": "Sistema de gestión de campañas de email"},
    "login_username": {"cs": "Uživatelské jméno", "en": "Username", "de": "Benutzername", "ru": "Имя пользователя", "es": "Usuario"},
    "login_password": {"cs": "Heslo", "en": "Password", "de": "Passwort", "ru": "Пароль", "es": "Contraseña"},
    "login_submit": {"cs": "Přihlásit se", "en": "Log in", "de": "Anmelden", "ru": "Войти", "es": "Entrar"},
    "login_error": {"cs": "Neplatné přihlašovací údaje", "en": "Invalid credentials", "de": "Ungültige Anmeldedaten", "ru": "Неверные данные", "es": "Credenciales inválidas"},
    "login_protected": {"cs": "Chráněný přístup", "en": "Protected access", "de": "Geschützter Zugang", "ru": "Защищённый доступ", "es": "Acceso protegido"},
    "login_authorized_only": {"cs": "Pouze autorizovaní uživatelé", "en": "Authorized users only", "de": "Nur für autorisierte Nutzer", "ru": "Только для авторизованных пользователей", "es": "Solo usuarios autorizados"},

    # ── Profile / change password ──
    "nav_profile": {"cs": "Profil", "en": "Profile", "de": "Profil", "ru": "Профиль", "es": "Perfil"},
    "profile_page_title": {"cs": "Profil uživatele", "en": "User profile", "de": "Benutzerprofil", "ru": "Профиль пользователя", "es": "Perfil de usuario"},
    "profile_breadcrumb": {"cs": "Profil", "en": "Profile", "de": "Profil", "ru": "Профиль", "es": "Perfil"},
    "profile_change_password_title": {"cs": "Změna hesla", "en": "Change password", "de": "Passwort ändern", "ru": "Смена пароля", "es": "Cambiar contraseña"},
    "profile_demo_mode": {"cs": "Demo režim", "en": "Demo mode", "de": "Demo-Modus", "ru": "Демо-режим", "es": "Modo demo"},
    "profile_demo_password_disabled": {"cs": "změna hesla je v této instalaci zakázána.", "en": "password change is disabled in this installation.", "de": "Passwortänderung ist in dieser Installation deaktiviert.", "ru": "смена пароля в этой установке отключена.", "es": "el cambio de contraseña está desactivado en esta instalación."},
    "profile_logged_as": {"cs": "Přihlášen jako:", "en": "Logged in as:", "de": "Angemeldet als:", "ru": "Вход выполнен как:", "es": "Sesión iniciada como:"},
    "profile_current_password": {"cs": "Stávající heslo", "en": "Current password", "de": "Aktuelles Passwort", "ru": "Текущий пароль", "es": "Contraseña actual"},
    "profile_new_password": {"cs": "Nové heslo", "en": "New password", "de": "Neues Passwort", "ru": "Новый пароль", "es": "Nueva contraseña"},
    "profile_password_min": {"cs": "Minimálně 8 znaků.", "en": "Minimum 8 characters.", "de": "Mindestens 8 Zeichen.", "ru": "Минимум 8 символов.", "es": "Mínimo 8 caracteres."},
    "profile_confirm_password": {"cs": "Potvrzení nového hesla", "en": "Confirm new password", "de": "Neues Passwort bestätigen", "ru": "Подтверждение нового пароля", "es": "Confirmar nueva contraseña"},
    "profile_btn_change_password": {"cs": "Změnit heslo", "en": "Change password", "de": "Passwort ändern", "ru": "Сменить пароль", "es": "Cambiar contraseña"},
    "profile_lang_title": {"cs": "Jazyk rozhraní", "en": "Interface language", "de": "Oberflächensprache", "ru": "Язык интерфейса", "es": "Idioma de la interfaz"},
    "profile_lang_description": {"cs": "Trvalá volba jazyka uživatelského rozhraní. Volba se uloží a aplikuje napříč prohlížeči.", "en": "Persistent UI language preference. The choice is saved and applied across browsers.", "de": "Dauerhafte Sprachauswahl der Benutzeroberfläche. Die Auswahl wird gespeichert und browserübergreifend angewendet.", "ru": "Постоянный выбор языка интерфейса. Выбор сохраняется и применяется во всех браузерах.", "es": "Preferencia persistente del idioma de la interfaz. La opción se guarda y se aplica en todos los navegadores."},
    "profile_lang_active": {"cs": "Aktuálně aktivní:", "en": "Currently active:", "de": "Aktuell aktiv:", "ru": "Сейчас активен:", "es": "Activo actualmente:"},
    "profile_lang_auto": {"cs": "automaticky podle prohlížeče", "en": "auto-detected from browser", "de": "automatisch vom Browser", "ru": "автоматически из браузера", "es": "detectado automáticamente del navegador"},
    "profile_btn_save_lang": {"cs": "Uložit jazyk", "en": "Save language", "de": "Sprache speichern", "ru": "Сохранить язык", "es": "Guardar idioma"},

    # ── Profile / server-side messages ──
    "profile_msg_password_changed": {"cs": "Heslo bylo úspěšně změněno.", "en": "Password successfully changed.", "de": "Passwort erfolgreich geändert.", "ru": "Пароль успешно изменён.", "es": "Contraseña cambiada con éxito."},
    "profile_err_password_mismatch": {"cs": "Potvrzení hesla nesouhlasí s novým heslem.", "en": "Password confirmation does not match the new password.", "de": "Passwortbestätigung stimmt nicht mit dem neuen Passwort überein.", "ru": "Подтверждение пароля не совпадает с новым паролем.", "es": "La confirmación de la contraseña no coincide con la nueva contraseña."},
    "profile_err_password_too_short": {"cs": "Nové heslo musí mít alespoň 8 znaků.", "en": "New password must be at least 8 characters.", "de": "Das neue Passwort muss mindestens 8 Zeichen lang sein.", "ru": "Новый пароль должен содержать не менее 8 символов.", "es": "La nueva contraseña debe tener al menos 8 caracteres."},
    "profile_err_password_same": {"cs": "Nové heslo se musí lišit od stávajícího.", "en": "New password must differ from the current one.", "de": "Das neue Passwort muss sich vom aktuellen unterscheiden.", "ru": "Новый пароль должен отличаться от текущего.", "es": "La nueva contraseña debe ser diferente de la actual."},
    "profile_err_current_wrong": {"cs": "Stávající heslo není správně.", "en": "Current password is incorrect.", "de": "Aktuelles Passwort ist nicht korrekt.", "ru": "Текущий пароль неверен.", "es": "La contraseña actual es incorrecta."},
    "profile_err_demo_blocked": {"cs": "Změna hesla není v demo režimu povolena.", "en": "Password change is not allowed in demo mode.", "de": "Passwortänderung ist im Demo-Modus nicht erlaubt.", "ru": "Смена пароля не разрешена в демо-режиме.", "es": "El cambio de contraseña no está permitido en modo demo."},
    "profile_err_invalid_lang": {"cs": "Neplatný kód jazyka.", "en": "Invalid language code.", "de": "Ungültiger Sprachcode.", "ru": "Неверный код языка.", "es": "Código de idioma no válido."},

    # ── Campaign detail ──
    "detail_progress": {"cs": "Průběh odesílání", "en": "Sending progress", "de": "Sendefortschritt", "ru": "Прогресс отправки", "es": "Progreso de envío"},
    "detail_recipients": {"cs": "Příjemci", "en": "Recipients", "de": "Empfänger", "ru": "Получатели", "es": "Destinatarios"},
    "detail_stat_failed": {"cs": "Selhání", "en": "Failed", "de": "Fehlgeschlagen", "ru": "Ошибки", "es": "Fallidos"},
    "detail_stat_blocked": {"cs": "Blokováno", "en": "Blocked", "de": "Blockiert", "ru": "Заблокировано", "es": "Bloqueados"},
    "detail_stat_unsubscribed": {"cs": "Odhlášení", "en": "Unsubscribes", "de": "Abmeldungen", "ru": "Отписки", "es": "Bajas"},
    "detail_settings_title": {"cs": "Nastavení kampaně", "en": "Campaign settings", "de": "Kampagneneinstellungen", "ru": "Настройки кампании", "es": "Configuración de campaña"},
    "detail_template": {"cs": "Šablona", "en": "Template", "de": "Vorlage", "ru": "Шаблон", "es": "Plantilla"},
    "detail_subject": {"cs": "Předmět", "en": "Subject", "de": "Betreff", "ru": "Тема", "es": "Asunto"},
    "detail_contact_list": {"cs": "Kontaktní seznam", "en": "Contact list", "de": "Kontaktliste", "ru": "Список контактов", "es": "Lista de contactos"},
    "detail_batch_size": {"cs": "Dávka", "en": "Batch", "de": "Stapel", "ru": "Партия", "es": "Lote"},
    "detail_interval": {"cs": "Interval", "en": "Interval", "de": "Intervall", "ru": "Интервал", "es": "Intervalo"},
    "detail_pause_between_batches": {"cs": "Pauza mezi dávkami", "en": "Pause between batches", "de": "Pause zwischen Stapeln", "ru": "Пауза между партиями", "es": "Pausa entre lotes"},
    "detail_no_pause": {"cs": "bez pauzy", "en": "no pause", "de": "ohne Pause", "ru": "без паузы", "es": "sin pausa"},
    "detail_server_rotation": {"cs": "Rotace serverů", "en": "Server rotation", "de": "Server-Rotation", "ru": "Ротация серверов", "es": "Rotación de servidores"},
    "detail_rotation_per": {"cs": "po", "en": "per", "de": "je", "ru": "по", "es": "cada"},
    "detail_created_at": {"cs": "Vytvořeno", "en": "Created", "de": "Erstellt", "ru": "Создано", "es": "Creado"},
    "detail_started_at": {"cs": "Spuštěno", "en": "Started", "de": "Gestartet", "ru": "Запущено", "es": "Iniciado"},
    "detail_completed_at": {"cs": "Dokončeno", "en": "Completed", "de": "Abgeschlossen", "ru": "Завершено", "es": "Completado"},
    "detail_assigned_servers": {"cs": "Přiřazené servery", "en": "Assigned servers", "de": "Zugewiesene Server", "ru": "Назначенные серверы", "es": "Servidores asignados"},
    "detail_no_servers_assigned": {"cs": "Žádné servery přiřazeny.", "en": "No servers assigned.", "de": "Keine Server zugewiesen.", "ru": "Серверы не назначены.", "es": "Sin servidores asignados."},
    "detail_sent_label": {"cs": "odesláno", "en": "sent", "de": "gesendet", "ru": "отправлено", "es": "enviados"},
    "detail_send_log_title": {"cs": "Log odesílání (posledních 50)", "en": "Send log (last 50)", "de": "Sendeprotokoll (letzte 50)", "ru": "Журнал отправки (последние 50)", "es": "Registro de envíos (últimos 50)"},
    "detail_sending_in_progress": {"cs": "Odesílání probíhá", "en": "Sending in progress", "de": "Versand läuft", "ru": "Идёт отправка", "es": "Envío en curso"},
    "detail_no_sending_yet": {"cs": "Zatím žádné odesílání.", "en": "No sending yet.", "de": "Noch kein Versand.", "ru": "Пока нет отправок.", "es": "Sin envíos aún."},
    "detail_th_error": {"cs": "Chyba", "en": "Error", "de": "Fehler", "ru": "Ошибка", "es": "Error"},
    "detail_btn_back": {"cs": "Zpět na kampaně", "en": "Back to campaigns", "de": "Zurück zu Kampagnen", "ru": "Назад к кампаниям", "es": "Volver a campañas"},
    "detail_btn_download_report": {"cs": "Stáhnout report", "en": "Download report", "de": "Report herunterladen", "ru": "Скачать отчёт", "es": "Descargar informe"},
    "detail_btn_edit_campaign": {"cs": "Upravit kampaň", "en": "Edit campaign", "de": "Kampagne bearbeiten", "ru": "Редактировать кампанию", "es": "Editar campaña"},
    "detail_btn_resend": {"cs": "Znovu odeslat", "en": "Resend", "de": "Erneut senden", "ru": "Отправить снова", "es": "Reenviar"},
    "detail_btn_delete_campaign": {"cs": "Smazat kampaň", "en": "Delete campaign", "de": "Kampagne löschen", "ru": "Удалить кампанию", "es": "Eliminar campaña"},
    "detail_btn_start_now": {"cs": "Spustit teď", "en": "Start now", "de": "Jetzt starten", "ru": "Запустить сейчас", "es": "Iniciar ahora"},

    # ── Campaign detail / confirm dialogs ──
    "confirm_start_campaign_named": {"cs": "Spustit kampaň", "en": "Start campaign", "de": "Kampagne starten", "ru": "Запустить кампанию", "es": "Iniciar campaña"},
    "confirm_stop_irreversible": {"cs": "Zastavit kampaň? Tato akce je nevratná.", "en": "Stop campaign? This action is irreversible.", "de": "Kampagne stoppen? Diese Aktion ist unwiderruflich.", "ru": "Остановить кампанию? Это действие необратимо.", "es": "¿Detener campaña? Esta acción es irreversible."},
    "confirm_resend_campaign": {"cs": "Znovu odeslat kampaň? Smaže se starý log odesílání a kampaň se vrátí do draftu.", "en": "Resend campaign? The old send log will be deleted and the campaign will return to draft.", "de": "Kampagne erneut senden? Das alte Sendeprotokoll wird gelöscht und die Kampagne kehrt zum Entwurf zurück.", "ru": "Отправить кампанию снова? Старый журнал отправки будет удалён, и кампания вернётся в черновик.", "es": "¿Reenviar campaña? Se borrará el registro anterior y la campaña volverá a borrador."},

    # ── Test email modal ──
    "test_modal_title": {"cs": "Odeslat testovací email", "en": "Send test email", "de": "Test-E-Mail senden", "ru": "Отправить тестовое письмо", "es": "Enviar email de prueba"},
    "test_recipient_email": {"cs": "Email příjemce", "en": "Recipient email", "de": "Empfänger-E-Mail", "ru": "Email получателя", "es": "Email del destinatario"},
    "test_sending_server": {"cs": "Odesílací server", "en": "Sending server", "de": "Sende-Server", "ru": "Отправляющий сервер", "es": "Servidor de envío"},
    "test_help": {"cs": "Odešle šablonu kampaně s testovacími daty a předmětem [TEST]. Proměnné budou nahrazeny ukázkovými hodnotami.", "en": "Sends the campaign template with test data and subject [TEST]. Variables will be replaced with sample values.", "de": "Sendet die Kampagnenvorlage mit Testdaten und Betreff [TEST]. Variablen werden durch Beispielwerte ersetzt.", "ru": "Отправит шаблон кампании с тестовыми данными и темой [TEST]. Переменные будут заменены примерами.", "es": "Envía la plantilla de la campaña con datos de prueba y asunto [TEST]. Las variables se reemplazarán por valores de ejemplo."},
    "test_btn_send": {"cs": "Odeslat test", "en": "Send test", "de": "Test senden", "ru": "Отправить тест", "es": "Enviar prueba"},

    # ── Campaign form (new/edit) ──
    "cform_breadcrumb_new": {"cs": "Nová", "en": "New", "de": "Neu", "ru": "Новая", "es": "Nueva"},
    "cform_basic_info": {"cs": "Základní údaje", "en": "Basic info", "de": "Grundinfo", "ru": "Основная информация", "es": "Información básica"},
    "cform_name": {"cs": "Název kampaně", "en": "Campaign name", "de": "Kampagnenname", "ru": "Название кампании", "es": "Nombre de la campaña"},
    "cform_name_placeholder": {"cs": "Newsletter březen 2025", "en": "Newsletter March 2025", "de": "Newsletter März 2025", "ru": "Рассылка март 2025", "es": "Newsletter marzo 2025"},
    "cform_template": {"cs": "Email šablona", "en": "Email template", "de": "E-Mail-Vorlage", "ru": "Email-шаблон", "es": "Plantilla de email"},
    "cform_select_template": {"cs": "-- Vyberte šablonu --", "en": "-- Select template --", "de": "-- Vorlage wählen --", "ru": "-- Выберите шаблон --", "es": "-- Seleccionar plantilla --"},
    "cform_contact_list": {"cs": "Kontaktní seznam", "en": "Contact list", "de": "Kontaktliste", "ru": "Список контактов", "es": "Lista de contactos"},
    "cform_select_list": {"cs": "-- Vyberte seznam --", "en": "-- Select list --", "de": "-- Liste wählen --", "ru": "-- Выберите список --", "es": "-- Seleccionar lista --"},
    "cform_country_filter": {"cs": "Filtr podle státu", "en": "Country filter", "de": "Länderfilter", "ru": "Фильтр по стране", "es": "Filtro por país"},
    "cform_country_all": {"cs": "Všechny státy", "en": "All countries", "de": "Alle Länder", "ru": "Все страны", "es": "Todos los países"},
    "cform_country_other": {"cs": "Ostatní (bez CZ/SK/DE/AT/PL/HU)", "en": "Other (excl. CZ/SK/DE/AT/PL/HU)", "de": "Andere (ohne CZ/SK/DE/AT/PL/HU)", "ru": "Другие (кроме CZ/SK/DE/AT/PL/HU)", "es": "Otros (sin CZ/SK/DE/AT/PL/HU)"},
    "cform_country_help": {"cs": "Omezí kampaň pouze na kontakty z vybraného státu. Kontakty bez zjištěného státu budou přeskočeny.", "en": "Limits the campaign to contacts from the selected country. Contacts without a detected country will be skipped.", "de": "Beschränkt die Kampagne auf Kontakte aus dem gewählten Land. Kontakte ohne erkanntes Land werden übersprungen.", "ru": "Ограничит кампанию только контактами из выбранной страны. Контакты без определённой страны будут пропущены.", "es": "Limita la campaña a contactos del país seleccionado. Los contactos sin país detectado se omitirán."},

    # ── Country names ──
    "country_cz": {"cs": "Česká republika", "en": "Czech Republic", "de": "Tschechien", "ru": "Чехия", "es": "República Checa"},
    "country_sk": {"cs": "Slovensko", "en": "Slovakia", "de": "Slowakei", "ru": "Словакия", "es": "Eslovaquia"},
    "country_de": {"cs": "Německo", "en": "Germany", "de": "Deutschland", "ru": "Германия", "es": "Alemania"},
    "country_at": {"cs": "Rakousko", "en": "Austria", "de": "Österreich", "ru": "Австрия", "es": "Austria"},
    "country_pl": {"cs": "Polsko", "en": "Poland", "de": "Polen", "ru": "Польша", "es": "Polonia"},
    "country_hu": {"cs": "Maďarsko", "en": "Hungary", "de": "Ungarn", "ru": "Венгрия", "es": "Hungría"},

    # ── Throttling form ──
    "cform_throttle_intro": {"cs": "Nastavení rychlosti a rozložení odesílání", "en": "Sending speed and pacing settings", "de": "Geschwindigkeits- und Verteilungseinstellungen", "ru": "Настройки скорости и распределения отправки", "es": "Ajustes de velocidad y distribución del envío"},
    "cform_batch_size": {"cs": "Velikost dávky", "en": "Batch size", "de": "Stapelgröße", "ru": "Размер партии", "es": "Tamaño del lote"},
    "cform_batch_size_help": {"cs": "Kolik emailů odeslat v jedné dávce", "en": "How many emails to send in one batch", "de": "Wie viele E-Mails in einem Stapel gesendet werden", "ru": "Сколько писем отправить в одной партии", "es": "Cuántos emails enviar en un lote"},
    "cform_interval_min": {"cs": "Min. interval mezi emaily (s)", "en": "Min. interval between emails (s)", "de": "Min. Intervall zwischen E-Mails (s)", "ru": "Мин. интервал между письмами (с)", "es": "Intervalo mín. entre emails (s)"},
    "cform_interval_max": {"cs": "Max. interval mezi emaily (s)", "en": "Max. interval between emails (s)", "de": "Max. Intervall zwischen E-Mails (s)", "ru": "Макс. интервал между письмами (с)", "es": "Intervalo máx. entre emails (s)"},
    "cform_interval_help": {"cs": "Náhodný interval mezi min a max simuluje přirozené chování", "en": "Random interval between min and max mimics natural behavior", "de": "Zufälliges Intervall zwischen Min und Max simuliert natürliches Verhalten", "ru": "Случайный интервал между мин и макс имитирует естественное поведение", "es": "Un intervalo aleatorio entre mín y máx simula un comportamiento natural"},
    "cform_pause_min": {"cs": "Pauza mezi dávkami (minuty)", "en": "Pause between batches (minutes)", "de": "Pause zwischen Stapeln (Minuten)", "ru": "Пауза между партиями (минуты)", "es": "Pausa entre lotes (minutos)"},
    "cform_pause_help": {"cs": "Jak dlouho čekat po odeslání celé dávky, než začne další. 0 = bez pauzy.", "en": "How long to wait after sending a batch before starting the next. 0 = no pause.", "de": "Wie lange nach dem Stapel zu warten, bevor der nächste beginnt. 0 = ohne Pause.", "ru": "Сколько ждать после отправки партии перед следующей. 0 = без паузы.", "es": "Cuánto esperar tras enviar un lote antes del siguiente. 0 = sin pausa."},
    "cform_presets": {"cs": "Rychlé předvolby", "en": "Quick presets", "de": "Schnellvorlagen", "ru": "Быстрые предустановки", "es": "Preajustes rápidos"},
    "preset_careful": {"cs": "Opatrný", "en": "Careful", "de": "Vorsichtig", "ru": "Осторожный", "es": "Prudente"},
    "preset_balanced": {"cs": "Vyvážený", "en": "Balanced", "de": "Ausgewogen", "ru": "Сбалансированный", "es": "Equilibrado"},
    "preset_fast": {"cs": "Rychlý", "en": "Fast", "de": "Schnell", "ru": "Быстрый", "es": "Rápido"},
    "preset_warmup": {"cs": "Warm-up", "en": "Warm-up", "de": "Aufwärmen", "ru": "Прогрев", "es": "Calentamiento"},
    "cform_timeline_label": {"cs": "Vizualizace jedné dávky (prvních 60s)", "en": "One-batch visualization (first 60s)", "de": "Visualisierung eines Stapels (erste 60s)", "ru": "Визуализация одной партии (первые 60с)", "es": "Visualización de un lote (primeros 60s)"},

    # ── Calculator (JS strings) ──
    "calc_interval": {"cs": "Interval", "en": "Interval", "de": "Intervall", "ru": "Интервал", "es": "Intervalo"},
    "calc_avg": {"cs": "prům.", "en": "avg", "de": "Ø", "ru": "ср.", "es": "prom."},
    "calc_speed": {"cs": "Rychlost", "en": "Speed", "de": "Geschwindigkeit", "ru": "Скорость", "es": "Velocidad"},
    "calc_email_per_min": {"cs": "email/min", "en": "email/min", "de": "E-Mail/min", "ru": "писем/мин", "es": "email/min"},
    "calc_batch_time": {"cs": "Čas dávky", "en": "Batch time", "de": "Stapelzeit", "ru": "Время партии", "es": "Tiempo del lote"},
    "calc_pause_after": {"cs": "Pauza po dávce", "en": "Pause after batch", "de": "Pause nach Stapel", "ru": "Пауза после партии", "es": "Pausa tras lote"},
    "calc_full_cycle": {"cs": "Celý cyklus", "en": "Full cycle", "de": "Voller Zyklus", "ru": "Полный цикл", "es": "Ciclo completo"},
    "calc_emails_per_hour": {"cs": "Emailů za hodinu", "en": "Emails per hour", "de": "E-Mails pro Stunde", "ru": "Писем в час", "es": "Emails por hora"},
    "calc_flow": {"cs": "Průběh", "en": "Flow", "de": "Ablauf", "ru": "Процесс", "es": "Flujo"},
    "calc_emails": {"cs": "emailů", "en": "emails", "de": "E-Mails", "ru": "писем", "es": "emails"},
    "calc_pause": {"cs": "Pauza", "en": "Pause", "de": "Pause", "ru": "Пауза", "es": "Pausa"},
    "calc_min_short": {"cs": "min", "en": "min", "de": "min", "ru": "мин", "es": "min"},
    "calc_more": {"cs": "dalších", "en": "more", "de": "weitere", "ru": "ещё", "es": "más"},
    "calc_no_pause_label": {"cs": "(bez pauzy)", "en": "(no pause)", "de": "(ohne Pause)", "ru": "(без паузы)", "es": "(sin pausa)"},
    "calc_warn_too_fast": {"cs": "Příliš rychlé! Interval pod 3s může vést k blokaci.", "en": "Too fast! Intervals under 3s can lead to blocking.", "de": "Zu schnell! Intervalle unter 3s können zu Sperrung führen.", "ru": "Слишком быстро! Интервал меньше 3с может привести к блокировке.", "es": "¡Demasiado rápido! Intervalos por debajo de 3s pueden bloquear."},
    "calc_warn_min_max": {"cs": "Min. interval je větší než max. interval!", "en": "Min interval is greater than max interval!", "de": "Min-Intervall ist größer als Max-Intervall!", "ru": "Мин. интервал больше макс. интервала!", "es": "¡El intervalo mín es mayor que el máx!"},
    "calc_warn_no_pause": {"cs": "Bez pauzy mezi dávkami – emaily se budou odesílat nepřetržitě.", "en": "No pause between batches — emails will send continuously.", "de": "Keine Pause zwischen Stapeln — E-Mails werden kontinuierlich gesendet.", "ru": "Без паузы между партиями — письма будут отправляться непрерывно.", "es": "Sin pausa entre lotes — los emails se enviarán de forma continua."},

    # ── Server selection ──
    "cform_servers_title": {"cs": "Mail servery", "en": "Mail servers", "de": "Mail Server", "ru": "Почтовые серверы", "es": "Servidores"},
    "cform_servers_intro": {"cs": "Vyberte servery a nastavte rotaci", "en": "Select servers and configure rotation", "de": "Server auswählen und Rotation einstellen", "ru": "Выберите серверы и настройте ротацию", "es": "Seleccione servidores y configure la rotación"},
    "cform_rotation_mode": {"cs": "Režim rotace", "en": "Rotation mode", "de": "Rotationsmodus", "ru": "Режим ротации", "es": "Modo de rotación"},
    "cform_rotation_round_robin": {"cs": "Round Robin – střídání po jednom", "en": "Round Robin — one by one", "de": "Round Robin — einzeln wechseln", "ru": "Round Robin — поочерёдно", "es": "Round Robin — uno por uno"},
    "cform_rotation_batch": {"cs": "Batch – střídání po dávkách", "en": "Batch — switch every N", "de": "Batch — Wechsel nach Stapeln", "ru": "Batch — смена партиями", "es": "Batch — cambio por lotes"},
    "cform_rotation_weighted": {"cs": "Weighted – podle váhy serveru", "en": "Weighted — by server weight", "de": "Gewichtet — nach Server-Gewicht", "ru": "Weighted — по весу сервера", "es": "Ponderado — por peso del servidor"},
    "cform_server_batch_size": {"cs": "Velikost server dávky", "en": "Server batch size", "de": "Server-Stapelgröße", "ru": "Размер партии сервера", "es": "Tamaño del lote por servidor"},
    "cform_server_batch_help": {"cs": "Kolik emailů odeslat přes jeden server, než se přepne na další", "en": "How many emails to send via one server before switching", "de": "Wie viele E-Mails über einen Server, bevor gewechselt wird", "ru": "Сколько писем отправлять через один сервер до переключения", "es": "Cuántos emails enviar por servidor antes de cambiar"},
    "cform_servers_for_campaign": {"cs": "Servery pro kampaň", "en": "Servers for campaign", "de": "Server für Kampagne", "ru": "Серверы для кампании", "es": "Servidores para la campaña"},
    "cform_no_active_servers": {"cs": "Nemáte žádné aktivní servery.", "en": "You have no active servers.", "de": "Sie haben keine aktiven Server.", "ru": "У вас нет активных серверов.", "es": "No tiene servidores activos."},
    "cform_add_server": {"cs": "Přidejte server", "en": "Add a server", "de": "Server hinzufügen", "ru": "Добавьте сервер", "es": "Añada un servidor"},

    # ── How it works info card ──
    "cform_how_title": {"cs": "Jak to funguje", "en": "How it works", "de": "So funktioniert es", "ru": "Как это работает", "es": "Cómo funciona"},
    "cform_how_batch_label": {"cs": "Dávka", "en": "Batch", "de": "Stapel", "ru": "Партия", "es": "Lote"},
    "cform_how_batch_desc": {"cs": "Systém odešle nastavený počet emailů s náhodným intervalem mezi min–max.", "en": "The system sends the configured number of emails with a random interval between min and max.", "de": "Das System sendet die festgelegte Anzahl E-Mails mit zufälligem Intervall zwischen Min und Max.", "ru": "Система отправляет заданное количество писем со случайным интервалом между мин и макс.", "es": "El sistema envía el número configurado de emails con un intervalo aleatorio entre mín y máx."},
    "cform_how_pause_label": {"cs": "Pauza", "en": "Pause", "de": "Pause", "ru": "Пауза", "es": "Pausa"},
    "cform_how_pause_desc": {"cs": "Po odeslání celé dávky systém čeká nastavenou pauzu.", "en": "After sending a batch the system waits the configured pause.", "de": "Nach dem Senden eines Stapels wartet das System die eingestellte Pause.", "ru": "После отправки партии система ждёт заданную паузу.", "es": "Tras enviar un lote, el sistema espera la pausa configurada."},
    "cform_how_repeat_label": {"cs": "Opakování", "en": "Repeat", "de": "Wiederholung", "ru": "Повторение", "es": "Repetición"},
    "cform_how_repeat_desc": {"cs": "Po pauze začne další dávka, dokud nejsou všichni příjemci obslouženi.", "en": "After the pause, the next batch starts until all recipients have been served.", "de": "Nach der Pause beginnt der nächste Stapel, bis alle Empfänger bedient sind.", "ru": "После паузы начинается следующая партия, пока не будут охвачены все получатели.", "es": "Tras la pausa comienza el siguiente lote hasta atender a todos los destinatarios."},
    "cform_how_example": {"cs": "Příklad: 100 emailů, interval 30–42s, pauza 30 min", "en": "Example: 100 emails, interval 30–42s, pause 30 min", "de": "Beispiel: 100 E-Mails, Intervall 30–42s, Pause 30 min", "ru": "Пример: 100 писем, интервал 30–42с, пауза 30 мин", "es": "Ejemplo: 100 emails, intervalo 30–42s, pausa 30 min"},
    "cform_how_example_line1": {"cs": "100 emailů se odešle za ~60 min", "en": "100 emails will be sent in ~60 min", "de": "100 E-Mails werden in ~60 min gesendet", "ru": "100 писем будут отправлены за ~60 мин", "es": "100 emails se enviarán en ~60 min"},
    "cform_how_example_line2": {"cs": "30 min pauza", "en": "30 min pause", "de": "30 min Pause", "ru": "30 мин паузы", "es": "30 min de pausa"},
    "cform_how_example_line3": {"cs": "dalších 100 emailů za ~60 min", "en": "another 100 emails in ~60 min", "de": "weitere 100 E-Mails in ~60 min", "ru": "ещё 100 писем за ~60 мин", "es": "otros 100 emails en ~60 min"},
    "cform_how_example_line4": {"cs": "atd.", "en": "etc.", "de": "usw.", "ru": "и так далее", "es": "etc."},

    # ── Submit / cancel ──
    "cform_submit_create_draft": {"cs": "Vytvořit kampaň (draft)", "en": "Create campaign (draft)", "de": "Kampagne erstellen (Entwurf)", "ru": "Создать кампанию (черновик)", "es": "Crear campaña (borrador)"},

    # ── Campaign edit form (additional keys) ──
    "cform_breadcrumb_edit": {"cs": "Upravit", "en": "Edit", "de": "Bearbeiten", "ru": "Редактировать", "es": "Editar"},
    "cform_page_title_edit": {"cs": "Upravit kampaň", "en": "Edit campaign", "de": "Kampagne bearbeiten", "ru": "Редактировать кампанию", "es": "Editar campaña"},
    "cform_interval_min_short": {"cs": "Min. interval (s)", "en": "Min. interval (s)", "de": "Min. Intervall (s)", "ru": "Мин. интервал (с)", "es": "Intervalo mín (s)"},
    "cform_interval_max_short": {"cs": "Max. interval (s)", "en": "Max. interval (s)", "de": "Max. Intervall (s)", "ru": "Макс. интервал (с)", "es": "Intervalo máx (s)"},
    "cform_pause_min_short": {"cs": "Pauza mezi dávkami (min)", "en": "Pause between batches (min)", "de": "Pause zwischen Stapeln (min)", "ru": "Пауза между партиями (мин)", "es": "Pausa entre lotes (min)"},
    "cform_servers_short": {"cs": "Servery", "en": "Servers", "de": "Server", "ru": "Серверы", "es": "Servidores"},
    "cform_submit_save": {"cs": "Uložit změny", "en": "Save changes", "de": "Änderungen speichern", "ru": "Сохранить изменения", "es": "Guardar cambios"},

    # ── Contacts list ──
    "contacts_breadcrumb": {"cs": "Kontakty", "en": "Contacts", "de": "Kontakte", "ru": "Контакты", "es": "Contactos"},
    "contacts_btn_export_clean": {"cs": "Export čistý", "en": "Export clean", "de": "Sauberer Export", "ru": "Чистый экспорт", "es": "Exportar limpios"},
    "contacts_btn_export_clean_title": {"cs": "Exportovat aktivní kontakty", "en": "Export active contacts", "de": "Aktive Kontakte exportieren", "ru": "Экспортировать активные контакты", "es": "Exportar contactos activos"},
    "contacts_search_placeholder": {"cs": "Hledat email, jméno...", "en": "Search email, name...", "de": "Email, Name suchen...", "ru": "Поиск email, имя...", "es": "Buscar email, nombre..."},
    "contacts_filter_all_statuses": {"cs": "Všechny stavy", "en": "All statuses", "de": "Alle Status", "ru": "Все статусы", "es": "Todos los estados"},
    "contacts_filter_all_lists": {"cs": "Všechny seznamy", "en": "All lists", "de": "Alle Listen", "ru": "Все списки", "es": "Todas las listas"},
    "contacts_status_active": {"cs": "Aktivní", "en": "Active", "de": "Aktiv", "ru": "Активные", "es": "Activos"},
    "contacts_status_unsubscribed": {"cs": "Odhlášení", "en": "Unsubscribed", "de": "Abgemeldet", "ru": "Отписавшиеся", "es": "Dados de baja"},
    "contacts_status_bounced": {"cs": "Bounced", "en": "Bounced", "de": "Bounced", "ru": "Bounced", "es": "Bounced"},
    "contacts_status_invalid": {"cs": "Neplatní", "en": "Invalid", "de": "Ungültig", "ru": "Недействительные", "es": "No válidos"},
    "contacts_total": {"cs": "Celkem", "en": "Total", "de": "Insgesamt", "ru": "Всего", "es": "Total"},
    "contacts_unsubscribed_badge": {"cs": "odhlášen", "en": "unsubscribed", "de": "abgemeldet", "ru": "отписан", "es": "dado de baja"},
    "contacts_bulk_actions": {"cs": "Hromadné akce:", "en": "Bulk actions:", "de": "Massenaktionen:", "ru": "Массовые действия:", "es": "Acciones masivas:"},
    "contacts_bulk_delete_selected": {"cs": "Smazat vybrané", "en": "Delete selected", "de": "Ausgewählte löschen", "ru": "Удалить выбранные", "es": "Borrar seleccionados"},
    "contacts_bulk_delete_filtered": {"cs": "Smazat všech %d (filtr)", "en": "Delete all %d (filter)", "de": "Alle %d löschen (Filter)", "ru": "Удалить все %d (фильтр)", "es": "Borrar todos %d (filtro)"},
    "contacts_bulk_delete_bounced": {"cs": "Smazat všechny bounced", "en": "Delete all bounced", "de": "Alle Bounced löschen", "ru": "Удалить все bounced", "es": "Borrar todos los bounced"},
    "contacts_bulk_delete_unsubscribed": {"cs": "Smazat všechny odhlášené", "en": "Delete all unsubscribed", "de": "Alle Abgemeldeten löschen", "ru": "Удалить всех отписавшихся", "es": "Borrar todos los dados de baja"},
    "contacts_bulk_reset_stats": {"cs": "Resetovat statistiky otevřeno/kliknuto", "en": "Reset open/click statistics", "de": "Öffnungs-/Klick-Statistiken zurücksetzen", "ru": "Сбросить статистику открытий/кликов", "es": "Restablecer estadísticas de aperturas/clics"},
    "contacts_bulk_delete_all": {"cs": "Smazat VŠECHNY kontakty", "en": "Delete ALL contacts", "de": "ALLE Kontakte löschen", "ru": "Удалить ВСЕ контакты", "es": "Borrar TODOS los contactos"},
    "contacts_confirm_delete_filtered": {"cs": "Smazat VŠECH %d kontaktů odpovídajících filtru?", "en": "Delete ALL %d contacts matching the filter?", "de": "Alle %d Kontakte des Filters löschen?", "ru": "Удалить ВСЕ %d контактов, подходящих под фильтр?", "es": "¿Borrar TODOS los %d contactos del filtro?"},
    "contacts_confirm_delete_bounced": {"cs": "Smazat VŠECHNY bounced kontakty z celé databáze?", "en": "Delete ALL bounced contacts from the entire database?", "de": "ALLE bounced Kontakte aus der gesamten Datenbank löschen?", "ru": "Удалить ВСЕ bounced контакты из всей базы?", "es": "¿Borrar TODOS los contactos bounced de toda la base de datos?"},
    "contacts_confirm_delete_unsubscribed": {"cs": "Smazat VŠECHNY odhlášené kontakty z celé databáze?", "en": "Delete ALL unsubscribed contacts from the entire database?", "de": "ALLE abgemeldeten Kontakte aus der gesamten Datenbank löschen?", "ru": "Удалить ВСЕ отписавшихся контактов из всей базы?", "es": "¿Borrar TODOS los contactos dados de baja de toda la base de datos?"},
    "contacts_confirm_reset_stats": {"cs": "Resetovat statistiky otevření a kliknutí pro všechny kontakty a kampaně?", "en": "Reset open/click statistics for all contacts and campaigns?", "de": "Öffnungs- und Klick-Statistiken für alle Kontakte und Kampagnen zurücksetzen?", "ru": "Сбросить статистику открытий и кликов для всех контактов и кампаний?", "es": "¿Restablecer estadísticas de aperturas y clics de todos los contactos y campañas?"},
    "contacts_confirm_delete_all": {"cs": "POZOR! Smazat VŠECH %d kontaktů? Tato akce je nevratná!", "en": "WARNING! Delete ALL %d contacts? This action is irreversible!", "de": "ACHTUNG! Alle %d Kontakte löschen? Diese Aktion ist unwiderruflich!", "ru": "ВНИМАНИЕ! Удалить ВСЕ %d контактов? Это действие необратимо!", "es": "¡ATENCIÓN! ¿Borrar TODOS los %d contactos? ¡Esta acción es irreversible!"},
    "contacts_confirm_delete_n": {"cs": "Smazat %d vybraných kontaktů?", "en": "Delete %d selected contacts?", "de": "%d ausgewählte Kontakte löschen?", "ru": "Удалить %d выбранных контактов?", "es": "¿Borrar %d contactos seleccionados?"},
    "contacts_th_name": {"cs": "Jméno", "en": "Name", "de": "Name", "ru": "Имя", "es": "Nombre"},
    "contacts_th_lists": {"cs": "Seznamy", "en": "Lists", "de": "Listen", "ru": "Списки", "es": "Listas"},
    "contacts_th_added": {"cs": "Přidán", "en": "Added", "de": "Hinzugefügt", "ru": "Добавлен", "es": "Añadido"},
    "contacts_th_country": {"cs": "Stát", "en": "Country", "de": "Land", "ru": "Страна", "es": "País"},
    "contacts_th_opened": {"cs": "Otevřeno", "en": "Opened", "de": "Geöffnet", "ru": "Открыто", "es": "Abierto"},
    "contacts_th_clicked": {"cs": "Kliknuto", "en": "Clicked", "de": "Geklickt", "ru": "Кликов", "es": "Clics"},
    "contacts_empty_long": {"cs": "Žádné kontakty. Importujte CSV soubor nebo přidejte ručně.", "en": "No contacts yet. Import a CSV file or add manually.", "de": "Keine Kontakte. Importieren Sie eine CSV-Datei oder fügen Sie manuell hinzu.", "ru": "Нет контактов. Импортируйте CSV или добавьте вручную.", "es": "Sin contactos. Importe un archivo CSV o añada manualmente."},

    # ── Contact form (new/edit) ──
    "cf_breadcrumb_new": {"cs": "Nový kontakt", "en": "New contact", "de": "Neuer Kontakt", "ru": "Новый контакт", "es": "Nuevo contacto"},
    "cf_breadcrumb_edit": {"cs": "Upravit", "en": "Edit", "de": "Bearbeiten", "ru": "Редактировать", "es": "Editar"},
    "cf_page_title_new": {"cs": "Nový kontakt", "en": "New contact", "de": "Neuer Kontakt", "ru": "Новый контакт", "es": "Nuevo contacto"},
    "cf_page_title_edit": {"cs": "Upravit kontakt", "en": "Edit contact", "de": "Kontakt bearbeiten", "ru": "Редактировать контакт", "es": "Editar contacto"},
    "cf_first_name": {"cs": "Jméno", "en": "First name", "de": "Vorname", "ru": "Имя", "es": "Nombre"},
    "cf_last_name": {"cs": "Příjmení", "en": "Last name", "de": "Nachname", "ru": "Фамилия", "es": "Apellido"},
    "cf_company": {"cs": "Firma", "en": "Company", "de": "Firma", "ru": "Компания", "es": "Empresa"},
    "cf_tags": {"cs": "Tagy", "en": "Tags", "de": "Tags", "ru": "Теги", "es": "Etiquetas"},
    "cf_tags_placeholder": {"cs": "klient, vip", "en": "client, vip", "de": "Kunde, vip", "ru": "клиент, vip", "es": "cliente, vip"},
    "cf_tags_help": {"cs": "Oddělte čárkou", "en": "Separate with comma", "de": "Mit Komma trennen", "ru": "Разделяйте запятой", "es": "Separar con comas"},
    "cf_assign_to_lists": {"cs": "Zařadit do seznamů", "en": "Assign to lists", "de": "Zu Listen zuordnen", "ru": "Добавить в списки", "es": "Asignar a listas"},
    "cf_no_lists_warning": {"cs": "Žádné seznamy.", "en": "No lists yet.", "de": "Keine Listen.", "ru": "Нет списков.", "es": "Sin listas."},
    "cf_create_first_list": {"cs": "Vytvořte první seznam", "en": "Create the first list", "de": "Erste Liste erstellen", "ru": "Создайте первый список", "es": "Cree la primera lista"},
    "cf_to_assign_contact": {"cs": "aby bylo možné kontakt zařadit.", "en": "so the contact can be assigned.", "de": "damit der Kontakt zugeordnet werden kann.", "ru": "чтобы можно было добавить контакт.", "es": "para poder asignar el contacto."},

    # ── Contacts import ──
    "ci_breadcrumb": {"cs": "Import", "en": "Import", "de": "Import", "ru": "Импорт", "es": "Importar"},
    "ci_page_title": {"cs": "Import kontaktů z CSV", "en": "Import contacts from CSV", "de": "Kontakte aus CSV importieren", "ru": "Импорт контактов из CSV", "es": "Importar contactos desde CSV"},
    "ci_csv_file": {"cs": "CSV soubor", "en": "CSV file", "de": "CSV-Datei", "ru": "CSV файл", "es": "Archivo CSV"},
    "ci_csv_help": {"cs": "Podporované formáty: CSV s hlavičkou. Povinný sloupec: email", "en": "Supported formats: CSV with header. Required column: email", "de": "Unterstützte Formate: CSV mit Kopfzeile. Pflichtspalte: email", "ru": "Поддерживается: CSV с заголовком. Обязательный столбец: email", "es": "Formatos: CSV con encabezado. Columna obligatoria: email"},
    "ci_add_to_lists": {"cs": "Přidat do seznamů", "en": "Add to lists", "de": "Zu Listen hinzufügen", "ru": "Добавить в списки", "es": "Añadir a listas"},
    "ci_multi_lists_help": {"cs": "Můžete vybrat více seznamů najednou", "en": "You can select multiple lists", "de": "Sie können mehrere Listen wählen", "ru": "Можно выбрать несколько списков", "es": "Puede seleccionar varias listas"},
    "ci_no_lists_warning": {"cs": "Žádné seznamy.", "en": "No lists yet.", "de": "Keine Listen.", "ru": "Нет списков.", "es": "Sin listas."},
    "ci_create_list_before": {"cs": "Vytvořte seznam", "en": "Create a list", "de": "Liste erstellen", "ru": "Создайте список", "es": "Cree una lista"},
    "ci_before_import": {"cs": "před importem.", "en": "before importing.", "de": "vor dem Import.", "ru": "перед импортом.", "es": "antes de importar."},
    "ci_delimiter": {"cs": "Oddělovač", "en": "Delimiter", "de": "Trennzeichen", "ru": "Разделитель", "es": "Delimitador"},
    "ci_delim_comma": {"cs": "Čárka (,)", "en": "Comma (,)", "de": "Komma (,)", "ru": "Запятая (,)", "es": "Coma (,)"},
    "ci_delim_semicolon": {"cs": "Středník (;)", "en": "Semicolon (;)", "de": "Semikolon (;)", "ru": "Точка с запятой (;)", "es": "Punto y coma (;)"},
    "ci_delim_tab": {"cs": "Tab", "en": "Tab", "de": "Tab", "ru": "Tab", "es": "Tab"},
    "ci_skip_duplicates": {"cs": "Přeskočit duplicitní emaily", "en": "Skip duplicate emails", "de": "Doppelte E-Mails überspringen", "ru": "Пропустить дубликаты", "es": "Omitir emails duplicados"},
    "ci_btn_import": {"cs": "Importovat", "en": "Import", "de": "Importieren", "ru": "Импортировать", "es": "Importar"},
    "ci_csv_format_title": {"cs": "Formát CSV souboru", "en": "CSV file format", "de": "CSV-Dateiformat", "ru": "Формат CSV файла", "es": "Formato del archivo CSV"},
    "ci_csv_format_help": {"cs": "Povinný je pouze sloupec", "en": "Only the column", "de": "Pflicht ist nur die Spalte", "ru": "Обязательный только столбец", "es": "Solo es obligatoria la columna"},
    "ci_csv_format_help_2": {"cs": "Ostatní jsou volitelné.", "en": "is required. Others are optional.", "de": "ist erforderlich. Andere sind optional.", "ru": ". Остальные необязательны.", "es": ". Las demás son opcionales."},

    # ── Contact lists ──
    "lists_breadcrumb": {"cs": "Seznamy", "en": "Lists", "de": "Listen", "ru": "Списки", "es": "Listas"},
    "lists_page_title": {"cs": "Kontaktní seznamy", "en": "Contact lists", "de": "Kontaktlisten", "ru": "Списки контактов", "es": "Listas de contactos"},
    "lists_btn_new": {"cs": "Nový seznam", "en": "New list", "de": "Neue Liste", "ru": "Новый список", "es": "Nueva lista"},
    "lists_th_description": {"cs": "Popis", "en": "Description", "de": "Beschreibung", "ru": "Описание", "es": "Descripción"},
    "lists_th_contacts_count": {"cs": "Kontaktů", "en": "Contacts", "de": "Kontakte", "ru": "Контактов", "es": "Contactos"},
    "lists_btn_export_clean": {"cs": "Export čistý", "en": "Export clean", "de": "Sauberer Export", "ru": "Чистый экспорт", "es": "Exportar limpios"},
    "lists_btn_export_clean_title": {"cs": "Exportovat aktivní kontakty (bez bounced/odhlášených)", "en": "Export active contacts (excluding bounced/unsubscribed)", "de": "Aktive Kontakte exportieren (ohne Bounced/Abgemeldete)", "ru": "Экспорт активных контактов (без bounced/отписанных)", "es": "Exportar contactos activos (sin bounced/dados de baja)"},
    "lists_btn_export_all": {"cs": "Export vše", "en": "Export all", "de": "Alle exportieren", "ru": "Экспорт всех", "es": "Exportar todos"},
    "lists_btn_export_all_title": {"cs": "Exportovat všechny kontakty včetně bounced", "en": "Export all contacts including bounced", "de": "Alle Kontakte einschließlich Bounced exportieren", "ru": "Экспорт всех контактов включая bounced", "es": "Exportar todos los contactos incluyendo bounced"},
    "lists_btn_delete_list": {"cs": "Smazat seznam", "en": "Delete list", "de": "Liste löschen", "ru": "Удалить список", "es": "Eliminar lista"},
    "lists_btn_delete_all": {"cs": "Smazat vše", "en": "Delete all", "de": "Alles löschen", "ru": "Удалить всё", "es": "Eliminar todo"},
    "lists_confirm_delete_keep_contacts": {"cs": "Smazat seznam %s? Kontakty zůstanou.", "en": "Delete list %s? Contacts will be kept.", "de": "Liste %s löschen? Kontakte bleiben erhalten.", "ru": "Удалить список %s? Контакты останутся.", "es": "¿Eliminar la lista %s? Los contactos se conservarán."},
    "lists_confirm_delete_with_contacts": {"cs": "Smazat seznam %s I VŠECHNY KONTAKTY (%d)?", "en": "Delete list %s AND ALL CONTACTS (%d)?", "de": "Liste %s UND ALLE KONTAKTE (%d) löschen?", "ru": "Удалить список %s И ВСЕ КОНТАКТЫ (%d)?", "es": "¿Eliminar la lista %s Y TODOS LOS CONTACTOS (%d)?"},
    "lists_empty": {"cs": "Žádné kontaktní seznamy.", "en": "No contact lists yet.", "de": "Keine Kontaktlisten.", "ru": "Нет списков контактов.", "es": "Sin listas de contactos."},
    "lists_btn_create_list": {"cs": "Vytvořit seznam", "en": "Create list", "de": "Liste erstellen", "ru": "Создать список", "es": "Crear lista"},

    # ── List form ──
    "lf_breadcrumb": {"cs": "Nový", "en": "New", "de": "Neu", "ru": "Новый", "es": "Nueva"},
    "lf_page_title": {"cs": "Nový kontaktní seznam", "en": "New contact list", "de": "Neue Kontaktliste", "ru": "Новый список контактов", "es": "Nueva lista de contactos"},
    "lf_name": {"cs": "Název seznamu", "en": "List name", "de": "Listenname", "ru": "Название списка", "es": "Nombre de la lista"},
    "lf_name_placeholder": {"cs": "Newsletter Q1 2025", "en": "Newsletter Q1 2025", "de": "Newsletter Q1 2025", "ru": "Рассылка Q1 2025", "es": "Newsletter Q1 2025"},
    "lf_description": {"cs": "Popis", "en": "Description", "de": "Beschreibung", "ru": "Описание", "es": "Descripción"},
    "lf_description_placeholder": {"cs": "Volitelný popis...", "en": "Optional description...", "de": "Optionale Beschreibung...", "ru": "Необязательное описание...", "es": "Descripción opcional..."},
    "lf_btn_create": {"cs": "Vytvořit", "en": "Create", "de": "Erstellen", "ru": "Создать", "es": "Crear"},

    # ── Servers list ──
    "servers_breadcrumb": {"cs": "Mail Servery", "en": "Mail Servers", "de": "Mail Server", "ru": "Почтовые серверы", "es": "Servidores"},
    "servers_btn_add": {"cs": "Přidat server", "en": "Add server", "de": "Server hinzufügen", "ru": "Добавить сервер", "es": "Añadir servidor"},
    "servers_th_smtp_host": {"cs": "SMTP Host", "en": "SMTP Host", "de": "SMTP Host", "ru": "SMTP Хост", "es": "Host SMTP"},
    "servers_th_from": {"cs": "From", "en": "From", "de": "Von", "ru": "От", "es": "Desde"},
    "servers_th_weight": {"cs": "Váha", "en": "Weight", "de": "Gewicht", "ru": "Вес", "es": "Peso"},
    "servers_th_limit_hd": {"cs": "Limit H/D", "en": "Limit H/D", "de": "Limit S/T", "ru": "Лимит Ч/Д", "es": "Límite H/D"},
    "servers_btn_test_smtp_title": {"cs": "Test SMTP spojení", "en": "Test SMTP connection", "de": "SMTP-Verbindung testen", "ru": "Тест SMTP соединения", "es": "Probar conexión SMTP"},
    "servers_btn_test_imap_title": {"cs": "Test IMAP bounce spojení", "en": "Test IMAP bounce connection", "de": "IMAP-Bounce-Verbindung testen", "ru": "Тест IMAP bounce соединения", "es": "Probar conexión IMAP de bounce"},
    "servers_btn_test_email": {"cs": "Test email", "en": "Test email", "de": "Test-E-Mail", "ru": "Тестовое письмо", "es": "Email de prueba"},
    "servers_btn_test_email_title": {"cs": "Odeslat testovací email", "en": "Send test email", "de": "Test-E-Mail senden", "ru": "Отправить тестовое письмо", "es": "Enviar email de prueba"},
    "servers_confirm_delete": {"cs": "Opravdu smazat server %s?", "en": "Really delete server %s?", "de": "Server %s wirklich löschen?", "ru": "Действительно удалить сервер %s?", "es": "¿Eliminar realmente el servidor %s?"},
    "servers_empty": {"cs": "Žádné mail servery. Přidejte první SMTP server pro odesílání.", "en": "No mail servers yet. Add the first SMTP server for sending.", "de": "Keine Mail Server. Fügen Sie den ersten SMTP-Server hinzu.", "ru": "Нет почтовых серверов. Добавьте первый SMTP сервер.", "es": "Sin servidores. Añada el primer servidor SMTP para envíos."},
    "servers_test_modal_help": {"cs": "Odešle testovací email přes vybraný server pro ověření doručitelnosti.", "en": "Sends a test email via the selected server to verify deliverability.", "de": "Sendet eine Test-E-Mail über den ausgewählten Server zur Überprüfung der Zustellbarkeit.", "ru": "Отправляет тестовое письмо через выбранный сервер для проверки доставляемости.", "es": "Envía un email de prueba por el servidor seleccionado para verificar la entrega."},
    "servers_test_modal_title_prefix": {"cs": "Test email –", "en": "Test email —", "de": "Test-E-Mail —", "ru": "Тестовое письмо —", "es": "Email de prueba —"},

    # ── Server form ──
    "sf_breadcrumb_new": {"cs": "Nový server", "en": "New server", "de": "Neuer Server", "ru": "Новый сервер", "es": "Nuevo servidor"},
    "sf_breadcrumb_edit": {"cs": "Upravit", "en": "Edit", "de": "Bearbeiten", "ru": "Редактировать", "es": "Editar"},
    "sf_page_title_new": {"cs": "Nový mail server", "en": "New mail server", "de": "Neuer Mail Server", "ru": "Новый почтовый сервер", "es": "Nuevo servidor de email"},
    "sf_page_title_edit": {"cs": "Upravit server", "en": "Edit server", "de": "Server bearbeiten", "ru": "Редактировать сервер", "es": "Editar servidor"},
    "sf_smtp_section": {"cs": "SMTP odesílání", "en": "SMTP sending", "de": "SMTP-Versand", "ru": "SMTP отправка", "es": "Envío SMTP"},
    "sf_weight_label": {"cs": "Váha v rotaci (%)", "en": "Weight in rotation (%)", "de": "Gewicht in Rotation (%)", "ru": "Вес в ротации (%)", "es": "Peso en rotación (%)"},
    "sf_weight_help": {"cs": "Vyšší váha = více mailů přes tento server", "en": "Higher weight = more emails via this server", "de": "Höheres Gewicht = mehr E-Mails über diesen Server", "ru": "Больший вес = больше писем через этот сервер", "es": "Mayor peso = más emails por este servidor"},
    "sf_status_paused": {"cs": "Pozastavený", "en": "Paused", "de": "Pausiert", "ru": "Приостановлен", "es": "Pausado"},
    "sf_bounce_section": {"cs": "Kontrola bounců (IMAP)", "en": "Bounce checking (IMAP)", "de": "Bounce-Prüfung (IMAP)", "ru": "Проверка bounce (IMAP)", "es": "Comprobación de bounces (IMAP)"},
    "sf_bounce_intro": {"cs": "Systém bude pravidelně kontrolovat tuto schránku na vrácené emaily a automaticky označí kontakty jako bounced.", "en": "The system will periodically check this mailbox for bounced emails and automatically mark contacts as bounced.", "de": "Das System prüft dieses Postfach regelmäßig auf zurückgewiesene E-Mails und markiert Kontakte automatisch als bounced.", "ru": "Система будет регулярно проверять этот ящик на возвращённые письма и автоматически помечать контакты как bounced.", "es": "El sistema revisará periódicamente este buzón en busca de emails rebotados y marcará contactos como bounced."},
    "sf_bounce_enable": {"cs": "Zapnout kontrolu bounců", "en": "Enable bounce checking", "de": "Bounce-Prüfung aktivieren", "ru": "Включить проверку bounce", "es": "Activar comprobación de bounces"},
    "sf_imap_host": {"cs": "IMAP Host", "en": "IMAP Host", "de": "IMAP Host", "ru": "IMAP Хост", "es": "Host IMAP"},
    "sf_imap_port": {"cs": "IMAP Port", "en": "IMAP Port", "de": "IMAP Port", "ru": "IMAP Порт", "es": "Puerto IMAP"},
    "sf_imap_user": {"cs": "IMAP Uživatel", "en": "IMAP User", "de": "IMAP Benutzer", "ru": "IMAP Пользователь", "es": "Usuario IMAP"},
    "sf_imap_user_help": {"cs": "Schránka, kam přicházejí vrácené emaily", "en": "Mailbox where bounced emails arrive", "de": "Postfach, in das zurückgewiesene E-Mails ankommen", "ru": "Ящик, куда приходят возвращённые письма", "es": "Buzón donde llegan los emails rebotados"},
    "sf_imap_password": {"cs": "IMAP Heslo", "en": "IMAP Password", "de": "IMAP Passwort", "ru": "IMAP Пароль", "es": "Contraseña IMAP"},
    "sf_use_ssl": {"cs": "Použít SSL", "en": "Use SSL", "de": "SSL verwenden", "ru": "Использовать SSL", "es": "Usar SSL"},
    "sf_last_check": {"cs": "Poslední kontrola:", "en": "Last check:", "de": "Letzte Prüfung:", "ru": "Последняя проверка:", "es": "Última comprobación:"},

    # ── Domains list ──
    "dom_breadcrumb": {"cs": "Limity domén", "en": "Domain limits", "de": "Domain-Limits", "ru": "Лимиты доменов", "es": "Límites de dominio"},
    "dom_page_title": {"cs": "Limity cílových domén", "en": "Target domain limits", "de": "Ziel-Domain-Limits", "ru": "Лимиты целевых доменов", "es": "Límites de dominios objetivo"},
    "dom_card_title": {"cs": "Rate limity pro cílové domény", "en": "Rate limits for target domains", "de": "Rate-Limits für Ziel-Domains", "ru": "Ограничения скорости для целевых доменов", "es": "Límites de velocidad para dominios objetivo"},
    "dom_card_help": {"cs": "Maximální počet emailů na doménu příjemce za hodinu/den. Chrání před blokací.", "en": "Max emails per recipient domain per hour/day. Protects against blocking.", "de": "Maximale E-Mails pro Empfänger-Domain pro Stunde/Tag. Schützt vor Blockierung.", "ru": "Максимум писем на домен получателя в час/день. Защищает от блокировки.", "es": "Máximo de emails por dominio destinatario por hora/día. Protege contra el bloqueo."},
    "dom_label_domain": {"cs": "Doména", "en": "Domain", "de": "Domain", "ru": "Домен", "es": "Dominio"},
    "dom_label_max_hour": {"cs": "Max/hodina", "en": "Max/hour", "de": "Max/Stunde", "ru": "Макс/час", "es": "Máx/hora"},
    "dom_label_max_day": {"cs": "Max/den", "en": "Max/day", "de": "Max/Tag", "ru": "Макс/день", "es": "Máx/día"},
    "dom_btn_add": {"cs": "Přidat", "en": "Add", "de": "Hinzufügen", "ru": "Добавить", "es": "Añadir"},
    "dom_th_max_hour": {"cs": "Max / hodina", "en": "Max / hour", "de": "Max / Stunde", "ru": "Макс / час", "es": "Máx / hora"},
    "dom_th_max_day": {"cs": "Max / den", "en": "Max / day", "de": "Max / Tag", "ru": "Макс / день", "es": "Máx / día"},
    "dom_th_sent_hour": {"cs": "Odesláno (hodina)", "en": "Sent (hour)", "de": "Gesendet (Stunde)", "ru": "Отправлено (час)", "es": "Enviados (hora)"},
    "dom_th_sent_day": {"cs": "Odesláno (den)", "en": "Sent (day)", "de": "Gesendet (Tag)", "ru": "Отправлено (день)", "es": "Enviados (día)"},
    "dom_badge_blocked": {"cs": "BLOKOVÁNO", "en": "BLOCKED", "de": "BLOCKIERT", "ru": "ЗАБЛОКИРОВАНО", "es": "BLOQUEADO"},
    "dom_badge_reputation": {"cs": "REPUTACE", "en": "REPUTATION", "de": "REPUTATION", "ru": "РЕПУТАЦИЯ", "es": "REPUTACIÓN"},
    "dom_btn_unblock": {"cs": "Odblokovat", "en": "Unblock", "de": "Entsperren", "ru": "Разблокировать", "es": "Desbloquear"},
    "dom_btn_block": {"cs": "Blokovat", "en": "Block", "de": "Blockieren", "ru": "Заблокировать", "es": "Bloquear"},
    "dom_confirm_block": {"cs": "Zablokovat doménu %s?", "en": "Block domain %s?", "de": "Domain %s blockieren?", "ru": "Заблокировать домен %s?", "es": "¿Bloquear el dominio %s?"},
    "dom_confirm_delete": {"cs": "Smazat limit pro %s? (Tato akce odstraní limit, ne blokaci)", "en": "Delete limit for %s? (This removes the limit, not the block)", "de": "Limit für %s löschen? (Entfernt das Limit, nicht die Blockierung)", "ru": "Удалить лимит для %s? (Удаляет лимит, не блокировку)", "es": "¿Eliminar el límite de %s? (Elimina el límite, no el bloqueo)"},

    # ── Email templates list ──
    "etl_breadcrumb": {"cs": "Šablony", "en": "Templates", "de": "Vorlagen", "ru": "Шаблоны", "es": "Plantillas"},
    "etl_page_title": {"cs": "Email šablony", "en": "Email templates", "de": "E-Mail-Vorlagen", "ru": "Email-шаблоны", "es": "Plantillas de email"},
    "etl_btn_new": {"cs": "Nová šablona", "en": "New template", "de": "Neue Vorlage", "ru": "Новый шаблон", "es": "Nueva plantilla"},
    "etl_th_subject": {"cs": "Předmět", "en": "Subject", "de": "Betreff", "ru": "Тема", "es": "Asunto"},
    "etl_th_updated": {"cs": "Aktualizováno", "en": "Updated", "de": "Aktualisiert", "ru": "Обновлено", "es": "Actualizado"},
    "etl_btn_duplicate": {"cs": "Duplikovat", "en": "Duplicate", "de": "Duplizieren", "ru": "Дублировать", "es": "Duplicar"},
    "etl_confirm_delete": {"cs": "Smazat šablonu %s?", "en": "Delete template %s?", "de": "Vorlage %s löschen?", "ru": "Удалить шаблон %s?", "es": "¿Eliminar plantilla %s?"},
    "etl_empty": {"cs": "Žádné email šablony. Vytvořte první šablonu pro vaše kampaně.", "en": "No email templates yet. Create the first template for your campaigns.", "de": "Keine E-Mail-Vorlagen. Erstellen Sie die erste Vorlage für Ihre Kampagnen.", "ru": "Нет email-шаблонов. Создайте первый шаблон для ваших кампаний.", "es": "Sin plantillas de email. Cree la primera plantilla para sus campañas."},
    "etl_btn_create_template": {"cs": "Vytvořit šablonu", "en": "Create template", "de": "Vorlage erstellen", "ru": "Создать шаблон", "es": "Crear plantilla"},

    # ── Email template form ──
    "etf_breadcrumb_new": {"cs": "Nová šablona", "en": "New template", "de": "Neue Vorlage", "ru": "Новый шаблон", "es": "Nueva plantilla"},
    "etf_breadcrumb_edit": {"cs": "Upravit", "en": "Edit", "de": "Bearbeiten", "ru": "Редактировать", "es": "Editar"},
    "etf_page_title_new": {"cs": "Nová email šablona", "en": "New email template", "de": "Neue E-Mail-Vorlage", "ru": "Новый email-шаблон", "es": "Nueva plantilla de email"},
    "etf_page_title_edit": {"cs": "Upravit šablonu", "en": "Edit template", "de": "Vorlage bearbeiten", "ru": "Редактировать шаблон", "es": "Editar plantilla"},
    "etf_basic_info": {"cs": "Základní údaje", "en": "Basic info", "de": "Grundinfo", "ru": "Основная информация", "es": "Información básica"},
    "etf_template_name": {"cs": "Název šablony", "en": "Template name", "de": "Vorlagenname", "ru": "Название шаблона", "es": "Nombre de la plantilla"},
    "etf_email_subject": {"cs": "Předmět emailu", "en": "Email subject", "de": "E-Mail-Betreff", "ru": "Тема письма", "es": "Asunto del email"},
    "etf_subject_placeholder": {"cs": "Ahoj {{first_name}}, máme novinky!", "en": "Hi {{first_name}}, we have news!", "de": "Hallo {{first_name}}, wir haben Neuigkeiten!", "ru": "Привет {{first_name}}, у нас новости!", "es": "¡Hola {{first_name}}, tenemos novedades!"},
    "etf_preheader": {"cs": "Preheader", "en": "Preheader", "de": "Preheader", "ru": "Прехедер", "es": "Preheader"},
    "etf_preheader_help": {"cs": "krátký text za předmětem v emailovém klientu", "en": "short text shown after the subject in email clients", "de": "kurzer Text nach dem Betreff in E-Mail-Clients", "ru": "короткий текст после темы в почтовых клиентах", "es": "texto corto que se muestra tras el asunto en clientes de email"},
    "etf_preheader_placeholder": {"cs": "Zjistěte více o naší nabídce...", "en": "Learn more about our offer...", "de": "Mehr über unser Angebot erfahren...", "ru": "Узнайте больше о нашем предложении...", "es": "Más información sobre nuestra oferta..."},
    "etf_insert_to_subject": {"cs": "Vložit do předmětu:", "en": "Insert into subject:", "de": "In Betreff einfügen:", "ru": "Вставить в тему:", "es": "Insertar en asunto:"},
    "etf_var_first_name": {"cs": "Jméno", "en": "First name", "de": "Vorname", "ru": "Имя", "es": "Nombre"},
    "etf_var_last_name": {"cs": "Příjmení", "en": "Last name", "de": "Nachname", "ru": "Фамилия", "es": "Apellido"},
    "etf_var_company": {"cs": "Firma", "en": "Company", "de": "Firma", "ru": "Компания", "es": "Empresa"},
    "etf_var_email": {"cs": "email", "en": "email", "de": "E-Mail", "ru": "email", "es": "email"},
    "etf_var_unsubscribe": {"cs": "odhlášení", "en": "unsubscribe", "de": "Abmeldung", "ru": "отписка", "es": "baja"},
    "etf_starters_title": {"cs": "Začít ze šablony", "en": "Start from template", "de": "Mit Vorlage beginnen", "ru": "Начать с шаблона", "es": "Comenzar desde plantilla"},
    "etf_starter_newsletter": {"cs": "Newsletter", "en": "Newsletter", "de": "Newsletter", "ru": "Рассылка", "es": "Newsletter"},
    "etf_starter_newsletter_desc": {"cs": "Hlavička, obsah, patička", "en": "Header, content, footer", "de": "Kopfzeile, Inhalt, Fußzeile", "ru": "Шапка, контент, подвал", "es": "Cabecera, contenido, pie"},
    "etf_starter_promo": {"cs": "Promo akce", "en": "Promo offer", "de": "Promo-Aktion", "ru": "Акция", "es": "Promoción"},
    "etf_starter_promo_desc": {"cs": "CTA tlačítko, nabídka", "en": "CTA button, offer", "de": "CTA-Button, Angebot", "ru": "CTA кнопка, предложение", "es": "Botón CTA, oferta"},
    "etf_starter_minimal": {"cs": "Minimální", "en": "Minimal", "de": "Minimal", "ru": "Минимальный", "es": "Mínima"},
    "etf_starter_minimal_desc": {"cs": "Čistý text, bez grafik", "en": "Plain text, no graphics", "de": "Reiner Text, ohne Grafiken", "ru": "Чистый текст, без графики", "es": "Texto puro, sin gráficos"},
    "etf_starter_welcome": {"cs": "Uvítací", "en": "Welcome", "de": "Willkommen", "ru": "Приветственный", "es": "Bienvenida"},
    "etf_starter_welcome_desc": {"cs": "Onboarding, vítejte", "en": "Onboarding, welcome", "de": "Onboarding, willkommen", "ru": "Онбординг, приветствие", "es": "Onboarding, bienvenida"},
    "etf_starter_announcement": {"cs": "Oznámení", "en": "Announcement", "de": "Ankündigung", "ru": "Объявление", "es": "Anuncio"},
    "etf_starter_announcement_desc": {"cs": "Novinka, update", "en": "News, update", "de": "Neuigkeit, Update", "ru": "Новость, обновление", "es": "Novedad, actualización"},
    "etf_starter_blank": {"cs": "Prázdná", "en": "Blank", "de": "Leer", "ru": "Пустая", "es": "En blanco"},
    "etf_starter_blank_desc": {"cs": "Od nuly", "en": "From scratch", "de": "Von Null", "ru": "С нуля", "es": "Desde cero"},
    "etf_tab_visual": {"cs": "Vizuální editor", "en": "Visual editor", "de": "Visueller Editor", "ru": "Визуальный редактор", "es": "Editor visual"},
    "etf_tab_html": {"cs": "HTML kód", "en": "HTML code", "de": "HTML-Code", "ru": "HTML код", "es": "Código HTML"},
    "etf_variables": {"cs": "Proměnné:", "en": "Variables:", "de": "Variablen:", "ru": "Переменные:", "es": "Variables:"},
    "etf_plain_text_title": {"cs": "Plain text verze", "en": "Plain text version", "de": "Plain-Text-Version", "ru": "Версия в простом тексте", "es": "Versión en texto plano"},
    "etf_btn_generate_text": {"cs": "Vygenerovat z HTML", "en": "Generate from HTML", "de": "Aus HTML generieren", "ru": "Сгенерировать из HTML", "es": "Generar desde HTML"},
    "etf_plain_text_placeholder": {"cs": "Vygeneruje se automaticky...", "en": "Will be generated automatically...", "de": "Wird automatisch generiert...", "ru": "Будет сгенерировано автоматически...", "es": "Se generará automáticamente..."},
    "etf_preview_title": {"cs": "Náhled", "en": "Preview", "de": "Vorschau", "ru": "Предпросмотр", "es": "Vista previa"},
    "etf_btn_desktop": {"cs": "Desktop", "en": "Desktop", "de": "Desktop", "ru": "ПК", "es": "Escritorio"},
    "etf_btn_mobile": {"cs": "Mobile", "en": "Mobile", "de": "Mobil", "ru": "Мобильный", "es": "Móvil"},
    "etf_btn_refresh": {"cs": "Obnovit", "en": "Refresh", "de": "Aktualisieren", "ru": "Обновить", "es": "Actualizar"},
    "etf_subject_label": {"cs": "Předmět:", "en": "Subject:", "de": "Betreff:", "ru": "Тема:", "es": "Asunto:"},
    "etf_btn_create": {"cs": "Vytvořit šablonu", "en": "Create template", "de": "Vorlage erstellen", "ru": "Создать шаблон", "es": "Crear plantilla"},
    "etf_name_placeholder": {"cs": "Newsletter březen 2025", "en": "Newsletter March 2025", "de": "Newsletter März 2025", "ru": "Рассылка март 2025", "es": "Newsletter marzo 2025"},

    # ── Dashboard ──
    "dash_total_contacts": {"cs": "Celkem kontaktů", "en": "Total contacts", "de": "Kontakte gesamt", "ru": "Всего контактов", "es": "Total contactos"},
    "dash_active": {"cs": "aktivních", "en": "active", "de": "aktiv", "ru": "активных", "es": "activos"},
    "dash_bounced": {"cs": "bounced", "en": "bounced", "de": "bounced", "ru": "отклонено", "es": "rebotados"},
    "dash_campaigns": {"cs": "Kampaně", "en": "Campaigns", "de": "Kampagnen", "ru": "Кампании", "es": "Campañas"},
    "dash_running": {"cs": "běží", "en": "running", "de": "laufen", "ru": "выполняется", "es": "en ejecución"},
    "dash_sent_today": {"cs": "Odesláno dnes", "en": "Sent today", "de": "Heute gesendet", "ru": "Отправлено сегодня", "es": "Enviados hoy"},
    "dash_servers": {"cs": "Mail servery", "en": "Mail servers", "de": "Mail Server", "ru": "Почтовые серверы", "es": "Servidores"},
    "dash_recent": {"cs": "Poslední kampaně", "en": "Recent campaigns", "de": "Letzte Kampagnen", "ru": "Последние кампании", "es": "Campañas recientes"},
    "dash_server_status": {"cs": "Stav serverů", "en": "Server status", "de": "Server-Status", "ru": "Статус серверов", "es": "Estado servidores"},
    "dash_all_servers_total": {"cs": "celkem všechny servery", "en": "all servers total", "de": "alle Server gesamt", "ru": "всего по всем серверам", "es": "total todos los servidores"},
    "dash_sent_per_hour": {"cs": "Odesláno / hodina", "en": "Sent / hour", "de": "Gesendet / Stunde", "ru": "Отправлено / час", "es": "Enviados / hora"},
    "dash_sent_per_day": {"cs": "Odesláno / den", "en": "Sent / day", "de": "Gesendet / Tag", "ru": "Отправлено / день", "es": "Enviados / día"},
    "empty_servers_long": {"cs": "Žádné mail servery. Přidejte první server.", "en": "No mail servers. Add the first one.", "de": "Keine Mail Server. Fügen Sie den ersten hinzu.", "ru": "Нет почтовых серверов. Добавьте первый сервер.", "es": "Sin servidores. Añada el primero."},

    # ── Common actions ──
    "btn_create": {"cs": "Vytvořit", "en": "Create", "de": "Erstellen", "ru": "Создать", "es": "Crear"},
    "btn_save": {"cs": "Uložit", "en": "Save", "de": "Speichern", "ru": "Сохранить", "es": "Guardar"},
    "btn_cancel": {"cs": "Zrušit", "en": "Cancel", "de": "Abbrechen", "ru": "Отмена", "es": "Cancelar"},
    "btn_delete": {"cs": "Smazat", "en": "Delete", "de": "Löschen", "ru": "Удалить", "es": "Eliminar"},
    "btn_edit": {"cs": "Upravit", "en": "Edit", "de": "Bearbeiten", "ru": "Редактировать", "es": "Editar"},
    "btn_start": {"cs": "Spustit", "en": "Start", "de": "Starten", "ru": "Запустить", "es": "Iniciar"},
    "btn_pause": {"cs": "Pauza", "en": "Pause", "de": "Pause", "ru": "Пауза", "es": "Pausar"},
    "btn_resume": {"cs": "Pokračovat", "en": "Resume", "de": "Fortsetzen", "ru": "Продолжить", "es": "Reanudar"},
    "btn_stop": {"cs": "Stop", "en": "Stop", "de": "Stopp", "ru": "Стоп", "es": "Detener"},
    "btn_test": {"cs": "Test", "en": "Test", "de": "Test", "ru": "Тест", "es": "Probar"},
    "btn_test_email": {"cs": "Test email", "en": "Test email", "de": "Test-E-Mail", "ru": "Тест письма", "es": "Email de prueba"},
    "btn_import_csv": {"cs": "Import CSV", "en": "Import CSV", "de": "CSV importieren", "ru": "Импорт CSV", "es": "Importar CSV"},
    "btn_add_contact": {"cs": "Přidat kontakt", "en": "Add contact", "de": "Kontakt hinzufügen", "ru": "Добавить контакт", "es": "Añadir contacto"},
    "btn_add_server": {"cs": "Přidat server", "en": "Add server", "de": "Server hinzufügen", "ru": "Добавить сервер", "es": "Añadir servidor"},
    "btn_new_campaign": {"cs": "Nová kampaň", "en": "New campaign", "de": "Neue Kampagne", "ru": "Новая кампания", "es": "Nueva campaña"},
    "btn_new_template": {"cs": "Nová šablona", "en": "New template", "de": "Neue Vorlage", "ru": "Новый шаблон", "es": "Nueva plantilla"},
    "btn_new_list": {"cs": "Nový seznam", "en": "New list", "de": "Neue Liste", "ru": "Новый список", "es": "Nueva lista"},
    "btn_resend": {"cs": "Znovu odeslat", "en": "Resend", "de": "Erneut senden", "ru": "Отправить снова", "es": "Reenviar"},
    "btn_duplicate": {"cs": "Duplikovat", "en": "Duplicate", "de": "Duplizieren", "ru": "Дублировать", "es": "Duplicar"},
    "btn_filter": {"cs": "Filtrovat", "en": "Filter", "de": "Filtern", "ru": "Фильтр", "es": "Filtrar"},
    "btn_reset": {"cs": "Reset", "en": "Reset", "de": "Zurücksetzen", "ru": "Сбросить", "es": "Restablecer"},
    "btn_show_all": {"cs": "Zobrazit vše", "en": "Show all", "de": "Alle anzeigen", "ru": "Показать все", "es": "Mostrar todo"},
    "btn_refresh": {"cs": "Obnovit", "en": "Refresh", "de": "Aktualisieren", "ru": "Обновить", "es": "Actualizar"},
    "btn_generate": {"cs": "Vygenerovat z HTML", "en": "Generate from HTML", "de": "Aus HTML generieren", "ru": "Сгенерировать из HTML", "es": "Generar desde HTML"},

    # ── Table headers ──
    "th_name": {"cs": "Název", "en": "Name", "de": "Name", "ru": "Название", "es": "Nombre"},
    "th_email": {"cs": "Email", "en": "Email", "de": "E-Mail", "ru": "Email", "es": "Email"},
    "th_status": {"cs": "Status", "en": "Status", "de": "Status", "ru": "Статус", "es": "Estado"},
    "th_sent": {"cs": "Odesláno", "en": "Sent", "de": "Gesendet", "ru": "Отправлено", "es": "Enviados"},
    "th_delivered": {"cs": "Doručeno", "en": "Delivered", "de": "Zugestellt", "ru": "Доставлено", "es": "Entregados"},
    "th_opened": {"cs": "Otevřeno", "en": "Opened", "de": "Geöffnet", "ru": "Открыто", "es": "Abiertos"},
    "th_clicked": {"cs": "Kliknuto", "en": "Clicked", "de": "Geklickt", "ru": "Клики", "es": "Clics"},
    "th_bounced": {"cs": "Bounced", "en": "Bounced", "de": "Bounced", "ru": "Отклонено", "es": "Rebotados"},
    "th_failed": {"cs": "Selhání", "en": "Failed", "de": "Fehlgeschlagen", "ru": "Ошибки", "es": "Fallidos"},
    "th_created": {"cs": "Vytvořeno", "en": "Created", "de": "Erstellt", "ru": "Создано", "es": "Creado"},
    "th_actions": {"cs": "Akce", "en": "Actions", "de": "Aktionen", "ru": "Действия", "es": "Acciones"},
    "th_server": {"cs": "Server", "en": "Server", "de": "Server", "ru": "Сервер", "es": "Servidor"},
    "th_recipients": {"cs": "Příjemci", "en": "Recipients", "de": "Empfänger", "ru": "Получатели", "es": "Destinatarios"},
    "th_progress": {"cs": "Průběh", "en": "Progress", "de": "Fortschritt", "ru": "Прогресс", "es": "Progreso"},
    "th_throttle": {"cs": "Throttle", "en": "Throttle", "de": "Drosselung", "ru": "Ограничение", "es": "Limitación"},
    "th_rotation": {"cs": "Rotace", "en": "Rotation", "de": "Rotation", "ru": "Ротация", "es": "Rotación"},
    "th_weight": {"cs": "Váha", "en": "Weight", "de": "Gewicht", "ru": "Вес", "es": "Peso"},
    "th_health": {"cs": "Health", "en": "Health", "de": "Gesundheit", "ru": "Здоровье", "es": "Salud"},
    "th_source": {"cs": "Zdroj", "en": "Source", "de": "Quelle", "ru": "Источник", "es": "Fuente"},
    "th_lists": {"cs": "Seznamy", "en": "Lists", "de": "Listen", "ru": "Списки", "es": "Listas"},
    "th_subject": {"cs": "Předmět", "en": "Subject", "de": "Betreff", "ru": "Тема", "es": "Asunto"},
    "th_domain": {"cs": "Doména", "en": "Domain", "de": "Domain", "ru": "Домен", "es": "Dominio"},
    "th_limit_hour": {"cs": "Max / hodina", "en": "Max / hour", "de": "Max / Stunde", "ru": "Макс / час", "es": "Máx / hora"},
    "th_limit_day": {"cs": "Max / den", "en": "Max / day", "de": "Max / Tag", "ru": "Макс / день", "es": "Máx / día"},

    # ── Forms ──
    "form_server_name": {"cs": "Název serveru", "en": "Server name", "de": "Servername", "ru": "Имя сервера", "es": "Nombre del servidor"},
    "form_smtp_host": {"cs": "SMTP Host", "en": "SMTP Host", "de": "SMTP Host", "ru": "SMTP Хост", "es": "Host SMTP"},
    "form_smtp_port": {"cs": "SMTP Port", "en": "SMTP Port", "de": "SMTP Port", "ru": "SMTP Порт", "es": "Puerto SMTP"},
    "form_smtp_user": {"cs": "SMTP Uživatel", "en": "SMTP User", "de": "SMTP Benutzer", "ru": "SMTP Пользователь", "es": "Usuario SMTP"},
    "form_smtp_password": {"cs": "SMTP Heslo", "en": "SMTP Password", "de": "SMTP Passwort", "ru": "SMTP Пароль", "es": "Contraseña SMTP"},
    "form_use_tls": {"cs": "Použít TLS", "en": "Use TLS", "de": "TLS verwenden", "ru": "Использовать TLS", "es": "Usar TLS"},
    "form_from_email": {"cs": "Odesílatel (email)", "en": "From (email)", "de": "Absender (E-Mail)", "ru": "Отправитель (email)", "es": "Remitente (email)"},
    "form_from_name": {"cs": "Odesílatel (jméno)", "en": "From (name)", "de": "Absender (Name)", "ru": "Отправитель (имя)", "es": "Remitente (nombre)"},
    "form_tracking_domain": {"cs": "Tracking doména", "en": "Tracking domain", "de": "Tracking-Domain", "ru": "Домен трекинга", "es": "Dominio de tracking"},
    "form_tracking_domain_help": {"cs": "Doména pro tracking a odhlášení (např. https://czsk.tv). Musí směřovat na tento server. Pokud prázdné, použije se APP_BASE_URL.", "en": "Domain for tracking & unsubscribe (e.g. https://czsk.tv). Must point to this server. Falls back to APP_BASE_URL if empty.", "de": "Domain für Tracking & Abmeldung (z.B. https://czsk.tv). Muss auf diesen Server zeigen. Fällt auf APP_BASE_URL zurück.", "ru": "Домен для трекинга и отписки (напр. https://czsk.tv). Должен указывать на этот сервер. Если пусто, используется APP_BASE_URL.", "es": "Dominio para tracking y desuscripción (ej. https://czsk.tv). Debe apuntar a este servidor. Si vacío, usa APP_BASE_URL."},
    "form_limit_hour": {"cs": "Limit / hodina", "en": "Limit / hour", "de": "Limit / Stunde", "ru": "Лимит / час", "es": "Límite / hora"},
    "form_limit_day": {"cs": "Limit / den", "en": "Limit / day", "de": "Limit / Tag", "ru": "Лимит / день", "es": "Límite / día"},
    "form_weight": {"cs": "Váha v rotaci (%)", "en": "Rotation weight (%)", "de": "Rotationsgewicht (%)", "ru": "Вес ротации (%)", "es": "Peso rotación (%)"},
    "form_campaign_name": {"cs": "Název kampaně", "en": "Campaign name", "de": "Kampagnenname", "ru": "Название кампании", "es": "Nombre campaña"},
    "form_template": {"cs": "Email šablona", "en": "Email template", "de": "E-Mail-Vorlage", "ru": "Шаблон письма", "es": "Plantilla email"},
    "form_contact_list": {"cs": "Kontaktní seznam", "en": "Contact list", "de": "Kontaktliste", "ru": "Список контактов", "es": "Lista de contactos"},
    "form_batch_size": {"cs": "Velikost dávky", "en": "Batch size", "de": "Stapelgröße", "ru": "Размер пакета", "es": "Tamaño del lote"},
    "form_interval_min": {"cs": "Min. interval (s)", "en": "Min. interval (s)", "de": "Min. Intervall (s)", "ru": "Мин. интервал (с)", "es": "Intervalo mín. (s)"},
    "form_interval_max": {"cs": "Max. interval (s)", "en": "Max. interval (s)", "de": "Max. Intervall (s)", "ru": "Макс. интервал (с)", "es": "Intervalo máx. (s)"},
    "form_pause_between": {"cs": "Pauza mezi dávkami (min)", "en": "Pause between batches (min)", "de": "Pause zwischen Stapeln (Min)", "ru": "Пауза между пакетами (мин)", "es": "Pausa entre lotes (min)"},
    "form_rotation_mode": {"cs": "Režim rotace", "en": "Rotation mode", "de": "Rotationsmodus", "ru": "Режим ротации", "es": "Modo de rotación"},
    "form_search": {"cs": "Hledat email, jméno...", "en": "Search email, name...", "de": "E-Mail, Name suchen...", "ru": "Поиск email, имя...", "es": "Buscar email, nombre..."},
    "form_all_statuses": {"cs": "Všechny stavy", "en": "All statuses", "de": "Alle Status", "ru": "Все статусы", "es": "Todos los estados"},
    "form_select_template": {"cs": "-- Vyberte šablonu --", "en": "-- Select template --", "de": "-- Vorlage wählen --", "ru": "-- Выберите шаблон --", "es": "-- Seleccionar plantilla --"},
    "form_select_list": {"cs": "-- Vyberte seznam --", "en": "-- Select list --", "de": "-- Liste wählen --", "ru": "-- Выберите список --", "es": "-- Seleccionar lista --"},
    "form_template_name": {"cs": "Název šablony", "en": "Template name", "de": "Vorlagenname", "ru": "Название шаблона", "es": "Nombre plantilla"},
    "form_subject": {"cs": "Předmět emailu", "en": "Email subject", "de": "E-Mail-Betreff", "ru": "Тема письма", "es": "Asunto del email"},
    "form_first_name": {"cs": "Jméno", "en": "First name", "de": "Vorname", "ru": "Имя", "es": "Nombre"},
    "form_last_name": {"cs": "Příjmení", "en": "Last name", "de": "Nachname", "ru": "Фамилия", "es": "Apellido"},
    "form_company": {"cs": "Firma", "en": "Company", "de": "Firma", "ru": "Компания", "es": "Empresa"},
    "form_tags": {"cs": "Tagy", "en": "Tags", "de": "Tags", "ru": "Теги", "es": "Etiquetas"},
    "form_assign_lists": {"cs": "Zařadit do seznamů", "en": "Assign to lists", "de": "Listen zuordnen", "ru": "Добавить в списки", "es": "Asignar a listas"},

    # ── Statuses ──
    "status_active": {"cs": "Aktivní", "en": "Active", "de": "Aktiv", "ru": "Активный", "es": "Activo"},
    "status_paused": {"cs": "Pozastavený", "en": "Paused", "de": "Pausiert", "ru": "Приостановлен", "es": "Pausado"},
    "status_draft": {"cs": "Koncept", "en": "Draft", "de": "Entwurf", "ru": "Черновик", "es": "Borrador"},
    "status_running": {"cs": "Běží", "en": "Running", "de": "Läuft", "ru": "Выполняется", "es": "En ejecución"},
    "status_completed": {"cs": "Dokončeno", "en": "Completed", "de": "Abgeschlossen", "ru": "Завершено", "es": "Completado"},
    "status_cancelled": {"cs": "Zrušeno", "en": "Cancelled", "de": "Abgebrochen", "ru": "Отменено", "es": "Cancelado"},
    "status_bounced": {"cs": "Bounced", "en": "Bounced", "de": "Bounced", "ru": "Отклонён", "es": "Rebotado"},
    "status_unsubscribed": {"cs": "Odhlášený", "en": "Unsubscribed", "de": "Abgemeldet", "ru": "Отписан", "es": "Desuscrito"},
    "status_warmup": {"cs": "Warm-up", "en": "Warm-up", "de": "Aufwärmung", "ru": "Прогрев", "es": "Calentamiento"},

    # ── Bounce ──
    "bounce_check": {"cs": "Kontrola bounců (IMAP)", "en": "Bounce checking (IMAP)", "de": "Bounce-Prüfung (IMAP)", "ru": "Проверка отказов (IMAP)", "es": "Control de rebotes (IMAP)"},
    "bounce_enable": {"cs": "Zapnout kontrolu bounců", "en": "Enable bounce checking", "de": "Bounce-Prüfung aktivieren", "ru": "Включить проверку отказов", "es": "Activar control de rebotes"},
    "bounce_imap_host": {"cs": "IMAP Host", "en": "IMAP Host", "de": "IMAP Host", "ru": "IMAP Хост", "es": "Host IMAP"},
    "bounce_imap_port": {"cs": "IMAP Port", "en": "IMAP Port", "de": "IMAP Port", "ru": "IMAP Порт", "es": "Puerto IMAP"},
    "bounce_imap_user": {"cs": "IMAP Uživatel", "en": "IMAP User", "de": "IMAP Benutzer", "ru": "IMAP Пользователь", "es": "Usuario IMAP"},
    "bounce_imap_password": {"cs": "IMAP Heslo", "en": "IMAP Password", "de": "IMAP Passwort", "ru": "IMAP Пароль", "es": "Contraseña IMAP"},
    "bounce_use_ssl": {"cs": "Použít SSL", "en": "Use SSL", "de": "SSL verwenden", "ru": "Использовать SSL", "es": "Usar SSL"},

    # ── Empty states ──
    "empty_campaigns": {"cs": "Žádné kampaně. Vytvořte první!", "en": "No campaigns yet. Create one!", "de": "Keine Kampagnen. Erstellen Sie eine!", "ru": "Нет кампаний. Создайте первую!", "es": "Sin campañas. ¡Cree una!"},
    "empty_contacts": {"cs": "Žádné kontakty.", "en": "No contacts yet.", "de": "Keine Kontakte.", "ru": "Нет контактов.", "es": "Sin contactos."},
    "empty_servers": {"cs": "Žádné mail servery.", "en": "No mail servers.", "de": "Keine Mail Server.", "ru": "Нет почтовых серверов.", "es": "Sin servidores."},
    "empty_templates": {"cs": "Žádné šablony.", "en": "No templates yet.", "de": "Keine Vorlagen.", "ru": "Нет шаблонов.", "es": "Sin plantillas."},
    "empty_lists": {"cs": "Žádné seznamy.", "en": "No lists yet.", "de": "Keine Listen.", "ru": "Нет списков.", "es": "Sin listas."},

    # ── Misc ──
    "total": {"cs": "Celkem", "en": "Total", "de": "Gesamt", "ru": "Всего", "es": "Total"},
    "preview": {"cs": "Náhled", "en": "Preview", "de": "Vorschau", "ru": "Предпросмотр", "es": "Vista previa"},
    "desktop": {"cs": "Desktop", "en": "Desktop", "de": "Desktop", "ru": "ПК", "es": "Escritorio"},
    "mobile": {"cs": "Mobile", "en": "Mobile", "de": "Mobil", "ru": "Мобильный", "es": "Móvil"},
    "visual_editor": {"cs": "Vizuální editor", "en": "Visual editor", "de": "Visueller Editor", "ru": "Визуальный редактор", "es": "Editor visual"},
    "html_code": {"cs": "HTML kód", "en": "HTML code", "de": "HTML-Code", "ru": "HTML код", "es": "Código HTML"},
    "plain_text": {"cs": "Plain text verze", "en": "Plain text version", "de": "Nur-Text-Version", "ru": "Текстовая версия", "es": "Versión texto plano"},
    "variables": {"cs": "Proměnné", "en": "Variables", "de": "Variablen", "ru": "Переменные", "es": "Variables"},
    "settings": {"cs": "Nastavení", "en": "Settings", "de": "Einstellungen", "ru": "Настройки", "es": "Configuración"},
    "language": {"cs": "Jazyk", "en": "Language", "de": "Sprache", "ru": "Язык", "es": "Idioma"},
    "confirm_delete": {"cs": "Opravdu smazat?", "en": "Are you sure?", "de": "Wirklich löschen?", "ru": "Удалить?", "es": "¿Está seguro?"},
    "confirm_start_campaign": {"cs": "Spustit kampaň?", "en": "Start campaign?", "de": "Kampagne starten?", "ru": "Запустить кампанию?", "es": "¿Iniciar campaña?"},
    "confirm_stop_campaign": {"cs": "Zastavit kampaň?", "en": "Stop campaign?", "de": "Kampagne stoppen?", "ru": "Остановить кампанию?", "es": "¿Detener campaña?"},
    "confirm_delete_campaign": {"cs": "Smazat kampaň?", "en": "Delete campaign?", "de": "Kampagne löschen?", "ru": "Удалить кампанию?", "es": "¿Eliminar campaña?"},
    "btn_detail": {"cs": "Detail", "en": "Detail", "de": "Detail", "ru": "Подробнее", "es": "Detalle"},
    "throttle_emails_per_batch": {"cs": "emailů", "en": "emails", "de": "E-Mails", "ru": "писем", "es": "correos"},
    "throttle_pause_label": {"cs": "pauza", "en": "pause", "de": "Pause", "ru": "пауза", "es": "pausa"},
    "empty_campaigns_long": {"cs": "Žádné kampaně. Vytvořte první kampaň!", "en": "No campaigns yet. Create the first one!", "de": "Keine Kampagnen. Erstellen Sie die erste!", "ru": "Нет кампаний. Создайте первую кампанию!", "es": "Sin campañas. ¡Cree la primera campaña!"},
    "btn_create_campaign": {"cs": "Vytvořit kampaň", "en": "Create campaign", "de": "Kampagne erstellen", "ru": "Создать кампанию", "es": "Crear campaña"},
    "send_log": {"cs": "Log odesílání", "en": "Send log", "de": "Sendeprotokoll", "ru": "Журнал отправки", "es": "Registro de envíos"},
    "assigned_servers": {"cs": "Přiřazené servery", "en": "Assigned servers", "de": "Zugewiesene Server", "ru": "Назначенные серверы", "es": "Servidores asignados"},
    "campaign_settings": {"cs": "Nastavení kampaně", "en": "Campaign settings", "de": "Kampagneneinstellungen", "ru": "Настройки кампании", "es": "Configuración campaña"},
    "throttle_settings": {"cs": "Throttling", "en": "Throttling", "de": "Drosselung", "ru": "Ограничение скорости", "es": "Limitación"},
    "basic_info": {"cs": "Základní údaje", "en": "Basic info", "de": "Grundinfo", "ru": "Основная информация", "es": "Información básica"},
    "sending_in_progress": {"cs": "Odesílání probíhá", "en": "Sending in progress", "de": "Versand läuft", "ru": "Отправка идёт", "es": "Envío en curso"},
    "no_sending_yet": {"cs": "Zatím žádné odesílání", "en": "No sending yet", "de": "Noch kein Versand", "ru": "Пока нет отправок", "es": "Sin envíos aún"},
}

DEFAULT_LANG = "cs"
SUPPORTED_LANGS = ["cs", "en", "de", "ru", "es"]
LANG_NAMES = {
    "cs": "Čeština",
    "en": "English",
    "de": "Deutsch",
    "ru": "Русский",
    "es": "Español",
}


def t(key: str, lang: str = None) -> str:
    """Get translation for key in given language."""
    lang = lang or DEFAULT_LANG
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get(DEFAULT_LANG, key))


def get_translations(lang: str = None) -> dict:
    """Get all translations as a flat dict for template use."""
    lang = lang or DEFAULT_LANG
    return {k: t(k, lang) for k in TRANSLATIONS}


# Cookie name for storing per-browser language override
LANG_COOKIE = "lang"


def _parse_accept_language(header: str) -> str | None:
    """
    Parse Accept-Language header and return the first supported language code,
    or None if none of the user's preferred languages is supported.
    Example header: 'cs-CZ,cs;q=0.9,en;q=0.8'
    """
    if not header:
        return None
    # Take just the language code (before '-' or ';'), preserve ordering
    for chunk in header.split(","):
        code = chunk.strip().split(";")[0].split("-")[0].lower()
        if code in SUPPORTED_LANGS:
            return code
    return None


def resolve_language(request) -> str:
    """
    Determine the active language for this request.
    Priority: explicit cookie > stored app_setting > Accept-Language > DEFAULT_LANG.
    Never raises — falls back to DEFAULT_LANG on any unexpected error.
    """
    try:
        # 1. Explicit cookie (manual override via dropdown)
        cookie_val = request.cookies.get(LANG_COOKIE)
        if cookie_val and cookie_val in SUPPORTED_LANGS:
            return cookie_val

        # 2. Stored preference in app_settings (set via profile, persists across browsers)
        # Imported lazily to avoid circular import (database -> translations on startup).
        try:
            from app.db.database import get_db
            db = get_db()
            try:
                row = db.execute(
                    "SELECT value FROM app_settings WHERE key='user_language'"
                ).fetchone()
                if row and row["value"] in SUPPORTED_LANGS:
                    return row["value"]
            finally:
                db.close()
        except Exception:
            pass  # DB not ready yet (first request before init?), continue

        # 3. Browser Accept-Language header
        header_lang = _parse_accept_language(
            request.headers.get("accept-language", "")
        )
        if header_lang:
            return header_lang
    except Exception:
        pass

    return DEFAULT_LANG