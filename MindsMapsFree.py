# Name Software: Mind Maps Free
# Author: Bocaletto Luca

# Importazione delle librerie necessarie
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QMessageBox
import sqlite3

# Definizione della classe principale dell'applicazione
class MappeMentaliApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Mappe Mentali")
        self.setGeometry(100, 100, 800, 600)

        # Creazione del widget centrale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Inizializzazione dell'interfaccia utente
        self.init_ui()

    def init_ui(self):
        # Creazione del layout principale
        layout = QVBoxLayout()

        # Layout per l'inserimento delle mappe mentali
        inserimento_layout = QHBoxLayout()
        self.nome_mappa_input = QLineEdit()
        self.descrizione_mappa_input = QLineEdit()
        btn_inserisci = QPushButton("Inserisci")
        btn_inserisci.clicked.connect(self.inserisci_mappa)
        inserimento_layout.addWidget(QLabel("Nome Mappa:"))
        inserimento_layout.addWidget(self.nome_mappa_input)
        inserimento_layout.addWidget(QLabel("Descrizione Mappa:"))
        inserimento_layout.addWidget(self.descrizione_mappa_input)
        inserimento_layout.addWidget(btn_inserisci)

        # Tabella per visualizzare le mappe mentali
        self.tabella_mappe = QTableWidget()
        self.tabella_mappe.setColumnCount(3)
        self.tabella_mappe.setHorizontalHeaderLabels(["ID", "Nome", "Descrizione"])
        self.tabella_mappe.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella_mappe.cellClicked.connect(self.apri_nodi_padre)
        self.carica_mappe()

        # Pulsante per eliminare mappe mentali
        btn_elimina = QPushButton("Elimina")
        btn_elimina.clicked.connect(self.elimina_mappa)

        # Aggiunta dei widget al layout principale
        layout.addLayout(inserimento_layout)
        layout.addWidget(self.tabella_mappe)
        layout.addWidget(btn_elimina)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.finestra_nodi_padre = FinestraNodiPadre()

    # Connessione al database o creazione se non esiste
    def connetti_o_crea_database(self):
        conn = sqlite3.connect("DATABASE.db")
        conn.execute('''CREATE TABLE IF NOT EXISTS mappe_mentali
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        descrizione TEXT)''')
        
        # Crea la tabella nodi_padre se non esiste
        conn.execute('''CREATE TABLE IF NOT EXISTS nodi_padre
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        descrizione TEXT,
                        mappa_id INTEGER,
                        FOREIGN KEY (mappa_id) REFERENCES mappe_mentali(id))''')
        
        # Crea la tabella nodi_figlio se non esiste
        conn.execute('''CREATE TABLE IF NOT EXISTS nodi_figlio
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        descrizione TEXT,
                        padre_id INTEGER,
                        FOREIGN KEY (padre_id) REFERENCES nodi_padre(id))''')
        
        conn.commit()
        return conn

    # Caricamento delle mappe mentali nella tabella
    def carica_mappe(self):
        self.tabella_mappe.setRowCount(0)
        conn = self.connetti_o_crea_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, descrizione FROM mappe_mentali")
            for row_idx, row_data in enumerate(cursor.fetchall()):
                self.tabella_mappe.insertRow(row_idx)
                for col_idx, cell_data in enumerate(row_data):
                    self.tabella_mappe.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
            conn.close()

    # Inserimento di una nuova mappa mentale
    def inserisci_mappa(self):
        nome_mappa = self.nome_mappa_input.text()
        descrizione_mappa = self.descrizione_mappa_input.text()
        conn = self.connetti_o_crea_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO mappe_mentali (nome, descrizione) VALUES (?, ?)", (nome_mappa, descrizione_mappa))
            conn.commit()
            conn.close()
            self.carica_mappe()
            self.nome_mappa_input.clear()
            self.descrizione_mappa_input.clear()

    # Eliminazione di una mappa mentale
    def elimina_mappa(self):
        selected_row = self.tabella_mappe.currentRow()
        if selected_row >= 0:
            mappa_id = int(self.tabella_mappe.item(selected_row, 0).text())
            conn = self.connetti_o_crea_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mappe_mentali WHERE id=?", (mappa_id,))
                conn.commit()
                conn.close()
                self.carica_mappe()

    # Apertura della finestra dei nodi padre per una mappa mentale specifica
    def apri_nodi_padre(self, row, col):
        mappa_id = int(self.tabella_mappe.item(row, 0).text())
        nome_mappa = self.tabella_mappe.item(row, 1).text()
        self.finestra_nodi_padre.mostra_nodi_padre(mappa_id, nome_mappa)

# Definizione della classe per la finestra dei nodi padre
class FinestraNodiPadre(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nodi Padre")
        self.setGeometry(200, 200, 400, 300)
        self.layout = QVBoxLayout()

        self.label_titolo = QLabel("Label Nodi Padre")
        self.layout.addWidget(self.label_titolo)

        # Elementi per l'inserimento/modifica/eliminazione del nodo padre
        self.nome_nodo_padre_input = QLineEdit()
        self.descrizione_nodo_padre_input = QLineEdit()
        self.btn_inserisci_nodo_padre = QPushButton("Inserisci Nodo Padre")
        self.btn_elimina_nodo_padre = QPushButton("Elimina Nodo Padre")
        self.btn_inserisci_nodo_padre.clicked.connect(self.inserisci_nodo_padre)
        self.btn_elimina_nodo_padre.clicked.connect(self.elimina_nodo_padre)

        # Tabella per visualizzare i nodi padre associati alla mappa mentale
        self.tabella_nodi_padre = QTableWidget()
        self.tabella_nodi_padre.setColumnCount(3)
        self.tabella_nodi_padre.setHorizontalHeaderLabels(["ID", "Nome", "Descrizione"])
        self.tabella_nodi_padre.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(QLabel("Inserisci Nodo Padre:"))
        self.layout.addWidget(QLabel("Nome Nodo Padre:"))
        self.layout.addWidget(self.nome_nodo_padre_input)
        self.layout.addWidget(QLabel("Descrizione Nodo Padre:"))
        self.layout.addWidget(self.descrizione_nodo_padre_input)
        self.layout.addWidget(self.btn_inserisci_nodo_padre)
        self.layout.addWidget(self.btn_elimina_nodo_padre)
        self.layout.addWidget(QLabel("Nodi Padre associati alla Mappa Mentale:"))
        self.layout.addWidget(self.tabella_nodi_padre)
        self.tabella_nodi_padre.cellClicked.connect(self.apri_nodi_figlio)

        self.setLayout(self.layout)

    # Mostra i nodi padre associati a una mappa mentale specifica
    def mostra_nodi_padre(self, mappa_id, nome_mappa):
        self.mappa_id = mappa_id
        self.label_titolo.setText(f"Nodi Padre - Mappa: {nome_mappa} (ID: {mappa_id})")
        self.carica_nodi_padre()
        self.show()

    # Carica i nodi padre associati alla mappa mentale nella tabella
    def carica_nodi_padre(self):
        self.tabella_nodi_padre.setRowCount(0)
        conn = sqlite3.connect("DATABASE.db")
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, descrizione FROM nodi_padre WHERE mappa_id=?", (self.mappa_id,))
            for row_idx, row_data in enumerate(cursor.fetchall()):
                self.tabella_nodi_padre.insertRow(row_idx)
                for col_idx, cell_data in enumerate(row_data):
                    self.tabella_nodi_padre.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
            conn.close()

    # Inserimento di un nuovo nodo padre associato a una mappa mentale
    def inserisci_nodo_padre(self):
        nome_nodo_padre = self.nome_nodo_padre_input.text()
        descrizione_nodo_padre = self.descrizione_nodo_padre_input.text()
        conn = sqlite3.connect("DATABASE.db")
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO nodi_padre (nome, descrizione, mappa_id) VALUES (?, ?, ?)",
                           (nome_nodo_padre, descrizione_nodo_padre, self.mappa_id))
            conn.commit()
            conn.close()
            self.carica_nodi_padre()
            self.nome_nodo_padre_input.clear()
            self.descrizione_nodo_padre_input.clear()

    # Eliminazione di un nodo padre selezionato
    def elimina_nodo_padre(self):
        selected_row = self.tabella_nodi_padre.currentRow()
        if selected_row >= 0:
            nodo_padre_id = int(self.tabella_nodi_padre.item(selected_row, 0).text())
            conn = sqlite3.connect("DATABASE.db")
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM nodi_padre WHERE id=?", (nodo_padre_id,))
                conn.commit()
                conn.close()
                self.carica_nodi_padre()

    # Apertura della finestra dei nodi figlio per un nodo padre specifico
    def apri_nodi_figlio(self, row, col):
        nodo_padre_id = int(self.tabella_nodi_padre.item(row, 0).text())
        nome_nodo_padre = self.tabella_nodi_padre.item(row, 1).text()
        finestra_nodi_figlio = FinestraNodiFiglio(nodo_padre_id, nome_nodo_padre)
        finestra_nodi_figlio.exec_()

# Definizione della classe per la finestra dei nodi figlio
class FinestraNodiFiglio(QDialog):
    def __init__(self, nodo_padre_id, nome_nodo_padre):
        super().__init__()
        self.setWindowTitle("Nodi Figlio")
        self.setGeometry(300, 300, 400, 300)
        self.layout = QVBoxLayout()

        self.label_titolo = QLabel(f"Nodi Figlio - Nodo Padre: {nome_nodo_padre} (ID: {nodo_padre_id})")
        self.layout.addWidget(self.label_titolo)

        self.nodo_padre_id = nodo_padre_id  # Memorizza l'ID del Nodo Padre

        # Elementi per l'inserimento/modifica/eliminazione del nodo figlio
        self.nome_nodo_figlio_input = QLineEdit()
        self.descrizione_nodo_figlio_input = QLineEdit()
        self.btn_inserisci_nodo_figlio = QPushButton("Inserisci Nodo Figlio")
        self.btn_elimina_nodo_figlio = QPushButton("Elimina Nodo Figlio")
        self.btn_inserisci_nodo_figlio.clicked.connect(self.inserisci_nodo_figlio)
        self.btn_elimina_nodo_figlio.clicked.connect(self.elimina_nodo_figlio)

        # Tabella per visualizzare i nodi figlio associati al nodo padre
        self.tabella_nodi_figlio = QTableWidget()
        self.tabella_nodi_figlio.setColumnCount(3)
        self.tabella_nodi_figlio.setHorizontalHeaderLabels(["ID", "Nome", "Descrizione"])
        self.tabella_nodi_figlio.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(QLabel("Inserisci Nodo Figlio:"))
        self.layout.addWidget(QLabel("Nome Nodo Figlio:"))
        self.layout.addWidget(self.nome_nodo_figlio_input)
        self.layout.addWidget(QLabel("Descrizione Nodo Figlio:"))
        self.layout.addWidget(self.descrizione_nodo_figlio_input)
        self.layout.addWidget(self.btn_inserisci_nodo_figlio)
        self.layout.addWidget(self.btn_elimina_nodo_figlio)
        self.layout.addWidget(QLabel("Nodi Figlio associati al Nodo Padre:"))
        self.layout.addWidget(self.tabella_nodi_figlio)

        self.tabella_nodi_figlio.cellClicked.connect(self.seleziona_nodo_figlio)

        self.setLayout(self.layout)

        # Carica i dati dei nodi figlio all'apertura della finestra
        self.carica_nodi_figlio()

    # Carica i nodi figlio associati al nodo padre nella tabella
    def carica_nodi_figlio(self):
        self.tabella_nodi_figlio.setRowCount(0)
        conn = sqlite3.connect("DATABASE.db")
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, descrizione FROM nodi_figlio WHERE padre_id=?", (self.nodo_padre_id,))
            for row_idx, row_data in enumerate(cursor.fetchall()):
                self.tabella_nodi_figlio.insertRow(row_idx)
                for col_idx, cell_data in enumerate(row_data):
                    self.tabella_nodi_figlio.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))
            conn.close()

    # Inserimento di un nuovo nodo figlio associato a un nodo padre
    def inserisci_nodo_figlio(self):
        nome_nodo_figlio = self.nome_nodo_figlio_input.text()
        descrizione_nodo_figlio = self.descrizione_nodo_figlio_input.text()
        conn = sqlite3.connect("DATABASE.db")
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO nodi_figlio (nome, descrizione, padre_id) VALUES (?, ?, ?)",
                           (nome_nodo_figlio, descrizione_nodo_figlio, self.nodo_padre_id))
            conn.commit()
            conn.close()
            self.carica_nodi_figlio()
            self.nome_nodo_figlio_input.clear()
            self.descrizione_nodo_figlio_input.clear()

    # Eliminazione di un nodo figlio selezionato
    def elimina_nodo_figlio(self):
        selected_row = self.tabella_nodi_figlio.currentRow()
        if selected_row >= 0:
            nodo_figlio_id = int(self.tabella_nodi_figlio.item(selected_row, 0).text())
            conn = sqlite3.connect("DATABASE.db")
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM nodi_figlio WHERE id=?", (nodo_figlio_id,))
                conn.commit()
                conn.close()
                self.carica_nodi_figlio()

    # Gestisce la selezione di un nodo figlio
    def seleziona_nodo_figlio(self, row, col):
        nodo_figlio_id = int(self.tabella_nodi_figlio.item(row, 0).text())
        nome_nodo_figlio = self.tabella_nodi_figlio.item(row, 1).text()
        QMessageBox.information(self, "Nodo Figlio Selezionato", f"ID Nodo Figlio: {nodo_figlio_id}\nNome: {nome_nodo_figlio}")

# Funzione principale
def main():
    app = QApplication(sys.argv)
    window = MappeMentaliApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
