import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout, QLabel, QComboBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont, QColor, QFontMetrics, QIcon
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerJavaScript, QsciLexerJava, QsciLexerRuby

class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)

        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)
        self.setMarginsFont(font)
        
        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#c6a5d4"))
        
        # Brace matching: enable for a LISP-like feel
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ebceea"))
        self.setCaretForegroundColor(QColor("#190042"))
        
        # Set lexer based on language
        self.lexer = QsciLexerPython()
        self.lexer.setDefaultFont(font)
        self.setLexer(self.lexer)
        
        # Auto-completion and other features
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionReplaceWord(True)
        
        # Set the editor's background color and other styling
        self.setStyleSheet("""
            QsciScintilla {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
            }
        """)

    def setLexerByLanguage(self, language):
        if language == 'Python':
            self.lexer = QsciLexerPython()
        elif language == 'JavaScript':
            self.lexer = QsciLexerJavaScript()
        elif language == 'Java':
            self.lexer = QsciLexerJava()
        elif language == 'Ruby':
            self.lexer = QsciLexerRuby()
        else:
            self.lexer = None
        
        if self.lexer:
            self.lexer.setDefaultFont(self.font())
            self.setLexer(self.lexer)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Code Tester")
        self.setWindowIcon(QIcon('logo.png'))
        
        # Create the layout
        layout = QHBoxLayout()
        
        # Create the code editor
        self.editor = CodeEditor()
        self.editor.setLexerByLanguage('Python')
        
        # Create the output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont('Consolas', 12))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #2e202d;
                color: #f0c3ee;
                border: 1px solid #da75ff;
                border-radius: 3px;
            }
        """)
        
        # Create the input area for user input
        self.user_input = QLineEdit()
        self.user_input.setFont(QFont('Consolas', 12))
        self.user_input.setStyleSheet("""
            QLineEdit {
                background-color: #2e202d;
                color: #f0c3ee;
                border: 1px solid #da75ff;
                border-radius: 3px;
            }
        """)
        self.user_input.setPlaceholderText("Introduzir dados aqui, se exigido pelo código.")
        self.user_input.returnPressed.connect(self.sendInputToProcess)
        
        # Create the language selector
        self.language_selector = QComboBox()
        self.language_selector.addItems(['Python', 'JavaScript', 'Java', 'Ruby'])
        self.language_selector.currentTextChanged.connect(self.changeLanguage)
        
        # Create the run button
        self.run_button = QPushButton("Run Code")
        self.run_button.clicked.connect(self.runCode)
        
        # Styling the button and selector
        self.run_button.setFont(QFont('Arial', 11))
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #7b1fad;
                color: white;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #6c1d96;
            }
            QPushButton:pressed {
                background-color: #8f24c9;
            }
        """)
        self.language_selector.setFont(QFont('Arial', 11))
        self.language_selector.setStyleSheet("""
            QComboBox {
                background-color: #42248c;
                color: #ffffff;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down-arrow.png);
                width: 8px;
                height: 8px;
            }
        """)
        
        # Add widgets to layout
        left_layout = QVBoxLayout()
        top_left_layout = QHBoxLayout()
        top_left_layout.addWidget(QLabel("Selecione a Linguagem:"))
        top_left_layout.addWidget(self.language_selector)
        top_left_layout.addWidget(self.run_button)
        
        left_layout.addLayout(top_left_layout)
        left_layout.addWidget(self.editor)
        left_layout.addWidget(QLabel("Input (se necessário):"))
        left_layout.addWidget(self.user_input)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Output:"))
        right_layout.addWidget(self.output)
        
        layout.addLayout(left_layout, 3)
        layout.addLayout(right_layout, 2)
        
        # Set the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Process for running code
        self.process = None

    def changeLanguage(self, language):
        self.editor.setLexerByLanguage(language)
        # Update placeholder text based on the selected language
        if language == 'Java':
            self.user_input.setPlaceholderText("Coloque aqui a entrada que seu código Java exigir.")
        elif language == 'Python':
            self.user_input.setPlaceholderText("Coloque aqui a entrada que seu código Python exigir.")
        elif language == 'JavaScript':
            self.user_input.setPlaceholderText("Coloque aqui a entrada que seu código JavaScript exigir.")
        elif language == 'Ruby':
            self.user_input.setPlaceholderText("Coloque aqui a entrada que seu código Ruby exigir.")

    def runCode(self):
        # Clear the output area each time we run the code
        self.output.clear()
        
        language = self.language_selector.currentText()
        code = self.editor.text()
        
        # Check for syntax errors before running the code
        if not self.checkSyntax(code, language):
            self.output.setText("\nErro de sintaxe: Corrija os erros antes de executar o código.")
            return

        if self.process is not None:
            self.process.kill()
        
        if language == 'Python':
            self.process = QProcess()
            self.process.setProgram("python3")
            self.process.setArguments(["-c", code])
        elif language == 'JavaScript':
            self.process = QProcess()
            self.process.setProgram("node")
            self.process.setArguments(["-e", code])
        elif language == 'Java':
            with open('Main.java', 'w', encoding='utf-8') as f:
                f.write(code)
            subprocess.run(['javac', 'Main.java'])
            self.process = QProcess()
            self.process.setProgram("java")
            self.process.setArguments(["-cp", ".", "Main"])
        elif language == 'Ruby':
            self.process = QProcess()
            self.process.setProgram("ruby")
            self.process.setArguments(["-e", code])
        else:
            self.output.setText("Unsupported language")
            return
        
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self.process.finished.connect(self.onProcessFinished)
        self.process.start()

    def sendInputToProcess(self):
        if self.process is not None and self.process.state() == QProcess.Running:
            text = self.user_input.text() + "\n"
            self.process.write(text.encode())
            self.user_input.clear()

    def onReadyReadStandardOutput(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.output.append(data)

    def onReadyReadStandardError(self):
        data = self.process.readAllStandardError().data().decode()
        self.output.append(data)
        self.suggestCorrection(data)

    def onProcessFinished(self):
        if self.process.exitCode() != 0:
            self.output.append("\nO processo terminou com erros.")
        else:
            self.output.append("\nO processo foi concluído com êxito.")

    def suggestCorrection(self, error_message):
        suggestions = {
            "IndentationError": "Verifique a indentação. Cada nível deve ser indentado por 4 espaços ou um tab.",
            "SyntaxError": "Verifique a sintaxe do seu código. Pode haver um parêntese, aspas ou um operador mal colocado.",
            "NameError": "Verifique se todas as variáveis ou funções estão corretamente definidas e/ou importadas.",
            "TypeError": "Verifique os tipos de dados. Você pode estar tentando realizar operações com tipos incompatíveis.",
            "ModuleNotFoundError": "Verifique se o módulo que você está tentando importar está instalado e disponível.",
            "AttributeError": "Verifique se o atributo que você está tentando acessar existe no objeto.",
            "KeyError": "Verifique se a chave que você está tentando acessar existe no dicionário.",
            "IndexError": "Verifique se o índice que você está tentando acessar existe na lista ou string.",
            "FileNotFoundError": "Verifique se o arquivo que você está tentando acessar existe e o caminho está correto.",
            "ZeroDivisionError": "Você está tentando dividir um número por zero. Verifique seus cálculos."
        }

        for key in suggestions:
            if key in error_message:
                suggestion = suggestions[key]
                self.output.append(f"\nSugestão: {suggestion}")
                return

    def checkSyntax(self, code, language):
        if language == 'Python':
            try:
                compile(code, "<string>", "exec")
                return True
            except SyntaxError as e:
                self.highlightError(e)
                return False
        elif language == 'JavaScript':
            # For JavaScript, we use a simple heuristic (not perfect)
            temp_file = 'Main.js'
            with open(temp_file, 'w') as f:
                f.write(code)
            result = subprocess.run(['node', '--check', temp_file], stderr=subprocess.PIPE)
            if result.returncode != 0:
                self.output.setText(result.stderr.decode())
                return False
            return True
        elif language == 'Ruby':
            # For Ruby, we use ruby -c to check for syntax errors
            temp_file = 'Main.rb'
            with open(temp_file, 'w') as f:
                f.write(code)
            result = subprocess.run(['ruby', '-c', temp_file], stderr=subprocess.PIPE)
            if result.returncode != 0:
                self.output.setText(result.stderr.decode())
                return False
            return True
        return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QMainWindow {background-color: #2e202d;}
    QLabel {color: #ebceea; font-size: 16px;}
    """)
    window = MainWindow()
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())
