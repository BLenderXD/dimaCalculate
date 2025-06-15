import tkinter as tk
from tkinter import ttk, messagebox
from core.converter import VALID_DIGITS, int_to_base
from core.operand import Operand

class ProgrammerCalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        # Установка заголовка и минимального размера окна
        self.title("Программистский калькулятор")
        self.minsize(500, 400)

        # Текущий вводимый операнд (строка)
        self.current_operand_str = ""
        # Система счисления для ввода
        self.current_input_base = 10
        # Система счисления для результата
        self.result_base = 10
        # Список токенов (операнды и операторы)
        self.tokens = []

        self._create_widgets()  # Создание виджетов интерфейса
        self._layout_config()   # Настройка расположения
        self._enable_disable_digit_buttons()  # Включение/отключение кнопок

    def _create_widgets(self):
    # Настройка стилей для всех элементов интерфейса
        style = ttk.Style()
        style.configure('Calc.TButton', font=('Arial', 16))
        style.configure('Calc.TLabel', font=('Arial', 14))
        style.configure('Calc.TRadiobutton', font=('Arial', 14))
        style.configure('Calc.TLabelframe.Label', font=('Arial', 14))
        style.configure('Calc.TEntry', font=('Arial', 16))

        # Фрейм для выбора системы счисления ввода
        input_base_frame = ttk.LabelFrame(self, text="Система ввода", style='Calc.TLabelframe')
        input_base_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.input_base_var = tk.IntVar(value=self.current_input_base)
        for i, base in enumerate([2, 8, 10, 16]):
            ttk.Radiobutton(input_base_frame, text=str(base), 
                        variable=self.input_base_var,
                        value=base, 
                        command=self._on_change_input_base,
                        style='Calc.TRadiobutton').grid(row=0, column=i)

        # Фрейм для выбора системы счисления результата
        result_base_frame = ttk.LabelFrame(self, text="Система результата", style='Calc.TLabelframe')
        result_base_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.result_base_var = tk.IntVar(value=self.result_base)
        for i, base in enumerate([2, 8, 10, 16]):
            ttk.Radiobutton(result_base_frame, text=str(base), 
                        variable=self.result_base_var,
                        value=base,
                        style='Calc.TRadiobutton').grid(row=0, column=i)

        # Подписи к полям
        input_label = ttk.Label(self, text="Ввод данных:", style='Calc.TLabel')
        input_label.grid(row=1, column=0, sticky="w", padx=5)
        
        result_label = ttk.Label(self, text="Результат:", style='Calc.TLabel')
        result_label.grid(row=2, column=0, sticky="w", padx=5)

        # Поле для отображения выражения
        self.expression_var = tk.StringVar()
        self.expr_entry = ttk.Entry(self, textvariable=self.expression_var, 
                                font=("Arial", 16), state="readonly")
        self.expr_entry.grid(row=1, column=1, sticky="nsew", padx=5, pady=2)

        # Поле для отображения текущего операнда
        self.current_operand_var = tk.StringVar()
        self.curr_op_entry = ttk.Entry(self, textvariable=self.current_operand_var, 
                                    font=("Arial", 16), state="readonly")
        self.curr_op_entry.grid(row=2, column=1, sticky="nsew", padx=5, pady=2)

        # Фрейм для кнопок калькулятора
        self.buttons_frame = ttk.LabelFrame(self, text="Клавиатура", style='Calc.TLabelframe')
        self.buttons_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Определение кнопок калькулятора
        digits = [
            ['7','8','9','A','B','C'],
            ['4','5','6','D','E','F'],
            ['1','2','3','+','-','*'],
            ['0','CE','/','CLR','=']
        ]
        self.btn_refs = {}

        # Создание и размещение кнопок
        for r, row in enumerate(digits):
            for c, char in enumerate(row):
                btn = ttk.Button(self.buttons_frame, text=char, 
                            command=lambda ch=char: self.on_button_click(ch),
                            style='Calc.TButton')
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                self.btn_refs[char] = btn

    def _layout_config(self):
        # Настройка весов строк и столбцов для адаптивного интерфейса
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)

        for r in range(4):
            self.buttons_frame.rowconfigure(r, weight=1)
        for c in range(6):
            self.buttons_frame.columnconfigure(c, weight=1)

    def _on_change_input_base(self):
        # Обработка смены системы счисления ввода
        self.current_input_base = self.input_base_var.get()
        self._enable_disable_digit_buttons()

    def _enable_disable_digit_buttons(self):
        # Включение/отключение кнопок цифр в зависимости от системы счисления
        valid = VALID_DIGITS[self.current_input_base]

        for ch in "0123456789ABCDEF":
            if ch in self.btn_refs:
                if ch in valid:
                    self.btn_refs[ch].state(["!disabled"])
                else:
                    self.btn_refs[ch].state(["disabled"])

        # Включаем/отключаем точку только для десятичной системы
        if '.' in self.btn_refs:
            if self.current_input_base == 10:
                self.btn_refs['.'].state(["!disabled"])
            else:
                self.btn_refs['.'].state(["disabled"])

        # Кнопки CE, CLR, = всегда активны — не отключаем

    def _update_current_operand_display(self):
        display_expression = ""
        subs = {2: '₂', 8: '₈', 10: '₁₀', 16: '₁₆'}
        
        # Добавляем все токены из списка
        for token in self.tokens:
            if isinstance(token, Operand):
                # Добавляем индекс системы счисления к каждому числу
                display_expression += f"{token.value_str}{subs[token.base]} "
            else:
                display_expression += f"{token} "
    
        # Добавляем текущий операнд с индексом его системы счисления
        if self.current_operand_str:
            display_expression += f"{self.current_operand_str}{subs[self.current_input_base]}"
    
        # Обновляем отображение
        self.expression_var.set(display_expression.strip())

        # Отображаем результат с системой счисления
        if self.tokens and isinstance(self.tokens[-1], Operand):
            base = self.result_base_var.get()
            self.current_operand_var.set(f"{str(self.tokens[-1])}{subs[base]}")

    def _update_expression_display(self):
        # Очищаем поле результата до нажатия "="
        self.current_operand_var.set("")

    def on_button_click(self, ch):
        # Обработка нажатия кнопок калькулятора
        if ch in "0123456789ABCDEF":
            self.current_operand_str += ch
            self._update_current_operand_display()
        elif ch in ['+','-','*','/']:
            if self.current_operand_str:  # Если есть текущий операнд
                self._append_current_operand_if_exists()
                self.tokens.append(ch)
                self._update_current_operand_display()
            elif self.tokens and isinstance(self.tokens[-1], str):
                # Если последний токен - оператор, заменяем его на новый
                self.tokens[-1] = ch
                self._update_current_operand_display()
        elif ch == 'CE':
            self.current_operand_str = ""
            self._update_current_operand_display()
        elif ch == 'CLR':
            self.current_operand_str = ""
            self.tokens.clear()
            self._update_current_operand_display()
            self._update_expression_display()
        elif ch == '=':
            if self.current_operand_str:
                self._append_current_operand_if_exists()
            if len(self.tokens) >= 3:  # Проверяем, есть ли полное выражение
                self._calculate_result()

    def _append_current_operand_if_exists(self):
        # Добавляет текущий операнд в список токенов, если он не пустой
        if self.current_operand_str:
            self.tokens.append(Operand(self.current_operand_str, self.current_input_base))
            self.current_operand_str = ""
            self._update_current_operand_display()

    def _calculate_result(self):
        try:
            # Преобразуем все операнды в десятичную систему
            eval_list = []
            for t in self.tokens:
                eval_list.append(t.to_int() if isinstance(t, Operand) else t)
            
            # Вычисляем результат
            result = eval_list[0]
            for i in range(1, len(eval_list)-1, 2):
                op, nxt = eval_list[i], eval_list[i+1]
                if op == '+': result += nxt
                elif op == '-': result -= nxt
                elif op == '*': result *= nxt
                elif op == '/':
                    if nxt == 0:
                        raise ZeroDivisionError
                    result //= nxt

            # Конвертируем результат в выбранную систему
            base = self.result_base_var.get()
            result_str = int_to_base(result, base)
            
            # Отображаем результат
            subs = {2: '₂', 8: '₈', 10: '₁₀', 16: '₁₆'}
            self.current_operand_var.set(f"{result_str}{subs[base]}")

        except ZeroDivisionError:
            messagebox.showerror("Ошибка", "Деление на ноль")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Ошибка вычисления: {str(e)}")

    def _apply_custom_input_base(self):
        try:
            base = int(self.custom_input_base.get())
            if 2 <= base <= 36:  # Ограничиваем диапазон от 2 до 36
                self.current_input_base = base
                self.input_base_var.set(base)
                self._enable_disable_digit_buttons()
            else:
                messagebox.showerror("Ошибка", "Система счисления должна быть от 2 до 36")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")

    def _apply_custom_result_base(self):
        try:
            base = int(self.custom_result_base.get())
            if 2 <= base <= 36:  # Ограничиваем диапазон от 2 до 36
                self.result_base = base
                self.result_base_var.set(base)
            else:
                messagebox.showerror("Ошибка", "Система счисления должна быть от 2 до 36")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")

def main():
    # Точка входа — запуск приложения
    app = ProgrammerCalculator()
    app.mainloop()