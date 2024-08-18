import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QTableWidget, 
    QTableWidgetItem, QGridLayout, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
import pymysql
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Conexão com o banco de dados usando variáveis de ambiente
connection = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

class ArtManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gerenciamento de Obras de Arte")

        # Layout principal
        layout = QVBoxLayout()

        # Centralizar conteúdo
        formLayout = QGridLayout()
        formLayout.setAlignment(Qt.AlignCenter)

        # Inputs e Labels com tamanhos ajustados
        self.title_input = QLineEdit()
        self.title_input.setFixedWidth(250)
        self.technique_input = QLineEdit()
        self.technique_input.setFixedWidth(250)
        self.dimensions_input = QLineEdit()
        self.dimensions_input.setFixedWidth(250)
        self.creation_date_input = QLineEdit()
        self.creation_date_input.setFixedWidth(250)
        self.status_input = QLineEdit()
        self.status_input.setFixedWidth(250)
        self.price_input = QLineEdit()
        self.price_input.setFixedWidth(250)
        self.description_input = QTextEdit()
        self.description_input.setFixedWidth(250)
        self.description_input.setFixedHeight(80)

        formLayout.addWidget(QLabel('Título:'), 0, 0)
        formLayout.addWidget(self.title_input, 0, 1)
        formLayout.addWidget(QLabel('Técnica:'), 1, 0)
        formLayout.addWidget(self.technique_input, 1, 1)
        formLayout.addWidget(QLabel('Dimensões:'), 2, 0)
        formLayout.addWidget(self.dimensions_input, 2, 1)
        formLayout.addWidget(QLabel('Data de Criação:'), 3, 0)
        formLayout.addWidget(self.creation_date_input, 3, 1)
        formLayout.addWidget(QLabel('Status:'), 4, 0)
        formLayout.addWidget(self.status_input, 4, 1)
        formLayout.addWidget(QLabel('Preço:'), 5, 0)
        formLayout.addWidget(self.price_input, 5, 1)
        formLayout.addWidget(QLabel('Descrição:'), 6, 0)
        formLayout.addWidget(self.description_input, 6, 1)

        layout.addLayout(formLayout)

        # Espaçadores para centralizar melhor o conteúdo
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Botões
        buttonLayout = QHBoxLayout()
        addButton = QPushButton("Adicionar")
        viewButton = QPushButton("Visualizar")
        updateButton = QPushButton("Atualizar")
        deleteButton = QPushButton("Deletar")

        # Conectando os botões às funções
        addButton.clicked.connect(self.add_artwork)
        viewButton.clicked.connect(self.view_artworks)
        updateButton.clicked.connect(self.update_artwork)
        deleteButton.clicked.connect(self.delete_artwork)

        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(viewButton)
        buttonLayout.addWidget(updateButton)
        buttonLayout.addWidget(deleteButton)

        layout.addLayout(buttonLayout)

        # Tabela para Visualizar Obras
        self.artTable = QTableWidget()
        layout.addWidget(self.artTable)

        # Outro espaçador para dar margem inferior
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def add_artwork(self):
        title = self.title_input.text()
        technique = self.technique_input.text()
        dimensions = self.dimensions_input.text()
        creation_date = self.creation_date_input.text()
        status = self.status_input.text()
        price = self.price_input.text()
        description = self.description_input.toPlainText()

        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO obras 
                (titulo, tecnica, dimensoes, data_criacao, status, preco, descricao) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (title, technique, dimensions, creation_date, status, price, description))
            connection.commit()
            self.clear_inputs()
            self.view_artworks()  # Atualiza a tabela após adicionar uma nova obra
        except Exception as e:
            print(f"Erro ao adicionar a obra: {e}")

    def view_artworks(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM obras")
                artworks = cursor.fetchall()

                self.artTable.setRowCount(len(artworks))
                self.artTable.setColumnCount(7)
                self.artTable.setHorizontalHeaderLabels(
                    ["ID", "Título", "Técnica", "Dimensões", "Data de Criação", "Status", "Preço"]
                )

                for row_idx, artwork in enumerate(artworks):
                    self.artTable.setItem(row_idx, 0, QTableWidgetItem(str(artwork["id"])))
                    self.artTable.setItem(row_idx, 1, QTableWidgetItem(artwork["titulo"]))
                    self.artTable.setItem(row_idx, 2, QTableWidgetItem(artwork["tecnica"]))
                    self.artTable.setItem(row_idx, 3, QTableWidgetItem(artwork["dimensoes"]))
                    self.artTable.setItem(row_idx, 4, QTableWidgetItem(artwork["data_criacao"].strftime("%Y-%m-%d")))
                    self.artTable.setItem(row_idx, 5, QTableWidgetItem(artwork["status"]))
                    self.artTable.setItem(row_idx, 6, QTableWidgetItem(str(artwork["preco"])))

                self.artTable.cellClicked.connect(self.fill_inputs_from_table)
        except Exception as e:
            print(f"Erro ao visualizar as obras: {e}")

    def fill_inputs_from_table(self, row):
        self.selected_artwork_id = self.artTable.item(row, 0).text()
        self.title_input.setText(self.artTable.item(row, 1).text())
        self.technique_input.setText(self.artTable.item(row, 2).text())
        self.dimensions_input.setText(self.artTable.item(row, 3).text())
        self.creation_date_input.setText(self.artTable.item(row, 4).text())
        self.status_input.setText(self.artTable.item(row, 5).text())
        self.price_input.setText(self.artTable.item(row, 6).text())

    def update_artwork(self):
        if not hasattr(self, 'selected_artwork_id'):
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione uma obra na tabela.")
            return

        title = self.title_input.text()
        technique = self.technique_input.text()
        dimensions = self.dimensions_input.text()
        creation_date = self.creation_date_input.text()
        status = self.status_input.text()
        price = self.price_input.text()
        description = self.description_input.toPlainText()

        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE obras SET 
                titulo = %s, tecnica = %s, dimensoes = %s, data_criacao = %s, 
                status = %s, preco = %s, descricao = %s 
                WHERE id = %s
                """
                cursor.execute(sql, (
                    title, technique, dimensions, creation_date, status, 
                    price, description, self.selected_artwork_id
                ))
            connection.commit()
            self.clear_inputs()
            self.view_artworks()  # Atualiza a tabela após a atualização
            QMessageBox.information(self, "Sucesso", "Obra atualizada com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar a obra: {e}")
            QMessageBox.critical(self, "Erro", "Não foi possível atualizar a obra.")

    def delete_artwork(self):
        selected_row = self.artTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione uma obra na tabela.")
            return

        artwork_id = self.artTable.item(selected_row, 0).text()

        confirm = QMessageBox.question(
            self, "Confirmar Exclusão", 
            f"Tem certeza de que deseja deletar a obra com ID {artwork_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                with connection.cursor() as cursor:
                    sql = "DELETE FROM obras WHERE id = %s"
                    cursor.execute(sql, (artwork_id,))
                connection.commit()

                self.artTable.removeRow(selected_row)
                QMessageBox.information(self, "Sucesso", "Obra deletada com sucesso.")
            except Exception as e:
                print(f"Erro ao deletar a obra: {e}")
                QMessageBox.critical(self, "Erro", "Não foi possível deletar a obra.")

    def clear_inputs(self):
        self.title_input.clear()
        self.technique_input.clear()
        self.dimensions_input.clear()
        self.creation_date_input.clear()
        self.status_input.clear()
        self.price_input.clear()
        self.description_input.clear()
        if hasattr(self, 'selected_artwork_id'):
            del self.selected_artwork_id

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArtManager()
    window.show()
    sys.exit(app.exec_())
