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