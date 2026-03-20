result_akaidoo.md

1. Установка — akaidoo 1.5.0 установлен успешно (+ зависимости: manifestoo, tree-sitter,    
  GitPython и др.)                                                                            
                                                                                              
  2. Конфиг — создан akaidoo.conf в корне проекта:                                            
  [options]                                                                                 
  ; akaidoo config for host (WSL2) — НЕ для Docker                                            
  ; Используется: akaidoo addon <module_name> -c akaidoo.conf                                 
  addons_path = ./odoo/addons,./custom_addons                                                 
                                                                                              
  3. Проверка — akaidoo --version → akaidoo version: 1.5.0                                    
                                                                                              
  4. Тест-запуск на модуле object_request — akaidoo корректно нашёл модуль и построил дерево  
  зависимостей с файлами из ./odoo/addons и ./custom_addons.                                  
                                                                                              
  ---                                                                                         
  Использование:                                                                            
  # Из корня проекта                                                                          
  akaidoo addon object_request -c akaidoo.conf                                              
                                                                                            
  # Скопировать контекст в буфер обмена                                                       
  akaidoo addon object_request -c akaidoo.conf --clipboard
                                                                                              
  # Сохранить в файл                                                                          
  akaidoo addon object_request -c akaidoo.conf -o context.md                                
                                                                                              
  Предупреждение could not obtain odoo.addons.__path__ — ожидаемо, т.к. Odoo не установлен на 
  хосте. Это не мешает работе: akaidoo нашёл все пути через addons_path из конфига.   

  ● Все 6 модулей найдены и работают. Итоговая сводка:

  ---
  Результаты разведки

  Модуль: stock
  Путь: odoo/addons/stock
  Файлов: 57
  Размер контекста: 761 KB / 210k токенов
  Зависимостей: barcodes_gs1, digest, product, resource, mail...
  ────────────────────────────────────────
  Модуль: purchase
  Путь: odoo/addons/purchase
  Файлов: 101
  Размер контекста: 1201 KB / 332k токенов
  Зависимостей: account, analytic, product, onboarding...
  ────────────────────────────────────────
  Модуль: sale
  Путь: odoo/addons/sale
  Файлов: 133
  Размер контекста: 1147 KB / 317k токенов
  Зависимостей: account, account_payment, payment, sales_team, utm...
  ────────────────────────────────────────
  Модуль: crm
  Путь: odoo/addons/crm
  Файлов: 66
  Размер контекста: 368 KB / 101k токенов
  Зависимостей: calendar, contacts, phone_validation, sales_team, utm...
  ────────────────────────────────────────
  Модуль: contacts
  Путь: odoo/addons/contacts
  Файлов: 14
  Размер контекста: 9.8 KB / 2k токенов
  Зависимостей: mail (только)
  ────────────────────────────────────────
  Модуль: object_request
  Путь: custom_addons/object_request
  Файлов: 147
  Размер контекста: 598 KB / 165k токенов
  Зависимостей: purchase, stock, contacts, product, account...

  ---
  Ключевые наблюдения
                                                                                              
  Предупреждение could not obtain odoo.addons.__path__ — норма, Odoo не установлен на хосте.
  На работу не влияет.                                                                        
                  
  Missing dependencies: base — модуль base не найден в ./odoo/addons (он в                    
  ./odoo/odoo/addons/base). Это cosmetic warning, akaidoo строит дерево и без него.
                                                                                              
  purchase и sale — самые тяжёлые (>300k токенов) из-за транзитивной зависимости на account   
  (аж 344KB только account_move.py). Для работы с ними стоит использовать --shrink medium или
  --context-budget 100k.                                                                      
                  
  object_request правильно подтянул purchase и stock как зависимости — конфиг работает        
  корректно.
                                                                                              
  ---             
  Если нужно убрать Missing dependencies: base
                                                                                              
  Добавь в akaidoo.conf путь к базовым аддонам Odoo:
                                                                                              
  addons_path = ./odoo/addons,./odoo/odoo/addons,./custom_addons

  ● Всё уложилось в бюджет. Смотрим результаты:                                                 
                                                                                              
  Read 3 files (ctrl+o to expand)                                                             
                                                                                              
● Цель достигнута. Итоги:                                                                     
                                                                                              
  ---                                                                                         
  Результат                                                                                   
                                                                                              
  ┌───────────────────────────┬────────┬─────────┬───────┬────────┐                           
  │           Файл            │ Размер │ Моделей │ Полей │ Статус │                           
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ contacts_context.md       │ 382 B  │ 1       │ 0     │ ✅     │                           
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ purchase_context.md       │ 12 KB  │ 21      │ 133   │ ✅     │                           
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ crm_context.md            │ 15 KB  │ 32      │ 157   │ ✅     │                           
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ sale_context.md           │ 17 KB  │ 33      │ 185   │ ✅     │
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ stock_context.md          │ 22 KB  │ 25      │ 351   │ ✅     │
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ object_request_context.md │ 30 KB  │ 40      │ 389   │ ✅     │
  ├───────────────────────────┼────────┼─────────┼───────┼────────┤                           
  │ account_context.md        │ 39 KB  │ 41      │ 511   │ ✅     │
  └───────────────────────────┴────────┴─────────┴───────┴────────┘                           
                  
  Все файлы в диапазоне 0.4–39 KB. Суммарно: ~135 KB vs 2.2 MB в прошлой итерации — сжатие в  
  16 раз.
                                                                                              
  ---             
  Что создано
                                                                                              
  - scripts/extract_schema.py — переиспользуемый скрипт. Принимает любой akaidoo-дамп, выдаёт
  markdown-таблицы. Запуск: python3 scripts/extract_schema.py input.md -o output.md           
  - generated/*.md — чистые схемы: только _name, _inherit, поля с типами и связями. Методы,
  импорты, манифесты, тесты — отброшены.                                                      
                  
  Одно наблюдение по contacts_context.md — там 0 полей, потому что contacts наследует         
  res.partner без добавления полей (только меню). Это корректно. Если нужна схема res.partner
  — она полностью есть в crm_context.md и object_request_context.md.   

  7/7 модулей, все файлы в статусе OK. Итог:                                                  
                                                                                              
  ---                                                                                         
  Результат запуска                                                                           
                                                                                              
  account_context.md         40K   776 строк  OK                                              
  contacts_context.md        4.0K    9 строк  OK                                              
  crm_context.md             16K   352 строки OK                                              
  object_request_context.md  32K   651 строка OK                                              
  purchase_context.md        12K   258 строк  OK                                              
  sale_context.md            20K   377 строк  OK                                              
  stock_context.md           24K   508 строк  OK                                              
                                                                                              
  Итого: 7/7 модулей успешно                                                                  
                                                                                              
  ---                                                                                       
  Что создано
                                                                                              
  scripts/update_knowledge.sh — полный pipeline одной командой из корня проекта:
                                                                                              
  ./scripts/update_knowledge.sh              # стандартный запуск                             
  ./scripts/update_knowledge.sh --no-cleanup # оставить /tmp/akaidoo_raw/ для отладки         
                                                                                              
  Особенности скрипта:                                                                        
  - Проверка зависимостей в начале: akaidoo, extract_schema.py, akaidoo.conf                  
  - Раздельные exclude-листы для account (без account в exclude) и остальных                  
  - Раздельный shrink для стандартных (max) и кастомных (soft) модулей                      
  - Продолжение при ошибке — warn + счётчик, не exit                                          
  - Таблица итогов с предупреждением > 50KB если файл вырос                                   
  - Автоочистка /tmp/akaidoo_raw/ в конце (флаг --no-cleanup отключает)                       
  - Чтобы добавить новый кастомный модуль — одна строка в массив CUSTOM_MODULES       



  Всё работает. Итог изменений в knowledge_provider.py:                                       
                                                                                          
  Добавлено (строки 13–26, 34, 105–133):                                                      
                                                                                              
  ┌────────────────────────────────┬──────────────────────────────────────┐                   
  │              Что               │                 Где                  │                   
  ├────────────────────────────────┼──────────────────────────────────────┤                   
  │ GENERATED_DIR                  │ путь к static/knowledge/generated/   │
  ├────────────────────────────────┼──────────────────────────────────────┤
  │ MAX_TECH_CONTEXT_CHARS = 15000 │ лимит для технических контекстов     │                   
  ├────────────────────────────────┼──────────────────────────────────────┤                   
  │ MODULE_CONTEXT_FILES           │ маппинг 7 модулей → имена .md файлов │                   
  ├────────────────────────────────┼──────────────────────────────────────┤                   
  │ self._tech_cache = {}          │ инициализация кэша в __init__        │
  ├────────────────────────────────┼──────────────────────────────────────┤                   
  │ get_technical_context(module)  │ новый публичный метод                │
  └────────────────────────────────┴──────────────────────────────────────┘                   
                                                            
  Поведение get_technical_context:                                                            
  - 'purchase' → 10 762 символа, возвращает как есть        
  - 'stock' → 24 KB файл, обрезается до 15 000 с ...(обрезано)                                
  - 'nonexistent' → None + warning в лог (fallback пробует {module}_context.md)
  - повторные вызовы → из _tech_cache без чтения диска                                        
                                                                                              
  Не тронуто: get_snippets, _rank_snippets, _apply_size_limit, _load_snippets,                
  load_knowledge_index, формат index.json.    



  Всё работает. Диффы минимальны:                                                             
                                                                                          
  ---                                                                                         
  prompt_builder.py — добавлен 1 метод (строки 74–84):                                        
  def build_technical_context_block(self, technical_context):                                 
      if not technical_context:                                                               
          return ''                                                                           
      return (                                                                                
          '## Структура данных текущего модуля\n'
          'Ниже — техническая карта моделей, полей и связей. ...\n\n'                         
          + technical_context                                                               
      )                                                                                       
       
  chat_controller.py — добавлено 4 строки после knowledge_block (строки 117–120):             
  technical_context = _knowledge_provider.get_technical_context(module)                       
  tech_block = _prompt_builder.build_technical_context_block(technical_context)
  if tech_block:                                                                              
      system_parts.append(tech_block)                                                       
                                                                                              
  Порядок system_parts (подтверждён тестом):                                                  
  1. system_prompt — роль ассистента                                                          
  2. safety — ограничения                                                                     
  3. context_block — контекст экрана                                                          
  4. knowledge_block — curated JSON (не тронут)                                               
  5. tech_block — akaidoo схема (новый, последний)        



  ● Все тесты прошли. Итог:                                                                     
                                                                                              
  ---                                                                                         
  Результат                                                                                   
                                                                                              
  0 failed, 0 error(s) of 89 tests                                                            
                                                                                              
  Добавлено 8 новых тестов:                                                                   
                                                                                              
  test_knowledge_provider.py (+5):                                                            
                                                            
  ┌────────────────────────────────────────────────────────┬───────────────────────────────┐  
  │                          Тест                          │         Что проверяет         │  
  ├────────────────────────────────────────────────────────┼───────────────────────────────┤  
  │ test_get_technical_context_returns_content             │ мок файла → возвращает        │  
  │                                                        │ содержимое                    │
  ├────────────────────────────────────────────────────────┼───────────────────────────────┤  
  │ test_get_technical_context_unknown_module_returns_none │ несуществующий модуль → None  │  
  ├────────────────────────────────────────────────────────┼───────────────────────────────┤  
  │ test_get_technical_context_caches_result               │ второй вызов из кэша, open()  │  
  │                                                        │ вызван 1 раз                  │  
  ├────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ test_get_technical_context_truncates_large_content     │ файл > 15000 обрезается с     │  
  │                                                        │ ...(обрезано)                 │  
  ├────────────────────────────────────────────────────────┼───────────────────────────────┤
  │ test_get_technical_context_file_not_found_returns_none │ файл отсутствует → None,      │  
  │                                                        │ повторный тоже None           │  
  └────────────────────────────────────────────────────────┴───────────────────────────────┘
                                                                                              
  test_prompt_builder.py (+3):                              

  ┌───────────────────────────────────────────────────────────────┬────────────────────────┐  
  │                             Тест                              │     Что проверяет      │
  ├───────────────────────────────────────────────────────────────┼────────────────────────┤  
  │ test_build_technical_context_block_with_content               │ заголовок + контент    │
  │                                                               │ присутствуют           │
  ├───────────────────────────────────────────────────────────────┼────────────────────────┤  
  │ test_build_technical_context_block_none_returns_empty         │ None → ''              │  
  ├───────────────────────────────────────────────────────────────┼────────────────────────┤  
  │ test_build_technical_context_block_empty_string_returns_empty │ '' → ''                │  
  └───────────────────────────────────────────────────────────────┴────────────────────────┘  
   
  Все 81 существующих теста прошли без изменений.      



  